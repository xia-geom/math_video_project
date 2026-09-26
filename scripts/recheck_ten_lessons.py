#!/usr/bin/env python3
"""Fresh silent encoded reviews of the ten additions, with containment evidence.

No publication, cloud synthesis, fake narration, Git writes or Drive copies.
Commands are split explicitly so the review runner also passes the course lint gate.
"""
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
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.course_catalog import delivery_name, load_catalog, resolve  # noqa: E402
from tools.course_timing import seconds, validate_timing_records  # noqa: E402


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def extract_samples(video, folder, records, rate, duration):
    samples = {}
    for index, record in enumerate(records):
        for kind, instant in (
            ('transition', record['start'] + 0.30),
            ('stable', (record['visible_from'] + record['speech_context_end']) / 2),
        ):
            frame = min(round(instant * rate), int(duration * rate) - 1)
            samples.setdefault(frame, []).append({'kind': kind, 'explanation': index,
                                                  'page': record['page']})
    folder.mkdir()
    ordered = sorted(samples)
    expression = "select='" + '+'.join(f'eq(n,{frame})' for frame in ordered) + "'"
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(video), '-vf', expression,
                    '-fps_mode', 'vfr', '-q:v', '2', str(folder / 'sample_%04d.jpg')],
                   check=True, timeout=300)
    if len(list(folder.glob('*.jpg'))) != len(ordered):
        raise RuntimeError('Extracted frame count differs from the requested samples.')
    save_json(folder / 'samples.json', [
        {'file': f'sample_{i:04d}.jpg', 'frame': frame, 'seconds': frame / rate,
         'purpose': samples[frame]} for i, frame in enumerate(ordered, 1)
    ])
    return len(ordered)


def render_one(entry, output, quality, shared):
    dest = output / delivery_name(entry)
    dest.mkdir()
    stem = delivery_name(entry) + '_silent_review'
    result = {'number': entry['order'], 'lesson_id': entry['lesson_id'],
              'legacy_id': entry['legacy_id'], 'render': 'failed', 'quality': quality,
              'audio_mode': 'silent_preview', 'listening': 'not_performed',
              'visual_review': 'pending', 'narrated_duration': 'not_measured',
              'release_ready': False, 'source_sha256': sha256(ROOT / entry['scene_file']),
              'shared_sha256': shared}
    env = os.environ.copy()
    env.update(MANIM_DISABLE_VOICEOVER='1',
               TEACHING_TIMING_PATH=str(dest / 'teaching_timing.json'),
               TEACHING_LAYOUT_AUDIT_PATH=str(dest / 'layout_audit.json'))
    env['PYTHONPATH'] = str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')
    try:
        command = [sys.executable, '-m', 'manim', '-' + quality, '--disable_caching',
                   '--media_dir', str(dest / '_media'), '-o', stem,
                   entry['scene_file'], entry['scene_class']]
        with (dest / 'render.log').open('w', encoding='utf-8') as log:
            subprocess.run(
                command, cwd=ROOT, env=env, stdout=log,
                stderr=subprocess.STDOUT, check=True, timeout=1200,
            )
        files = list((dest / '_media/videos').glob(f'**/{stem}.mp4'))
        if len(files) != 1:
            raise RuntimeError('Expected exactly one fresh encoded output.')
        video = dest / (stem + '.mp4')
        shutil.copy2(files[0], video)
        probe_command = [
            'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video),
        ]
        info = json.loads(subprocess.check_output(probe_command))
        save_json(dest / 'ffprobe.json', info)
        streams = info.get('streams', [])
        videos = [s for s in streams if s['codec_type'] == 'video']
        if len(videos) != 1 or any(s['codec_type'] == 'audio' for s in streams):
            raise RuntimeError('This review must contain one video stream and no audio.')
        expected = (1920, 1080, 60) if quality == 'qh' else (854, 480, 15)
        v = videos[0]
        actual = (v['width'], v['height'], Fraction(v['r_frame_rate']))
        if actual != expected:
            raise RuntimeError(f'Unexpected stream format: {actual}')
        duration = seconds(info['format']['duration'])
        records = json.loads((dest / 'teaching_timing.json').read_text())
        errors = validate_timing_records(records, mode='silent_preview', tolerance=0.12)
        if errors or records[-1]['end'] > duration + 0.12:
            raise RuntimeError('Timing evidence invalid: ' + '; '.join(errors))
        layout = json.loads((dest / 'layout_audit.json').read_text())
        if (
            layout['status'] != 'passed'
            or layout['panel_checks'] <= 0
            or layout['visible_panel_checks'] <= 0
            or layout['worked_example_steps'] != 10
            or layout['practice_questions'] != 1
            or layout['practice_solution_steps'] != 3
        ):
            raise RuntimeError('Missing containment, worked-example or practice evidence.')
        frame_count = extract_samples(video, dest / 'frames', records, expected[2], duration)
        result.update(render='passed', duration_seconds=duration,
                      dimensions=list(expected[:2]), fps=expected[2],
                      narration_word_count=sum(len(r['text'].split()) for r in records),
                      explanation_count=len(records), sampled_frames=frame_count,
                      video_sha256=sha256(video), containment=layout)
        shutil.rmtree(dest / '_media')
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
        result['error'] = str(exc)
    save_json(dest / 'STATUS.json', result)
    print(f"{entry['order']:02d}: {result['render']} {result.get('error', '')}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quality', choices=('ql', 'qh'), default='qh')
    parser.add_argument('--numbers', default='', help='Optional global numbers or stable IDs')
    args = parser.parse_args()
    entries = [e for e in load_catalog()[1] if e['legacy_id'].startswith('S')]
    if args.numbers:
        selected = {resolve(v.strip(), entries)['lesson_id'] for v in args.numbers.split(',')}
        entries = [e for e in entries if e['lesson_id'] in selected]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    names = ['tools/expanded_teaching.py', 'tools/teaching_layout.py', 'tools/course_timing.py',
             'tools/teaching_voiceover.py', 'tools/tts.py', 'tools/branding.py',
             'curriculum/programme_principal_fr.yaml', 'curriculum/duration_policy.yaml',
             'assets/branding/uqam_logo.png', 'tools/lesson_practice.py',
             'curriculum/practice_questions.yaml']
    names += [str(p.relative_to(ROOT)) for p in sorted((ROOT / 'curriculum/worked_examples').glob('*.yaml'))]
    shared = {name: sha256(ROOT / name) for name in names}
    snapshot_names = names + [e['scene_file'] for e in entries] + [
        'scripts/recheck_ten_lessons.py', 'tests/test_expanded_teaching.py',
        'tests/test_practice_questions.py', 'tests/test_practice_layout.py',
        '.github/workflows/ten-lesson-recheck.yml']
    with zipfile.ZipFile(output / 'reviewed_source.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in snapshot_names:
            archive.write(ROOT / name, name)
    status = {'source_commit': commit, 'mode': 'silent_preview', 'quality': args.quality,
              'selected_numbers': [e['order'] for e in entries],
              'publication': False, 'release_ready': False}
    save_json(output / 'STATUS.json', status)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        status['videos'] = list(pool.map(lambda e: render_one(e, output, args.quality, shared), entries))
    save_json(output / 'STATUS.json', status)
    return int(any(v['render'] != 'passed' for v in status['videos']))


if __name__ == '__main__':
    raise SystemExit(main())
