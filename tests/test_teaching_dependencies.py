"""The reviewed teaching profile and lightweight checks share explicit versions."""
import ast
import fnmatch
import shlex
import tomllib
from pathlib import Path

import pytest
import yaml
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

ROOT = Path(__file__).resolve().parents[1]
TEACHING_JOBS = (
    ('course-numbering.yml', 'audit'),
    ('teaching-revision.yml', 'review'),
    ('syllabus-expansion.yml', 'preview'),
    ('ten-lesson-recheck.yml', 'recheck'),
    ('smoke.yml', 'render'),
)
CHECK_JOBS = (
    ('course-numbering.yml', 'catalog'),
    ('smoke.yml', 'lint'),
    ('smoke.yml', 'catalog'),
    ('public-audit.yml', 'audit'),
)


def workflow(name):
    # Preserve GitHub's `on` key rather than YAML 1.1's boolean interpretation.
    return yaml.load((ROOT / '.github/workflows' / name).read_text(), Loader=yaml.BaseLoader)


def requirement_graph(path, *, constraint=False, seen=None):
    """Read local pip includes without importing the renderer or invoking pip."""
    seen = set() if seen is None else seen
    path = path.resolve()
    assert path.is_relative_to(ROOT / 'requirements')
    assert path not in seen, f'Repeated or cyclic requirement include: {path}'
    seen.add(path)
    requests, constraints = [], []
    for raw_line in path.read_text().splitlines():
        line = raw_line.partition('#')[0].strip()
        if not line:
            continue
        tokens = shlex.split(line)
        if tokens[0] in ('-r', '--requirement', '-c', '--constraint'):
            assert len(tokens) == 2
            nested = requirement_graph(
                path.parent / tokens[1],
                constraint=constraint or tokens[0] in ('-c', '--constraint'),
                seen=seen,
            )
            requests.extend(nested[0])
            constraints.extend(nested[1])
        else:
            (constraints if constraint else requests).append(Requirement(line))
    return requests, constraints, seen


def exact_version(requirement):
    specs = list(requirement.specifier)
    assert len(specs) == 1 and specs[0].operator == '=='
    assert '*' not in specs[0].version
    assert requirement.marker is None and requirement.url is None
    return specs[0].version


def named(requirements):
    result = {canonicalize_name(item.name): item for item in requirements}
    assert len(result) == len(requirements), 'Duplicate requirement authorities'
    return result


def pip_installs(job):
    commands = []
    for step in job['steps']:
        for line in step.get('run', '').replace('\\\n', ' ').splitlines():
            tokens = shlex.split(line, comments=True)
            if tokens[:3] in (['python', '-m', 'pip'], ['python3', '-m', 'pip']):
                tokens = tokens[3:]
            elif tokens[:1] in (['pip'], ['pip3']):
                tokens = tokens[1:]
            else:
                continue
            if tokens[:1] == ['install']:
                commands.append(tokens[1:])
    return commands


def option_value(tokens, names):
    return [tokens[index + 1] for index, token in enumerate(tokens[:-1]) if token in names]


def python_version(job):
    setups = [step for step in job['steps']
              if step.get('uses', '').startswith('actions/setup-python@')]
    assert len(setups) == 1
    return setups[0]['with']['python-version']


def test_profile_pins_direct_dependencies_and_preserves_requested_extras():
    requests, constraints, files = requirement_graph(ROOT / 'requirements/teaching.txt')
    requested, constrained = named(requests), named(constraints)
    assert {path.name for path in files} == {
        'teaching.txt', 'checks.txt', 'teaching-constraints.txt',
    }
    pins = {name: exact_version(requirement) for name, requirement in constrained.items()}
    assert all(not requirement.extras for requirement in constrained.values())
    for name, requirement in requested.items():
        if name not in pins:
            pins[name] = exact_version(requirement)
        assert requirement.specifier.contains(pins[name]), name

    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    for requirement in map(Requirement, project['dependencies']):
        name = canonicalize_name(requirement.name)
        assert name in requested, f'Uninstalled project dependency: {name}'
        assert requirement.extras <= requested[name].extras
        assert requirement.specifier.contains(pins[name]), name
    assert {'azure'} <= requested['manim-voiceover'].extras
    assert {'python-dotenv', 'setuptools'} <= requested.keys()
    assert {'manim', 'manim-voiceover', 'python-dotenv', 'setuptools',
            'numpy', 'scipy', 'pandas', 'xlrd', 'av'} <= constrained.keys()


def test_checks_remain_pinned_and_do_not_install_the_renderer():
    requests, constraints, files = requirement_graph(ROOT / 'requirements/checks.txt')
    assert {canonicalize_name(requirement.name) for requirement in requests} == {
        'pytest', 'ruff', 'pyyaml',
    }
    assert not constraints
    assert len(files) == 1
    for requirement in requests:
        exact_version(requirement)


def test_precommit_ruff_matches_ci_checks():
    requests, _, _ = requirement_graph(ROOT / 'requirements/checks.txt')
    version = exact_version(named(requests)['ruff'])
    config = yaml.safe_load((ROOT / '.pre-commit-config.yaml').read_text())
    hooks = [repo for repo in config['repos']
             if repo['repo'] == 'https://github.com/astral-sh/ruff-pre-commit']
    assert len(hooks) == 1
    assert hooks[0]['rev'] == f'v{version}'
    assert any(hook['id'] == 'ruff-check' for hook in hooks[0]['hooks'])


@pytest.mark.parametrize(('filename', 'job_name'), TEACHING_JOBS)
def test_teaching_jobs_use_reviewed_python_and_shared_profile(filename, job_name):
    job = workflow(filename)['jobs'][job_name]
    assert python_version(job) == '3.13'
    installs = pip_installs(job)
    assert option_value(installs[0], ('-r', '--requirement')) == ['requirements/teaching.txt']
    # Editable metadata must not resolve another renderer or isolated setuptools.
    for arguments in installs[1:]:
        assert option_value(arguments, ('-e', '--editable')) == ['.']
        assert {'--no-deps', '--no-build-isolation'} <= set(arguments)
    if filename in ('course-numbering.yml', 'ten-lesson-recheck.yml', 'smoke.yml'):
        assert len(installs) == 2
    assert any('pip check' in step.get('run', '') for step in job['steps'])


@pytest.mark.parametrize(('filename', 'job_name'), CHECK_JOBS)
def test_fast_jobs_use_lightweight_checks_on_python311(filename, job_name):
    job = workflow(filename)['jobs'][job_name]
    assert python_version(job) == '3.11'
    installs = pip_installs(job)
    assert len(installs) == 1
    assert option_value(installs[0], ('-r', '--requirement')) == ['requirements/checks.txt']


def test_dependency_changes_trigger_every_consuming_filtered_workflow():
    _, _, files = requirement_graph(ROOT / 'requirements/teaching.txt')
    paths = [path.relative_to(ROOT).as_posix() for path in files] + ['pyproject.toml']
    for filename in {name for name, _ in TEACHING_JOBS}:
        events = workflow(filename)['on']
        for event in ('pull_request', 'push'):
            settings = events.get(event) or {}
            if 'paths' not in settings:
                continue
            for path in paths:
                assert any(fnmatch.fnmatchcase(path, pattern) for pattern in settings['paths']), (
                    filename, event, path,
                )


def test_pip_cache_accounts_for_all_profile_files():
    _, _, files = requirement_graph(ROOT / 'requirements/teaching.txt')
    for filename, job_name in TEACHING_JOBS:
        for step in workflow(filename)['jobs'][job_name]['steps']:
            settings = step.get('with', {})
            if settings.get('cache') != 'pip':
                continue
            patterns = settings['cache-dependency-path'].splitlines()
            for path in files | {ROOT / 'pyproject.toml'}:
                assert any(fnmatch.fnmatchcase(path.relative_to(ROOT).as_posix(), pattern)
                           for pattern in patterns), (filename, path)


@pytest.mark.parametrize('filename', ['teaching-revision.yml', 'syllabus-expansion.yml'])
def test_embedded_source_archives_include_profile_files(filename):
    # Inspect the archive's Python allowlist instead of executing its CI shell.
    job = workflow(filename)['jobs'][dict(TEACHING_JOBS)[filename]]
    sources = [step['run'] for step in job['steps'] if "<<'PY'\n" in step.get('run', '')]
    assert len(sources) == 1
    tree = ast.parse(sources[0].split("<<'PY'\n", 1)[1].rsplit('\nPY', 1)[0])
    roots = next(ast.literal_eval(node.value) for node in ast.walk(tree)
                 if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == 'roots'
                         for target in node.targets))
    _, _, files = requirement_graph(ROOT / 'requirements/teaching.txt')
    assert all(path.relative_to(ROOT).as_posix().startswith(roots) for path in files)


@pytest.mark.parametrize(('filename', 'job_name'), [
    ('course-numbering.yml', 'catalog'), ('public-audit.yml', 'audit'),
])
def test_dependency_contract_runs_in_fast_ci(filename, job_name):
    job = workflow(filename)['jobs'][job_name]
    assert any('tests/test_teaching_dependencies.py' in step.get('run', '')
               and '-m pytest' in step['run'] for step in job['steps'])
