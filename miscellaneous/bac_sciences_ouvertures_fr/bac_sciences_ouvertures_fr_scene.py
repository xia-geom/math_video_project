"""20-second UQAM interdisciplinary-pathway clip; Manim CE + shared Azure TTS.

Silent previews are explicit and watermarked. Narrated output never silently
falls back to a different service, voice or a word-count timing estimate.
"""
from __future__ import annotations

import json
import os
from contextlib import nullcontext
from pathlib import Path

from manim import (
    DOWN, WHITE, FadeIn, FadeOut, LaggedStart, Line,
    RoundedRectangle, Text, VGroup, config,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from manimpango import list_fonts, register_font

from miscellaneous.bac_sciences_ouvertures_fr.project import ROOT, load_project
from tools.tts import (
    VOICE_LOCALES, azure_service_kwargs, configure_azure_speech_environment,
    resolve_voice, ssml,
)

BLUE_UQAM = "#0079BE"
INK = "#312F2D"
MUTED = "#59616B"
PALE = "#F1F6FA"
config.background_color = WHITE


class BacSciencesOuverturesFR(VoiceoverScene):
    """Majeure -> one complementary certificate -> bachelor by accumulation."""

    def label(self, text, size=32, color=INK):
        return Text(text, font=self.font, font_size=size, color=color, line_spacing=0.6)

    def fit(self, obj, width):
        if obj.width > width:
            obj.scale_to_fit_width(width)
        return obj

    def card(self, text, center, width=3.05, height=1.15, size=28):
        box = RoundedRectangle(
            width=width, height=height, corner_radius=0.12,
            stroke_color=BLUE_UQAM, stroke_width=2.2,
            fill_color=PALE, fill_opacity=1,
        ).move_to(center)
        label = self.fit(self.label(text, size), width - 0.35).move_to(box)
        return VGroup(box, label)

    def check_layout(self, beat_id, group):
        """Check frame/subtitle-safe bounds, including every text glyph group."""
        records = []
        for obj in group.get_family():
            if not isinstance(obj, Text):
                continue
            box = [float(obj.get_left()[0]), float(obj.get_right()[0]),
                   float(obj.get_bottom()[1]), float(obj.get_top()[1])]
            if box[0] < -6.6 or box[1] > 6.6 or box[2] < -2.65 or box[3] > 3.65:
                raise ValueError(f"Text outside safe area: {beat_id}: {obj.text}")
            records.append({"text": obj.text, "box": box})
        # Text groups should never overlap. Background boxes intentionally contain text.
        for i, a in enumerate(records):
            for b in records[i + 1:]:
                x1, x2, y1, y2 = a["box"]
                u1, u2, v1, v2 = b["box"]
                if min(x2, u2) - max(x1, u1) > 0.02 and min(y2, v2) - max(y1, v1) > 0.02:
                    raise ValueError(f"Overlapping labels: {a['text']} / {b['text']}")
        self.layout.append({"beat": beat_id, "labels": records})

    def make_act(self, beat_id):
        if beat_id == "hook":
            return VGroup(
                self.label("Les maths,", 70).move_to([0, 1.15, 0]),
                self.label("et après ?", 70, BLUE_UQAM).move_to([0, -0.05, 0]),
                self.label("Garde tes options ouvertes.", 30).move_to([0, -1.45, 0]),
            )
        if beat_id == "major":
            return VGroup(
                self.label("UNE BASE SCIENTIFIQUE", 28, BLUE_UQAM).move_to([0, 2.9, 0]),
                self.label("2 ans", 78).move_to([0, 1.6, 0]),
                self.label("à temps plein", 22, MUTED).move_to([0, 0.72, 0]),
                self.label("Mathématiques ou statistique", 38).move_to([0, -0.3, 0]),
                self.card("Une majeure", [0, -1.6, 0], width=5.1, height=0.95, size=32),
            )
        if beat_id == "certificate":
            cards = VGroup(*[
                self.card(text, center, width=3.35, size=27)
                for text, center in zip(self.spec["fields"], [
                    [0.25, 1.05, 0], [4.0, 1.05, 0],
                    [0.25, -0.55, 0], [4.0, -0.55, 0],
                ], strict=True)
            ])
            return VGroup(
                self.label("UN CERTIFICAT AU CHOIX", 36, BLUE_UQAM).move_to([0, 2.8, 0]),
                self.card("Ta majeure\nmaths ou statistique", [-4.5, 0.25, 0],
                          width=3.15, height=2.1, size=26),
                self.label("+", 54, BLUE_UQAM).move_to([-2.3, 0.25, 0]),
                cards,
                self.label("Une ouverture vers une autre discipline.", 28).move_to([0, -1.9, 0]),
            )
        return VGroup(
            self.label("BACCALAURÉAT PAR CUMUL", 30, BLUE_UQAM).move_to([0, 2.8, 0]),
            self.label("Un bac en sciences", 54).move_to([0, 1.35, 0]),
            self.label("à ton image.", 54, BLUE_UQAM).move_to([0, 0.25, 0]),
            Line([-4.5, -0.65, 0], [4.5, -0.65, 0], color=BLUE_UQAM, stroke_width=2),
            # Plain typeset name, not an imitation or unauthorized official logo.
            self.label("UQAM", 31).move_to([0, -1.15, 0]),
            self.label(self.spec["cta_display"], 28, BLUE_UQAM).move_to([0, -1.9, 0]),
        )

    def construct(self):
        self.spec = load_project()
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
            self.font = "DejaVu Sans"  # explicit preview-only fallback, recorded below
        selector = os.getenv("UQAM_OUVERTURES_VOICE", os.getenv(
            "UQAM_PROMO_VOICE", os.getenv("MANIM_VOICE", self.spec["voice_selector"])))
        voice = resolve_voice(selector)
        rate = os.getenv("UQAM_OUVERTURES_RATE", self.spec["voice_rate"])
        if not silent:
            configure_azure_speech_environment(voice, require_credentials=True)
            self.set_speech_service(AzureService(**azure_service_kwargs(voice)))

        qualifier = self.fit(self.label(self.spec["qualifier"], 18, MUTED), 12.5)
        qualifier.move_to([0, -2.48, 0])
        self.add(qualifier)
        if silent:
            preview_mark = self.label("APERÇU MUET — VOIX AZURE NON INCLUSE", 15, MUTED)
            preview_mark.move_to([0, 3.65, 0])
            self.add(preview_mark)
        self.timeline, self.layout = [], []
        previous = None
        for beat in self.spec["beats"]:
            act = self.make_act(beat["id"])
            self.check_layout(beat["id"], act)
            start = float(self.renderer.time)
            context = nullcontext(None) if silent else self.voiceover(
                text=ssml(beat["text"], rate=rate, locale=VOICE_LOCALES.get(voice, "fr-CA")),
                subcaption="",  # the build writes matching SRT from the actual timeline
            )
            with context as tracker:
                speech_seconds = None if silent else float(tracker.duration)
                slot = beat["seconds"] if silent else max(beat["seconds"], speech_seconds + 0.12)
                if previous is not None:
                    self.play(FadeOut(previous), run_time=0.25)
                self.play(LaggedStart(*[
                    FadeIn(obj, shift=0.13 * DOWN) for obj in act
                ], lag_ratio=0.10), run_time=0.9)
                remaining = slot - (float(self.renderer.time) - start)
                if remaining > 0:
                    self.wait(remaining)
            end = float(self.renderer.time)
            self.timeline.append({
                "id": beat["id"], "start": start, "end": end,
                "caption": beat["caption"], "speech_seconds": speech_seconds,
                "source_pages": beat["source_pages"],
            })
            previous = act
        destination = Path(os.getenv("UQAM_OUVERTURES_TIMELINE",
                                     str(ROOT / "media/bac_sciences_ouvertures_fr/timeline.json")))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps({
            "mode": mode, "font": self.font, "voice": None if silent else voice,
            "voice_selector": selector, "rate": rate, "beats": self.timeline,
            "duration": float(self.renderer.time), "layout": self.layout,
            "listening_review": "not_performed", "institutional_approval": "not_inferred",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
