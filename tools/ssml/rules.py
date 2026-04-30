"""
tools.ssml.rules
================
Dataclasses for the rule/action model plus a strict YAML loader.

A RuleSet is loaded from tools/ssml/config/fr_ca_math.yaml and consumed
by tools.ssml.engine. Rule authors touch only the YAML; Python code only
changes when a *new* action primitive is added.

Schema invariants (enforced by load()):
  * Top-level keys: version (==1), defaults, pronunciation, prosody,
    math, voice_overrides. Any other key raises ConfigError.
  * Each rule has exactly one pattern primitive and at least one
    action with exactly one action primitive.
  * Rule ids are unique across the whole config.
  * voices: list[str], may be empty.
  * priority: int 0..999, default 100.

ConfigError messages always include a path string so YAML location
errors are diagnosable without a parser.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


# ── Errors ────────────────────────────────────────────────────────────

class ConfigError(ValueError):
    """Raised when a rule YAML is structurally invalid.

    The message is prefixed with a dotted path into the YAML so the
    caller can locate the offending key.
    """


# ── Patterns ──────────────────────────────────────────────────────────

_PATTERN_KEYS = ("word", "regex", "phrase", "token_class")


@dataclass(frozen=True)
class Pattern:
    """One of {word, regex, phrase, token_class}; exactly one set."""
    word: str | None = None
    regex: str | None = None
    phrase: tuple[str, ...] | None = None
    token_class: str | None = None
    when: str | None = None  # extra guard, e.g. "in_math"


# ── Actions ───────────────────────────────────────────────────────────

_ACTION_KEYS = (
    "insert_break", "wrap", "substitute_phoneme",
    "lexicon", "emphasize", "no_op",
)


@dataclass(frozen=True)
class Action:
    """One action primitive; exactly one of the *_keys is set."""
    insert_break: dict[str, Any] | None = None       # {before/after: "120ms"}
    wrap: dict[str, Any] | None = None               # {tag, attrs}
    substitute_phoneme: dict[str, str] | None = None  # {ipa}
    lexicon: str | None = None                       # lookup key
    emphasize: dict[str, str] | None = None          # {level}
    no_op: bool = False


# ── Rule ──────────────────────────────────────────────────────────────

_RULE_KEYS = ("id", "pattern", "actions", "priority", "voices",
              "enabled", "notes")

_VALID_CATEGORIES = ("pronunciation", "prosody", "math")


@dataclass(frozen=True)
class Rule:
    id: str
    pattern: Pattern
    actions: tuple[Action, ...]
    priority: int = 100
    voices: tuple[str, ...] = ()      # empty = all voices
    enabled: bool = True
    notes: str = ""
    category: str = "prosody"         # auto-set from YAML section


@dataclass(frozen=True)
class VoiceOverride:
    voice: str
    defaults: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RuleSet:
    rules: tuple[Rule, ...] = ()
    voice_overrides: tuple[VoiceOverride, ...] = ()
    defaults: dict[str, Any] = field(default_factory=dict)


# ── Loader ────────────────────────────────────────────────────────────

DEFAULT_CONFIG = Path(__file__).resolve().parent / "config" / "fr_ca_math.yaml"

_TOP_LEVEL_KEYS = ("version", "defaults", "pronunciation", "prosody",
                   "math", "voice_overrides")


def load(path: str | Path | None = None) -> RuleSet:
    """Load a RuleSet from YAML with strict schema validation.

    Raises:
        ConfigError: schema violation. Message contains a dotted path.
        FileNotFoundError: path does not exist.
    """
    p = Path(path) if path else DEFAULT_CONFIG
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))

    if raw is None:
        # Empty file is treated as an empty config — useful for tests.
        return RuleSet()

    if not isinstance(raw, dict):
        raise ConfigError(f"$: top-level YAML must be a mapping, got {type(raw).__name__}")

    _check_keys(raw, _TOP_LEVEL_KEYS, path="$")

    version = raw.get("version")
    if version != 1:
        raise ConfigError(f"$.version: must be 1, got {version!r}")

    defaults = raw.get("defaults") or {}
    if not isinstance(defaults, dict):
        raise ConfigError(f"$.defaults: must be a mapping, got {type(defaults).__name__}")

    rules: list[Rule] = []
    seen_ids: set[str] = set()
    for category in _VALID_CATEGORIES:
        section = raw.get(category) or []
        if not isinstance(section, list):
            raise ConfigError(
                f"$.{category}: must be a list, got {type(section).__name__}"
            )
        for i, raw_rule in enumerate(section):
            rule = _parse_rule(raw_rule, category=category, path=f"$.{category}[{i}]")
            if rule.id in seen_ids:
                raise ConfigError(
                    f"$.{category}[{i}].id: duplicate rule id {rule.id!r}"
                )
            seen_ids.add(rule.id)
            rules.append(rule)

    overrides_raw = raw.get("voice_overrides") or []
    if not isinstance(overrides_raw, list):
        raise ConfigError(
            f"$.voice_overrides: must be a list, got {type(overrides_raw).__name__}"
        )
    overrides = tuple(
        _parse_override(o, path=f"$.voice_overrides[{i}]")
        for i, o in enumerate(overrides_raw)
    )

    return RuleSet(
        rules=tuple(rules),
        voice_overrides=overrides,
        defaults=defaults,
    )


# ── Parsers ───────────────────────────────────────────────────────────

def _parse_rule(raw: Any, *, category: str, path: str) -> Rule:
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: must be a mapping, got {type(raw).__name__}")
    _check_keys(raw, _RULE_KEYS, path=path)

    rid = raw.get("id")
    if not isinstance(rid, str) or not rid:
        raise ConfigError(f"{path}.id: must be a non-empty string")

    if "pattern" not in raw:
        raise ConfigError(f"{path}.pattern: required")
    pattern = _parse_pattern(raw["pattern"], path=f"{path}.pattern")

    if "actions" not in raw:
        raise ConfigError(f"{path}.actions: required")
    actions_raw = raw["actions"]
    if not isinstance(actions_raw, list) or not actions_raw:
        raise ConfigError(f"{path}.actions: must be a non-empty list")
    actions = tuple(
        _parse_action(a, path=f"{path}.actions[{i}]")
        for i, a in enumerate(actions_raw)
    )

    priority = raw.get("priority", 100)
    if not isinstance(priority, int) or not (0 <= priority <= 999):
        raise ConfigError(f"{path}.priority: must be int in [0, 999], got {priority!r}")

    voices_raw = raw.get("voices", [])
    if not isinstance(voices_raw, list) or any(not isinstance(v, str) for v in voices_raw):
        raise ConfigError(f"{path}.voices: must be a list of strings")

    enabled = raw.get("enabled", True)
    if not isinstance(enabled, bool):
        raise ConfigError(f"{path}.enabled: must be a bool, got {enabled!r}")

    notes = raw.get("notes", "")
    if not isinstance(notes, str):
        raise ConfigError(f"{path}.notes: must be a string, got {type(notes).__name__}")

    return Rule(
        id=rid,
        pattern=pattern,
        actions=actions,
        priority=priority,
        voices=tuple(voices_raw),
        enabled=enabled,
        notes=notes,
        category=category,
    )


def _parse_pattern(raw: Any, *, path: str) -> Pattern:
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: must be a mapping, got {type(raw).__name__}")
    _check_keys(raw, _PATTERN_KEYS + ("when",), path=path)

    set_keys = [k for k in _PATTERN_KEYS if k in raw]
    if len(set_keys) != 1:
        raise ConfigError(
            f"{path}: must set exactly one of {_PATTERN_KEYS}, got {set_keys}"
        )

    word = raw.get("word")
    regex = raw.get("regex")
    phrase = raw.get("phrase")
    token_class = raw.get("token_class")

    if word is not None and (not isinstance(word, str) or not word):
        raise ConfigError(f"{path}.word: must be a non-empty string")
    if regex is not None and not isinstance(regex, str):
        raise ConfigError(f"{path}.regex: must be a string")
    if phrase is not None:
        if not isinstance(phrase, list) or not phrase or any(not isinstance(p, str) for p in phrase):
            raise ConfigError(f"{path}.phrase: must be a non-empty list of strings")
        phrase = tuple(phrase)
    if token_class is not None and not isinstance(token_class, str):
        raise ConfigError(f"{path}.token_class: must be a string")

    when = raw.get("when")
    if when is not None and not isinstance(when, str):
        raise ConfigError(f"{path}.when: must be a string")

    return Pattern(word=word, regex=regex, phrase=phrase,
                   token_class=token_class, when=when)


def _parse_action(raw: Any, *, path: str) -> Action:
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: must be a mapping, got {type(raw).__name__}")
    _check_keys(raw, _ACTION_KEYS, path=path)

    set_keys = [k for k in _ACTION_KEYS if k in raw]
    if len(set_keys) != 1:
        raise ConfigError(
            f"{path}: must set exactly one of {_ACTION_KEYS}, got {set_keys}"
        )

    kwargs: dict[str, Any] = {}
    if "insert_break" in raw:
        v = raw["insert_break"]
        if not isinstance(v, dict):
            raise ConfigError(f"{path}.insert_break: must be a mapping")
        kwargs["insert_break"] = v
    if "wrap" in raw:
        v = raw["wrap"]
        if not isinstance(v, dict) or "tag" not in v:
            raise ConfigError(f"{path}.wrap: must be a mapping with at least 'tag'")
        kwargs["wrap"] = v
    if "substitute_phoneme" in raw:
        v = raw["substitute_phoneme"]
        if not isinstance(v, dict) or "ipa" not in v:
            raise ConfigError(f"{path}.substitute_phoneme: must be a mapping with 'ipa'")
        if not isinstance(v["ipa"], str):
            raise ConfigError(f"{path}.substitute_phoneme.ipa: must be a string")
        kwargs["substitute_phoneme"] = v
    if "lexicon" in raw:
        v = raw["lexicon"]
        if not isinstance(v, str) or not v:
            raise ConfigError(f"{path}.lexicon: must be a non-empty string")
        kwargs["lexicon"] = v
    if "emphasize" in raw:
        v = raw["emphasize"]
        if not isinstance(v, dict) or "level" not in v:
            raise ConfigError(f"{path}.emphasize: must be a mapping with 'level'")
        kwargs["emphasize"] = v
    if "no_op" in raw:
        v = raw["no_op"]
        if not isinstance(v, bool):
            raise ConfigError(f"{path}.no_op: must be a bool")
        kwargs["no_op"] = v

    return Action(**kwargs)


def _parse_override(raw: Any, *, path: str) -> VoiceOverride:
    if not isinstance(raw, dict):
        raise ConfigError(f"{path}: must be a mapping, got {type(raw).__name__}")
    _check_keys(raw, ("voice", "defaults"), path=path)

    voice = raw.get("voice")
    if not isinstance(voice, str) or not voice:
        raise ConfigError(f"{path}.voice: must be a non-empty string")

    defaults = raw.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ConfigError(f"{path}.defaults: must be a mapping")

    return VoiceOverride(voice=voice, defaults=defaults)


# ── Helpers ───────────────────────────────────────────────────────────

def _check_keys(d: dict, allowed: tuple[str, ...], *, path: str) -> None:
    """Raise ConfigError if d has any key not in allowed."""
    extras = set(d) - set(allowed)
    if extras:
        raise ConfigError(
            f"{path}: unknown key(s) {sorted(extras)!r}; "
            f"allowed: {list(allowed)!r}"
        )
