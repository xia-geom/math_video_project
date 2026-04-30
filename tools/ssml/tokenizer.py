"""
tools.ssml.tokenizer
====================
Split author input into a stream of typed tokens while preserving any
SSML/XML regions that were written by hand (bookmarks, existing breaks,
say-as, phoneme, etc.) as opaque verbatim blocks.

Contract
--------
tokenize(text: str) -> list[Token]

* Each Token carries its surface text, a kind tag, and the source
  offset range so downstream rules can match position-aware.
* Round-trip property: "".join(t.text for t in tokenize(s)) == s.
* Tag handling: any "<...>" span (self-closing, opening, or closing
  tag) becomes a single VERBATIM token. Text BETWEEN tags is still
  tokenised normally — so "<say-as ...>a</say-as>" yields three
  tokens: the open tag (VERBATIM), "a" (WORD), the close tag (VERBATIM).
* Word definition: a maximal run of letters (Unicode "letter" category,
  so French accents are preserved). Apostrophes split words.
* Punctuation: each of  , . ; : ! ?  and the apostrophe characters
  '  ’  becomes its own PUNCT token.
* Whitespace: preserved as WHITESPACE tokens.
* Numbers: maximal runs of ASCII digits become NUMBER tokens. A
  digit immediately followed by letters (e.g. "3D") is split into a
  NUMBER then a WORD.

The tokenizer is idempotent on its own emit: feeding tokens.text values
back through tokenize yields an equivalent stream.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class TokenKind(str, Enum):
    WORD = "word"
    NUMBER = "number"
    PUNCT = "punct"
    VERBATIM = "verbatim"
    WHITESPACE = "ws"
    # Legacy alias — emitted only if a caller passes a chunk that the
    # tokeniser cannot classify (should not happen with current rules,
    # but keeps the type stable for forward compatibility).
    TEXT = "text"


@dataclass(frozen=True)
class Token:
    text: str
    kind: TokenKind
    start: int   # inclusive char offset into original input
    end: int     # exclusive


# ── Internal patterns ─────────────────────────────────────────────────

# A verbatim region: '<' ... '>', non-greedy, no embedded '<' or '>'.
# This intentionally does NOT try to parse XML — it just protects spans
# the author already wrote.
_VERBATIM_RE = re.compile(r"<[^<>]*>")

# Punctuation we surface as its own token. Apostrophes (' and ’) are
# included so contractions split: l'aire -> ['l', "'", 'aire'].
_PUNCT_CHARS = set(",.;:!?'’")

# A word: one or more "letter" characters (ASCII + Unicode letter,
# covering French accents). Digits handled separately.
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
_NUMBER_RE = re.compile(r"\d+")
_WS_RE = re.compile(r"\s+")


# ── Main entry point ──────────────────────────────────────────────────

def tokenize(text: str) -> list[Token]:
    """Tokenise *text*. See module docstring for the contract."""
    if not text:
        return []

    out: list[Token] = []
    # First pass: split into verbatim spans and bare-text spans.
    cursor = 0
    for m in _VERBATIM_RE.finditer(text):
        if m.start() > cursor:
            _tokenise_bare(text, cursor, m.start(), out)
        out.append(Token(
            text=m.group(0),
            kind=TokenKind.VERBATIM,
            start=m.start(),
            end=m.end(),
        ))
        cursor = m.end()
    if cursor < len(text):
        _tokenise_bare(text, cursor, len(text), out)

    return out


def _tokenise_bare(text: str, start: int, end: int, out: list[Token]) -> None:
    """Tokenise the slice text[start:end] (no verbatim regions inside)."""
    i = start
    while i < end:
        ch = text[i]

        # Whitespace run
        if ch.isspace():
            m = _WS_RE.match(text, i, end)
            assert m is not None
            out.append(Token(
                text=m.group(0),
                kind=TokenKind.WHITESPACE,
                start=i,
                end=m.end(),
            ))
            i = m.end()
            continue

        # Punctuation — single character
        if ch in _PUNCT_CHARS:
            out.append(Token(
                text=ch,
                kind=TokenKind.PUNCT,
                start=i,
                end=i + 1,
            ))
            i += 1
            continue

        # Number run (ASCII digits)
        if ch.isdigit():
            m = _NUMBER_RE.match(text, i, end)
            assert m is not None
            out.append(Token(
                text=m.group(0),
                kind=TokenKind.NUMBER,
                start=i,
                end=m.end(),
            ))
            i = m.end()
            continue

        # Word run (letters, including accented)
        m = _WORD_RE.match(text, i, end)
        if m is not None and m.end() > i:
            out.append(Token(
                text=m.group(0),
                kind=TokenKind.WORD,
                start=i,
                end=m.end(),
            ))
            i = m.end()
            continue

        # Fallback: unknown single character. Preserve as TEXT so the
        # round-trip property still holds.
        out.append(Token(
            text=ch,
            kind=TokenKind.TEXT,
            start=i,
            end=i + 1,
        ))
        i += 1
