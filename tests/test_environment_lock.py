"""Hashed environments must cover the dependency graph and native wheel bytes."""
import copy
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import environment_lock as lock

ROOT = Path(__file__).resolve().parents[1]


def package(name, *, requested=False, requires=(), extras=(), python='>=3.11'):
    return {'metadata': {'name': name, 'version': '1.0', 'requires_python': python,
                         'requires_dist': list(requires)},
            'requested': requested, 'requested_extras': list(extras), 'is_direct': False,
            'is_yanked': False,
            'download_info': {'url': 'https://files.pythonhosted.org/synthetic.whl',
                              'archive_info': {'hashes': {'sha256': 'a' * 64}}}}


@pytest.fixture
def report():
    return {'version': '1', 'pip_version': '25.1.1',
            'environment': {'python_version': '3.13', 'python_full_version': '3.13.5',
                            'platform_system': 'Darwin', 'platform_machine': 'arm64',
                            'sys_platform': 'darwin', 'implementation_name': 'cpython'},
            'install': [package('renderer', requested=True, extras=['voice'], requires=(
                'shared>=1', 'mac-only; sys_platform == "darwin"',
                'voice>=1; extra == "voice"')),
                package('shared'), package('mac-only'), package('voice')]}


def test_target_graph_keeps_extras_and_excludes_macos_dependencies_from_linux(report):
    mac = lock.selected_packages(report, 'macos-arm64', '3.13')
    linux = lock.selected_packages(report, 'linux-x86_64', '3.13')
    assert set(mac) == {'renderer', 'shared', 'voice', 'mac-only'}
    assert set(linux) == {'renderer', 'shared', 'voice'}
    assert linux['renderer']['extras'] == {'voice'}


def test_projection_fails_when_the_native_report_lacks_a_target_dependency(report):
    report['install'][0]['metadata']['requires_dist'].append('linux-only; sys_platform == "linux"')
    with pytest.raises(ValueError, match='resolve natively'):
        lock.selected_packages(report, 'linux-x86_64', '3.13')


@pytest.mark.parametrize('change', ['python', 'version', 'duplicate', 'direct', 'yanked', 'incomplete'])
def test_invalid_or_incomplete_resolution_cannot_become_a_lock(report, change):
    if change == 'python':
        report['install'][1]['metadata']['requires_python'] = '>=3.14'
    elif change == 'version':
        report['install'][1]['metadata']['version'] = '0.5'
    elif change == 'duplicate':
        report['install'].append(copy.deepcopy(report['install'][0]))
    elif change in {'direct', 'yanked'}:
        report['install'][0]['is_' + change] = True
    else:
        report['install'].pop()
    with pytest.raises(ValueError):
        lock.selected_packages(report, 'macos-arm64', '3.13')


def test_hash_lock_uses_all_reviewed_release_hashes_without_copying_report_urls(report, monkeypatch,
                                                                            tmp_path):
    monkeypatch.setattr(lock, 'release_hashes', lambda *args: {'a' * 64, 'b' * 64})
    profile = tmp_path / 'profile.txt'
    profile.write_text('renderer[voice]\n')
    content = lock.report_lock(report, 'linux-x86_64', '3.13', [profile])
    assert 'https://' not in content
    assert 'renderer[voice]==1.0' in content
    assert 'mac-only' not in content
    assert lock.digest(profile) in content
    assert content.count('--hash=sha256:') == 6
    path = tmp_path / 'lock.txt'
    path.write_text(content)
    assert set(lock.read_lock(path)) == {'renderer', 'shared', 'voice'}


def test_report_artifact_must_match_public_release_hash(report, monkeypatch):
    monkeypatch.setattr(lock, 'release_hashes', lambda *args: {'b' * 64})
    with pytest.raises(ValueError, match='not a hashed PyPI release'):
        lock.report_lock(report, 'linux-x86_64', '3.13')


def test_portable_lock_rejects_platform_specific_closure(report):
    with pytest.raises(ValueError, match='platform-specific'):
        lock.report_lock(report, 'portable', '3.13')


@pytest.mark.parametrize('entry', ['renderer>=1.0', 'renderer==1.*', 'renderer==1.0',
                                  'renderer==1.0 --hash=sha256:short'])
def test_unpinned_or_unhashed_lock_is_rejected(tmp_path, entry):
    path = tmp_path / 'lock.txt'
    path.write_text(entry + '\n')
    with pytest.raises(ValueError):
        lock.read_lock(path)


def write_wheel(folder, name, version='1.0'):
    path = folder / f'{name}-{version}-py3-none-any.whl'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr(f'{name}-{version}.dist-info/METADATA',
                         f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n')
        archive.writestr(f'{name}/__init__.py', '# synthetic fixture\n')
    return path


def test_native_wheel_lock_binds_exact_output_bytes_and_extras(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text(lock.requirement_text('renderer', '1.0', {'voice'}, {'a' * 64}))
    wheel = write_wheel(tmp_path, 'renderer')
    # Setuptools and similar wheels can bundle vendors' metadata below packages.
    with zipfile.ZipFile(wheel, 'a') as archive:
        archive.writestr('renderer/vendor/nested-9.0.dist-info/METADATA',
                         'Name: nested\nVersion: 9.0\n')
    content = lock.wheel_lock(tmp_path, source)
    assert 'renderer[voice]==1.0' in content
    assert lock.digest(wheel) in content
    assert 'a' * 64 not in content
    with zipfile.ZipFile(wheel, 'a') as archive:
        archive.writestr('changed.txt', 'changed wheel bytes')
    assert lock.wheel_lock(tmp_path, source) != content


@pytest.mark.parametrize('problem', ['missing', 'extra', 'version', 'symlink'])
def test_wheel_bundle_must_match_complete_locked_distribution_set(tmp_path, problem):
    source = tmp_path / 'source.txt'
    source.write_text(lock.requirement_text('renderer', '1.0', (), {'a' * 64}))
    if problem == 'extra':
        write_wheel(tmp_path, 'unreviewed')
    elif problem == 'version':
        write_wheel(tmp_path, 'renderer', '2.0')
    elif problem == 'symlink':
        target = tmp_path / 'outside'
        target.mkdir()
        wheel = write_wheel(target, 'renderer')
        (tmp_path / wheel.name).symlink_to(wheel)
    with pytest.raises(ValueError):
        lock.wheel_lock(tmp_path, source)


def test_font_inventory_marks_fallback_and_omits_local_font_path(tmp_path, monkeypatch):
    font = tmp_path / 'synthetic-font.ttf'
    font.write_bytes(b'Synthetic font fixture.')
    monkeypatch.setattr(lock, 'command_version',
                        lambda command: 'Verdana' if command[2] == '%{family}\n' else str(font))
    result = lock.font_match('Roboto')
    assert result['family'] == 'Verdana'
    assert result['matches_requested_family'] is False
    assert result['file_sha256'] == lock.digest(font)
    assert str(font) not in repr(result)


def test_python_inventory_reports_conflicting_metadata_without_hiding_selected_version(monkeypatch):
    records = [SimpleNamespace(metadata={'Name': 'Pip'}, version='25.1.1'),
               SimpleNamespace(metadata={'Name': 'pip'}, version='26.1')]
    monkeypatch.setattr(lock.importlib.metadata, 'distributions', lambda: records)
    monkeypatch.setattr(lock.importlib.metadata, 'version', lambda name: '25.1.1')
    packages, conflicts = lock.python_packages()
    assert packages == {'pip': '25.1.1'}
    assert conflicts == {'pip': ['25.1.1', '26.1']}


@pytest.mark.parametrize('name', ['checks-py311', 'build-py313',
                                  'teaching-py313-macos-arm64', 'teaching-py313-linux-x86_64'])
def test_committed_locks_remain_hashed_and_match_their_declared_inputs(name):
    path = ROOT / 'requirements/locks' / (name + '.txt')
    packages = lock.read_lock(path)
    content = path.read_text()
    assert 'https://' not in content
    inputs = [line.split(': ', 1)[1].split() for line in content.splitlines()
              if line.startswith('# Input-SHA256: ')]
    assert inputs, 'A lock needs hashes of its source profiles.'
    for relative, expected in inputs:
        assert lock.digest(ROOT / relative) == expected, f'Regenerate {name}: {relative} changed.'
    if name.startswith('teaching-'):
        assert packages['pillow']['version'] == '11.3.0'
        assert packages['manim-voiceover']['extras'] == {'azure'}
        assert ('pyobjc-core' in packages) == name.endswith('macos-arm64')
