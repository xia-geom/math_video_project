"""Regression checks for formatting, read-only review and comparison filenames."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tools.video_audit.tests.test_render_script import ARTIFACT, SCENE_FILE, render_project  # noqa: F401

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


@pytest.mark.parametrize('quality', ['ql', 'qh'])
def test_voice_comparisons_follow_global_numbering_without_mirroring_previews(render_project, quality):
    root = render_project
    wrapper = root / 'scripts/render_all_voices.sh'
    shutil.copy2(ROOT / 'scripts/render_all_voices.sh', wrapper)
    wrapper.chmod(0o755)
    env = os.environ.copy()
    env.update(REAL_PYTHON=sys.executable, RENDER_PYTHON=str(root / '.venv/bin/python'),
               GOOGLE_DRIVE_VIDEO_DIR=str(root / 'drive'), MOCK_NO_OUTPUT='0',
               SPEECH_KEY='unit-test-placeholder', SPEECH_REGION='unit-test-placeholder')
    env.pop('RENDER_SKIP_DRIVE_COPY', None)
    result = subprocess.run([str(wrapper), SCENE_FILE, 'CompositionFonctionsFR', quality],
                            cwd=root, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    folder = root / 'dist' / ARTIFACT if quality == 'qh' else root / 'dist/_previews/ql' / ARTIFACT
    stem = ARTIFACT if quality == 'qh' else ARTIFACT + '__ql'
    for voice in ('Sylvie', 'Jean', 'Antoine', 'Thierry'):
        assert (folder / f'{stem}_fr-CA-{voice}Neural.mp4').read_bytes() == b'fake-mp4'
    assert len(list((root / 'drive').rglob('*.mp4'))) == (4 if quality == 'qh' else 0)
    assert not (folder / f'{stem}.mp4').exists()
