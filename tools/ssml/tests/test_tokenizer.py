"""
Tokenizer tests.

Each fixture in tests/fixtures/*.txt is checked against an inline
expected list of (kind, text) pairs. We assert:

  1. The kinds and surface texts come out in order.
  2. The round-trip property holds:  "".join(t.text) == original.
  3. Offsets are non-overlapping, contiguous, and in [0, len(input)].

Whitespace is collapsed to "_" in the (kind, text) summary so the
expected lists stay readable. (This is purely cosmetic — the real
assertion compares each token individually.)
"""

from __future__ import annotations

from pathlib import Path

from tools.ssml.tokenizer import Token, TokenKind, tokenize


FIXTURE_DIR = Path(__file__).parent / "fixtures"


# ── helpers ───────────────────────────────────────────────────────────

def _summary(tokens: list[Token]) -> list[tuple[str, str]]:
    return [(t.kind.value, t.text) for t in tokens]


def _assert_round_trip(text: str, tokens: list[Token]) -> None:
    rejoined = "".join(t.text for t in tokens)
    assert rejoined == text, (
        f"round-trip failed:\n  expected: {text!r}\n  got:      {rejoined!r}"
    )


def _assert_offsets_contiguous(text: str, tokens: list[Token]) -> None:
    cursor = 0
    for t in tokens:
        assert t.start == cursor, f"gap before {t!r}: cursor={cursor}"
        assert t.end == t.start + len(t.text), f"end mismatch on {t!r}"
        assert 0 <= t.start <= len(text) and 0 <= t.end <= len(text)
        cursor = t.end
    assert cursor == len(text), f"trailing gap: cursor={cursor}, len={len(text)}"


def _load(name: str) -> str:
    return (FIXTURE_DIR / name).read_text(encoding="utf-8")


# ── fixture-driven cases ──────────────────────────────────────────────

def test_01_plain():
    text = _load("01_plain.txt")
    toks = tokenize(text)
    assert _summary(toks) == [
        ("word", "Considérons"),
        ("ws", " "),
        ("word", "un"),
        ("ws", " "),
        ("word", "triangle"),
        ("punct", "."),
        ("ws", "\n"),
    ]
    _assert_round_trip(text, toks)
    _assert_offsets_contiguous(text, toks)


def test_02_with_bookmark():
    text = _load("02_with_bookmark.txt")
    toks = tokenize(text)
    assert _summary(toks) == [
        ("word", "On"),
        ("ws", " "),
        ("word", "part"),
        ("ws", " "),
        ("word", "d"),
        ("punct", "'"),
        ("word", "un"),
        ("ws", " "),
        ("word", "triangle"),
        ("ws", " "),
        ("verbatim", "<bookmark mark='start'/>"),
        ("ws", " "),
        ("word", "rectangle"),
        ("punct", "."),
        ("ws", "\n"),
    ]
    _assert_round_trip(text, toks)
    _assert_offsets_contiguous(text, toks)


def test_03_with_say_as():
    text = _load("03_with_say_as.txt")
    toks = tokenize(text)
    assert _summary(toks) == [
        ("word", "Ses"),
        ("ws", " "),
        ("word", "côtés"),
        ("ws", " "),
        ("word", "sont"),
        ("ws", " "),
        ("verbatim", "<say-as interpret-as='characters'>"),
        ("word", "a"),
        ("verbatim", "</say-as>"),
        ("ws", " "),
        ("word", "et"),
        ("ws", " "),
        ("verbatim", "<say-as interpret-as='characters'>"),
        ("word", "b"),
        ("verbatim", "</say-as>"),
        ("punct", "."),
        ("ws", "\n"),
    ]
    _assert_round_trip(text, toks)
    _assert_offsets_contiguous(text, toks)


def test_04_punctuation():
    text = _load("04_punctuation.txt")
    toks = tokenize(text)
    # Note: NBSP before "!" and "?" in real French copy is not used here;
    # the fixture uses a regular space, which is just whitespace.
    assert _summary(toks) == [
        ("word", "Bonjour"),
        ("punct", ","),
        ("ws", " "),
        ("word", "le"),
        ("ws", " "),
        ("word", "monde"),
        ("ws", " "),
        ("punct", "!"),
        ("ws", " "),
        ("word", "Ça"),
        ("ws", " "),
        ("word", "va"),
        ("ws", " "),
        ("punct", "?"),
        ("ws", "\n"),
    ]
    _assert_round_trip(text, toks)
    _assert_offsets_contiguous(text, toks)


def test_05_apostrophe():
    text = _load("05_apostrophe.txt")
    toks = tokenize(text)
    assert _summary(toks) == [
        ("word", "L"),
        ("punct", "'"),
        ("word", "aire"),
        ("ws", " "),
        ("word", "d"),
        ("punct", "'"),
        ("word", "un"),
        ("ws", " "),
        ("word", "cercle"),
        ("punct", "."),
        ("ws", "\n"),
    ]
    _assert_round_trip(text, toks)
    _assert_offsets_contiguous(text, toks)


def test_06_break_tag():
    text = _load("06_break_tag.txt")
    toks = tokenize(text)
    assert _summary(toks) == [
        ("word", "Rappel"),
        ("ws", " "),
        ("word", "algébrique"),
        ("punct", "."),
        ("ws", " "),
        ("verbatim", "<break time='120ms'/>"),
        ("ws", " "),
        ("word", "On"),
        ("ws", " "),
        ("word", "écrit"),
        ("ws", " "),
        ("word", "a"),
        ("ws", " "),
        ("word", "plus"),
        ("ws", " "),
        ("word", "b"),
        ("punct", "."),
        ("ws", "\n"),
    ]
    _assert_round_trip(text, toks)
    _assert_offsets_contiguous(text, toks)


def test_07_empty():
    text = _load("07_empty.txt")
    toks = tokenize(text)
    assert toks == []


# ── property tests ────────────────────────────────────────────────────

def test_round_trip_for_all_fixtures():
    for fixture in sorted(FIXTURE_DIR.glob("*.txt")):
        text = fixture.read_text(encoding="utf-8")
        _assert_round_trip(text, tokenize(text))


def test_numbers_split_from_letters():
    toks = tokenize("3D")
    assert [(t.kind.value, t.text) for t in toks] == [
        ("number", "3"),
        ("word", "D"),
    ]


def test_typographic_apostrophe():
    toks = tokenize("l’aire")
    assert [(t.kind.value, t.text) for t in toks] == [
        ("word", "l"),
        ("punct", "’"),
        ("word", "aire"),
    ]


def test_unicode_token_kind_str_value():
    """TokenKind values are stable strings — config files reference them."""
    assert TokenKind.WORD.value == "word"
    assert TokenKind.NUMBER.value == "number"
    assert TokenKind.VERBATIM.value == "verbatim"


def test_returns_token_instances():
    toks = tokenize("ok")
    assert all(isinstance(t, Token) for t in toks)
