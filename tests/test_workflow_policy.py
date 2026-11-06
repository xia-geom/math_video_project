"""Synthetic unsafe changes must fail the all-workflow policy check."""
from copy import deepcopy
from pathlib import Path
from shutil import copytree

import pytest

from scripts.check_workflow_policy import (
    CLOUD_ENV,
    read_yaml,
    validate_repository,
    validate_workflow,
)

ROOT = Path(__file__).resolve().parents[1]


def inputs(name):
    workflow = read_yaml(ROOT / '.github/workflows' / name)
    classification = read_yaml(ROOT / '.github/workflow-policy.yaml')['workflows'][name]
    return workflow, classification


def assert_rejected(name, workflow, classification, reason):
    errors = validate_workflow(name, workflow, classification)
    assert any(reason in error for error in errors), errors


@pytest.mark.parametrize(('path', 'replacement', 'reason'), [
    (('permissions',), 'write-all', 'workflow permissions'),
    (('jobs', 'lint', 'permissions'), {'contents': 'write'}, 'effective permissions'),
    (('jobs', 'lint', 'steps', 0, 'uses'), 'actions/checkout@v7', 'full commit SHA'),
    (('jobs', 'lint', 'steps', 0, 'with', 'persist-credentials'), 'true', 'persist credentials'),
    (('jobs', 'lint', 'timeout-minutes'), '${{ inputs.timeout }}', 'bounded timeout'),
    (('jobs', 'lint', 'continue-on-error'), 'true', 'failure must remain blocking'),
    (('jobs', 'lint', 'steps', 0, 'continue-on-error'), 'true', 'aggregated regression suites'),
    (('env',), {'KEY': '${{ secrets.SYNTHETIC }}'}, 'confined to gated steps'),
    (('jobs', 'lint', 'env'), {'KEY': '${{ secrets["SYNTHETIC"] }}'}, 'confined to gated steps'),
    (('jobs', 'lint', 'secrets'), 'inherit', 'reusable workflow/secrets'),
    (('jobs', 'lint', 'uses'), 'owner/repo/.github/workflows/check.yml@main', 'reusable workflow/secrets'),
])
def test_ordinary_jobs_reject_privilege_and_action_regressions(path, replacement, reason):
    name = 'smoke.yml'
    workflow, classification = inputs(name)
    target = workflow
    for part in path[:-1]:
        target = target[part]
    target[path[-1]] = replacement
    assert_rejected(name, workflow, classification, reason)


@pytest.mark.parametrize('name', ['smoke.yml', 'audit-integration.yml', 'publish-archive-preview.yml'])
def test_new_jobs_do_not_inherit_an_administrative_exception(name):
    workflow, classification = inputs(name)
    workflow['jobs']['unreviewed'] = {
        'permissions': {'contents': 'write'}, 'timeout-minutes': '5',
        'steps': [{'run': 'true'}],
    }
    errors = validate_workflow(name, workflow, classification)
    assert any('unclassified or missing job' in error for error in errors)
    assert any('unexpected effective permissions' in error for error in errors)


@pytest.mark.parametrize('event', ['pull_request_target', 'workflow_run', 'schedule'])
def test_unreviewed_triggers_cannot_bypass_pr_boundaries(event):
    workflow, classification = inputs('smoke.yml')
    workflow['on'][event] = {}
    assert_rejected('smoke.yml', workflow, classification, 'unclassified trigger')


@pytest.mark.parametrize('extension', ['yml', 'yaml'])
def test_discovery_rejects_new_unclassified_workflow_files(tmp_path, extension):
    copytree(ROOT / '.github', tmp_path / '.github')
    path = tmp_path / '.github/workflows' / f'unreviewed.{extension}'
    path.write_text('name: synthetic\non:\n  pull_request:\njobs: {}\n')
    result = validate_repository(tmp_path)
    assert result['status'] == 'failed'
    assert f'unreviewed.{extension}: classification missing' in result['violations']


@pytest.mark.parametrize('suffix', ['', " || true", " || github.event_name == 'pull_request'"])
def test_narration_requires_complete_non_bypassable_gate(suffix):
    name = 'teaching-revision.yml'
    workflow, classification = inputs(name)
    step = next(s for s in workflow['jobs']['review']['steps'] if 'SPEECH_KEY' in s.get('env', {}))
    step['if'] = step['if'] + suffix if suffix else "inputs.narrated_review == true"
    assert_rejected(name, workflow, classification, 'manual/main/paid gate')


def test_cloud_credentials_cannot_move_into_shell_or_new_steps():
    name = 'teaching-revision.yml'
    workflow, classification = inputs(name)
    steps = workflow['jobs']['review']['steps']
    original = next(s for s in steps if 'SPEECH_KEY' in s.get('env', {}))
    original['run'] += '\necho "${{ secrets.SYNTHETIC }}"\n'
    assert_rejected(name, workflow, classification, 'only appear in step environment')
    original['run'] = 'true'
    steps.append(deepcopy(original))
    assert_rejected(name, workflow, classification, 'narration steps must remain covered')


def test_read_only_step_cannot_acquire_speech_credentials_even_with_manual_gate():
    name = 'smoke.yml'
    workflow, classification = inputs(name)
    workflow['jobs']['lint']['steps'].append({
        'if': "github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main' && inputs.narrated_review == true",
        'env': CLOUD_ENV, 'run': 'true',
    })
    assert_rejected(name, workflow, classification, 'unreviewed cloud-secret consumer')


@pytest.mark.parametrize(('name', 'job_name', 'input_name', 'default'), [
    ('teaching-revision.yml', 'review', 'narrated_review', 'true'),
    ('uqam-revision.yml', 'revision', 'narrated_review', 'true'),
    ('uqam-ouvertures.yml', 'review', 'mode', 'azure'),
])
def test_paid_narration_never_becomes_default(name, job_name, input_name, default):
    workflow, classification = inputs(name)
    workflow['on']['workflow_dispatch']['inputs'][input_name]['default'] = default
    assert_rejected(name, workflow, classification, 'cannot be the default')


def test_publishing_exception_rejects_pr_or_arbitrary_release_expansion():
    name = 'publish-archive-preview.yml'
    workflow, classification = inputs(name)
    job = workflow['jobs']['publish']
    job['if'] += ' || true'
    assert_rejected(name, workflow, classification, 'publication must exclude PRs')
    job['if'] = inputs(name)[0]['jobs']['publish']['if']
    step = next(s for s in job['steps'] if 'run' in s)
    step['run'] = step['run'].replace('conversation-archive-intro-v1', 'unreviewed-release')
    assert_rejected(name, workflow, classification, 'verified fixed preview')


def test_integration_checkpoint_is_not_a_generic_write_exception():
    name = 'audit-integration.yml'
    workflow, classification = inputs(name)
    checkpoint = next(s for s in workflow['jobs']['verify']['steps']
                      if s.get('name') == 'Save integration branch checkpoint only')
    checkpoint['if'] = 'always()'
    checkpoint['run'] = 'git push origin HEAD:refs/heads/main'
    errors = validate_workflow(name, workflow, classification)
    assert any('checkpoint gate' in error for error in errors)
    assert any('only the named integration branch' in error for error in errors)
    workflow['on']['pull_request'] = {}
    assert_rejected(name, workflow, classification, 'cannot run on PRs')


def test_history_trial_cannot_turn_into_a_rewrite_publisher():
    name = 'history-cleanup.yml'
    workflow, classification = inputs(name)
    workflow['jobs']['trial']['steps'].append({'run': 'python scripts/cleanup_billing_history.py --publish'})
    assert_rejected(name, workflow, classification, 'must not publish a rewrite')


@pytest.mark.parametrize(('name', 'job_name', 'aggregate'), [
    ('audit-integration.yml', 'verify', 'Require both test suites'),
    ('uqam-revision.yml', 'revision', 'Require both regression suites to pass'),
])
def test_continued_suite_failures_still_have_a_blocking_aggregator(name, job_name, aggregate):
    workflow, classification = inputs(name)
    gate = next(s for s in workflow['jobs'][job_name]['steps'] if s.get('name') == aggregate)
    gate['run'] = 'true'
    assert_rejected(name, workflow, classification, 'continued regression failures must remain blocking')


def test_public_audit_rejects_raw_report_upload_or_new_token_consumer():
    name = 'public-audit.yml'
    workflow, classification = inputs(name)
    steps = workflow['jobs']['audit']['steps']
    upload = next(s for s in steps if s.get('uses', '').startswith('actions/upload-artifact@'))
    upload['with']['path'] = '${{ runner.temp }}/**'
    assert_rejected(name, workflow, classification, 'sanitized audit summary')
    steps.append({'name': 'Unreviewed token use', 'env': {'GH_TOKEN': '${{ github.token }}'}, 'run': 'true'})
    assert_rejected(name, workflow, classification, 'unreviewed token consumer')


def test_duplicate_yaml_keys_fail_instead_of_hiding_permissions(tmp_path):
    path = tmp_path / 'ambiguous.yml'
    path.write_text('permissions: {contents: read}\npermissions: {contents: write}\n')
    with pytest.raises(ValueError, match='Duplicate YAML key'):
        read_yaml(path)
