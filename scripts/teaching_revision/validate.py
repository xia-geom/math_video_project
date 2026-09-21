"""Review changed teaching sources; separate construction, video and cloud speech."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.teaching_revision.review import entries  # noqa: E402


def call(args, log, **kwargs):
    with log.open('w') as stream:
        return subprocess.run([str(a) for a in args], cwd=ROOT, stdout=stream,
                              stderr=subprocess.STDOUT, **kwargs).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--narration', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    targets = entries()
    result = {'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
              'listening': 'not_performed', 'full_motion_review': 'pending', 'publication': False}
    if not args.narration:
        result['tests_returncode'] = call([sys.executable, '-m', 'pytest', 'tests/test_tts.py',
                                          'tests/test_teaching_revision.py', '-q',
                                          f'--junitxml={output / "tests.xml"}'], output / 'tests.log')
        result['compile_returncode'] = call([sys.executable, '-m', 'compileall', '-q', 'scenes', 'tools',
                                            'scripts/teaching_revision'], output / 'compile.log')
        result['focused_correctness_lint'] = call(['ruff', 'check', '--select', 'E9,F63,F7,F82',
                                                  'scenes', 'tools/teaching_layout.py',
                                                  'tools/teaching_voiceover.py', 'tools/branding.py',
                                                  'scripts/teaching_revision'], output / 'correctness_lint.log')

        def inspect(index):
            entry = targets[index]
            key = f"{entry['track']}_{entry['order']:02d}"
            dest = output / 'layout' / key
            dest.mkdir(parents=True, exist_ok=True)
            try:
                code = call([sys.executable, ROOT / 'scripts/teaching_revision/review.py', '--entry', index,
                             '--output', dest], dest / 'construction.log', timeout=300)
            except subprocess.TimeoutExpired:
                code = 124
            p = dest / 'audit.json'
            data = json.loads(p.read_text()) if p.exists() else {**entry, 'construction': 'failed'}
            states = data.pop('states', [])
            clipping = sum(any(a['box'][0] < -7.12 or a['box'][1] > 7.12 or
                              a['box'][2] < -4.01 or a['box'][3] > 4.01 for a in s['labels']) for s in states)
            data.update(key=key, returncode=code, states=len(states),
                        overlap_candidates=sum(bool(s['overlaps']) for s in states),
                        frame_clipping_candidates=clipping,
                        safe_margin_candidates=sum(bool(s['outside']) for s in states))
            # Keep meaningful evidence, not LaTeX/cache bulk.
            shutil.rmtree(dest / '_media', ignore_errors=True)
            print(key, code, data['overlap_candidates'], clipping, flush=True)
            return data

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            summaries = list(pool.map(inspect, range(len(targets))))
        (output / 'layout_summary.json').write_text(json.dumps(summaries, ensure_ascii=False, indent=2)+'\n')
        result['construction_failures'] = [s['key'] for s in summaries if s['returncode']]

    result['videos'] = []
    selected = [e for e in targets if e['legacy_id'] in {'E02', 'E03'}]
    for entry in selected:
        mode = 'azure_review' if args.narration else 'silent_layout_preview'
        stem = f"{Path(entry['scene_file']).parent.name}_{mode}"
        dest = output / 'videos' / stem
        dest.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env['MANIM_DISABLE_VOICEOVER'] = '0' if args.narration else '1'
        code = call([sys.executable, '-m', 'manim', '-ql', '--disable_caching',
                     '--media_dir', dest / 'media', '-o', stem, entry['scene_file'], entry['scene_class']],
                    dest / 'render.log', env=env, timeout=300)
        data = {'scene': entry['scene_class'], 'mode': mode, 'returncode': code}
        candidates = list((dest / 'media/videos').glob(f'**/{stem}.mp4'))
        if code == 0 and len(candidates) == 1:
            film = dest / f'{stem}.mp4'
            shutil.copy2(candidates[0], film)
            info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
                              '-show_format', '-of', 'json', str(film)]))
            audio = [s for s in info['streams'] if s['codec_type'] == 'audio']
            data.update(duration=float(info['format']['duration']), has_audio=bool(audio),
                        sha256=hashlib.sha256(film.read_bytes()).hexdigest())
            if bool(audio) != args.narration:
                data['returncode'] = 1
                data['error'] = 'Unexpected audio-stream contract'
            (dest / 'ffprobe.json').write_text(json.dumps(info, indent=2)+'\n')
            for caption in candidates[0].parent.glob('*.srt'):
                shutil.copy2(caption, dest / caption.name)
            # Encoded checkpoints, including the standard opening; full-motion
            # review remains distinct from these samples.
            for index, t in enumerate([0.8, 3, data['duration']/3, data['duration']*2/3, data['duration']-1]):
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(max(0,t)), '-i', str(film),
                                '-frames:v', '1', '-update', '1', str(dest / f'frame_{index}.png')], check=True)
            shutil.rmtree(dest / 'media', ignore_errors=True)
        result['videos'].append(data)
    name = 'azure_status.json' if args.narration else 'STATUS.json'
    (output / name).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    failures = any(v['returncode'] for v in result['videos'])
    if not args.narration:
        failures = failures or result['tests_returncode'] or result['compile_returncode'] or result['focused_correctness_lint'] or result['construction_failures']
    return int(bool(failures))


if __name__ == '__main__':
    raise SystemExit(main())
