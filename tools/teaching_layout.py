"""Readable teaching panels: grow boxes, never silently shrink their contents."""
from __future__ import annotations

from manim import BLACK, BLUE_D, DOWN, FadeIn, FadeOut, MathTex, RoundedRectangle, Text, VGroup
from manim_voiceover import VoiceoverScene

from tools import tts
from tools.course_timing import seconds
from tools.teaching_voiceover import TeachingAzureService

BODY_WIDTH = 12.0
BODY_HEIGHT = 4.9


def assert_inside(content, box, padding=0.18):
    if (content.get_left()[0] < box.get_left()[0] + padding - 0.001
            or content.get_right()[0] > box.get_right()[0] - padding + 0.001
            or content.get_bottom()[1] < box.get_bottom()[1] + padding - 0.001
            or content.get_top()[1] > box.get_top()[1] - padding + 0.001):
        raise ValueError('Formula outside its panel; split or enlarge the panel.')


def panel(content, *, width=5.45, height=1.6, color=BLUE_D, padding=0.28):
    """Minimum dimensions, not a fixed-size box; preserve the authored font size."""
    width = max(width, content.width + 2 * padding)
    height = max(height, content.height + 2 * padding)
    if width > BODY_WIDTH or height > BODY_HEIGHT:
        raise ValueError('Panel cannot fit legibly: split the explanation into another page.')
    box = RoundedRectangle(width=width, height=height, corner_radius=0.12,
                           stroke_color=color, stroke_width=2,
                           fill_color=color, fill_opacity=0.035)
    content.move_to(box)
    assert_inside(content, box, padding)
    group = VGroup(box, content)
    group.teaching_panel = True
    return group


class TeachingScene(VoiceoverScene):
    """One heading and sequential reveals; genuine speech or explicit silent preview."""

    def setup_narration(self):
        import os
        from pathlib import Path

        from dotenv import load_dotenv

        load_dotenv(Path(__file__).resolve().parents[1] / '.env', override=False)
        self.silent = os.getenv('MANIM_DISABLE_VOICEOVER', '').lower() in {'1', 'true', 'yes'}
        self.page = None
        self.teaching_timeline = []
        self.teaching_page_title = None
        if not self.silent:
            tts.configure_azure_speech_environment(require_credentials=True)
            self.set_speech_service(TeachingAzureService())

    @staticmethod
    def words(text, size=30, color=BLACK):
        return Text(text, font_size=size, color=color)

    @staticmethod
    def formula(text, size=42, color=BLACK):
        return MathTex(text, font_size=size, color=color)

    def new_page(self, title, *blocks, gap=0.48):
        self.teaching_page_title = title
        if self.page is not None:
            self.play(FadeOut(self.page), run_time=0.35)
            self.remove(*list(self.mobjects))
        heading = self.words(title, 40, BLUE_D).move_to([0, 3.12, 0])
        body = VGroup(*blocks).arrange(DOWN, buff=gap).move_to([0, 0.0, 0])
        if heading.width > BODY_WIDTH or body.width > BODY_WIDTH or body.height > BODY_HEIGHT:
            raise ValueError(f'Overcrowded page: {title!r}; split it instead of shrinking text.')
        self.page = VGroup(heading, body)
        self.play(FadeIn(heading), run_time=0.45)
        return blocks

    def explain(self, text, *objects, hold=1.0, pause_after=0.0):
        """Honor minimum reading time and an explicit post-question thinking pause.

        Silent mode remains a fast structural preview, not a narration estimate.
        Narrated mode waits for real speech and minimum visibility, then adds only
        the explicitly authored reflection pause. Never stretch the whole film.
        """
        import json
        import os
        from pathlib import Path

        hold = seconds(hold, allow_zero=True)
        pause_after = seconds(pause_after, allow_zero=True)
        start = float(self.renderer.time)
        speech_duration = None
        if self.silent:
            self.play(*(FadeIn(obj) for obj in objects), run_time=0.6)
            visible_from = float(self.renderer.time)
            self.wait(max(hold, pause_after))
            speech_context_end = float(self.renderer.time)
        else:
            spoken = tts.ssml(text)
            with self.voiceover(text=spoken, subcaption=tts.strip_ssml(spoken)) as tracker:
                speech_duration = seconds(tracker.duration)
                self.play(*(FadeIn(obj) for obj in objects), run_time=0.6)
                visible_from = float(self.renderer.time)
                # The voiceover context also waits for any remaining real speech.
                self.wait(hold)
            speech_context_end = float(self.renderer.time)
            if pause_after:
                self.wait(pause_after)
        record = {
            'mode': 'silent_preview' if self.silent else 'azure_review',
            'page': self.teaching_page_title, 'text': text, 'start': start,
            'visible_from': visible_from, 'speech_context_end': speech_context_end,
            'end': float(self.renderer.time), 'minimum_visible_seconds': hold,
            'reflection_pause_seconds': pause_after,
            'speech_duration_seconds': speech_duration,
        }
        self.teaching_timeline.append(record)
        # The review runner supplies an isolated output path. No source Git writes.
        timing_path = os.getenv('TEACHING_TIMING_PATH')
        if timing_path:
            Path(timing_path).write_text(
                json.dumps(self.teaching_timeline, ensure_ascii=False, indent=2) + '\n',
                encoding='utf-8',
            )
