#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.video_audit.batch import filter_registry, load_ci_scene_registry, run_batch_audit


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and audit all CI production scenes.")
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Do not render first; audit existing dist MP4s and mark missing videos as skipped.",
    )
    parser.add_argument(
        "--scene-class",
        help="Limit the batch to one scene class from the CI render matrix.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("reports") / "video_audits",
        help="Directory for audit reports and INDEX.md.",
    )
    parser.add_argument(
        "--render-timeout",
        type=int,
        default=180,
        help="Maximum seconds to allow each low-quality render before recording a failure.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    project_root = Path.cwd()
    entries = filter_registry(load_ci_scene_registry(project_root), args.scene_class)
    if not entries:
        print(f"No scenes matched --scene-class={args.scene_class!r}")
        return 2

    results = run_batch_audit(
        project_root=project_root,
        entries=entries,
        out_dir=args.out_dir,
        render=not args.no_render,
        render_timeout=args.render_timeout,
        verbose=True,
    )

    failed = [result for result in results if result.render_status == "failed"]
    blockers = sum(result.counts.get("blocker", 0) for result in results)
    print(f"Batch audit index: {(project_root / args.out_dir / 'INDEX.md').resolve()}")
    print(f"Audited {sum(1 for result in results if result.audit_status == 'audited')} / {len(results)} scenes")
    print(f"Render failures: {len(failed)}")
    print(f"Audit blockers: {blockers}")
    return 1 if failed or blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
