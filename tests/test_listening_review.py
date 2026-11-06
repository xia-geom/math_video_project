"""Listening decisions bind exact report, utterance interval and original/copied media."""
import copy
import json
from pathlib import Path

import pytest

from scripts.review_narration_flags import main
from tools.listening_review import digest, prepare_queue, validate_decisions, validate_queue


@pytest.fixture
def prepared(tmp_path):
    source = tmp_path / 'original'
    source.mkdir()
    audio = source / 'utterance.mp3'
    movie = source / 'complete.mp4'
    audio.write_bytes(b'Synthetic unchanged utterance; not actual encoded audio.')
    movie.write_bytes(b'Synthetic complete-video identity; not actual encoded video.')
    audio_hash, video_hash = digest(audio), digest(movie)
    report = tmp_path / 'report.json'
    report.write_text(json.dumps({'videos': [{
        'lesson_id': 'synthetic_lesson', 'title': 'Synthetic </script> title',
        'video_path': str(movie), 'video_sha256': video_hash,
    }], 'flags': [{
        'lesson_id': 'synthetic_lesson', 'video_sha256': video_hash,
        'audio_sha256': audio_hash, 'voiceover_index': 4, 'audio_paths': [str(audio)],
        'start_seconds': 2.0, 'end_seconds': 4.0, 'clip_duration_seconds': 8.0,
        'video_start_seconds': 12.0, 'video_end_seconds': 14.0,
        'plain_text': 'Synthetic utterance.', 'flags': ['internal_silence'],
    }]}))
    expected = digest(report)
    queue = tmp_path / 'queue'
    manifest = prepare_queue(report, expected, queue, ['synthetic_lesson'])
    return {'root': tmp_path, 'queue': queue, 'report': report, 'expected': expected,
            'audio': audio, 'video': movie, 'manifest': manifest}


def decision_file(prepared):
    manifest = prepared['manifest']
    flag = manifest['flags'][0]
    return {'schema_version': 1, 'queue_id': manifest['queue_id'],
            'report_sha256': prepared['expected'], 'full_video_reviews': [],
            'decisions': [{'flag_id': flag['flag_id'], 'binding': copy.deepcopy(flag['binding']),
                           'reviewer': 'Synthetic reviewer', 'reason': 'Synthetic listening decision fixture.',
                           'checked_at': '2026-11-06T12:00:00Z', 'listened': True,
                           'disposition': 'needs_more_review'}]}


def validate(prepared, decisions):
    return validate_decisions(prepared['queue'], decisions, prepared['expected'])


def replace(path, content):
    path.unlink()
    path.write_bytes(content)


def test_preparation_keeps_unchanged_media_and_creates_no_decisions(prepared):
    manifest = validate_queue(prepared['queue'], prepared['expected'])
    assert manifest['listening'] == 'not_performed'
    assert manifest['release_ready'] is False
    assert not (prepared['queue'] / 'listening-decisions.json').exists()
    for name, media in manifest['media'].items():
        path = prepared['queue'] / name
        assert path.read_bytes() == Path(media['source_path']).read_bytes()
        assert path.stat().st_mode & 0o222 == 0
    html = (prepared['queue'] / 'index.html').read_text()
    assert 'player.controls=true' in html and 'audio.controls=true' in html
    assert 'Historical audio' in html and 'predates later wording changes' in html
    assert '</script> title' not in html
    assert str(prepared['root']) not in html
    assert 'full_video_reviews' in html and 'listened_entire_video' in html


def test_flag_ids_are_stable_across_queue_destinations(prepared):
    second = prepare_queue(prepared['report'], prepared['expected'], prepared['root'] / 'second', ['synthetic_lesson'])
    assert second['flags'][0]['flag_id'] == prepared['manifest']['flags'][0]['flag_id']
    with pytest.raises(ValueError, match='never overwritten'):
        prepare_queue(prepared['report'], prepared['expected'], prepared['queue'], ['synthetic_lesson'])


@pytest.mark.parametrize('value', [False, 'false', 'true', 0, 1, None, [], {}, [True]])
def test_flag_listening_confirmation_requires_actual_true(prepared, value):
    decisions = decision_file(prepared)
    decisions['decisions'][0]['listened'] = value
    with pytest.raises(ValueError, match='boolean listened=true'):
        validate(prepared, decisions)


def test_missing_confirmation_unknown_and_duplicate_decisions_are_rejected(prepared):
    decisions = decision_file(prepared)
    del decisions['decisions'][0]['listened']
    with pytest.raises(ValueError, match='Unexpected flag-decision'):
        validate(prepared, decisions)
    decisions = decision_file(prepared)
    decisions['decisions'][0]['flag_id'] = 'unknown'
    with pytest.raises(ValueError, match='Unknown or duplicate'):
        validate(prepared, decisions)
    decisions = decision_file(prepared)
    decisions['decisions'].append(copy.deepcopy(decisions['decisions'][0]))
    with pytest.raises(ValueError, match='Unknown or duplicate'):
        validate(prepared, decisions)


@pytest.mark.parametrize(('field', 'replacement'), [
    ('reviewer', ''), ('reason', '  '), ('checked_at', '2026-11-06'),
    ('disposition', 'approved'),
])
def test_named_dated_reason_and_known_disposition_are_required(prepared, field, replacement):
    decisions = decision_file(prepared)
    decisions['decisions'][0][field] = replacement
    with pytest.raises(ValueError):
        validate(prepared, decisions)


def test_interval_and_report_bindings_cannot_be_relabelled(prepared):
    decisions = decision_file(prepared)
    decisions['decisions'][0]['binding']['start_seconds'] = 1.0
    with pytest.raises(ValueError, match='binding changed'):
        validate(prepared, decisions)
    decisions = decision_file(prepared)
    decisions['report_sha256'] = '0' * 64
    with pytest.raises(ValueError, match='different queue/report'):
        validate(prepared, decisions)


@pytest.mark.parametrize('which', ['original_audio', 'original_video', 'copied_audio', 'copied_video',
                                   'original_report', 'copied_report', 'html'])
def test_replaced_source_or_copy_invalidates_decisions(prepared, which):
    manifest = prepared['manifest']
    paths = {'original_audio': prepared['audio'], 'original_video': prepared['video'],
             'copied_audio': prepared['queue'] / manifest['flags'][0]['audio_file'],
             'copied_video': prepared['queue'] / manifest['videos'][0]['file'],
             'original_report': prepared['report'], 'copied_report': prepared['queue'] / 'screen-report.json',
             'html': prepared['queue'] / 'index.html'}
    replace(paths[which], b'Replacement synthetic bytes.')
    with pytest.raises(ValueError):
        validate(prepared, decision_file(prepared))


def test_flag_decisions_never_imply_full_video_review(prepared):
    result = validate(prepared, decision_file(prepared))
    assert result['flag_decisions'] == 1 and result['pending_flags'] == 0
    assert result['full_video_reviews'] == 0
    assert result['ledger_checks_updated'] is False and result['release_ready'] is False
    decisions = decision_file(prepared)
    decisions['decisions'][0]['coverage'] = 'complete'
    with pytest.raises(ValueError, match='cannot record full-video approval'):
        validate(prepared, decisions)
    decisions = decision_file(prepared)
    decisions['narration'] = 'passed'
    with pytest.raises(ValueError, match='no approval status'):
        validate(prepared, decisions)


def full_review(prepared):
    video = prepared['manifest']['videos'][0]
    return {'video_id': video['video_id'], 'binding': copy.deepcopy(video['binding']),
            'reviewer': 'Synthetic reviewer', 'reason': 'Synthetic complete-review fixture.',
            'checked_at': '2026-11-06T12:00:00Z', 'disposition': 'needs_more_review',
            'listened_entire_video': True, 'watched_entire_video': True}


@pytest.mark.parametrize('field', ['listened_entire_video', 'watched_entire_video'])
@pytest.mark.parametrize('value', [False, 'true', 1, None])
def test_full_video_confirmations_are_separate_strict_booleans(prepared, field, value):
    decisions = decision_file(prepared)
    row = full_review(prepared)
    row[field] = value
    decisions['full_video_reviews'] = [row]
    with pytest.raises(ValueError, match='separate complete listening and viewing'):
        validate(prepared, decisions)


def test_full_video_records_validate_without_updating_ledger(prepared):
    decisions = decision_file(prepared)
    decisions['decisions'] = []
    decisions['full_video_reviews'] = [full_review(prepared)]
    result = validate(prepared, decisions)
    assert result['pending_flags'] == 1 and result['full_video_reviews'] == 1
    assert result['ledger_checks_updated'] is False and result['release_ready'] is False
    decisions['full_video_reviews'].append(copy.deepcopy(decisions['full_video_reviews'][0]))
    with pytest.raises(ValueError, match='duplicate full-video'):
        validate(prepared, decisions)


def test_cli_preparation_rejects_locations_outside_ignored_artifacts(prepared, capsys):
    record = prepared['root'] / 'record.json'
    record.write_text(json.dumps({'existing_audio_analysis': {'output_report_sha256': prepared['expected']}}))
    result = main(['--record', str(record), 'prepare', '--report', str(prepared['report']),
                   '--output', str(prepared['root'] / 'unsafe'), '--lessons', 'synthetic_lesson'])
    assert result == 1
    assert 'ignored review_artifacts' in capsys.readouterr().out
    assert not (prepared['root'] / 'unsafe').exists()
