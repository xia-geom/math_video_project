#!/usr/bin/env python3
"""Audit the actual globally numbered course; never publish or infer human approval."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_private_data import path_reason  # noqa: E402
from tools.course_catalog import load_catalog, resolve  # noqa: E402
from tools.course_review import input_hashes, sha256, signature  # noqa: E402


def run(command, path, *, timeout=600):
    with path.open('w', encoding='utf-8') as log:
        try:
            return subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=timeout, check=False).returncode
        except subprocess.TimeoutExpired:
            return 124


def snapshot_inputs():
    """Select tracked candidates and provide a guard for every source read."""
    root = ROOT.resolve()
    roots = ('scenes/', 'tools/', 'scripts/', 'tests/', 'curriculum/', 'docs/', '.github/', '.vscode/', 'assets/branding/')
    names = set(subprocess.check_output(
        ['git', 'ls-files', '--cached', '-z'], cwd=root
    ).decode('utf-8', 'surrogateescape').split('\0')) - {''}
    allowed = {'README.md', 'AGENT.md', 'AGENTS.md', 'ARCHITECTURE.md', 'pyproject.toml', '.gitignore'}
    suffixes = {'.py', '.md', '.sh', '.json', '.yml', '.yaml', '.toml', '.txt', '.csv', '.png', '.ssml', '.srt'}

    def eligible(name):
        return ((name.startswith(roots) or name in allowed)
                and (Path(name).suffix.lower() in suffixes or name == '.gitignore'))

    def safe_path(name):
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError(f'Source snapshot rejects a path outside the repository: {name!r}')
        reason = path_reason(name)
        if reason:
            raise ValueError(f'Source snapshot rejects {reason}: {name!r}')
        path = root
        for part in relative.parts:
            path /= part
            if path.is_symlink():
                raise ValueError(f'Source snapshot rejects a symlink: {name!r}')
        if not path.resolve().is_relative_to(root):
            raise ValueError(f'Source snapshot rejects a path outside the repository: {name!r}')
        return path

    # Validate indexed candidates before reading them or creating an archive.
    candidates = {name: safe_path(name) for name in sorted(names) if eligible(name)}

    def validate_input(path):
        try:
            name = path.relative_to(root).as_posix()
        except ValueError:
            raise ValueError('Source snapshot rejects an input outside the repository.') from None
        path = safe_path(name)
        if name not in names:
            raise ValueError(f'Source snapshot requires reviewed, tracked inputs; untracked: {name!r}')
        if path.suffix.lower() in suffixes and name not in candidates:
            raise ValueError(f'Required source falls outside the source snapshot scope: {name!r}')
        if not path.is_file():
            raise ValueError(f'Required source snapshot input is missing: {name!r}')

    return candidates, validate_input


def snapshot(output, entries=()):
    """Archive tracked public sources, retaining working-tree edits.

    Required local inputs must be reviewed and staged first. Rendered audio/video
    and fonts remain hash-recorded inputs, not additions to this source archive.
    """
    candidates, validate_input = snapshot_inputs()
    for entry in entries:
        input_hashes(entry, root=ROOT.resolve(), validate_path=validate_input)
    with zipfile.ZipFile(output / 'source.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
        for name, path in candidates.items():
            if path.is_file():
                archive.write(path, name)


def construct_one(pair, *, retain_all=False):
    index, entry, output = pair
    dest = output / 'construction' / f"{entry['order']:02d}_{entry['delivery_slug']}"
    dest.mkdir(parents=True)
    before = input_hashes(entry)
    code = run([sys.executable, 'scripts/teaching_revision/review.py', '--entry', str(index),
                '--output', str(dest), *(['--all-states'] if retain_all else [])], dest / 'construction.log', timeout=300)
    path = dest / 'audit.json'
    data = json.loads(path.read_text()) if path.is_file() else {'construction': 'failed'}
    if before != input_hashes(entry):
        data['construction'] = 'stale'
        code = 1
    data.update(input_sha256=before, input_signature=signature(before),
                inspector_sha256=sha256(ROOT / 'scripts/teaching_revision/review.py'),
                frame_sha256={p.name: sha256(p) for p in sorted(dest.glob('state_*.png'))})
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    states = data.get('states', [])
    shutil.rmtree(dest / '_media', ignore_errors=True)
    print(f"Construction {entry['order']:02d}: {data['construction']}", flush=True)
    return {'global_number': entry['order'], 'lesson_id': entry['lesson_id'],
            'legacy_id': entry['legacy_id'], 'returncode': code,
            'construction': data['construction'], 'states': len(states),
            'input_sha256': before,
            'retained_frames': len(data.get('retained_frames', [])),
            'overlap_candidate_states': sum(bool(s['overlaps']) for s in states),
            'outside_margin_candidate_states': sum(bool(s['outside']) for s in states),
            'visual_review': 'pending', 'full_motion_review': 'pending'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--numbers', help='Global numbers or stable/legacy IDs; default: the entire course')
    parser.add_argument('--no-render', action='store_true', help='Construction only; do not claim encoded-video validation')
    parser.add_argument('--jobs', type=int, choices=(1, 2), default=2,
                        help='Maximum concurrent construction/render subprocesses (default: 2)')
    parser.add_argument('--quality', choices=('ql', 'qh'), default='ql')
    parser.add_argument('--all-construction-states', action='store_true',
                        help='Retain every distinct construction endpoint for inspection')
    parser.add_argument('--narration', action='store_true',
                        help='Explicitly request real Azure audio; missing credentials block the run')
    parser.add_argument('--skip-tests', action='store_true',
                        help='Reuse separately recorded shared checks; skipped tests remain unverified')
    args = parser.parse_args()
    if args.narration and args.no_render:
        parser.error('--narration requires encoded rendering')
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    os.environ['MANIM_DISABLE_VOICEOVER'] = '1'
    os.environ['OPENBLAS_NUM_THREADS'] = '1'
    os.environ['OMP_NUM_THREADS'] = '1'
    status = {'publication': False, 'release_ready': False, 'listening': 'not_performed',
              'requested_audio_mode': 'azure_review' if args.narration else 'silent_preview',
              'narrated_duration_review': 'pending' if args.narration else 'not_assessable_from_silent_preview'}
    try:
        _, validate_input = snapshot_inputs()
        root = ROOT.resolve()
        _, all_entries = load_catalog(root / 'curriculum/programme_principal_fr.yaml',
                                      root=root, validate_path=validate_input)
        selected_ids = {resolve(x.strip(), all_entries)['lesson_id'] for x in args.numbers.split(',')} if args.numbers else {e['lesson_id'] for e in all_entries}
        selected = [(i, e) for i, e in enumerate(all_entries) if e['lesson_id'] in selected_ids]
        source_hashes = {}
        for _, entry in selected:
            path = root / entry['scene_file']
            validate_input(path)
            source_hashes[entry['lesson_id']] = hashlib.sha256(path.read_bytes()).hexdigest()
        commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        status.update(source_commit=commit, selected_numbers=[e['order'] for _, e in selected],
                      source_sha256=source_hashes)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        status.update(source_snapshot='blocked', reason=str(error))
        (output / 'STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
        print('Course review blocked by source preflight; see STATUS.json.', flush=True)
        return 1
    if args.narration:
        from tools.tts import configure_azure_speech_environment
        try:
            configure_azure_speech_environment(require_credentials=True)
        except (RuntimeError, ValueError) as error:
            status.update(narration='blocked', reason=str(error))
            (output / 'STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
            print('Narrated review blocked; see STATUS.json.', flush=True)
            return 1
    (output / 'tested_commit.txt').write_text(commit + '\n')
    try:
        snapshot(output, [entry for _, entry in selected])
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        status.update(source_snapshot='blocked', reason=str(error))
        (output / 'STATUS.json').write_text(json.dumps(status, indent=2) + '\n')
        print('Course review blocked by source snapshot; see STATUS.json.', flush=True)
        return 1
    status['tests_returncode'] = None if args.skip_tests else run([sys.executable, '-m', 'pytest', 'tests/test_course_catalog.py',
        'tests/test_render_curriculum.py', 'tests/test_syllabus_expansion.py', 'tests/test_teaching_revision.py',
        'tests/test_tts.py', 'tests/test_course_narration_preflight.py',
        'tests/test_narration_quality.py', 'tests/test_archive_renders.py', 'tests/test_course_workflow_syntax.py',
        'tests/test_course_delivery_regressions.py', 'tests/test_private_data_guard.py',
        'tests/test_course_source_snapshot.py',
        'tests/test_public_audit.py', 'tests/test_public_workflow_policy.py', 'tools/video_audit/tests',
        'tests/test_course_timing.py', 'tests/test_course_boundaries.py', 'tests/test_course_visual_followup.py',
        'tests/test_course_review.py', 'tests/test_course_review_a.py',
        'tests/test_course_review_b.py', 'tests/test_course_review_c.py',
        '-q', f"--junitxml={output / 'tests.xml'}"], output / 'tests.log')
    status['repository_ruff_returncode'] = None if args.skip_tests else run(['ruff', 'check', '.', '--output-format', 'json'], output / 'ruff.json')
    try:
        findings = json.loads((output / 'ruff.json').read_text())
        (output / 'ruff_summary.json').write_text(json.dumps({'by_code': dict(Counter(f['code'] for f in findings)),
            'by_top_level': dict(Counter(Path(f['filename']).relative_to(ROOT).parts[0] for f in findings)),
            'total': len(findings)}, indent=2) + '\n')
    except (OSError, ValueError, TypeError, KeyError):
        pass
    status['correctness_lint_returncode'] = None if args.skip_tests else run(['ruff', 'check', '--select', 'E9,F63,F7,F82', 'scenes', 'tools', 'scripts/render_curriculum.py', 'scripts/render_syllabus_expansion.py', 'scripts/course_audit.py'], output / 'correctness_lint.log')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        status['construction'] = list(pool.map(
            lambda pair: construct_one(pair, retain_all=args.all_construction_states),
            [(i, e, output) for i, e in selected]))
    status['videos'] = []
    if not args.no_render:
        from scripts.render_syllabus_expansion import render_one
        videos = output / 'videos'
        videos.mkdir()
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            mode = 'azure' if args.narration else 'silent'
            status['videos'] = list(pool.map(lambda e: render_one({**e, 'id': e['legacy_id']}, videos, mode, args.quality), [e for _, e in selected]))
    status['selected_render_checks_passed'] = (all(e['returncode'] == 0 for e in status['construction']) and
        bool(status['videos']) and all(v['render'] == 'passed' for v in status['videos']))
    status['automated_course_checks_passed'] = None if args.skip_tests else (status['tests_returncode'] == 0 and
        status['correctness_lint_returncode'] == 0 and all(e['returncode'] == 0 for e in status['construction']) and
        (args.no_render or all(v['render'] == 'passed' for v in status['videos'])))
    status['repository_lint_passed'] = None if args.skip_tests else status['repository_ruff_returncode'] == 0
    (output / 'STATUS.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'source_commit': commit, 'construction': len(status['construction']),
        'renders': len(status['videos']), 'course_checks_passed': status['automated_course_checks_passed'],
        'repository_lint_passed': status['repository_lint_passed']}, indent=2), flush=True)
    if args.skip_tests:
        return int(not (all(e['returncode'] == 0 for e in status['construction'])
                        if args.no_render else status['selected_render_checks_passed']))
    return int(not status['automated_course_checks_passed'])


if __name__ == '__main__':
    raise SystemExit(main())
