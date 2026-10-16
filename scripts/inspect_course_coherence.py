#!/usr/bin/env python3
"""Extract encoded card/body samples and a local review index; never publish."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import html
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.course_review import input_hashes, sha256  # noqa: E402
from tools.course_catalog import load_catalog  # noqa: E402


def inspect(folder, entry, sample_set):
    from PIL import Image, ImageDraw

    status = json.loads((folder / 'STATUS.json').read_text())
    if status['render'] != 'passed':
        return
    video = ROOT / status['video_path']
    if sha256(video) != status['video_sha256'] or input_hashes(entry) != status['input_sha256']:
        raise ValueError(f'Stale render: {folder}')
    cards = json.loads((folder / 'cards.json').read_text())
    states = json.loads((folder / 'checkpoints.json').read_text())
    duration = status['duration']
    # Reviewed frame IDs must remain immutable when sampling policies change.
    # Legacy frames directly under the lesson directory are left untouched.
    output = folder / 'sample_sets' / sample_set
    if output.exists():
        raise ValueError(f'Preserve existing samples; choose a new --sample-set: {output}')
    output.mkdir(parents=True)
    selected = {}
    for event in cards:
        selected[round(event['visible_from'] + .7, 3)] = event['kind'] + ' readable'
        selected[round(event['speech_end'] - .09, 3)] = event['kind'] + ' hold end'
    unique = {}
    hold_lengths = {}
    previous = None
    for state in states:
        prior, previous = previous, state
        if any(event['start'] <= state['time'] <= event['end'] for event in cards):
            continue
        key = tuple(label['text'] for label in state['labels'])
        # Prefer completed reading holds over headings alone or the last
        # instant of a fade. Two matching endpoints delimit a stable hold.
        gap = state['time'] - prior['time'] if prior else 0
        if (len(key) >= 2 and prior and gap >= .5
                and key == tuple(label['text'] for label in prior['labels'])
                and gap > hold_lengths.get(key, 0)):
            unique[key] = state
            hold_lengths[key] = gap
    body = sorted(unique.values(), key=lambda state: state['time'])
    if not body:
        body = [state for state in states if len(state['labels']) >= 2
                and not any(event['start'] <= state['time'] <= event['end'] for event in cards)]
    for index in sorted({round(i * (len(body) - 1) / 11) for i in range(12)} if body else []):
        selected[round(max(0, body[index]['time'] - .09), 3)] = 'body sample'
    candidates = sorted(states, key=lambda s: sum(x['outside_frame'] for x in s['labels']), reverse=True)
    for state in candidates[:4]:
        if any(x['outside_frame'] for x in state['labels']):
            selected[round(max(0, state['time'] - .09), 3)] = 'clipping candidate'
    selected[round(duration - .09, 3)] = 'last frame'
    frames = output / 'frames'
    frames.mkdir(exist_ok=True)
    index = [{'time': time, 'kind': kind, 'file': f'frame_{i:03d}.png'}
             for i, (time, kind) in enumerate(sorted(selected.items())) if 0 <= time < duration]

    def extract(row):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(row['time']),
                        '-i', str(video), '-frames:v', '1', str(frames / row['file'])], check=True)

    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(extract, index))
    (output / 'frame_index.json').write_text(json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    # A first compact sheet makes all structural cards directly comparable.
    structural = [row for row in index if row['kind'].endswith('readable')]
    selections = [('cards', structural), ('body', [r for r in index if 'sample' in r['kind'] or 'candidate' in r['kind']])]
    for name, rows in selections:
        for start in range(0, len(rows), 12):
            page = rows[start:start + 12]
            sheet = Image.new('RGB', (1281, 270 * ((len(page) + 2) // 3)), '#dddddd')
            draw = ImageDraw.Draw(sheet)
            for position, row in enumerate(page):
                x, y = position % 3 * 427, position // 3 * 270
                with Image.open(frames / row['file']) as source:
                    sheet.paste(source.convert('RGB').resize((427, 240)), (x, y + 30))
                draw.text((x + 7, y + 8), f"{entry['order']:02d} | {row['time']:.2f}s | {row['kind']}", fill='black')
            sheet.save(output / f'{name}_{start // 12:02d}.png')
    review = {'lesson_id': entry['lesson_id'], 'video_sha256': status['video_sha256'],
              'sampled_frames': len(index), 'structural_cards': len(structural),
              'sample_policy': 'all fully visible structural cards; stratified stable body holds and clipping candidates',
              'sample_set': sample_set, 'extractor_sha256': sha256(Path(__file__)),
              'visual_inspection': 'pending', 'full_motion': 'not_checked', 'listening': 'not_performed'}
    (output / 'sample-review.json').write_text(json.dumps(review, ensure_ascii=False, indent=2) + '\n')
    print(f"{entry['order']:02d}: {len(index)} encoded samples in {output}", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--order', type=int, action='append')
    parser.add_argument('--sample-set', default='review_v1',
                        help='New immutable extraction-set name; never overwrites earlier samples.')
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_relative_to(ROOT / 'review_artifacts'):
        parser.error('Review outputs must be under this repository’s review_artifacts directory.')
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}', args.sample_set):
        parser.error('--sample-set must be a short alphanumeric name with underscores or hyphens.')
    entries = load_catalog()[1]
    rows = []
    for entry in entries:
        folder = root / f"{entry['order']:02d}"
        if not (folder / 'STATUS.json').exists():
            continue
        if not args.order or entry['order'] in args.order:
            inspect(folder, entry, args.sample_set)
        state = json.loads((folder / 'STATUS.json').read_text())
        video = f"{entry['order']:02d}/{entry['lesson_id']}_silent.mp4"
        title = html.escape(f"{entry['order']:02d} — {entry['title']}")
        content = (f'<video controls preload="none" src="{video}"></video>'
                   if state['render'] == 'passed' else '<p>Render needs correction.</p>')
        rows.append(f'<article><h2>{title}</h2>{content}</article>')
    root.mkdir(parents=True, exist_ok=True)
    (root / 'index.html').write_text(
        '<!doctype html><html lang="fr"><meta charset="utf-8"><title>Revue silencieuse du cours</title>'
        '<style>body{max-width:1100px;margin:32px auto;font:18px system-ui;color:#111;background:#fff}'
        'article{margin:40px 0}video{width:100%;max-width:854px}h2{font-size:23px}</style>'
        '<h1>Revue silencieuse du cours</h1><p>Prévisualisations sans Azure. '
        'Les contrôles d’images ne remplacent pas une lecture continue ou une écoute.</p>'
        + ''.join(rows) + '</html>', encoding='utf-8')


if __name__ == '__main__':
    main()
