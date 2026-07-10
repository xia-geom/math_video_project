from pathlib import Path

from tools.video_audit.agents import finding
from tools.video_audit.batch import (
    BatchSceneResult,
    SceneEntry,
    count_findings,
    filter_registry,
    load_ci_scene_registry,
    render_index,
)


def test_load_ci_scene_registry_reads_render_matrix(tmp_path: Path) -> None:
    workflow = tmp_path / "smoke.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(
        """
jobs:
  render:
    strategy:
      matrix:
        include:
          - file: scenes/a/a_scene.py
            class: AScene
          - file: scenes/b/b_scene.py
            class: BScene
""",
        encoding="utf-8",
    )

    entries = load_ci_scene_registry(tmp_path, workflow)

    assert entries == [
        SceneEntry(Path("scenes/a/a_scene.py"), "AScene"),
        SceneEntry(Path("scenes/b/b_scene.py"), "BScene"),
    ]


def test_filter_registry_by_scene_class() -> None:
    entries = [SceneEntry(Path("a.py"), "A"), SceneEntry(Path("b.py"), "B")]

    assert filter_registry(entries, "B") == [SceneEntry(Path("b.py"), "B")]
    assert filter_registry(entries, None) == entries


def test_count_findings_by_severity() -> None:
    findings = [
        finding("A", "blocker", "input", "Bad", "Detail", "Fix"),
        finding("A", "warning", "visual", "Warn", "Detail", "Fix"),
        finding("A", "warning", "audio", "Warn2", "Detail", "Fix"),
    ]

    counts = count_findings(findings)

    assert counts["blocker"] == 1
    assert counts["warning"] == 2
    assert counts["polish"] == 0


def test_render_index_lists_failures_and_links(tmp_path: Path) -> None:
    out_dir = tmp_path / "reports"
    out_dir.mkdir()
    report = out_dir / "AScene_audit.md"
    report.write_text("# report", encoding="utf-8")
    result = BatchSceneResult(
        entry=SceneEntry(Path("scenes/a.py"), "AScene"),
        video_path=tmp_path / "dist" / "AScene" / "AScene.mp4",
        report_path=report,
        render_status="failed",
        audit_status="skipped",
        counts={"blocker": 0, "warning": 0, "polish": 0, "info": 0},
        error="Render exploded",
    )

    markdown = render_index(project_root=tmp_path, out_dir=out_dir, results=[result])

    assert "Render failures: 1" in markdown
    assert "`AScene`" in markdown
    assert "Render exploded" in markdown
    assert "[open](AScene_audit.md)" in markdown
