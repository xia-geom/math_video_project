from __future__ import annotations

from pathlib import Path


def artifact_name_for_scene(scene_path: Path) -> str:
    """Return the repository topic-folder slug used for render artifacts."""
    return scene_path.parent.name


def canonical_video_path(project_root: Path, scene_path: Path) -> Path:
    artifact_name = artifact_name_for_scene(scene_path)
    return project_root / "dist" / artifact_name / f"{artifact_name}.mp4"
