"""
Loader tests.

Each test writes a small YAML to a tmp file and asserts either the
parsed RuleSet or that ConfigError is raised with a helpful path.

The bundled config tools/ssml/config/fr_ca_math.yaml is also tested to
ensure it stays loadable as rules are added over time.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.ssml.rules import (
    Action,
    ConfigError,
    DEFAULT_CONFIG,
    Pattern,
    Rule,
    RuleSet,
    VoiceOverride,
    load,
)


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "rules.yaml"
    p.write_text(body, encoding="utf-8")
    return p


# ── happy paths ───────────────────────────────────────────────────────

def test_default_config_loads():
    rs = load(DEFAULT_CONFIG)
    assert isinstance(rs, RuleSet)
    assert rs.defaults["clause_break_ms"] == 120
    assert rs.defaults["sentence_break_ms"] == 200


def test_empty_file_returns_empty_ruleset(tmp_path):
    p = _write(tmp_path, "")
    rs = load(p)
    assert rs == RuleSet()


def test_single_rule_minimal(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: r1
    pattern: { word: "et" }
    actions:
      - insert_break: { before: "100ms" }
""")
    rs = load(p)
    assert len(rs.rules) == 1
    r = rs.rules[0]
    assert r.id == "r1"
    assert r.category == "prosody"
    assert r.pattern.word == "et"
    assert r.priority == 100
    assert r.enabled is True
    assert len(r.actions) == 1
    assert r.actions[0].insert_break == {"before": "100ms"}


def test_rules_from_all_three_sections(tmp_path):
    p = _write(tmp_path, """
version: 1
pronunciation:
  - id: pron1
    pattern: { word: "plus" }
    actions:
      - substitute_phoneme: { ipa: "plys" }
prosody:
  - id: pros1
    pattern: { word: "et" }
    actions:
      - insert_break: { before: "120ms" }
math:
  - id: math1
    pattern: { token_class: "letter" }
    actions:
      - wrap: { tag: "say-as", attrs: { "interpret-as": "characters" } }
""")
    rs = load(p)
    cats = sorted(r.category for r in rs.rules)
    assert cats == ["math", "pronunciation", "prosody"]
    by_id = {r.id: r for r in rs.rules}
    assert by_id["pron1"].actions[0].substitute_phoneme == {"ipa": "plys"}
    assert by_id["math1"].pattern.token_class == "letter"


def test_phrase_pattern(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: interval
    pattern: { phrase: ["entre", "{any}", "et", "{any}"] }
    actions:
      - insert_break: { after: "120ms" }
""")
    rs = load(p)
    assert rs.rules[0].pattern.phrase == ("entre", "{any}", "et", "{any}")


def test_voice_overrides(tmp_path):
    p = _write(tmp_path, """
version: 1
voice_overrides:
  - voice: fr-CA-JeanNeural
    defaults: { clause_break_ms: 150 }
""")
    rs = load(p)
    assert rs.voice_overrides == (
        VoiceOverride(voice="fr-CA-JeanNeural",
                      defaults={"clause_break_ms": 150}),
    )


def test_rule_with_when_guard_and_voices(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: r-with-guard
    pattern: { word: "plus", when: "in_math" }
    voices: ["fr-CA-SylvieNeural", "fr-CA-JeanNeural"]
    priority: 50
    enabled: false
    notes: "only in math context"
    actions:
      - substitute_phoneme: { ipa: "plys" }
""")
    rs = load(p)
    r = rs.rules[0]
    assert r.pattern.when == "in_math"
    assert r.voices == ("fr-CA-SylvieNeural", "fr-CA-JeanNeural")
    assert r.priority == 50
    assert r.enabled is False
    assert r.notes == "only in math context"


# ── failure modes ─────────────────────────────────────────────────────

def test_unknown_top_level_key_fails(tmp_path):
    p = _write(tmp_path, "version: 1\nbogus: 42\n")
    with pytest.raises(ConfigError, match=r"\$:.*bogus"):
        load(p)


def test_wrong_version_fails(tmp_path):
    p = _write(tmp_path, "version: 2\n")
    with pytest.raises(ConfigError, match=r"\$\.version"):
        load(p)


def test_missing_version_fails(tmp_path):
    p = _write(tmp_path, "defaults: {}\n")
    with pytest.raises(ConfigError, match=r"\$\.version"):
        load(p)


def test_pattern_must_set_exactly_one_primitive(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: bad
    pattern: { word: "et", regex: ".*" }
    actions:
      - insert_break: { before: "100ms" }
""")
    with pytest.raises(ConfigError, match=r"prosody\[0\]\.pattern.*exactly one"):
        load(p)


def test_pattern_with_no_primitive_fails(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: bad
    pattern: { when: "in_math" }
    actions:
      - insert_break: { before: "100ms" }
""")
    with pytest.raises(ConfigError, match=r"exactly one"):
        load(p)


def test_action_must_set_exactly_one_primitive(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: bad
    pattern: { word: "et" }
    actions:
      - { insert_break: { before: "100ms" }, no_op: true }
""")
    with pytest.raises(ConfigError, match=r"actions\[0\].*exactly one"):
        load(p)


def test_actions_must_be_non_empty(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: bad
    pattern: { word: "et" }
    actions: []
""")
    with pytest.raises(ConfigError, match=r"actions: must be a non-empty list"):
        load(p)


def test_unknown_rule_key_fails(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: bad
    pattern: { word: "et" }
    actions:
      - insert_break: { before: "100ms" }
    typo_field: 1
""")
    with pytest.raises(ConfigError, match=r"prosody\[0\]:.*typo_field"):
        load(p)


def test_duplicate_rule_id_fails(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: dup
    pattern: { word: "et" }
    actions:
      - insert_break: { before: "100ms" }
math:
  - id: dup
    pattern: { word: "plus" }
    actions:
      - substitute_phoneme: { ipa: "plys" }
""")
    with pytest.raises(ConfigError, match=r"duplicate rule id 'dup'"):
        load(p)


def test_priority_out_of_range_fails(tmp_path):
    p = _write(tmp_path, """
version: 1
prosody:
  - id: r
    pattern: { word: "et" }
    priority: 1500
    actions:
      - insert_break: { before: "100ms" }
""")
    with pytest.raises(ConfigError, match=r"priority"):
        load(p)


def test_substitute_phoneme_missing_ipa_fails(tmp_path):
    p = _write(tmp_path, """
version: 1
pronunciation:
  - id: r
    pattern: { word: "plus" }
    actions:
      - substitute_phoneme: { not_ipa: "plys" }
""")
    with pytest.raises(ConfigError, match=r"substitute_phoneme"):
        load(p)


def test_wrap_missing_tag_fails(tmp_path):
    p = _write(tmp_path, """
version: 1
math:
  - id: r
    pattern: { token_class: "letter" }
    actions:
      - wrap: { attrs: { "interpret-as": "characters" } }
""")
    with pytest.raises(ConfigError, match=r"wrap.*tag"):
        load(p)


def test_voice_overrides_must_be_list(tmp_path):
    p = _write(tmp_path, """
version: 1
voice_overrides: { fr-CA-JeanNeural: {} }
""")
    with pytest.raises(ConfigError, match=r"voice_overrides"):
        load(p)


def test_top_level_must_be_mapping(tmp_path):
    p = _write(tmp_path, "- 1\n- 2\n")
    with pytest.raises(ConfigError, match=r"top-level"):
        load(p)


def test_load_default_path_when_none():
    """load() with no argument uses DEFAULT_CONFIG."""
    rs = load()
    assert isinstance(rs, RuleSet)


def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        load(tmp_path / "does_not_exist.yaml")
