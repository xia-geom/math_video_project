#!/usr/bin/env python3
"""Render the audited, low-density UQAM program-introduction prototype.

The source tables are reconstructed as editable objects.  Every scene keeps the
complete pathway visible as a quiet map, while only a few relevant cells receive
text.  This avoids turning the video into a timetable-reading exercise.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import html
import importlib.metadata
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import tomllib
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Callable, Iterable

# Keep MoviePy on the same checked FFmpeg binary recorded by the manifest.
if system_ffmpeg := shutil.which("ffmpeg"):
    os.environ.setdefault("IMAGEIO_FFMPEG_EXE", system_ffmpeg)

import numpy as np
from moviepy import AudioFileClip, VideoClip
from PIL import Image, ImageDraw, ImageFont
from program_data import COMMON_FOUNDATION, INFO_THEMES, PROGRAMS
from pydub import AudioSegment
from theme import CATEGORY_STYLE, COLORS, PROGRAM_ACCENTS

ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "project-manifest.toml"


def load_project_manifest(path: Path = MANIFEST_PATH) -> dict:
    with path.open("rb") as handle:
        manifest = tomllib.load(handle)
    if manifest.get("schema_version") != 1:
        raise RuntimeError(f"Unsupported project manifest schema in {path}")
    required_sections = {
        "project", "pathway", "source", "identity", "fonts",
        "narration", "render", "artifacts", "toolchain",
    }
    missing = sorted(required_sections - manifest.keys())
    if missing:
        raise RuntimeError(f"Project manifest is missing sections: {', '.join(missing)}")
    return manifest


MANIFEST = load_project_manifest()
ASSETS = ROOT / "assets"
BUILD_DIR = ROOT / MANIFEST["artifacts"]["build_dir"]
DIST_DIR = ROOT / MANIFEST["artifacts"]["dist_dir"]
VOICE_DIR = BUILD_DIR / "audio"
SCENE_DIR = BUILD_DIR / "scenes"
TABLE_DIR = DIST_DIR / "tables"
NARRATION_PATH = ROOT / MANIFEST["narration"]["source"]
IDENTITY_PNG = ROOT / MANIFEST["identity"]["png"]
IDENTITY_SVG = ROOT / MANIFEST["identity"]["svg"]
FONT_REGULAR = ROOT / MANIFEST["fonts"]["regular"]
FONT_BOLD = ROOT / MANIFEST["fonts"]["bold"]
FONT_MONO = ROOT / MANIFEST["fonts"]["mono"]

WIDTH = int(MANIFEST["render"]["width"])
HEIGHT = int(MANIFEST["render"]["height"])
FPS = int(MANIFEST["render"]["fps"])
AZURE_VOICE = os.getenv("MANIM_VOICE", MANIFEST["narration"]["voice"])
AZURE_RATE = MANIFEST["narration"]["rate"]
TARGET_SPEECH_DBFS = float(MANIFEST["narration"]["target_dbfs"])
LEAD_SILENCE_MS = int(MANIFEST["narration"]["lead_silence_ms"])
TAIL_SILENCE_MS = int(MANIFEST["narration"]["tail_silence_ms"])
PATHWAY_LABEL = MANIFEST["pathway"]["display_label"]
SOURCE_YEAR_SLUG = MANIFEST["project"]["source_year"].replace("–", "-")
ARTIFACT_STEM = MANIFEST["artifacts"]["stem_template"].format(
    source_year=SOURCE_YEAR_SLUG
)


@dataclass(frozen=True)
class Narration:
    scene_id: str
    cues: tuple[str, ...]

    @property
    def text(self) -> str:
        return " ".join(self.cues)

    @property
    def digest(self) -> str:
        canonical = json.dumps(
            {"scene_id": self.scene_id, "cues": list(self.cues)},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class Scene:
    scene_id: str
    program_key: str
    title: str
    phrase: str
    narration: Narration
    visual: str
    highlight: list[tuple[int, int]]
    labels: list[tuple[int, int]]
    duration: float = 0.0
    audio_path: Path | None = None

    @property
    def transcript(self) -> str:
        return self.narration.text


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_scene_ids() -> tuple[str, ...]:
    return (
        "01_intro",
        *(f"02_math_{theme['id']}" for theme in PROGRAMS["math"]["themes"]),
        *(f"03_stat_{theme['id']}" for theme in PROGRAMS["stat"]["themes"]),
        *(f"04_info_{theme['id']}" for theme in INFO_THEMES),
        "05_closing",
    )


def wrap_subtitle(cue: str, width: int = 42) -> tuple[str, ...]:
    lines = tuple(
        textwrap.wrap(
            cue,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )
    if not lines or len(lines) > 2:
        raise ValueError(
            f"Subtitle cue must fit on at most two {width}-character lines: {cue!r}"
        )
    return lines


def load_narration(path: Path = NARRATION_PATH) -> dict[str, Narration]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    header_pattern = re.compile(r"^\[([a-z0-9_]+)\]$")

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line:
            continue
        match = header_pattern.fullmatch(line)
        if match:
            current = match.group(1)
            if current in sections:
                raise ValueError(
                    f"Duplicate narration section [{current}] at line {line_number}"
                )
            sections[current] = []
            continue
        if current is None:
            raise ValueError(
                f"Narration text before the first section at line {line_number}"
            )
        if not line.endswith((".", "?", "!", "…")):
            raise ValueError(
                f"Narration cue must end in sentence punctuation at line {line_number}"
            )
        wrap_subtitle(line)
        sections[current].append(line)

    expected = set(expected_scene_ids())
    actual = set(sections)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    empty = sorted(scene_id for scene_id, cues in sections.items() if not cues)
    problems = []
    if missing:
        problems.append(f"missing: {', '.join(missing)}")
    if unknown:
        problems.append(f"unknown: {', '.join(unknown)}")
    if empty:
        problems.append(f"empty: {', '.join(empty)}")
    if problems:
        raise ValueError("Invalid narration source (" + "; ".join(problems) + ")")

    return {
        scene_id: Narration(scene_id, tuple(sections[scene_id]))
        for scene_id in expected_scene_ids()
    }


def _version_tuple(value: str) -> tuple[int, ...]:
    match = re.match(r"(\d+(?:\.\d+)*)", value)
    return tuple(int(part) for part in match.group(1).split(".")) if match else ()


def verify_static_assets() -> None:
    checks = [
        (
            ROOT / MANIFEST["source"]["guide"]["path"],
            MANIFEST["source"]["guide"]["sha256"],
            "source guide",
        ),
        (IDENTITY_SVG, MANIFEST["identity"]["svg_sha256"], "official UQAM SVG"),
        (IDENTITY_PNG, MANIFEST["identity"]["png_sha256"], "official UQAM PNG"),
        (FONT_REGULAR, MANIFEST["fonts"]["regular_sha256"], "regular font"),
        (FONT_BOLD, MANIFEST["fonts"]["bold_sha256"], "bold font"),
        (FONT_MONO, MANIFEST["fonts"]["mono_sha256"], "monospace font"),
    ]
    problems = []
    for path, expected_hash, label in checks:
        if not path.is_file():
            problems.append(f"{label} is missing: {path}")
        elif sha256_file(path) != expected_hash:
            problems.append(f"{label} does not match its manifest hash: {path}")
    if problems:
        raise RuntimeError("Asset verification failed:\n- " + "\n- ".join(problems))


def check_environment() -> dict[str, str]:
    problems: list[str] = []
    minimum = _version_tuple(MANIFEST["toolchain"]["python_min"])
    maximum = _version_tuple(MANIFEST["toolchain"]["python_max_exclusive"])
    running_python = sys.version_info[:3]
    if running_python < minimum or running_python >= maximum:
        problems.append(
            "Python "
            f"{MANIFEST['toolchain']['python_min']}–"
            f"{MANIFEST['toolchain']['python_max_exclusive']} (exclusive) is required; "
            f"found {sys.version.split()[0]}"
        )

    versions: dict[str, str] = {"python": sys.version.split()[0]}
    for distribution, expected in MANIFEST["toolchain"]["packages"].items():
        try:
            actual = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            problems.append(f"Python package is missing: {distribution}=={expected}")
            continue
        versions[distribution] = actual
        if actual != expected:
            problems.append(
                f"{distribution} must be {expected}; found {actual}"
            )

    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg:
        problems.append("FFmpeg is missing from PATH")
    if not ffprobe:
        problems.append("ffprobe is missing from PATH")
    if ffmpeg:
        version_result = subprocess.run(
            [ffmpeg, "-version"],
            check=True,
            capture_output=True,
            text=True,
        )
        match = re.search(r"ffmpeg version\s+([^\s]+)", version_result.stdout)
        ffmpeg_version = match.group(1) if match else "unknown"
        versions["ffmpeg"] = ffmpeg_version
        if _version_tuple(ffmpeg_version) < _version_tuple(MANIFEST["toolchain"]["ffmpeg_min"]):
            problems.append(
                f"FFmpeg {MANIFEST['toolchain']['ffmpeg_min']} or newer is required; "
                f"found {ffmpeg_version}"
            )
        encoders = subprocess.run(
            [ffmpeg, "-hide_banner", "-encoders"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        for encoder in (
            MANIFEST["render"]["video_codec"],
            MANIFEST["render"]["audio_codec"],
        ):
            if not re.search(rf"\b{re.escape(encoder)}\b", encoders):
                problems.append(f"FFmpeg encoder is unavailable: {encoder}")

    verify_static_assets()
    load_narration()
    if problems:
        raise RuntimeError(
            "Environment check failed:\n- "
            + "\n- ".join(problems)
            + "\nInstall the pinned requirements and retry."
        )
    return versions


def rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16) for i in (0, 2, 4))


def rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    return (*rgb(value), alpha)


@lru_cache(maxsize=64)
def fnt(size: int, bold: bool = False, mono: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_MONO if mono else (FONT_BOLD if bold else FONT_REGULAR)
    return ImageFont.truetype(str(path), size=size)


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def smooth(x: float) -> float:
    x = clamp(x)
    return x * x * (3 - 2 * x)


def phase(p: float, start: float, end: float) -> float:
    if end <= start:
        return 1.0
    return smooth((p - start) / (end - start))


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if text_size(draw, trial, font)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, size: int, color: str,
                 max_width: int, *, bold: bool = False, anchor: str = "la", alpha: int = 255,
                 line_gap: int | None = None) -> int:
    font = fnt(size, bold=bold)
    lines = wrap(draw, text, font, max_width)
    gap = line_gap or int(size * 1.25)
    x, y = xy
    for i, line in enumerate(lines):
        draw.text((x, y + i * gap), line, font=font, fill=rgba(color, alpha), anchor=anchor)
    return len(lines) * gap


def composite_text(
    image: Image.Image,
    xy: tuple[float, float],
    text: str,
    *,
    font: ImageFont.FreeTypeFont,
    color: str | tuple[int, int, int],
    alpha: int = 255,
    anchor: str | None = None,
) -> None:
    """Alpha-composite antialiased text without degrading the glyph edges."""
    if alpha <= 0:
        return
    probe = ImageDraw.Draw(image)
    bbox = probe.textbbox(xy, text, font=font, anchor=anchor)
    left = max(0, math.floor(bbox[0]) - 2)
    top = max(0, math.floor(bbox[1]) - 2)
    right = min(WIDTH, math.ceil(bbox[2]) + 2)
    bottom = min(HEIGHT, math.ceil(bbox[3]) + 2)
    layer = Image.new("RGBA", (right - left, bottom - top), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    layer_draw.text(
        (xy[0] - left, xy[1] - top),
        text,
        font=font,
        fill=(*rgb(color), alpha) if isinstance(color, str) else (*color, alpha),
        anchor=anchor,
    )
    image.paste(layer, (left, top), layer)


class CompositeImageDraw:
    """Proxy ImageDraw whose text method preserves opacity and antialiasing."""

    def __init__(self, image: Image.Image):
        self.image = image
        self.raw = ImageDraw.Draw(image, "RGBA")

    def __getattr__(self, name: str):
        return getattr(self.raw, name)

    def text(
        self,
        xy: tuple[float, float],
        text: str,
        *,
        font: ImageFont.FreeTypeFont,
        fill: tuple[int, int, int] | tuple[int, int, int, int],
        anchor: str | None = None,
    ) -> None:
        color = tuple(fill[:3])
        alpha = fill[3] if len(fill) == 4 else 255
        composite_text(
            self.image,
            xy,
            text,
            font=font,
            color=color,
            alpha=alpha,
            anchor=anchor,
        )


@lru_cache(maxsize=1)
def base_background() -> Image.Image:
    # Keep the working canvas opaque. Drawing RGBA colors onto an RGB image
    # alpha-composites each reveal correctly; converting a transparent canvas
    # directly to RGB made low-opacity glyphs appear blocky before sharpening.
    image = Image.new("RGB", (WIDTH, HEIGHT), rgb(COLORS["background"]))
    draw = ImageDraw.Draw(image, "RGBA")
    for x in range(0, WIDTH, 80):
        draw.line([(x, 0), (x, HEIGHT)], fill=rgba(COLORS["grid"], 22), width=1)
    for y in range(0, HEIGHT, 80):
        draw.line([(0, y), (WIDTH, y)], fill=rgba(COLORS["grid"], 22), width=1)
    return image


def base_canvas() -> tuple[Image.Image, CompositeImageDraw]:
    image = base_background().copy()
    return image, CompositeImageDraw(image)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str, *, outline: str | None = None,
            radius: int = 16, width: int = 2, alpha: int = 255) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=rgba(fill, alpha),
                           outline=rgba(outline, alpha) if outline else None, width=width)


@lru_cache(maxsize=1)
def official_logo() -> Image.Image:
    logo = Image.open(IDENTITY_PNG).convert("RGBA")
    return logo.resize((115, 38), Image.Resampling.LANCZOS)


def draw_brand(draw: CompositeImageDraw, accent: str) -> None:
    draw.rectangle((0, 0, WIDTH, 82), fill=rgba(COLORS["dark"]))
    logo = official_logo()
    draw.image.paste(logo, (48, 20), logo)
    draw.text(
        (190, 40),
        "Unité de programme en mathématiques et statistique",
        font=fnt(17, bold=True),
        fill=rgba("#FFFFFF"),
        anchor="lm",
    )
    draw.text(
        (WIDTH - 48, 40),
        "FACULTÉ DES SCIENCES",
        font=fnt(13, bold=True),
        fill=rgba("#DDE3E6"),
        anchor="rm",
    )
    draw.rectangle((0, 78, WIDTH, 82), fill=rgba(accent))


def short_course(title: str) -> str:
    replacements = {
        "Introduction à la topologie": "Topologie",
        "Géométrie différentielle": "Géométrie\ndifférentielle",
        "Analyse numérique ou processus stochastiques": "Analyse numérique /\nprocessus stochastiques",
        "Analyse numérique ou probabilités II": "Analyse numérique /\nprobabilités II",
        "Statistique III ou sujets spéciaux": "Statistique III /\nsujets spéciaux",
        "Plans d'expérience et ANOVA": "Plans d'expérience\net ANOVA",
        "Structures de données et algorithmes": "Structures de données\net algorithmes",
        "Bases de données ou systèmes": "Bases de données\nou systèmes",
        "Éthique ou mathématiques dans la société": "Éthique / mathématiques\ndans la société",
        "Introduction à la programmation": "Programmation",
        "INF1120 Programmation I ou INF1035 Informatique pour les sciences": "INF1120 / INF1035",
        "Laboratoire de statistique": "Laboratoire\nde statistique",
        "Statistique informatique": "Statistique\ninformatique",
        "Apprentissage statistique": "Apprentissage\nstatistique",
        "Séminaire de mathématiques": "Séminaire",
        "Algèbre linéaire III": "Algèbre linéaire III",
        "Spécialisation en mathématiques": "Spécialisation\nmathématique",
        "Option mathématiques-statistique": "Option math / stat",
        "Informatique avancée": "Informatique avancée",
    }
    return replacements.get(title, title)


@dataclass(frozen=True)
class PathwayLayout:
    x0: int
    y0: int
    table_width: int
    label_w: int = 48
    col_gap: int = 7
    row_gap: int = 6
    year_gap: int = 8
    header_h: int = 22
    cols: int = 5
    cell_h: int = 58

    @property
    def cell_w(self) -> int:
        return (
            self.table_width - self.label_w - (self.cols - 1) * self.col_gap
        ) // self.cols

    def group_y(self, year: int) -> int:
        stride = self.header_h + 2 * self.cell_h + self.row_gap + self.year_gap
        return self.y0 + year * stride

    def cell_box(self, row: int, column: int) -> tuple[int, int, int, int]:
        group_y = self.group_y(row // 2)
        local_row = row % 2
        cy = group_y + self.header_h + local_row * (self.cell_h + self.row_gap)
        cx = self.x0 + self.label_w + column * (self.cell_w + self.col_gap)
        return cx, cy, cx + self.cell_w, cy + self.cell_h


def draw_pathway_table(draw: ImageDraw.ImageDraw, program_key: str, accent: str,
                       highlight: list[tuple[int, int]], labels: list[tuple[int, int]],
                       progress: float = 1.0, origin: tuple[int, int] = (54, 160),
                       table_width: int = 760, table_height: int = 455) -> None:
    program = PROGRAMS[program_key]
    x0, y0 = origin
    layout = PathwayLayout(x0, y0, table_width)
    label_w = layout.label_w
    cell_w = layout.cell_w

    semesters = ["A1", "H1", "A2", "H2", "A3", "H3"]
    year_names = ["1re année", "2e année", "3e année"]
    highlight_set = set(highlight)
    label_set = set(labels)

    draw.text(
        (x0 + label_w, y0 - 17),
        PATHWAY_LABEL,
        font=fnt(12, bold=True),
        fill=rgba(COLORS["muted"], int(255 * progress)),
        anchor="lm",
    )

    row_index = 0
    for year in range(3):
        group_y = layout.group_y(year)
        draw.text((x0 + label_w + 4, group_y + 8), year_names[year], font=fnt(13, bold=True),
                  fill=rgba(accent, int(255 * progress)), anchor="lm")
        draw.rounded_rectangle((x0 + label_w + 86, group_y + 6, x0 + table_width, group_y + 11), radius=2,
                               fill=rgba(accent, int(145 * progress)))

        for local_row in range(2):
            r = row_index
            semester = program["semesters"][r]
            _, cy, _, _ = layout.cell_box(r, 0)
            draw.text((x0 + 24, cy + layout.cell_h / 2), semesters[r], font=fnt(15, bold=True),
                      fill=rgba(COLORS["muted"], int(255 * progress)), anchor="mm")
            for col, course in enumerate(semester):
                cx, _, _, _ = layout.cell_box(r, col)
                fill, edge = CATEGORY_STYLE[course.category]
                is_highlight = (r, col) in highlight_set
                alpha = int((245 if is_highlight else 96) * progress)
                rounded(draw, (cx, cy, cx + cell_w, cy + layout.cell_h), fill,
                        outline=accent if is_highlight else edge, radius=11,
                        width=4 if is_highlight else 1, alpha=alpha)
                if is_highlight:
                    draw.rounded_rectangle((cx + 7, cy + 7, cx + 15, cy + layout.cell_h - 7), radius=4,
                                           fill=rgba(accent, int(255 * progress)))
                if (r, col) in label_set:
                    label = short_course(course.title)
                    parts = label.split("\n")
                    if len(parts) == 1:
                        font_size = 12 if len(label) <= 19 else 10
                        lines = wrap(draw, label, fnt(font_size, bold=True), cell_w - 28)
                    else:
                        font_size = 10
                        lines = parts
                    total = len(lines) * (font_size + 3)
                    sy = cy + (layout.cell_h - total) / 2 + (font_size + 1) / 2
                    for i, line in enumerate(lines[:3]):
                        draw.text((cx + cell_w / 2 + 4, sy + i * (font_size + 3)), line,
                                  font=fnt(font_size, bold=True), fill=rgba(COLORS["ink"], int(255 * progress)),
                                  anchor="mm")
            row_index += 1

def draw_curve(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    x0, y0, w, h = 912, 340, 255, 165
    draw.line([(x0, y0 + h / 2), (x0 + w, y0 + h / 2)], fill=rgba(COLORS["muted"], 130), width=2)
    draw.line([(x0 + 18, y0), (x0 + 18, y0 + h)], fill=rgba(COLORS["muted"], 130), width=2)
    pts = []
    n = max(2, int(90 * phase(p, 0.12, 0.72)))
    for i in range(n):
        t = i / 89
        pts.append((x0 + 18 + t * (w - 28), y0 + h / 2 - 58 * math.sin(2.6 * math.pi * t) * (0.6 + 0.4 * t)))
    if len(pts) > 1:
        draw.line(pts, fill=rgba(accent), width=5, joint="curve")
    draw.text((1041, 522), "une fonction évolue", font=fnt(15, bold=True), fill=rgba(accent), anchor="mm")


def draw_algebra(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    draw.text((1042, 335), "structure", font=fnt(18, bold=True), fill=rgba(accent), anchor="mm")
    values = [["1", "0", "−1"], ["2", "3", "1"], ["0", "1", "2"]]
    for r in range(3):
        for c in range(3):
            draw.text((959 + c * 46, 386 + r * 38), values[r][c], font=fnt(23, mono=True),
                      fill=rgba(COLORS["ink"]), anchor="mm")
    draw.line([(921, 365), (909, 365), (909, 473), (921, 473)], fill=rgba(accent), width=4)
    draw.line([(1088, 365), (1100, 365), (1100, 473), (1088, 473)], fill=rgba(accent), width=4)
    cx, cy = 1150, 425
    a = phase(p, 0.15, 0.80) * math.pi / 2
    pts = []
    for k in range(4):
        ang = a + math.pi / 4 + k * math.pi / 2
        pts.append((cx + 42 * math.cos(ang), cy + 42 * math.sin(ang)))
    pts.append(pts[0])
    draw.line(pts, fill=rgba(accent), width=5)


def draw_geometry(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    cx, cy = 1042, 422
    morph = phase(p, 0.12, 0.82)
    pts = []
    for i in range(100):
        a = 2 * math.pi * i / 99
        r = 82 * (1 + 0.16 * morph * math.cos(3 * a))
        pts.append((cx + r * math.cos(a), cy + 0.65 * r * math.sin(a)))
    draw.line(pts, fill=rgba(accent), width=5, joint="curve")
    draw.ellipse((1013, 405, 1071, 439), outline=rgba(COLORS["gold"]), width=5)
    draw.text((1042, 522), "formes et espaces", font=fnt(16, bold=True), fill=rgba(accent), anchor="mm")


def draw_seminar(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["dark"], radius=24)
    lines = ["Définition", "Exemple", "Théorème"]
    for i, line in enumerate(lines):
        alpha = int(255 * phase(p, 0.12 + i * 0.12, 0.40 + i * 0.12))
        draw.text((914, 355 + i * 63), line, font=fnt(24, bold=True), fill=rgba("#FFFFFF", alpha))
        if i < 2:
            draw.line([(1060, 370 + i * 63), (1138, 370 + i * 63)], fill=rgba(accent, alpha), width=4)
    draw.ellipse((1142, 470, 1170, 498), outline=rgba("#FFFFFF"), width=3)
    draw.line([(1156, 498), (1156, 525)], fill=rgba("#FFFFFF"), width=3)
    draw.line([(1138, 525), (1174, 525)], fill=rgba("#FFFFFF"), width=3)


def draw_sampling(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    for i in range(54):
        col = i % 9
        row = i // 9
        x = 910 + col * 29
        y = 350 + row * 28
        selected = (i * 7) % 11 < 3
        color = accent if selected and phase(p, 0.20, 0.60) > 0.3 else COLORS["grid"]
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=rgba(color, 235))
    draw.text((1042, 520), "population et échantillon", font=fnt(16, bold=True), fill=rgba(accent), anchor="mm")


def draw_regression(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    rng = np.random.default_rng(123)
    for i in range(28):
        x = 915 + i * 9
        y = 485 - (0.45 * i * 9 + rng.normal(0, 22))
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=rgba(accent, 220))
    q = phase(p, 0.25, 0.70)
    x1, y1 = 910, 492
    x2, y2 = 1175, 358
    draw.line([(x1, y1), (x1 + (x2 - x1) * q, y1 + (y2 - y1) * q)], fill=rgba(COLORS["gold"]), width=5)
    draw.text((1042, 520), "tendance + incertitude", font=fnt(16, bold=True), fill=rgba(accent), anchor="mm")


def draw_multivariate(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    rng = np.random.default_rng(55)
    centers = [(970, 410), (1090, 390), (1035, 470)]
    for j, (cx, cy) in enumerate(centers):
        for _ in range(18):
            x = cx + rng.normal(0, 24)
            y = cy + rng.normal(0, 19)
            color = [accent, COLORS["gold"], COLORS["math"]][j]
            draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=rgba(color, 205))
    draw.text((1042, 520), "plusieurs variables", font=fnt(16, bold=True), fill=rgba(accent), anchor="mm")


def draw_learning(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    draw.line([(925, 490), (1165, 350)], fill=rgba(COLORS["gold"]), width=4)
    for i in range(30):
        x = 915 + (i * 37) % 260
        y = 348 + (i * 53) % 150
        side = y > (-0.58 * (x - 925) + 490)
        color = accent if side else COLORS["math"]
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=rgba(color, 220))
    draw.text((1042, 520), "apprendre une règle", font=fnt(16, bold=True), fill=rgba(accent), anchor="mm")


def draw_code(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["dark"], radius=24)
    code = ["def methode(donnees):", "    modele = ajuster(donnees)", "    return modele.predire()"]
    for i, line in enumerate(code):
        alpha = int(255 * phase(p, 0.12 + i * 0.13, 0.42 + i * 0.13))
        draw.text((902, 356 + i * 58), line, font=fnt(16, mono=True), fill=rgba("#FFFFFF", alpha))
    draw.text((1042, 520), "de l’idée au programme", font=fnt(16, bold=True), fill=rgba(accent), anchor="mm")


def draw_tree(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    nodes = [(1042, 350), (975, 415), (1110, 415), (930, 485), (1005, 485), (1075, 485), (1150, 485)]
    edges = [(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]
    q = phase(p, 0.12, 0.75)
    for k, (a,b) in enumerate(edges):
        local = phase(q, k * 0.08, 0.52 + k * 0.08)
        x1,y1 = nodes[a]
        x2,y2 = nodes[b]
        draw.line([(x1,y1),(x1+(x2-x1)*local,y1+(y2-y1)*local)], fill=rgba(accent, int(220*local)), width=4)
    for i,(x,y) in enumerate(nodes):
        alpha = int(255 * phase(q, i * 0.06, 0.45 + i * 0.06))
        draw.ellipse((x-14,y-14,x+14,y+14), fill=rgba(COLORS["paper"], alpha), outline=rgba(accent, alpha), width=4)
    draw.text((1042, 525), "organiser pour chercher vite", font=fnt(15, bold=True), fill=rgba(accent), anchor="mm")


def draw_database(draw: ImageDraw.ImageDraw, p: float, accent: str) -> None:
    rounded(draw, (874, 302, 1210, 552), COLORS["paper"], outline=COLORS["grid"], radius=24)
    x0,y0 = 935,360
    for layer in range(3):
        y = y0 + layer * 43
        draw.ellipse((x0, y, x0+125, y+35), fill=rgba(COLORS["info"], 210), outline=rgba(accent), width=3)
        if layer < 2:
            draw.rectangle((x0, y+17, x0+125, y+60), fill=rgba(COLORS["info"], 210))
            draw.line([(x0,y+17),(x0,y+60)], fill=rgba(accent), width=3)
            draw.line([(x0+125,y+17),(x0+125,y+60)], fill=rgba(accent), width=3)
    draw.text((1118, 377), "SELECT", font=fnt(18, bold=True, mono=True), fill=rgba(accent), anchor="mm")
    draw.line([(1084, 410),(1154,410)], fill=rgba(COLORS["gold"]), width=4)
    draw.line([(1119,410),(1119,475)], fill=rgba(COLORS["gold"]), width=4)
    draw.text((1042, 525), "stocker et interroger", font=fnt(16, bold=True), fill=rgba(accent), anchor="mm")


def draw_profiles_scene(scene: Scene, p: float) -> np.ndarray:
    image, draw = base_canvas()
    accent = COLORS["computer"]
    draw_brand(draw, accent)
    header_alpha = int(255 * phase(p, 0.0, 0.16))
    draw.text(
        (54, 107),
        "Concentration informatique",
        font=fnt(22, bold=True),
        fill=rgba(accent, header_alpha),
    )
    draw.text(
        (54, 142),
        "Deux profils : les différences, directement",
        font=fnt(31, bold=True),
        fill=rgba(COLORS["ink"], header_alpha),
    )

    common_alpha = int(255 * phase(p, 0.08, 0.28))
    rounded(
        draw,
        (54, 184, 1226, 238),
        COLORS["dark"],
        radius=18,
        alpha=common_alpha,
    )
    draw.text(
        (82, 211),
        "BASE COMMUNE",
        font=fnt(14, bold=True),
        fill=rgba("#FFFFFF", common_alpha),
        anchor="lm",
    )
    draw.text(
        (250, 211),
        "Programmation I et II  ·  structures de données  ·  algorithmique",
        font=fnt(18, bold=True),
        fill=rgba("#FFFFFF", common_alpha),
        anchor="lm",
    )

    profiles = [
        {
            "box": (54, 266, 622, 630),
            "color": COLORS["math"],
            "title": "Profil Mathématiques",
            "subtitle": "Bloc intermédiaire obligatoire · 6 crédits",
            "courses": [
                ("MAT2250", "Théorie des groupes"),
                ("MAT2260", "Théorie des anneaux"),
            ],
            "next_label": "Puis, dans le cheminement",
            "next_courses": ["Cours de spécialisation en mathématiques"],
        },
        {
            "box": (658, 266, 1226, 630),
            "color": COLORS["stat"],
            "title": "Profil Statistique",
            "subtitle": "Science des données · bloc obligatoire · 6 crédits",
            "courses": [
                ("STT2000", "Statistique II"),
                ("STT2120", "Régression"),
            ],
            "next_label": "Puis, dans le cheminement",
            "next_courses": [
                "STT3010 · Statistique informatique",
                "STT3030 · Apprentissage statistique",
            ],
        },
    ]

    for i, profile in enumerate(profiles):
        local = phase(p, 0.17 + i * 0.08, 0.44 + i * 0.08)
        alpha = int(255 * local)
        x1, y1, x2, y2 = profile["box"]
        rounded(
            draw,
            (x1, y1, x2, y2),
            COLORS["paper"],
            outline=profile["color"],
            radius=26,
            width=4,
            alpha=alpha,
        )
        draw.rounded_rectangle(
            (x1, y1, x2, y1 + 74),
            radius=25,
            fill=rgba(profile["color"], alpha),
        )
        draw.rectangle(
            (x1, y1 + 48, x2, y1 + 74),
            fill=rgba(profile["color"], alpha),
        )
        draw.text(
            ((x1 + x2) / 2, y1 + 27),
            profile["title"],
            font=fnt(23, bold=True),
            fill=rgba("#FFFFFF", alpha),
            anchor="mm",
        )
        draw.text(
            ((x1 + x2) / 2, y1 + 55),
            profile["subtitle"],
            font=fnt(13, bold=True),
            fill=rgba("#FFFFFF", alpha),
            anchor="mm",
        )

        for row, (code, title) in enumerate(profile["courses"]):
            cy = y1 + 96 + row * 74
            rounded(
                draw,
                (x1 + 26, cy, x2 - 26, cy + 58),
                COLORS["background"],
                outline=profile["color"],
                radius=15,
                width=2,
                alpha=alpha,
            )
            draw.text(
                (x1 + 48, cy + 29),
                code,
                font=fnt(17, bold=True, mono=True),
                fill=rgba(profile["color"], alpha),
                anchor="lm",
            )
            draw.text(
                (x1 + 166, cy + 29),
                title,
                font=fnt(18, bold=True),
                fill=rgba(COLORS["ink"], alpha),
                anchor="lm",
            )

        divider_y = y1 + 250
        draw.line(
            [(x1 + 28, divider_y), (x2 - 28, divider_y)],
            fill=rgba(COLORS["grid"], alpha),
            width=2,
        )
        draw.text(
            (x1 + 28, divider_y + 25),
            profile["next_label"].upper(),
            font=fnt(12, bold=True),
            fill=rgba(COLORS["muted"], alpha),
        )
        for row, course in enumerate(profile["next_courses"]):
            draw.text(
                (x1 + 28, divider_y + 54 + row * 26),
                "• " + course,
                font=fnt(15, bold=True),
                fill=rgba(profile["color"], alpha),
            )

    label_alpha = int(255 * phase(p, 0.45, 0.68))
    draw.text(
        (640, 673),
        PATHWAY_LABEL,
        font=fnt(13, bold=True),
        fill=rgba(COLORS["muted"], label_alpha),
        anchor="mm",
    )
    return np.asarray(image.convert("RGB"))


VISUALS: dict[str, Callable[[ImageDraw.ImageDraw, float, str], None]] = {
    "analysis": draw_curve,
    "algebra": draw_algebra,
    "geometry": draw_geometry,
    "seminar": draw_seminar,
    "collection": draw_sampling,
    "models": draw_regression,
    "advanced": draw_multivariate,
    "learning": draw_learning,
    "programming": draw_code,
    "algorithms": draw_tree,
    "systems": draw_database,
}


def build_scenes() -> list[Scene]:
    narration = load_narration()
    scenes = [
        Scene(
            "01_intro",
            "intro",
            "Une base commune. Trois parcours.",
            "Les cours se spécialisent progressivement",
            narration["01_intro"],
            "intro",
            [],
            [],
        )
    ]
    for theme in PROGRAMS["math"]["themes"]:
        scene_id = f"02_math_{theme['id']}"
        scenes.append(
            Scene(
                scene_id,
                "math",
                theme["title"],
                theme["phrase"],
                narration[scene_id],
                theme["id"],
                theme["highlight"],
                theme["labels"],
            )
        )
    for theme in PROGRAMS["stat"]["themes"]:
        scene_id = f"03_stat_{theme['id']}"
        scenes.append(
            Scene(
                scene_id,
                "stat",
                theme["title"],
                theme["phrase"],
                narration[scene_id],
                theme["id"],
                theme["highlight"],
                theme["labels"],
            )
        )
    for theme in INFO_THEMES:
        scene_id = f"04_info_{theme['id']}"
        scenes.append(
            Scene(
                scene_id,
                theme["program"],
                theme["title"],
                theme["phrase"],
                narration[scene_id],
                theme["id"],
                theme["highlight"],
                theme["labels"],
            )
        )
    scenes.append(
        Scene(
            "05_closing",
            "closing",
            "Une base proche. Trois orientations.",
            "Le guide complet présente les cheminements exacts.",
            narration["05_closing"],
            "closing",
            [],
            [],
        )
    )
    return scenes


def synthesize_azure(text: str, path: Path, voice: str) -> None:
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError as exc:
        raise RuntimeError(
            "Azure Speech support is missing; install the requirements first"
        ) from exc

    subscription_key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")
    service_region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")
    if not subscription_key or not service_region:
        raise RuntimeError(
            "Set SPEECH_KEY and SPEECH_REGION before regenerating Azure narration"
        )

    speech_config = speechsdk.SpeechConfig(
        subscription=subscription_key,
        region=service_region,
    )
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Audio48Khz192KBitRateMonoMp3
    )
    ssml = (
        "<speak version='1.0' "
        "xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='fr-CA'>"
        f"<voice name='{html.escape(voice, quote=True)}'>"
        f"<prosody rate='{AZURE_RATE}'>{html.escape(text)}</prosody>"
        "</voice></speak>"
    )

    with tempfile.TemporaryDirectory(prefix="uqam_azure_tts_") as temp_dir:
        raw_path = Path(temp_dir) / "narration.mp3"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=str(raw_path))
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )
        result = synthesizer.speak_ssml_async(ssml).get()
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            details = result.cancellation_details
            message = details.error_details if details else str(result.reason)
            raise RuntimeError(f"Azure speech synthesis failed: {message}")

        audio = AudioSegment.from_mp3(raw_path)
        if audio.dBFS != float("-inf"):
            audio = audio.apply_gain(TARGET_SPEECH_DBFS - audio.dBFS)
        audio = (
            AudioSegment.silent(duration=LEAD_SILENCE_MS)
            + audio
            + AudioSegment.silent(duration=TAIL_SILENCE_MS)
        )
        audio.export(path, format="wav")


def synthesize_espeak(text: str, path: Path, rate: int) -> None:
    executable = shutil.which("espeak")
    if not executable:
        raise RuntimeError(
            "eSpeak was explicitly requested but is not installed. "
            "Use --tts azure for release narration."
        )
    with tempfile.TemporaryDirectory(prefix="uqam_espeak_tts_") as temp_dir:
        raw_path = Path(temp_dir) / "narration.wav"
        subprocess.run(
            [
                executable,
                "-v",
                "fr",
                "-s",
                str(rate),
                "-p",
                "47",
                "-a",
                "155",
                "-w",
                str(raw_path),
                text,
            ],
            check=True,
        )
        audio = AudioSegment.from_wav(raw_path)
        audio = (
            AudioSegment.silent(duration=LEAD_SILENCE_MS)
            + audio
            + AudioSegment.silent(duration=TAIL_SILENCE_MS)
        )
        audio.export(path, format="wav")


def voice_metadata_path(audio_path: Path) -> Path:
    return audio_path.with_suffix(".voice.json")


def stale_narration_error(scene: Scene) -> RuntimeError:
    return RuntimeError(
        f"Existing narration for {scene.scene_id} is missing or stale.\n"
        "Regenerate it with:\n"
        f".venv/bin/python render_video.py --scene {scene.scene_id} --tts azure"
    )


def read_validated_audio(scene: Scene, audio_path: Path) -> float:
    metadata_path = voice_metadata_path(audio_path)
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("schema") != 1:
            raise ValueError("unsupported metadata schema")
        if metadata.get("scene_id") != scene.scene_id:
            raise ValueError("scene id mismatch")
        if metadata.get("narration_sha256") != scene.narration.digest:
            raise ValueError("narration changed")
        if not audio_path.is_file():
            raise FileNotFoundError(audio_path)
        if metadata.get("audio_sha256") != sha256_file(audio_path):
            raise ValueError("audio hash mismatch")
        audio = AudioSegment.from_wav(audio_path)
        duration_ms = len(audio)
        if int(metadata.get("duration_ms", -1)) != duration_ms:
            raise ValueError("duration mismatch")
    except (OSError, ValueError, TypeError, AttributeError, json.JSONDecodeError):
        raise stale_narration_error(scene) from None
    return duration_ms / 1000.0


def generate_audio(
    scene: Scene,
    audio_path: Path,
    *,
    tts: str,
    rate: int,
    azure_voice: str,
) -> float:
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".narration-", dir=VOICE_DIR) as temp_dir:
        temporary_audio = Path(temp_dir) / f"{scene.scene_id}.wav"
        if tts == "azure":
            print(f"Azure narration: {scene.scene_id}")
            synthesize_azure(scene.transcript, temporary_audio, azure_voice)
            provider = "azure"
            voice = azure_voice
            speech_rate = AZURE_RATE
        elif tts == "espeak":
            print(f"Draft eSpeak narration: {scene.scene_id}")
            synthesize_espeak(scene.transcript, temporary_audio, rate)
            provider = "espeak"
            voice = "fr"
            speech_rate = str(rate)
        else:
            raise ValueError(f"Unsupported narration provider: {tts}")

        audio = AudioSegment.from_wav(temporary_audio)
        duration_ms = len(audio)
        metadata = {
            "schema": 1,
            "scene_id": scene.scene_id,
            "narration_sha256": scene.narration.digest,
            "audio_sha256": sha256_file(temporary_audio),
            "provider": provider,
            "voice": voice,
            "rate": speech_rate,
            "duration_ms": duration_ms,
        }
        temporary_metadata = Path(temp_dir) / f"{scene.scene_id}.voice.json"
        temporary_metadata.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary_audio, audio_path)
        os.replace(temporary_metadata, voice_metadata_path(audio_path))
    return duration_ms / 1000.0


def prepare_audio(
    scenes: list[Scene],
    rate: int = 150,
    *,
    tts: str = "existing",
    azure_voice: str = AZURE_VOICE,
) -> None:
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    for scene in scenes:
        path = VOICE_DIR / f"{scene.scene_id}.wav"
        if tts == "existing":
            scene.duration = read_validated_audio(scene, path)
        else:
            scene.duration = generate_audio(
                scene,
                path,
                tts=tts,
                rate=rate,
                azure_voice=azure_voice,
            )
        scene.audio_path = path


def draw_intro(p: float) -> np.ndarray:
    image, draw = base_canvas()
    draw_brand(draw, COLORS["gold"])
    hero = phase(p, 0.0, 0.14)
    hero_alpha = int(255 * hero)
    composite_text(
        image,
        (54, 113),
        "Une base commune.",
        font=fnt(44, bold=True),
        color=COLORS["ink"],
        alpha=hero_alpha,
    )
    composite_text(
        image,
        (54, 168),
        "Trois parcours qui se précisent.",
        font=fnt(27, bold=True),
        color=COLORS["gold"],
        alpha=hero_alpha,
    )
    rounded(
        draw,
        (1010, 112, 1226, 156),
        COLORS["paper"],
        outline=COLORS["grid"],
        radius=22,
        alpha=hero_alpha,
    )
    composite_text(
        image,
        (1118, 134),
        "3 CONCENTRATIONS",
        font=fnt(14, bold=True),
        color=COLORS["muted"],
        alpha=hero_alpha,
        anchor="mm",
    )

    # The common core is a single, calm panel instead of a floating card cloud.
    panel = phase(p, 0.08, 0.28)
    panel_alpha = int(255 * panel)
    rounded(
        draw,
        (54, 226, 758, 625),
        COLORS["paper"],
        outline=COLORS["grid"],
        radius=28,
        width=2,
        alpha=panel_alpha,
    )
    rounded(
        draw,
        (78, 252, 92, 266),
        COLORS["gold"],
        radius=5,
        alpha=panel_alpha,
    )
    composite_text(
        image,
        (106, 259),
        "SOCLE COMMUN",
        font=fnt(16, bold=True),
        color=COLORS["muted"],
        alpha=panel_alpha,
        anchor="lm",
    )
    composite_text(
        image,
        (728, 259),
        "les fondamentaux d’abord",
        font=fnt(15),
        color=COLORS["muted"],
        alpha=panel_alpha,
        anchor="rm",
    )
    draw.line(
        [(78, 286), (734, 286)],
        fill=rgba(COLORS["grid"], panel_alpha),
        width=2,
    )

    labels = COMMON_FOUNDATION
    chip_layout = [
        (78, 318, 150, 66),
        (244, 318, 150, 66),
        (410, 318, 150, 66),
        (576, 318, 158, 66),
        (116, 407, 178, 72),
        (310, 407, 206, 72),
        (532, 407, 178, 72),
    ]
    for i, (label, (x, y, width, height)) in enumerate(zip(labels, chip_layout)):
        local = phase(p, 0.15 + i * 0.035, 0.34 + i * 0.035)
        local_alpha = int(255 * local)
        rise = int(10 * (1.0 - local))
        rounded(
            draw,
            (x, y + rise, x + width, y + height + rise),
            COLORS["mathstat"],
            outline=COLORS["mathstat_edge"],
            radius=16,
            alpha=int(238 * local),
        )
        draw.rounded_rectangle(
            (x + 12, y + 12 + rise, x + 19, y + height - 12 + rise),
            radius=4,
            fill=rgba(COLORS["math"], local_alpha),
        )
        font_size = 17 if len(label) < 18 else 15
        lines = wrap(draw, label, fnt(font_size, bold=True), width - 44)
        total = len(lines) * (font_size + 4)
        sy = y + rise + (height - total) / 2 + (font_size + 2) / 2
        for j, line in enumerate(lines):
            composite_text(
                image,
                (x + width / 2 + 7, sy + j * (font_size + 4)),
                line,
                font=fnt(font_size, bold=True),
                color=COLORS["ink"],
                alpha=local_alpha,
                anchor="mm",
            )

    # A directional footer makes the progression explicit without a heavy rail.
    flow = phase(p, 0.36, 0.57)
    flow_alpha = int(255 * flow)
    composite_text(
        image,
        (82, 557),
        "BASE COMMUNE",
        font=fnt(13, bold=True),
        color=COLORS["dark"],
        alpha=flow_alpha,
        anchor="lm",
    )
    draw.line(
        [(214, 557), (690, 557)],
        fill=rgba(COLORS["dark"], int(190 * flow)),
        width=4,
    )
    arrow_x = int(690 + 22 * flow)
    draw.polygon(
        [(arrow_x, 557), (arrow_x - 14, 549), (arrow_x - 14, 565)],
        fill=rgba(COLORS["dark"], flow_alpha),
    )
    composite_text(
        image,
        (710, 588),
        "spécialisation progressive",
        font=fnt(15, bold=True),
        color=COLORS["muted"],
        alpha=flow_alpha,
        anchor="rm",
    )

    # The three destination cards share one visual system and slide gently in.
    paths_label = phase(p, 0.42, 0.58)
    composite_text(
        image,
        (824, 222),
        "PUIS, TROIS PARCOURS",
        font=fnt(15, bold=True),
        color=COLORS["muted"],
        alpha=int(255 * paths_label),
    )
    branches = [
        (COLORS["math"], "01", "Mathématiques\nfondamentales", "démontrer et structurer"),
        (COLORS["stat"], "02", "Statistique", "modéliser les données"),
        (COLORS["computer"], "03", "Concentration\ninformatique", "programmer et concevoir"),
    ]
    for i, (color, number, label, descriptor) in enumerate(branches):
        local = phase(p, 0.48 + i * 0.06, 0.70 + i * 0.06)
        local_alpha = int(255 * local)
        y = 254 + i * 120
        x = int(824 + 34 * (1.0 - local))
        rounded(
            draw,
            (x, y, 1226, y + 98),
            COLORS["paper"],
            outline=color,
            radius=24,
            width=3,
            alpha=local_alpha,
        )
        draw.rounded_rectangle(
            (x, y, x + 10, y + 98),
            radius=5,
            fill=rgba(color, local_alpha),
        )
        rounded(
            draw,
            (x + 28, y + 27, x + 72, y + 71),
            color,
            radius=14,
            alpha=local_alpha,
        )
        composite_text(
            image,
            (x + 50, y + 49),
            number,
            font=fnt(16, bold=True),
            color=COLORS["paper"],
            alpha=local_alpha,
            anchor="mm",
        )
        lines = label.split("\n")
        label_size = 21 if len(lines) == 1 else 19
        label_y = y + 35 if len(lines) == 1 else y + 27
        for j, line in enumerate(lines):
            composite_text(
                image,
                (x + 92, label_y + j * 23),
                line,
                font=fnt(label_size, bold=True),
                color=color,
                alpha=local_alpha,
                anchor="lm",
            )
        composite_text(
            image,
            (1200, y + 76),
            descriptor,
            font=fnt(14),
            color=COLORS["muted"],
            alpha=local_alpha,
            anchor="rm",
        )
    return np.asarray(image.convert("RGB"))


def draw_theme_scene(scene: Scene, p: float) -> np.ndarray:
    if scene.visual == "profiles":
        return draw_profiles_scene(scene, p)

    image, draw = base_canvas()
    accent = PROGRAM_ACCENTS[scene.program_key]
    base_program = scene.program_key
    draw_brand(draw, accent)
    head_alpha = int(255 * phase(p, 0.0, 0.13))
    program_title = PROGRAMS[base_program].get("short_title", PROGRAMS[base_program]["title"])
    draw.text((54, 105), program_title, font=fnt(23, bold=True), fill=rgba(accent, head_alpha))
    draw_pathway_table(draw, base_program, accent, scene.highlight, scene.labels, phase(p, 0.02, 0.25))

    panel_alpha = int(255 * phase(p, 0.08, 0.30))
    title_h = draw_wrapped(draw, (850, 116), scene.title, 29, accent, 365, bold=True,
                           alpha=panel_alpha, line_gap=34)
    draw_wrapped(draw, (850, 126 + title_h), scene.phrase, 20, COLORS["ink"], 355,
                 bold=True, alpha=panel_alpha, line_gap=27)
    VISUALS[scene.visual](draw, p, accent)
    return np.asarray(image.convert("RGB"))


def draw_closing(p: float) -> np.ndarray:
    image, draw = base_canvas()
    draw_brand(draw, COLORS["gold"])
    q = phase(p, 0.0, 0.18)
    draw.text((640, 125), "Une base proche. Trois orientations.", font=fnt(40, bold=True), fill=rgba(COLORS["ink"], int(255*q)), anchor="ma")
    cards = [
        (COLORS["math"], "Mathématiques fondamentales", ["analyse", "algèbre", "géométrie"]),
        (COLORS["stat"], "Statistique", ["données", "modèles", "apprentissage"]),
        (COLORS["computer"], "Concentration informatique", ["programmation", "algorithmes", "deux profils"]),
    ]
    for i,(accent,title,words) in enumerate(cards):
        local = phase(p, 0.12+i*0.07, 0.40+i*0.07)
        x = 64 + i*405
        rounded(draw, (x,230,x+360,505), COLORS["paper"], outline=accent, radius=26, width=4, alpha=int(255*local))
        draw.text((x+180,278), title, font=fnt(20 if i!=2 else 18, bold=True), fill=rgba(accent, int(255*local)), anchor="mm")
        # Three large, spacious blocks echo the table without reproducing it.
        for j,word in enumerate(words):
            rounded(draw, (x+48,325+j*52,x+312,365+j*52), COLORS["background"], outline=COLORS["grid"], radius=12, alpha=int(255*local))
            draw.text((x+180,345+j*52), word, font=fnt(18, bold=True), fill=rgba(COLORS["ink"], int(255*local)), anchor="mm")
    r = phase(p, 0.55, 0.78)
    draw.text((640, 580), "Consultez le guide pour les cours exacts et les cheminements.", font=fnt(23, bold=True), fill=rgba(COLORS["ink"], int(255*r)), anchor="ma")
    draw.text((640, 626), "math.uqam.ca", font=fnt(24, bold=True), fill=rgba(COLORS["gold"], int(255*r)), anchor="ma")
    return np.asarray(image.convert("RGB"))


def scene_opacity(t: float, duration: float, fps: int) -> float:
    fade_in = phase(t, 0.0, 0.30)
    fade_end = max(0.0, duration - 1 / fps)
    fade_start = max(0.0, fade_end - 0.65)
    fade_out = 1.0 - phase(t, fade_start, fade_end)
    return min(fade_in, fade_out)


def make_frame(scene: Scene, fps: int = FPS) -> Callable[[float], np.ndarray]:
    def frame(t: float) -> np.ndarray:
        p = clamp(t / max(scene.duration, 0.1))
        if scene.scene_id == "01_intro":
            arr = draw_intro(p)
        elif scene.scene_id == "05_closing":
            arr = draw_closing(p)
        else:
            arr = draw_theme_scene(scene, p)
        fade = scene_opacity(t, scene.duration, fps)
        if fade <= 0:
            return np.asarray(base_background().convert("RGB")).copy()
        if fade < 0.999:
            bg = np.asarray(base_background().convert("RGB"))
            arr = (
                arr.astype(float) * fade
                + bg.astype(float) * (1 - fade)
            ).astype(np.uint8)
        return arr
    return frame


def render_scene(scene: Scene, index: int, fps: int) -> Path:
    SCENE_DIR.mkdir(parents=True, exist_ok=True)
    path = SCENE_DIR / f"{index:02d}-{scene.scene_id}.mp4"
    clip = VideoClip(frame_function=make_frame(scene, fps), duration=scene.duration)
    audio = AudioFileClip(str(scene.audio_path)) if scene.audio_path else None
    if audio:
        clip = clip.with_audio(audio)
    clip.write_videofile(
        str(path),
        fps=fps,
        codec=MANIFEST["render"]["video_codec"],
        audio_codec=MANIFEST["render"]["audio_codec"],
        bitrate=MANIFEST["render"]["video_bitrate"],
        audio_bitrate=MANIFEST["render"]["audio_bitrate"],
        preset="veryfast",
        threads=4,
        pixel_format=MANIFEST["render"]["pixel_format"],
        logger=None,
    )
    clip.close()
    if audio:
        audio.close()
    return path


def assemble(scene_paths: list[Path]) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    concat = SCENE_DIR / "concat.txt"
    concat.write_text("\n".join(f"file '{p.resolve()}'" for p in scene_paths) + "\n", encoding="utf-8")
    output = DIST_DIR / f"{ARTIFACT_STEM}.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(output),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return output


def srt_time(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def subtitle_intervals(scene: Scene) -> list[tuple[float, float, str]]:
    spoken_start = min(scene.duration, LEAD_SILENCE_MS / 1000)
    spoken_end = max(spoken_start, scene.duration - TAIL_SILENCE_MS / 1000)
    if spoken_end <= spoken_start:
        spoken_start = 0.0
        spoken_end = scene.duration
    weights = [
        max(1, len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", cue)))
        for cue in scene.narration.cues
    ]
    total_weight = sum(weights)
    cursor = spoken_start
    intervals = []
    for index, (cue, weight) in enumerate(zip(scene.narration.cues, weights)):
        if index == len(weights) - 1:
            end = spoken_end
        else:
            end = cursor + (spoken_end - spoken_start) * weight / total_weight
        intervals.append((cursor, end, "\n".join(wrap_subtitle(cue))))
        cursor = end
    return intervals


def write_srt(scenes: list[Scene]) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    path = DIST_DIR / f"{ARTIFACT_STEM}.srt"
    cursor = 0.0
    blocks = []
    cue_number = 1
    for scene in scenes:
        for start, end, cue in subtitle_intervals(scene):
            blocks.append(
                f"{cue_number}\n"
                f"{srt_time(cursor + start)} --> {srt_time(cursor + end)}\n"
                f"{cue}\n"
            )
            cue_number += 1
        cursor += scene.duration
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def svg_tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


def add_svg_text(
    parent: ET.Element,
    x: float,
    y: float,
    text: str,
    *,
    size: int,
    fill: str,
    bold: bool = False,
    anchor: str = "start",
    css_class: str | None = None,
) -> ET.Element:
    attributes = {
        "x": f"{x:g}",
        "y": f"{y:g}",
        "fill": fill,
        "font-family": "Noto Sans, Arial, sans-serif",
        "font-size": str(size),
        "font-weight": "700" if bold else "400",
        "text-anchor": anchor,
        "dominant-baseline": "middle",
    }
    if css_class:
        attributes["class"] = css_class
    element = ET.SubElement(parent, svg_tag("text"), attributes)
    element.text = text
    return element


def inline_official_logo(parent: ET.Element, x: int = 48, y: int = 20) -> None:
    source = ET.parse(IDENTITY_SVG).getroot()
    wrapper = ET.SubElement(
        parent,
        svg_tag("g"),
        {
            "id": "official-uqam-logo",
            "transform": f"translate({x} {y})",
            "aria-label": "UQAM",
        },
    )
    for child in source:
        wrapper.append(copy.deepcopy(child))


def svg_cell_lines(
    title: str,
    max_width: int,
) -> tuple[int, list[str]]:
    probe = ImageDraw.Draw(Image.new("RGB", (4, 4), "white"))
    simplified = short_course(title).replace("\n", " ")
    for size in range(11, 7, -1):
        lines = wrap(probe, simplified, fnt(size, bold=True), max_width)
        if len(lines) <= 3:
            return size, lines
    return 8, wrap(probe, simplified, fnt(8, bold=True), max_width)[:3]


def render_table_svg(program_key: str, path: Path) -> Path:
    accent = PROGRAM_ACCENTS[program_key]
    program = PROGRAMS[program_key]
    root = ET.Element(
        svg_tag("svg"),
        {
            "width": str(WIDTH),
            "height": str(HEIGHT),
            "viewBox": f"0 0 {WIDTH} {HEIGHT}",
            "role": "img",
            "aria-labelledby": "table-title table-description",
        },
    )
    title = ET.SubElement(root, svg_tag("title"), {"id": "table-title"})
    title.text = program["title"]
    description = ET.SubElement(
        root, svg_tag("desc"), {"id": "table-description"}
    )
    description.text = (
        f"{PATHWAY_LABEL}. Reconstructed from page {program['source_page']} "
        "of the official student guide."
    )
    metadata = ET.SubElement(root, svg_tag("metadata"))
    metadata.text = json.dumps(
        {
            "project": MANIFEST["project"]["id"],
            "source_year": MANIFEST["project"]["source_year"],
            "source_page": program["source_page"],
            "pathway": PATHWAY_LABEL,
        },
        ensure_ascii=False,
        sort_keys=True,
    )

    ET.SubElement(
        root,
        svg_tag("rect"),
        {
            "x": "0",
            "y": "0",
            "width": str(WIDTH),
            "height": str(HEIGHT),
            "fill": COLORS["background"],
        },
    )
    grid_group = ET.SubElement(root, svg_tag("g"), {"opacity": "0.28"})
    for x in range(0, WIDTH, 80):
        ET.SubElement(
            grid_group,
            svg_tag("line"),
            {
                "x1": str(x),
                "y1": "0",
                "x2": str(x),
                "y2": str(HEIGHT),
                "stroke": COLORS["grid"],
            },
        )
    for y in range(0, HEIGHT, 80):
        ET.SubElement(
            grid_group,
            svg_tag("line"),
            {
                "x1": "0",
                "y1": str(y),
                "x2": str(WIDTH),
                "y2": str(y),
                "stroke": COLORS["grid"],
            },
        )

    ET.SubElement(
        root,
        svg_tag("rect"),
        {
            "x": "0",
            "y": "0",
            "width": str(WIDTH),
            "height": "82",
            "fill": COLORS["dark"],
        },
    )
    inline_official_logo(root)
    add_svg_text(
        root,
        190,
        40,
        "Unité de programme en mathématiques et statistique",
        size=17,
        fill="#FFFFFF",
        bold=True,
    )
    add_svg_text(
        root,
        WIDTH - 48,
        40,
        "FACULTÉ DES SCIENCES",
        size=13,
        fill="#DDE3E6",
        bold=True,
        anchor="end",
    )
    ET.SubElement(
        root,
        svg_tag("rect"),
        {"x": "0", "y": "78", "width": str(WIDTH), "height": "4", "fill": accent},
    )
    add_svg_text(
        root,
        54,
        108,
        program["title"],
        size=25,
        fill=accent,
        bold=True,
    )

    layout = PathwayLayout(150, 168, 980)
    add_svg_text(
        root,
        layout.x0 + layout.label_w,
        layout.y0 - 17,
        PATHWAY_LABEL,
        size=12,
        fill=COLORS["muted"],
        bold=True,
    )
    semesters = ["A1", "H1", "A2", "H2", "A3", "H3"]
    year_names = ["1re année", "2e année", "3e année"]
    for year, year_name in enumerate(year_names):
        group_y = layout.group_y(year)
        add_svg_text(
            root,
            layout.x0 + layout.label_w + 4,
            group_y + 8,
            year_name,
            size=13,
            fill=accent,
            bold=True,
        )
        ET.SubElement(
            root,
            svg_tag("rect"),
            {
                "x": str(layout.x0 + layout.label_w + 86),
                "y": str(group_y + 6),
                "width": str(layout.table_width - layout.label_w - 86),
                "height": "5",
                "rx": "2",
                "fill": accent,
                "opacity": "0.57",
            },
        )

    for row, semester in enumerate(program["semesters"]):
        _, cy, _, _ = layout.cell_box(row, 0)
        add_svg_text(
            root,
            layout.x0 + 24,
            cy + layout.cell_h / 2,
            semesters[row],
            size=15,
            fill=COLORS["muted"],
            bold=True,
            anchor="middle",
        )
        for column, course in enumerate(semester):
            cx, cy, right, bottom = layout.cell_box(row, column)
            fill, edge = CATEGORY_STYLE[course.category]
            group = ET.SubElement(
                root,
                svg_tag("g"),
                {
                    "id": f"cell-{row + 1}-{column + 1}",
                    "class": "course-cell",
                    "data-row": str(row + 1),
                    "data-column": str(column + 1),
                    "data-full-title": course.title,
                },
            )
            tooltip = ET.SubElement(group, svg_tag("title"))
            tooltip.text = course.title
            ET.SubElement(
                group,
                svg_tag("rect"),
                {
                    "x": str(cx),
                    "y": str(cy),
                    "width": str(right - cx),
                    "height": str(bottom - cy),
                    "rx": "11",
                    "fill": fill,
                    "stroke": edge,
                    "stroke-width": "1.5",
                },
            )
            size, lines = svg_cell_lines(course.title, layout.cell_w - 20)
            line_height = size + 3
            center_y = cy + layout.cell_h / 2
            start_y = center_y - (len(lines) - 1) * line_height / 2
            text_element = ET.SubElement(
                group,
                svg_tag("text"),
                {
                    "fill": COLORS["ink"],
                    "font-family": "Noto Sans, Arial, sans-serif",
                    "font-size": str(size),
                    "font-weight": "700",
                    "text-anchor": "middle",
                    "class": "course-label",
                },
            )
            for line_index, line in enumerate(lines):
                tspan = ET.SubElement(
                    text_element,
                    svg_tag("tspan"),
                    {
                        "x": f"{cx + layout.cell_w / 2:g}",
                        "y": f"{start_y + line_index * line_height:g}",
                    },
                )
                tspan.text = line

    add_svg_text(
        root,
        WIDTH - 54,
        672,
        f"Source : Guide de la personne étudiante, p. {program['source_page']}",
        size=12,
        fill=COLORS["muted"],
        anchor="end",
    )
    ET.indent(root, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(
        path,
        encoding="utf-8",
        xml_declaration=True,
    )
    return path


def table_basename(program_key: str) -> str:
    names = {
        "math": "uqam-cheminement-mathematiques-fondamentales",
        "stat": "uqam-cheminement-statistique",
        "info_math": (
            "uqam-cheminement-concentration-informatique-profil-mathematiques"
        ),
        "info_stat": (
            "uqam-cheminement-concentration-informatique-profil-statistique"
        ),
    }
    return (
        f"{names[program_key]}-automne-5-cours-"
        f"{SOURCE_YEAR_SLUG}"
    )


def render_table_stills() -> list[Path]:
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    outputs = []
    all_labels = [(row, column) for row in range(6) for column in range(5)]
    for key in ["math", "stat", "info_math", "info_stat"]:
        image, draw = base_canvas()
        accent = PROGRAM_ACCENTS[key]
        draw_brand(draw, accent)
        draw.text(
            (54, 108),
            PROGRAMS[key]["title"],
            font=fnt(25, bold=True),
            fill=rgba(accent),
            anchor="lm",
        )
        draw_pathway_table(
            draw,
            key,
            accent,
            [],
            all_labels,
            1.0,
            origin=(150, 168),
            table_width=980,
            table_height=455,
        )
        draw.text(
            (WIDTH - 54, 672),
            f"Source : Guide de la personne étudiante, p. {PROGRAMS[key]['source_page']}",
            font=fnt(12),
            fill=rgba(COLORS["muted"]),
            anchor="rm",
        )
        basename = table_basename(key)
        png_path = TABLE_DIR / f"{basename}.png"
        svg_path = TABLE_DIR / f"{basename}.svg"
        image.convert("RGB").save(png_path)
        render_table_svg(key, svg_path)
        outputs.extend([png_path, svg_path])
    return outputs


def build_storyboard(scenes: list[Scene], fps: int = FPS) -> Path:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    cols = 3
    thumb_w, thumb_h = 426, 240
    rows = math.ceil(len(scenes) / cols)
    board = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + 34)), "white")
    draw = ImageDraw.Draw(board)
    for i, scene in enumerate(scenes):
        frame = Image.fromarray(
            make_frame(scene, fps)(scene.duration * 0.55)
        ).resize((thumb_w, thumb_h))
        x = (i % cols) * thumb_w
        y = (i // cols) * (thumb_h + 34)
        board.paste(frame, (x, y))
        draw.text((x + 10, y + thumb_h + 8), scene.title, font=fnt(15, bold=True), fill=rgb(COLORS["ink"]))
    path = DIST_DIR / f"{ARTIFACT_STEM}-storyboard.png"
    board.save(path)
    return path


def probe_video(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            (
                "format=duration:"
                "stream=index,codec_type,codec_name,width,height,"
                "r_frame_rate,pix_fmt,sample_rate,channels"
            ),
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def validate_video(path: Path, fps: int) -> dict:
    probe = probe_video(path)
    video_streams = [
        stream for stream in probe.get("streams", [])
        if stream.get("codec_type") == "video"
    ]
    audio_streams = [
        stream for stream in probe.get("streams", [])
        if stream.get("codec_type") == "audio"
    ]
    problems = []
    if len(video_streams) != 1:
        problems.append("expected exactly one video stream")
    else:
        video = video_streams[0]
        if video.get("codec_name") != "h264":
            problems.append(f"expected H.264; found {video.get('codec_name')}")
        if (video.get("width"), video.get("height")) != (WIDTH, HEIGHT):
            problems.append(
                f"expected {WIDTH}×{HEIGHT}; "
                f"found {video.get('width')}×{video.get('height')}"
            )
        if video.get("pix_fmt") != MANIFEST["render"]["pixel_format"]:
            problems.append(
                f"expected {MANIFEST['render']['pixel_format']}; "
                f"found {video.get('pix_fmt')}"
            )
        numerator, denominator = (
            int(value) for value in video.get("r_frame_rate", "0/1").split("/")
        )
        actual_fps = numerator / denominator if denominator else 0
        if not math.isclose(actual_fps, fps, rel_tol=0, abs_tol=0.001):
            problems.append(f"expected {fps} fps; found {actual_fps:g}")
    if len(audio_streams) != 1:
        problems.append("expected exactly one audio stream")
    elif audio_streams[0].get("codec_name") != "aac":
        problems.append(
            f"expected AAC; found {audio_streams[0].get('codec_name')}"
        )
    if problems:
        raise RuntimeError(
            f"Rendered video validation failed for {path}:\n- "
            + "\n- ".join(problems)
        )
    return probe


def artifact_record(path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "sha256": sha256_file(path),
        "bytes": path.stat().st_size,
    }


def write_build_manifest(
    scenes: list[Scene],
    outputs: Iterable[Path],
    *,
    tool_versions: dict[str, str],
    video_probe: dict,
    fps: int,
) -> Path:
    input_paths = [
        MANIFEST_PATH,
        ROOT / "render_video.py",
        ROOT / "program_data.py",
        ROOT / "theme.py",
        NARRATION_PATH,
        ROOT / "requirements.txt",
        ROOT / MANIFEST["source"]["guide"]["path"],
        IDENTITY_SVG,
        IDENTITY_PNG,
        FONT_REGULAR,
        FONT_BOLD,
        FONT_MONO,
        ROOT / "assets/fonts/OFL-1.1.txt",
    ]
    lock_path = ROOT / "requirements.lock"
    if lock_path.is_file():
        input_paths.append(lock_path)

    audio_records = []
    for scene in scenes:
        if not scene.audio_path:
            continue
        metadata_path = voice_metadata_path(scene.audio_path)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        audio_records.append(
            {
                "scene_id": scene.scene_id,
                "narration_sha256": scene.narration.digest,
                "audio": artifact_record(scene.audio_path),
                "metadata": artifact_record(metadata_path),
                "provider": metadata["provider"],
                "voice": metadata["voice"],
                "rate": metadata["rate"],
                "duration_ms": metadata["duration_ms"],
            }
        )

    payload = {
        "schema": 1,
        "project": {
            "id": MANIFEST["project"]["id"],
            "release": MANIFEST["project"]["release"],
            "language": MANIFEST["project"]["language"],
            "source_year": MANIFEST["project"]["source_year"],
            "pathway": PATHWAY_LABEL,
        },
        "identity": {
            "provenance_url": MANIFEST["identity"]["provenance_url"],
            "usage_policy_url": MANIFEST["identity"]["usage_policy_url"],
            "authorization": MANIFEST["identity"]["authorization"],
        },
        "render": {
            **MANIFEST["render"],
            "actual_fps": fps,
        },
        "toolchain": tool_versions,
        "inputs": [
            artifact_record(path)
            for path in sorted(input_paths, key=lambda item: item.as_posix())
        ],
        "narration_segments": audio_records,
        "outputs": [
            artifact_record(path)
            for path in sorted(outputs, key=lambda item: item.as_posix())
        ],
        "video_probe": video_probe,
    }
    path = DIST_DIR / "build-manifest.json"
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def select_scenes(
    scenes: list[Scene],
    scene_id: str | None,
) -> list[tuple[int, Scene]]:
    indexed = list(enumerate(scenes, start=1))
    if scene_id is None:
        return indexed
    selected = [(index, scene) for index, scene in indexed if scene.scene_id == scene_id]
    if not selected:
        available = ", ".join(scene.scene_id for _, scene in indexed)
        raise SystemExit(f"Unknown scene: {scene_id}\nAvailable scenes: {available}")
    return selected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fps", type=int, default=FPS)
    parser.add_argument("--scene", help="Render only a scene id")
    parser.add_argument("--audio-rate", type=int, default=150)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate dependencies, versions, narration, and source assets, then exit",
    )
    parser.add_argument(
        "--tts",
        choices=("existing", "azure", "espeak"),
        default="existing",
        help=(
            "Validate existing narration, or explicitly regenerate selected "
            "segments with Azure/eSpeak"
        ),
    )
    parser.add_argument("--azure-voice", default=AZURE_VOICE)
    args = parser.parse_args()

    scenes = build_scenes()
    selected = select_scenes(scenes, args.scene)
    tool_versions = check_environment()
    if args.check:
        print("Environment, source assets, and narration: OK")
        for name, version in sorted(tool_versions.items()):
            print(f"{name}={version}")
        return

    selected_scenes = [scene for _, scene in selected]
    prepare_audio(
        selected_scenes,
        rate=args.audio_rate,
        tts=args.tts,
        azure_voice=args.azure_voice,
    )

    if args.scene:
        index, scene = selected[0]
        output = render_scene(scene, index, args.fps)
        validate_video(output, args.fps)
        print(output)
        return

    table_paths = render_table_stills()
    paths = [render_scene(scene, i, args.fps) for i, scene in enumerate(scenes, start=1)]
    video = assemble(paths)
    srt = write_srt(scenes)
    storyboard = build_storyboard(scenes, args.fps)
    video_probe = validate_video(video, args.fps)
    build_manifest = write_build_manifest(
        scenes,
        [video, srt, storyboard, *table_paths],
        tool_versions=tool_versions,
        video_probe=video_probe,
        fps=args.fps,
    )
    print(video)
    print(srt)
    print(storyboard)
    print(build_manifest)
    print(f"duration={sum(s.duration for s in scenes):.1f}s")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
