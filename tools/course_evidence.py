"""Read historical production records without turning screening into approval."""
from __future__ import annotations

import json
from pathlib import Path

from tools.course_review import CHECKS, sha256, signature


def local_file(root, name):
    """Evidence manifests may name repository-relative files, never outside files."""
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        return None
    candidate = Path(root) / name
    if '..' in Path(name).parts or not candidate.resolve().is_relative_to(Path(root).resolve()):
        return None
    return candidate if candidate.is_file() else None


def bound_record(root, lesson, *, path, expected, inputs=None, runtime=None,
                 current_runtime=None):
    """Separate missing media, changed identity, and incomplete provenance.

    Fresh means that the declared bytes, complete source inputs and runtime match.
    It says nothing about playback, listening, mathematical correctness or release.
    """
    file = local_file(root, path)
    result = {'path': path, 'expected_sha256': expected,
              'recorded_input_signature': signature(inputs) if inputs else None,
              'current_input_signature': lesson['input_signature'],
              'runtime_versions': runtime, 'changed_inputs': [], 'unrecorded_inputs': []}
    if inputs:
        result['changed_inputs'] = sorted(p for p, h in inputs.items()
                                           if lesson['inputs'].get(p) != h)
        result['unrecorded_inputs'] = sorted(set(lesson['inputs']) - inputs.keys())
    else:
        result['unrecorded_inputs'] = sorted(lesson['inputs'])
    if not file:
        result.update(state='unavailable', reason='Declared local artifact is absent or outside the repository.')
        return result
    result['actual_sha256'] = sha256(file)
    if result['actual_sha256'] != expected or result['changed_inputs']:
        result.update(state='stale', reason='Artifact bytes or recorded source inputs changed.')
    elif (runtime and current_runtime and any(runtime[k] and current_runtime[k]
          and runtime[k] != current_runtime[k] for k in runtime.keys() & current_runtime.keys())):
        result.update(state='stale', reason='Rendering runtime changed.')
    elif (not inputs or result['unrecorded_inputs'] or not runtime or not current_runtime
          or runtime.keys() != current_runtime.keys()
          or not all(current_runtime.values()) or not all(runtime.values())):
        result.update(state='unreviewed', reason='Complete source and runtime provenance is unavailable.')
    else:
        result.update(state='fresh', reason='Artifact identity, complete source inputs and runtime match.')
    return result


def ingest_coherence(path, lessons, root, runtime):
    report = json.loads(Path(path).read_text(encoding='utf-8'))
    report_id = {'report': Path(path).resolve().relative_to(Path(root).resolve()).as_posix(),
                 'report_sha256': sha256(path)}
    seen = set()
    for row in report['lessons']:
        key = row['lesson_id']
        if key not in lessons or key in seen:
            raise ValueError(f'Unknown or duplicate coherence lesson: {key}')
        seen.add(key)
        lesson = lessons[key]
        status_path = local_file(root, row.get('origin_status'))
        status = json.loads(status_path.read_text()) if status_path else {}
        inputs = dict(status.get('input_sha256') or status.get('shared_sha256') or {})
        source = next(p for p in lesson['inputs'] if p.startswith('scenes/') and p.endswith('_scene.py'))
        conflict = status.get('source_sha256') and source in inputs and inputs[source] != status['source_sha256']
        if status.get('source_sha256'):
            inputs[source] = status['source_sha256']
        record = bound_record(root, lesson, path=row.get('video_path'), expected=row.get('video_sha256'),
                              inputs=inputs, runtime=status.get('runtime_versions'), current_runtime=runtime)
        if conflict or (status and (status.get('lesson_id') != key
                                   or status.get('video_sha256') != row.get('video_sha256'))):
            record.update(state='stale', reason='Coherence manifest and originating status disagree.')
        elif record['state'] == 'fresh' and status.get('render') != 'passed':
            record.update(state='unreviewed', reason='Originating render did not record success.')
        record.update(report_id, kind='coherence', coverage='sampled_encoded_frames',
                      mode=report.get('mode'), origin_status=row.get('origin_status'),
                      origin_status_sha256=sha256(status_path) if status_path else None,
                      full_motion=report.get('full_motion', 'not_checked'),
                      listening=report.get('listening', 'not_performed'),
                      acceptance='No checks are passed by importing a historical manifest.')
        lesson.setdefault('production_context', []).append(record)


def ingest_narration(path, lessons, root):
    report = json.loads(Path(path).read_text(encoding='utf-8'))
    analysis = report['existing_audio_analysis']
    changed = {row['lesson_id']: row for row in report.get('changed_lessons', [])}
    affected = set(analysis['summary']['affected_lessons']) | set(changed)
    report_name = Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
    for key in sorted(affected):
        if key not in lessons:
            raise ValueError(f'Unknown narration lesson: {key}')
        lesson = lessons[key]
        evidence = local_file(root, analysis.get('output_report'))
        matched = evidence and sha256(evidence) == analysis.get('output_report_sha256')
        source = changed.get(key, {})
        source_match = (lesson['inputs'].get(source.get('source')) == source.get('source_sha256')
                        if source else None)
        record = {'kind': 'narration_screen', 'report': report_name,
                  'report_sha256': sha256(path), 'path': analysis.get('output_report'),
                  'expected_sha256': analysis.get('output_report_sha256'),
                  'state': 'unreviewed' if matched else 'stale' if evidence else 'unavailable',
                  'source_revision_matches': source_match,
                  'screening_flagged': key in analysis['summary']['affected_lessons'],
                  'coverage': 'automated_screening_of_historical_audio',
                  'listening': 'not_performed', 'replacement_audio': 'not_generated',
                  'reason': 'Screening identifies listening candidates; it is not a listening decision.',
                  'historical_scope': analysis.get('historical_scope', '')}
        if evidence:
            record['actual_sha256'] = sha256(evidence)
        lesson.setdefault('production_context', []).append(record)


def overview(lesson):
    """Compact freshness view alongside the unchanged acceptance/check states."""
    result = {}
    for name in CHECKS:
        check = lesson['checks'][name]
        status = check['status']
        evidence = check.get('evidence_sha256')
        result[name] = ('stale' if status == 'stale' else
                        'fresh' if status in {'passed', 'failed'} and evidence else 'unreviewed')
    for kind in ('coherence', 'narration_screen'):
        records = [r for r in lesson.get('production_context', []) if r['kind'] == kind]
        # Preserve all original rows; the most recently supplied report is displayed.
        result[kind] = records[-1]['state'] if records else 'unreviewed'
    return result
