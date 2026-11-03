"""Five clear steps towards a B.Sc.; complete film capped at thirty seconds."""

from __future__ import annotations

import json
import os
from contextlib import nullcontext
from pathlib import Path

from manim import (
    DOWN,
    WHITE,
    AnimationGroup,
    FadeIn,
    FadeOut,
    Group,
    ImageMobject,
    Rectangle,
    Succession,
    Text,
    Wait,
    config,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from manim_voiceover.tracker import get_duration
from manimpango import list_fonts, register_font

from miscellaneous.bac_sciences_ouvertures_fr.project import (
    ROOT,
    allocate_slots,
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
from tools.uqam_promo_layout import check_copy_layout, mark_copy, photo_canvas

INK = "#24333D"
BLUE = "#0079BE"
config.background_color = WHITE


class BacSciencesOuverturesFR(VoiceoverScene):
    def label(self, text: str, size: int, color=INK, role="message"):
        return mark_copy(Text(text, font=self.font, font_size=size, color=color), text, role=role)

    def background(self, beat: dict):
        canvas = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            stroke_width=0,
            fill_color=WHITE,
            fill_opacity=1,
        )
        key = beat["background"]
        if key is None:
            return Group(canvas)
        asset = self.spec["assets"][key]
        if beat["layout"] == "split":
            photo = photo_canvas(
                self.asset_paths[key], width=6.6, height=4.67, center=(3.35, 0.20),
                focal=tuple(asset.get("focal", (0.5, 0.5))),
            )
            group = Group(photo)
            credit_color = INK
        else:
            photo = photo_canvas(
                self.asset_paths[key],
                width=config.frame_width,
                height=config.frame_height,
                focal=(0.5, 0.42),
                veil=max(0.52, asset.get("overlay_opacity", 0.52)),
            )
            group = Group(photo)
            credit_color = WHITE
        if self.spec.get("show_photo_credits", True):
            credit = self.label(asset["credit"], 14, credit_color, role="credit")
            credit.move_to([config.frame_width / 2 - credit.width / 2 - 0.30, 3.20, 0])
            group.photo_credit = credit
        return group

    def make_copy(self, beat: dict):
        lines = beat["screen"]
        if beat["id"] == "hook":
            group = Group(self.label(lines[0], 45, BLUE), self.label(lines[1], 36))
            group.arrange(DOWN, buff=0.30)
            group.move_to([-3.65, 0.25, 0])
        elif beat["id"] == "major":
            group = Group(
                self.label(lines[0], 43, BLUE).move_to([-3.65, 1.10, 0]),
                self.label(lines[1], 29).move_to([-3.65, 0.05, 0]),
                self.label(lines[2], 27).move_to([-3.65, -0.85, 0]),
            )
        elif beat["id"] == "openings":
            group = Group(
                self.label(lines[0], 45, BLUE).move_to([0, 1.10, 0]),
                self.label(lines[1], 39).move_to([0, 0.00, 0]),
                self.label(lines[2], 39).move_to([0, -0.82, 0]),
            )
        elif beat["id"] == "degree":
            group = Group(
                self.label(lines[0], 46, BLUE).move_to([0, 0.50, 0]),
                self.label(lines[1], 34).move_to([0, -0.50, 0]),
            )
        else:
            group = Group(
                self.label(lines[0], 40, BLUE).move_to([-3.65, 0.85, 0]),
                self.label(lines[1], 36).move_to([-3.65, -0.05, 0]),
                self.label(lines[2], 28, BLUE, role="cta").move_to([-3.65, -1.20, 0]),
            )
        return group.set_z_index(20)

    def transition(self, old_background, old_copy, background, copy, seconds):
        # The old photograph stays opaque until its successor covers it. Only
        # one principal message is present at a time: no double text or black dip.
        if old_copy is None:
            self.add(background)
            self.play(FadeIn(copy), run_time=seconds)
            return
        if background is old_background:
            # Consecutive white pathway cards use a clean cut. Fading both
            # messages out/in left an empty white frame between the two ideas.
            self.remove(old_copy)
            self.add(copy)
            self.wait(seconds)
            return
        exchange = Succession(
            FadeOut(old_copy, run_time=0.18), Wait(0.16), FadeIn(copy, run_time=seconds - 0.34)
        )
        self.play(AnimationGroup(FadeIn(background, run_time=seconds), exchange, lag_ratio=0))
        self.remove(old_background)

    def construct(self):
        self.spec = load_project()
        self.asset_paths = validate_assets(self.spec)
        mode = os.getenv("UQAM_OUVERTURES_MODE", "azure")
        if mode not in {"silent", "azure"}:
            raise ValueError("Select silent or azure explicitly")
        silent = mode == "silent"
        self.font = self.spec["font"]
        font_path = ROOT / "assets/uqam_promo/fonts/Roboto-VariableFont_wdth,wght.ttf"
        if font_path.exists():
            register_font(str(font_path))
        if self.font not in list_fonts():
            raise RuntimeError("Install Roboto before rendering the reviewed layout")
        selector = os.getenv(
            "UQAM_OUVERTURES_VOICE",
            os.getenv("UQAM_PROMO_VOICE", os.getenv("MANIM_VOICE", self.spec["voice_selector"])),
        )
        voice = resolve_voice(selector)
        rate = os.getenv("UQAM_OUVERTURES_RATE", self.spec["voice_rate"])
        spoken = [
            ssml(b["text"], rate=rate, locale=VOICE_LOCALES.get(voice, "fr-CA"))
            for b in self.spec["beats"]
        ]
        speech = None
        slots = [b["seconds"] for b in self.spec["beats"]]
        if not silent:
            configure_azure_speech_environment(voice, require_credentials=True)
            self.set_speech_service(
                AzureService(
                    **azure_service_kwargs(voice), cache_dir=ROOT / "media" / "voiceovers"
                ), create_subcaption=False
            )
            # Prewarm exactly the same pinned manim-voiceover 0.3.7 cache path
            # used by voiceover(). Reject a duration overrun BEFORE any frames.
            cached = [self.speech_service._wrap_generate_from_text(text) for text in spoken]
            speech = [
                get_duration(Path(self.speech_service.cache_dir) / item["final_audio"])
                for item in cached
            ]
            slots = allocate_slots(self.spec, speech, float(config.frame_rate))
        if silent:
            preview = self.label("APERÇU MUET — VOIX NON INCLUSE", 14, BLUE, role="preview")
            panel = Rectangle(
                width=preview.width + 0.25,
                height=preview.height + 0.12,
                stroke_width=0,
                fill_color=WHITE,
                fill_opacity=1,
            )
            panel.move_to([0, 3.62, 0])
            preview.move_to(panel)
            self.add_foreground_mobjects(Group(panel, preview).set_z_index(10000))
        self.timeline, self.layout = [], []
        old_background = old_copy = None
        for index, (beat, slot) in enumerate(zip(self.spec["beats"], slots)):
            background = old_background if beat.get("keep_background") else self.background(beat)
            copy = self.make_copy(beat)
            if hasattr(background, "photo_credit"):
                copy.add(background.photo_credit.copy())
            start = float(self.renderer.time)
            context = nullcontext(None) if silent else self.voiceover(text=spoken[index])
            with context as tracker:
                actual_speech = None if silent else float(tracker.duration)
                if speech is not None and abs(actual_speech - speech[index]) > 0.03:
                    raise RuntimeError("Speech changed after measured timing preflight")
                self.transition(
                    old_background, old_copy, background, copy, self.spec["transition_seconds"]
                )
                self.layout.append(check_copy_layout(self.mobjects, beat["id"]))
                target_frame = round(sum(slots[: index + 1]) * config.frame_rate)
                remaining_frames = target_frame - round(
                    float(self.renderer.time) * config.frame_rate
                )
                logo_outro = index == len(slots) - 1 and self.spec.get("official_logo")
                outro_frames = round(1.5 * config.frame_rate) if logo_outro else 0
                if remaining_frames > outro_frames:
                    self.wait((remaining_frames - outro_frames) / config.frame_rate + 1e-8)
                if logo_outro:
                    logo_path = ROOT / "assets/branding/uqam_logo.png"
                    if not logo_path.is_file():
                        raise FileNotFoundError(logo_path)
                    white_card = Rectangle(width=config.frame_width, height=config.frame_height,
                                           stroke_width=0, fill_color=WHITE, fill_opacity=1)
                    logo = ImageMobject(str(logo_path)).scale_to_fit_width(4.0)
                    self.play(FadeIn(white_card), FadeOut(copy), run_time=0.35)
                    self.add(white_card)
                    self.play(FadeIn(logo), run_time=0.4)
                    self.wait(0.75)
            end = float(self.renderer.time)
            caption_end = start + actual_speech if actual_speech is not None else end
            if silent and index == len(slots) - 1:
                caption_end -= self.spec["final_hold_seconds"]
            self.timeline.append(
                {
                    "id": beat["id"],
                    "start": start,
                    "end": end,
                    "caption_end": caption_end,
                    "caption": beat["caption"],
                    "speech_seconds": actual_speech,
                    "background": beat["background"],
                    "photo_credit": None if beat["background"] is None else {
                        "required": self.spec["assets"][beat["background"]]["full_credit"],
                        "displayed": self.spec.get("show_photo_credits", True),
                        "source": self.spec["assets"][beat["background"]]["source_url"],
                    },
                    "source_pages": beat["source_pages"],
                    "transition_seconds": self.spec["transition_seconds"],
                }
            )
            old_background, old_copy = background, copy
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
                    "timing_source": "storyboard_only"
                    if silent
                    else "measured_speech_before_render",
                    "final_hold_seconds": self.spec["final_hold_seconds"],
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
