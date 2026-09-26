from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=4)
def _catalogue(root: Path, _mtime_ns: int):
    from tools.course_catalog import load_catalog
    return load_catalog(root / "curriculum/programme_principal_fr.yaml", root=root)[1]


def artifact_name_for_scene(scene_path: Path, project_root: Path | None = None) -> str:
    """Resolve the shared delivery identity, with a fallback only outside a catalogue."""
    from tools.course_catalog import ROOT, delivery_name, resolve_scene_path
    root = project_root or ROOT
    manifest = root / "curriculum/programme_principal_fr.yaml"
    if manifest.is_file():
        entries = _catalogue(root.resolve(), manifest.stat().st_mtime_ns)
        source = resolve_scene_path(str(scene_path), root=root)
        entry = next((e for e in entries if e["scene_file"] == source), None)
        if entry is not None:
            return delivery_name(entry)
    return scene_path.parent.name


def canonical_video_path(project_root: Path, scene_path: Path, quality: str = "qh") -> Path:
    name = artifact_name_for_scene(scene_path, project_root)
    if quality not in {"ql", "qm", "qh"}:
        raise ValueError("Unknown render quality")
    if quality == "qh":
        return project_root / "dist" / name / f"{name}.mp4"
    return project_root / "dist/_previews" / quality / name / f"{name}__{quality}.mp4"
