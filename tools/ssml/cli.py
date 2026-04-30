"""
tools.ssml.cli
==============
Command-line entry point for iterating on rules.

    python -m tools.ssml compile <text-or-file>
    python -m tools.ssml lint    <text-or-file>

Status
------
Skeleton — wires argparse to compile() and lint() so the CLI runs end-to-end
even before rules are implemented.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.ssml import compile as ssml_compile
from tools.ssml import lint as ssml_lint


def _read_input(arg: str) -> str:
    p = Path(arg)
    if p.exists() and p.is_file():
        return p.read_text(encoding="utf-8")
    return arg  # treat as literal text


def _cmd_compile(args: argparse.Namespace) -> int:
    text = _read_input(args.input)
    out = ssml_compile(text, voice=args.voice, math_mode=args.math, verbose=args.verbose)
    sys.stdout.write(out)
    if not out.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    text = _read_input(args.input)
    findings = ssml_lint(text, stage=args.stage)
    if not findings:
        print("OK — no findings.")
        return 0
    for f in findings:
        loc = f" @{f.offset}" if f.offset is not None else ""
        print(f"[{f.severity}] {f.rule_id}{loc}: {f.message}")
    worst = max((f.severity for f in findings), default="info")
    return 1 if worst == "error" else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tools.ssml")
    sub = parser.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("compile", help="Compile raw text to SSML")
    c.add_argument("input", help="Literal text or path to a .txt file")
    c.add_argument("--voice", default=None)
    c.add_argument("--math", action="store_true", help="Treat body as math context")
    c.add_argument("--verbose", action="store_true")
    c.set_defaults(func=_cmd_compile)

    l = sub.add_parser("lint", help="Run advisory checks")
    l.add_argument("input", help="Literal text or path to a .txt file")
    l.add_argument("--stage", choices=["pre", "post", "both"], default="both")
    l.set_defaults(func=_cmd_lint)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
