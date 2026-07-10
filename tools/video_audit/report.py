from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path

from tools.video_audit.agents import AuditContext, Finding, relpath


def render_report(context: AuditContext, findings: list[Finding]) -> str:
    sorted_findings = sorted(findings, key=lambda item: item.sort_key())
    counts = Counter(item.severity for item in sorted_findings)
    rel_scene = relpath(context.scene_path, context.project_root)
    rel_video = relpath(context.video_path, context.project_root)
    rel_artifacts = relpath(context.artifacts_dir, context.project_root)

    lines = [
        f"# Video Audit: {context.scene_class}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Executive Summary",
        "",
        f"- Scene: `{rel_scene}`",
        f"- Video: `{rel_video}`",
        f"- Frame artifacts: `{rel_artifacts}`",
        f"- Silent preview mode: `{context.silent_preview}`",
        f"- Findings: {counts['blocker']} blocker, {counts['warning']} warning, {counts['polish']} polish, {counts['info']} info.",
        "",
    ]

    if not sorted_findings:
        lines.extend(["No findings were produced.", ""])
    else:
        for severity, title in [
            ("blocker", "Blocking Issues"),
            ("warning", "Warnings"),
            ("polish", "Polish Items"),
            ("info", "Informational Notes"),
        ]:
            subset = [item for item in sorted_findings if item.severity == severity]
            lines.extend(_render_section(title, subset))

    lines.extend(
        [
            "## Recommended Commands",
            "",
            "```bash",
            f"./.venv/bin/python -m py_compile {rel_scene}",
            f"MANIM_DISABLE_VOICEOVER=1 ./scripts/render.sh {rel_scene} {context.scene_class} ql",
            f"./.venv/bin/python scripts/audit_video.py --scene {rel_scene} --class {context.scene_class} --video {rel_video} --out {relpath(context.out_path, context.project_root)} --silent-preview",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(context: AuditContext, findings: list[Finding]) -> Path:
    context.out_path.parent.mkdir(parents=True, exist_ok=True)
    context.out_path.write_text(render_report(context, findings), encoding="utf-8")
    return context.out_path


def _render_section(title: str, findings: list[Finding]) -> list[str]:
    lines = [f"## {title}", ""]
    if not findings:
        lines.extend(["None.", ""])
        return lines

    for idx, item in enumerate(findings, start=1):
        lines.append(f"{idx}. **[{item.agent}] {item.title}**")
        lines.append(f"   - Category: `{item.category}`")
        if item.location:
            lines.append(f"   - Location: `{item.location}`")
        if item.timestamp:
            lines.append(f"   - Timestamp: `{item.timestamp}`")
        lines.append(f"   - Detail: {item.detail}")
        lines.append(f"   - Fix: {item.fix}")
        lines.append("")
    return lines
