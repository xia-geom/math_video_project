from __future__ import annotations

import importlib.util
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import tools.tts as tts

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_curriculum.py"
SPEC = importlib.util.spec_from_file_location("render_curriculum", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
render_curriculum = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = render_curriculum
SPEC.loader.exec_module(render_curriculum)


def test_manifest_has_complete_tracks() -> None:
    _, entries = render_curriculum.read_manifest(
        ROOT / "curriculum" / "nouveau_programme_fr.yaml"
    )

    core = [entry for entry in entries if entry.track == "core"]
    supplements = [entry for entry in entries if entry.track == "supplement"]

    assert [entry.order for entry in core] == list(range(1, 25))
    assert [entry.order for entry in supplements] == list(range(1, 10))


def test_curriculum_delivery_names_are_unique() -> None:
    _, entries = render_curriculum.read_manifest(
        ROOT / "curriculum" / "nouveau_programme_fr.yaml"
    )

    keys = [(entry.track, entry.delivery_name) for entry in entries]
    assert len(keys) == len(set(keys))


def test_new_lessons_fill_positions_15_through_23() -> None:
    _, entries = render_curriculum.read_manifest(
        ROOT / "curriculum" / "nouveau_programme_fr.yaml"
    )
    selected = render_curriculum.select_entries(
        entries,
        track="core",
        orders=set(range(15, 24)),
    )

    assert len(selected) == 9
    assert selected[0].scene_class == "PrincipeFondamentalDenombrementFR"
    assert selected[-1].scene_class == "DeterminantEtMatriceInverseFR"


def test_new_scene_narration_is_well_formed_ssml() -> None:
    _, entries = render_curriculum.read_manifest(
        ROOT / "curriculum" / "nouveau_programme_fr.yaml"
    )
    new_entries = render_curriculum.select_entries(
        entries,
        track="core",
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
