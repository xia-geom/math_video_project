"""
tools.ssml.engine
=================
Rule-application engine. Walks the token stream, matches rules against
tokens (respecting priority, voice, math context, and verbatim regions),
and produces a parallel list of annotations consumed by the emitter.

Public entry point
------------------
compile(body, *, voice=None, config=None, math_mode=False, verbose=False) -> str

Matching contract (v1)
----------------------
* Only `word` patterns are matched. Other pattern kinds are accepted by
  the loader but the engine logs a debug note and skips them. (Phrase,
  regex, token_class arrive in step 5.)
* Word matching is case-insensitive on token text.
* A rule with `when: "in_math"` only fires when compile(math_mode=True).
  A rule with no `when` fires regardless.
* A rule with non-empty `voices` only fires when `voice` is in the list.
* `enabled: false` rules never fire.

Conflict resolution
-------------------
Multiple rules may match the same token. Their actions are appended to
that token's annotation list in descending-priority order (higher
priority first). The emitter is responsible for sensible merging
(e.g. taking max() of stacked break durations).
"""

from __future__ import annotations

from pathlib import Path

from tools.ssml.emitter import Annotation, emit
from tools.ssml.rules import Action, Rule, RuleSet, load
from tools.ssml.tokenizer import Token, TokenKind, tokenize


def compile(
    body: str,
    *,
    voice: str | None = None,
    config: str | Path | None = None,
    math_mode: bool = False,
    verbose: bool = False,
) -> str:
    """Compile plain author text into SSML using the rule engine.

    Returned string does NOT include the outer <lang>/<prosody> envelope;
    that remains the job of tools.tts.ssml().
    """
    tokens = tokenize(body)
    ruleset: RuleSet = load(config)

    annotations = _apply_rules(
        tokens,
        ruleset=ruleset,
        voice=voice,
        math_mode=math_mode,
        verbose=verbose,
    )

    return emit(tokens, annotations=annotations, ruleset=ruleset, voice=voice)


# ── Rule application ─────────────────────────────────────────────────

def _apply_rules(
    tokens: list[Token],
    *,
    ruleset: RuleSet,
    voice: str | None,
    math_mode: bool,
    verbose: bool,
) -> list[Annotation]:
    """Return one Annotation per token (parallel list)."""
    annotations: list[Annotation] = [Annotation() for _ in tokens]

    # Rules sorted descending by priority — first one to annotate "wins"
    # the visual order in the emitter.
    active_rules = sorted(
        (r for r in ruleset.rules if r.enabled),
        key=lambda r: r.priority,
        reverse=True,
    )

    for rule in active_rules:
        if rule.voices and voice is not None and voice not in rule.voices:
            continue
        if rule.pattern.when == "in_math" and not math_mode:
            continue

        for i, tok in enumerate(tokens):
            if not _matches(rule, tok, math_mode=math_mode):
                continue
            for action in rule.actions:
                _apply_action(action, annotations[i], tok)
            if verbose:
                print(f"[ssml] {rule.id} fired @ token {i} ({tok.text!r})")

    return annotations


def _matches(rule: Rule, tok: Token, *, math_mode: bool) -> bool:
    """Return True if *rule* applies to *tok*."""
    if tok.kind == TokenKind.VERBATIM:
        return False  # never modify hand-authored SSML

    pat = rule.pattern
    if pat.word is not None:
        return tok.kind == TokenKind.WORD and tok.text.lower() == pat.word.lower()
    # Other pattern kinds: not yet implemented in v1; skip silently.
    return False


def _apply_action(action: Action, annot: Annotation, tok: Token) -> None:
    """Mutate *annot* in place to reflect *action*."""
    if action.insert_break is not None:
        before = action.insert_break.get("before")
        after = action.insert_break.get("after")
        if before:
            annot.breaks_before.append(before)
        if after:
            annot.breaks_after.append(after)
    elif action.substitute_phoneme is not None:
        ipa = action.substitute_phoneme["ipa"]
        annot.replacement = (
            f"<phoneme alphabet='ipa' ph='{ipa}'>{tok.text}</phoneme>"
        )
    # Other actions (wrap, lexicon, emphasize, no_op) are accepted by the
    # loader but not yet wired in v1. They are silently ignored here so
    # adding them later does not require ruleset/loader changes.
