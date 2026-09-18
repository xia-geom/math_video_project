"""Sparse UQAM photo film: a measured audio package, not fresh TTS per render."""
from __future__ import annotations

import json
import os
from pathlib import Path

from manim import BLACK, FadeIn, FadeOut, Group, ImageMobject, Rectangle, Text, config
from manim_voiceover import VoiceoverScene
from manimpango import list_fonts, register_font

from miscellaneous.bac_sciences_ouvertures_fr.narration import selection, verify_package
from miscellaneous.bac_sciences_ouvertures_fr.project import ROOT, inspect_assets, load_project
from miscellaneous.bac_sciences_ouvertures_fr.timing import plan_timeline

config.background_color = BLACK


class BacSciencesOuverturesFR(VoiceoverScene):
    """Use AzureService upstream; render only the exact already-measured clips."""

    def label(self, text: str, size: int, y: float, color: str = "#FFFFFF") -> Text:
        item = Text(text, font=self.font, font_size=size, color=color)
        if item.width > 12:
            item.scale_to_fit_width(12)
        return item.move_to([0, y, 0]).set_z_index(10)

    def photo_layer(self, key: str) -> Group:
        image = ImageMobject(str(self.asset_paths[key]))
        # Uniform cover scaling, never stretch a photograph to a different ratio.
        image.scale(max(config.frame_width / image.width, config.frame_height / image.height))
        image.move_to([0, 0, 0])
        veil = Rectangle(width=config.frame_width, height=3.55, stroke_width=0,
                         fill_color=BLACK, fill_opacity=0.76).move_to([0, -2.225, 0])
        return Group(image, veil)

    def make_copy(self, beat: dict, second_pair: bool = False) -> Group:
        lines = beat["screen"]
        if beat["id"] == "hook":
            return Group(self.label(lines[0], 56, -1.30))
        if beat["id"] == "major":
            return Group(self.label(lines[0], 48, -1.20), self.label(lines[1], 30, -2.08))
        if beat["id"] == "certificate":
            return Group(self.label(lines[0], 30, -0.95),
                         self.label(lines[2 if second_pair else 1], 43, -1.85))
        return Group(self.label(lines[0], 47, -0.90),
                     self.label(lines[1], 49, -1.67, "#64C7F2"),
                     self.label(lines[2], 27, -2.43))

    def check_layout(self, beat_id: str, group: Group) -> None:
        records = []
        for item in group.get_family():
            if not isinstance(item, Text):
                continue
            box = [float(item.get_left()[0]), float(item.get_right()[0]),
                   float(item.get_bottom()[1]), float(item.get_top()[1])]
            if box[0] < -6.55 or box[1] > 6.55 or box[2] < -2.72 or box[3] > 3.45:
                raise ValueError(f"Text outside safe area: {beat_id}: {item.text}")
            records.append({"text": item.text, "box": box})
        if len(records) > 3:
            raise ValueError("More than three visible text lines")
        for i, a in enumerate(records):
            for b in records[i + 1:]:
                x1, x2, y1, y2 = a["box"]
                u1, u2, v1, v2 = b["box"]
                if min(x2, u2) > max(x1, u1) and min(y2, v2) > max(y1, v1):
                    raise ValueError(f"Text overlap: {a['text']} / {b['text']}")
        self.layout.append({"beat": beat_id, "labels": records})

    def check_live_copy(self, copy: Group) -> None:
        """Reject stale text promoted to scene roots by subgroup animations."""
        expected = {id(item) for item in copy.get_family() if isinstance(item, Text)}
        visible = {id(item) for root in self.mobjects for item in root.get_family()
                   if isinstance(item, Text) and item.z_index < 100}
        if visible != expected:
            raise ValueError("Stale or missing text after a scene transition")

    def wait_until(self, target: float) -> None:
        remaining = target - float(self.renderer.time)
        if remaining < -1.1 / self.fps:
            raise ValueError("Animation exceeds its frame budget")
        if remaining > 0.5 / self.fps:
            self.wait(round(remaining * self.fps) / self.fps)

    def construct(self) -> None:
        spec = load_project()
        mode = os.getenv("UQAM_OUVERTURES_MODE", "azure")
        if mode not in {"azure", "silent"}:
            raise ValueError("Invalid render mode")
        silent = mode == "silent"
        self.asset_paths, asset_evidence = inspect_assets(spec, require_native=not silent)
        self.fps = int(config.frame_rate)
        self.font = spec["font"]
        font_path = ROOT / "assets/uqam_promo/fonts/Roboto-VariableFont_wdth,wght.ttf"
        if font_path.is_file():
            register_font(str(font_path))
        if self.font not in list_fonts():
            self.font = "DejaVu Sans"
        package = None
        if not silent:
            package_path = Path(os.environ["UQAM_OUVERTURES_AUDIO_PACKAGE"])
            package = verify_package(spec, package_path)
        durations = None if package is None else [c["duration_seconds"] for c in package["clips"]]
        plan = plan_timeline(spec, durations, self.fps)
        self.layout = []
        previous_copy = None
        background = None
        background_key = None
        if silent:
            note = "APERÇU MUET"
            if not asset_evidence["native_source_recovered"]:
                note += " — IMAGES DE CONTRÔLE BASSE RÉSOLUTION"
            disclosure_back = Rectangle(width=config.frame_width, height=0.32,
                                        stroke_width=0, fill_color=BLACK, fill_opacity=0.75)
            disclosure_back.move_to([0, 3.65, 0]).set_z_index(99)
            self.add(disclosure_back, self.label(note, 14, 3.62).set_z_index(100))
        timeline = []
        review_times = []
        for i, (beat, row) in enumerate(zip(spec["beats"], plan["beats"], strict=True)):
            self.wait_until(row["start"])
            copy = self.make_copy(beat)
            self.check_layout(beat["id"], copy)
            if package is not None:
                audio = package_path.parent / package["clips"][i]["path"]
                self.add_sound(str(audio), time_offset=row["lead_frames"] / self.fps)
            lead = row["lead_frames"]
            outgoing = 0 if previous_copy is None else max(1, round(0.15 * self.fps))
            if previous_copy is not None:
                old_family = previous_copy.get_family()
                self.play(FadeOut(previous_copy), run_time=outgoing / self.fps)
                self.remove(*old_family)
            incoming = lead - outgoing
            transitions = [FadeIn(copy)]
            if beat["background"] != background_key:
                new_background = self.photo_layer(beat["background"])
                if background is None:
                    self.add(new_background)
                else:
                    # Crossfade over the old photo rather than briefly exposing black.
                    transitions.append(FadeIn(new_background))
            else:
                new_background = background
            self.play(*transitions, run_time=incoming / self.fps)
            if new_background is not background and background is not None:
                self.remove(background)
            background, background_key = new_background, beat["background"]
            self.check_live_copy(copy)
            review_times.append({"id": beat["id"] + "_settled", "seconds": row["start"] + 0.8})
            if beat["id"] == "certificate":
                midpoint = (row["start"] + row["end"]) / 2
                self.wait_until(midpoint)
                second = self.make_copy(beat, second_pair=True)
                self.check_layout("certificate_second_pair", second)
                # Header and background stay still; only the two field names change.
                fade = max(1, round(0.15 * self.fps)) / self.fps
                old_family = copy.get_family()
                header = copy[0]
                self.play(FadeOut(copy[1]), run_time=fade)
                # Manim may promote the untouched header to a scene root when
                # a child fades out. Remove that exact old family, then regroup
                # the same header with the new pair (no visible header blink).
                self.remove(*old_family)
                copy = Group(header, second[1])
                self.add(copy)
                self.play(FadeIn(copy[1]), run_time=fade)
                self.check_live_copy(copy)
                review_times.append({"id": "certificate_second_pair", "seconds": midpoint + 0.6})
            self.wait_until(row["end"])
            previous_copy = copy
            timeline.append({**row, "background": beat["background"],
                             "source_pages": beat["source_pages"]})
            if i:
                review_times.extend([
                    {"id": f"boundary_{i}_before", "seconds": row["start"] - 1 / self.fps},
                    {"id": f"boundary_{i}_during", "seconds": row["start"] + 0.2},
                ])
        review_times.append({"id": "end_card", "seconds": spec["target_seconds"] - 0.5})
        selector, voice, rate, _ = selection(spec)
        destination = Path(os.getenv("UQAM_OUVERTURES_TIMELINE", str(ROOT / "media/uqam_timeline.json")))
        destination.parent.mkdir(parents=True, exist_ok=True)
        result = {"mode": mode, "font": self.font, "voice": None if silent else voice,
                  "voice_selector": selector, "rate": rate, "beats": timeline,
                  "duration": float(self.renderer.time), "layout": self.layout,
                  "plan": plan, "asset_quality": asset_evidence,
                  "review_times": review_times, "visual_concept": spec["visual_concept"],
                  "field_pair_timing": "visual_midpoint_not_word_alignment",
                  "listening_review": "not_performed", "institutional_approval": "not_inferred"}
        destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
