#!/usr/bin/env python3
"""Compiler les examens révisés localement, sans créer de release."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
EDITION = "2026-10-10"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compile_one(item: dict, source: Path, build_dir: Path, dist_dir: Path) -> dict:
    name = item["name"]
    folder = f"serie_{item['series']}"
    filename = f"examen_{item['exam']}_{'corrige' if item['teacher'] else 'sujet'}.tex"
    src = source / "sources" / folder / filename
    out = build_dir / folder / name
    out.mkdir(parents=True, exist_ok=True)
    epoch = int(datetime.fromisoformat(EDITION).replace(tzinfo=timezone.utc).timestamp())
    env = dict(os.environ, SOURCE_DATE_EPOCH=str(epoch), FORCE_SOURCE_DATE="1", TZ="UTC")
    command = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error",
               "-file-line-error", "-pdflatex=pdflatex -no-shell-escape %O %S",
               f"-outdir={out}", f"-jobname={name}", src.name]
    result = subprocess.run(command, cwd=src.parent, env=env, capture_output=True,
                            text=True, encoding="utf-8", errors="replace")
    (out / "build-output.txt").write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Compilation échouée : {src}; voir {out / 'build-output.txt'}")
    log = (out / f"{name}.log").read_text(errors="replace")
    if re.search(r"undefined references|Reference .* undefined|multiply defined|^!", log, re.M):
        raise RuntimeError(f"Références ou erreurs LaTeX : {src}")
    pdf = out / f"{name}.pdf"
    info = subprocess.run(["pdfinfo", str(pdf)], check=True, capture_output=True, text=True).stdout
    pages = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
    if pages != 6:
        raise RuntimeError(f"{name}: {pages} pages, six attendues (une question par page)")
    warnings = re.findall(r"Overfull \\[hv]box.*", log)
    dest = dist_dir / folder / pdf.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf, dest)
    print(f"{name}: {pages} pages; {len(warnings)} débordements", flush=True)
    return {"file": dest.relative_to(dist_dir).as_posix(), "sha256": digest(dest),
            "pages": pages, "overfull_boxes": warnings, "command": command,
            "source": src.relative_to(ROOT).as_posix(), "source_sha256": digest(src)}


def merge(python: str, inputs: list[Path], dest: Path, series: str, teacher: bool) -> None:
    code = '''
import sys
from pypdf import PdfReader, PdfWriter
writer = PdfWriter()
for number, source in enumerate(sys.argv[4:], 1):
    reader = PdfReader(source)
    if len(reader.pages) != 6:
        raise ValueError("Expected six pages per examination")
    writer.append(reader, outline_item=f"Examen {number}")
writer.add_metadata({"/Title": sys.argv[2], "/Author": "Document de travail pédagogique",
                     "/Subject": "Révision du 10 octobre 2026; validation institutionnelle en attente"})
with open(sys.argv[1], "wb") as output:
    writer.write(output)
assert len(PdfReader(sys.argv[1]).pages) == 18
'''
    title = f"MAT0339 - Série {series} - Trois examens - {'corrigés' if teacher else 'sujets'}"
    subprocess.run([python, "-c", code, str(dest), title, EDITION,
                    *map(str, inputs)], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-python", default=sys.executable,
                        help="Python disposant de pypdf (par exemple le runtime documentaire fourni).")
    parser.add_argument("--jobs", type=int, choices=range(1, 5), default=2)
    args = parser.parse_args()
    for executable in ("latexmk", "pdflatex", "pdfinfo"):
        if not shutil.which(executable):
            parser.error(f"Commande manquante : {executable}")
    subprocess.run([args.pdf_python, "-c", "import pypdf"], check=True)
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"),
                    "-p", "test_exams_revision.py", "-v"], check=True)
    source = ROOT / "exams" / EDITION
    build_dir = ROOT / "build" / "exams" / EDITION
    dist_dir = ROOT / "dist" / "exams" / EDITION
    build_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((source / "examens_manifest.json").read_text())
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        outputs = list(pool.map(lambda item: compile_one(item, source, build_dir, dist_dir), manifest))
    for series in "ABC":
        for teacher in (False, True):
            suffix = "corrige" if teacher else "sujet"
            inputs = [dist_dir / f"serie_{series}/MAT0339_serie_{series}_examen_{n}_{suffix}.pdf"
                      for n in range(1, 4)]
            dest = dist_dir / f"MAT0339_serie_{series}_trois_examens_{'corriges' if teacher else 'sujets'}.pdf"
            merge(args.pdf_python, inputs, dest, series, teacher)
            outputs.append({"file": dest.name, "sha256": digest(dest), "pages": 18,
                            "inputs": [p.relative_to(dist_dir).as_posix() for p in inputs]})
    report = {"edition": EDITION, "status": "local-working-drafts", "outputs": outputs,
              "source_hashes": {p.relative_to(source).as_posix(): digest(p)
                                for p in sorted((source / "sources").rglob("*.tex"))},
              "latex_engine": subprocess.run(["pdflatex", "--version"], check=True,
                                              capture_output=True, text=True).stdout.splitlines()[0],
              "pypdf_version": subprocess.run([args.pdf_python, "-c", "import pypdf; print(pypdf.__version__)"],
                                               check=True, capture_output=True, text=True).stdout.strip(),
              "reproducibility": "Fixed source date, no shell escape; hashes depend on the recorded TeX/pypdf versions.",
              "scope": "Compilation and mathematical regression checks; visual evidence is recorded separately. No release or institutional approval."}
    (build_dir / "build-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    (dist_dir / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(f"18 PDF individuels et 6 recueils locaux : {dist_dir}")


if __name__ == "__main__":
    main()
