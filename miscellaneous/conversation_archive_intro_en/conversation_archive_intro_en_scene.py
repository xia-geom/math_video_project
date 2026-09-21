"""English product explainer. Silent, captioned, synthetic; no network or TTS.

The storage-architecture beat is explicitly a target, not a release claim.
Use the project build.py for isolated output and ffprobe validation.
"""
from __future__ import annotations

import json
from pathlib import Path

from manim import (
    BLACK, BLUE_D, DOWN, RIGHT, UP, WHITE,
    Arrow, Create, DashedLine, FadeIn, FadeOut, LaggedStart,
    Line, RoundedRectangle, Scene, Text, VGroup, config,
)

INK = BLACK
ACCENT = BLUE_D
MUTED = "#526171"
BORDER = "#CAD2DC"
FONT = "DejaVu Sans"
HERE = Path(__file__).resolve().parent


def label(text, size=28, color=INK, font=FONT):
    return Text(text, font=font, font_size=size, color=color, line_spacing=1.05)


def card(title, body, x=0, y=0.2, width=3.6, height=1.7):
    box = RoundedRectangle(width=width, height=height, corner_radius=0.12,
                           stroke_color=BORDER, stroke_width=2, fill_color=WHITE,
                           fill_opacity=1)
    heading = label(title, 28, ACCENT).move_to(box.get_top() + DOWN * 0.36)
    content = label(body, 26).move_to(box.get_center() + DOWN * 0.23)
    for text in (heading, content):
        if text.width > width - 0.35 or text.height > height - 0.55:
            raise ValueError(f"Card {title!r}: text {text.text!r} has dimensions {text.width:.3f} x {text.height:.3f}; shorten or wrap it")
    return VGroup(box, heading, content).move_to([x, y, 0])


class ConversationArchiveIntroEN(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        self.story = json.loads((HERE / "storyboard.json").read_text(encoding="utf-8"))
        for index, beat in enumerate(self.story["beats"]):
            begin = self.renderer.time
            heading = label(beat["title"], 40).to_edge(UP, buff=0.73)
            caption = label(beat["caption"], 25, MUTED).move_to([0, -2.82, 0])
            footer = label("CONVERSATION ARCHIVE  /  INVENTED EXAMPLES", 15, MUTED)
            footer.to_edge(DOWN, buff=0.22)
            step = label(f"{index + 1:02d} / 07", 16, MUTED).to_corner(UP + RIGHT, buff=0.2)
            self.play(FadeIn(VGroup(heading, caption, footer, step)), run_time=0.6)
            getattr(self, "beat_" + beat["id"])()
            self.check_frame()
            ending = 0 if index == len(self.story["beats"]) - 1 else 0.4
            remaining = beat["seconds"] - (self.renderer.time - begin) - ending
            if remaining < 1:
                raise ValueError("Beat has insufficient reading time")
            self.wait(remaining)
            if ending:
                self.play(*(FadeOut(mob) for mob in list(self.mobjects)), run_time=ending)
                self.clear()

    def check_frame(self):
        """Assert safe edges; semantic readability still needs visual review."""
        for item in self.mobjects:
            if (item.get_left()[0] < -config.frame_width / 2 + 0.1
                    or item.get_right()[0] > config.frame_width / 2 - 0.1
                    or item.get_top()[1] > config.frame_height / 2 - 0.1
                    or item.get_bottom()[1] < -config.frame_height / 2 + 0.1):
                raise ValueError("Object exceeds the frame-safe area")

    def beat_opening(self):
        cards = VGroup(card("A conversation", "An idea", -4.2),
                       card("Another chat", "A decision", 0),
                       card("A later note", "A new view", 4.2))
        self.play(LaggedStart(*(FadeIn(c, shift=UP * 0.12) for c in cards), lag_ratio=0.2), run_time=1.2)
        joins = VGroup(*(Line(cards[i].get_right(), cards[i + 1].get_left(),
                             color=ACCENT, stroke_width=3) for i in range(2)))
        self.play(Create(joins), run_time=0.8)
        self.play(FadeIn(label("Connect the record. Keep the evidence.", 32).move_to([0, -1.45, 0])), run_time=0.6)

    def beat_evidence(self):
        source = card("Original text", '"I postponed the\nsummer build after\nthe budget review."', -3.5, width=5.5, height=2.25)
        record = card("E0004", "User statement\nExact source span\nOriginal words kept", 3.5, width=5.5, height=2.25)
        arrow = Arrow(source.get_right(), record.get_left(), buff=0.18, color=ACCENT)
        self.play(FadeIn(source), run_time=0.8)
        self.play(Create(arrow), FadeIn(record), run_time=1.0)
        self.play(FadeIn(label("Preserved input. Inspectable output.", 30).move_to([0, -1.65, 0])), run_time=0.6)

    def project_cards(self):
        return VGroup(card("E0001", "Plan Orchard", -4.2, -0.1),
                      card("E0002", "A prototype", 0, -0.1),
                      card("E0005", "Restart\nOrchard", 4.2, -0.1))

    def beat_connections(self):
        cards = self.project_cards()
        project = label("One project?", 33, ACCENT).move_to([0, 1.9, 0])
        links = VGroup(*(DashedLine(c.get_top(), project.get_bottom(), color=MUTED,
                                   stroke_width=2, dash_length=0.12) for c in cards))
        self.play(FadeIn(cards), run_time=0.8)
        self.play(FadeIn(project), Create(links), run_time=1.2)
        self.play(FadeIn(label("PROPOSED CONNECTION  /  SEPARATE ENTRIES", 23, MUTED).move_to([0, -1.55, 0])), run_time=0.6)

    def beat_questions(self):
        count = label("15", 105, ACCENT).move_to([-4.75, 0.7, 0])
        count_text = label("questions\nprepared together", 26).move_to([-4.75, -0.55, 0])
        panel = RoundedRectangle(width=8.2, height=3.35, corner_radius=0.12,
                                 stroke_color=BORDER).move_to([1.6, 0.2, 0])
        title = label("Same project?", 32, ACCENT).move_to([1.6, 1.35, 0])
        references = label("A  Planning Orchard\nB  The summer-build prototype\nC  Restarting Orchard", 27)
        references.move_to([1.6, 0.32, 0])
        choices = label("All same   /   Only some   /   Unsure", 25).move_to([1.6, -0.82, 0])
        self.play(FadeIn(VGroup(count, count_text, panel, title)), run_time=0.8)
        self.play(FadeIn(references), run_time=0.8)
        self.play(FadeIn(choices), run_time=0.6)
        self.play(FadeIn(label("EXAMPLE CARD  /  ONLY DISPLAYED REFERENCES ARE IN SCOPE", 19, MUTED).move_to([0, -1.8, 0])), run_time=0.6)

    def beat_corrections(self):
        cards = self.project_cards()
        project = label("Orchard", 34, ACCENT).move_to([0, 1.95, 0])
        links = VGroup(*(Line(c.get_top(), project.get_bottom(), color=ACCENT,
                             stroke_width=3) for c in cards))
        self.play(FadeIn(cards), FadeIn(project), run_time=0.8)
        self.play(Create(links), run_time=1.2)
        support = label("CONFIRMED IN THIS EXAMPLE  /  FINITE SCOPE  /  REVOCABLE", 21, MUTED)
        self.play(FadeIn(support.move_to([0, -1.55, 0])), run_time=0.6)

    def beat_architecture(self):
        badge = label("TARGET ARCHITECTURE", 23, ACCENT).move_to([0, 2.15, 0])
        records = card("Records + rules", "Entries\nEvidence", -4.25, width=3.7, height=1.9)
        index = card("SQLite", "Rebuildable\nretrieval index", 0, width=3.7, height=1.9)
        views = card("Readable views", "Navigation\nExplanations", 4.25, width=3.7, height=1.9)
        arrows = VGroup(Arrow(records.get_right(), index.get_left(), buff=0.05, color=ACCENT),
                        Arrow(index.get_right(), views.get_left(), buff=0.05, color=ACCENT))
        self.play(FadeIn(badge), FadeIn(records), run_time=0.8)
        self.play(Create(arrows[0]), FadeIn(index), run_time=0.8)
        self.play(Create(arrows[1]), FadeIn(views), run_time=0.8)
        note = label("Local migration reported; not yet shipped in this baseline.", 23, MUTED)
        self.play(FadeIn(note.move_to([0, -1.65, 0])), run_time=0.6)

    def beat_start(self):
        route = label("README  >  AGENTS.md  >  project.json", 31, ACCENT).move_to([0, 1.7, 0])
        command = label("python3 -m conversation_archive.demo\n  --output data/first-run", 29,
                        font="DejaVu Sans Mono").move_to([0, 0.35, 0])
        box = RoundedRectangle(width=12, height=1.65, corner_radius=0.12,
                               stroke_color=BORDER).move_to(command)
        repository = label("xia-geom / conversation-archive", 30).move_to([0, -1.25, 0])
        self.play(FadeIn(route), run_time=0.8)
        self.play(Create(box), FadeIn(command), run_time=0.8)
        self.play(FadeIn(repository), run_time=0.6)
