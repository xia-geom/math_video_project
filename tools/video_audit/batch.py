from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from tools.video_audit.agents import SEVERITY_ORDER, Finding, relpath
from tools.video_audit.orchestrator import run_audit
from tools.video_audit.paths import canonical_video_path


@dataclass(frozen=True)
class SceneEntry:
    scene_file: Path
    scene_class: str


@dataclass
class BatchSceneResult:
    entry: SceneEntry
    video_path: Path
    report_path: Path
    render_status: str
    audit_status: str
    counts: dict[str, int] = field(default_factory=dict)
    contact_sheet: Path | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.render_status == "rendered" and self.audit_status == "audited"


def load_ci_scene_registry(project_root: Path, workflow_path: Path | None = None) -> list[SceneEntry]:
    if workflow_path is None:
        from tools.course_catalog import load_catalog
        _, entries = load_catalog(project_root / "curriculum/programme_principal_fr.yaml", root=project_root)
        return [SceneEntry(Path(e["scene_file"]), e["scene_class"]) for e in entries]
    workflow = workflow_path
    data = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    includes = data["jobs"]["render"]["strategy"]["matrix"]["include"]
    return [SceneEntry(Path(item["file"]), item["class"]) for item in includes]


def filter_registry(entries: list[SceneEntry], scene_class: str | None) -> list[SceneEntry]:
    if scene_class is None:
        return entries
    return [entry for entry in entries if entry.scene_class == scene_class]


def run_batch_audit(
    *,
    project_root: Path,
    entries: list[SceneEntry],
    out_dir: Path,
    render: bool = True,
    render_timeout: int = 600,
    verbose: bool = False,
) -> list[BatchSceneResult]:
    out_dir = _resolve(project_root, out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    results: list[BatchSceneResult] = []

    total = len(entries)
    for index, entry in enumerate(entries, start=1):
        video_path = canonical_video_path(project_root, entry.scene_file, quality="ql" if render else "qh")
        report_path = out_dir / f"{entry.scene_class}_audit.md"

        render_status = "not_requested"
        error: str | None = None
        if render:
            if verbose:
                print(f"[{index}/{total}] Rendering {entry.scene_class}...", flush=True)
            render_status, error = render_scene(project_root, entry, timeout=render_timeout)
        elif video_path.exists():
            render_status = "existing"
        else:
            render_status = "missing"

        if render_status in {"rendered", "existing"} and video_path.exists():
            if verbose:
                print(f"[{index}/{total}] Auditing {entry.scene_class}...", flush=True)
            _, findings, _ = run_audit(
                project_root=project_root,
                scene_path=entry.scene_file,
                scene_class=entry.scene_class,
                video_path=video_path,
                out_path=report_path,
                silent_preview=True,
            )
            counts = count_findings(findings)
            audit_status = "audited"
            contact_sheet = report_path.with_suffix("")
            contact_sheet = contact_sheet.parent / f"{contact_sheet.name}_frames" / "contact_sheet.png"
            results.append(
                BatchSceneResult(
                    entry=entry,
                    video_path=video_path,
                    report_path=report_path,
                    render_status=render_status,
                    audit_status=audit_status,
                    counts=counts,
                    contact_sheet=contact_sheet if contact_sheet.exists() else None,
                    error=error,
                )
            )
        else:
            if verbose:
                print(f"[{index}/{total}] Skipping audit for {entry.scene_class}: {render_status}", flush=True)
            results.append(
                BatchSceneResult(
                    entry=entry,
                    video_path=video_path,
                    report_path=report_path,
                    render_status=render_status,
                    audit_status="skipped",
                    counts={severity: 0 for severity in SEVERITY_ORDER},
                    error=error or "No rendered MP4 available for audit.",
                )
            )

    write_index(project_root=project_root, out_dir=out_dir, results=results)
    return results


def render_scene(project_root: Path, entry: SceneEntry, timeout: int = 600) -> tuple[str, str | None]:
    env = os.environ.copy()
    env["MANIM_DISABLE_VOICEOVER"] = "1"
    for key in ("SPEECH_KEY", "SPEECH_REGION", "AZURE_SUBSCRIPTION_KEY", "AZURE_SERVICE_REGION"):
        env[key] = ""

    command = ["./scripts/render.sh", str(entry.scene_file), entry.scene_class, "ql"]
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output = ((exc.stdout or "") + "\n" + (exc.stderr or "")).strip()
        summary = _summarize_output(output) if output else f"Render exceeded {timeout} seconds."
        return "failed", summary
    if result.returncode == 0:
        return "rendered", None
    output = (result.stdout + "\n" + result.stderr).strip()
    return "failed", _summarize_output(output)


def count_findings(findings: list[Finding]) -> dict[str, int]:
    counts = {severity: 0 for severity in SEVERITY_ORDER}
    for item in findings:
        counts[item.severity] = counts.get(item.severity, 0) + 1
    return counts


def write_index(*, project_root: Path, out_dir: Path, results: list[BatchSceneResult]) -> Path:
    index_path = out_dir / "INDEX.md"
    index_path.write_text(render_index(project_root=project_root, out_dir=out_dir, results=results), encoding="utf-8")
    return index_path


def render_index(*, project_root: Path, out_dir: Path, results: list[BatchSceneResult]) -> str:
    total = len(results)
    rendered = sum(1 for result in results if result.render_status == "rendered")
    audited = sum(1 for result in results if result.audit_status == "audited")
    failed = sum(1 for result in results if result.render_status == "failed")
    blockers = sum(result.counts.get("blocker", 0) for result in results)
    warnings = sum(result.counts.get("warning", 0) for result in results)
    polish = sum(result.counts.get("polish", 0) for result in results)

    lines = [
        "# Production Scene Audit Index",
        "",
        "## Summary",
        "",
        f"- Scenes in scope: {total}",
        f"- Rendered this run: {rendered}",
        f"- Audited: {audited}",
        f"- Render failures: {failed}",
        f"- Findings: {blockers} blocker, {warnings} warning, {polish} polish",
        "",
        "## Scene Results",
        "",
        "| Scene | Render | Audit | Findings | Report | Contact Sheet |",
        "|---|---|---|---:|---|---|",
    ]

    for result in results:
        report = _link(result.report_path, out_dir) if result.report_path.exists() else "-"
        contact = _link(result.contact_sheet, out_dir) if result.contact_sheet else "-"
        counts = (
            f"B:{result.counts.get('blocker', 0)} "
            f"W:{result.counts.get('warning', 0)} "
            f"P:{result.counts.get('polish', 0)} "
            f"I:{result.counts.get('info', 0)}"
        )
        lines.append(
            f"| `{result.entry.scene_class}` | {result.render_status} | {result.audit_status} | {counts} | {report} | {contact} |"
        )

    failures = [result for result in results if result.error]
    if failures:
        lines.extend(["", "## Render Or Audit Failures", ""])
        for result in failures:
            lines.append(f"- `{result.entry.scene_class}`: {result.error}")

    lines.extend(
        [
            "",
            "## Recommended Commands",
            "",
            "```bash",
            "./.venv/bin/python scripts/audit_all_scenes.py",
            "./.venv/bin/python scripts/audit_all_scenes.py --no-render",
            "./.venv/bin/python scripts/audit_all_scenes.py --scene-class GraphProperties",
            "```",
            "",
            "Use full narrated renders with Azure credentials for final audio/SRT QA.",
            "",
        ]
    )
    return "\n".join(lines)


def _resolve(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def _link(path: Path | None, base: Path) -> str:
    if path is None:
        return "-"
    rel = relpath(path, base)
    return f"[open]({rel})"


def _summarize_output(output: str, limit: int = 900) -> str:
    if not output:
        return "Command failed without output."
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    text = " ".join(lines[-12:])
    if len(text) > limit:
        return text[-limit:]
    return text
