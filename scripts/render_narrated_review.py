"""Run the ordinary Manim CLI with isolated narration evidence capture enabled."""
from __future__ import annotations

import os

from manim import Scene
from manim.__main__ import main
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.azure import AzureService

from tools.narration_provenance import NarrationCapture

if __name__ == '__main__':
    capture = NarrationCapture(os.environ['TEACHING_NARRATION_EVIDENCE_PATH'])
    with capture.observe(Scene, VoiceoverScene, AzureService):
        main()
