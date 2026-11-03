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
from tools.course_catalog import load_catalog, resolve  # noqa: E402
from tools.course_review import input_hashes, sha256, signature  # noqa: E402


def run(command, path, *, timeout=600):
    with path.open('w', encoding='utf-8') as log:
        try:
            return subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=timeout, check=False).returncode
        except subprocess.TimeoutExpired:
            return 124


def snapshot(output):
    roots = ('scenes/', 'tools/', 'scripts/', 'tests/', 'curriculum/', 'docs/', '.github/', '.vscode/', 'assets/branding/')
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT).decode().split('\0')
    allowed = {'README.md', 'AGENT.md', 'AGENTS.md', 'ARCHITECTURE.md', 'pyproject.toml', '.gitignore'}
    with zipfile.ZipFile(output / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(set(names)):
            path = ROOT / name
            if not path.is_file() or not (name.startswith(roots) or name in allowed):
                continue
            if path.suffix.lower() not in {'.py', '.md', '.sh', '.json', '.yml', '.yaml', '.toml', '.txt', '.csv', '.png', '.ssml', '.srt'} and name != '.gitignore':
                continue
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
    _, all_entries = load_catalog()
    selected_ids = {resolve(x.strip(), all_entries)['lesson_id'] for x in args.numbers.split(',')} if args.numbers else {e['lesson_id'] for e in all_entries}
    selected = [(i, e) for i, e in enumerate(all_entries) if e['lesson_id'] in selected_ids]
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    status = {'source_commit': commit, 'selected_numbers': [e['order'] for _, e in selected],
              'source_sha256': {e['lesson_id']: hashlib.sha256((ROOT / e['scene_file']).read_bytes()).hexdigest() for _, e in selected},
              'publication': False, 'release_ready': False, 'listening': 'not_performed',
              'requested_audio_mode': 'azure_review' if args.narration else 'silent_preview',
              'narrated_duration_review': 'pending' if args.narration else 'not_assessable_from_silent_preview'}
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
    snapshot(output)
    status['tests_returncode'] = None if args.skip_tests else run([sys.executable, '-m', 'pytest', 'tests/test_course_catalog.py',
        'tests/test_render_curriculum.py', 'tests/test_syllabus_expansion.py', 'tests/test_teaching_revision.py',
        'tests/test_tts.py', 'tests/test_archive_renders.py', 'tests/test_course_workflow_syntax.py',
        'tests/test_course_delivery_regressions.py', 'tests/test_private_data_guard.py',
        'tests/test_public_audit.py', 'tests/test_public_workflow_policy.py', 'tools/video_audit/tests',
        'tests/test_course_timing.py', 'tests/test_course_boundaries.py', 'tests/test_course_visual_followup.py',
        'tests/test_course_review.py', 'tests/test_course_review_a.py',
        'tests/test_course_review_b.py', 'tests/test_course_review_c.py',
        'tests/test_course_review_audio.py', 'tests/test_course_review_scope_import.py',
        'tests/test_narration_provenance.py',
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
            status['videos'] = list(pool.map(lambda e: render_one({**e, 'id': e['legacy_id'] or e['lesson_id']}, videos, mode, args.quality), [e for _, e in selected]))
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
