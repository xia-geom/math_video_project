"""
Smoke tests for the tools.ssml skeleton.

These confirm the package imports, the public API has the expected
shape, and the v0 pass-through behaviour is in place. They will be
superseded by real tokenizer/engine/emitter tests in step 2 of the
coding plan.
"""

from tools.ssml import LintFinding, compile, lint
from tools.ssml.rules import Rule, RuleSet, load
from tools.ssml.tokenizer import Token, TokenKind, tokenize


def test_compile_passthrough():
    assert compile("bonjour") == "bonjour"


def test_compile_accepts_kwargs():
    out = compile("bonjour", voice="fr-CA-SylvieNeural", math_mode=True, verbose=False)
    assert out == "bonjour"


def test_lint_returns_list():
    result = lint("bonjour")
    assert isinstance(result, list)
    assert all(isinstance(f, LintFinding) for f in result)


def test_tokenizer_nonempty():
    toks = tokenize("bonjour")
    assert len(toks) == 1
    assert isinstance(toks[0], Token)
    assert toks[0].kind == TokenKind.WORD
    assert toks[0].text == "bonjour"


def test_tokenizer_empty():
    assert tokenize("") == []


def test_ruleset_loads():
    rs = load()
    assert isinstance(rs, RuleSet)


def test_rule_dataclass_constructable():
    from tools.ssml.rules import Action, Pattern

    r = Rule(
        id="test",
        pattern=Pattern(word="plus"),
        actions=(Action(substitute_phoneme={"ipa": "plys"}),),
    )
    assert r.priority == 100
    assert r.enabled is True
