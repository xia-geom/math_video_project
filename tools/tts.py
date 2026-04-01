"""
tools/tts.py
============
Single source of truth for all TTS / SSML configuration used across
every scene and experiment in this project.

Usage
-----
    from tools.tts import VOICE_ID, VOICE_RATE, ssml, char, chars, strip_ssml
    from tools.tts import PLUS, A, B, C, X, Y, P, T

    # Wrap narration in the standard fr-CA prosody envelope:
    text = ssml("Ses côtés sont " + A + " et " + B + ".")

    # Strip tags to get a clean subtitle string:
    subtitle = strip_ssml(text)

Overriding the voice at render time
------------------------------------
    MANIM_VOICE=fr-CA-JeanNeural manim -pql scenes/.../my_scene.py MyScene

The default voice is fr-CA-SylvieNeural.

Future integration
------------------
The numeric-sync checks in tools/ssml_sync_check.py are planned to be
migrated here so they can import VOICE_CONFIGS directly instead of
maintaining a parallel list.
"""

import os
import re

# ── Voice configuration ────────────────────────────────────────────────
# All four supported fr-CA voices with their tuned prosody rates.
# Rate is a negative percentage that slows the voice to a comfortable
# teaching pace (Azure TTS reads noticeably fast by default).

VOICE_CONFIGS: dict[str, str] = {
    "fr-CA-SylvieNeural":  "-14%",  # female — series default
    "fr-CA-JeanNeural":    "-14%",  # male, natural delivery
    "fr-CA-AntoineNeural": "-14%",  # male, expressive
    "fr-CA-ThierryNeural": "-14%",  # male, clear diction
}

DEFAULT_VOICE = "fr-CA-SylvieNeural"

# Resolved at import time from the environment, falling back to the default.
VOICE_ID:   str = os.getenv("MANIM_VOICE", DEFAULT_VOICE)
VOICE_RATE: str = VOICE_CONFIGS.get(VOICE_ID, "-14%")


# ── SSML helpers ──────────────────────────────────────────────────────

def ssml(text: str, rate: str = VOICE_RATE) -> str:
    """Wrap *text* in the standard fr-CA language + prosody envelope.

    This is the one place in the project where the locale tag and the
    prosody rate live.  All scene files should call this instead of
    building the XML by hand.

    Args:
        text: The narration body, which may already contain inner SSML
              tags (bookmarks, breaks, say-as, phonemes, etc.).
        rate: Prosody rate override — defaults to the project-wide
              VOICE_RATE derived from VOICE_CONFIGS[VOICE_ID].
    """
    return (
        f"<lang xml:lang='fr-CA'>"
        f"<prosody rate='{rate}'>"
        f"{text}"
        f"</prosody>"
        f"</lang>"
    )


def char(c: str) -> str:
    """Return an SSML token that reads *c* as a spelled-out character.

    Use for single-letter math variables (a, b, x, y, …) so that Azure
    does not try to pronounce them as French words.

    Example:
        char('x')  →  "<say-as interpret-as='characters'>x</say-as>"
    """
    return f"<say-as interpret-as='characters'>{c}</say-as>"


def chars(*letters: str) -> str:
    """Return space-joined char() tokens for two or more letters.

    Avoids the pitfall of putting multi-letter strings inside a single
    say-as tag, which Azure sometimes reads as a word.

    Example:
        chars('a', 'b')  →  "<say-as …>a</say-as> <say-as …>b</say-as>"
    """
    return " ".join(char(c) for c in letters)


_SSML_TAG_RE = re.compile(r"<[^>]+>")

def strip_ssml(text: str) -> str:
    """Strip all XML/SSML tags from *text*, leaving only the spoken words.

    Use this to derive a clean subtitle / subcaption string from an SSML
    narration string so you don't have to maintain both separately.

    Example:
        strip_ssml("<lang xml:lang='fr-CA'>Bonjour <break time='100ms'/></lang>")
        →  "Bonjour"
    """
    return _SSML_TAG_RE.sub("", text).replace("  ", " ").strip()


# ── Pronunciation constants ────────────────────────────────────────────
# Pre-built SSML tokens for symbols whose default Azure pronunciation is
# wrong or inconsistent in French-Canadian math narration.
#
# Import the ones you need; they are plain strings and compose freely
# with f-strings.

# "plus" — Azure fr-CA often drops the final /s/, yielding "plu".
# Force the correct /plys/ pronunciation with a phoneme tag.
PLUS = "<phoneme alphabet='ipa' ph='plys'>plus</phoneme>"

# French liaison fix — "et" between vowel sounds can be swallowed by Azure TTS.
# Use ET in narration strings instead of bare "et" to force clear separation.
ET = "<break time='150ms'/> et <break time='100ms'/>"

# Common single-letter math variables
A = char("a")
B = char("b")
C = char("c")
P = char("p")
Q = char("q")
T = char("T")
X = char("x")
Y = char("y")
