#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.video_audit.agents import SEVERITY_ORDER
from tools.video_audit.orchestrator import run_audit


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local multi-agent audit for a Manim scene + MP4.")
    parser.add_argument("--scene", required=True, type=Path, help="Path to the Manim scene file.")
    parser.add_argument("--class", dest="scene_class", required=True, help="Renderable Manim scene class.")
    parser.add_argument("--video", required=True, type=Path, help="Path to the rendered MP4.")
    parser.add_argument("--out", type=Path, help="Markdown report output path.")
    parser.add_argument(
        "--silent-preview",
        action="store_true",
        help="Treat a missing audio stream/SRT as expected because the render was intentionally silent.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    project_root = Path.cwd()
    out_path = args.out or Path("reports") / "video_audits" / f"{args.scene_class}_audit.md"
    _, findings, report_path = run_audit(
        project_root=project_root,
        scene_path=args.scene,
        scene_class=args.scene_class,
        video_path=args.video,
        out_path=out_path,
        silent_preview=args.silent_preview,
    )

    counts = {severity: 0 for severity in SEVERITY_ORDER}
    for item in findings:
        counts[item.severity] = counts.get(item.severity, 0) + 1

    print(f"Audit report: {report_path}")
    print(
        "Findings: "
        f"{counts.get('blocker', 0)} blocker, "
        f"{counts.get('warning', 0)} warning, "
        f"{counts.get('polish', 0)} polish, "
        f"{counts.get('info', 0)} info"
    )
    return 1 if counts.get("blocker", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
