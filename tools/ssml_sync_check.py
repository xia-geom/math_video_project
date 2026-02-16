#!/usr/bin/env python3
"""
tools/ssml_sync_check.py
========================
Semantic sync checker for Manim + SSML scenes.

Detects mismatches between:
  (a) constants defined in the SINGLE SOURCE OF TRUTH block,
  (b) values narrated in the derived SSML strings, and
  (c) values rendered on screen (MathTex / Text calls).

Usage:
    python tools/ssml_sync_check.py <scene_file.py>

Exit codes:
    0  — all checks passed
    1  — one or more errors found

Example:
    python tools/ssml_sync_check.py variables_et_polynomes/variables_et_polynomes_scene.py
"""

import sys
import re
import importlib.util
import pathlib
from typing import Any


# ── helpers ───────────────────────────────────────────────────────────

def _load_module(path: str):
    """Import a scene file as a Python module without executing Manim."""
    spec = importlib.util.spec_from_file_location("_scene_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    # Suppress Manim's config side-effects during import
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        # Some Manim imports may fail without a display; still extract constants
        pass
    return mod


def _strip_ssml_tags(ssml: str) -> str:
    """Remove XML tags, leaving only spoken text."""
    text = re.sub(r"<[^>]+>", " ", ssml)
    return re.sub(r"\s+", " ", text).strip()


def _fr_to_int(word: str) -> int | None:
    """Convert a Québec French number word to int, or None if unknown."""
    table = {
        "zéro": 0, "zero": 0,
        "un": 1, "une": 1,
        "deux": 2,
        "trois": 3,
        "quatre": 4,
        "cinq": 5,
        "six": 6,
        "sept": 7,
        "huit": 8,
        "neuf": 9,
        "dix": 10,
    }
    return table.get(word.lower().strip())


def _extract_numbers_from_ssml(ssml: str) -> list[int]:
    """
    Extract integer values narrated inside SSML.
    Recognises both digit literals ("x = 2") and French words ("vaut deux").
    """
    plain = _strip_ssml_tags(ssml)
    found: list[int] = []

    # French word numbers
    for word in re.findall(r"\b[a-zéèêëàâîïùûüÀÂÈÉÊËÎÏÔÙÛÜç]+\b", plain, re.I):
        n = _fr_to_int(word)
        if n is not None:
            found.append(n)

    # Digit literals
    for m in re.findall(r"\b\d+\b", plain):
        found.append(int(m))

    return found


# ── individual checks ─────────────────────────────────────────────────

def check_eval_points(mod, errors: list[str], warnings: list[str]) -> None:
    """
    Verify that SSML_2A narrates exactly the values in EVAL_POINTS,
    and that EVAL_POINTS values match EXPR_A * x + EXPR_B.
    """
    try:
        expr_a  = mod.EXPR_A
        expr_b  = mod.EXPR_B
        points  = mod.EVAL_POINTS
        ssml_2a = mod.SSML_2A
    except AttributeError as e:
        errors.append(f"[check_eval_points] Missing constant: {e}")
        return

    # 1. Check that EVAL_POINTS values are correctly computed
    for xv, yv in points:
        expected = expr_a * xv + expr_b
        if yv != expected:
            errors.append(
                f"[eval_points] EVAL_POINTS mismatch: "
                f"({xv}, {yv}) but {expr_a}*{xv}+{expr_b} = {expected}"
            )

    # 2. Check SSML_2A mentions expr_a and expr_b
    ssml_nums = _extract_numbers_from_ssml(ssml_2a)
    for xv, yv in points:
        if xv not in ssml_nums:
            errors.append(
                f"[ssml_2a] x value {xv} from EVAL_POINTS "
                f"not found in SSML_2A narration."
            )
        if yv not in ssml_nums:
            errors.append(
                f"[ssml_2a] output value {yv} from EVAL_POINTS "
                f"not found in SSML_2A narration."
            )

    if expr_a not in ssml_nums:
        errors.append(
            f"[ssml_2a] EXPR_A={expr_a} not narrated in SSML_2A."
        )
    if expr_b not in ssml_nums:
        errors.append(
            f"[ssml_2a] EXPR_B={expr_b} not narrated in SSML_2A."
        )


def check_ssml_2b(mod, errors: list[str], warnings: list[str]) -> None:
    """SSML_2B must mention EXPR_A and EXPR_B as the 'fixed' constants."""
    try:
        expr_a  = mod.EXPR_A
        expr_b  = mod.EXPR_B
        ssml_2b = mod.SSML_2B
    except AttributeError as e:
        errors.append(f"[check_ssml_2b] Missing constant: {e}")
        return

    nums = _extract_numbers_from_ssml(ssml_2b)
    if expr_a not in nums:
        errors.append(f"[ssml_2b] EXPR_A={expr_a} not mentioned in SSML_2B (constants beat).")
    if expr_b not in nums:
        errors.append(f"[ssml_2b] EXPR_B={expr_b} not mentioned in SSML_2B (constants beat).")


def check_poly_label(mod, errors: list[str], warnings: list[str]) -> None:
    """POLY_LABEL_TEX must be consistent with POLY_A, POLY_B, POLY_C."""
    try:
        poly_a     = mod.POLY_A
        poly_b     = mod.POLY_B
        poly_c     = mod.POLY_C
        label_tex  = mod.POLY_LABEL_TEX
        poly_func  = mod.POLY_FUNC
    except AttributeError as e:
        errors.append(f"[check_poly_label] Missing constant: {e}")
        return

    # Spot-check: label must contain the coefficient values
    label_stripped = re.sub(r"[{}\s]", "", label_tex)
    for coeff, name in [(poly_b, "POLY_B"), (poly_c, "POLY_C")]:
        if str(coeff) not in label_stripped:
            errors.append(
                f"[poly_label] {name}={coeff} not found in POLY_LABEL_TEX: {label_tex!r}"
            )

    # Verify POLY_FUNC matches the coefficients at a test point
    for xv in [-2, 0, 1, 3]:
        expected = poly_a * xv**2 + poly_b * xv + poly_c
        actual   = poly_func(xv)
        if abs(actual - expected) > 1e-9:
            errors.append(
                f"[poly_func] POLY_FUNC({xv})={actual} "
                f"but POLY_A*x²+POLY_B*x+POLY_C={expected}"
            )


def check_voice_config(mod, errors: list[str], warnings: list[str]) -> None:
    """All four expected voices must be present in VOICE_CONFIGS."""
    expected_voices = {
        "fr-CA-SylvieNeural",
        "fr-CA-JeanNeural",
        "fr-CA-AntoineNeural",
        "fr-CA-ThierryNeural",
    }
    try:
        configs = mod.VOICE_CONFIGS
    except AttributeError:
        warnings.append("[voice_config] VOICE_CONFIGS not found — skipping.")
        return

    for v in expected_voices:
        if v not in configs:
            errors.append(f"[voice_config] Voice {v!r} missing from VOICE_CONFIGS.")

    # Rates must be valid negative percentage strings
    for voice, rate in configs.items():
        if not re.match(r"^-\d+%$", rate):
            errors.append(
                f"[voice_config] Rate {rate!r} for {voice!r} "
                f"must be a negative percentage like '-12%'."
            )


def check_caption_length(mod, errors: list[str], warnings: list[str]) -> None:
    """
    Scan the scene source file for _show_caption() calls and warn if any
    caption string exceeds 55 characters (AGENT.md §8.4).
    """
    scene_path = getattr(mod, "__file__", None)
    if scene_path is None:
        warnings.append("[caption_length] Cannot determine scene file path.")
        return

    source = pathlib.Path(scene_path).read_text(encoding="utf-8")
    # Match _show_caption("...") or _show_caption('...')  (simple single-line)
    pattern = re.compile(r'_show_caption\(\s*[fF]?["\']([^"\'\\]+)["\']')
    for m in pattern.finditer(source):
        text = m.group(1)
        if len(text) > 55:
            warnings.append(
                f"[caption_length] Caption too long ({len(text)} chars): {text!r}"
            )


def check_fr_num_coverage(mod, errors: list[str], warnings: list[str]) -> None:
    """
    All integer values in EVAL_POINTS must have a French word in _FR_NUM.
    """
    try:
        points = mod.EVAL_POINTS
        fr_num = mod._FR_NUM
    except AttributeError:
        warnings.append("[fr_num] _FR_NUM or EVAL_POINTS not accessible — skipping.")
        return

    for xv, yv in points:
        for val in (xv, yv):
            if val not in fr_num:
                errors.append(
                    f"[fr_num] Value {val} appears in EVAL_POINTS "
                    f"but has no entry in _FR_NUM. Add it to keep SSML in sync."
                )


# ── main ──────────────────────────────────────────────────────────────

CHECKS = [
    check_eval_points,
    check_ssml_2b,
    check_poly_label,
    check_voice_config,
    check_caption_length,
    check_fr_num_coverage,
]


def run(scene_path: str) -> int:
    errors:   list[str] = []
    warnings: list[str] = []

    print(f"ssml_sync_check  →  {scene_path}")
    print("─" * 60)

    mod = _load_module(scene_path)

    for check in CHECKS:
        check(mod, errors, warnings)

    if warnings:
        for w in warnings:
            print(f"  WARN  {w}")
    if errors:
        for e in errors:
            print(f"  ERR   {e}")
    else:
        print(f"  OK    all {len(CHECKS)} checks passed.")

    if warnings:
        print(f"\n  {len(warnings)} warning(s).")
    if errors:
        print(f"\n  {len(errors)} error(s) — fix before rendering.")
        return 1

    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <scene_file.py>")
        sys.exit(1)
    sys.exit(run(sys.argv[1]))
