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


def run(command, path, *, timeout=600):
    with path.open('w', encoding='utf-8') as log:
        try:
            return subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                  timeout=timeout, check=False).returncode
        except subprocess.TimeoutExpired:
            return 124


def snapshot(output):
    roots = ('scenes/', 'tools/', 'scripts/', 'tests/', 'curriculum/', 'docs/', '.github/', '.vscode/', 'assets/branding/')
    names = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    allowed = {'README.md', 'AGENT.md', 'AGENTS.md', 'ARCHITECTURE.md', 'pyproject.toml', '.gitignore'}
    with zipfile.ZipFile(output / 'source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in names:
            path = ROOT / name
            if not path.is_file() or not (name.startswith(roots) or name in allowed):
                continue
            if path.suffix.lower() not in {'.py', '.md', '.sh', '.json', '.yml', '.yaml', '.toml', '.txt', '.csv', '.png', '.ssml', '.srt'} and name != '.gitignore':
                continue
            archive.write(path, name)


def construct_one(pair):
    index, entry, output = pair
    dest = output / 'construction' / f"{entry['order']:02d}_{entry['delivery_slug']}"
    dest.mkdir(parents=True)
    code = run([sys.executable, 'scripts/teaching_revision/review.py', '--entry', str(index),
                '--output', str(dest)], dest / 'construction.log', timeout=300)
    path = dest / 'audit.json'
    data = json.loads(path.read_text()) if path.is_file() else {'construction': 'failed'}
    states = data.get('states', [])
    shutil.rmtree(dest / '_media', ignore_errors=True)
    print(f"Construction {entry['order']:02d}: {data['construction']}", flush=True)
    return {'global_number': entry['order'], 'lesson_id': entry['lesson_id'],
            'legacy_id': entry['legacy_id'], 'returncode': code,
            'construction': data['construction'], 'states': len(states),
            'retained_frames': len(data.get('retained_frames', [])),
            'overlap_candidate_states': sum(bool(s['overlaps']) for s in states),
            'outside_margin_candidate_states': sum(bool(s['outside']) for s in states),
            'visual_review': 'pending', 'full_motion_review': 'pending'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--numbers', help='Global numbers or stable/legacy IDs; default: the entire course')
    parser.add_argument('--no-render', action='store_true', help='Construction only; do not claim encoded-video validation')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    os.environ['MANIM_DISABLE_VOICEOVER'] = '1'
    _, all_entries = load_catalog()
    selected_ids = {resolve(x.strip(), all_entries)['lesson_id'] for x in args.numbers.split(',')} if args.numbers else {e['lesson_id'] for e in all_entries}
    selected = [(i, e) for i, e in enumerate(all_entries) if e['lesson_id'] in selected_ids]
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    status = {'source_commit': commit, 'selected_numbers': [e['order'] for _, e in selected],
              'source_sha256': {e['lesson_id']: hashlib.sha256((ROOT / e['scene_file']).read_bytes()).hexdigest() for _, e in selected},
              'publication': False, 'release_ready': False, 'listening': 'not_performed'}
    (output / 'tested_commit.txt').write_text(commit + '\n')
    snapshot(output)
    status['tests_returncode'] = run([sys.executable, '-m', 'pytest', 'tests/test_course_catalog.py',
        'tests/test_render_curriculum.py', 'tests/test_syllabus_expansion.py', 'tests/test_teaching_revision.py',
        'tests/test_tts.py', 'tests/test_archive_renders.py', 'tests/test_course_workflow_syntax.py',
        'tests/test_course_delivery_regressions.py', 'tests/test_private_data_guard.py',
        'tests/test_public_audit.py', 'tests/test_public_workflow_policy.py', 'tools/video_audit/tests',
        '-q', f"--junitxml={output / 'tests.xml'}"], output / 'tests.log')
    status['repository_ruff_returncode'] = run(['ruff', 'check', '.', '--output-format', 'json'], output / 'ruff.json')
    try:
        findings = json.loads((output / 'ruff.json').read_text())
        (output / 'ruff_summary.json').write_text(json.dumps({'by_code': dict(Counter(f['code'] for f in findings)),
            'by_top_level': dict(Counter(Path(f['filename']).relative_to(ROOT).parts[0] for f in findings)),
            'total': len(findings)}, indent=2) + '\n')
    except (ValueError, TypeError, KeyError):
        pass
    status['correctness_lint_returncode'] = run(['ruff', 'check', '--select', 'E9,F63,F7,F82', 'scenes', 'tools', 'scripts/render_curriculum.py', 'scripts/render_syllabus_expansion.py', 'scripts/course_audit.py'], output / 'correctness_lint.log')
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        status['construction'] = list(pool.map(construct_one, [(i, e, output) for i, e in selected]))
    status['videos'] = []
    if not args.no_render:
        from scripts.render_syllabus_expansion import render_one
        videos = output / 'videos'
        videos.mkdir()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            status['videos'] = list(pool.map(lambda e: render_one({**e, 'id': e['legacy_id']}, videos, 'silent'), [e for _, e in selected]))
    status['automated_course_checks_passed'] = (status['tests_returncode'] == 0 and
        status['correctness_lint_returncode'] == 0 and all(e['returncode'] == 0 for e in status['construction']) and
        (args.no_render or all(v['render'] == 'passed' for v in status['videos'])))
    status['repository_lint_passed'] = status['repository_ruff_returncode'] == 0
    (output / 'STATUS.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'source_commit': commit, 'construction': len(status['construction']),
        'renders': len(status['videos']), 'course_checks_passed': status['automated_course_checks_passed'],
        'repository_lint_passed': status['repository_lint_passed']}, indent=2), flush=True)
    return int(not status['automated_course_checks_passed'])


if __name__ == '__main__':
    raise SystemExit(main())
