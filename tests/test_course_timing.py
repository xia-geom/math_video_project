"""Duration evidence must not turn silent previews into narrated releases."""
from __future__ import annotations

import ast
import contextlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools.course_catalog import load_catalog
from tools.course_timing import assess_duration, load_duration_policy, seconds, validate_timing_records

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('value', [None, True, False, -1, 0, 'nan', 'inf', '-inf', 'not-a-time'])
def test_invalid_duration_is_rejected(value):
    with pytest.raises(ValueError):
        seconds(value)


def test_zero_is_only_allowed_for_an_explicit_pause():
    assert seconds(0, allow_zero=True) == 0
    assert seconds('12.5') == 12.5


def test_no_promotional_duration_is_invented_for_teaching():
    policy = load_duration_policy()
    assert policy['narrated_range_seconds'] is None
    assert policy['numeric_target_status'] == 'not_documented_in_inspected_sources'
    assert policy['allow_clipped_speech'] is False
    assert policy['allow_empty_padding_to_reach_target'] is False


def test_silent_preview_cannot_certify_narrated_length():
    policy = {'narrated_range_seconds': {'minimum': 180, 'maximum': 360}}
    review = assess_duration(240, mode='silent_preview', has_audio=False, policy=policy)
    assert review['status'] == 'not_assessable_from_silent_preview'
    assert review['narrated_duration_verified'] is False
    assert review['release_ready'] is False


@pytest.mark.parametrize('duration,status', [(179, 'outside_range'), (180, 'within_range'),
                                            (360, 'within_range'), (361, 'outside_range')])
def test_explicit_numeric_range_when_owner_supplies_one(duration, status):
    policy = {'narrated_range_seconds': {'minimum': 180, 'maximum': 360}}
    assert assess_duration(duration, mode='azure_review', has_audio=True, policy=policy)['status'] == status


def test_audio_is_not_itself_proof_of_range_compliance():
    result = assess_duration(240, mode='azure_review', has_audio=True, policy=load_duration_policy())
    assert result['status'] == 'numeric_target_not_documented'
    assert result['narrated_duration_verified'] is False
    with pytest.raises(ValueError):
        assess_duration(240, mode='azure_review', has_audio=False, policy=load_duration_policy())


def explain_method():
    # Execute the exact production method with a synthetic clock, not copied timing code.
    # Manim integration/render checks run separately in the established CI runtime.
    tree = ast.parse((ROOT / 'tools/teaching_layout.py').read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'TeachingScene')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'explain')
    env = {'seconds': seconds, 'FadeIn': lambda obj: obj,
           'tts': SimpleNamespace(ssml=lambda x: x, strip_ssml=lambda x: x)}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(ROOT / 'tools/teaching_layout.py'), 'exec'), env)
    return env['explain']


class ClockScene:
    def __init__(self, silent, speech_duration=2):
        self.silent = silent
        self.speech_duration = speech_duration
        self.renderer = SimpleNamespace(time=0.0)
        self.teaching_timeline = []
        self.teaching_page_title = 'À vous'

    def play(self, *objects, run_time):
        self.renderer.time += run_time

    def wait(self, value):
        self.renderer.time += value

    @contextlib.contextmanager
    def voiceover(self, **kwargs):
        start = self.renderer.time
        yield SimpleNamespace(duration=self.speech_duration)
        self.renderer.time = max(self.renderer.time, start + self.speech_duration)


@pytest.mark.parametrize('silent,speech,hold,pause,expected', [
    (True, 20, 3, 0, 3.6), (False, 20, 3, 0, 20),
    (False, 1, 4, 0, 4.6), (False, 9, 6, 6, 15),
    (True, 9, 6, 6, 6.6), (False, 1, 6, 6, 12.6),
])
def test_reading_hold_and_post_question_pause(silent, speech, hold, pause, expected, monkeypatch):
    monkeypatch.delenv('TEACHING_TIMING_PATH', raising=False)
    scene = ClockScene(silent, speech)
    explain_method()(scene, 'Question complète.', object(), hold=hold, pause_after=pause)
    assert scene.renderer.time == pytest.approx(expected)
    mode = 'silent_preview' if silent else 'azure_review'
    assert not validate_timing_records(scene.teaching_timeline, mode=mode)


def test_next_answer_starts_after_the_thinking_pause(monkeypatch, tmp_path):
    path = tmp_path / 'timing.json'
    monkeypatch.setenv('TEACHING_TIMING_PATH', str(path))
    scene = ClockScene(False, 8)
    explain = explain_method()
    explain(scene, 'Question.', object(), hold=6, pause_after=6)
    explain(scene, 'Réponse.', object(), hold=1)
    records = json.loads(path.read_text())
    assert records[0]['speech_context_end'] == pytest.approx(8)
    assert records[0]['end'] == pytest.approx(14)
    assert records[1]['start'] == pytest.approx(14)
    assert not validate_timing_records(records, mode='azure_review')
    records[0]['end'] = 10
    assert validate_timing_records(records, mode='azure_review')


def test_every_new_self_check_has_an_explicit_thinking_pause():
    for entry in load_catalog()[1]:
        if not entry['legacy_id'].startswith('S'):
            continue
        tree = ast.parse((ROOT / entry['scene_file']).read_text())
        calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
                 and getattr(n.func, 'attr', '') == 'explain'
                 and any(k.arg == 'pause_after' for k in n.keywords)]
        assert len(calls) == 1, entry['lesson_id']
        keywords = {k.arg: ast.literal_eval(k.value) for k in calls[0].keywords}
        assert keywords['pause_after'] == 6


def test_timing_records_cannot_claim_speech_completed_early():
    record = {'mode': 'azure_review', 'start': 0, 'visible_from': 0.6,
              'speech_context_end': 4, 'end': 10, 'minimum_visible_seconds': 3,
              'reflection_pause_seconds': 6, 'speech_duration_seconds': 9}
    assert validate_timing_records([record], mode='azure_review')
