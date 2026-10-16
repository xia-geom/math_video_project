#!/usr/bin/env python3
"""Générer la carte source et le répertoire LaTeX, sans compiler les livres."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def section_indexes(root: Path = ROOT) -> dict:
    """Validate stable section targets against the current book sources."""
    indexes = {}
    for area in ('manual', 'workbook'):
        rows = json.loads((root / f'docs/{area}_section_index.json').read_text())
        indexes[area] = {row['id']: row for row in rows}
        for row in rows:
            source = (root / row['path']).read_text()
            if f"\\label{{{row['label']}}}" not in source:
                raise ValueError(f"Section absente des sources : {row['label']}")
    return indexes


def validate_references(mapping: dict, entries: list[dict], indexes: dict) -> None:
    refs = mapping['catalogue_references']
    if set(refs) != {entry['lesson_id'] for entry in entries}:
        raise ValueError('Les renvois doivent couvrir exactement les identités du catalogue.')
    for lesson_id, reference in refs.items():
        if not reference.get('note', '').strip():
            raise ValueError(f'Préciser la portée du renvoi : {lesson_id}')
        for area in ('manual', 'workbook'):
            target = reference[area]
            sections, chapters = target['sections'], target['chapters']
            if len(sections) != len(set(sections)) or len(chapters) != len(set(chapters)):
                raise ValueError(f'Renvoi répété : {lesson_id}/{area}')
            if any(section not in indexes[area] for section in sections):
                raise ValueError(f'Section inconnue : {lesson_id}/{area}')
            if any(type(chapter) is not int or chapter not in range(1, 18) for chapter in chapters):
                raise ValueError(f'Chapitre inconnu : {lesson_id}/{area}')
            if set(chapters) & {indexes[area][section]['chapter'] for section in sections}:
                raise ValueError(f'Précision ambiguë chapitre/section : {lesson_id}/{area}')


def tex_escape(text: str) -> str:
    replacements = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%',
                    '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
                    '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
                    '²': r'\textsuperscript{2}', '³': r'\textsuperscript{3}',
                    '—': '-', '–': '-', '‑': '-'}
    return ''.join(replacements.get(char, char) for char in text)


def reference_text(reference: dict) -> str:
    labels = []
    if reference['sections']:
        prefix = r'\S\S\ ' if len(reference['sections']) > 1 else r'\S\ '
        labels.append(prefix + ', '.join(reference['sections']))
    if reference['chapters']:
        labels.append('Ch. ' + ', '.join(str(ch) for ch in reference['chapters']))
    return '; '.join(labels) if labels else 'Complément transversal'


def render_catalogue(mapping: dict, entries: list[dict], indexes: dict) -> str:
    """One standalone student document; course metadata stays in the catalogue."""
    validate_references(mapping, entries, indexes)
    rows = sorted(entries, key=lambda entry: entry['order'])
    edition = tex_escape(mapping['catalogue_review']['book_edition'])
    result = [r'''% Fichier généré : ne pas modifier à la main.
\documentclass[11pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[french]{babel}
\usepackage[margin=19mm]{geometry}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage[table]{xcolor}
\usepackage{array,longtable,booktabs}
\definecolor{ink}{HTML}{163F59}
\definecolor{soft}{HTML}{EFF4F7}
\renewcommand{\familydefault}{\sfdefault}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\tabcolsep}{6pt}
\renewcommand{\arraystretch}{1.18}
\pagestyle{plain}
\begin{document}
{\color{ink}\Huge\bfseries Revoir une notion}\par
{\Large Capsules vidéo et repères dans les livres}\par
''', f'\nManuel et cahier MAT0339 : édition du {edition}.\\par\n',
        r'''Après le cours, repérez la notion à revoir, puis revenez aux sections du
manuel et aux exercices du cahier. Le numéro à gauche identifie la vidéo.
\textbf{Les renvois du manuel et du cahier se lisent séparément.}

\S\ désigne une section; « Ch. » désigne un chapitre lorsque le rapprochement
est seulement thématique. Chaque vidéo soutient une partie des sections citées :
elle ne remplace ni leur étude complète ni la recherche des exercices.
Ce répertoire n'atteste pas que toutes les vidéos sont disponibles ou validées.
''']
    for track, title in [('programme', 'Notions du cours'), ('errors', 'Erreurs fréquentes')]:
        track_rows = [row for row in rows if row['track'] == track]
        if not track_rows:
            continue
        result.extend([f'\n\\section*{{{title}}}\n', r'''
\small
\begin{longtable}{@{}p{0.055\textwidth}p{0.525\textwidth}p{0.17\textwidth}p{0.17\textwidth}@{}}
\rowcolor{soft}\textbf{No} & \textbf{Vidéo et point de révision} & \textbf{Manuel} & \textbf{Cahier} \\
\midrule
\endfirsthead
\rowcolor{soft}\textbf{No} & \textbf{Vidéo et point de révision} & \textbf{Manuel} & \textbf{Cahier} \\
\midrule
\endhead
\midrule
\multicolumn{4}{r}{\footnotesize Suite à la page suivante}\\
\endfoot
\bottomrule
\endlastfoot
'''])
        for entry in track_rows:
            ref = mapping['catalogue_references'][entry['lesson_id']]
            title_tex, note_tex = tex_escape(entry['title']), tex_escape(ref['note'])
            result.append(
                f"{entry['order']:02d} & \\textbf{{{title_tex}}}\\newline "
                f"{{\\footnotesize {note_tex}}} & {reference_text(ref['manual'])} & "
                f"{reference_text(ref['workbook'])} \\\\\n\\addlinespace[7pt]\n")
        result.append('\\end{longtable}\n\\normalsize\n')
    result.append('\\end{document}\n')
    return '\n'.join(result)


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
    outputs = {
        'video-map.md': render(mapping, entries),
        'catalogue-videos.tex': render_catalogue(mapping, entries, section_indexes()),
    }
    for name, content in outputs.items():
        output = ROOT / 'curriculum' / name
        if args.write:
            output.write_text(content, encoding='utf-8')
        elif not output.is_file() or output.read_text(encoding='utf-8') != content:
            raise SystemExit(f'{name} périmé : exécuter video_map.py --write.')
    print(f'Carte des 17 chapitres et répertoire des {len(entries)} vidéos vérifiés.')


if __name__ == '__main__':
    main()
