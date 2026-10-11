#!/usr/bin/env python3
"""Générer ou contrôler les renvois vidéo, indépendamment de la compilation PDF."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def render(mapping: dict, entries: list[dict]) -> str:
    by_id = {entry['lesson_id']: entry for entry in entries}
    lines = ['# Correspondance du manuel avec les capsules', '',
             'Fichier généré par `python3 books/mat0339/scripts/video_map.py --write`.',
             'Les associations par chapitre sont dans `video-map.json`; les numéros, titres et chemins proviennent du catalogue unifié.', '',
             'Cette carte indique la présence de sources. Elle ne certifie ni une couverture complète du chapitre, ni un rendu ou une publication.', '',
             '| Chapitre | Sources associées | Limites |', '|---|---|---|']
    chapters = mapping['chapters']
    if [c['chapter'] for c in chapters] != list(range(1, 18)):
        raise ValueError('Les 17 chapitres doivent être présents dans leur ordre.')
    for chapter in chapters:
        ids = chapter['lesson_ids']
        if len(ids) != len(set(ids)):
            raise ValueError('Identifiant vidéo répété dans un chapitre.')
        lessons = sorted((by_id[i] for i in ids), key=lambda e: e['order'])
        links = '<br>'.join(f"[{e['order']:02d} - {e['title']}](../../../{e['scene_file']})" for e in lessons)
        lines.append(f"| {chapter['chapter']} - {chapter['title']} | {links or 'Aucune source associée'} | {chapter['note']} |")
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    sys.path.insert(0, str(REPO))
    from tools.course_catalog import load_catalog
    _, entries = load_catalog()
    mapping = json.loads((ROOT / 'curriculum/video-map.json').read_text())
    for ch in mapping['chapters']:
        for field in ['manual_file', 'workbook_file']:
            if not (ROOT / 'curriculum' / ch[field]).is_file():
                raise ValueError(f'Renvoi introuvable : {ch[field]}')
    content = render(mapping, entries)
    output = ROOT / 'curriculum/video-map.md'
    if args.write:
        output.write_text(content, encoding='utf-8')
    elif output.read_text(encoding='utf-8') != content:
        raise SystemExit('Carte périmée : exécuter video_map.py --write.')
    print('Correspondance de 17 chapitres vérifiée avec le catalogue unifié.')


if __name__ == '__main__':
    main()
