"""Pure Pillow/numpy visuals for the V4 UQAM programme video.

The module has no audio, subtitle, MoviePy, or file-output responsibilities.
It exposes the same frame-level API as the V3 visual module while keeping all
V4 decisions isolated:

``draw_scene(scene_id, t, duration=None, cue_times_or_actions=None)``
    Return one RGB frame at the configured native output size.

The concentration maps intentionally do not reconstruct an empty 6 × 5 table.
They show only representative courses, placed on explicitly named semester
rows.  Horizontal card position is treated as a layout choice, not an implied
prerequisite sequence.
"""

from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from program_data_v4 import PROGRAMS
import v4_photos
from theme import COLORS
from v4_storyboard_data import (
    ActionWindow,
    BRANCH_SEGMENTS,
    FPS as BASE_FPS,
    FRAME_SIZE_OPTIONS,
    HEIGHT as BASE_HEIGHT,
    PATHWAY_LABEL,
    SCENES,
    SCENE_BY_ID,
    SCENE_DURATIONS,
    SEMESTER_LABELS,
    WIDTH as BASE_WIDTH,
    BranchSegment,
)


ROOT = Path(__file__).resolve().parent

WIDTH = BASE_WIDTH
HEIGHT = BASE_HEIGHT
FPS = BASE_FPS
RENDER_SCALE = 1.0

BACKGROUND = COLORS["background"]
SURFACE = COLORS["paper"]
INK = COLORS["ink"]
MUTED = COLORS["muted"]
GRID = COLORS["grid"]
MATH = COLORS["math"]
STATISTICS = COLORS["stat"]
COMPUTING = COLORS["computer"]
GOLD = COLORS["gold"]
NAVY = COLORS["dark"]
SHADOW = COLORS["dark"]

PALE_MATH = "#E9EFF9"
PALE_STATISTICS = "#E4F2EF"
PALE_COMPUTING = "#F7E9E5"
PALE_GOLD = "#F7EFD8"
SOFT_SURFACE = "#FAFBFC"

DOMAIN_ILLUSTRATION_BOX = (887, 397, 1184, 536)
ANALYSIS_TANGENT_X = 1060.0
CONCLUSION_LOGO_WIDTH = 360
ALGEBRA_MODULUS = 3
ALGEBRA_TABLE = tuple(
    tuple((row + column) % ALGEBRA_MODULUS for column in range(ALGEBRA_MODULUS))
    for row in range(ALGEBRA_MODULUS)
)
ALGORITHM_INPUT = (7, 2, 5, 1)
ALGORITHM_OUTPUT = tuple(sorted(ALGORITHM_INPUT))
SYSTEM_LAYERS = ("APPLICATION", "SERVICE", "DONNÉES")

FONT_REGULAR = ROOT / "assets/fonts/NotoSans-Regular.ttf"
FONT_BOLD = ROOT / "assets/fonts/NotoSans-Bold.ttf"
FONT_MONO = ROOT / "assets/fonts/NotoSansMono-Regular.ttf"
LOGO_PATH = ROOT / "assets/identity/uqam-logo-officiel-blanc.png"
GUIDE_COVER_PATH = (
    ROOT / "assets/sources/uqam-guide-cover-2026-2027.png"
)

DEFAULT_ACTIONS: dict[str, tuple[ActionWindow, ...]] = {
    scene.id: scene.actions for scene in SCENES
}


def configure_output(width: int, height: int, fps: int) -> None:
    """Configure a native 16:9 canvas while preserving logical coordinates.

    Every drawing primitive and font is rasterized directly at the requested
    size.  This is not a post-render resize of a 720p frame.
    """

    width, height, fps = int(width), int(height), int(fps)
    if width <= 0 or height <= 0 or fps <= 0:
        raise ValueError("Output width, height, and fps must be positive")
    if width * BASE_HEIGHT != height * BASE_WIDTH:
        raise ValueError(
            f"V4 output must preserve the {BASE_WIDTH}:{BASE_HEIGHT} aspect ratio"
        )
    if (width, height) not in FRAME_SIZE_OPTIONS:
        raise ValueError(
            f"Unsupported native V4 frame size: {width}×{height}; "
            f"expected one of {FRAME_SIZE_OPTIONS!r}"
        )

    global WIDTH, HEIGHT, FPS, RENDER_SCALE
    WIDTH = width
    HEIGHT = height
    FPS = fps
    RENDER_SCALE = width / BASE_WIDTH
    font.cache_clear()


def _scaled(value: float) -> int:
    return round(float(value) * RENDER_SCALE)


def _scaled_coords(
    value: Sequence[float] | Sequence[Sequence[float]],
) -> tuple[int, ...] | list[tuple[int, ...]]:
    if value and isinstance(value[0], (tuple, list)):
        return [tuple(_scaled(item) for item in point) for point in value]
    return tuple(_scaled(item) for item in value)


class _ScaledDraw:
    """Scale logical 1280×720 Pillow drawing calls to the native canvas."""

    def __init__(self, image: Image.Image) -> None:
        self._draw = ImageDraw.Draw(image)

    def rounded_rectangle(
        self,
        xy,
        *,
        radius: float = 0,
        fill=None,
        outline=None,
        width: int = 1,
    ) -> None:
        self._draw.rounded_rectangle(
            _scaled_coords(xy),
            radius=_scaled(radius),
            fill=fill,
            outline=outline,
            width=max(1, _scaled(width)),
        )

    def ellipse(
        self,
        xy,
        *,
        fill=None,
        outline=None,
        width: int = 1,
    ) -> None:
        self._draw.ellipse(
            _scaled_coords(xy),
            fill=fill,
            outline=outline,
            width=max(1, _scaled(width)),
        )

    def line(
        self,
        xy,
        *,
        fill=None,
        width: int = 0,
        joint=None,
    ) -> None:
        self._draw.line(
            _scaled_coords(xy),
            fill=fill,
            width=max(1, _scaled(width)),
            joint=joint,
        )

    def polygon(self, xy, *, fill=None, outline=None) -> None:
        self._draw.polygon(
            _scaled_coords(xy),
            fill=fill,
            outline=outline,
        )

    def multiline_text(
        self,
        xy,
        text: str,
        *,
        font=None,
        fill=None,
        anchor=None,
        align="left",
        spacing: int = 4,
        **kwargs,
    ) -> None:
        self._draw.multiline_text(
            _scaled_coords(xy),
            text,
            font=font,
            fill=fill,
            anchor=anchor,
            align=align,
            spacing=_scaled(spacing),
            **kwargs,
        )

    def textbbox(self, xy, text: str, *, font=None, **kwargs):
        return self._draw.textbbox(
            _scaled_coords(xy),
            text,
            font=font,
            **kwargs,
        )


def _draw(image: Image.Image) -> _ScaledDraw:
    return _ScaledDraw(image)


def normalise_actions(
    scene_id: str,
    value: (
        None
        | Mapping[str, Sequence[float]]
        | Iterable[ActionWindow | Mapping[str, Any] | Sequence[Any]]
    ),
) -> dict[str, ActionWindow]:
    """Return validated action windows keyed by action name."""

    if scene_id not in SCENE_DURATIONS:
        valid = ", ".join(SCENE_DURATIONS)
        raise KeyError(f"Unknown V4 scene {scene_id!r}. Expected: {valid}")
    if value is None:
        windows = list(DEFAULT_ACTIONS[scene_id])
    elif isinstance(value, Mapping):
        windows = [
            ActionWindow(str(action), float(span[0]), float(span[1]))
            for action, span in value.items()
        ]
    else:
        windows: list[ActionWindow] = []
        for item in value:
            if isinstance(item, ActionWindow):
                windows.append(item)
            elif isinstance(item, Mapping):
                windows.append(
                    ActionWindow(
                        str(item["action"]),
                        float(item["start"]),
                        float(item["end"]),
                    )
                )
            elif all(
                hasattr(item, attribute)
                for attribute in ("action", "start", "end")
            ):
                windows.append(
                    ActionWindow(
                        str(item.action),
                        float(item.start),
                        float(item.end),
                    )
                )
            else:
                action, start, end = item
                windows.append(
                    ActionWindow(str(action), float(start), float(end))
                )
    result: dict[str, ActionWindow] = {}
    for window in windows:
        if window.action in result:
            raise ValueError(
                f"Duplicate action {window.action!r} in {scene_id!r}"
            )
        result[window.action] = window
    return result


@lru_cache(maxsize=None)
def font(
    size: int,
    *,
    bold: bool = False,
    mono: bool = False,
) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return ImageFont.truetype(str(path), size=max(1, _scaled(size)))


@lru_cache(maxsize=1)
def official_logo() -> Image.Image:
    return Image.open(LOGO_PATH).convert("RGBA")


@lru_cache(maxsize=1)
def guide_cover() -> Image.Image:
    return Image.open(GUIDE_COVER_PATH).convert("RGBA")


def _rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index : index + 2], 16) for index in (0, 2, 4))


def _rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*_rgb(value), max(0, min(255, int(alpha))))


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return min(upper, max(lower, value))


def ease(value: float) -> float:
    value = clamp(value)
    return value * value * (3.0 - 2.0 * value)


def lerp(start: float, end: float, progress_value: float) -> float:
    return start + (end - start) * progress_value


def progress(
    actions: Mapping[str, ActionWindow],
    action: str,
    t: float,
) -> float:
    window = actions.get(action)
    if window is None:
        return 0.0
    return ease((t - window.start) / (window.end - window.start))


def raw_progress(
    actions: Mapping[str, ActionWindow],
    action: str,
    t: float,
) -> float:
    window = actions.get(action)
    if window is None:
        return 0.0
    return clamp((t - window.start) / (window.end - window.start))


def _segment_weights(
    actions: Mapping[str, ActionWindow],
    names: Sequence[str],
    t: float,
) -> list[float]:
    reveals = [progress(actions, name, t) for name in names]
    return [
        reveal
        * (1.0 - reveals[index + 1] if index + 1 < len(reveals) else 1.0)
        for index, reveal in enumerate(reveals)
    ]


def _phased_segment_weights(
    actions: Mapping[str, ActionWindow],
    names: Sequence[str],
    t: float,
) -> list[float]:
    """Fade old content out before new content enters the same action window."""

    weights = [0.0 for _ in names]
    if not names:
        return weights
    first = raw_progress(actions, names[0], t)
    if first < 1.0:
        weights[0] = ease(first)
        return weights
    weights[0] = 1.0
    for index in range(1, len(names)):
        reveal = raw_progress(actions, names[index], t)
        if reveal <= 0.0:
            return weights
        weights[index - 1] = 0.0
        if reveal <= 0.5 + 1e-9:
            weights[index - 1] = 1.0 - ease(min(reveal, 0.5) * 2.0)
            return weights
        weights[index] = ease((reveal - 0.5) * 2.0)
        if reveal < 1.0:
            return weights
    return weights


def _new_canvas() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), _rgba(BACKGROUND))


def _composite(
    image: Image.Image,
    layer: Image.Image,
    opacity: float = 1.0,
) -> None:
    opacity = clamp(opacity)
    if opacity <= 0:
        return
    if opacity < 1:
        layer = layer.copy()
        alpha = layer.getchannel("A").point(
            lambda value: round(value * opacity)
        )
        layer.putalpha(alpha)
    image.alpha_composite(layer)


def _text(
    draw: _ScaledDraw,
    xy: tuple[float, float],
    text: str,
    size: int,
    *,
    fill: str = INK,
    bold: bool = False,
    mono: bool = False,
    anchor: str = "la",
    align: str = "left",
    spacing: int = 6,
    opacity: float = 1.0,
) -> None:
    opacity = clamp(opacity)
    if opacity <= 0:
        return
    draw.multiline_text(
        xy,
        text,
        font=font(size, bold=bold, mono=mono),
        fill=_rgba(fill, round(255 * opacity)),
        anchor=anchor,
        align=align,
        spacing=spacing,
    )


def _wrap(
    draw: _ScaledDraw,
    text: str,
    size: int,
    max_width: float,
    *,
    bold: bool = False,
    mono: bool = False,
) -> str:
    words = text.split()
    lines: list[str] = []
    current = ""
    used_font = font(size, bold=bold, mono=mono)
    for word in words:
        candidate = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), candidate, font=used_font)
        if current and bbox[2] - bbox[0] > _scaled(max_width):
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


def _concentration_card_title(
    image: Image.Image,
    program_key: str,
    size: int,
    max_width: float,
) -> str:
    """Keep the common concentration label visible above each branch name."""
    label, name = PROGRAMS[program_key]["short_title"].split(" ", 1)
    return label + "\n" + _wrap(
        _draw(image), name, size, max_width, bold=True
    )


def _rounded_card(
    image: Image.Image,
    box: tuple[float, float, float, float],
    *,
    fill: str = SURFACE,
    outline: str = GRID,
    radius: int = 16,
    rail: str | None = None,
    shadow: bool = True,
    opacity: float = 1.0,
) -> None:
    x0, y0, x1, y1 = [round(value) for value in box]
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    if shadow:
        shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        shadow_draw = _draw(shadow_layer)
        shadow_draw.rounded_rectangle(
            (x0 + 2, y0 + 6, x1 + 2, y1 + 8),
            radius=radius,
            fill=_rgba(SHADOW, 17),
        )
        shadow_layer = shadow_layer.filter(
            ImageFilter.GaussianBlur(7 * RENDER_SCALE)
        )
        layer.alpha_composite(shadow_layer)
    draw = _draw(layer)
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
    _composite(image, layer, opacity)


def _pill(
    image: Image.Image,
    box: tuple[float, float, float, float],
    label: str,
    *,
    fill: str,
    text_fill: str = INK,
    outline: str | None = None,
    size: int = 15,
    bold: bool = True,
    opacity: float = 1.0,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = _draw(layer)
    draw.rounded_rectangle(
        box,
        radius=round((box[3] - box[1]) / 2),
        fill=_rgba(fill),
        outline=_rgba(outline or fill),
        width=1,
    )
    _text(
        draw,
        ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2),
        label,
        size,
        fill=text_fill,
        bold=bold,
        anchor="mm",
    )
    _composite(image, layer, opacity)


def _brand(image: Image.Image) -> None:
    x0, y0, x1, y1 = 1102, 35, 1224, 77
    draw = _draw(image)
    draw.rounded_rectangle(
        (x0, y0, x1, y1),
        radius=8,
        fill=_rgba(NAVY),
    )
    logo = official_logo().copy()
    logo.thumbnail((_scaled(101), _scaled(34)), Image.Resampling.LANCZOS)
    image.alpha_composite(logo, (_scaled(x0 + 10), _scaled(y0 + 4)))


def _scene_title(
    image: Image.Image,
    title: str,
    subtitle: str = "",
    *,
    accent: str | None = None,
) -> None:
    draw = _draw(image)
    title_x = 78 if accent else 60
    if accent:
        draw.rounded_rectangle(
            (58, 39, 64, 102),
            radius=3,
            fill=_rgba(accent),
        )
    _text(draw, (title_x, 36), title, 32, bold=True)
    if subtitle:
        wrapped = _wrap(draw, subtitle, 16, 850)
        _text(draw, (title_x, 82), wrapped, 16, fill=MUTED)
    _brand(image)


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
    align: str = "left",
    rise: float = 10,
    spacing: int = 6,
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = _draw(layer)
    _text(
        draw,
        (xy[0], xy[1] + (1.0 - reveal) * rise),
        text,
        size,
        fill=fill,
        bold=bold,
        anchor=anchor,
        align=align,
        spacing=spacing,
        opacity=reveal,
    )
    blur_radius = (1.0 - clamp(reveal)) * 4.5 * RENDER_SCALE
    if blur_radius > 0.05:
        layer = layer.filter(ImageFilter.GaussianBlur(blur_radius))
    _composite(image, layer)


def _arrow(
    image: Image.Image,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str,
    reveal: float,
    width: int = 4,
) -> None:
    reveal = clamp(reveal)
    current = (
        lerp(start[0], end[0], reveal),
        lerp(start[1], end[1], reveal),
    )
    draw = _draw(image)
    draw.line((*start, *current), fill=_rgba(color), width=width)
    if reveal > 0.92:
        x, y = end
        draw.polygon(
            ((x, y), (x - 12, y - 7), (x - 12, y + 7)),
            fill=_rgba(color),
        )


def _pathway_label(image: Image.Image) -> None:
    draw = _draw(image)
    _text(
        draw,
        (60, 119),
        PATHWAY_LABEL,
        13,
        fill=MUTED,
        bold=True,
    )


def _draw_opening(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    _brand(image)
    kicker = progress(actions, "show_kicker", t)
    title_reveal = progress(actions, "show_title", t)
    _reveal_text(
        image,
        "APERÇU DU PROGRAMME",
        (640, 105),
        15,
        kicker,
        fill=MUTED,
        bold=True,
        anchor="ma",
        rise=6,
    )
    _reveal_text(
        image,
        "Baccalauréat en mathématiques",
        (640, 157),
        46,
        title_reveal,
        bold=True,
        anchor="ma",
        align="center",
        rise=15,
    )
    _reveal_text(
        image,
        "Comprendre les cheminements et les concentrations",
        (640, 222),
        21,
        title_reveal,
        fill=MUTED,
        anchor="ma",
        rise=10,
    )
    cards = (
        (
            "show_math_card",
            (72, 326, 430, 562),
            MATH,
            PALE_MATH,
            _concentration_card_title(image, "math", 23, 298),
            "Théorie · structures · démonstrations",
        ),
        (
            "show_statistics_card",
            (461, 326, 819, 562),
            STATISTICS,
            PALE_STATISTICS,
            _concentration_card_title(image, "stat", 23, 298),
            "Données · modèles · incertitude",
        ),
        (
            "show_computing_card",
            (850, 326, 1208, 562),
            COMPUTING,
            PALE_COMPUTING,
            _concentration_card_title(image, "info_math", 23, 298),
            "Programmation · algorithmes · systèmes",
        ),
    )
    for action, box, accent, pale, heading, description in cards:
        reveal = progress(actions, action, t)
        shifted = (
            box[0],
            box[1] + (1 - reveal) * 14,
            box[2],
            box[3] + (1 - reveal) * 14,
        )
        _rounded_card(
            image,
            shifted,
            fill=SURFACE,
            outline=pale,
            rail=accent,
            opacity=reveal,
        )
        content = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = _draw(content)
        _text(
            draw,
            ((box[0] + box[2]) / 2, box[1] + 76),
            heading,
            23,
            fill=accent,
            bold=True,
            anchor="mm",
            align="center",
            spacing=4,
        )
        _text(
            draw,
            ((box[0] + box[2]) / 2, box[1] + 164),
            _wrap(draw, description, 15, box[2] - box[0] - 60),
            15,
            fill=INK,
            anchor="mm",
            align="center",
        )
        _composite(image, content, reveal)
    footer_reveal = progress(actions, "show_computing_card", t)
    _reveal_text(
        image,
        "Trois concentrations · des orientations disciplinaires distinctes",
        (640, 632),
        17,
        footer_reveal,
        fill=MUTED,
        anchor="ma",
        rise=6,
    )
    return image


def _load_card(
    image: Image.Image,
    box: tuple[int, int, int, int],
    *,
    accent: str,
    pale: str,
    heading: str,
    count: int,
    reveal: float,
    timeline_reveal: float,
    timeline_label: str,
) -> None:
    _rounded_card(
        image,
        box,
        fill=SURFACE,
        outline=pale,
        rail=accent,
        opacity=reveal,
    )
    draw = _draw(image)
    _text(
        draw,
        (box[0] + 38, box[1] + 34),
        heading,
        24,
        fill=accent,
        bold=True,
        opacity=reveal,
    )
    _text(
        draw,
        (box[0] + 38, box[1] + 82),
        f"{count} cours par session",
        18,
        fill=INK,
        bold=True,
        opacity=reveal,
    )
    inner_x0 = box[0] + 38
    available = box[2] - box[0] - 76
    gap = 9
    card_w = (available - gap * (count - 1)) / count
    for index in range(count):
        cx0 = inner_x0 + index * (card_w + gap)
        draw.rounded_rectangle(
            (cx0, box[1] + 126, cx0 + card_w, box[1] + 198),
            radius=10,
            fill=_rgba(pale, round(255 * reveal)),
            outline=_rgba(accent, round(120 * reveal)),
            width=1,
        )
        _text(
            draw,
            (cx0 + card_w / 2, box[1] + 162),
            str(index + 1),
            15,
            fill=accent,
            bold=True,
            anchor="mm",
            opacity=reveal,
        )
    timeline_y = box[1] + 245
    line_x0, line_x1 = box[0] + 55, box[2] - 55
    current_x = lerp(line_x0, line_x1, timeline_reveal)
    draw.line(
        (line_x0, timeline_y, current_x, timeline_y),
        fill=_rgba(accent, round(255 * reveal)),
        width=3,
    )
    if timeline_reveal > 0.02:
        node_count = 6 if count == 5 else 8
        visible = max(1, round(node_count * timeline_reveal))
        for index in range(visible):
            x = line_x0 + index * (line_x1 - line_x0) / (node_count - 1)
            draw.ellipse(
                (x - 5, timeline_y - 5, x + 5, timeline_y + 5),
                fill=_rgba(accent, round(255 * reveal)),
            )
    _text(
        draw,
        ((box[0] + box[2]) / 2, timeline_y + 31),
        timeline_label,
        14,
        fill=MUTED,
        anchor="ma",
        opacity=reveal * timeline_reveal,
    )


def _draw_course_load(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    _scene_title(
        image,
        "Deux rythmes de progression",
        "Le guide présente une grille distincte pour chaque rythme.",
        accent=MATH,
    )
    five = progress(actions, "show_five", t)
    five_timeline = progress(actions, "show_three_years", t)
    four = progress(actions, "show_four", t)
    four_timeline = progress(actions, "show_extended_path", t)
    _load_card(
        image,
        (65, 166, 610, 548),
        accent=MATH,
        pale=PALE_MATH,
        heading="Rythme présenté dans cette vidéo",
        count=5,
        reveal=five,
        timeline_reveal=five_timeline,
        timeline_label="6 sessions · début à l’automne",
    )
    _load_card(
        image,
        (670, 166, 1215, 548),
        accent=STATISTICS,
        pale=PALE_STATISTICS,
        heading="Autre rythme proposé dans le guide",
        count=4,
        reveal=four,
        timeline_reveal=four_timeline,
        timeline_label="Parcours réparti sur davantage de sessions",
    )
    note = progress(actions, "show_load_note", t)
    _reveal_text(
        image,
        "La durée du parcours varie selon la charge retenue.",
        (640, 615),
        20,
        note,
        fill=INK,
        bold=True,
        anchor="ma",
        rise=7,
    )
    return image


def _draw_complementary(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    _scene_title(
        image,
        "Des choix intégrés au cheminement",
        "Certaines sessions réservent une place à la diversification.",
        accent=GOLD,
    )
    session_reveal = progress(actions, "show_session", t)
    x0, y0, card_w, gap = 80, 222, 208, 18
    labels = (
        "Cours du\ncheminement",
        "Cours du\ncheminement",
        "Cours du\ncheminement",
        "Cours du\ncheminement",
    )
    for index, label in enumerate(labels):
        reveal = ease(clamp(session_reveal * 4 - index))
        box = (
            x0 + index * (card_w + gap),
            y0,
            x0 + index * (card_w + gap) + card_w,
            y0 + 238,
        )
        _rounded_card(
            image,
            box,
            fill=SURFACE,
            shadow=True,
            opacity=reveal,
        )
        draw = _draw(image)
        _text(
            draw,
            ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2),
            label,
            17,
            fill=MUTED,
            anchor="mm",
            align="center",
            opacity=reveal,
        )
    special_box = (984, y0 - 14, 1200, y0 + 252)
    _rounded_card(
        image,
        special_box,
        fill=PALE_GOLD,
        outline="#D7C17D",
        rail=GOLD,
        opacity=session_reveal,
    )
    choices = (
        ("show_complementary", "Cours\ncomplémentaire"),
        ("show_option", "Cours\nà option"),
        (
            "show_society",
            "Éthique ou\nmathématiques\ndans la société",
        ),
    )
    weights = _segment_weights(
        actions,
        [action for action, _ in choices],
        t,
    )
    for (_, label), weight in zip(choices, weights):
        _reveal_text(
            image,
            label,
            (
                (special_box[0] + special_box[2]) / 2,
                (special_box[1] + special_box[3]) / 2,
            ),
            18,
            weight,
            fill=GOLD,
            bold=True,
            anchor="mm",
            align="center",
            rise=6,
            spacing=4,
        )
    draw = _draw(image)
    _text(
        draw,
        (640, 507),
        "UNE SESSION · CINQ COURS",
        13,
        fill=MUTED,
        bold=True,
        anchor="ma",
        opacity=session_reveal,
    )
    note = progress(actions, "show_choice_note", t)
    _reveal_text(
        image,
        "Ces choix de cours permettent de diversifier la formation.",
        (640, 590),
        20,
        note,
        fill=INK,
        bold=True,
        anchor="ma",
    )
    return image


def _draw_common_to_specialization(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    _scene_title(
        image,
        "Des enseignements communs à la spécialisation",
        "Le cheminement se précise progressivement.",
        accent=COMPUTING,
    )
    common_reveal = progress(actions, "show_common", t)
    _rounded_card(
        image,
        (66, 165, 565, 552),
        fill=SURFACE,
        rail=NAVY,
        opacity=common_reveal,
    )
    draw = _draw(image)
    _text(
        draw,
        (100, 197),
        "ENSEIGNEMENTS COMMUNS",
        14,
        fill=MUTED,
        bold=True,
        opacity=common_reveal,
    )
    _text(
        draw,
        (100, 230),
        "Fondements des 3 concentrations\nen 1re année",
        23,
        fill=INK,
        bold=True,
        spacing=5,
        opacity=common_reveal,
    )
    subjects = (
        "Calcul",
        "Algèbre linéaire",
        "Probabilités",
        "Statistique",
        "Analyse",
        "Mathématiques algorithmiques",
        "Informatique / programmation",
    )
    subject_reveal = raw_progress(actions, "show_subjects", t)
    for index, subject in enumerate(subjects):
        item_reveal = ease(clamp(subject_reveal * len(subjects) - index))
        column = index % 2
        row = index // 2
        bx0 = 100 + column * 217
        by0 = 318 + row * 52
        width = 410 if index == len(subjects) - 1 else 197
        _pill(
            image,
            (bx0, by0, bx0 + width, by0 + 38),
            subject,
            fill=SOFT_SURFACE,
            outline=GRID,
            text_fill=INK,
            size=13 if len(subject) > 24 else 14,
            bold=False,
            opacity=item_reveal,
        )
    transition = progress(actions, "show_transition", t)
    _arrow(
        image,
        (595, 362),
        (735, 362),
        color=COMPUTING,
        reveal=transition,
        width=5,
    )
    _reveal_text(
        image,
        "spécialisation",
        (665, 330),
        13,
        transition,
        fill=COMPUTING,
        bold=True,
        anchor="ms",
        rise=4,
    )
    concentrations = (
        (MATH, PALE_MATH, _concentration_card_title(image, "math", 20, 386)),
        (STATISTICS, PALE_STATISTICS, _concentration_card_title(image, "stat", 20, 386)),
        (COMPUTING, PALE_COMPUTING, _concentration_card_title(image, "info_math", 20, 386)),
    )
    concentration_reveal = raw_progress(
        actions,
        "show_concentrations",
        t,
    )
    for index, (accent, pale, label) in enumerate(concentrations):
        reveal = ease(
            clamp(concentration_reveal * len(concentrations) - index)
        )
        y = 196 + index * 118
        _rounded_card(
            image,
            (758, y, 1208, y + 91),
            fill=SURFACE,
            outline=pale,
            rail=accent,
            opacity=reveal,
        )
        _text(
            _draw(image),
            (790, y + 45),
            label,
            20,
            fill=accent,
            bold=True,
            anchor="lm",
            opacity=reveal,
        )
    note = progress(actions, "show_specialization_note", t)
    _reveal_text(
        image,
        "La spécialisation s’amorce en deuxième année.",
        (640, 614),
        19,
        note,
        fill=INK,
        bold=True,
        anchor="ma",
    )
    return image


def _draw_map_skeleton(
    image: Image.Image,
    *,
    accent: str,
    reveal: float,
) -> None:
    x0, x1 = 54, 828
    y0, row_h = 160, 72
    axis_x = 236
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = _draw(layer)
    draw.line(
        (axis_x, y0 + 30, axis_x, y0 + 5 * row_h + 30),
        fill=_rgba(accent, 175),
        width=3,
    )
    for row, semester in enumerate(SEMESTER_LABELS):
        y = y0 + row * row_h
        draw.rounded_rectangle(
            (x0, y, x1, y + 60),
            radius=12,
            fill=_rgba(SURFACE, 218),
            outline=_rgba(GRID),
            width=1,
        )
        draw.ellipse(
            (axis_x - 6, y + 24, axis_x + 6, y + 36),
            fill=_rgba(accent),
        )
        _text(
            draw,
            (72, y + 30),
            semester,
            14,
            fill=INK,
            bold=True,
            anchor="lm",
        )
    _composite(image, layer, reveal)


def _course_font_size(title: str) -> int:
    if len(title) <= 24:
        return 15
    if len(title) <= 38:
        return 13
    return 11


def _draw_course_placements(
    image: Image.Image,
    segment: BranchSegment,
    *,
    accent: str,
    pale: str,
    opacity: float,
) -> None:
    by_row: dict[int, list[str]] = {}
    for placement in segment.courses:
        by_row.setdefault(placement.row, []).append(placement.title)
    x0, x1 = 264, 814
    y0, row_h = 160, 72
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = _draw(layer)
    for row, titles in by_row.items():
        gap = 10
        width = min(
            268,
            (x1 - x0 - gap * (len(titles) - 1)) / len(titles),
        )
        for index, title in enumerate(titles):
            bx0 = x0 + index * (width + gap)
            by0 = y0 + row * row_h + 5
            bx1, by1 = bx0 + width, by0 + 50
            draw.rounded_rectangle(
                (bx0, by0, bx1, by1),
                radius=11,
                fill=_rgba(pale),
                outline=_rgba(accent, 205),
                width=2,
            )
            size = _course_font_size(title)
            wrapped = _wrap(
                draw,
                title,
                size,
                width - 18,
                bold=True,
            )
            _text(
                draw,
                ((bx0 + bx1) / 2, (by0 + by1) / 2),
                wrapped,
                size,
                fill=accent,
                bold=True,
                anchor="mm",
                align="center",
                spacing=2,
            )
    _composite(image, layer, opacity)


def _stage(reveal: float, start: float, end: float) -> float:
    """Return one eased, bounded stage within a cue-bound reveal."""

    if end <= start:
        return 1.0 if reveal >= end else 0.0
    return ease((reveal - start) / (end - start))


def _polyline_prefix(
    points: Sequence[tuple[float, float]],
    reveal: float,
) -> list[tuple[float, float]]:
    """Return the length-proportional prefix of a polyline."""

    if len(points) < 2 or reveal <= 0:
        return []
    reveal = clamp(reveal)
    lengths = [
        math.hypot(end[0] - start[0], end[1] - start[1])
        for start, end in zip(points, points[1:])
    ]
    total = sum(lengths)
    if total <= 0:
        return [points[0]]
    remaining = total * reveal
    prefix = [points[0]]
    for start, end, length in zip(points, points[1:], lengths):
        if remaining >= length:
            prefix.append(end)
            remaining -= length
            continue
        fraction = 0.0 if length == 0 else remaining / length
        prefix.append(
            (
                lerp(start[0], end[0], fraction),
                lerp(start[1], end[1], fraction),
            )
        )
        break
    return prefix


def _draw_polyline(
    draw: _ScaledDraw,
    points: Sequence[tuple[float, float]],
    reveal: float,
    *,
    fill,
    width: int = 2,
) -> list[tuple[float, float]]:
    prefix = _polyline_prefix(points, reveal)
    if len(prefix) >= 2:
        draw.line(prefix, fill=fill, width=width, joint="curve")
    return prefix


def _draw_arrow(
    draw: _ScaledDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    reveal: float,
    *,
    fill,
    width: int = 2,
) -> None:
    prefix = _draw_polyline(
        draw,
        (start, end),
        reveal,
        fill=fill,
        width=width,
    )
    if len(prefix) < 2 or reveal < 0.2:
        return
    tip = prefix[-1]
    previous = prefix[-2]
    angle = math.atan2(tip[1] - previous[1], tip[0] - previous[0])
    head = 8.0
    spread = 0.55
    draw.polygon(
        (
            tip,
            (
                tip[0] - head * math.cos(angle - spread),
                tip[1] - head * math.sin(angle - spread),
            ),
            (
                tip[0] - head * math.cos(angle + spread),
                tip[1] - head * math.sin(angle + spread),
            ),
        ),
        fill=fill,
    )


def _illustration_surface(
    image: Image.Image,
    *,
    accent: str,
    pale: str,
) -> _ScaledDraw:
    draw = _draw(image)
    draw.rounded_rectangle(
        DOMAIN_ILLUSTRATION_BOX,
        radius=12,
        fill=_rgba(pale, 155),
        outline=_rgba(accent, 70),
        width=1,
    )
    return draw


def _analysis_curve_y(x: float) -> float:
    """Screen-space parabola used by the analysis illustration."""

    u = (float(x) - 1040.0) / 100.0
    value = 0.35 * u * u + 0.90 * u + 0.10
    return 478.0 - 42.0 * value


def _analysis_curve_slope(x: float) -> float:
    """Exact screen-space derivative of :func:`_analysis_curve_y`."""

    u = (float(x) - 1040.0) / 100.0
    return -42.0 * (0.70 * u + 0.90) / 100.0


def _analysis_tangent_y(x: float) -> float:
    contact_y = _analysis_curve_y(ANALYSIS_TANGENT_X)
    slope = _analysis_curve_slope(ANALYSIS_TANGENT_X)
    return contact_y + slope * (float(x) - ANALYSIS_TANGENT_X)


def _illustration_analysis(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    axes = _stage(reveal, 0.00, 0.24)
    _draw_polyline(
        draw,
        ((910, 511), (1161, 511)),
        axes,
        fill=_rgba(INK, 150),
        width=1,
    )
    _draw_polyline(
        draw,
        ((914, 515), (914, 416)),
        axes,
        fill=_rgba(INK, 150),
        width=1,
    )
    curve_points = [
        (x, _analysis_curve_y(x))
        for x in range(920, 1161, 4)
    ]
    curve = _stage(reveal, 0.12, 0.82)
    prefix = _draw_polyline(
        draw,
        curve_points,
        curve,
        fill=_rgba(accent),
        width=3,
    )
    if prefix:
        x, y = prefix[-1]
        draw.ellipse(
            (x - 3, y - 3, x + 3, y + 3),
            fill=_rgba(accent),
        )
    tangent = _stage(reveal, 0.64, 1.00)
    tangent_points = (
        (978, _analysis_tangent_y(978)),
        (1148, _analysis_tangent_y(1148)),
    )
    _draw_polyline(
        draw,
        tangent_points,
        tangent,
        fill=_rgba(GOLD),
        width=3,
    )
    contact_y = _analysis_curve_y(ANALYSIS_TANGENT_X)
    draw.ellipse(
        (
            ANALYSIS_TANGENT_X - 5,
            contact_y - 5,
            ANALYSIS_TANGENT_X + 5,
            contact_y + 5,
        ),
        fill=_rgba(accent, round(255 * tangent)),
    )
    _text(
        draw,
        (1134, 402),
        "f(x)",
        12,
        fill=accent,
        bold=True,
        opacity=tangent,
    )
    _text(
        draw,
        (1110, 455),
        "tangente",
        11,
        fill=GOLD,
        bold=True,
        opacity=tangent,
    )


def _illustration_algebra(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    _text(
        draw,
        (913, 447),
        "ℤ / 3ℤ\naddition",
        12,
        fill=INK,
        bold=True,
        spacing=3,
        opacity=_stage(reveal, 0.00, 0.28),
    )
    table_x, table_y, cell = 1024, 416, 25
    grid = _stage(reveal, 0.05, 0.42)
    for index in range(5):
        x = table_x + index * cell
        y = table_y + index * cell
        draw.line(
            (x, table_y, x, table_y + 4 * cell),
            fill=_rgba(INK, round(115 * grid)),
            width=1,
        )
        draw.line(
            (table_x, y, table_x + 4 * cell, y),
            fill=_rgba(INK, round(115 * grid)),
            width=1,
        )
    values = (("+", "0", "1", "2"),) + tuple(
        (str(row), *(str(value) for value in table_row))
        for row, table_row in enumerate(ALGEBRA_TABLE)
    )
    for row, cells in enumerate(values):
        row_reveal = _stage(reveal, 0.20 + row * 0.13, 0.58 + row * 0.13)
        for column, value in enumerate(cells):
            if row == 0 or column == 0:
                draw.rounded_rectangle(
                    (
                        table_x + column * cell + 2,
                        table_y + row * cell + 2,
                        table_x + (column + 1) * cell - 2,
                        table_y + (row + 1) * cell - 2,
                    ),
                    radius=4,
                    fill=_rgba(accent, round(42 * row_reveal)),
                )
            _text(
                draw,
                (
                    table_x + (column + 0.5) * cell,
                    table_y + (row + 0.5) * cell,
                ),
                value,
                12,
                fill=accent if row == 0 or column == 0 else INK,
                bold=row == 0 or column == 0,
                mono=True,
                anchor="mm",
                opacity=row_reveal,
            )


def _illustration_geometry(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    square = (
        (920, 431),
        (986, 431),
        (986, 505),
        (920, 505),
        (920, 431),
    )
    square_reveal = _stage(reveal, 0.00, 0.38)
    _draw_polyline(
        draw,
        square,
        square_reveal,
        fill=_rgba(accent),
        width=3,
    )
    arrow_reveal = _stage(reveal, 0.28, 0.62)
    _draw_arrow(
        draw,
        (1007, 468),
        (1062, 468),
        arrow_reveal,
        fill=_rgba(INK, 175),
        width=2,
    )
    circle = [
        (
            1114 + 42 * math.cos(-math.pi / 2 + step * math.pi / 16),
            468 + 42 * math.sin(-math.pi / 2 + step * math.pi / 16),
        )
        for step in range(33)
    ]
    circle_reveal = _stage(reveal, 0.50, 0.94)
    _draw_polyline(
        draw,
        circle,
        circle_reveal,
        fill=_rgba(accent),
        width=3,
    )
    points_reveal = _stage(reveal, 0.72, 1.00)
    corresponding = (
        (920, 431),
        (986, 431),
        (986, 505),
        (920, 505),
        (1114, 426),
        (1156, 468),
        (1114, 510),
        (1072, 468),
    )
    for x, y in corresponding:
        draw.ellipse(
            (x - 4, y - 4, x + 4, y + 4),
            fill=_rgba(INK, round(225 * points_reveal)),
        )


def _illustration_collection(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    population_reveal = _stage(reveal, 0.00, 0.30)
    population = [
        (914 + column * 18, 429 + row * 24)
        for row in range(4)
        for column in range(6)
    ]
    selected = {1, 6, 10, 15, 20, 23}
    for index, (x, y) in enumerate(population):
        draw.ellipse(
            (x - 3, y - 3, x + 3, y + 3),
            fill=_rgba(INK, round(110 * population_reveal)),
        )
        if index in selected:
            selected_reveal = _stage(
                reveal,
                0.20 + (index % 4) * 0.04,
                0.52 + (index % 4) * 0.04,
            )
            draw.ellipse(
                (x - 6, y - 6, x + 6, y + 6),
                outline=_rgba(accent, round(255 * selected_reveal)),
                width=2,
            )
    _draw_arrow(
        draw,
        (1020, 469),
        (1063, 469),
        _stage(reveal, 0.42, 0.72),
        fill=_rgba(INK, 175),
        width=2,
    )
    groups_reveal = _stage(reveal, 0.62, 1.00)
    for label, top in (("A", 423), ("B", 477)):
        draw.rounded_rectangle(
            (1082, top, 1158, top + 39),
            radius=8,
            fill=_rgba(SURFACE, round(245 * groups_reveal)),
            outline=_rgba(accent, round(125 * groups_reveal)),
            width=1,
        )
        _text(
            draw,
            (1094, top + 19),
            label,
            12,
            fill=accent,
            bold=True,
            anchor="lm",
            opacity=groups_reveal,
        )
        for offset in range(3):
            x = 1120 + offset * 12
            draw.ellipse(
                (x - 3, top + 16, x + 3, top + 22),
                fill=_rgba(INK, round(170 * groups_reveal)),
            )


def _illustration_models(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    axes = _stage(reveal, 0.00, 0.22)
    draw.line(
        (914, 514, 1158, 514),
        fill=_rgba(INK, round(145 * axes)),
        width=1,
    )
    draw.line(
        (914, 514, 914, 417),
        fill=_rgba(INK, round(145 * axes)),
        width=1,
    )
    band_reveal = _stage(reveal, 0.46, 0.78)
    draw.polygon(
        (
            (923, 492),
            (1150, 427),
            (1150, 452),
            (923, 514),
        ),
        fill=_rgba(accent, round(42 * band_reveal)),
    )
    points = (
        (930, 496),
        (949, 482),
        (970, 493),
        (993, 465),
        (1017, 472),
        (1038, 451),
        (1064, 458),
        (1087, 434),
        (1112, 445),
        (1139, 425),
    )
    for index, (x, y) in enumerate(points):
        point_reveal = _stage(
            reveal,
            0.10 + index * 0.025,
            0.40 + index * 0.025,
        )
        draw.ellipse(
            (x - 4, y - 4, x + 4, y + 4),
            fill=_rgba(INK, round(190 * point_reveal)),
            outline=_rgba(accent, round(255 * point_reveal)),
            width=1,
        )
    _draw_polyline(
        draw,
        ((923, 504), (1150, 437)),
        _stage(reveal, 0.52, 1.00),
        fill=_rgba(accent),
        width=3,
    )


def _illustration_advanced(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    panels = ((899, 413, 982, 523), (994, 413, 1077, 523), (1089, 413, 1172, 523))
    stages = (
        _stage(reveal, 0.00, 0.45),
        _stage(reveal, 0.28, 0.73),
        _stage(reveal, 0.56, 1.00),
    )
    for box, panel_reveal in zip(panels, stages):
        draw.rounded_rectangle(
            box,
            radius=8,
            fill=_rgba(SURFACE, round(225 * panel_reveal)),
            outline=_rgba(accent, round(85 * panel_reveal)),
            width=1,
        )

    survival = stages[0]
    draw.line(
        (908, 487, 973, 487),
        fill=_rgba(INK, round(120 * survival)),
        width=1,
    )
    draw.line(
        (908, 487, 908, 428),
        fill=_rgba(INK, round(120 * survival)),
        width=1,
    )
    _draw_polyline(
        draw,
        ((910, 438), (929, 438), (929, 451), (950, 451), (950, 469), (972, 469)),
        survival,
        fill=_rgba(accent),
        width=2,
    )
    _draw_polyline(
        draw,
        ((910, 445), (923, 445), (923, 462), (943, 462), (943, 478), (972, 478)),
        survival,
        fill=_rgba(INK, 175),
        width=2,
    )
    _text(
        draw,
        (940, 507),
        "BIOSTAT.",
        9,
        fill=INK,
        bold=True,
        anchor="mm",
        opacity=survival,
    )

    matrix = stages[1]
    matrix_values = ((0.30, 0.55, 0.80), (0.65, 0.90, 0.45), (0.85, 0.40, 0.70))
    for row, values in enumerate(matrix_values):
        for column, value in enumerate(values):
            draw.rounded_rectangle(
                (
                    1011 + column * 17,
                    433 + row * 17,
                    1025 + column * 17,
                    447 + row * 17,
                ),
                radius=3,
                fill=_rgba(accent, round(190 * value * matrix)),
                outline=_rgba(INK, round(55 * matrix)),
                width=1,
            )
    _text(
        draw,
        (1035, 507),
        "CALCUL",
        9,
        fill=INK,
        bold=True,
        anchor="mm",
        opacity=matrix,
    )

    learning = stages[2]
    for x, y in ((1102, 451), (1112, 438), (1118, 460), (1143, 477), (1152, 461), (1158, 485)):
        draw.ellipse(
            (x - 3, y - 3, x + 3, y + 3),
            fill=_rgba(accent if x < 1130 else INK, round(210 * learning)),
        )
    _draw_polyline(
        draw,
        ((1138, 427), (1126, 491)),
        learning,
        fill=_rgba(INK, 185),
        width=2,
    )
    _text(
        draw,
        (1131, 507),
        "APPRENT.",
        9,
        fill=INK,
        bold=True,
        anchor="mm",
        opacity=learning,
    )


def _illustration_programming(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    labels = ("1 · LIRE", "2 · TRAITER", "3 · PRODUIRE")
    centers = (431, 467, 503)
    draw.line(
        (915, centers[0], 915, centers[-1]),
        fill=_rgba(INK, 125),
        width=2,
    )
    for index, (label, center) in enumerate(zip(labels, centers)):
        step_reveal = _stage(reveal, index * 0.20, 0.42 + index * 0.20)
        draw.rounded_rectangle(
            (932, center - 13, 1157, center + 13),
            radius=7,
            fill=_rgba(SURFACE, round(240 * step_reveal)),
            outline=_rgba(accent, round(125 * step_reveal)),
            width=1,
        )
        _text(
            draw,
            (950, center),
            label,
            11,
            fill=INK,
            bold=True,
            anchor="lm",
            opacity=step_reveal,
        )
    cursor_y = lerp(centers[0], centers[-1], ease(reveal))
    draw.ellipse(
        (909, cursor_y - 6, 921, cursor_y + 6),
        fill=_rgba(accent),
        outline=_rgba(SURFACE),
        width=2,
    )


def _draw_array(
    draw: _ScaledDraw,
    values: Sequence[int],
    *,
    x: float,
    y: float,
    cell: float,
    accent: str,
    opacity: float,
    highlighted: set[int] | None = None,
) -> None:
    highlighted = highlighted or set()
    for index, value in enumerate(values):
        draw.rounded_rectangle(
            (x + index * cell, y, x + (index + 1) * cell - 3, y + 31),
            radius=6,
            fill=_rgba(accent, round((48 if index in highlighted else 18) * opacity)),
            outline=_rgba(accent, round((210 if index in highlighted else 105) * opacity)),
            width=2 if index in highlighted else 1,
        )
        _text(
            draw,
            (x + index * cell + (cell - 3) / 2, y + 15),
            str(value),
            12,
            fill=INK,
            bold=True,
            mono=True,
            anchor="mm",
            opacity=opacity,
        )


def _illustration_algorithms(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    source = _stage(reveal, 0.00, 0.30)
    _text(
        draw,
        (909, 429),
        "ENTRÉE",
        9,
        fill=INK,
        bold=True,
        opacity=source,
    )
    _draw_array(
        draw,
        ALGORITHM_INPUT,
        x=909,
        y=446,
        cell=28,
        accent=accent,
        opacity=source,
        highlighted={0, 3},
    )
    arrow = _stage(reveal, 0.28, 0.68)
    _draw_arrow(
        draw,
        (1025, 461),
        (1051, 461),
        arrow,
        fill=_rgba(INK, 175),
        width=2,
    )
    result = _stage(reveal, 0.54, 1.00)
    _text(
        draw,
        (1059, 429),
        "TRIÉE",
        9,
        fill=INK,
        bold=True,
        opacity=result,
    )
    _draw_array(
        draw,
        ALGORITHM_OUTPUT,
        x=1059,
        y=446,
        cell=26,
        accent=accent,
        opacity=result,
    )
    _text(
        draw,
        (1035, 505),
        "comparaison · échange · ordre",
        10,
        fill=INK,
        anchor="mm",
        opacity=_stage(reveal, 0.70, 1.00),
    )


def _illustration_systems(
    image: Image.Image,
    accent: str,
    pale: str,
    reveal: float,
) -> None:
    draw = _illustration_surface(image, accent=accent, pale=pale)
    centers = (430, 468, 506)
    draw.line(
        (914, centers[0], 914, centers[-1]),
        fill=_rgba(INK, 115),
        width=2,
    )
    for index, (label, center) in enumerate(zip(SYSTEM_LAYERS, centers)):
        layer_reveal = _stage(reveal, index * 0.18, 0.46 + index * 0.18)
        draw.rounded_rectangle(
            (934, center - 13, 1158, center + 13),
            radius=7,
            fill=_rgba(SURFACE, round(240 * layer_reveal)),
            outline=_rgba(accent, round(130 * layer_reveal)),
            width=1,
        )
        _text(
            draw,
            (1046, center),
            label,
            11,
            fill=INK,
            bold=True,
            anchor="mm",
            opacity=layer_reveal,
        )
    request_y = lerp(centers[0], centers[-1], ease(reveal))
    draw.ellipse(
        (908, request_y - 6, 920, request_y + 6),
        fill=_rgba(accent),
        outline=_rgba(SURFACE),
        width=2,
    )


DomainIllustrator = Callable[[Image.Image, str, str, float], None]

DOMAIN_ILLUSTRATORS: dict[tuple[str, str], DomainIllustrator] = {
    ("v4_06_fundamental_mathematics", "analysis"): _illustration_analysis,
    ("v4_06_fundamental_mathematics", "algebra"): _illustration_algebra,
    ("v4_06_fundamental_mathematics", "geometry"): _illustration_geometry,
    ("v4_07_statistics", "collection"): _illustration_collection,
    ("v4_07_statistics", "models"): _illustration_models,
    ("v4_07_statistics", "advanced"): _illustration_advanced,
    ("v4_08_mathematics_computing", "programming"): _illustration_programming,
    ("v4_08_mathematics_computing", "algorithms"): _illustration_algorithms,
    ("v4_08_mathematics_computing", "systems"): _illustration_systems,
}


def _draw_domain_illustration(
    scene_id: str,
    segment_id: str,
    *,
    accent: str,
    pale: str,
    reveal: float,
) -> Image.Image:
    key = (scene_id, segment_id)
    try:
        illustrator = DOMAIN_ILLUSTRATORS[key]
    except KeyError as exc:
        raise KeyError(f"Missing domain illustration for {key!r}") from exc
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    illustrator(layer, accent, pale, clamp(reveal))
    return layer


def _draw_branch_scene(
    scene_id: str,
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    if scene_id == "v4_06_fundamental_mathematics":
        accent, pale = MATH, PALE_MATH
    elif scene_id == "v4_07_statistics":
        accent, pale = STATISTICS, PALE_STATISTICS
    else:
        accent, pale = COMPUTING, PALE_COMPUTING
    spec = SCENE_BY_ID[scene_id]
    _scene_title(
        image,
        spec.title,
        spec.subtitle,
        accent=accent,
    )
    _pathway_label(image)
    segments = BRANCH_SEGMENTS[scene_id]
    action_names = [segment.action for segment in segments]
    weights = _phased_segment_weights(actions, action_names, t)
    skeleton_reveal = progress(actions, action_names[0], t)
    _draw_map_skeleton(image, accent=accent, reveal=skeleton_reveal)
    for segment, weight in zip(segments, weights):
        _draw_course_placements(
            image,
            segment,
            accent=accent,
            pale=pale,
            opacity=weight,
        )
    _rounded_card(
        image,
        (852, 160, 1219, 592),
        fill=SURFACE,
        outline=pale,
        rail=accent,
        opacity=skeleton_reveal,
    )
    for segment, weight in zip(segments, weights):
        if weight <= 0:
            continue
        layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = _draw(layer)
        _text(
            draw,
            (887, 194),
            "DOMAINE PRÉSENTÉ",
            12,
            fill=MUTED,
            bold=True,
        )
        wrapped_heading = _wrap(draw, segment.heading, 25, 284, bold=True)
        _text(
            draw,
            (887, 228),
            wrapped_heading,
            25,
            fill=accent,
            bold=True,
            spacing=4,
        )
        wrapped_description = _wrap(
            draw,
            segment.description,
            17,
            282,
        )
        heading_lines = wrapped_heading.count("\n") + 1
        description_y = 278 + (heading_lines - 1) * 30
        _text(
            draw,
            (887, description_y),
            wrapped_description,
            17,
            fill=INK,
            spacing=6,
        )
        transition_reveal = (
            raw_progress(actions, "show_profiles_transition", t)
            if scene_id == "v4_08_mathematics_computing"
            else 0.0
        )
        illustration_exit = _stage(transition_reveal, 0.0, 0.5)
        profile_enter = _stage(transition_reveal, 0.5, 1.0)
        illustration = _draw_domain_illustration(
            scene_id,
            segment.id,
            accent=accent,
            pale=pale,
            reveal=raw_progress(actions, segment.action, t),
        )
        _composite(layer, illustration, 1.0 - illustration_exit)
        if scene_id == "v4_08_mathematics_computing" and profile_enter > 0:
            profile_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
            profile_draw = _draw(profile_layer)
            profile_draw.line(
                (887, 436, 1184, 436),
                fill=_rgba(pale),
                width=2,
            )
            _text(
                profile_draw,
                (887, 453),
                "DEUX PROFILS À PARTIR DU MÊME NOYAU",
                11,
                fill=MUTED,
                bold=True,
            )
            _pill(
                profile_layer,
                (887, 488, 1184, 525),
                "Profil mathématiques  ·  Profil statistique",
                fill=pale,
                text_fill=accent,
                size=13,
            )
            _composite(layer, profile_layer, profile_enter)
        _text(
            draw,
            (887, 569),
            "Cours représentatifs · grille complète dans le guide",
            11,
            fill=MUTED,
        )
        _composite(image, layer, weight)
    return image


def _profile_column(
    image: Image.Image,
    box: tuple[int, int, int, int],
    *,
    accent: str,
    pale: str,
    heading: str,
    focus: str,
    characteristic_courses: str,
    advanced_courses: str,
    reveal: float,
    details_reveal: float,
) -> None:
    _rounded_card(
        image,
        box,
        fill=SURFACE,
        outline=pale,
        rail=accent,
        opacity=reveal,
    )
    draw = _draw(image)
    _text(
        draw,
        (box[0] + 38, box[1] + 34),
        heading,
        24,
        fill=accent,
        bold=True,
        opacity=reveal,
    )
    rows = (
        ("ORIENTATION", focus),
        ("COURS CARACTÉRISTIQUES", characteristic_courses),
        ("APPROFONDISSEMENTS", advanced_courses),
    )
    for index, (label, value) in enumerate(rows):
        y = box[1] + 104 + index * 119
        row_reveal = reveal * ease(
            clamp(details_reveal * len(rows) - index)
        )
        draw.rounded_rectangle(
            (box[0] + 34, y, box[2] - 28, y + 94),
            radius=12,
            fill=_rgba(pale, round(255 * row_reveal)),
        )
        _text(
            draw,
            (box[0] + 54, y + 14),
            label,
            11,
            fill=accent,
            bold=True,
            opacity=row_reveal,
        )
        wrapped = _wrap(
            draw,
            value,
            15,
            box[2] - box[0] - 110,
            bold=index == 0,
        )
        _text(
            draw,
            (box[0] + 54, y + 42),
            wrapped,
            15,
            fill=INK,
            bold=index == 0,
            spacing=3,
            opacity=row_reveal,
        )


def _draw_profiles(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    spec = SCENE_BY_ID["v4_09_computing_profiles"]
    _scene_title(
        image,
        spec.title,
        spec.subtitle,
        accent=COMPUTING,
    )
    math_reveal = progress(actions, "show_math_profile", t)
    statistics_reveal = progress(
        actions,
        "show_statistics_profile",
        t,
    )
    math_details = raw_progress(actions, "show_math_details", t)
    statistics_details = raw_progress(
        actions,
        "show_statistics_details",
        t,
    )
    _profile_column(
        image,
        (66, 146, 620, 589),
        accent=MATH,
        pale=PALE_MATH,
        heading="Profil mathématiques",
        focus="Structures théoriques",
        characteristic_courses=(
            "Théorie des groupes · Théorie des anneaux"
        ),
        advanced_courses="Spécialisation en mathématiques",
        reveal=math_reveal,
        details_reveal=math_details,
    )
    _profile_column(
        image,
        (660, 146, 1214, 589),
        accent=STATISTICS,
        pale=PALE_STATISTICS,
        heading="Profil statistique\n(science des données)",
        focus="Modélisation et science des données",
        characteristic_courses="Statistique II · Régression",
        advanced_courses=(
            "Statistique informatique · Apprentissage statistique"
        ),
        reveal=statistics_reveal,
        details_reveal=statistics_details,
    )
    orientation_note = progress(actions, "show_orientation_note", t)
    common_note = progress(actions, "show_common_note", t)
    _reveal_text(
        image,
        "Le profil choisi détermine l’orientation disciplinaire du cheminement.",
        (640, 631),
        17,
        orientation_note * (1.0 - common_note),
        fill=INK,
        bold=True,
        anchor="ma",
    )
    _reveal_text(
        image,
        "Le noyau informatique demeure commun aux deux profils.",
        (640, 631),
        18,
        common_note,
        fill=COMPUTING,
        bold=True,
        anchor="ma",
    )
    return image


def _comparison_card(
    image: Image.Image,
    box: tuple[int, int, int, int],
    *,
    accent: str,
    pale: str,
    heading: str,
    object_text: str,
    tools_text: str,
    reveal: float,
    object_reveal: float,
    tools_reveal: float,
) -> None:
    _rounded_card(
        image,
        box,
        fill=SURFACE,
        outline=pale,
        rail=accent,
        opacity=reveal,
    )
    draw = _draw(image)
    _text(
        draw,
        ((box[0] + box[2]) / 2, box[1] + 62),
        heading,
        20,
        fill=accent,
        bold=True,
        anchor="mm",
        align="center",
        spacing=3,
        opacity=reveal,
    )
    sections = (
        ("OBJETS D’ÉTUDE", object_text, object_reveal),
        ("OUTILS PRIVILÉGIÉS", tools_text, tools_reveal),
    )
    for index, (label, value, section_reveal) in enumerate(sections):
        y = box[1] + 119 + index * 136
        opacity = reveal * section_reveal
        draw.rounded_rectangle(
            (box[0] + 29, y, box[2] - 24, y + 112),
            radius=12,
            fill=_rgba(pale, round(255 * opacity)),
        )
        _text(
            draw,
            (box[0] + 48, y + 16),
            label,
            11,
            fill=accent,
            bold=True,
            opacity=opacity,
        )
        wrapped = _wrap(
            draw,
            value,
            16,
            box[2] - box[0] - 96,
            bold=True,
        )
        _text(
            draw,
            (box[0] + 48, y + 48),
            wrapped,
            16,
            fill=INK,
            bold=True,
            spacing=3,
            opacity=opacity,
        )


def _draw_comparison(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    spec = SCENE_BY_ID["v4_10_comparison"]
    _scene_title(
        image,
        spec.title,
        spec.subtitle,
        accent=NAVY,
    )
    objects = progress(actions, "show_objects", t)
    tools = progress(actions, "show_tools", t)
    cards = (
        (
            "show_math",
            (54, 145, 432, 583),
            MATH,
            PALE_MATH,
            _concentration_card_title(image, "math", 20, 318),
            "Théorie et structures",
            "Démonstration · abstraction",
        ),
        (
            "show_statistics",
            (451, 145, 829, 583),
            STATISTICS,
            PALE_STATISTICS,
            _concentration_card_title(image, "stat", 20, 318),
            "Données · modèles · incertitude",
            "Inférence · calcul statistique",
        ),
        (
            "show_computing",
            (848, 145, 1226, 583),
            COMPUTING,
            PALE_COMPUTING,
            _concentration_card_title(image, "info_math", 20, 318),
            "Programmation · algorithmes · systèmes",
            "Conception · mise en œuvre",
        ),
    )
    for action, box, accent, pale, heading, object_text, tools_text in cards:
        _comparison_card(
            image,
            box,
            accent=accent,
            pale=pale,
            heading=heading,
            object_text=object_text,
            tools_text=tools_text,
            reveal=progress(actions, action, t),
            object_reveal=objects,
            tools_reveal=tools,
        )
    note = progress(actions, "show_comparison_note", t)
    _reveal_text(
        image,
        "Ainsi, le choix de la concentration dépend de ce que l’on souhaite étudier\n"
        "et des méthodes que l’on souhaite maîtriser.",
        (640, 604),
        17,
        note,
        fill=INK,
        bold=True,
        anchor="ma",
        align="center",
    )
    return image


def _draw_guide(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    image = _new_canvas()
    _brand(image)
    cover_reveal = progress(actions, "show_guide", t)
    cover_box = (88, 116, 422, 632)
    shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = _draw(shadow_layer)
    shadow_draw.rounded_rectangle(
        (
            cover_box[0] + 3,
            cover_box[1] + 7,
            cover_box[2] + 3,
            cover_box[3] + 9,
        ),
        radius=14,
        fill=_rgba(SHADOW, 24),
    )
    shadow_layer = shadow_layer.filter(
        ImageFilter.GaussianBlur(8 * RENDER_SCALE)
    )
    _composite(image, shadow_layer, cover_reveal)
    cover = guide_cover().copy()
    cover.thumbnail(
        (
            _scaled(cover_box[2] - cover_box[0]),
            _scaled(cover_box[3] - cover_box[1]),
        ),
        Image.Resampling.LANCZOS,
    )
    cover_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    x = round(
        (_scaled(cover_box[0]) + _scaled(cover_box[2]) - cover.width) / 2
    )
    y = _scaled(cover_box[1])
    cover_layer.alpha_composite(cover, (x, y))
    _composite(image, cover_layer, cover_reveal)
    title_reveal = progress(actions, "show_guide_title", t)
    _reveal_text(
        image,
        "Consulter le guide officiel",
        (506, 137),
        35,
        title_reveal,
        bold=True,
    )
    _reveal_text(
        image,
        "Guide de la personne étudiante\nMathématiques et statistique",
        (506, 199),
        20,
        title_reveal,
        fill=STATISTICS,
        bold=True,
        spacing=5,
    )
    details = (
        (
            "show_loads",
            "Rythmes de quatre ou cinq cours par session",
        ),
        (
            "show_starts",
            "Départs possibles à l’automne ou à l’hiver",
        ),
        (
            "show_prerequisites",
            "Cours, préalables, options et cheminements détaillés",
        ),
    )
    draw = _draw(image)
    for index, (action, label) in enumerate(details):
        reveal = progress(actions, action, t)
        y = 331 + index * 73
        draw.ellipse(
            (510, y + 5, 523, y + 18),
            fill=_rgba(STATISTICS, round(255 * reveal)),
        )
        _reveal_text(
            image,
            label,
            (546, y),
            18,
            reveal,
            fill=INK,
            rise=6,
        )
    url_reveal = progress(actions, "show_url", t)
    _reveal_text(
        image,
        "math.uqam.ca",
        (506, 570),
        29,
        url_reveal,
        fill=INK,
        bold=True,
    )
    if url_reveal > 0:
        draw = _draw(image)
        draw.rounded_rectangle(
            (506, 612, 702, 617),
            radius=2,
            fill=_rgba(STATISTICS, round(255 * url_reveal)),
        )
    return image


def _draw_conclusion(
    t: float,
    duration: float,
    actions: Mapping[str, ActionWindow],
) -> Image.Image:
    """Draw an institutional closing card with the approved local logo."""

    image = Image.new("RGBA", (WIDTH, HEIGHT), _rgba(NAVY))
    draw = _draw(image)
    logo_reveal = progress(actions, "show_logo", t)
    world_reveal = progress(actions, "show_world", t)
    future_reveal = progress(actions, "show_future", t)
    url_reveal = progress(actions, "show_url", t)

    logo = official_logo().copy()
    logo.thumbnail(
        (_scaled(CONCLUSION_LOGO_WIDTH), _scaled(124)),
        Image.Resampling.LANCZOS,
    )
    logo_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    logo_x = round((WIDTH - logo.width) / 2)
    logo_y = _scaled(84)
    logo_layer.alpha_composite(logo, (logo_x, logo_y))
    _composite(image, logo_layer, logo_reveal)

    line_width = 250 * ease(logo_reveal)
    draw.rounded_rectangle(
        (640 - line_width / 2, 257, 640 + line_width / 2, 263),
        radius=3,
        fill=_rgba(STATISTICS, round(255 * logo_reveal)),
    )
    _reveal_text(
        image,
        "Les mathématiques pour comprendre le monde.",
        (640, 324),
        39,
        world_reveal,
        fill=SURFACE,
        bold=True,
        anchor="ma",
        align="center",
        rise=12,
    )
    _reveal_text(
        image,
        "Une formation pour construire votre avenir.",
        (640, 403),
        36,
        future_reveal,
        fill=SURFACE,
        anchor="ma",
        align="center",
        rise=12,
    )
    _reveal_text(
        image,
        "BACCALAURÉAT EN MATHÉMATIQUES",
        (640, 518),
        15,
        future_reveal,
        fill=PALE_STATISTICS,
        bold=True,
        anchor="ma",
        align="center",
        rise=6,
    )
    _reveal_text(
        image,
        "math.uqam.ca",
        (640, 574),
        22,
        url_reveal,
        fill=SURFACE,
        bold=True,
        anchor="ma",
        align="center",
        rise=6,
    )
    return image


DRAWERS = {
    "v4_01_opening": _draw_opening,
    "v4_03_course_load": _draw_course_load,
    "v4_04_complementary_column": _draw_complementary,
    "v4_05_common_to_specialization": _draw_common_to_specialization,
    "v4_06_fundamental_mathematics": _draw_branch_scene,
    "v4_07_statistics": _draw_branch_scene,
    "v4_08_mathematics_computing": _draw_branch_scene,
    "v4_09_computing_profiles": _draw_profiles,
    "v4_10_comparison": _draw_comparison,
    "v4_11_guide": _draw_guide,
    "v4_12_conclusion": _draw_conclusion,
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
    """Draw one V4 frame as an RGB ``uint8`` numpy array."""

    if scene_id not in DRAWERS:
        valid = ", ".join(DRAWERS)
        raise KeyError(f"Unknown V4 scene {scene_id!r}. Expected: {valid}")
    scene_duration = (
        SCENE_DURATIONS[scene_id] if duration is None else float(duration)
    )
    if scene_duration <= 0:
        raise ValueError("duration must be positive.")
    local_t = clamp(float(t), 0.0, scene_duration)
    actions = normalise_actions(scene_id, cue_times_or_actions)
    drawer = DRAWERS[scene_id]
    if scene_id in BRANCH_SEGMENTS:
        image = drawer(scene_id, local_t, scene_duration, actions)
    else:
        image = drawer(local_t, scene_duration, actions)
    flattened = Image.new("RGBA", image.size, _rgba(BACKGROUND))
    flattened.alpha_composite(image)
    return v4_photos.composite(scene_id, local_t, np.asarray(flattened.convert("RGB"), dtype=np.uint8), actions)


__all__ = [
    "ALGEBRA_MODULUS",
    "ALGEBRA_TABLE",
    "ALGORITHM_INPUT",
    "ALGORITHM_OUTPUT",
    "ANALYSIS_TANGENT_X",
    "ActionWindow",
    "BASE_FPS",
    "BASE_HEIGHT",
    "BASE_WIDTH",
    "DEFAULT_ACTIONS",
    "DOMAIN_ILLUSTRATION_BOX",
    "CONCLUSION_LOGO_WIDTH",
    "DOMAIN_ILLUSTRATORS",
    "DRAWERS",
    "FPS",
    "HEIGHT",
    "SCENE_DURATIONS",
    "SYSTEM_LAYERS",
    "WIDTH",
    "configure_output",
    "draw_scene",
    "normalise_actions",
]
