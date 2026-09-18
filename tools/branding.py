"""One standard UQAM opening: official asset, white canvas, 1.5-second bumper."""
from pathlib import Path

from manim import ORIGIN, WHITE, FadeIn, FadeOut, ImageMobject

UQAM_LOGO_PATH = str(Path(__file__).resolve().parents[1] / 'assets/branding/uqam_logo.png')
INTRO_WIDTH = 4.0
INTRO_TIMING = {'fade_in': 0.4, 'hold': 0.5, 'fade_out': 0.4, 'pad': 0.2}


def play_uqam_intro(scene, *, width=INTRO_WIDTH, fade_in=0.4, hold=0.5, fade_out=0.4, pad=0.2):
    """Use once before lesson content; the standalone identity scene is separate."""
    if getattr(scene, '_uqam_intro_played', False):
        raise RuntimeError('Duplicate UQAM opening: remove the scene-local bumper.')
    if not Path(UQAM_LOGO_PATH).is_file():
        raise FileNotFoundError('The official UQAM logo asset is missing.')
    if scene.mobjects:
        raise RuntimeError('UQAM opening must precede the lesson content.')
    scene._uqam_intro_played = True
    scene.camera.background_color = WHITE
    logo = ImageMobject(UQAM_LOGO_PATH).scale_to_fit_width(width).move_to(ORIGIN)
    scene.play(FadeIn(logo), run_time=fade_in)
    scene.wait(hold)
    scene.play(FadeOut(logo), run_time=fade_out)
    scene.wait(pad)
    scene.uqam_intro = {'asset': 'assets/branding/uqam_logo.png', 'width': width,
                        'duration_seconds': fade_in + hold + fade_out + pad}
