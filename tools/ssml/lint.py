"""
tools.ssml.lint
===============
Advisory checks on raw narration input (pre-compile) and generated SSML
(post-compile). Findings are warnings by default; nothing blocks a
render in v1.

Each finding carries a stable id so CI output can be grep-checked.

Status
------
Skeleton — returns no findings.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


Severity = Literal["info", "warn", "error"]
Stage = Literal["pre", "post", "both"]


@dataclass(frozen=True)
class LintFinding:
    rule_id: str         # e.g. "stacked-breaks", "unknown-variable-letter"
    severity: Severity
    message: str
    offset: int | None = None  # char offset into the linted text, if applicable


def lint(
    body: str,
    *,
    stage: Stage = "both",
    config: str | Path | None = None,
) -> list[LintFinding]:
    """Return advisory findings for *body*. v0 stub: empty list.

    Args:
        body: Raw narration (pre-compile) or emitted SSML (post-compile).
        stage: Which check set to run.
        config: Override path to rule YAML (lints also read config for
                voice-specific thresholds).
    """
    # TODO:
    #   pre-compile:  unbalanced brackets, lone "et" at clause end,
    #                 unknown capital-letter variables outside say-as
    #   post-compile: stacked <break>s, nested <prosody>, phoneme with
    #                 non-IPA text, empty wrap tags
    return []
