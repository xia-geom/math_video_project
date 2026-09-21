"""Regression checks for migration formatting and read-only course review."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_generated_playlist_uses_git_safe_line_endings():
    payload = (ROOT / 'curriculum/playlist.csv').read_bytes()
    assert b'\r' not in payload
    assert payload.endswith(b'\n')


def test_course_review_is_read_only_and_never_synthesizes():
    path = ROOT / '.github/workflows/course-numbering.yml'
    workflow = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
    assert 'pull_request' in workflow['on']
    assert 'pull_request_target' not in workflow['on']
    assert workflow['permissions'] == {'contents': 'read'}
    assert 'renumber' not in workflow['jobs']
    assert 'secrets.' not in path.read_text()
    assert 'git push' not in path.read_text()
    for job in workflow['jobs'].values():
        assert all(v in {'read', 'none'} for v in job.get('permissions', {}).values())
        assert int(job['timeout-minutes']) > 0
        for step in job['steps']:
            if step.get('uses', '').startswith('actions/checkout@'):
                assert step['with']['persist-credentials'] == 'false'


def test_deep_audit_includes_delivery_and_workflow_regressions():
    source = (ROOT / 'scripts/course_audit.py').read_text()
    assert 'tools/video_audit/tests' in source
    assert 'tests/test_course_delivery_regressions.py' in source
    assert 'tests/test_public_workflow_policy.py' in source
