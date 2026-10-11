"""Artifact-bound course review evidence; rendering is never audiovisual approval."""
from __future__ import annotations

import ast
import hashlib
import json
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from tools.course_catalog import ROOT

STATES = {'not_checked', 'blocked', 'failed', 'passed', 'stale'}
CHECKS = ('source_math', 'technical', 'displayed_math', 'readability', 'motion',
          'narration', 'timing', 'final_resolution')
VISUAL_CHECKS = ('source_math', 'technical', 'displayed_math', 'readability',
                 'motion', 'final_resolution')
AUDIO_CHECKS = ('narration', 'timing')


def renderer_runtime_versions():
    """Read resolved renderer dependencies without importing Manim or cloud SDKs."""
    versions = {}
    for name in ('manim', 'manim-voiceover', 'numpy', 'scipy', 'Pillow'):
        try:
            versions[name] = version(name)
        except PackageNotFoundError:
            versions[name] = None
    return versions


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def input_hashes(entry, root=ROOT):
    """Conservative local dependency closure, plus teaching data and local assets.

    Walk local imports without executing scenes or importing the cloud adapter.
    Hash extra data conservatively rather than claiming dynamic imports are known.
    Audit tooling itself is recorded separately from video inputs.
    """
    root = Path(root)
    pending = [root / entry['scene_file']]
    paths = set()
    while pending:
        path = pending.pop()
        if path in paths or not path.is_file():
            continue
        paths.add(path)
        if path.suffix != '.py':
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if node.level:
                    parent = path.parent
                    for _ in range(node.level - 1):
                        parent = parent.parent
                    module = '.'.join((*parent.relative_to(root).parts,
                                       *module.split('.'))).strip('.')
                names = [module, *(f'{module}.{a.name}' for a in node.names)]
            for name in names:
                for candidate in (root / (name.replace('.', '/') + '.py'),
                                  root / name.replace('.', '/') / '__init__.py'):
                    if candidate.is_file() and candidate.is_relative_to(root):
                        pending.append(candidate)
        # Plain filename imports and data live beside some historical scenes.
        pending.extend(p for p in path.parent.glob('*.py')
                       if path.parent == (root / entry['scene_file']).parent)
    for folder in ((root / entry['scene_file']).parent, root / 'assets/branding',
                   root / 'tools/ssml', root / 'curriculum/worked_examples'):
        if folder.is_dir():
            paths.update(p for p in folder.rglob('*') if p.is_file()
                         and p.suffix.lower() in {'.py', '.yaml', '.json', '.ssml',
                                                  '.svg', '.png', '.jpg', '.mp3', '.wav',
                                                  '.ttf', '.otf'})
    for name in ('pyproject.toml', 'curriculum/programme_principal_fr.yaml',
                 'curriculum/duration_policy.yaml', 'curriculum/practice_questions.yaml'):
        if (root / name).is_file():
            paths.add(root / name)
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(paths)}


def validate_coverage(lessons, entries):
    expected = {e['lesson_id'] for e in entries}
    ids = [e['lesson_id'] for e in lessons]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('Review coverage must match the catalogue exactly once.')


def empty_lesson(entry, inputs):
    return {'lesson_id': entry['lesson_id'], 'number': entry['order'],
            'title': entry['title'], 'inputs': inputs, 'input_signature': signature(inputs),
            'artifacts': [], 'current_artifact': None, 'findings': [],
            'checks': {key: {'status': 'not_checked'} for key in CHECKS},
            'visual_complete': False, 'narrated_complete': False, 'release_ready': False}


def refresh_lesson(lesson, inputs):
    current = signature(inputs)
    changed = lesson.get('input_signature') != current
    if changed:
        for check in lesson['checks'].values():
            if check['status'] in {'passed', 'failed', 'blocked'}:
                check['status'] = 'stale'
        for finding in lesson['findings']:
            if finding.get('status') == 'closed':
                finding['status'] = 'awaiting_verification'
        lesson['current_artifact'] = None
    lesson.update(inputs=inputs, input_signature=current)
    summarize(lesson)
    return changed


def record_check(lesson, name, review, artifact=None):
    """Accept an explicit review record only for its exact source/output revision."""
    if name not in CHECKS or review.get('status') not in STATES:
        raise ValueError('Unknown review check or status.')
    if review['status'] == 'passed':
        if not all(review.get(k) for k in ('reviewer', 'checked_at', 'evidence')):
            raise ValueError('A pass needs a reviewer, date and evidence.')
        if review.get('input_signature') != lesson['input_signature']:
            raise ValueError('Review inputs are stale.')
        if name != 'source_math':
            if not artifact or artifact.get('provenance') != 'current':
                raise ValueError('This check requires current encoded media.')
            if artifact.get('video_sha256') != lesson.get('current_artifact'):
                raise ValueError('Review must target the selected current video.')
            if review.get('video_sha256') != artifact.get('video_sha256'):
                raise ValueError('Review belongs to a different video.')
            if name != 'technical' and review.get('coverage') != 'complete':
                raise ValueError('Partial inspection cannot pass a whole-video check.')
            if name == 'motion' and review.get('method') != 'full_playback':
                raise ValueError('Motion requires full playback.')
            if name in AUDIO_CHECKS:
                if not artifact.get('has_audio') or artifact.get('audio_mode') == 'silent_preview':
                    raise ValueError('Silent media cannot pass narration or narrated timing.')
                required = 'full_listening' if name == 'narration' else 'full_av_review'
                if review.get('method') != required:
                    raise ValueError('Listening and timing need their actual review methods.')
            if name == 'final_resolution':
                width, height = artifact.get('dimensions', [0, 0])
                if width < 1920 or height < 1080 or review.get('method') != 'display_size_review':
                    raise ValueError('Final legibility requires display-size review at 1080p or above.')
    lesson['checks'][name] = dict(review)
    summarize(lesson)


def close_finding(lesson, finding_id, verification, artifact):
    finding = next(f for f in lesson['findings'] if f['id'] == finding_id)
    if finding.get('status') not in {'awaiting_verification', 'closed'} or not finding.get('fixed_by'):
        raise ValueError('Only a recorded correction can receive independent closure.')
    if not verification.get('reviewer') or verification['reviewer'] == finding.get('fixed_by'):
        raise ValueError('The fixing agent cannot close its own finding.')
    if not verification.get('evidence') or not verification.get('checked_at'):
        raise ValueError('Closure requires dated replacement-artifact evidence.')
    if (artifact.get('provenance') != 'current'
            or artifact.get('video_sha256') != lesson.get('current_artifact')
            or verification.get('video_sha256') != artifact.get('video_sha256')
            or verification.get('input_signature') != lesson['input_signature']):
        raise ValueError('Closure must refer to current inputs and replacement media.')
    if not verification.get('acceptance_passed'):
        raise ValueError('Closure requires an explicit acceptance result.')
    if finding.get('original_video_sha256') == artifact.get('video_sha256'):
        raise ValueError('The defective original is not replacement evidence.')
    finding.update(status='closed', verification=dict(verification))
    summarize(lesson)


def unresolved_finding(finding):
    deferrer = finding.get('deferred_by')
    return finding.get('status') != 'closed' and not (
        finding.get('severity') == 'minor' and finding.get('status') == 'deferred'
        and finding.get('category') == 'cosmetic'
        and isinstance(deferrer, str) and deferrer.strip())


def summarize(lesson):
    for item in lesson.get('review_history', []):
        review = item['review']
        current = (review.get('input_signature') in {None, lesson['input_signature']}
                   and review.get('video_sha256') in {None, lesson['current_artifact']})
        item['applicability'] = 'current' if current else 'stale'
    unresolved = [f for f in lesson['findings'] if unresolved_finding(f)]
    def affects_visual(finding):
        affected = finding.get('affected_checks', CHECKS)
        if not isinstance(affected, (list, tuple)) or not affected or set(affected) - set(CHECKS):
            return True
        return bool(set(affected) & set(VISUAL_CHECKS))

    visual_unresolved = any(affects_visual(f) for f in unresolved)
    checks = lesson['checks']
    lesson['visual_complete'] = not visual_unresolved and all(checks[k]['status'] == 'passed'
                                                             for k in VISUAL_CHECKS)
    lesson['narrated_complete'] = lesson['visual_complete'] and not unresolved and all(
        checks[k]['status'] == 'passed' for k in AUDIO_CHECKS)
    lesson['release_ready'] = False


def replace_artifact(lesson, artifact):
    """A new movie invalidates all prior movie reviews, including silent-to-audio."""
    if lesson.get('current_artifact') != artifact['video_sha256']:
        for name, check in lesson['checks'].items():
            if name != 'source_math' and check['status'] in {'passed', 'failed'}:
                check['status'] = 'stale'
            elif name != 'source_math' and check['status'] == 'blocked':
                lesson['checks'][name] = {'status': 'not_checked', 'reason': 'Replacement artifact needs review.'}
        for finding in lesson['findings']:
            if finding.get('status') == 'closed':
                finding['status'] = 'awaiting_verification'
    lesson['current_artifact'] = artifact['video_sha256']
    summarize(lesson)
