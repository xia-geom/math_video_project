"""Twenty-second UQAM film with independently timed photos and messages.

Photographs dissolve over an opaque predecessor, under one persistent veil.
Text never crossfades into other text. Extra photographs do not change the
approved four-beat narration, voice profile, subtitles or total silent duration.
"""
from __future__ import annotations

import json
import os
from contextlib import nullcontext
from pathlib import Path

from manim import (
    BLACK,
    ORIGIN,
    Group,
    ImageMobject,
    Rectangle,
    Text,
    UpdateFromAlphaFunc,
    VGroup,
    config,
    linear,
)
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService
from manimpango import list_fonts, register_font

from miscellaneous.bac_sciences_ouvertures_fr.project import (
    ROOT,
    load_project,
    validate_assets,
)
from miscellaneous.bac_sciences_ouvertures_fr.visual_timing import (
    copy_opacities,
    dissolve_opacities,
    ease,
    shot_plan,
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
    """One full-frame photograph and one short, readable message at a time."""

    def label(self, text: str, size: int, color: str = INK_WHITE) -> Text:
        return Text(text, font=self.font, font_size=size, color=color, line_spacing=0.7)

    @staticmethod
    def fit(obj, width: float):
        if obj.width > width:
            obj.scale_to_fit_width(width)
        return obj

    def make_copy(self, beat: dict) -> VGroup:
        lines = beat["screen"]
        # Lower-third placement frees faces and activity in the upper image.
        if beat["id"] == "hook":
            return VGroup(self.fit(self.label(lines[0], 56), 12.0).move_to([0, -1.15, 0]))
        if beat["id"] == "major":
            return VGroup(
                self.fit(self.label(lines[0], 46), 12.0).move_to([0, -0.90, 0]),
                self.fit(self.label(lines[1], 32, SOFT_WHITE), 11.2).move_to([0, -1.72, 0]),
            )
        if beat["id"] == "openings":
            return VGroup(
                self.fit(self.label(lines[0], 29, SOFT_WHITE), 10.5).move_to([0, -0.30, 0]),
                self.fit(self.label(lines[1], 40), 12.0).move_to([0, -1.05, 0]),
                self.fit(self.label(lines[2], 40), 12.0).move_to([0, -1.82, 0]),
            )
        return VGroup(
            self.fit(self.label(lines[0], 49, UQAM_BLUE), 11.5).move_to([0, 0.35, 0]),
            self.fit(self.label(lines[1], 43), 11.5).move_to([0, -0.45, 0]),
            self.fit(self.label(lines[2], 29, SOFT_WHITE), 8.0).move_to([0, -1.65, 0]),
        )

    def check_layout(self, beat_id: str, group: Group) -> None:
        records = []
        for obj in group.get_family():
            if not isinstance(obj, Text):
                continue
            box = [float(obj.get_left()[0]), float(obj.get_right()[0]),
                   float(obj.get_bottom()[1]), float(obj.get_top()[1])]
            if box[0] < -6.55 or box[1] > 6.55 or box[2] < -2.30 or box[3] > 3.45:
                raise ValueError(f"Text outside safe area: {beat_id}: {obj.text}")
            records.append({"text": obj.text, "box": box})
        if len(records) > 3:
            raise ValueError(f"Too many message labels in sparse beat {beat_id}")
        for i, a in enumerate(records):
            for b in records[i + 1:]:
                x1, x2, y1, y2 = a["box"]
                u1, u2, v1, v2 = b["box"]
                if min(x2, u2) - max(x1, u1) > 0.02 and min(y2, v2) - max(y1, v1) > 0.02:
                    raise ValueError(f"Overlapping labels: {a['text']} / {b['text']}")
        self.layout.append({"beat": beat_id, "labels": records})

    def prepare_stage(self, silent: bool) -> None:
        self.stage = Group()
        self.images, self.credits, self.last_opacity = {}, {}, {}
        keys = [key for beat in self.spec["beats"]
                for key in beat.get("photos", [beat["background"]])]
        for order, key in enumerate(keys):
            asset = self.spec["assets"][key]
            image = ImageMobject(str(self.asset_paths[key]))
            # Cover both dimensions, with overscan sufficient for the small pan.
            image.scale(max(config.frame_width / image.width,
                            config.frame_height / image.height) * 1.025)
            # Place each photograph once; only its opacity changes during dissolves.
            anchor = asset.get("crop_anchor", [0.5, 0.5])
            x_room = (image.width - config.frame_width) / 2
            y_room = (image.height - config.frame_height) / 2
            x = (1 - 2 * anchor[0]) * x_room
            y = (2 * anchor[1] - 1) * y_room
            image.move_to([max(-x_room, min(x_room, x)), max(-y_room, min(y_room, y)), 0])
            image.set_opacity(0).set_z_index(order)
            self.images[key] = image
            self.last_opacity[key] = 0.0
            credit = self.fit(self.label(asset["credit"], 13, SOFT_WHITE), 5.1)
            credit.move_to([config.frame_width / 2 - credit.width / 2 - 0.25,
                            config.frame_height / 2 - credit.height / 2 - 0.65, 0])
            credit.set_opacity(0).set_z_index(30)
            self.credits[key] = credit
            self.stage.add(image, credit)
        self.veil = Rectangle(width=config.frame_width, height=config.frame_height,
                              stroke_width=0, fill_color=BLACK, fill_opacity=0.36)
        self.veil.move_to(ORIGIN).set_z_index(20)
        self.stage.add(self.veil)
        self.messages = {}
        for beat in self.spec["beats"]:
            message = self.make_copy(beat)
            self.check_layout(beat["id"], message)
            message.set_opacity(0).set_z_index(40)
            if any(m.get_fill_opacity() != 0 for m in message.get_family() if m.has_points()):
                raise ValueError("Message group failed to hide its glyphs")
            self.messages[beat["id"]] = message
            self.stage.add(message)
        if silent:
            mark = self.label("APERÇU MUET — VOIX AZURE NON INCLUSE", 14, SOFT_WHITE)
            mark.move_to([0, 3.62, 0]).set_z_index(50)
            self.stage.add(mark)
        self.add(self.stage)

    def update_photos(self, time: float) -> None:
        shots = self.photo_timeline
        index = max(i for i, shot in enumerate(shots) if shot["start"] <= time + 1e-7)
        current = shots[index]
        previous = shots[index - 1] if index else None
        elapsed = time - current["start"]
        progress = elapsed / self.spec["photo_transition_seconds"]
        lower, upper = dissolve_opacities(progress)
        opacities = {current["key"]: upper if previous else 1.0}
        if previous and progress < 1.0:
            opacities[previous["key"]] = lower
        for key, image in self.images.items():
            opacity = opacities.get(key, 0.0)
            if opacity != self.last_opacity[key]:
                image.set_opacity(opacity)
                self.last_opacity[key] = opacity
            self.credits[key].set_opacity(0)
        before, after = copy_opacities(elapsed, opening=previous is None)
        if previous:
            self.credits[previous["key"]].set_opacity(0.90 * before)
        self.credits[current["key"]].set_opacity(0.90 * after)
        new_shade = self.spec["assets"][current["key"]].get("overlay_opacity", 0.36)
        old_shade = (self.spec["assets"][previous["key"]].get("overlay_opacity", 0.36)
                     if previous else new_shade)
        self.veil.set_fill(opacity=old_shade + ease(progress) * (new_shade - old_shade))

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
        selector = os.getenv("UQAM_OUVERTURES_VOICE", os.getenv("UQAM_PROMO_VOICE",
                             os.getenv("MANIM_VOICE", self.spec["voice_selector"])))
        voice = resolve_voice(selector)
        rate = os.getenv("UQAM_OUVERTURES_RATE", self.spec["voice_rate"])
        if not silent:
            configure_azure_speech_environment(voice, require_credentials=True)
            self.set_speech_service(AzureService(**azure_service_kwargs(voice)), create_subcaption=False)
        self.timeline, self.photo_timeline, self.layout = [], [], []
        self.prepare_stage(silent)
        previous_message = None
        for beat in self.spec["beats"]:
            start = float(self.renderer.time)
            context = nullcontext(None) if silent else self.voiceover(
                text=ssml(beat["text"], rate=rate, locale=VOICE_LOCALES.get(voice, "fr-CA")))
            with context as tracker:
                speech_seconds = None if silent else float(tracker.duration)
                slot = beat["seconds"] if silent else max(beat["seconds"], speech_seconds + 0.12)
                self.photo_timeline.extend(shot_plan(beat, start, slot))
                current_message = self.messages[beat["id"]]

                def update_frame(_stage, alpha):
                    elapsed = float(alpha) * slot
                    self.update_photos(start + elapsed)
                    before, after = copy_opacities(elapsed, opening=previous_message is None)
                    if previous_message is not None:
                        previous_message.set_opacity(before)
                    current_message.set_opacity(after)

                # Animating the complete stage prevents Cairo from treating a
                # photograph or foreground text modified by the callback as static.
                self.play(UpdateFromAlphaFunc(self.stage, update_frame), run_time=slot, rate_func=linear)
            end = float(self.renderer.time)
            self.timeline.append({"id": beat["id"], "start": start, "end": end,
                                  "caption": beat["caption"], "speech_seconds": speech_seconds,
                                  "background": beat["background"], "source_pages": beat["source_pages"]})
            previous_message = current_message
        destination = Path(os.getenv("UQAM_OUVERTURES_TIMELINE",
                           str(ROOT / "media/bac_sciences_ouvertures_fr/timeline.json")))
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps({
            "mode": mode, "font": self.font, "voice": None if silent else voice,
            "voice_selector": selector, "rate": rate, "beats": self.timeline,
            "photos": self.photo_timeline, "photo_transition_seconds": self.spec["photo_transition_seconds"],
            "photo_zoom": self.spec["photo_zoom"], "duration": float(self.renderer.time),
            "layout": self.layout, "visual_concept": self.spec["visual_concept"],
            "listening_review": "not_performed", "institutional_approval": "not_inferred",
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
