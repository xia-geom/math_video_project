#!/usr/bin/env python3
"""Contrôler les sources, les archives, les renvois et les exemples corrigés."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from video_map import section_indexes

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    baseline = json.loads((ROOT / 'docs/baseline.json').read_text())
    for src in baseline['sources']:
        p = ROOT / 'originals/2026-08' / (src['kind'] + '.tex')
        assert hashlib.sha256(p.read_bytes()).hexdigest() == src['sha256'], f'Archive modifiée : {p}'
    indexes = section_indexes()
    for area in ['manual', 'workbook']:
        source = ROOT / 'sources' / area
        assert len(list((source / 'chapters').glob('ch*.tex'))) == 17, (area, '17 chapitres requis')
        assert [p.name for p in (source / 'appendices').glob('*.tex')] == ['circular_motion.tex']
        entry = (ROOT / 'sources' / area / 'main.tex').read_text()
        assert len(re.findall(r'\\part\{', entry)) == 5, (area, '5 parties requises')
        assert len(re.findall(r'\\input\{chapters/', entry)) == 17
        assert entry.count('\\appendix') == 1
        assert entry.index('\\appendix') < entry.index('\\input{appendices/circular_motion.tex}')
        paths = [source / name for name in re.findall(r'\\input\{((?:chapters|appendices)/[^}]+)\}', entry)]
        assert paths == [source / f'chapters/ch{n:02}.tex' for n in range(1, 18)] + [source / 'appendices/circular_motion.tex']
        text = '\n'.join(p.read_text() for p in paths)
        labels = re.findall(r'\\label\{([^}]+)\}', text)
        assert len(labels) == len(set(labels)), (area, 'étiquette dupliquée')
        for ref in re.findall(r'\\(?:ref|pageref)\{([^}]+)\}', text):
            assert ref in labels, f'Renvoi non défini : {ref}'
        rows = list(indexes[area].values())
        current = re.findall(rf'\\label\{{({area}:section:[^}}]+)\}}', text)
        assert current == [row['label'] for row in rows], (area, 'Ordre ou section non indexée')
        assert len(rows) == 134
        for chapter in list(range(1, 18)) + ['A']:
            chapter_rows = [row for row in rows if row['chapter'] == chapter]
            assert [row['section'] for row in chapter_rows] == list(range(1, len(chapter_rows)+1))
        for chapter, path in zip(list(range(1, 18)) + ['A'], paths):
            path_rows = [row for row in rows if ROOT / row['path'] == path]
            assert path_rows and all(row['chapter'] == chapter for row in path_rows)
            expected = [row['label'] for row in path_rows]
            actual = re.findall(rf'\\label\{{({area}:section:[^}}]+)\}}', path.read_text())
            assert expected == actual, (area, path, 'Chemin indexé incohérent')
        if area == 'workbook':
            base_text = (ROOT / 'originals/2026-08/workbook.tex').read_text()
            assert text.count('\\begin{exerciseblock}') == base_text.count('\\begin{exerciseblock}') + 8
            assert text.count('\\begin{synthesisbox}') == base_text.count('\\begin{synthesisbox}') + 1
    assert list(indexes['manual']) == list(indexes['workbook']), 'Identités manuel/cahier incohérentes'
    for section_id, row in indexes['manual'].items():
        other = indexes['workbook'][section_id]
        assert row.get('display', section_id) == other.get('display', section_id)
    for p in (ROOT / 'sources').rglob('*.tex'):
        text = p.read_text()
        assert not re.search(r'^orm\{', text, re.M), f'Commande norm endommagée : {p}'
        assert '\x00' not in text
        # All sources are self-contained in this directory; shell escape is never needed.
        assert not re.search(r'\\(?:write18|immediate\s*\\write18)\b', text)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'])
    if tests.returncode:
        raise SystemExit(tests.returncode)
    print(f'Archives SHA-256 intactes; 17 chapitres, 1 annexe et {len(indexes["manual"])} sections alignées; renvois valides.')


if __name__ == '__main__':
    main()
