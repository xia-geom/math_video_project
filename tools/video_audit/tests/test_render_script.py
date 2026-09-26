"""Exercise real catalogue routing with a fake renderer and no cloud services."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ARTIFACT = "10_composition_de_fonctions"
SCENE_FILE = (
    "scenes/fonctions_et_graphiques_fr/10_composition_de_fonctions_fr/"
    "10_composition_de_fonctions_fr_scene.py"
)


@pytest.fixture
def render_project(tmp_path: Path) -> Path:
    project_root = Path(__file__).resolve().parents[3]
    for folder in ("scripts", "tools", "curriculum"):
        (tmp_path / folder).mkdir()
    for name in ("render.sh", "render_outputs.sh"):
        destination = tmp_path / "scripts" / name
        shutil.copy2(project_root / "scripts" / name, destination)
        destination.chmod(0o755)
    shutil.copy2(project_root / "tools/course_catalog.py", tmp_path / "tools/course_catalog.py")
    for name in ("programme_principal_fr.yaml", "numbering_migration.json"):
        shutil.copy2(project_root / "curriculum" / name, tmp_path / "curriculum" / name)
    # Catalogue validation needs every registered source, but no fonts or media.
    for source in (project_root / "scenes").rglob("*_scene.py"):
        target = tmp_path / source.relative_to(project_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    fake_python = tmp_path / ".venv/bin/python"
    fake_python.parent.mkdir(parents=True)
    fake_python.write_text(
        r'''#!/usr/bin/env bash
set -euo pipefail
case "$1" in
    */tools/course_catalog.py) exec "$REAL_PYTHON" "$@" ;;
    */scripts/archive_renders.py)
        printf '%s\n' "$@" >> archive_args.txt
        exit 0 ;;
esac
printf '%s\n' "$@" > manim_args.txt
[[ "${MOCK_NO_OUTPUT:-0}" == "1" ]] && exit 0
scene_file="$4"
scene_class="$5"
scene_stem="$(basename "$scene_file" .py)"
subdir="480p15"
[[ "$3" == "-qh" ]] && subdir="1080p60"
output_dir="media/videos/$scene_stem/$subdir"
mkdir -p "$output_dir"
printf 'fake-mp4' > "$output_dir/$scene_class.mp4"
printf '1\n00:00:00,000 --> 00:00:01,000\nTest\n' > "$output_dir/$scene_class.srt"
''', encoding="utf-8",
    )
    fake_python.chmod(0o755)
    return tmp_path


def invoke(root: Path, quality: str, *, no_output: bool = False) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.update(REAL_PYTHON=sys.executable, GOOGLE_DRIVE_VIDEO_DIR=str(root / "drive"),
               RENDER_PYTHON=str(root / ".venv/bin/python"), MOCK_NO_OUTPUT=str(int(no_output)))
    env.pop("RENDER_SKIP_DRIVE_COPY", None)
    return subprocess.run(
        [str(root / "scripts/render.sh"), SCENE_FILE, "CompositionFonctionsFR", quality],
        cwd=root, env=env, capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("quality", ["ql", "qh"])
def test_render_script_uses_global_delivery_name_and_preserves_preview_isolation(render_project, quality):
    root = render_project
    result = invoke(root, quality)
    assert result.returncode == 0, result.stdout + result.stderr
    folder = root / "dist" / ARTIFACT if quality == "qh" else root / "dist/_previews/ql" / ARTIFACT
    stem = ARTIFACT if quality == "qh" else ARTIFACT + "__ql"
    assert (folder / f"{stem}.mp4").read_bytes() == b"fake-mp4"
    assert (folder / f"{stem}.srt").is_file()
    target = root / "drive/1 - Programme principal/02 - Fonctions et graphiques" / f"{ARTIFACT}.mp4"
    if quality == "qh":
        assert target.read_bytes() == b"fake-mp4"
        assert (root / "archive_args.txt").exists()
    else:
        assert not list((root / "drive").rglob("*.mp4"))
        assert not (root / "dist" / ARTIFACT / f"{ARTIFACT}.mp4").exists()
    assert not list((root / "drive").rglob("*.srt"))
    args = (root / "manim_args.txt").read_text().splitlines()
    assert "CompositionFonctionsFR" in args and SCENE_FILE in args


def test_missing_fresh_render_cannot_pass_by_reusing_an_old_master(render_project):
    root = render_project
    old_master = root / "dist" / ARTIFACT / f"{ARTIFACT}.mp4"
    old_master.parent.mkdir(parents=True)
    old_master.write_bytes(b"previous-master")
    result = invoke(root, "qh", no_output=True)
    assert result.returncode != 0
    assert "no fresh MP4" in result.stderr
    assert old_master.read_bytes() == b"previous-master"
    assert not list((root / "drive").rglob("*.mp4"))
    assert not (root / "archive_args.txt").exists()
