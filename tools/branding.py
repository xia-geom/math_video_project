"""
tools/branding.py
=================
Shared UQAM-logo intro used at the start of every production scene.

Usage
-----
    from tools.branding import play_uqam_intro

    class MyScene(VoiceoverScene):
        def construct(self):
            self.camera.background_color = WHITE
            play_uqam_intro(self)
            # ... rest of the scene ...

The full animated bumper (with the accent-tap flourish) lives in
scenes/uqam_bumper/uqam_bumper_scene.py and can still be rendered
as a standalone clip.
"""

from pathlib import Path

from manim import FadeIn, FadeOut, ImageMobject, ORIGIN

UQAM_LOGO_PATH = str(
    Path(__file__).resolve().parents[1] / "assets" / "branding" / "uqam_logo.png"
)


def play_uqam_intro(
    scene,
    *,
    width: float = 4.0,
    fade_in: float = 0.4,
    hold: float = 0.5,
    fade_out: float = 0.4,
    pad: float = 0.2,
) -> None:
    """Play a short UQAM logo fade-in / hold / fade-out at scene start.

    Total on-screen time ≈ fade_in + hold + fade_out + pad (≈ 1.5 s default).
    """
    logo = ImageMobject(UQAM_LOGO_PATH)
    logo.scale_to_fit_width(width)
    logo.move_to(ORIGIN)

    scene.play(FadeIn(logo), run_time=fade_in)
    scene.wait(hold)
    scene.play(FadeOut(logo), run_time=fade_out)
    scene.wait(pad)
