"""Validate reviewed GitHub workflow privileges without executing any workflow.

This is a bounded policy check, not a shell interpreter or a security clearance.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ACTION = re.compile(r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}$')
SECRET = re.compile(r'\bsecrets\s*(?:\.|\[)')
TOKEN = re.compile(r'\bgithub\s*(?:\.\s*token\b|\[\s*[\'"]token[\'"]\s*\])')
MANUAL_MAIN = "github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main'"
PUBLISH_GATE = (
    "github.repository == 'xia-geom/math_video_project' && "
    "github.ref == 'refs/heads/main' && github.event_name != 'pull_request'"
)
INTEGRATION_REF = 'refs/heads/integration/audits-2026-09-17'
WRITE_JOBS = {
    ('audit-integration.yml', 'verify'): {'contents': 'write', 'statuses': 'write'},
    ('publish-archive-preview.yml', 'publish'): {'contents': 'write', 'actions': 'read'},
}
CLOUD_JOBS = {
    ('teaching-revision.yml', 'review'): 'narrated_review',
    ('uqam-revision.yml', 'revision'): 'narrated_review',
    ('uqam-ouvertures.yml', 'review'): 'mode',
}
CLOUD_ENV = {
    'SPEECH_KEY': '${{ secrets.SPEECH_KEY || secrets.AZURE_SUBSCRIPTION_KEY }}',
    'SPEECH_REGION': '${{ secrets.SPEECH_REGION || secrets.AZURE_SERVICE_REGION }}',
}


class PolicyLoader(yaml.BaseLoader):
    """Preserve GitHub's `on` key and reject ambiguous duplicate YAML keys."""


def unique_mapping(loader, node):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key] = loader.construct_object(value_node)
    return result


PolicyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_yaml(path):
    value = yaml.load(Path(path).read_text(), Loader=PolicyLoader)
    if not isinstance(value, dict):
        raise ValueError('Expected a YAML mapping')
    return value


def strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, str):
        yield value


def references(value, pattern):
    return any(pattern.search(text) for text in strings(value))


def condition(value):
    text = str(value or '').strip()
    if text.startswith('${{') and text.endswith('}}'):
        text = text[3:-2].strip()
    return ' '.join(text.split())


def validate_workflow(name, workflow, classification):
    """Return location-only violations, never environment values or shell text."""
    errors = []

    def require(ok, location, rule):
        if not ok:
            errors.append(f'{name}:{location}: {rule}')

    events = workflow.get('on')
    require(isinstance(events, dict), 'on', 'events must be explicit mappings')
    events = events if isinstance(events, dict) else {}
    require(set(events) == set(classification.get('events', [])), 'on', 'unclassified trigger')
    require('pull_request_target' not in events, 'on', 'privileged PR trigger is forbidden')
    expected_class = ('administration' if any(key[0] == name for key in WRITE_JOBS)
                      else 'gated_narration' if any(key[0] == name for key in CLOUD_JOBS)
                      else 'read_only')
    require(classification.get('class') == expected_class, 'classification', 'incorrect privilege class')
    require(bool(classification.get('purpose')), 'classification', 'purpose must be documented')
    top_permissions = {'contents': 'read'}
    if name == 'public-audit.yml':
        top_permissions.update(actions='read', issues='read', **{'pull-requests': 'read'})
    require(workflow.get('permissions') == top_permissions, 'permissions', 'unexpected workflow permissions')
    root_fields = {key: value for key, value in workflow.items() if key != 'jobs'}
    require(not references(root_fields, SECRET), 'workflow', 'secrets must be confined to gated steps')
    require(not references(root_fields, TOKEN), 'workflow', 'token must be confined to reviewed steps')
    jobs = workflow.get('jobs', {})
    if not isinstance(jobs, dict):
        require(False, 'jobs', 'jobs must be a mapping')
        return errors
    require(set(jobs) == set(classification.get('jobs', [])), 'jobs', 'unclassified or missing job')
    for job_name, job in jobs.items():
        location = f'jobs.{job_name}'
        if not isinstance(job, dict):
            require(False, location, 'job must be a mapping')
            continue
        key = (name, job_name)
        permissions = job.get('permissions', top_permissions)
        expected_permissions = WRITE_JOBS.get(key, top_permissions)
        require(permissions == expected_permissions, location, 'unexpected effective permissions')
        if key not in WRITE_JOBS:
            require(isinstance(permissions, dict)
                    and all(value in ('read', 'none') for value in permissions.values()),
                    location, 'unreviewed write permissions')
        require('uses' not in job and 'secrets' not in job, location, 'unreviewed reusable workflow/secrets')
        require(job.get('continue-on-error', 'false') == 'false', location, 'job failure must remain blocking')
        job_fields = {field: value for field, value in job.items() if field != 'steps'}
        require(not references(job_fields, SECRET), location, 'secrets must be confined to gated steps')
        require(not references(job_fields, TOKEN), location, 'token must be confined to reviewed steps')
        timeout = str(job.get('timeout-minutes', ''))
        require(timeout.isdigit() and 0 < int(timeout) <= 360, location, 'bounded timeout required')
        steps = job.get('steps', [])
        require(isinstance(steps, list) and bool(steps), location, 'explicit steps required')
        if not isinstance(steps, list):
            continue
        cloud_count = 0
        for index, step in enumerate(steps):
            here = f'{location}.steps[{index}]'
            if not isinstance(step, dict):
                require(False, here, 'step must be a mapping')
                continue
            if 'uses' in step:
                require(bool(ACTION.fullmatch(str(step['uses']))), here, 'action must use a full commit SHA')
                if str(step['uses']).startswith('actions/checkout@'):
                    require(step.get('with', {}).get('persist-credentials') == 'false', here,
                            'checkout must not persist credentials')
            if step.get('continue-on-error', 'false') != 'false':
                require(key in {('audit-integration.yml', 'verify'), ('uqam-revision.yml', 'revision')}
                        and step.get('id') in {'short_tests', 'long_tests'}
                        and step.get('continue-on-error') == 'true', here,
                        'only explicitly aggregated regression suites may continue on failure')
            if references(step, SECRET):
                cloud_count += 1
                input_name = CLOUD_JOBS.get(key)
                require(input_name is not None, here, 'unreviewed cloud-secret consumer')
                allowed = {MANUAL_MAIN + " && inputs.narrated_review == true"}
                if input_name == 'mode':
                    base = MANUAL_MAIN + " && inputs.mode == 'azure'"
                    allowed = {base, base + " && steps.speech.outputs.available == 'true'"}
                require(condition(step.get('if')) in allowed, here, 'explicit manual/main/paid gate required')
                env = step.get('env', {})
                secret_env = {k: v for k, v in env.items() if references(v, SECRET)} if isinstance(env, dict) else {}
                require(secret_env == CLOUD_ENV, here, 'only the reviewed Speech credentials are permitted')
                require(not references({k: v for k, v in step.items() if k != 'env'}, SECRET), here,
                        'secrets may only appear in step environment')
            if references(step, TOKEN):
                allowed_names = {
                    ('public-audit.yml', 'audit'): {'Scan reachable history, tracked files and bounded public GitHub surfaces'},
                    ('audit-integration.yml', 'verify'): {'Save integration branch checkpoint only', 'Record machine results on the tested commit'},
                    ('publish-archive-preview.yml', 'publish'): {'Publish only the previously verified synthetic clip'},
                }
                require(step.get('name') in allowed_names.get(key, set()), here, 'unreviewed token consumer')
                token_env = {k: v for k, v in step.get('env', {}).items() if references(v, TOKEN)}
                require(token_env == {'GH_TOKEN': '${{ github.token }}'}, here,
                        'token must use the reviewed environment binding')
                require(not references({k: v for k, v in step.items() if k != 'env'}, TOKEN), here,
                        'token may only appear in step environment')
        if key in CLOUD_JOBS:
            require(cloud_count == (2 if CLOUD_JOBS[key] == 'mode' else 1), location,
                    'reviewed narration steps must remain covered')
            dispatch = events.get('workflow_dispatch') or {}
            inputs = dispatch.get('inputs', {})
            setting = inputs.get(CLOUD_JOBS[key], {})
            require(setting.get('default') == ('silent' if CLOUD_JOBS[key] == 'mode' else 'false'),
                    location, 'paid narration cannot be the default')
        validate_exception(name, job_name, job, events, require)
    return errors


def validate_exception(name, job_name, job, events, require):
    """Protect the two existing administrative operations and sensitive artifacts."""
    steps = job.get('steps', [])
    by_name = {step.get('name'): step for step in steps if isinstance(step, dict)}
    here = f'jobs.{job_name}'
    if (name, job_name) == ('publish-archive-preview.yml', 'publish'):
        require(condition(job.get('if')) == PUBLISH_GATE, here, 'publication must exclude PRs and bind owner/main')
        require(job.get('needs') == 'check', here, 'publication must depend on checks')
        require((events.get('push') or {}).get('branches') == ['main'], 'on.push', 'publication push must bind main')
        run = by_name.get('Publish only the previously verified synthetic clip', {}).get('run', '')
        for anchor in ('gh run download 35561938845', 'sha256sum --check --status',
                       'gh release create conversation-archive-intro-v1',
                       '--target 5361489bc68c932d84cf509256f53c63acb729cd',
                       "if [ \"$existing\" != 0 ]; then", 'exit 0'):
            require(anchor in run, here, 'verified fixed preview and existing-release preservation required')
    if (name, job_name) == ('audit-integration.yml', 'verify'):
        require(set(events) == {'push', 'workflow_dispatch'}, 'on', 'integration write job cannot run on PRs')
        require((events.get('push') or {}).get('branches') == ['main', INTEGRATION_REF.removeprefix('refs/heads/')],
                'on.push', 'integration push branches must stay bounded')
        checkpoint = by_name.get('Save integration branch checkpoint only', {})
        gate = f"always() && github.ref == '{INTEGRATION_REF}' && steps.prepare.outcome == 'success'"
        require(condition(checkpoint.get('if')) == gate, here, 'checkpoint gate must bind the integration branch')
        require(f'git push origin HEAD:{INTEGRATION_REF}' in checkpoint.get('run', ''), here,
                'checkpoint must push only the named integration branch')
        status = by_name.get('Record machine results on the tested commit', {})
        require(condition(status.get('if')) == "always() && steps.source.outcome == 'success'", here,
                'status write requires recorded source')
        aggregate = by_name.get('Require both test suites', {})
        require(condition(aggregate.get('if')) == 'always()', here, 'regression aggregation must always run')
        for suite in ('short_tests', 'long_tests', 'source', 'lint'):
            require("test '${{ steps." + suite + ".outcome }}' = success" in aggregate.get('run', ''),
                    here, 'continued regression failures must remain blocking')
    if (name, job_name) == ('uqam-revision.yml', 'revision'):
        aggregate = by_name.get('Require both regression suites to pass', {})
        require(condition(aggregate.get('if')) == "steps.short_tests.outcome != 'success' || steps.long_tests.outcome != 'success'"
                and aggregate.get('run', '').strip() == 'exit 1', here,
                'continued regression failures must remain blocking')
    if name == 'history-cleanup.yml':
        require(not references(job, TOKEN), here, 'history trial must not receive a token')
        require(not any('--publish' in s.get('run', '') for s in steps if isinstance(s, dict)), here,
                'history trial must not publish a rewrite')
    if name == 'public-audit.yml':
        uploads = [s for s in steps if isinstance(s, dict)
                   and s.get('uses', '').startswith('actions/upload-artifact@')]
        require(len(uploads) == 1 and uploads[0].get('with', {}).get('path') == '${{ runner.temp }}/public-audit-summary.json',
                here, 'only the sanitized audit summary may be uploaded')


def validate_repository(root=ROOT):
    root = Path(root)
    policy = read_yaml(root / '.github/workflow-policy.yaml')
    if policy.get('schema_version') != '1' or not isinstance(policy.get('workflows'), dict):
        raise ValueError('Unsupported workflow policy manifest')
    classifications = policy['workflows']
    folder = root / '.github/workflows'
    paths = {p.relative_to(folder).as_posix(): p for p in folder.rglob('*')
             if p.suffix in ('.yml', '.yaml') and p.is_file()}
    errors = [f'{name}: classification missing' for name in sorted(paths.keys() - classifications.keys())]
    errors += [f'{name}: classified workflow missing' for name in sorted(classifications.keys() - paths.keys())]
    for name in sorted(paths.keys() & classifications.keys()):
        try:
            if paths[name].is_symlink():
                raise ValueError('Workflow symlinks are not supported')
            errors.extend(validate_workflow(name, read_yaml(paths[name]), classifications[name]))
        except (ValueError, TypeError, AttributeError, yaml.YAMLError):
            errors.append(f'{name}: invalid workflow structure')
    return {'workflow_count': len(paths), 'status': 'failed' if errors else 'passed', 'violations': errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(argv)
    try:
        result = validate_repository(args.root)
    except (OSError, ValueError, yaml.YAMLError):
        result = {'status': 'failed', 'violations': ['Unable to read workflow policy inputs']}
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
