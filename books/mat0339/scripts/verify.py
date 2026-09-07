#!/usr/bin/env python3
"""Contrôler les sources, les archives, les renvois et les exemples corrigés."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    baseline = json.loads((ROOT / 'docs/baseline.json').read_text())
    for src in baseline['sources']:
        p = ROOT / 'originals/2026-08' / (src['kind'] + '.tex')
        assert hashlib.sha256(p.read_bytes()).hexdigest() == src['sha256'], f'Archive modifiée : {p}'
    indexes = {}
    for area in ['manual', 'workbook']:
        paths = sorted((ROOT / 'sources' / area / 'chapters').glob('ch*.tex'))
        assert len(paths) == 17, (area, '17 chapitres requis')
        entry = (ROOT / 'sources' / area / 'main.tex').read_text()
        assert len(re.findall(r'\\part\{', entry)) == 5, (area, '5 parties requises')
        assert len(re.findall(r'\\input\{chapters/', entry)) == 17
        text = '\n'.join(p.read_text() for p in paths)
        labels = re.findall(r'\\label\{([^}]+)\}', text)
        assert len(labels) == len(set(labels)), (area, 'étiquette dupliquée')
        for ref in re.findall(r'\\(?:ref|pageref)\{([^}]+)\}', text):
            assert ref in labels, f'Renvoi non défini : {ref}'
        original = json.loads((ROOT / f'docs/{area}_section_index.json').read_text())
        current = re.findall(rf'\\label\{{{area}:section:([^}}]+)\}}', text)
        assert current == [f'{i["chapter"]:02}.{i["section"]:02}' for i in original]
        indexes[area] = [i['id'] for i in original]
        if area == 'workbook':
            base_text = (ROOT / 'originals/2026-08/workbook.tex').read_text()
            assert text.count('\\begin{exerciseblock}') == base_text.count('\\begin{exerciseblock}')
            assert text.count('\\begin{synthesisbox}') == base_text.count('\\begin{synthesisbox}')
    assert indexes['manual'] == indexes['workbook'], 'Numérotation manuel/cahier incohérente'
    for p in (ROOT / 'sources').rglob('*.tex'):
        text = p.read_text()
        assert not re.search(r'^orm\{', text, re.M), f'Commande norm endommagée : {p}'
        assert '\x00' not in text
        # All sources are self-contained in this directory; shell escape is never needed.
        assert not re.search(r'\\(?:write18|immediate\s*\\write18)\b', text)
    tests = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'])
    if tests.returncode:
        raise SystemExit(tests.returncode)
    print(f'Archives SHA-256 intactes; 17 chapitres et {len(indexes["manual"])} sections alignées; renvois valides.')


if __name__ == '__main__':
    main()
