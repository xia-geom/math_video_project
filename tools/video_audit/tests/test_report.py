from pathlib import Path

from tools.video_audit.agents import AuditContext, finding
from tools.video_audit.report import render_report


def test_report_groups_findings_by_severity(tmp_path: Path) -> None:
    context = AuditContext(
        project_root=tmp_path,
        scene_path=tmp_path / "scene.py",
        scene_class="DemoScene",
        video_path=tmp_path / "dist" / "DemoScene" / "DemoScene.mp4",
        out_path=tmp_path / "reports" / "DemoScene_audit.md",
        artifacts_dir=tmp_path / "reports" / "DemoScene_audit_frames",
        silent_preview=True,
    )
    findings = [
        finding("AgentB", "polish", "visual", "Polish item", "Detail", "Fix"),
        finding("AgentA", "blocker", "input", "Blocker item", "Detail", "Fix"),
        finding("AgentC", "warning", "audio", "Warning item", "Detail", "Fix"),
    ]

    report = render_report(context, findings)

    assert "1 blocker, 1 warning, 1 polish" in report
    assert report.index("## Blocking Issues") < report.index("## Warnings")
    assert "Blocker item" in report
    assert "Warning item" in report
    assert "Polish item" in report
