#!/usr/bin/env python3
"""Construire les PDF MAT0339 sans modifier les sources ni les autres projets."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITION = '2026-09-05'
TARGETS = {
    'manual': ('manual', 'main.tex', 'MAT0339_manuel_2026-09-05'),
    'student': ('workbook', 'main.tex', 'MAT0339_cahier_etudiant_2026-09-05'),
    'answers': ('workbook', 'answers.tex', 'MAT0339_cahier_reponses_2026-09-05'),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes() -> dict[str, str]:
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted((ROOT / 'sources').rglob('*.tex'))}


def build(target: str) -> dict:
    area, entry, name = TARGETS[target]
    out = ROOT / 'build' / target
    out.mkdir(parents=True, exist_ok=True)
    (ROOT / 'dist').mkdir(exist_ok=True)
    env = dict(os.environ, SOURCE_DATE_EPOCH='1788566400', FORCE_SOURCE_DATE='1', TZ='UTC')
    command = ['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error',
               '-file-line-error', '-pdflatex=pdflatex -no-shell-escape %O %S',
               f'-outdir={out}', f'-jobname={name}', entry]
    result = subprocess.run(command, cwd=ROOT / 'sources' / area, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
    (out / 'build-output.txt').write_text(result.stdout, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(f'{target}: compilation échouée. Voir {out / "build-output.txt"}\n'
                           + result.stdout[-4500:])
    log = (out / (name + '.log')).read_text(errors='replace')
    if re.search(r'undefined references|Reference .* undefined|multiply defined|^!', log, re.M):
        raise RuntimeError(f'{target}: références non résolues ou erreur LaTeX; voir le journal.')
    pdf = out / (name + '.pdf')
    info = subprocess.run(['pdfinfo', str(pdf)], check=True, capture_output=True, text=True).stdout
    pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    tagged = re.search(r'^Tagged:\s+(\S+)', info, re.M).group(1)
    boxes = re.findall(r'Overfull \\hbox \(([^)]+)\).*', log)
    dest = ROOT / 'dist' / pdf.name
    shutil.copy2(pdf, dest)
    print(f'{target}: {pages} pages; {len(boxes)} avertissements de débordement; {dest}')
    return {'target': target, 'file': dest.name, 'sha256': digest(dest), 'bytes': dest.stat().st_size,
            'pages': pages, 'tagged': tagged, 'overfull_hboxes': boxes,
            'command': command, 'latex_engine': subprocess.run(['pdflatex', '--version'],
            check=True, capture_output=True, text=True).stdout.splitlines()[0]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('target', choices=['all', *TARGETS], nargs='?', default='all')
    parser.add_argument('--release', action='store_true', help='Créer un instantané daté, sans écraser un existant.')
    args = parser.parse_args()
    for cmd in ['latexmk', 'pdflatex', 'pdfinfo']:
        if not shutil.which(cmd):
            parser.error(f'Commande manquante : {cmd}. Voir README.md.')
    subprocess.run(['python3', str(ROOT / 'scripts' / 'verify.py')], check=True)
    chosen = list(TARGETS) if args.target == 'all' else [args.target]
    if args.release and args.target != 'all':
        parser.error('--release exige la cible all afin de synchroniser les trois PDF.')
    report = {'edition': EDITION, 'source_hashes': source_hashes(), 'outputs': [build(t) for t in chosen],
              'scope': 'Build and source checks; not exhaustive mathematical or PDF/UA certification.'}
    (ROOT / 'build' / 'build-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    if args.release:
        dest = ROOT / 'releases' / EDITION
        dest.mkdir(parents=True, exist_ok=True)
        for item in report['outputs']:
            path = dest / item['file']
            if path.exists():
                raise RuntimeError(f'Instantané existant : {path}. Créer une nouvelle édition au lieu de l’écraser.')
        for item in report['outputs']:
            shutil.copy2(ROOT / 'dist' / item['file'], dest / item['file'])
        (dest / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print('Instantané créé :', dest)


if __name__ == '__main__':
    main()
