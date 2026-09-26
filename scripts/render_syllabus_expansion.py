#!/usr/bin/env python3
"""Validate and preview syllabus candidates without publishing or Drive mirroring."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.course_timing import (  # noqa: E402
    assess_duration, load_duration_policy, seconds, validate_timing_records,
)
MANIFEST = ROOT / 'curriculum/extension_syllabus_fr.yaml'
SHARED = ('tools/teaching_layout.py', 'tools/teaching_voiceover.py', 'tools/tts.py',
          'tools/branding.py', 'assets/branding/uqam_logo.png', 'pyproject.toml',
          'tools/course_timing.py', 'curriculum/duration_policy.yaml')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_candidates(path=MANIFEST):
    sys.path.insert(0, str(ROOT))
    from tools.course_catalog import load_catalog
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if data.get('version') != 2 or data.get('release_ready') is not False:
        raise ValueError('Expected a version-two, non-release production scope.')
    _, rows = load_catalog(ROOT / data['canonical_manifest'])
    by_id = {e['lesson_id']: e for e in rows}
    ids = data['candidate_ids']
    if not ids or len(ids) != len(set(ids)) or set(ids) - by_id.keys():
        raise ValueError('Invalid candidate scope; sources belong in the main catalogue.')
    return data, sorted(({**by_id[key], 'id': by_id[key]['legacy_id']} for key in ids), key=lambda e: e['order'])


def select_candidates(entries, requested):
    if not requested:
        return list(entries)
    from tools.course_catalog import resolve
    selectors = {value.strip() for value in requested.split(',') if value.strip()}
    if not selectors:
        raise ValueError('Empty candidate selection')
    selected = {resolve(value, entries)['lesson_id'] for value in selectors}
    return [e for e in entries if e['lesson_id'] in selected]


def inspect_streams(info, mode):
    video = [s for s in info.get('streams', []) if s.get('codec_type') == 'video']
    audio = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
    duration = seconds(info.get('format', {}).get('duration'))
    if len(video) != 1:
        raise ValueError('Expected one video stream and positive duration.')
    s = video[0]
    if (s['width'], s['height']) != (854, 480) or Fraction(s['r_frame_rate']) != 15:
        raise ValueError('Unexpected low-quality preview dimensions or frame rate.')
    if bool(audio) != (mode == 'azure'):
        raise ValueError('Audio mode does not match the encoded streams.')
    return duration, bool(audio)


def render_one(entry, output, mode):
    dest = output / f"{entry['order']:02d}_{entry['delivery_slug']}"
    dest.mkdir()
    label = 'silent_preview' if mode == 'silent' else 'azure_review'
    stem = f"{entry['order']:02d}_{entry['delivery_slug']}_{label}"
    result = {'id': entry['id'], 'global_number': entry['order'],
              'lesson_id': entry['lesson_id'], 'scene': entry['scene_class'], 'mode': label,
              'source_sha256': digest(ROOT / entry['scene_file']),
              'render': 'failed', 'visual_review': 'pending', 'full_motion_review': 'pending',
              'listening': 'not_performed', 'release_ready': False}
    env = os.environ.copy()
    env['MANIM_DISABLE_VOICEOVER'] = '1' if mode == 'silent' else '0'
    env['PYTHONPATH'] = str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')
    env['TEACHING_TIMING_PATH'] = str((dest / 'teaching_timing.json').resolve())
    result['shared_sha256'] = {name: digest(ROOT / name) for name in SHARED}
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
        result['duration_review'] = assess_duration(
            duration, mode=label, has_audio=has_audio, policy=load_duration_policy())
        if result['duration_review']['status'] == 'outside_range':
            raise RuntimeError('Narrated duration is outside the documented course range.')
        timing_file = dest / 'teaching_timing.json'
        result['pacing_review'] = {'status': 'not_instrumented', 'records': 0}
        if timing_file.is_file():
            records = json.loads(timing_file.read_text(encoding='utf-8'))
            errors = validate_timing_records(records, mode=label)
            if records and float(records[-1]['end']) > duration + 0.10:
                errors.append('Recorded timing exceeds the encoded video duration.')
            result['pacing_review'] = {'status': 'failed' if errors else 'recorded',
                                      'records': len(records), 'errors': errors,
                                      'mode': label}
            if errors:
                raise RuntimeError('; '.join(errors))
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
