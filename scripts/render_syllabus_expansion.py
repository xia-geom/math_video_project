#!/usr/bin/env python3
"""Validate and preview syllabus candidates without publishing or Drive mirroring."""
from __future__ import annotations

import argparse
import ast
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'curriculum/extension_syllabus_fr.yaml'
SHARED = ('tools/teaching_layout.py', 'tools/teaching_voiceover.py', 'tools/tts.py',
          'tools/branding.py', 'assets/branding/uqam_logo.png', 'pyproject.toml')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_candidates(path=MANIFEST):
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if data.get('version') != 1 or data.get('release_ready') is not False:
        raise ValueError('Expected a version-one, non-release candidate manifest.')
    entries = data.get('entries', [])
    if not entries:
        raise ValueError('No candidate entries.')
    canonical = yaml.safe_load((ROOT / data['canonical_manifest']).read_text(encoding='utf-8'))
    known = {f"{'P' if e['track'] == 'programme' else 'E'}{e['order']:02d}"
             for e in canonical['entries']}
    ids = [e['id'] for e in entries]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r'S\d{2}', i) for i in ids):
        raise ValueError('Candidate IDs must be unique S identifiers.')
    sources, classes = set(), set()
    by_id = {e['id']: e for e in entries}
    for e in entries:
        for key in ('title', 'module', 'scene_file', 'scene_class', 'prerequisites',
                    'objective', 'self_check', 'status'):
            if key not in e or (key != 'prerequisites' and not e[key]):
                raise ValueError(f"{e['id']}: missing {key}")
        p = (ROOT / e['scene_file']).resolve()
        if not p.is_relative_to(ROOT / 'scenes') or not p.is_file():
            raise ValueError(f"{e['id']}: invalid scene source")
        tree = ast.parse(p.read_text(encoding='utf-8'))
        if e['scene_class'] not in {n.name for n in tree.body if isinstance(n, ast.ClassDef)}:
            raise ValueError(f"{e['id']}: class absent from source")
        if e['scene_file'] in sources or e['scene_class'] in classes:
            raise ValueError('Duplicate scene file or class.')
        sources.add(e['scene_file'])
        classes.add(e['scene_class'])
        if set(e['prerequisites']) - (known | set(ids)):
            raise ValueError(f"{e['id']}: unknown prerequisite")
        if e['status'] != 'authored':
            raise ValueError('Measured review states belong in dated evidence, not this source queue.')
    visited, active = set(), set()

    def visit(key):
        if key in active:
            raise ValueError('Cyclic candidate prerequisites.')
        if key in visited or key not in by_id:
            return
        active.add(key)
        for parent in by_id[key]['prerequisites']:
            visit(parent)
        active.remove(key)
        visited.add(key)

    for key in ids:
        visit(key)
    return data, entries


def select_candidates(entries, requested):
    if not requested:
        return list(entries)
    ids = {item.strip() for item in requested.split(',') if item.strip()}
    unknown = ids - {e['id'] for e in entries}
    if not ids or unknown:
        raise ValueError(f'Unknown or empty candidate selection: {sorted(unknown)}')
    return [e for e in entries if e['id'] in ids]


def inspect_streams(info, mode):
    video = [s for s in info.get('streams', []) if s.get('codec_type') == 'video']
    audio = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
    if len(video) != 1 or float(info.get('format', {}).get('duration', 0)) <= 0:
        raise ValueError('Expected one video stream and positive duration.')
    s = video[0]
    if (s['width'], s['height']) != (854, 480) or Fraction(s['r_frame_rate']) != 15:
        raise ValueError('Unexpected low-quality preview dimensions or frame rate.')
    if bool(audio) != (mode == 'azure'):
        raise ValueError('Audio mode does not match the encoded streams.')
    return float(info['format']['duration']), bool(audio)


def render_one(entry, output, mode):
    dest = output / entry['id']
    dest.mkdir()
    label = 'silent_preview' if mode == 'silent' else 'azure_review'
    stem = f"{entry['id']}_{label}"
    result = {'id': entry['id'], 'scene': entry['scene_class'], 'mode': label,
              'source_sha256': digest(ROOT / entry['scene_file']),
              'render': 'failed', 'visual_review': 'pending', 'full_motion_review': 'pending',
              'listening': 'not_performed', 'release_ready': False}
    env = os.environ.copy()
    env['MANIM_DISABLE_VOICEOVER'] = '1' if mode == 'silent' else '0'
    env['PYTHONPATH'] = str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')
    try:
        with (dest / 'render.log').open('w', encoding='utf-8') as log:
            process = subprocess.run([sys.executable, '-m', 'manim', '-ql', '--disable_caching',
                                      '--media_dir', str(dest / 'media'), '-o', stem,
                                      entry['scene_file'], entry['scene_class']],
                                     cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                     timeout=300, check=False)
        if process.returncode:
            raise RuntimeError(f'Manim exited with {process.returncode}; see render.log')
        matches = list((dest / 'media/videos').glob(f'**/{stem}.mp4'))
        if len(matches) != 1:
            raise RuntimeError('Expected exactly one fresh rendered MP4.')
        film = dest / f'{stem}.mp4'
        shutil.copy2(matches[0], film)
        info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                                                   '-show_format', '-of', 'json', str(film)]))
        duration, has_audio = inspect_streams(info, mode)
        (dest / 'ffprobe.json').write_text(json.dumps(info, indent=2) + '\n')
        for subtitle in matches[0].parent.glob('*.srt'):
            shutil.copy2(subtitle, dest / subtitle.name)
        frames = dest / 'frames'
        frames.mkdir()
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(film), '-vf', 'fps=1/3',
                        str(frames / 'sample_%04d.png')], check=True, timeout=90)
        result.update(render='passed', duration=duration, has_audio=has_audio,
                      video_sha256=digest(film), frame_interval_seconds=3,
                      frame_samples=len(list(frames.glob('*.png'))))
        shutil.rmtree(dest / 'media')
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        result['error'] = str(exc)
    (dest / 'STATUS.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(entry['id'], result['render'], result.get('error', ''), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids', help='Comma-separated candidate IDs; default: all required candidates.')
    parser.add_argument('--mode', choices=('silent', 'azure'), default='silent')
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    _, entries = read_candidates()
    selected = select_candidates(entries, args.ids)
    if args.check_only:
        print(f'Validated {len(entries)} candidates; selected {len(selected)}.')
        return 0
    if args.mode == 'azure':
        sys.path.insert(0, str(ROOT))
        from dotenv import load_dotenv
        from tools import tts
        load_dotenv(ROOT / '.env', override=False)
        # Fail before creating a misleading preview when real narration was requested.
        tts.configure_azure_speech_environment(require_credentials=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = (args.output or ROOT / 'review_artifacts/syllabus' / stamp).resolve()
    output.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    status = {'source_commit': commit, 'manifest_sha256': digest(MANIFEST), 'mode': args.mode,
              'shared_sha256': {name: digest(ROOT / name) for name in SHARED},
              'publication': False, 'drive_mirror': False, 'release_ready': False}
    workers = 2 if args.mode == 'silent' else 1
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        status['videos'] = list(pool.map(lambda e: render_one(e, output, args.mode), selected))
    (output / 'STATUS.json').write_text(json.dumps(status, ensure_ascii=False, indent=2) + '\n')
    print(output)
    return int(any(v['render'] != 'passed' for v in status['videos']))


if __name__ == '__main__':
    raise SystemExit(main())
