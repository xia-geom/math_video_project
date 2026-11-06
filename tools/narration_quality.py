"""Offline, hash-bound screening of final narration clips for long silences.

This module never synthesizes, edits, trims or publishes audio. A clean screen
does not establish correct pronunciation, natural delivery or release approval.
"""
from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
_SHA = re.compile(r'[0-9a-f]{64}')
_NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
TIMING_TOLERANCE_SECONDS = 0.1  # Container padding and tracker rounding, not pacing slack.


class AuditError(ValueError):
    """Missing or inconsistent evidence prevents a completed quality screen."""


@dataclass(frozen=True)
class AuditConfig:
    noise_db: float = -40.0
    min_silence: float = 2.0
    boundary_tolerance: float = 0.25
    jobs: int = 4

    def __post_init__(self):
        def finite(value):
            return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)

        if not finite(self.noise_db) or self.noise_db > 0:
            raise AuditError('noise_db must be finite and at most zero')
        if not finite(self.min_silence) or self.min_silence <= 0:
            raise AuditError('min_silence must be finite and positive')
        if not finite(self.boundary_tolerance) or not 0 <= self.boundary_tolerance < self.min_silence:
            raise AuditError('boundary_tolerance must be nonnegative and smaller than min_silence')
        if type(self.jobs) is not int or not 1 <= self.jobs <= 32:
            raise AuditError('jobs must be between 1 and 32')


@dataclass(frozen=True)
class AuditPair:
    video: Path
    provenance: Path
    lesson_id: str | None = None


def sha256(path: Path) -> str:
    try:
        with Path(path).open('rb') as source:
            return hashlib.file_digest(source, 'sha256').hexdigest()
    except OSError as exc:
        raise AuditError(f'Cannot read artifact {path}: {exc}') from exc


def _json(path: Path) -> dict:
    try:
        value = json.loads(Path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise AuditError(f'Cannot read JSON {path}: {exc}') from exc
    if not isinstance(value, dict):
        raise AuditError(f'Expected a JSON object: {path}')
    return value


def _expected_hash(value: Any, context: str) -> str:
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise AuditError(f'Missing or invalid SHA-256: {context}')
    return value


def _video_hash(data: dict, path: Path) -> str:
    binding = data.get('artifact_binding')
    if not isinstance(binding, dict):
        raise AuditError(f'Missing artifact_binding: {path}')
    return _expected_hash(binding.get('video_sha256'), str(path))


def discover_pairs(videos_root: Path, provenance_root: Path,
                   video_glob: str = '*.mp4') -> list[AuditPair]:
    """Match every selected video by bytes; never choose a latest filename."""
    videos_root, provenance_root = Path(videos_root), Path(provenance_root)
    if not videos_root.is_dir() or not provenance_root.is_dir():
        raise AuditError('Both input roots must be existing directories')
    videos = sorted(p for p in videos_root.rglob(video_glob) if p.is_file())
    if not videos:
        raise AuditError('No videos match the selected root and glob')
    index: dict[str, list[Path]] = {}
    for path in sorted(provenance_root.rglob('provenance.json')):
        index.setdefault(_video_hash(_json(path), path), []).append(path)
    pairs = []
    for video in videos:
        matches = index.get(sha256(video), [])
        if not matches:
            raise AuditError(f'No hash-matching provenance for {video}')
        pairs.extend(AuditPair(video.resolve(), p.resolve()) for p in matches)
    return pairs


def load_manifest(path: Path) -> list[AuditPair]:
    """Read {"pairs": [{"video": "...", "provenance": "..."}]}.

    Relative paths resolve beside the manifest. Optional lesson_id must agree
    with the unified catalogue and any identity found in the evidence.
    """
    path = Path(path).resolve()
    rows = _json(path).get('pairs')
    if not isinstance(rows, list) or not rows:
        raise AuditError('A pair manifest needs a nonempty pairs list')
    pairs = []
    for row in rows:
        if not isinstance(row, dict) or not all(isinstance(row.get(k), str)
                                               for k in ('video', 'provenance')):
            raise AuditError('Each manifest pair needs video and provenance paths')
        pairs.append(AuditPair((path.parent / row['video']).resolve(),
                               (path.parent / row['provenance']).resolve(), row.get('lesson_id')))
    return pairs


def _status_path(provenance: Path) -> Path | None:
    candidates = [provenance.parent / 'STATUS.json', provenance.parent.parent / 'STATUS.json']
    found = [p for p in candidates if p.is_file()]
    if len(found) > 1:
        raise AuditError(f'Ambiguous sibling STATUS records for {provenance}')
    return found[0] if found else None


def pair_from_provenance(provenance: Path, video: Path | None = None) -> AuditPair:
    """Resolve standalone evidence using an explicit video or sibling STATUS."""
    provenance = Path(provenance).resolve()
    expected = _video_hash(_json(provenance), provenance)
    if video is not None:
        return AuditPair(Path(video).resolve(), provenance)
    status_path = _status_path(provenance)
    if status_path is None:
        raise AuditError('Standalone provenance needs --video or a sibling STATUS.json')
    status = _json(status_path)
    if status.get('video_sha256') != expected:
        raise AuditError('Sibling STATUS video hash disagrees with provenance')
    candidates = set(status_path.parent.glob('*.mp4'))
    if isinstance(status.get('video_path'), str):
        declared = Path(status['video_path'])
        candidates.update([status_path.parent / declared, ROOT / declared])
    matches = sorted(p.resolve() for p in candidates if p.is_file() and sha256(p) == expected)
    if not matches:
        raise AuditError('No sibling/declaratively referenced video matches STATUS and provenance')
    return AuditPair(matches[0], provenance)


def parse_breaks(text: str, minimum: float = 2.0) -> dict:
    """Keep authored pauses as evidence, including unknown-duration strengths.

    Adjacent breaks without spoken words are summed. Their presence never
    exempts a detected interval from review: alignment has not been established.
    """
    breaks, groups = [], []
    previous_end, total = 0, 0.0
    for match in re.finditer(r'<break\b([^>]*)/?>', text, re.IGNORECASE):
        attrs = dict(re.findall(r'([\w:-]+)\s*=\s*[\"\']([^\"\']*)[\"\']', match[1]))
        seconds = None
        if 'time' in attrs:
            duration = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*(ms|s)\s*', attrs['time'])
            if not duration:
                raise AuditError(f'Unparseable explicit break time: {attrs["time"]!r}')
            seconds = float(duration[1]) / (1000 if duration[2] == 'ms' else 1)
            if not math.isfinite(seconds):
                raise AuditError('Explicit break time must be finite')
        between = html.unescape(re.sub(r'<[^>]*>', '', text[previous_end:match.start()]))
        if re.search(r'\w', between):
            total = 0.0
        total += seconds or 0.0
        groups.append(total)
        breaks.append({'tag': match[0], 'seconds': seconds, 'strength': attrs.get('strength'),
                       'character_offset': match.start()})
        previous_end = match.end()
    return {'breaks': breaks, 'max_contiguous_seconds': max(groups, default=0.0),
            'has_explicit_long_break': max(groups, default=0.0) >= minimum,
            'has_unquantified_break': any(b['seconds'] is None for b in breaks)}


def parse_silencedetect(stderr: str, duration: float, config: AuditConfig) -> list[dict]:
    """Parse FFmpeg events, retaining boundary intervals separately."""
    intervals, start = [], None

    def append(begin, end, length, inferred=False):
        if not all(math.isfinite(x) for x in (begin, end, length)) or end < begin or length < 0:
            raise AuditError('Invalid silencedetect interval')
        boundary = begin <= config.boundary_tolerance or end >= duration - config.boundary_tolerance
        intervals.append({'start_seconds': begin, 'end_seconds': end, 'duration_seconds': length,
                          'boundary': boundary,
                          'requires_review': length + 1e-6 >= config.min_silence,
                          'end_inferred_from_probe': inferred})

    for line in stderr.splitlines():
        match = re.search(rf'silence_start:\s*({_NUMBER})', line)
        if match:
            if start is not None:
                raise AuditError('Unclosed silence_start in FFmpeg output')
            start = float(match[1])
        match = re.search(rf'silence_end:\s*({_NUMBER})\s*\|\s*silence_duration:\s*({_NUMBER})', line)
        if match:
            end, length = float(match[1]), float(match[2])
            append(start if start is not None else end - length, end, length)
            start = None
    if start is not None:
        append(start, duration, duration - start, True)
    return intervals


def detect_silences(path: Path, config: AuditConfig) -> dict:
    """Decode one audio file to a null sink; no media or cache is written."""
    ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:
        raise AuditError('Offline analysis requires ffmpeg and ffprobe on PATH')
    try:
        probe = subprocess.run([ffprobe, '-v', 'error', '-show_entries',
                                'format=duration:stream=codec_type', '-of', 'json', str(path)],
                               capture_output=True, text=True, check=True, timeout=30)
        data = json.loads(probe.stdout)
        duration = float(data['format']['duration'])
        if not math.isfinite(duration) or duration <= 0:
            raise AuditError(f'Invalid audio duration: {path}')
        if not any(s.get('codec_type') == 'audio' for s in data.get('streams', [])):
            raise AuditError(f'No audio stream: {path}')
        silence_filter = f'silencedetect=noise={config.noise_db:g}dB:d={config.min_silence:g}'
        run = subprocess.run([ffmpeg, '-nostdin', '-hide_banner', '-nostats', '-xerror', '-threads', '1',
                              '-i', str(path), '-map', '0:a:0', '-af', silence_filter,
                              '-f', 'null', '-'], stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, text=True, check=True, timeout=300)
    except (OSError, subprocess.SubprocessError, KeyError, ValueError) as exc:
        raise AuditError(f'Audio decoding/analysis failed for {path}: {exc}') from exc
    return {'duration_seconds': duration,
            'intervals': parse_silencedetect(run.stderr, duration, config)}


def _identity(data: dict, status: dict | None, pair: AuditPair, entries: list[dict]) -> dict:
    candidates = set()
    by_id = {e['lesson_id']: e for e in entries}
    by_class = {e['scene_class']: e for e in entries}
    for value in (pair.lesson_id, data.get('lesson_id'), (status or {}).get('lesson_id')):
        if value is not None:
            if value not in by_id:
                raise AuditError(f'Unknown catalogue lesson_id: {value!r}')
            candidates.add(value)
    scenes, voiceovers = data.get('scenes', []), data.get('voiceovers', [])
    if not isinstance(scenes, list) or not isinstance(voiceovers, list):
        raise AuditError(f'Malformed scenes/voiceovers evidence: {pair.provenance}')
    for row in [*scenes, *voiceovers]:
        if not isinstance(row, dict):
            raise AuditError(f'Malformed scene/voiceover entry: {pair.provenance}')
        value = row.get('scene_class')
        if value:
            if value not in by_class:
                raise AuditError(f'Unknown catalogue scene_class: {value!r}')
            candidates.add(by_class[value]['lesson_id'])
    if len(candidates) != 1:
        raise AuditError(f'Missing/conflicting catalogue identity: {pair.provenance}')
    entry = by_id[candidates.pop()]
    for key in ('number', 'order', 'global_number'):
        if status and key in status and (type(status[key]) is not int or status[key] != entry['order']):
            raise AuditError(f'STATUS {key} disagrees with catalogue: {pair.provenance}')
    return {'lesson_id': entry['lesson_id'], 'number': entry['order'], 'title': entry.get('title', '')}


def _time(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise AuditError(f'Missing/invalid {context}')
    return float(value)


def _status_binding(data: dict, provenance: Path, status: dict | None,
                    status_path: Path | None) -> dict:
    """Check available historical integrity records without comparing today's source."""
    evidence = {'provenance_path': str(provenance), 'provenance_sha256': sha256(provenance),
                'status_path': str(status_path) if status_path else None,
                'status_sha256': sha256(status_path) if status_path else None,
                'provenance_integrity_cross_checked': False,
                'input_signature': data['artifact_binding'].get('input_signature')}
    if not status:
        return evidence
    evidence.update(source_sha256=status.get('source_sha256'), source_commit=status.get('source_commit'))
    if 'input_signature' in status:
        expected = _expected_hash(status['input_signature'], str(status_path))
        if data['artifact_binding'].get('input_signature') != expected:
            raise AuditError(f'STATUS input_signature disagrees with provenance: {provenance}')
    if 'narration_evidence' in status:
        narration = status['narration_evidence']
        if not isinstance(narration, dict):
            raise AuditError(f'Malformed STATUS narration_evidence: {status_path}')
        expected = _expected_hash(narration.get('sha256'), f'{status_path} narration_evidence')
        if evidence['provenance_sha256'] != expected:
            raise AuditError(f'STATUS provenance SHA-256 mismatch: {provenance}')
        for key in ('voiceovers', 'adapter_returns'):
            if key in narration:
                actual = data.get(key)
                if type(narration[key]) is not int or not isinstance(actual, list) or len(actual) != narration[key]:
                    raise AuditError(f'STATUS narration {key} count mismatch: {provenance}')
        evidence['provenance_integrity_cross_checked'] = True
    return evidence


def audit_pairs(pairs: list[AuditPair], *, config: AuditConfig | None = None,
                entries: list[dict] | None = None, detector=None) -> dict:
    """Validate all evidence before decoding each distinct final audio once."""
    config = config or AuditConfig()
    if not pairs:
        raise AuditError('No video/provenance pairs were selected')
    if entries is None:
        from tools.course_catalog import load_catalog
        entries = load_catalog(check_inventory=False)[1]
    detector = detector or detect_silences
    hashes, videos, audio, video_signatures = {}, {}, {}, {}

    def verified(path, expected):
        path = Path(path).resolve()
        if path not in hashes:
            hashes[path] = sha256(path)
        if hashes[path] != expected:
            raise AuditError(f'SHA-256 mismatch for {path}')
        return path

    for pair in pairs:
        provenance = Path(pair.provenance).resolve()
        data = _json(provenance)
        video_hash = _video_hash(data, provenance)
        video = verified(pair.video, video_hash)
        status_path = _status_path(provenance)
        status = _json(status_path) if status_path else None
        if status and status.get('video_sha256') != video_hash:
            raise AuditError(f'STATUS video hash disagrees with provenance: {status_path}')
        evidence = _status_binding(data, provenance, status, status_path)
        identity = _identity(data, status, pair, entries)
        voiceovers = data.get('voiceovers')
        if not isinstance(voiceovers, list) or not voiceovers:
            raise AuditError(f'No final voiceover evidence: {provenance}')
        occurrences = []
        for index, row in enumerate(voiceovers):
            final = row.get('final_audio')
            if not isinstance(final, dict) or not isinstance(final.get('path'), str):
                raise AuditError(f'Missing final_audio at voiceover {index}: {provenance}')
            audio_hash = _expected_hash(final.get('sha256'), f'{provenance} voiceover {index}')
            audio_path = verified(provenance.parent / final['path'], audio_hash)
            spoken = row.get('input_text')
            if not isinstance(spoken, str) or not spoken.strip():
                raise AuditError(f'Missing spoken input at voiceover {index}: {provenance}')
            start = _time(row.get('start_seconds'), 'voiceover start_seconds')
            end = _time(row.get('end_seconds'), 'voiceover end_seconds')
            duration = _time(row.get('duration_seconds'), 'voiceover duration_seconds')
            if end < start or duration <= 0 or abs((end - start) - duration) > TIMING_TOLERANCE_SECONDS:
                raise AuditError(f'Invalid voiceover timing: {provenance} #{index}')
            occurrence = {**identity, 'voiceover_index': index, 'audio_sha256': audio_hash,
                          'scene_start_seconds': start, 'scene_end_seconds': end,
                          'tracker_duration_seconds': duration, 'input_text': spoken,
                          'plain_text': ' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', spoken)).split()),
                          'authored_pauses': parse_breaks(spoken, config.min_silence)}
            occurrences.append(occurrence)
            clip = audio.setdefault(audio_hash, {'sha256': audio_hash, 'paths': [], 'sha256_verified': True})
            if str(audio_path) not in clip['paths']:
                clip['paths'].append(str(audio_path))
        signature = json.dumps({'identity': identity, 'voiceovers': occurrences,
                                'input_signature': evidence['input_signature']}, sort_keys=True)
        if video_hash in video_signatures and video_signatures[video_hash] != signature:
            raise AuditError(f'Conflicting provenance for the same video hash: {video}')
        video_signatures[video_hash] = signature
        key = str(video)
        if key in videos:
            if videos[key]['_signature'] != signature:
                raise AuditError(f'Conflicting provenance for the same video: {video}')
            if str(provenance) not in videos[key]['provenance_paths']:
                videos[key]['provenance_paths'].append(str(provenance))
                videos[key]['provenance_records'].append(evidence)
        else:
            videos[key] = {**identity, 'video_path': key, 'video_sha256': video_hash,
                           'provenance_paths': [str(provenance)], 'provenance_records': [evidence],
                           'voiceovers': occurrences,
                           '_signature': signature}

    def analyze(item):
        digest, clip = item
        return digest, detector(Path(clip['paths'][0]), config)

    with ThreadPoolExecutor(max_workers=config.jobs) as pool:
        for digest, result in pool.map(analyze, audio.items()):
            audio[digest].update(result)
    flags, affected = [], set()
    for video in videos.values():
        del video['_signature']
        for occurrence in video['voiceovers']:
            clip = audio[occurrence['audio_sha256']]
            if abs(clip['duration_seconds'] - occurrence['tracker_duration_seconds']) > TIMING_TOLERANCE_SECONDS:
                raise AuditError(f'Probed audio duration disagrees with tracker: {clip["paths"][0]}')
            for interval in clip['intervals']:
                pauses = occurrence['authored_pauses']
                tags = ['boundary_silence' if interval['boundary'] else 'internal_silence']
                if pauses['has_explicit_long_break']:
                    tags.append('explicit_long_break_candidate_alignment_unverified')
                if pauses['has_unquantified_break']:
                    tags.append('unquantified_authored_break')
                if not pauses['has_explicit_long_break'] and not pauses['has_unquantified_break']:
                    tags.append('no_explicit_long_break_explanation')
                if interval['requires_review']:
                    affected.add(occurrence['lesson_id'])
                flags.append({**occurrence, **interval, 'flags': tags,
                              'clip_duration_seconds': clip['duration_seconds'],
                              'video_start_seconds': occurrence['scene_start_seconds'] + interval['start_seconds'],
                              'video_end_seconds': occurrence['scene_start_seconds'] + interval['end_seconds'],
                              'video_path': video['video_path'], 'video_sha256': video['video_sha256'],
                              'audio_paths': clip['paths'], 'provenance_paths': video['provenance_paths']})
    flags.sort(key=lambda row: (row['number'], row['video_path'], row['voiceover_index'], row['start_seconds']))
    review = [row for row in flags if row['requires_review']]
    internal = [row for row in review if not row['boundary']]
    return {'schema_version': 1, 'status': 'review_required' if review else 'no_flags_detected',
            'listening': 'not_performed', 'pronunciation': 'not_assessed', 'release_ready': False,
            'parameters': asdict(config),
            'method': {'binding': 'Actual video SHA-256 matches artifact_binding.video_sha256; every final audio reference is hash-verified.',
                       'selection': 'voiceovers[].final_audio only; decode once per unique verified audio SHA-256.',
                       'filter': f'silencedetect=noise={config.noise_db:g}dB:d={config.min_silence:g}',
                       'boundary': 'Leading/trailing intervals are classified separately and still require review; neither boundary position nor a silent whole clip is an exemption.',
                       'authored_pauses': 'Explicit long or unquantified breaks are evidence, never automatic exemptions. No temporal alignment or listening is claimed.',
                       'video_timestamps': 'Approximate: recorded scene audio start + clip-relative interval; encoded stream offsets are not independently measured.',
                       'timing_tolerance_seconds': TIMING_TOLERANCE_SECONDS,
                       'timing_validation': 'end-start and tracker duration, then probed clip and tracker duration, must agree within the codec/rounding tolerance.'},
            'limitations': ['Signal screening does not validate pronunciation or natural delivery.',
                            'Intentional scene waits outside final narration audio are not scanned.',
                            'No audio is modified; no automatic trim or release approval.'],
            'summary': {'videos': len(videos), 'provenance_files': len({p for v in videos.values() for p in v['provenance_paths']}),
                        'voiceover_occurrences': sum(len(v['voiceovers']) for v in videos.values()),
                        'unique_final_audio_clips': len(audio), 'verified_audio_paths': sum(len(a['paths']) for a in audio.values()),
                        'clips_with_internal_silence': sum(any(i['requires_review'] and not i['boundary'] for i in a['intervals']) for a in audio.values()),
                        'unique_internal_intervals': sum(sum(i['requires_review'] and not i['boundary'] for i in a['intervals']) for a in audio.values()),
                        'internal_occurrence_intervals': len(internal),
                        'review_required_occurrence_intervals': len(review),
                        'boundary_occurrence_intervals': sum(r['boundary'] for r in flags),
                        'affected_lessons': sorted(affected), 'affected_lesson_count': len(affected)},
            'videos': sorted(videos.values(), key=lambda v: (v['number'], v['video_path'])),
            'audio': list(audio.values()), 'flags': flags}


CSV_FIELDS = ['lesson_id', 'number', 'video_start_seconds', 'video_end_seconds',
              'voiceover_index', 'start_seconds', 'end_seconds', 'duration_seconds',
              'clip_duration_seconds', 'requires_review', 'boundary', 'flags',
              'input_text', 'plain_text', 'authored_pauses', 'video_sha256', 'audio_sha256',
              'video_path', 'audio_paths', 'provenance_paths']


def write_report(report: dict, output: Path) -> None:
    """Create a new immutable audit directory; never overwrite earlier evidence."""
    output = Path(output)
    try:
        output.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise AuditError(f'Output already exists; choose a new directory: {output}') from exc
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (output / 'review.csv').open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for flag in sorted(report.get('flags', []),
                           key=lambda row: (-row['requires_review'], -row['duration_seconds'], row['number'])):
            row = {key: flag.get(key, '') for key in CSV_FIELDS}
            for key in ('flags', 'authored_pauses', 'audio_paths', 'provenance_paths'):
                row[key] = json.dumps(row[key], ensure_ascii=False)
            writer.writerow(row)
