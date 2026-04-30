"""
tools.ssml.emitter
==================
Render an annotated token stream back to an SSML string.

Annotation model
----------------
For each token the engine produces a parallel Annotation that carries:
  * breaks_before — list of "Xms" durations to insert before the token
  * breaks_after  — list of "Xms" durations to insert after the token
  * replacement   — optional string that fully replaces the token's
                    surface text (e.g. <phoneme>...</phoneme>)

When multiple rules add breaks to the same side of the same token, the
emitter takes the *maximum* duration rather than concatenating tags. This
guards against accidental "robot pause" stacking when rules overlap.

Whitespace / punctuation tokens are emitted verbatim and never receive
breaks — the engine only annotates WORD tokens in v1.

The result string does NOT include the outer <lang>/<prosody> envelope;
that wrapping is applied by tools.tts.ssml() at the call site.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from tools.ssml.rules import RuleSet
from tools.ssml.tokenizer import Token


@dataclass
class Annotation:
    breaks_before: list[str] = field(default_factory=list)
    breaks_after: list[str] = field(default_factory=list)
    replacement: str | None = None


_DURATION_RE = re.compile(r"^(\d+)\s*ms$")


def _max_duration(durations: list[str]) -> str | None:
    """Return the longest "Xms" string from *durations*, or None if empty.

    Non-conforming entries fall back to lexical comparison so a
    misconfigured rule cannot crash the emitter.
    """
    if not durations:
        return None
    best_ms = -1
    best = durations[0]
    for d in durations:
        m = _DURATION_RE.match(d.strip())
        ms = int(m.group(1)) if m else -1
        if ms > best_ms:
            best_ms = ms
            best = d
    return best


def _render_break(duration: str | None) -> str:
    return f"<break time='{duration}'/>" if duration else ""


def emit(
    tokens: list[Token],
    *,
    annotations: list[Annotation] | None = None,
    ruleset: RuleSet | None = None,
    voice: str | None = None,
) -> str:
    """Render tokens (+ annotations) back to a string.

    *annotations* is parallel to *tokens*. If None or shorter, missing
    entries are treated as empty annotations — the round-trip property
    on plain text still holds.
    """
    if annotations is None:
        annotations = []
    out: list[str] = []

    for i, tok in enumerate(tokens):
        annot = annotations[i] if i < len(annotations) else Annotation()

        before = _max_duration(annot.breaks_before)
        after = _max_duration(annot.breaks_after)

        if before:
            out.append(_render_break(before))
        if annot.replacement is not None:
            out.append(annot.replacement)
        else:
            out.append(tok.text)
        if after:
            out.append(_render_break(after))

    return "".join(out)
