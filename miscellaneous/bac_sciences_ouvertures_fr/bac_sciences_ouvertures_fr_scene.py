"""Sparse 20-second UQAM interdisciplinary-pathway clip.

The visual audit deliberately removes the card-heavy presentation style. Every
beat uses one of two photographs cropped from slide 1 of the supplied UQAM
presentation, a restrained dark overlay, and at most three short text lines.
Narration continues to use the repository's shared Azure/MAI configuration.
"""
from __future__ import annotations

import json
import os
from contextlib import nullcontext
from pathlib import Path

from manim import (
    BLACK,
    ORIGIN,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Rectangle,
    Text,
    config,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from manimpango import list_fonts, register_font

from miscellaneous.bac_sciences_ouvertures_fr.project import (
    ROOT,
    load_project,
    validate_assets,
)
from tools.tts import (
    VOICE_LOCALES,
    azure_service_kwargs,
    configure_azure_speech_environment,
    resolve_voice,
    ssml,
)

config.background_color = BLACK

INK_WHITE = "#FFFFFF"
SOFT_WHITE = "#EEF3F6"
UQAM_BLUE = "#4DB7E5"


class BacSciencesOuverturesFR(VoiceoverScene):
    """One UQAM photo and one short idea at a time."""

    def label(self, text: str, size: int, color: str = INK_WHITE) -> Text:
        return Text(text, font=self.font, font_size=size, color=color, line_spacing=0.7)

    @staticmethod
    def fit(obj, width: float):
        if obj.width > width:
            obj.scale_to_fit_width(width)
        return obj

    def photo_layer(self, key: str) -> Group:
        image = ImageMobject(str(self.asset_paths[key]))
        image.scale_to_fit_width(config.frame_width)
        image.move_to(ORIGIN)
        opacity = 0.48 if key == "students" else 0.34
        veil = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=BLACK,
            fill_opacity=opacity,
        ).move_to(ORIGIN)
        return Group(image, veil)

    def make_copy(self, beat: dict) -> Group:
        lines = beat["screen"]
        if beat["id"] == "hook":
            return Group(
                self.fit(self.label(lines[0], 58), 12.0).move_to([0, -0.65, 0]),
            )
        if beat["id"] == "major":
            return Group(
                self.fit(self.label(lines[0], 50), 12.0).move_to([0, 0.45, 0]),
                self.fit(self.label(lines[1], 31, SOFT_WHITE), 11.0).move_to([0, -0.55, 0]),
            )
        if beat["id"] == "certificate":
            return Group(
                self.fit(self.label(lines[0], 30, SOFT_WHITE), 10.0).move_to([0, 1.15, 0]),
                self.fit(self.label(lines[1], 43), 12.0).move_to([0, 0.15, 0]),
                self.fit(self.label(lines[2], 43), 12.0).move_to([0, -0.65, 0]),
            )
        return Group(
            self.fit(self.label(lines[0], 47), 11.5).move_to([0, 0.65, 0]),
            self.fit(self.label(lines[1], 50, UQAM_BLUE), 11.5).move_to([0, -0.15, 0]),
            self.fit(self.label(lines[2], 27, SOFT_WHITE), 8.0).move_to([0, -1.45, 0]),
        )

    def make_act(self, beat: dict) -> Group:
        return Group(self.photo_layer(beat["background"]), self.make_copy(beat))

    def check_layout(self, beat_id: str, group: Group) -> None:
        """Enforce sparse copy and keep every text object out of subtitle space."""
        records = []
        for obj in group.get_family():
            if not isinstance(obj, Text):
                continue
            box = [
                float(obj.get_left()[0]),
                float(obj.get_right()[0]),
                float(obj.get_bottom()[1]),
                float(obj.get_top()[1]),
            ]
            if box[0] < -6.55 or box[1] > 6.55 or box[2] < -2.30 or box[3] > 3.45:
                raise ValueError(f"Text outside safe area: {beat_id}: {obj.text}")
            records.append({"text": obj.text, "box": box})
        if len(records) > 3:
            raise ValueError(f"Too many text objects in sparse beat {beat_id}")
        for i, a in enumerate(records):
            for b in records[i + 1 :]:
                x1, x2, y1, y2 = a["box"]
                u1, u2, v1, v2 = b["box"]
                if min(x2, u2) - max(x1, u1) > 0.02 and min(y2, v2) - max(y1, v1) > 0.02:
                    raise ValueError(f"Overlapping labels: {a['text']} / {b['text']}")
        self.layout.append({"beat": beat_id, "labels": records})

    def construct(self) -> None:
        self.spec = load_project()
        self.asset_paths = validate_assets(self.spec)
        mode = os.getenv("UQAM_OUVERTURES_MODE", "azure")
        if mode not in {"azure", "silent"}:
            raise ValueError("UQAM_OUVERTURES_MODE must be azure or silent")
        silent = mode == "silent"

        self.font = self.spec["font"]
        font_path = ROOT / "assets/uqam_promo/fonts/Roboto-VariableFont_wdth,wght.ttf"
        if font_path.is_file():
            register_font(str(font_path))
        if self.font not in list_fonts():
            if not silent:
                raise RuntimeError("Roboto is required for narrated review; install or register it")
            self.font = "DejaVu Sans"

        selector = os.getenv(
            "UQAM_OUVERTURES_VOICE",
            os.getenv("UQAM_PROMO_VOICE", os.getenv("MANIM_VOICE", self.spec["voice_selector"])),
        )
        voice = resolve_voice(selector)
        rate = os.getenv("UQAM_OUVERTURES_RATE", self.spec["voice_rate"])
        if not silent:
            configure_azure_speech_environment(voice, require_credentials=True)
            # Captions are generated from the measured timeline by build.py.
            # Disabling VoiceoverScene's duplicate captions also avoids passing
            # an empty caption through its chunking code.
            self.set_speech_service(
                AzureService(**azure_service_kwargs(voice)), create_subcaption=False
            )

        if silent:
            preview_mark = self.label("APERÇU MUET — VOIX AZURE NON INCLUSE", 14, SOFT_WHITE)
            preview_mark.move_to([0, 3.62, 0])
            self.add(preview_mark)

        self.timeline: list[dict] = []
        self.layout: list[dict] = []
        previous = None
        for beat in self.spec["beats"]:
            act = self.make_act(beat)
            self.check_layout(beat["id"], act)
            start = float(self.renderer.time)
            context = nullcontext(None) if silent else self.voiceover(
                text=ssml(
                    beat["text"],
                    rate=rate,
                    locale=VOICE_LOCALES.get(voice, "fr-CA"),
                ),
            )
            with context as tracker:
                speech_seconds = None if silent else float(tracker.duration)
                slot = beat["seconds"] if silent else max(beat["seconds"], speech_seconds + 0.12)
                if previous is not None:
                    self.play(FadeOut(previous), run_time=0.28)
                self.play(FadeIn(act), run_time=0.52)
                remaining = slot - (float(self.renderer.time) - start)
                if remaining > 0:
                    self.wait(remaining)
            end = float(self.renderer.time)
            self.timeline.append(
                {
                    "id": beat["id"],
                    "start": start,
                    "end": end,
                    "caption": beat["caption"],
                    "speech_seconds": speech_seconds,
                    "background": beat["background"],
                    "source_pages": beat["source_pages"],
                }
            )
            previous = act

        destination = Path(
            os.getenv(
                "UQAM_OUVERTURES_TIMELINE",
                str(ROOT / "media/bac_sciences_ouvertures_fr/timeline.json"),
            )
        )
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(
                {
                    "mode": mode,
                    "font": self.font,
                    "voice": None if silent else voice,
                    "voice_selector": selector,
                    "rate": rate,
                    "beats": self.timeline,
                    "duration": float(self.renderer.time),
                    "layout": self.layout,
                    "visual_concept": self.spec["visual_concept"],
                    "listening_review": "not_performed",
                    "institutional_approval": "not_inferred",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
