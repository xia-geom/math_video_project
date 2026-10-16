"""Offline quality screening must preserve evidence and fail closed."""
import csv
import json
import math
import shutil
import struct
import subprocess
import wave

import pytest

from tools.narration_quality import (
    AuditConfig,
    AuditError,
    AuditPair,
    audit_pairs,
    detect_silences,
    discover_pairs,
    load_manifest,
    pair_from_provenance,
    parse_breaks,
    parse_silencedetect,
    sha256,
    write_report,
)

ENTRIES = [
    {'lesson_id': 'first_lesson', 'order': 1, 'scene_class': 'FirstLesson', 'title': 'First'},
    {'lesson_id': 'second_lesson', 'order': 2, 'scene_class': 'SecondLesson', 'title': 'Second'},
]


def fixture_pair(tmp_path, number=1, *, spoken='Une phrase. Puis une autre.', audio=b'fixture audio'):
    folder = tmp_path / str(number)
    narration = folder / 'narration'
    narration.mkdir(parents=True)
    video = folder / 'arbitrary-video-name.mp4'
    video.write_bytes(f'video {number}'.encode())
    clip = narration / 'clip.wav'
    clip.write_bytes(audio)
    entry = ENTRIES[number - 1]
    data = {
        'artifact_binding': {'video_sha256': sha256(video)},
        'voiceovers': [{'scene_class': entry['scene_class'], 'input_text': spoken,
                       'final_audio': {'path': 'clip.wav', 'sha256': sha256(clip)},
                       'start_seconds': 5.0, 'end_seconds': 15.0, 'duration_seconds': 10.0}],
    }
    provenance = narration / 'provenance.json'
    provenance.write_text(json.dumps(data))
    (folder / 'STATUS.json').write_text(json.dumps({'lesson_id': entry['lesson_id'],
        'global_number': number, 'video_sha256': sha256(video)}))
    return AuditPair(video, provenance)


def fake_detector(path, config):
    return {'duration_seconds': 10.0,
            'intervals': parse_silencedetect('silence_start: 1\nsilence_end: 4 | silence_duration: 3',
                                             10.0, config)}


def test_breaks_keep_strength_and_sum_adjacent_pauses():
    parsed = parse_breaks("Bonjour.<break time='900ms'/><bookmark mark='b'/><break time='1.2s'/>"
                          "Suite.<break strength='strong'/>")
    assert [row['seconds'] for row in parsed['breaks']] == [0.9, 1.2, None]
    assert parsed['max_contiguous_seconds'] == pytest.approx(2.1)
    assert parsed['has_explicit_long_break']
    assert parsed['has_unquantified_break']
    with pytest.raises(AuditError, match='break time'):
        parse_breaks('<break time="two seconds"/>')


def test_silence_parser_separates_boundaries_and_keeps_unclosed_trailing_interval():
    text = '\n'.join(['silence_start: 0', 'silence_end: 2 | silence_duration: 2',
                      'silence_start: 3', 'silence_end: 6 | silence_duration: 3',
                      'silence_start: 8'])
    intervals = parse_silencedetect(text, 10, AuditConfig())
    assert [row['boundary'] for row in intervals] == [True, False, True]
    assert intervals[1]['requires_review']
    assert all(row['requires_review'] for row in intervals)
    assert intervals[-1]['end_inferred_from_probe']
    with pytest.raises(AuditError, match='Unclosed'):
        parse_silencedetect('silence_start: 1\nsilence_start: 2', 10, AuditConfig())


@pytest.mark.parametrize('kwargs', [{'jobs': True}, {'jobs': 2.5}, {'boundary_tolerance': 1000},
                                   {'noise_db': float('nan')}, {'min_silence': 0}])
def test_invalid_config_cannot_hide_flags(kwargs):
    with pytest.raises(AuditError):
        AuditConfig(**kwargs)


def test_deduplicates_detection_but_preserves_occurrences_and_hashes_every_copy(tmp_path):
    one = fixture_pair(tmp_path, 1)
    two = fixture_pair(tmp_path, 2)
    calls = []

    def detector(path, config):
        calls.append(path)
        return fake_detector(path, config)

    report = audit_pairs([one, two], entries=ENTRIES, detector=detector)
    assert len(calls) == 1
    assert report['summary']['unique_final_audio_clips'] == 1
    assert report['summary']['verified_audio_paths'] == 2
    assert report['summary']['voiceover_occurrences'] == 2
    assert report['summary']['affected_lesson_count'] == 2
    assert len(report['flags']) == 2
    assert report['flags'][0]['video_start_seconds'] == 6
    (two.provenance.parent / 'clip.wav').write_bytes(b'corrupted duplicate copy')
    with pytest.raises(AuditError, match='SHA-256 mismatch'):
        audit_pairs([one, two], entries=ENTRIES, detector=detector)
    assert len(calls) == 1  # Full evidence validation precedes decoding.


def test_mismatched_video_missing_audio_and_missing_voiceover_fail_closed(tmp_path):
    pair = fixture_pair(tmp_path)
    original = pair.video.read_bytes()
    pair.video.write_bytes(b'changed video')
    with pytest.raises(AuditError, match='SHA-256 mismatch'):
        audit_pairs([pair], entries=ENTRIES, detector=fake_detector)
    pair.video.write_bytes(original)
    clip = pair.provenance.parent / 'clip.wav'
    clip.unlink()
    with pytest.raises(AuditError, match='Cannot read artifact'):
        audit_pairs([pair], entries=ENTRIES, detector=fake_detector)
    data = json.loads(pair.provenance.read_text())
    data['voiceovers'] = []
    pair.provenance.write_text(json.dumps(data))
    with pytest.raises(AuditError):
        audit_pairs([pair], entries=ENTRIES, detector=fake_detector)


def test_duplicate_provenance_must_agree_and_never_duplicates_occurrences(tmp_path):
    pair = fixture_pair(tmp_path)
    second = pair.provenance.with_name('copy.json')
    second.write_bytes(pair.provenance.read_bytes())
    duplicate = AuditPair(pair.video, second)
    report = audit_pairs([pair, duplicate], entries=ENTRIES, detector=fake_detector)
    assert report['summary']['provenance_files'] == 2
    assert report['summary']['voiceover_occurrences'] == 1
    data = json.loads(second.read_text())
    data['voiceovers'][0]['input_text'] = 'A different authored input.'
    second.write_text(json.dumps(data))
    with pytest.raises(AuditError, match='Conflicting provenance'):
        audit_pairs([pair, duplicate], entries=ENTRIES, detector=fake_detector)
    alias = pair.video.with_name('same-bytes-another-name.mp4')
    alias.write_bytes(pair.video.read_bytes())
    with pytest.raises(AuditError, match='same video hash'):
        audit_pairs([pair, AuditPair(alias, second)], entries=ENTRIES, detector=fake_detector)


@pytest.mark.parametrize('change, message', [('tamper', 'provenance SHA-256 mismatch'),
                                          ('count', 'voiceovers count mismatch'),
                                          ('signature', 'input_signature disagrees')])
def test_status_cross_checks_provenance_integrity_counts_and_source_signature(tmp_path, change, message):
    pair = fixture_pair(tmp_path)
    data = json.loads(pair.provenance.read_text())
    data['artifact_binding']['input_signature'] = 'a' * 64
    pair.provenance.write_text(json.dumps(data))
    status_path = pair.video.parent / 'STATUS.json'
    status = json.loads(status_path.read_text())
    status.update(input_signature='a' * 64, source_sha256='c' * 64,
                  narration_evidence={'sha256': sha256(pair.provenance), 'voiceovers': 1})
    if change == 'tamper':
        data['voiceovers'][0]['input_text'] = 'Modified narration.'
        pair.provenance.write_text(json.dumps(data))
    elif change == 'count':
        status['narration_evidence']['voiceovers'] = 2
    else:
        status['input_signature'] = 'b' * 64
    status_path.write_text(json.dumps(status))
    with pytest.raises(AuditError, match=message):
        audit_pairs([pair], entries=ENTRIES, detector=fake_detector)


def test_metadata_and_probed_timing_must_agree(tmp_path):
    pair = fixture_pair(tmp_path)
    data = json.loads(pair.provenance.read_text())
    data['voiceovers'][0]['end_seconds'] = 20
    pair.provenance.write_text(json.dumps(data))
    with pytest.raises(AuditError, match='Invalid voiceover timing'):
        audit_pairs([pair], entries=ENTRIES, detector=fake_detector)
    data['voiceovers'][0]['end_seconds'] = 15
    pair.provenance.write_text(json.dumps(data))
    with pytest.raises(AuditError, match='Probed audio duration disagrees'):
        audit_pairs([pair], entries=ENTRIES,
                    detector=lambda p, c: {'duration_seconds': 12, 'intervals': []})


def test_entirely_silent_clip_cannot_report_clean(tmp_path):
    pair = fixture_pair(tmp_path)

    def silent(path, config):
        return {'duration_seconds': 10, 'intervals': parse_silencedetect(
            'silence_start: 0\nsilence_end: 10 | silence_duration: 10', 10, config)}

    report = audit_pairs([pair], entries=ENTRIES, detector=silent)
    assert report['status'] == 'review_required'
    assert report['summary']['boundary_occurrence_intervals'] == 1
    assert report['summary']['internal_occurrence_intervals'] == 0
    assert report['summary']['review_required_occurrence_intervals'] == 1


def test_malformed_voiceover_is_a_structured_error(tmp_path):
    pair = fixture_pair(tmp_path)
    data = json.loads(pair.provenance.read_text())
    data['voiceovers'] = [None]
    pair.provenance.write_text(json.dumps(data))
    with pytest.raises(AuditError, match='Malformed scene/voiceover'):
        audit_pairs([pair], entries=ENTRIES, detector=fake_detector)


def test_long_authored_break_is_not_an_automatic_exemption_and_csv_is_reviewable(tmp_path):
    pair = fixture_pair(tmp_path, spoken='Début.<break time="3s"/>Fin.')
    report = audit_pairs([pair], entries=ENTRIES, detector=fake_detector)
    assert report['status'] == 'review_required'
    assert 'explicit_long_break_candidate_alignment_unverified' in report['flags'][0]['flags']
    output = tmp_path / 'new-audit'
    write_report(report, output)
    rows = list(csv.DictReader((output / 'review.csv').open()))
    assert rows[0]['lesson_id'] == 'first_lesson'
    assert rows[0]['number'] == '1'
    assert '<break time="3s"/>' in rows[0]['input_text']
    assert rows[0]['audio_sha256'] == sha256(pair.provenance.parent / 'clip.wav')
    before = (output / 'report.json').read_bytes()
    with pytest.raises(AuditError, match='already exists'):
        write_report(report, output)
    assert (output / 'report.json').read_bytes() == before


def test_catalogue_identity_is_not_inferred_from_filename_or_number(tmp_path):
    pair = fixture_pair(tmp_path)
    status = pair.video.parent / 'STATUS.json'
    data = json.loads(status.read_text())
    data['lesson_id'] = 'second_lesson'
    status.write_text(json.dumps(data))
    with pytest.raises(AuditError, match='conflicting catalogue identity'):
        audit_pairs([pair], entries=ENTRIES, detector=fake_detector)


def test_root_manifest_and_standalone_discovery_bind_actual_bytes(tmp_path):
    pair = fixture_pair(tmp_path)
    assert discover_pairs(tmp_path, tmp_path) == [AuditPair(pair.video.resolve(), pair.provenance.resolve())]
    assert pair_from_provenance(pair.provenance) == AuditPair(pair.video.resolve(), pair.provenance.resolve())
    manifest = tmp_path / 'pairs.json'
    manifest.write_text(json.dumps({'pairs': [{'video': str(pair.video.relative_to(tmp_path)),
        'provenance': str(pair.provenance.relative_to(tmp_path))}]}))
    assert load_manifest(manifest) == [AuditPair(pair.video.resolve(), pair.provenance.resolve())]
    (tmp_path / 'unbound.mp4').write_bytes(b'unbound video')
    with pytest.raises(AuditError, match='No hash-matching provenance'):
        discover_pairs(tmp_path, tmp_path)
    (pair.video.parent / 'STATUS.json').unlink()
    with pytest.raises(AuditError, match='needs --video'):
        pair_from_provenance(pair.provenance)


def test_no_flags_does_not_validate_pronunciation(tmp_path):
    pair = fixture_pair(tmp_path)
    report = audit_pairs([pair], entries=ENTRIES,
                         detector=lambda p, c: {'duration_seconds': 10, 'intervals': []})
    assert report['status'] == 'no_flags_detected'
    assert report['pronunciation'] == 'not_assessed'
    assert report['listening'] == 'not_performed'
    assert report['release_ready'] is False


def test_cli_review_exit_code_errors_and_immutable_output(tmp_path, monkeypatch, capsys):
    from scripts import audit_narration_quality as cli

    pair = fixture_pair(tmp_path)
    report = audit_pairs([pair], entries=ENTRIES, detector=fake_detector)
    monkeypatch.setattr(cli, 'audit_pairs', lambda *args, **kwargs: report)
    output = tmp_path / 'cli-audit'
    argv = ['--provenance', str(pair.provenance), '--video', str(pair.video), '--output', str(output)]
    assert cli.main([*argv, '--fail-on-review']) == 2
    before = (output / 'report.json').read_bytes()
    assert cli.main(argv) == 1
    assert (output / 'report.json').read_bytes() == before
    argv[-1] = str(tmp_path / 'review-without-fail')
    assert cli.main(argv) == 0
    argv[-1] = str(tmp_path / 'error-audit')
    argv[1] = str(tmp_path / 'missing-provenance.json')
    assert cli.main(argv) == 1
    assert json.loads((tmp_path / 'error-audit/report.json').read_text())['status'] == 'error'
    capsys.readouterr()


@pytest.mark.skipif(not shutil.which('ffmpeg') or not shutil.which('ffprobe'), reason='ffmpeg/ffprobe unavailable')
def test_real_ffmpeg_finds_synthetic_tone_silence_tone(tmp_path):
    path = tmp_path / 'tone-silence-tone.wav'
    rate = 16000
    tone = b''.join(struct.pack('<h', round(16000 * math.sin(2 * math.pi * 440 * i / rate)))
                    for i in range(rate))
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        wav.writeframes(tone + b'\0\0' * round(2.6 * rate) + tone)
    original = sha256(path)
    result = detect_silences(path, AuditConfig())
    assert result['duration_seconds'] == pytest.approx(4.6, abs=0.01)
    assert len(result['intervals']) == 1
    event = result['intervals'][0]
    assert event['start_seconds'] == pytest.approx(1.0, abs=0.01)
    assert event['end_seconds'] == pytest.approx(3.6, abs=0.01)
    assert event['duration_seconds'] == pytest.approx(2.6, abs=0.01)
    assert event['requires_review'] and not event['boundary']
    assert sha256(path) == original


@pytest.mark.skipif(not shutil.which('ffmpeg') or not shutil.which('ffprobe'), reason='ffmpeg/ffprobe unavailable')
@pytest.mark.parametrize('layout', ['all_silent', 'leading', 'trailing'])
def test_real_ffmpeg_boundary_gaps_still_require_review(tmp_path, layout):
    path = tmp_path / f'{layout}.wav'
    rate = 16000
    tone = b''.join(struct.pack('<h', round(16000 * math.sin(2 * math.pi * 440 * i / rate)))
                    for i in range(rate))
    silence = b'\0\0' * round(2.6 * rate)
    samples = {'all_silent': silence, 'leading': silence + tone, 'trailing': tone + silence}[layout]
    with wave.open(str(path), 'wb') as wav:
        wav.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        wav.writeframes(samples)
    result = detect_silences(path, AuditConfig())
    assert len(result['intervals']) == 1
    assert result['intervals'][0]['boundary']
    assert result['intervals'][0]['requires_review']


def test_decode_error_cannot_be_a_clean_screen(monkeypatch, tmp_path):
    from tools import narration_quality as quality

    monkeypatch.setattr(quality.shutil, 'which', lambda name: name)

    def run(command, **kwargs):
        if command[0] == 'ffprobe':
            return subprocess.CompletedProcess(command, 0, json.dumps(
                {'format': {'duration': '10'}, 'streams': [{'codec_type': 'audio'}]}), '')
        assert '-xerror' in command
        raise subprocess.CalledProcessError(1, command, stderr='corrupt packet')

    monkeypatch.setattr(quality.subprocess, 'run', run)
    with pytest.raises(AuditError, match='Audio decoding/analysis failed'):
        detect_silences(tmp_path / 'broken.mp3', AuditConfig())
