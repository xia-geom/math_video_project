#!/usr/bin/env python3
"""Render isolated, explicitly silent course reviews; never synthesize or publish.

Each process renders one stable catalogue identity. Opening/chapter/closing
cards and candidate body states are sampled from the actual encoded movie.
Samples and structural checks do not certify full playback or listening.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.course_catalog import load_catalog  # noqa: E402
from tools.course_review import input_hashes, renderer_runtime_versions, sha256  # noqa: E402


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def render_one(entry, output):
    destination = output / f"{entry['order']:02d}"
    destination.mkdir(parents=True, exist_ok=True)
    os.environ['MANIM_DISABLE_VOICEOVER'] = '1'
    for name, filename in [('TEACHING_CHAPTER_AUDIT_PATH', 'cards.json'),
                           ('TEACHING_TIMING_PATH', 'narration.json'),
                           ('TEACHING_LAYOUT_AUDIT_PATH', 'layout.json')]:
        os.environ[name] = str(destination / filename)
    # A scene accidentally ignoring silent mode must fail before Azure starts.
    from manim_voiceover.services.azure import AzureService

    def forbidden_azure(*args, **kwargs):
        raise RuntimeError('Azure is disabled for this silent course review.')

    AzureService.__init__ = forbidden_azure
    from manim import ManimColor, MathTex, Scene, Tex, Text, tempconfig

    before = input_hashes(entry)
    status = {'lesson_id': entry['lesson_id'], 'number': entry['order'],
              'title': entry['title'], 'mode': 'silent_preview', 'quality': 'ql',
              'render': 'running', 'azure_disabled': True, 'input_sha256': before,
              'source_sha256': before[entry['scene_file']],
              'runtime_versions': renderer_runtime_versions(),
              'full_motion': 'not_checked', 'listening': 'not_performed',
              'institutional_approval': 'pending', 'release_ready': False}
    write_json(destination / 'STATUS.json', status)
    checkpoints = []
    original_play, original_wait = Scene.play, Scene.wait
    depth = 0

    def capture(scene):
        labels, seen = [], set()

        def visit(obj):
            if id(obj) in seen:
                return
            seen.add(id(obj))
            if isinstance(obj, (Text, Tex, MathTex)):
                leaves = obj.family_members_with_points()
                if obj.width < .001 or obj.height < .001 or not any(
                        max(float(m.get_fill_opacity().max()),
                            float(m.get_stroke_opacity().max())) > .05 for m in leaves):
                    return
                box = [float(obj.get_left()[0]), float(obj.get_right()[0]),
                       float(obj.get_bottom()[1]), float(obj.get_top()[1])]
                # BackgroundRectangle.get_color recurses in Manim 0.19. Read
                # rendered RGBA data directly, including only visible paint.
                colors = {ManimColor(rgba[:3]).to_hex() for m in leaves
                          for rgba in [*m.fill_rgbas, *m.stroke_rgbas] if rgba[3] > .05}
                labels.append({'text': getattr(obj, 'text', getattr(obj, 'tex_string', '?')),
                               'box': box, 'colors': sorted(colors),
                               'outside_frame': box[0] < -7.12 or box[1] > 7.12
                               or box[2] < -4.01 or box[3] > 4.01})
            else:
                for child in obj.submobjects:
                    visit(child)

        for obj in scene.mobjects:
            visit(obj)
        if labels:
            checkpoints.append({'time': float(scene.renderer.time), 'labels': labels})

    def wrapped(original):
        def call(scene, *args, **kwargs):
            nonlocal depth
            depth += 1
            try:
                result = original(scene, *args, **kwargs)
            finally:
                depth -= 1
            if depth == 0:
                capture(scene)
            return result
        return call

    Scene.play, Scene.wait = wrapped(original_play), wrapped(original_wait)
    try:
        source = ROOT / entry['scene_file']
        sys.path.insert(0, str(source.parent))
        with tempconfig({'pixel_width': 854, 'pixel_height': 480, 'frame_rate': 15,
                         'verbosity': 'WARNING', 'progress_bar': 'none',
                         'disable_caching': True, 'media_dir': str(destination / 'media'),
                         'output_file': entry['lesson_id'] + '_silent'}):
            spec = importlib.util.spec_from_file_location('coherence_target', source)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            scene = getattr(module, entry['scene_class'])()
            scene.render()
            generated = Path(scene.renderer.file_writer.movie_file_path)
        movie = destination / (entry['lesson_id'] + '_silent.mp4')
        shutil.copy2(generated, movie)
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(movie)]))
        write_json(destination / 'ffprobe.json', probe)
        if any(s['codec_type'] == 'audio' for s in probe['streams']):
            raise ValueError('An explicitly silent preview unexpectedly contains audio.')
        if input_hashes(entry) != before:
            raise ValueError('Source changed during rendering; retain this attempt but rebuild.')
        cards = json.loads((destination / 'cards.json').read_text())
        kinds = [card['kind'] for card in cards]
        if (kinds[0] != 'opening' or kinds[-3:] != ['recap', 'closing_practice', 'closing']
                or not 3 <= kinds.count('chapter') <= 4):
            raise ValueError('Opening, authored chapters or common ending is incomplete.')
        if not any(''.join(label['text'].split()) == 'Findelacapsule'
                   for label in checkpoints[-1]['labels']):
            raise ValueError('Final card is not the last recorded visible state.')
        status.update(render='passed', video_path=str(movie.relative_to(ROOT)),
                      video_sha256=sha256(movie), duration=float(probe['format']['duration']),
                      chapter_count=kinds.count('chapter'),
                      clipped_state_candidates=sum(any(x['outside_frame'] for x in p['labels'])
                                                   for p in checkpoints),
                      colored_text_candidates=sum(any(c not in {'#000000', '#FFFFFF'}
                                                     for x in p['labels'] for c in x['colors'])
                                                  for p in checkpoints))
    except Exception:
        status.update(render='failed', error=traceback.format_exc())
    finally:
        Scene.play, Scene.wait = original_play, original_wait
        write_json(destination / 'checkpoints.json', checkpoints)
        write_json(destination / 'STATUS.json', status)
    return 0 if status['render'] == 'passed' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--order', type=int, action='append')
    parser.add_argument('--jobs', type=int, default=2, choices=(1, 2),
                        help='Concurrent render processes (default: 2; maximum: 2).')
    parser.add_argument('--worker', help=argparse.SUPPRESS)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / 'review_artifacts'):
        parser.error('Review outputs must be under this repository’s review_artifacts directory.')
    entries = load_catalog()[1]
    if args.worker:
        return render_one(next(e for e in entries if e['lesson_id'] == args.worker), output)
    selected = [e for e in entries if not args.order or e['order'] in args.order]
    if args.order and set(args.order) != {e['order'] for e in selected}:
        parser.error('Unknown catalogue number.')

    def run(entry):
        destination = output / f"{entry['order']:02d}"
        destination.mkdir(parents=True, exist_ok=True)
        if (destination / 'STATUS.json').exists():
            raise ValueError(f'Use a new output directory to preserve the previous attempt: {destination}')
        with (destination / 'render.log').open('w') as log:
            result = subprocess.run([sys.executable, __file__, '--output', str(output),
                                     '--worker', entry['lesson_id']], cwd=ROOT,
                                    stdout=log, stderr=subprocess.STDOUT, timeout=1800)
        print(f"{entry['order']:02d} {entry['lesson_id']}: {'passed' if result.returncode == 0 else 'failed'}", flush=True)
        return result.returncode

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(run, selected))
    return int(any(results))


if __name__ == '__main__':
    raise SystemExit(main())
