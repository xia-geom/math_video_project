"""Pure Pillow/numpy visuals for the UQAM mathematics-program V3 storyboard.

The module deliberately contains no audio, subtitle, MoviePy, or file-output
logic.  Every animation is driven by named action windows expressed in local
scene seconds.  The renderer can therefore replace ``DEFAULT_ACTIONS`` with
speech-aligned timings after the final voice track is available.

Public API
----------
``draw_scene(scene_id, t, duration=None, cue_times_or_actions=None)``
    Return one 1280 x 720 RGB numpy frame.

``ActionWindow(action, start, end)``
    A small immutable timing record.  The API also accepts mappings and tuples;
    see :func:`normalise_actions`.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from program_data import PROGRAMS


WIDTH = 1280
HEIGHT = 720
FPS = 30
ROOT = Path(__file__).resolve().parent

BACKGROUND = "#F7F8FA"
SURFACE = "#FFFFFF"
INK = "#18212B"
MUTED = "#69737D"
GRID = "#E6E9ED"
SHADOW = "#18212B"
MATH = "#3157D5"
STATISTICS = "#008A7A"
COMPUTING = "#E15B45"
COMPLEMENTARY = "#F2E6C9"
NAVY = "#172A3A"

FONT_REGULAR = ROOT / "assets/fonts/NotoSans-Regular.ttf"
FONT_BOLD = ROOT / "assets/fonts/NotoSans-Bold.ttf"
FONT_MONO = ROOT / "assets/fonts/NotoSansMono-Regular.ttf"
LOGO_PATH = ROOT / "assets/identity/uqam-logo-officiel-blanc.png"


@dataclass(frozen=True)
class ActionWindow:
    """A named animation window in absolute local scene seconds."""

    action: str
    start: float
    end: float

    def __post_init__(self) -> None:
        if not self.action:
            raise ValueError("An action name cannot be empty.")
        if self.start < 0 or self.end <= self.start:
            raise ValueError(
                f"Invalid window for {self.action!r}: {self.start}–{self.end}."
            )


SCENE_DURATIONS: dict[str, float] = {
    "v3_01_opening": 7.0,
    "v3_02_reading_the_table": 16.0,
    "v3_03_course_load": 16.0,
    "v3_04_complementary_column": 15.0,
    "v3_05_common_foundation": 16.0,
    "v3_06_fundamental_mathematics": 31.0,
    "v3_07_statistics": 31.0,
    "v3_08_mathematics_computing": 32.0,
    "v3_09_computing_profiles": 16.0,
    "v3_10_comparison": 18.0,
    "v3_11_guide": 17.0,
}


# Windows are local to each scene.  Reveal motions last 0.35–0.55 seconds
# whenever possible; the rest of each storyboard interval is a visual hold.
DEFAULT_ACTIONS: dict[str, tuple[ActionWindow, ...]] = {
    "v3_01_opening": (
        ActionWindow("draw_line", 0.00, 1.20),
        ActionWindow("show_title", 1.20, 1.72),
        ActionWindow("show_curve", 2.50, 2.92),
        ActionWindow("show_points", 3.42, 3.84),
        ActionWindow("show_code", 4.34, 4.76),
    ),
    "v3_02_reading_the_table": (
        ActionWindow("show_frame", 0.00, 0.50),
        ActionWindow("show_autumn", 2.00, 2.48),
        ActionWindow("unfold_autumn", 2.48, 5.00),
        ActionWindow("show_winter", 5.00, 5.48),
        ActionWindow("unfold_winter", 5.48, 8.00),
        ActionWindow("show_year_bracket", 8.00, 8.50),
        ActionWindow("show_year_equation", 12.00, 12.50),
    ),
    "v3_03_course_load": (
        ActionWindow("show_five_cards", 0.00, 0.52),
        ActionWindow("activate_five", 3.00, 3.45),
        ActionWindow("transform_to_four", 7.00, 11.00),
        ActionWindow("expand_timeline", 8.20, 10.80),
        ActionWindow("activate_four", 11.00, 11.45),
    ),
    "v3_04_complementary_column": (
        ActionWindow("show_columns", 0.00, 3.00),
        ActionWindow("lift_right_column", 3.00, 3.50),
        ActionWindow("show_complementary", 6.00, 6.45),
        ActionWindow("show_option", 9.00, 9.45),
        ActionWindow("show_ethics", 12.00, 12.45),
    ),
    "v3_05_common_foundation": (
        ActionWindow("show_first_table", 0.00, 0.52),
        ActionWindow("duplicate_tables", 4.00, 7.00),
        ActionWindow("highlight_foundation", 7.00, 12.00),
        ActionWindow("separate_paths", 12.00, 12.55),
    ),
    "v3_06_fundamental_mathematics": (
        ActionWindow("show_analysis", 0.00, 0.50),
        ActionWindow("show_algebra", 10.00, 10.50),
        ActionWindow("show_geometry", 19.00, 19.50),
        ActionWindow("show_summary", 28.00, 28.50),
    ),
    "v3_07_statistics": (
        ActionWindow("show_collection", 0.00, 0.50),
        ActionWindow("show_models", 10.00, 10.50),
        ActionWindow("show_learning", 20.00, 20.50),
        ActionWindow("show_summary", 28.00, 28.50),
    ),
    "v3_08_mathematics_computing": (
        ActionWindow("show_programming", 0.00, 0.50),
        ActionWindow("show_algorithms", 10.00, 10.50),
        ActionWindow("show_databases", 21.00, 21.50),
        ActionWindow("show_summary", 29.00, 29.50),
    ),
    "v3_09_computing_profiles": (
        ActionWindow("show_common_card", 0.00, 0.50),
        ActionWindow("split_profiles", 3.00, 7.00),
        ActionWindow("highlight_math_profile", 7.00, 7.50),
        ActionWindow("highlight_stat_profile", 12.00, 12.50),
    ),
    "v3_10_comparison": (
        ActionWindow("show_math_map", 0.00, 0.50),
        ActionWindow("show_stat_map", 1.65, 2.15),
        ActionWindow("show_computing_map", 3.30, 3.80),
        ActionWindow("pulse_math", 5.00, 5.50),
        ActionWindow("pulse_stat", 7.00, 7.50),
        ActionWindow("pulse_computing", 9.00, 9.50),
        ActionWindow("align_foundation", 11.00, 11.55),
        ActionWindow("show_comparison_line", 15.00, 15.50),
    ),
    "v3_11_guide": (
        ActionWindow("show_guide", 0.00, 0.52),
        ActionWindow("show_guide_title", 3.00, 3.50),
        ActionWindow("show_detail_load", 7.00, 7.45),
        ActionWindow("show_detail_start", 8.70, 9.15),
        ActionWindow("show_detail_choices", 10.40, 10.85),
        ActionWindow("show_url", 12.00, 12.50),
        # No action begins after 12.5 s; the final 4.5 s, including the
        # required final two seconds, remain a perfectly still guide hold.
    ),
}


def normalise_actions(
    scene_id: str,
    value: (
        None
        | Mapping[str, Sequence[float]]
        | Iterable[ActionWindow | Mapping[str, Any] | Sequence[Any]]
    ),
) -> dict[str, ActionWindow]:
    """Return validated action windows keyed by action name.

    Accepted custom formats:

    - ``{"show_title": (1.2, 1.7)}``
    - ``[ActionWindow("show_title", 1.2, 1.7)]``
    - ``[{"action": "show_title", "start": 1.2, "end": 1.7}]``
    - ``[("show_title", 1.2, 1.7)]``
    - cue-like objects exposing ``action``, ``start`` and ``end`` attributes
    """

    if scene_id not in SCENE_DURATIONS:
        valid = ", ".join(SCENE_DURATIONS)
        raise KeyError(f"Unknown V3 scene {scene_id!r}. Expected one of: {valid}")
    if value is None:
        windows = list(DEFAULT_ACTIONS[scene_id])
    elif isinstance(value, Mapping):
        windows = [
            ActionWindow(str(action), float(span[0]), float(span[1]))
            for action, span in value.items()
        ]
    else:
        windows = []
        for item in value:
            if isinstance(item, ActionWindow):
                windows.append(item)
            elif isinstance(item, Mapping):
                windows.append(
                    ActionWindow(
                        str(item["action"]), float(item["start"]), float(item["end"])
                    )
                )
            elif all(hasattr(item, name) for name in ("action", "start", "end")):
                windows.append(
                    ActionWindow(
                        str(item.action), float(item.start), float(item.end)
                    )
                )
            else:
                action, start, end = item
                windows.append(ActionWindow(str(action), float(start), float(end)))
    by_name: dict[str, ActionWindow] = {}
    for window in windows:
        if window.action in by_name:
            raise ValueError(
                f"Duplicate action {window.action!r} for scene {scene_id!r}."
            )
        by_name[window.action] = window
    return by_name


@lru_cache(maxsize=None)
def font(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size=size)


@lru_cache(maxsize=1)
def official_logo() -> Image.Image:
    return Image.open(LOGO_PATH).convert("RGBA")


def _rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def _rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*_rgb(value), alpha)


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, value))


def ease(value: float) -> float:
    """Smoothstep easing with a complete stop at both ends."""

    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def lerp(a: float, b: float, progress: float) -> float:
    return a + (b - a) * progress


def progress(actions: Mapping[str, ActionWindow], action: str, t: float) -> float:
    window = actions.get(action)
    if window is None:
        return 0.0
    return ease((t - window.start) / (window.end - window.start))


def raw_progress(actions: Mapping[str, ActionWindow], action: str, t: float) -> float:
    window = actions.get(action)
    if window is None:
        return 0.0
    return clamp((t - window.start) / (window.end - window.start))


def _new_canvas() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), _rgba(BACKGROUND))


def _alpha_composite(base: Image.Image, overlay: Image.Image, opacity: float = 1.0) -> None:
    if opacity <= 0:
        return
    if opacity < 1:
        overlay = overlay.copy()
        channel = overlay.getchannel("A").point(lambda a: round(a * opacity))
        overlay.putalpha(channel)
    base.alpha_composite(overlay)


def _rounded_card(
    image: Image.Image,
    box: tuple[float, float, float, float],
    *,
    fill: str = SURFACE,
    outline: str = GRID,
    radius: int = 16,
    shadow: bool = True,
    shadow_alpha: int = 17,
    rail: str | None = None,
    opacity: float = 1.0,
) -> None:
    x0, y0, x1, y1 = [round(v) for v in box]
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    if shadow:
        shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.rounded_rectangle(
            (x0 + 1, y0 + 5, x1 + 1, y1 + 7),
            radius=radius,
            fill=_rgba(SHADOW, shadow_alpha),
        )
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(7))
        layer.alpha_composite(shadow_layer)
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (x0, y0, x1, y1),
        radius=radius,
        fill=_rgba(fill),
        outline=_rgba(outline),
        width=1,
    )
    if rail:
        draw.rounded_rectangle(
            (x0, y0, x0 + 7, y1),
            radius=4,
            fill=_rgba(rail),
        )
    _alpha_composite(image, layer, opacity)


def _text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    size: int,
    *,
    fill: str = INK,
    bold: bool = False,
    mono: bool = False,
    anchor: str = "la",
    align: str = "left",
    spacing: int = 7,
    opacity: float = 1.0,
) -> None:
    color = _rgba(fill, round(255 * clamp(opacity)))
    draw.multiline_text(
        xy,
        text,
        font=font(size, bold=bold, mono=mono),
        fill=color,
        anchor=anchor,
        align=align,
        spacing=spacing,
    )


def _wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    size: int,
    max_width: float,
    *,
    bold: bool = False,
    mono: bool = False,
    max_lines: int | None = None,
) -> str:
    words = text.split()
    lines: list[str] = []
    current = ""
    used_font = font(size, bold=bold, mono=mono)
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=used_font)[2]
        if current and width > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines[-1] and draw.textbbox(
            (0, 0), f"{lines[-1]}…", font=used_font
        )[2] > max_width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = f"{lines[-1].rstrip()}…"
    return "\n".join(lines)


def _title(
    image: Image.Image,
    title: str,
    subtitle: str | None = None,
    *,
    accent: str | None = None,
) -> None:
    draw = ImageDraw.Draw(image)
    if accent:
        draw.rounded_rectangle((58, 50, 64, 111), radius=3, fill=_rgba(accent))
    _text(draw, (80 if accent else 60, 48), title, 35, bold=True)
    if subtitle:
        _text(draw, (80 if accent else 60, 94), subtitle, 18, fill=MUTED)
    _brand(image)


def _brand(image: Image.Image) -> None:
    """Place the approved white UQAM asset on a dark, high-contrast plaque."""

    x0, y0, x1, y1 = 1106, 42, 1224, 82
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((x0, y0, x1, y1), radius=8, fill=_rgba(NAVY))
    logo = official_logo().copy()
    logo.thumbnail((98, 33), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (x0 + 10, y0 + 4))


def _reveal_text(
    image: Image.Image,
    text: str,
    xy: tuple[float, float],
    size: int,
    reveal: float,
    *,
    fill: str = INK,
    bold: bool = False,
    anchor: str = "la",
    rise: float = 12,
    align: str = "left",
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    _text(
        draw,
        (xy[0], xy[1] + (1 - reveal) * rise),
        text,
        size,
        fill=fill,
        bold=bold,
        anchor=anchor,
        align=align,
        opacity=reveal,
    )
    # Titles enter softly out of focus, then resolve to the exact Noto glyphs.
    # The blur is applied to the rasterized text layer—not to a scaled font—so
    # accented French characters remain crisp at the end of every reveal.
    blur_radius = (1 - clamp(reveal)) * 6.0
    if blur_radius > 0.05:
        layer = layer.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    _alpha_composite(image, layer)


def _course_grid(
    image: Image.Image,
    program_key: str,
    highlighted: Sequence[tuple[int, int]],
    *,
    x: int = 60,
    y: int = 174,
    width: int = 620,
    height: int = 438,
    accent: str,
    reveal: float = 1.0,
) -> None:
    """Draw a neutral six-session grid with labels only in selected cells."""

    data = PROGRAMS[program_key]["semesters"]
    cell_w = width / 5
    cell_h = height / 6
    selected = set(highlighted)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    for row in range(6):
        _text(
            draw,
            (x - 12, y + row * cell_h + cell_h / 2),
            f"{row + 1}",
            14,
            fill=MUTED,
            anchor="rm",
        )
        for col in range(5):
            cx0 = x + col * cell_w + 4
            cy0 = y + row * cell_h + 4
            cx1 = x + (col + 1) * cell_w - 4
            cy1 = y + (row + 1) * cell_h - 4
            active = (row, col) in selected
            draw.rounded_rectangle(
                (cx0, cy0, cx1, cy1),
                radius=10,
                fill=_rgba(SURFACE if not active else accent, 255 if active else 70),
                outline=_rgba(GRID if not active else accent, 90 if not active else 210),
                width=1,
            )
            if active:
                course = data[row][col].title
                replacements = {
                    "Plans d'expérience et ANOVA": "Plans\nd’expérience",
                    "Structures de données et algorithmes": "Structures de données\net algorithmes",
                    "Bases de données ou systèmes": "Bases de données\nou systèmes",
                    "Éthique ou mathématiques dans la société": "Éthique ou maths\ndans la société",
                    "Analyse numérique ou processus stochastiques": "Processus\nstochastiques",
                    "Analyse numérique ou probabilités II": "Probabilités II",
                }
                label = replacements.get(course, course)
                label = _wrap(draw, label, 13, cell_w - 22, bold=True, max_lines=2)
                _text(
                    draw,
                    ((cx0 + cx1) / 2, (cy0 + cy1) / 2),
                    label,
                    13,
                    fill=SURFACE,
                    bold=True,
                    anchor="mm",
                    align="center",
                    spacing=3,
                )
    _alpha_composite(image, layer, reveal)


def _segment_weights(
    actions: Mapping[str, ActionWindow], names: Sequence[str], t: float
) -> list[float]:
    starts = [progress(actions, name, t) for name in names]
    weights: list[float] = []
    for index, value in enumerate(starts):
        next_value = starts[index + 1] if index + 1 < len(starts) else 0.0
        weights.append(value * (1.0 - next_value))
    return weights


def _abstract_plot(
    image: Image.Image,
    kind: str,
    accent: str,
    phase: float,
    *,
    x0: int = 750,
    y0: int = 205,
    x1: int = 1215,
    y1: int = 594,
) -> None:
    _rounded_card(image, (x0, y0, x1, y1), shadow=True)
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + 15
    w, h = x1 - x0, y1 - y0
    pale = _rgba(accent, 45)
    strong = _rgba(accent, 235)
    if kind == "analysis":
        draw.line((x0 + 58, y1 - 74, x1 - 48, y1 - 74), fill=_rgba(GRID), width=2)
        draw.line((x0 + 58, y1 - 74, x0 + 58, y0 + 86), fill=_rgba(GRID), width=2)
        points = []
        for index in range(100):
            u = index / 99
            px = x0 + 65 + u * (w - 125)
            py = cy + 85 * math.exp(-2.8 * u) * math.cos(7.4 * u + phase * 0.5)
            points.append((px, py))
        draw.line(points, fill=strong, width=5, joint="curve")
        limit_y = cy
        draw.line((x0 + 70, limit_y, x1 - 50, limit_y), fill=pale, width=2)
        _text(draw, (x1 - 64, limit_y - 10), "limite", 14, fill=accent, anchor="rs")
    elif kind == "algebra":
        angle = phase * math.pi / 2
        centers = [(cx - 105, cy), (cx + 105, cy)]
        for idx, (sx, sy) in enumerate(centers):
            radius = 68
            pts = []
            for k in range(4):
                a = angle * idx + math.pi / 4 + k * math.pi / 2
                pts.append((sx + radius * math.cos(a), sy + radius * math.sin(a)))
            draw.polygon(pts, outline=strong, width=5)
        for a in range(4):
            p1 = (
                centers[0][0] + 68 * math.cos(math.pi / 4 + a * math.pi / 2),
                centers[0][1] + 68 * math.sin(math.pi / 4 + a * math.pi / 2),
            )
            p2 = (
                centers[1][0]
                + 68 * math.cos(angle + math.pi / 4 + a * math.pi / 2),
                centers[1][1]
                + 68 * math.sin(angle + math.pi / 4 + a * math.pi / 2),
            )
            draw.line((*p1, *p2), fill=pale, width=2)
    elif kind == "geometry":
        points = []
        morph = (1 + math.sin(phase * math.pi - math.pi / 2)) / 2
        for index in range(121):
            a = 2 * math.pi * index / 120
            radial = 112 * (1 + morph * 0.17 * math.cos(3 * a))
            px = cx + radial * math.cos(a)
            py = cy + radial * (0.58 + 0.14 * morph) * math.sin(a)
            points.append((px, py))
        draw.line(points, fill=strong, width=5, joint="curve")
        inner = [(cx + 48 * math.cos(a), cy + 28 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 80)]
        draw.line(inner, fill=pale, width=3)
    elif kind == "sample":
        chosen = {7, 12, 18, 24, 31, 40, 47, 53}
        for index in range(60):
            col, row = index % 10, index // 10
            px = x0 + 67 + col * 36
            py = y0 + 108 + row * 42
            selected = index in chosen
            r = 7 if selected else 5
            draw.ellipse(
                (px - r, py - r, px + r, py + r),
                fill=strong if selected else _rgba(MUTED, 76),
            )
        draw.rounded_rectangle(
            (x0 + 44, y0 + 82, x1 - 48, y1 - 62),
            radius=16,
            outline=_rgba(accent, 95),
            width=2,
        )
        _text(draw, (cx, y1 - 34), "un échantillon rigoureux", 15, fill=accent, anchor="ms")
    elif kind == "regression":
        rng = np.random.default_rng(21)
        coords = []
        for index in range(34):
            u = index / 33
            px = x0 + 65 + u * (w - 125)
            py = y1 - 92 - u * 190 + rng.normal(0, 34)
            coords.append((px, py))
        band = [
            (x0 + 65, y1 - 132),
            (x1 - 60, y0 + 106),
            (x1 - 60, y0 + 166),
            (x0 + 65, y1 - 72),
        ]
        draw.polygon(band, fill=pale)
        for px, py in coords:
            draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=_rgba(MUTED, 150))
        draw.line((x0 + 65, y1 - 102, x1 - 60, y0 + 136), fill=strong, width=5)
    elif kind == "clusters":
        centers = [(cx - 110, cy + 58), (cx + 28, cy - 75), (cx + 125, cy + 65)]
        rng = np.random.default_rng(33)
        colors = (MATH, STATISTICS, COMPUTING)
        for center, color in zip(centers, colors):
            for _ in range(22):
                px = center[0] + rng.normal(0, 31)
                py = center[1] + rng.normal(0, 26)
                draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=_rgba(color, 185))
            draw.ellipse(
                (center[0] - 56, center[1] - 45, center[0] + 56, center[1] + 45),
                outline=_rgba(color, 80),
                width=2,
            )
    elif kind == "code":
        _text(draw, (cx, y0 + 88), "x ↦ x² + 1", 27, fill=INK, bold=True, anchor="ma")
        draw.line((cx, y0 + 133, cx, y0 + 172), fill=_rgba(accent), width=3)
        draw.polygon(
            [(cx - 6, y0 + 166), (cx + 6, y0 + 166), (cx, y0 + 176)],
            fill=_rgba(accent),
        )
        code = "fonction f(x):\n    retourner x*x + 1"
        _text(draw, (cx, cy), code, 19, fill=accent, mono=True, anchor="mm", spacing=9)
        _text(draw, (cx, y1 - 69), "f(3) = 10", 24, fill=INK, bold=True, anchor="ms")
    elif kind == "tree":
        nodes = [
            (cx, y0 + 105),
            (cx - 115, y0 + 205),
            (cx + 115, y0 + 205),
            (cx - 165, y0 + 305),
            (cx - 65, y0 + 305),
            (cx + 65, y0 + 305),
            (cx + 165, y0 + 305),
        ]
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)]
        path = {(0, 2), (2, 5)}
        for a, b in edges:
            draw.line(
                (*nodes[a], *nodes[b]),
                fill=strong if (a, b) in path else _rgba(GRID),
                width=5 if (a, b) in path else 3,
            )
        for index, (px, py) in enumerate(nodes):
            active = index in (0, 2, 5)
            draw.ellipse(
                (px - 17, py - 17, px + 17, py + 17),
                fill=_rgba(accent if active else SURFACE),
                outline=_rgba(accent if active else MUTED, 210),
                width=2,
            )
    elif kind == "database":
        dbx0, dby0, dbx1, dby1 = x0 + 83, y0 + 90, x0 + 236, y1 - 60
        draw.rounded_rectangle(
            (dbx0, dby0, dbx1, dby1),
            radius=15,
            fill=_rgba(accent, 30),
            outline=strong,
            width=3,
        )
        for row in range(5):
            ry = dby0 + 35 + row * 48
            draw.line((dbx0 + 18, ry, dbx1 - 18, ry), fill=_rgba(accent, 92), width=2)
        query_x = x0 + 282
        _text(draw, (query_x, y0 + 137), "SELECT", 18, fill=accent, bold=True, mono=True)
        _text(draw, (query_x, y0 + 174), "données utiles", 17, fill=INK, mono=True)
        draw.line((dbx1 + 15, cy, query_x - 17, cy), fill=strong, width=3)
        draw.polygon(
            [(query_x - 23, cy - 6), (query_x - 23, cy + 6), (query_x - 13, cy)],
            fill=strong,
        )
        for row in range(3):
            ry = y0 + 235 + row * 48
            draw.rounded_rectangle(
                (query_x, ry, x1 - 55, ry + 31),
                radius=8,
                fill=_rgba(accent, 35),
            )
    _alpha_composite(image, layer)


def _draw_opening(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    draw = ImageDraw.Draw(image)
    _brand(image)
    line_p = progress(actions, "draw_line", t)
    x_start, x_end, y = 80, 640, 430
    current_x = lerp(x_start, x_end, line_p)
    draw.line((x_start, y, current_x, y), fill=_rgba(INK), width=2)
    if line_p > 0.98:
        draw.ellipse((635, 425, 645, 435), fill=_rgba(INK))
    title_p = progress(actions, "show_title", t)
    _reveal_text(
        image,
        "Étudier les mathématiques à l’UQAM",
        (640, 222),
        49,
        title_p,
        bold=True,
        anchor="ma",
        rise=18,
        align="center",
    )
    _reveal_text(
        image,
        "Une formation commune, plusieurs orientations",
        (640, 295),
        23,
        title_p,
        fill=MUTED,
        anchor="ma",
        rise=11,
        align="center",
    )
    symbols = (
        ("show_curve", 245, "curve"),
        ("show_points", 450, "points"),
        ("show_code", 835, "code"),
    )
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    for action, sx, kind in symbols:
        p = progress(actions, action, t)
        sy = y
        if kind == "curve":
            pts = []
            for i in range(35):
                u = i / 34
                pts.append((sx - 48 + 96 * u, sy - 18 * math.sin(u * math.pi)))
            sd.line(pts, fill=_rgba(MATH, round(255 * p)), width=4)
        elif kind == "points":
            for dx, dy in ((-34, -17), (-10, 8), (15, -22), (35, 13), (4, 25)):
                sd.ellipse(
                    (sx + dx - 5, sy + dy - 5, sx + dx + 5, sy + dy + 5),
                    fill=_rgba(STATISTICS, round(255 * p)),
                )
        else:
            _text(sd, (sx, sy), "{  }", 34, fill=COMPUTING, bold=True, anchor="mm", opacity=p)
    _alpha_composite(image, layer)
    return image


def _draw_reading_table(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    _title(image, "Comment lire le cheminement?")
    frame_p = progress(actions, "show_frame", t)
    x0, x1 = 245, 1090
    y_a, y_h = 238, 390
    card_w, card_h, gap = 132, 86, 14
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        (180, 170, 1138, 534),
        radius=18,
        fill=_rgba(SURFACE, round(255 * frame_p)),
        outline=_rgba(GRID, round(255 * frame_p)),
        width=1,
    )
    _alpha_composite(image, layer)
    for label, action_label, action_row, row_y in (
        ("AUTOMNE", "show_autumn", "unfold_autumn", y_a),
        ("HIVER", "show_winter", "unfold_winter", y_h),
    ):
        label_p = progress(actions, action_label, t)
        _reveal_text(
            image,
            label,
            (203, row_y + card_h / 2),
            16,
            label_p,
            fill=MUTED,
            bold=True,
            anchor="rm",
            rise=0,
        )
        unfold = raw_progress(actions, action_row, t)
        for col in range(5):
            card_progress = ease(clamp(unfold * 5 - col))
            cx0 = x0 + col * (card_w + gap)
            width = card_w * card_progress
            if width > 1:
                _rounded_card(
                    image,
                    (cx0, row_y, cx0 + width, row_y + card_h),
                    shadow=False,
                    opacity=0.98,
                )
                if card_progress > 0.7:
                    draw = ImageDraw.Draw(image)
                    _text(
                        draw,
                        (cx0 + width / 2, row_y + card_h / 2),
                        "cours",
                        16,
                        fill=MUTED,
                        anchor="mm",
                        opacity=(card_progress - 0.7) / 0.3,
                    )
    bracket_p = progress(actions, "show_year_bracket", t)
    if bracket_p:
        d = ImageDraw.Draw(image)
        bx = 1120
        top, bottom = y_a, y_h + card_h
        mid = (top + bottom) / 2
        shown_bottom = lerp(top, bottom, bracket_p)
        d.line((bx, top, bx, shown_bottom), fill=_rgba(MUTED, round(175 * bracket_p)), width=3)
        if bracket_p > 0.72:
            d.arc((bx - 22, top, bx + 22, top + 44), 270, 90, fill=_rgba(MUTED), width=3)
            d.arc((bx - 22, bottom - 44, bx + 22, bottom), 270, 90, fill=_rgba(MUTED), width=3)
            d.line((bx, mid, bx + 20, mid), fill=_rgba(MUTED), width=3)
    equation_p = progress(actions, "show_year_equation", t)
    _reveal_text(
        image,
        "1 année = Automne + Hiver",
        (640, 604),
        25,
        equation_p,
        bold=True,
        anchor="ma",
        rise=10,
    )
    return image


def _draw_course_load(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    _title(image, "Choisir un rythme de cheminement")
    five_active = progress(actions, "activate_five", t)
    four_active = progress(actions, "activate_four", t)
    transform = progress(actions, "transform_to_four", t)
    tabs = [
        (238, 157, 590, 223, "5 cours par session", five_active * (1 - four_active)),
        (690, 157, 1042, 223, "4 cours par session", four_active),
    ]
    draw = ImageDraw.Draw(image)
    for x0, y0, x1, y1, label, active in tabs:
        fill = INK if active > 0.5 else SURFACE
        text_fill = SURFACE if active > 0.5 else MUTED
        draw.rounded_rectangle(
            (x0, y0, x1, y1),
            radius=15,
            fill=_rgba(fill),
            outline=_rgba(INK if active > 0.5 else GRID),
            width=1,
        )
        _text(draw, ((x0 + x1) / 2, (y0 + y1) / 2), label, 19, fill=text_fill, bold=True, anchor="mm")
    reveal = progress(actions, "show_five_cards", t)
    area_x0, area_x1, cy = 150, 1130, 360
    five_positions = np.linspace(area_x0, area_x1 - 160, 5)
    four_positions = np.linspace(area_x0, area_x1 - 205, 4)
    card_w = lerp(160, 205, transform)
    count = 5
    for index in range(count):
        if index < 4:
            x = lerp(float(five_positions[index]), float(four_positions[index]), transform)
            opacity = reveal
        else:
            x = float(five_positions[index])
            opacity = reveal * (1 - transform)
        y = cy - 54
        _rounded_card(
            image,
            (x, y, x + card_w, y + 108),
            shadow=True,
            opacity=opacity,
        )
        if opacity > 0.05:
            d = ImageDraw.Draw(image)
            _text(d, (x + card_w / 2, cy), str(index + 1), 22, fill=MUTED, bold=True, anchor="mm", opacity=opacity)
    timeline_p = progress(actions, "expand_timeline", t)
    d = ImageDraw.Draw(image)
    line_y = 528
    start_x = 205
    end_x = lerp(900, 1075, timeline_p)
    d.line((start_x, line_y, end_x, line_y), fill=_rgba(MUTED, 100), width=3)
    for index, label in enumerate(("A1", "H1", "A2", "H2", "A3")):
        marker_x = lerp(start_x, end_x, index / 4)
        d.ellipse((marker_x - 5, line_y - 5, marker_x + 5, line_y + 5), fill=_rgba(INK))
        _text(d, (marker_x, line_y + 24), label, 13, fill=MUTED, anchor="ma")
    _text(
        d,
        (640, 612),
        "Le guide propose les deux rythmes, pour un début à l’automne ou à l’hiver.",
        18,
        fill=MUTED,
        anchor="ma",
    )
    return image


def _draw_complementary(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    _title(image, "Une place pour personnaliser le parcours")
    show = raw_progress(actions, "show_columns", t)
    lift = progress(actions, "lift_right_column", t)
    x0, y0, gap = 102, 236, 16
    card_w, card_h = 200, 284
    for index in range(5):
        p = ease(clamp(show * 5 - index))
        x = x0 + index * (card_w + gap)
        y = y0 - (12 * lift if index == 4 else 0)
        special = index == 4
        _rounded_card(
            image,
            (x, y, x + card_w, y + card_h),
            fill=COMPLEMENTARY if special else SURFACE,
            outline="#DCCCA7" if special else GRID,
            rail=COMPUTING if special else None,
            opacity=p,
        )
        if not special and p > 0.4:
            d = ImageDraw.Draw(image)
            _text(d, (x + card_w / 2, y + card_h / 2), "cours", 17, fill=MUTED, anchor="mm", opacity=p * 0.62)
    labels = (
        ("show_complementary", "Cours\ncomplémentaire"),
        ("show_option", "Cours\nd’option"),
        ("show_ethics", "Éthique ou\nmathématiques dans\nla société"),
    )
    weights = _segment_weights(actions, [name for name, _ in labels], t)
    label_x = x0 + 4 * (card_w + gap) + card_w / 2
    label_y = y0 - 12 * lift + card_h / 2
    for (_, label), weight in zip(labels, weights):
        if weight <= 0:
            continue
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        _text(d, (label_x, label_y), label, 18, fill=INK, bold=True, anchor="mm", align="center", spacing=5)
        _alpha_composite(image, layer, weight)
    d = ImageDraw.Draw(image)
    _text(d, (640, 597), "Compléter · explorer · diversifier", 20, fill=MUTED, anchor="ma")
    return image


def _draw_common_foundation(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    _title(image, "Une base largement commune")
    show = progress(actions, "show_first_table", t)
    duplicate = progress(actions, "duplicate_tables", t)
    separate = progress(actions, "separate_paths", t)
    centers_initial = [640, 640, 640]
    centers_final = [265, 640, 1015]
    accents = (MATH, STATISTICS, COMPUTING)
    names = ("Mathématiques\nfondamentales", "Statistique", "Concentration\ninformatique")
    order = (2, 1, 0)
    for idx in order:
        cx = lerp(centers_initial[idx], centers_final[idx], max(duplicate * 0.8, separate))
        offset_y = (2 - idx) * 12 * (1 - duplicate)
        opacity = show if idx == 0 else show * duplicate * (0.74 if not separate else 1.0)
        width = lerp(665, 330, max(duplicate, separate))
        x0, y0 = cx - width / 2, 190 + offset_y
        _rounded_card(image, (x0, y0, x0 + width, 520 + offset_y), rail=accents[idx], opacity=opacity)
        d = ImageDraw.Draw(image)
        _text(d, (cx, y0 + 33), names[idx], 16, fill=accents[idx], bold=True, anchor="ma", align="center", spacing=2, opacity=opacity)
        # First-year-only abstraction: two rows, broad labels, no codes.
        labels = ("Calcul", "Probabilités", "Algèbre linéaire", "Statistique", "Analyse", "Informatique")
        columns = 3 if width < 450 else 6
        rows = 2 if columns == 3 else 1
        item_w = (width - 40) / columns
        for label_index, label in enumerate(labels):
            col = label_index % columns
            row = label_index // columns
            bx0 = x0 + 20 + col * item_w + 4
            by0 = y0 + 102 + row * 90
            bx1 = x0 + 20 + (col + 1) * item_w - 4
            by1 = by0 + 62
            d.rounded_rectangle((bx0, by0, bx1, by1), radius=10, fill=_rgba(SURFACE), outline=_rgba(GRID), width=1)
            if width >= 450 or separate > 0.65:
                _text(d, ((bx0 + bx1) / 2, (by0 + by1) / 2), label, 12 if width < 450 else 13, fill=INK, anchor="mm", align="center")
    highlight = raw_progress(actions, "highlight_foundation", t)
    if highlight > 0 and separate < 0.98:
        subjects = (
            "Calcul",
            "Probabilités",
            "Algèbre linéaire",
            "Statistique",
            "Analyse",
            "Informatique / programmation",
        )
        active = min(len(subjects) - 1, int(highlight * len(subjects)))
        _rounded_card(image, (431, 550, 849, 617), fill=SURFACE, rail=(MATH, STATISTICS, COMPUTING)[active % 3], shadow=False)
        d = ImageDraw.Draw(image)
        _text(
            d,
            (640, 584),
            subjects[active],
            21 if active == len(subjects) - 1 else 24,
            bold=True,
            anchor="mm",
        )
    return image


def _draw_branch_scene(
    scene_id: str,
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    if scene_id == "v3_06_fundamental_mathematics":
        accent = MATH
        title = "Mathématiques fondamentales"
        subtitle = "Approfondir les structures et les raisonnements"
        program_key = "math"
        segments = (
            ("show_analysis", "Analyse", [(1, 3), (2, 3), (3, 1), (3, 2), (4, 1)], "analysis"),
            ("show_algebra", "Algèbre", [(0, 2), (1, 2), (2, 2), (3, 0), (4, 0)], "algebra"),
            ("show_geometry", "Géométrie et topologie", [(0, 3), (2, 1), (3, 3), (5, 0), (5, 1)], "geometry"),
            ("show_summary", "Analyse · Algèbre · Géométrie · Topologie", [], "summary"),
        )
    elif scene_id == "v3_07_statistics":
        accent = STATISTICS
        title = "Statistique"
        subtitle = "Recueillir, modéliser et comprendre les données"
        program_key = "stat"
        segments = (
            ("show_collection", "Recueillir des données", [(2, 0), (2, 1), (3, 1)], "sample"),
            ("show_models", "Construire des modèles", [(2, 2), (3, 0), (3, 2)], "regression"),
            ("show_learning", "Analyser et apprendre", [(4, 1), (4, 2), (5, 0), (5, 1)], "clusters"),
            ("show_summary", "Collecte · Modélisation · Analyse · Apprentissage", [], "summary"),
        )
    else:
        accent = COMPUTING
        title = "Concentration informatique"
        subtitle = "Relier mathématiques, algorithmes et programmation"
        program_key = "info_math"
        segments = (
            ("show_programming", "Programmer", [(1, 4), (2, 3)], "code"),
            ("show_algorithms", "Organiser et résoudre", [(3, 3), (4, 2)], "tree"),
            ("show_databases", "Données et informatique avancée", [(3, 2), (4, 3), (5, 2)], "database"),
            ("show_summary", "Programmation · Structures de données · Algorithmes · Bases de données", [], "summary"),
        )
    _title(image, title, subtitle, accent=accent)
    names = [segment[0] for segment in segments]
    weights = _segment_weights(actions, names, t)
    for (action_name, heading, highlights, visual), weight in zip(segments, weights):
        if weight <= 0:
            continue
        layer = _new_canvas()
        # Make the branch layer transparent rather than painting its background.
        layer.putalpha(0)
        if visual == "summary":
            _rounded_card(layer, (130, 230, 1150, 500), fill=SURFACE, rail=accent)
            d = ImageDraw.Draw(layer)
            _text(d, (640, 338), heading, 28, fill=accent, bold=True, anchor="mm", align="center")
            _text(
                d,
                (640, 414),
                "Une lecture simplifiée des grands domaines du cheminement",
                18,
                fill=MUTED,
                anchor="mm",
            )
        else:
            _course_grid(layer, program_key, highlights, accent=accent)
            d = ImageDraw.Draw(layer)
            _text(d, (750, 164), heading, 25, fill=accent, bold=True)
            phase_window = actions[action_name]
            phase = clamp((t - phase_window.start) / max(2.0, phase_window.end - phase_window.start + 3.0))
            _abstract_plot(layer, visual, accent, phase)
        _alpha_composite(image, layer, weight)
    return image


def _draw_profiles(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    _title(
        image,
        "Deux profils dans la concentration informatique",
        "Une base informatique commune, puis deux approfondissements",
        accent=COMPUTING,
    )
    common = progress(actions, "show_common_card", t)
    split = progress(actions, "split_profiles", t)
    math_active = progress(actions, "highlight_math_profile", t) * (
        1 - progress(actions, "highlight_stat_profile", t)
    )
    stat_active = progress(actions, "highlight_stat_profile", t)
    common_box = (
        lerp(350, 552, split),
        lerp(222, 174, split),
        lerp(930, 728, split),
        lerp(492, 294, split),
    )
    _rounded_card(image, common_box, rail=COMPUTING, opacity=common)
    d = ImageDraw.Draw(image)
    _text(
        d,
        ((common_box[0] + common_box[2]) / 2, (common_box[1] + common_box[3]) / 2 - 18),
        "Concentration informatique",
        24,
        fill=COMPUTING,
        bold=True,
        anchor="mm",
        opacity=common,
    )
    _text(
        d,
        ((common_box[0] + common_box[2]) / 2, (common_box[1] + common_box[3]) / 2 + 24),
        "Programmation · algorithmes · données",
        16,
        fill=MUTED,
        anchor="mm",
        opacity=common,
    )
    card_y0, card_y1 = 345, 617
    profile_cards = (
        (
            (95, card_y0, 610, card_y1),
            MATH,
            "Profil mathématiques",
            "Structures et mathématiques avancées",
            ("Théorie des groupes", "Théorie des anneaux", "Spécialisation en mathématiques"),
            math_active,
        ),
        (
            (670, card_y0, 1185, card_y1),
            STATISTICS,
            "Profil statistique",
            "Statistique et science des données",
            ("Statistique II", "Régression", "Statistique informatique", "Apprentissage statistique"),
            stat_active,
        ),
    )
    for box, accent, heading, phrase, courses, active in profile_cards:
        opacity = split * lerp(0.72, 1.0, active)
        _rounded_card(image, box, rail=accent, opacity=opacity, shadow=True)
        d = ImageDraw.Draw(image)
        _text(d, (box[0] + 34, box[1] + 30), heading, 23, fill=accent, bold=True, opacity=opacity)
        _text(d, (box[0] + 34, box[1] + 72), phrase, 16, fill=MUTED, opacity=opacity)
        for idx, course in enumerate(courses):
            py = box[1] + 122 + idx * 34
            d.ellipse((box[0] + 37, py + 5, box[0] + 45, py + 13), fill=_rgba(accent, round(255 * opacity)))
            _text(d, (box[0] + 58, py), course, 15, fill=INK, opacity=opacity)
        if active > 0.05:
            d.rounded_rectangle(
                (box[2] - 56, box[1] + 24, box[2] - 26, box[1] + 30),
                radius=3,
                fill=_rgba(accent, round(255 * active)),
            )
    if split > 0.05:
        d = ImageDraw.Draw(image)
        start_x, start_y = 640, common_box[3]
        left_end, right_end = 353, card_y0
        d.line((start_x, start_y, left_end, right_end), fill=_rgba(MATH, round(150 * split)), width=2)
        d.line((start_x, start_y, 928, right_end), fill=_rgba(STATISTICS, round(150 * split)), width=2)
    return image


def _draw_comparison(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    _title(image, "Trois orientations")
    align = progress(actions, "align_foundation", t)
    maps = (
        ("show_math_map", "pulse_math", MATH, "Mathématiques\nfondamentales", ("Analyse", "Algèbre", "Géométrie", "Topologie")),
        ("show_stat_map", "pulse_stat", STATISTICS, "Statistique", ("Données", "Modèles", "Incertitude", "Apprentissage")),
        ("show_computing_map", "pulse_computing", COMPUTING, "Concentration\ninformatique", ("Programmation", "Structures de données", "Algorithmes", "Deux profils")),
    )
    for index, (show_name, pulse_name, accent, heading, topics) in enumerate(maps):
        show = progress(actions, show_name, t)
        pulse = progress(actions, pulse_name, t)
        x0 = 82 + index * 405
        y0 = lerp(178 + index * 14, 178, align)
        x1, y1 = x0 + 350, 576
        _rounded_card(image, (x0, y0, x1, y1), rail=accent, opacity=show)
        d = ImageDraw.Draw(image)
        _text(d, ((x0 + x1) / 2, y0 + 58), heading, 21, fill=accent, bold=True, anchor="mm", align="center", opacity=show)
        for topic_idx, topic in enumerate(topics):
            ty = y0 + 126 + topic_idx * 61
            fill_alpha = round(26 + pulse * 30)
            d.rounded_rectangle(
                (x0 + 31, ty, x1 - 31, ty + 42),
                radius=10,
                fill=_rgba(accent, round(fill_alpha * show)),
            )
            _text(d, (x0 + 50, ty + 21), topic, 16, fill=INK, anchor="lm", opacity=show)
        base_y = lerp(y1 - 38 - index * 7, 538, align)
        d.rounded_rectangle(
            (x0 + 31, base_y, x1 - 31, base_y + 14),
            radius=7,
            fill=_rgba(accent, round(195 * show)),
        )
        if align > 0.65:
            _text(d, ((x0 + x1) / 2, base_y - 11), "base commune", 12, fill=MUTED, anchor="ms", opacity=show * align)
    line_p = progress(actions, "show_comparison_line", t)
    _reveal_text(
        image,
        "Une base largement commune. Trois orientations.",
        (640, 642),
        24,
        line_p,
        bold=True,
        anchor="ma",
        rise=10,
    )
    return image


def _guide_cover(image: Image.Image, reveal: float) -> None:
    x0, y0, x1, y1 = 105, 130, 470, 624
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    _rounded_card(layer, (x0, y0, x1, y1), shadow=True)
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((x0, y0, x1, y0 + 116), radius=16, fill=_rgba(NAVY))
    d.rectangle((x0, y0 + 90, x1, y0 + 116), fill=_rgba(NAVY))
    logo = official_logo().copy()
    logo.thumbnail((132, 44), Image.Resampling.LANCZOS)
    layer.alpha_composite(logo, (x0 + 30, y0 + 28))
    d.rectangle((x0 + 30, y0 + 146, x0 + 38, y1 - 35), fill=_rgba(STATISTICS))
    _text(d, (x0 + 64, y0 + 155), "GUIDE DE LA\nPERSONNE ÉTUDIANTE", 24, bold=True, spacing=5)
    _text(d, (x0 + 64, y0 + 249), "Mathématiques\net statistique", 21, fill=STATISTICS, bold=True, spacing=5)
    _text(d, (x0 + 64, y0 + 344), "2025–2026", 32, bold=True)
    _text(d, (x0 + 64, y1 - 61), "Baccalauréat · majeures · cheminements", 11, fill=MUTED)
    _alpha_composite(image, layer, reveal)


def _draw_guide(
    t: float, duration: float, actions: Mapping[str, ActionWindow]
) -> Image.Image:
    image = _new_canvas()
    _brand(image)
    guide_p = progress(actions, "show_guide", t)
    _guide_cover(image, guide_p)
    title_p = progress(actions, "show_guide_title", t)
    _reveal_text(image, "Pour tous les détails", (565, 135), 34, title_p, bold=True)
    _reveal_text(
        image,
        "Guide de la personne étudiante 2025–2026\nmathématiques et statistique",
        (565, 205),
        23,
        title_p,
        fill=STATISTICS,
        bold=True,
        rise=10,
    )
    details = (
        ("show_detail_load", "Cheminements à 4 ou 5 cours"),
        ("show_detail_start", "Début à l’automne ou à l’hiver"),
        ("show_detail_choices", "Préalables, options et cours complémentaires"),
    )
    d = ImageDraw.Draw(image)
    for index, (action, label) in enumerate(details):
        p = progress(actions, action, t)
        y = 335 + index * 70
        d.ellipse((568, y + 5, 580, y + 17), fill=_rgba(STATISTICS, round(255 * p)))
        _reveal_text(image, label, (602, y), 19, p, rise=7)
    url_p = progress(actions, "show_url", t)
    _reveal_text(
        image,
        "math.uqam.ca",
        (565, 585),
        30,
        url_p,
        fill=INK,
        bold=True,
        rise=8,
    )
    if url_p > 0:
        d = ImageDraw.Draw(image)
        d.rounded_rectangle((565, 628, 760, 633), radius=2, fill=_rgba(STATISTICS, round(255 * url_p)))
    return image


DRAWERS = {
    "v3_01_opening": _draw_opening,
    "v3_02_reading_the_table": _draw_reading_table,
    "v3_03_course_load": _draw_course_load,
    "v3_04_complementary_column": _draw_complementary,
    "v3_05_common_foundation": _draw_common_foundation,
    "v3_06_fundamental_mathematics": _draw_branch_scene,
    "v3_07_statistics": _draw_branch_scene,
    "v3_08_mathematics_computing": _draw_branch_scene,
    "v3_09_computing_profiles": _draw_profiles,
    "v3_10_comparison": _draw_comparison,
    "v3_11_guide": _draw_guide,
}


def draw_scene(
    scene_id: str,
    t: float,
    duration: float | None = None,
    cue_times_or_actions: (
        None
        | Mapping[str, Sequence[float]]
        | Iterable[ActionWindow | Mapping[str, Any] | Sequence[Any]]
    ) = None,
) -> np.ndarray:
    """Draw a single V3 frame as an RGB ``uint8`` numpy array.

    Parameters
    ----------
    scene_id:
        One of the eleven IDs in :data:`SCENE_DURATIONS`.
    t:
        Absolute local time in seconds from the beginning of this scene.
    duration:
        Scene duration in seconds.  Defaults to the storyboard duration.  It is
        validated but is never used to normalise animation progress.
    cue_times_or_actions:
        Optional replacement action windows.  Missing actions intentionally
        remain absent; the function never scales defaults to the audio length.
    """

    if scene_id not in DRAWERS:
        valid = ", ".join(DRAWERS)
        raise KeyError(f"Unknown V3 scene {scene_id!r}. Expected one of: {valid}")
    scene_duration = SCENE_DURATIONS[scene_id] if duration is None else float(duration)
    if scene_duration <= 0:
        raise ValueError("duration must be positive.")
    local_t = clamp(float(t), 0.0, scene_duration)
    actions = normalise_actions(scene_id, cue_times_or_actions)
    drawer = DRAWERS[scene_id]
    if scene_id in {
        "v3_06_fundamental_mathematics",
        "v3_07_statistics",
        "v3_08_mathematics_computing",
    }:
        image = drawer(scene_id, local_t, scene_duration, actions)
    else:
        image = drawer(local_t, scene_duration, actions)
    # Some primitives intentionally paint translucent RGBA pixels directly.
    # Flattening against the specified background (instead of simply dropping
    # alpha with ``convert``) preserves their intended muted opacity.
    flattened = Image.new("RGBA", image.size, _rgba(BACKGROUND))
    flattened.alpha_composite(image)
    return np.asarray(flattened.convert("RGB"), dtype=np.uint8)


__all__ = [
    "ActionWindow",
    "DEFAULT_ACTIONS",
    "DRAWERS",
    "FPS",
    "HEIGHT",
    "SCENE_DURATIONS",
    "WIDTH",
    "draw_scene",
    "normalise_actions",
]
