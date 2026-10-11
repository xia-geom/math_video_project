#!/usr/bin/env python3
"""Reconcile course evidence into JSON, Markdown and CSV; never render or publish."""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.course_catalog import load_catalog  # noqa: E402
from tools.course_review import (  # noqa: E402
    CHECKS,
    STATES,
    AudioClosureError,
    apply_finding_scope,
    close_finding,
    empty_lesson,
    finding_definition_signature,
    input_hashes,
    record_check,
    refresh_lesson,
    renderer_runtime_versions,
    replace_artifact,
    revalidate_audio_closures,
    sha256,
    signature,
    summarize,
    unresolved_finding,
    validate_coverage,
)


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def inspect_artifact(status_file, status, entry, inputs):
    movies = list(status_file.parent.glob('*.mp4'))
    if len(movies) != 1:
        return None
    video = movies[0]
    actual_hash = sha256(video)
    recorded = dict(status.get('input_sha256') or status.get('shared_sha256') or {})
    conflict = (entry['scene_file'] in recorded and status.get('source_sha256')
                and recorded[entry['scene_file']] != status['source_sha256'])
    if status.get('source_sha256'):
        recorded[entry['scene_file']] = status['source_sha256']
    changed = [p for p, h in recorded.items()
               if not (ROOT / p).resolve().is_relative_to(ROOT)
               or not (ROOT / p).is_file() or sha256(ROOT / p) != h]
    missing = sorted(set(inputs) - recorded.keys())
    recorded_runtime = status.get('runtime_versions')
    expected_runtime = renderer_runtime_versions()
    if conflict:
        provenance = 'conflicting_source_records'
    elif actual_hash != status.get('video_sha256'):
        provenance = 'output_mismatch'
    elif changed:
        provenance = 'stale'
    elif not recorded or missing:
        provenance = 'recorded_inputs_match' if recorded else 'unknown'
    elif status.get('render') != 'passed':
        provenance = 'failed'
    elif not recorded_runtime:
        provenance = 'runtime_unknown'
    elif not all(expected_runtime.values()):
        provenance = 'runtime_unavailable'
    elif recorded_runtime != expected_runtime:
        provenance = 'runtime_mismatch'
    else:
        provenance = 'current'
    result = {'path': relative(video), 'status_path': relative(status_file),
              'video_sha256': actual_hash, 'provenance': provenance,
              'changed_inputs': changed, 'unrecorded_inputs': missing,
              'runtime_versions': recorded_runtime,
              'runtime_signature': signature(recorded_runtime) if recorded_runtime else None,
              'expected_runtime_signature': signature(expected_runtime),
              'audio_mode': status.get('mode', status.get('audio_mode', 'unknown'))}
    try:
        media = json.loads(subprocess.check_output(
            ['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)],
            stderr=subprocess.PIPE, timeout=60))
        streams = media.get('streams', [])
        pictures = [s for s in streams if s.get('codec_type') == 'video']
        audio = any(s.get('codec_type') == 'audio' for s in streams)
        duration = float(media.get('format', {}).get('duration', 0))
        if len(pictures) != 1 or duration <= 0:
            raise ValueError('Expected one video stream and positive duration.')
        if result['audio_mode'] in {'silent_preview', 'azure_review'}:
            if audio != (result['audio_mode'] == 'azure_review'):
                raise ValueError('Encoded audio disagrees with the declared mode.')
        pic = pictures[0]
        expected = (1920, 1080, '60/1') if status.get('quality') == 'qh' else (854, 480, '15/1')
        if status.get('quality') in {'ql', 'qh'} and (pic['width'], pic['height'], pic['r_frame_rate']) != expected:
            raise ValueError('Encoded format disagrees with the declared quality.')
        if audio and result['provenance'] == 'current':
            from tools.narration_provenance import (
                validate_narration_tooling,
                verify_narration_manifest,
            )
            validate_narration_tooling(status.get('narration_tooling_sha256'), ROOT)
            result['narration_evidence'] = verify_narration_manifest(
                status_file, status, actual_hash, signature(inputs))
        elif not audio:
            result['environment_attestation'] = 'legacy_silent_environment_not_attested'
        result.update(has_audio=audio, duration_seconds=duration,
                      dimensions=[pic['width'], pic['height']], fps=pic['r_frame_rate'],
                      stream_check='passed')
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        result.update(stream_check='failed', error=str(error), provenance='failed')
    return result


def collect_artifacts(roots, entries, lessons):
    by_id = {e['lesson_id']: e for e in entries}
    seen = set()
    for folder in roots:
        for status_file in sorted(folder.rglob('STATUS.json')):
            if status_file in seen:
                continue
            seen.add(status_file)
            status = read_json(status_file)
            key = status.get('lesson_id')
            if key not in by_id:
                continue
            lesson = lessons[key]
            artifact = inspect_artifact(status_file, status, by_id[key], lesson['inputs'])
            if artifact:
                lesson['artifacts'].append(artifact)


def ingest_workers(paths, lessons, checked_at):
    owners = set()
    for path in paths:
        report = read_json(path)
        worker = report['worker']
        for row in report['lessons']:
            key = row['lesson_id']
            if key in owners:
                raise ValueError(f'Multiple source-review owners for {key}')
            owners.add(key)
            lesson = lessons[key]
            lesson['owner'] = worker
            lesson['source_notes'] = row.get('notes', '')
            source = next(p for p in lesson['inputs'] if p.startswith('scenes/') and p.endswith('_scene.py'))
            matches = (row.get('source_sha256') == lesson['inputs'][source]
                       and row.get('input_sha256') == lesson['inputs'])
            if row.get('source_review') not in STATES:
                raise ValueError('Unknown worker source-review state.')
            review = {'status': row['source_review'] if matches else 'stale',
                      'reviewer': worker, 'checked_at': report.get('checked_at', checked_at),
                      'evidence': [relative(path)], 'input_signature': lesson['input_signature'],
                      'method': 'source_inspection', 'coverage': 'source_only'}
            record_check(lesson, 'source_math', review)
            existing = {f['id']: f for f in lesson['findings']}
            for finding in row.get('findings', []):
                if finding.get('status') == 'closed':
                    raise ValueError('Worker reports cannot close findings; supply independent artifact verification.')
                old = existing.get(finding['id'])
                if old and old.get('status') == 'closed':
                    continue
                lesson['findings'] = [f for f in lesson['findings'] if f['id'] != finding['id']]
                replacement = {**finding, 'fixed_by': worker}
                scope = old.get('scope_review') if old else None
                if (scope and scope.get('finding_definition_sha256')
                        == finding_definition_signature(replacement)):
                    holder = {'findings': [replacement]}
                    apply_finding_scope(holder, scope)
                lesson['findings'].append(replacement)


def ingest_reviews(paths, lessons):
    """Explicit reviewer-authored records; no generated declarations of watching."""
    def retain(lesson, kind, name, review):
        stale = (review.get('input_signature') not in {None, lesson['input_signature']}
                 or review.get('video_sha256') not in {None, lesson['current_artifact']})
        identity = signature({'kind': kind, 'name': name, 'review': review})
        history = lesson.setdefault('review_history', [])
        history[:] = [r for r in history if r['id'] != identity]
        history.append({'id': identity, 'kind': kind, 'name': name, 'review': review,
                        'applicability': 'stale' if stale else 'current'})
        return not stale

    rows = [row for path in paths for row in read_json(path).get('reviews', [])]
    # Dated classifications precede every closure, regardless of argument order.
    for row in rows:
        lesson = lessons[row['lesson_id']]
        for scope in row.get('finding_scopes', []):
            apply_finding_scope(lesson, scope)
    for row in rows:
        lesson = lessons[row['lesson_id']]
        artifact = next((a for a in lesson['artifacts']
                         if a['video_sha256'] == lesson['current_artifact']
                         and a.get('provenance') == 'current'), None)
        for name, review in row.get('checks', {}).items():
            if retain(lesson, 'check', name, review):
                record_check(lesson, name, review, artifact)
    for row in rows:
        lesson = lessons[row['lesson_id']]
        artifact = next((a for a in lesson['artifacts']
                         if a['video_sha256'] == lesson['current_artifact']
                         and a.get('provenance') == 'current'), None)
        for closure in row.get('closures', []):
            if not retain(lesson, 'closure', closure['finding_id'], closure):
                continue
            if artifact is None:
                raise ValueError('No current artifact for finding closure.')
            try:
                close_finding(lesson, closure['finding_id'], closure, artifact)
            except AudioClosureError as error:
                # Preserve old narrow evidence, without upgrading it into listening.
                identity = signature({'kind': 'closure', 'name': closure['finding_id'], 'review': closure})
                item = next(r for r in lesson['review_history'] if r['id'] == identity)
                item.update(acceptance='rejected', reason=str(error))
    for lesson in lessons.values():
        revalidate_audio_closures(lesson)


def write_reports(ledger, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / 'review.json').write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    headings = ['number', 'lesson_id', 'owner', *CHECKS, 'open_findings',
                'visual_complete', 'narrated_complete', 'current_artifact', 'next_action']
    rows = []
    for lesson in ledger['lessons']:
        unresolved = sum(bool(unresolved_finding(f)) for f in lesson['findings'])
        next_action = ('Obtain current render evidence' if not lesson['current_artifact'] else
                       'Independently verify corrections and inspect full video' if unresolved else
                       'Complete encoded mathematics, visual and motion review' if not lesson['visual_complete'] else
                       'Complete narrated playback and listening' if not lesson['narrated_complete'] else
                       'Separate publication approval remains pending')
        rows.append({'number': lesson['number'], 'lesson_id': lesson['lesson_id'],
                     'owner': lesson.get('owner', ''),
                     **{key: lesson['checks'][key]['status'] for key in CHECKS},
                     'open_findings': unresolved, 'visual_complete': lesson['visual_complete'],
                     'narrated_complete': lesson['narrated_complete'],
                     'current_artifact': lesson['current_artifact'] or '', 'next_action': next_action})
    with (output / 'review.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=headings, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    lines = ['# Current course production review', '',
             f"Generated: {ledger['generated_at']}. Source: `{ledger['source_commit']}`.", '',
             f"Working tree modified: {ledger['working_tree_dirty']}. Exact input and output hashes are recorded in [the ledger](review.json).", '',
             'Source mathematics, encoded inspection, complete playback and listening are separate checks.',
             'Partial inspection and matching historical hashes do not imply final audiovisual approval.', '',
             f"Matching encoded artifacts: {sum(bool(e['current_artifact']) for e in ledger['lessons'])}/{len(rows)}.", '',
             '| No. | Lesson | Source math | Technical | Displayed math | Readability | Motion | Audio | Timing | Final size | Open |',
             '|---:|---|---|---|---|---|---|---|---|---|---:|']
    for row in rows:
        lines.append('| ' + ' | '.join(str(row[k]) for k in
                     ('number', 'lesson_id', 'source_math', 'technical', 'displayed_math',
                      'readability', 'motion', 'narration', 'timing', 'final_resolution', 'open_findings')) + ' |')
    lines.extend(['', f"Visual completion: {sum(r['visual_complete'] for r in rows)}/{len(rows)}.",
                  f"Narrated completion: {sum(r['narrated_complete'] for r in rows)}/{len(rows)}.",
                  'Publication approval: separate, not granted by this report.', '', '## Next actions', ''])
    lines.extend(f"- {r['number']:02d}: {r['next_action']}." for r in rows)
    (output / 'REVIEW.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--artifact-root', type=Path, action='append', default=[])
    parser.add_argument('--worker-report', type=Path, action='append', default=[])
    parser.add_argument('--reviews', type=Path, action='append', default=[])
    args = parser.parse_args()
    _, entries = load_catalog()
    previous = args.output / 'review.json'
    old = read_json(previous) if previous.is_file() else {'lessons': []}
    lessons = {e['lesson_id']: e for e in old['lessons']}
    if lessons:
        validate_coverage(old['lessons'], entries)
    for entry in entries:
        inputs = input_hashes(entry)
        key = entry['lesson_id']
        if key not in lessons:
            lessons[key] = empty_lesson(entry, inputs)
        else:
            refresh_lesson(lessons[key], inputs)
        lessons[key]['artifacts'] = []
    timestamp = datetime.now(timezone.utc).isoformat()
    migration = read_json(ROOT / 'curriculum/numbering_migration.json')
    for row in migration['entries']:
        slug = row['old_artifact_slug']
        path = ROOT / 'dist' / slug / (slug + '.mp4')
        lessons[row['lesson_id']]['historical_media'] = {
            'path': relative(path), 'exists': path.is_file(), 'provenance': 'unknown',
            'note': 'Historical file identity only; not probed or approved as current source.'}
    collect_artifacts([p.resolve() for p in args.artifact_root], entries, lessons)
    for lesson in lessons.values():
        current = [a for a in lesson['artifacts'] if a['provenance'] == 'current' and a['stream_check'] == 'passed']
        if current:
            # Prefer narrated, then higher resolution; deterministic path tie-break.
            artifact = max(current, key=lambda a: (a['has_audio'], a['dimensions'][1], a['path']))
            replace_artifact(lesson, artifact)
            record_check(lesson, 'technical', {
                'status': 'passed', 'reviewer': 'ffprobe+provenance', 'checked_at': timestamp,
                'input_signature': lesson['input_signature'], 'video_sha256': artifact['video_sha256'],
                'evidence': [artifact['status_path']], 'method': 'encoded_stream_check'}, artifact)
            if not artifact['has_audio']:
                for key in ('narration', 'timing'):
                    if lesson['checks'][key]['status'] != 'passed':
                        lesson['checks'][key] = {'status': 'blocked', 'reason': 'Current artifact is explicitly silent.'}
        else:
            lesson['current_artifact'] = None
            for key, check in lesson['checks'].items():
                if key != 'source_math' and check['status'] in {'passed', 'failed', 'blocked'}:
                    check['status'] = 'stale'
            for finding in lesson['findings']:
                if finding.get('status') == 'closed':
                    finding['status'] = 'awaiting_verification'
    ingest_workers(args.worker_report, lessons, timestamp)
    ingest_reviews(args.reviews, lessons)
    ordered = [lessons[e['lesson_id']] for e in entries]
    for lesson in ordered:
        summarize(lesson)
    validate_coverage(ordered, entries)
    ledger = {'schema_version': 1, 'generated_at': timestamp,
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'working_tree_dirty': bool(subprocess.check_output(
                  ['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True)),
              'release_ready': False, 'lessons': ordered}
    write_reports(ledger, args.output)
    print(json.dumps({'lessons': len(ordered), 'current_artifacts': sum(bool(e['current_artifact']) for e in ordered),
                      'visual_complete': sum(e['visual_complete'] for e in ordered),
                      'narrated_complete': sum(e['narrated_complete'] for e in ordered)}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
