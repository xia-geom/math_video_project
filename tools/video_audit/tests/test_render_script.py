from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def test_render_script_uses_slug_for_artifacts_and_class_for_manim(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[3]
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    for name in ("render.sh", "render_outputs.sh"):
        destination = scripts_dir / name
        shutil.copy2(project_root / "scripts" / name, destination)
        destination.chmod(0o755)

    scene = (
        tmp_path
        / "scenes"
        / "fonctions_et_graphiques_fr"
        / "09_composition_de_fonctions_fr"
        / "09_composition_de_fonctions_fr_scene.py"
    )
    scene.parent.mkdir(parents=True)
    scene.write_text("class CompositionFonctionsFR: pass\n", encoding="utf-8")

    fake_python = tmp_path / ".venv" / "bin" / "python"
    fake_python.parent.mkdir(parents=True)
    fake_python.write_text(
        """#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$@" > manim_args.txt
scene_file="$4"
scene_class="$5"
scene_stem="$(basename "$scene_file" .py)"
output_dir="media/videos/$scene_stem/480p15"
mkdir -p "$output_dir"
printf 'fake-mp4' > "$output_dir/$scene_class.mp4"
printf '1\\n00:00:00,000 --> 00:00:01,000\\nTest\\n' > "$output_dir/$scene_class.srt"
""",
        encoding="utf-8",
    )
    fake_python.chmod(0o755)

    drive_root = tmp_path / "drive"
    env = os.environ.copy()
    env["GOOGLE_DRIVE_VIDEO_DIR"] = str(drive_root)
    result = subprocess.run(
        [
            str(scripts_dir / "render.sh"),
            str(scene.relative_to(tmp_path)),
            "CompositionFonctionsFR",
            "ql",
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    artifact = "09_composition_de_fonctions_fr"
    assert (tmp_path / "dist" / artifact / f"{artifact}.mp4").read_bytes() == b"fake-mp4"
    assert (tmp_path / "dist" / artifact / f"{artifact}.srt").exists()
    assert (
        drive_root
        / "Nouveau programme"
        / "1 - Programme principal"
        / "02 - Fonctions et graphiques"
        / f"{artifact}.mp4"
    ).read_bytes() == b"fake-mp4"

    manim_args = (tmp_path / "manim_args.txt").read_text(encoding="utf-8").splitlines()
    assert "CompositionFonctionsFR" in manim_args
    assert str(scene.relative_to(tmp_path)) in manim_args
