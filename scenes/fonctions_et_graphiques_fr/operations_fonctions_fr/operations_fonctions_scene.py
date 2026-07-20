import os
from contextlib import contextmanager
from dataclasses import dataclass
from math import sqrt

from manim import *

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

try:
    from manim_voiceover import VoiceoverScene
    from manim_voiceover.services.azure import AzureService
except ImportError: