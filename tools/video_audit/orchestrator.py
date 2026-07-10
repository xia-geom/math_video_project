from __future__ import annotations

from pathlib import Path

from tools.video_audit.agents import (
    AgentResult,
    AuditAgent,
    AuditContext,
    AudioCaptionAgent,
    Finding,
    PedagogyAccessibilityAgent,
    RenderMetadataAgent,
    SourceScriptAgent,
    VisualFrameAgent,
    finding,
)
from tools.video_audit.media import ffprobe, has_ffmpeg
from tools.video_audit.report import write_report
from tools.video_audit.source import load_source


def default_agents() -> list[AuditAgent]:
    return [
        SourceScriptAgent(),
        RenderMetadataAgent(),
        VisualFrameAgent(),
        AudioCaptionAgent(),
        PedagogyAccessibilityAgent(),
    ]


def run_audit(
    *,
    project_root: Path,
    scene_path: Path,
    scene_class: str,
    video_path: Path,
    out_path: Path,
    silent_preview: bool = False,
    agents: list[AuditAgent] | None = None,
) -> tuple[AuditContext, list[Finding], Path]:
    project_root = project_root.resolve()
    scene_path = _resolve(project_root, scene_path)
    video_path = _resolve(project_root, video_path)
    out_path = _resolve(project_root, out_path)
    artifacts_dir = out_path.with_suffix("")
    artifacts_dir = artifacts_dir.parent / f"{artifacts_dir.name}_frames"

    context = AuditContext(
        project_root=project_root,
        scene_path=scene_path,
        scene_class=scene_class,
        video_path=video_path,
        out_path=out_path,
        artifacts_dir=artifacts_dir,
        silent_preview=silent_preview,
    )

    bootstrap_findings: list[Finding] = []
    if scene_path.exists():
        context.source = load_source(scene_path)
    else:
        bootstrap_findings.append(
            finding(
                "Orchestrator",
                "blocker",
                "input",
                "Scene file not found",
                f"`{scene_path}` does not exist.",
                "Pass a valid `--scene` path.",
                location=str(scene_path),
            )
        )

    if video_path.exists() and has_ffmpeg():
        try:
            context.media = ffprobe(video_path)
        except Exception as exc:
            bootstrap_findings.append(
                finding(
                    "Orchestrator",
                    "blocker",
                    "input",
                    "Video probe failed",
                    str(exc),
                    "Confirm ffprobe can read the MP4.",
                    location=str(video_path),
                )
            )
    elif not video_path.exists():
        bootstrap_findings.append(
            finding(
                "Orchestrator",
                "blocker",
                "input",
                "Video file not found",
                f"`{video_path}` does not exist.",
                "Render the scene or pass a valid `--video` path.",
                location=str(video_path),
            )
        )
    else:
        bootstrap_findings.append(
            finding(
                "Orchestrator",
                "blocker",
                "input",
                "ffmpeg/ffprobe unavailable",
                "The audit runner needs ffmpeg and ffprobe for media checks.",
                "Install ffmpeg and re-run the audit.",
            )
        )

    findings = list(bootstrap_findings)
    for agent in agents or default_agents():
        result: AgentResult = agent.run(context)
        findings.extend(result.findings)

    report_path = write_report(context, findings)
    return context, findings, report_path


def _resolve(root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return root / path
