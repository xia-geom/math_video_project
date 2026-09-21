"""Measure actual Manim construction states; candidates are not visual approvals."""
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def entries():
    import yaml
    data = yaml.safe_load((ROOT / 'curriculum/programme_principal_fr.yaml').read_text())
    return sorted(data['entries'], key=lambda e: e['order'])


def source_inventory(entry):
    path = ROOT / entry['scene_file']
    source = path.read_text(encoding='utf-8')
    calls = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Call)]
    small = []
    for n in calls:
        if getattr(n.func, 'id', '') not in {'Text', 'Tex', 'MathTex'}:
            continue
        for k in n.keywords:
            if k.arg == 'font_size' and isinstance(k.value, ast.Constant):
                size = k.value.value
                if isinstance(size, (int, float)) and size < 26:
                    small.append({'line': n.lineno, 'size': size})
    return {**entry, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'intro_calls': sum(getattr(n.func, 'id', '') == 'play_uqam_intro' for n in calls),
            'small_size_sites': small, 'source_lines': len(source.splitlines())}


def audit_one(entry, output):
    from manim import MathTex, Scene, Tex, Text, tempconfig
    import numpy as np

    path = ROOT / entry['scene_file']
    spec = importlib.util.spec_from_file_location('review_target', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    scene_type = getattr(module, entry['scene_class'])
    output.mkdir(parents=True, exist_ok=True)
    (output / '_media').mkdir(exist_ok=True)
    states, seen, kept = [], set(), []
    frame_limit = 100 if entry['legacy_id'] in {'E02', 'E03', 'P01', 'P08', 'P12'} else 12
    original_play, original_wait = Scene.play, Scene.wait
    busy = False

    def inspect_state(scene):
        nonlocal busy
        if busy:
            return
        busy = True
        try:
            labels, ids = [], set()

            def walk(obj):
                if id(obj) in ids:
                    return
                ids.add(id(obj))
                if isinstance(obj, (Text, Tex, MathTex)):
                    if obj.width < 0.001 or obj.height < 0.001:
                        return
                    leaves = obj.family_members_with_points()
                    visible = any(max(float(np.max(m.get_fill_opacity())),
                                      float(np.max(m.get_stroke_opacity()))) > 0.05
                                  for m in leaves)
                    if not visible:
                        return
                    labels.append({'text': getattr(obj, 'text', getattr(obj, 'tex_string', '?')),
                                   'box': [float(obj.get_left()[0]), float(obj.get_right()[0]),
                                           float(obj.get_bottom()[1]), float(obj.get_top()[1])]})
                    return
                for child in obj.submobjects:
                    walk(child)
            for obj in scene.mobjects:
                walk(obj)
            signature = json.dumps(labels, sort_keys=True)
            if signature in seen or not labels:
                return
            seen.add(signature)
            overlaps, outside = [], []
            for i, a in enumerate(labels):
                x1, x2, y1, y2 = a['box']
                if x1 < -6.62 or x2 > 6.62 or y1 < -3.55 or y2 > 3.55:
                    outside.append(i)
                for j, b in enumerate(labels[i+1:], i+1):
                    u1, u2, v1, v2 = b['box']
                    dx, dy = min(x2, u2)-max(x1, u1), min(y2, v2)-max(y1, v1)
                    if dx > 0.12 and dy > 0.08:
                        area = min((x2-x1)*(y2-y1), (u2-u1)*(v2-v1))
                        if area and dx*dy/area > 0.18:
                            overlaps.append([i, j])
            stack = [f for f in traceback.extract_stack() if Path(f.filename) == path]
            location = {'method': stack[-1].name, 'line': stack[-1].lineno} if stack else {}
            state = {'index': len(states), 'time': float(scene.renderer.time), **location,
                     'labels': labels, 'overlaps': overlaps, 'outside': outside}
            state['score'] = 4*len(outside) + 3*len(overlaps) + max(0, len(labels)-8)/5
            states.append(state)
            # Keep the eight highest-scoring distinct states; these are review candidates.
            if len(kept) < frame_limit or state['score'] > min(s['score'] for s in kept):
                if len(kept) >= frame_limit:
                    old = min(kept, key=lambda s: s['score'])
                    (output / old['frame']).unlink(missing_ok=True)
                    kept.remove(old)
                scene.camera.reset()
                scene.camera.capture_mobjects(scene.mobjects)
                state['frame'] = f"state_{state['index']:04d}.png"
                scene.camera.get_image().save(output / state['frame'])
                kept.append(state)
        finally:
            busy = False

    def play(scene, *args, **kwargs):
        result = original_play(scene, *args, **kwargs)
        inspect_state(scene)
        return result

    def wait(scene, *args, **kwargs):
        result = original_wait(scene, *args, **kwargs)
        inspect_state(scene)
        return result

    Scene.play, Scene.wait = play, wait
    result = source_inventory(entry)
    try:
        with tempconfig({'dry_run': True, 'skip_animations': True, 'pixel_width': 854,
                         'pixel_height': 480, 'frame_rate': 15, 'verbosity': 'ERROR',
                         'disable_caching': True, 'media_dir': str(output / '_media')}):
            scene = scene_type()
            scene.render()
        result['construction'] = 'passed'
    except Exception:
        result['construction'] = 'failed'
        result['error'] = traceback.format_exc()
    finally:
        Scene.play, Scene.wait = original_play, original_wait
    result.update(states=states, retained_frames=[s['index'] for s in kept],
                  visual_review='pending', audio_review='not_performed',
                  instrument_scope='stable play/wait endpoints, not in-between frames')
    (output / 'audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--entry', type=int)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ['MANIM_DISABLE_VOICEOVER'] = '1'
    targets = entries()
    if args.entry is not None:
        result = audit_one(targets[args.entry], output)
        return 0 if result['construction'] == 'passed' else 1
    summary = []
    for i, entry in enumerate(targets):
        key = f"{entry['track']}_{entry['order']:02d}"
        target = output / 'layout' / key
        target.mkdir(parents=True, exist_ok=True)
        with (target / 'construction.log').open('w') as log:
            process = subprocess.run([sys.executable, __file__, '--entry', str(i),
                                      '--output', str(target)], cwd=ROOT,
                                     stdout=log, stderr=subprocess.STDOUT, timeout=180)
        p = target / 'audit.json'
        result = json.loads(p.read_text()) if p.exists() else {'construction': 'failed'}
        states = result.pop('states', [])
        result.update(key=key, returncode=process.returncode, states=len(states),
                      overlap_candidates=sum(bool(s['overlaps']) for s in states),
                      outside_candidates=sum(bool(s['outside']) for s in states))
        summary.append(result)
        print(key, result['construction'], result['overlap_candidates'], result['outside_candidates'], flush=True)
    (output / 'layout_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    # This first pass reports candidates, not a false pass/fail visual verdict.
    return int(any(s['construction'] != 'passed' for s in summary))


if __name__ == '__main__':
    raise SystemExit(main())
