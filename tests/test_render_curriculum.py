from __future__ import annotations

import importlib.util
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import tools.tts as tts

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_curriculum.py"
MANIFEST = ROOT / "curriculum" / "programme_principal_fr.yaml"
SPEC = importlib.util.spec_from_file_location("render_curriculum", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
render_curriculum = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = render_curriculum
SPEC.loader.exec_module(render_curriculum)


def test_manifest_has_complete_tracks() -> None:
    _, entries = render_curriculum.read_manifest(MANIFEST)

    programme = [entry for entry in entries if entry.track == "programme"]
    errors = [entry for entry in entries if entry.track == "errors"]

    assert [entry.order for entry in programme] == list(range(1, 28))
    assert [entry.order for entry in errors] == list(range(1, 7))
    assert [entry.module for entry in programme[-3:]] == [
        "08 - Géométrie",
        "08 - Géométrie",
        "09 - Notations",
    ]


def test_curriculum_delivery_names_are_unique() -> None:
    _, entries = render_curriculum.read_manifest(MANIFEST)

    keys = [(entry.track, entry.delivery_name) for entry in entries]
    assert len(keys) == len(set(keys))


def test_preview_and_production_media_paths_are_distinct() -> None:
    _, entries = render_curriculum.read_manifest(MANIFEST)
    entry = entries[0]

    assert entry.rendered_video("qh") == entry.source_video
    assert entry.rendered_video("ql") == (
        ROOT
        / "dist"
        / "_previews"
        / "ql"
        / entry.artifact_slug
        / f"{entry.artifact_slug}__ql.mp4"
    )
    assert entry.rendered_subtitle("ql") == entry.rendered_video("ql").with_suffix(
        ".srt"
    )


def test_new_lessons_fill_positions_15_through_23() -> None:
    _, entries = render_curriculum.read_manifest(MANIFEST)
    selected = render_curriculum.select_entries(
        entries,
        track="programme",
        orders=set(range(15, 24)),
    )

    assert len(selected) == 9
    assert selected[0].scene_class == "PrincipeFondamentalDenombrementFR"
    assert selected[-1].scene_class == "DeterminantEtMatriceInverseFR"


def test_new_scene_narration_is_well_formed_ssml() -> None:
    _, entries = render_curriculum.read_manifest(MANIFEST)
    new_entries = render_curriculum.select_entries(
        entries,
        track="programme",
        orders=set(range(15, 24)),
    )

    checked_scenes = 0
    for entry in new_entries:
        source = ROOT / entry.scene_file
        spec = importlib.util.spec_from_file_location(f"scene_{entry.order}", source)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        container = getattr(module, "SCRIPT_SEGMENTS", getattr(module, "SCRIPT", None))
        if container is None:
            continue
        checked_scenes += 1
        segments = container.values() if isinstance(container, dict) else container
        for segment in segments:
            if isinstance(segment, dict):
                caption = segment.get("caption", "")
                assert "<" not in caption and ">" not in caption
                spoken = segment.get("ssml", "")
            else:
                spoken = segment
            document = spoken if spoken.lstrip().startswith("<lang") else tts.ssml(spoken)
            root = ET.fromstring(document)
            bookmarks = [
                node.attrib["mark"]
                for node in root.iter("bookmark")
                if "mark" in node.attrib
            ]
            assert len(bookmarks) == len(set(bookmarks))
    assert checked_scenes == 7


def test_mp4_drive_mirror_omits_non_video_files(tmp_path: Path) -> None:
    package = tmp_path / "package"
    module = package / "01 - Module"
    module.mkdir(parents=True)
    (module / "lesson.mp4").write_bytes(b"video")
    (module / "lesson.srt").write_text("subtitle", encoding="utf-8")
    (package / "INDEX.md").write_text("index", encoding="utf-8")

    destination = tmp_path / "drive" / "1 - Programme principal"
    destination.mkdir(parents=True)
    (destination / "Icon").write_text("icon", encoding="utf-8")
    (destination / ".DS_Store").write_bytes(b"metadata")

    render_curriculum.mirror_mp4_collection(package, destination)

    files = [
        path.relative_to(destination)
        for path in destination.rglob("*")
        if path.is_file()
    ]
    assert files == [Path("01 - Module/lesson.mp4")]


def test_render_output_routing_skips_unclassified_scenes() -> None:
    helper = ROOT / "scripts" / "render_outputs.sh"
    command = 'source "$1"; resolve_google_drive_video_theme_dir "$2"'

    known = subprocess.run(
        [
            "bash",
            "-c",
            command,
            "bash",
            str(helper),
            "scenes/vecteurs_fr/example/example_scene.py",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert known.stdout.strip().endswith("1 - Programme principal/05 - Vecteurs")

    unknown = subprocess.run(
        ["bash", "-c", command, "bash", str(helper), "experiments/example_scene.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert unknown.returncode != 0
    assert unknown.stdout == ""


def test_archive_mp4_tree_registers_each_video(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(render_curriculum, "PROJECT_ROOT", tmp_path)
    package = tmp_path / "dist" / "package"
    (package / "module").mkdir(parents=True)
    first = package / "first.mp4"
    second = package / "module" / "second.mp4"
    first.write_bytes(b"first")
    second.write_bytes(b"second")
    calls: list[list[str]] = []

    def fake_run(command, **_kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(render_curriculum.subprocess, "run", fake_run)
    render_curriculum.archive_mp4_tree(package)

    assert [Path(command[3]) for command in calls] == [first, second]
    assert all(command[2] == "register" for command in calls)
