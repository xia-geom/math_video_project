"""
tools/tts.py
============
Single source of truth for all TTS / SSML configuration used across
every scene and experiment in this project.

Usage
-----
    from tools.tts import VOICE_ID, VOICE_RATE, ssml, char, chars, strip_ssml
    from tools.tts import PLUS, A, B, C, X, Y, P, T

    # Wrap narration in the selected voice's locale and prosody envelope:
    text = ssml("Ses côtés sont " + A + " et " + B + ".")

    # Strip tags to get a clean subtitle string:
    subtitle = strip_ssml(text)

Overriding the voice at render time
------------------------------------
    MANIM_VOICE=fr-CA-JeanNeural manim -pql scenes/.../my_scene.py MyScene
    MANIM_VOICE=MAI-Voice-2 manim -pql scenes/.../my_scene.py MyScene

The teaching default is MAI-Voice-2, with the existing -3% teaching rate.

``MAI-Voice-2`` is a convenience alias for Microsoft's French
``fr-FR-Soleil:MAI-Voice-2`` voice. MAI synthesis uses the same Azure
Speech SDK/SSML pipeline as the standard neural voices, but requires the
Speech resource to be in ``canadacentral`` for this project.

Future integration
------------------
The numeric-sync checks in tools/ssml_sync_check.py are planned to be
migrated here so they can import VOICE_CONFIGS directly instead of
maintaining a parallel list.
"""

import os
import re

# ── Voice configuration ────────────────────────────────────────────────
# MAI teaching standard plus explicit opt-in legacy fr-CA profiles.
# Rate is a negative percentage that slows the voice to a comfortable
# teaching pace (Azure TTS reads noticeably fast by default).

MAI_VOICE_2 = "fr-FR-Soleil:MAI-Voice-2"
MAI_VOICE_2_REGION = "canadacentral"
AZURE_OUTPUT_FORMAT = "Audio48Khz192KBitRateMonoMp3"

VOICE_CONFIGS: dict[str, str] = {
    "fr-CA-SylvieNeural": "-14%",  # legacy female profile
    "fr-CA-JeanNeural": "-14%",  # male, natural delivery
    "fr-CA-AntoineNeural": "-14%",  # male, expressive
    "fr-CA-ThierryNeural": "-14%",  # male, clear diction
    # Neutral style lets MAI supply natural phrasing and varied intonation.
    # A modest slowdown keeps the delivery calm but still moderately paced.
    MAI_VOICE_2: "-3%",
}

VOICE_LOCALES: dict[str, str] = {
    MAI_VOICE_2: "fr-FR",
}

# The published French MAI voice has no calm or narration-specific style.
# Neutral is intentional: the model supplies its native expressive intonation,
# while the authored punctuation and SSML breaks control pedagogical pauses.
VOICE_STYLES: dict[str, str | None] = {
    MAI_VOICE_2: None,
}

VOICE_ALIASES: dict[str, str] = {
    "mai-voice-2": MAI_VOICE_2,
}

DEFAULT_VOICE = MAI_VOICE_2


def resolve_voice(selection: str | None = None) -> str:
    """Resolve a friendly selector or an Azure voice ShortName."""

    selected = (selection or os.getenv("MANIM_VOICE") or DEFAULT_VOICE).strip()
    return VOICE_ALIASES.get(selected.casefold(), selected)


def is_mai_voice(voice_id: str) -> bool:
    """Return whether *voice_id* selects the MAI-Voice-2 model."""

    return voice_id.endswith(":MAI-Voice-2")


# Resolved at import time from the environment, falling back to the default.
VOICE_ID: str = resolve_voice()
VOICE_RATE: str = VOICE_CONFIGS.get(VOICE_ID, "-14%")
VOICE_LOCALE: str = VOICE_LOCALES.get(VOICE_ID, "fr-CA")


def configure_azure_speech_environment(
    voice_id: str = VOICE_ID,
    *,
    require_credentials: bool = True,
) -> str | None:
    """Validate Azure Speech settings and bridge supported variable names.

    Microsoft documentation uses ``SPEECH_KEY`` and ``SPEECH_REGION`` while
    manim-voiceover 0.3.x reads the older ``AZURE_SUBSCRIPTION_KEY`` and
    ``AZURE_SERVICE_REGION`` names. Values remain environment-only; this
    helper neither embeds nor logs credentials.

    Returns:
        The normalized Azure Speech region, or ``None`` when optional
        settings are absent during a cache-only render.

    Raises:
        RuntimeError: If required credentials are missing, aliases conflict,
            or MAI-Voice-2 is selected outside Canada Central.
    """

    speech_key = os.getenv("SPEECH_KEY")
    legacy_key = os.getenv("AZURE_SUBSCRIPTION_KEY")
    speech_region = os.getenv("SPEECH_REGION")
    legacy_region = os.getenv("AZURE_SERVICE_REGION")

    if speech_key and legacy_key and speech_key != legacy_key:
        raise RuntimeError("Azure Speech key environment aliases do not match")
    if speech_region and legacy_region and speech_region.casefold() != legacy_region.casefold():
        raise RuntimeError("Azure Speech region environment aliases do not match")

    key = speech_key or legacy_key
    region = (speech_region or legacy_region or "").strip().casefold()
    if require_credentials and not key:
        raise RuntimeError("Set SPEECH_KEY (or AZURE_SUBSCRIPTION_KEY) for Azure Speech")
    if require_credentials and not region:
        raise RuntimeError("Set SPEECH_REGION (or AZURE_SERVICE_REGION) for Azure Speech")
    if region and is_mai_voice(voice_id) and region != MAI_VOICE_2_REGION:
        raise RuntimeError(f"MAI-Voice-2 requires SPEECH_REGION={MAI_VOICE_2_REGION}")

    # The third-party Manim adapter currently reads the legacy names.
    if key:
        os.environ["SPEECH_KEY"] = key
        os.environ["AZURE_SUBSCRIPTION_KEY"] = key
    if region:
        os.environ["SPEECH_REGION"] = region
        os.environ["AZURE_SERVICE_REGION"] = region
    return region or None


def azure_service_kwargs(voice_id: str = VOICE_ID) -> dict[str, str | None]:
    """Return credential-free options for Manim's Azure Speech adapter."""

    # Bridge settings when present, but keep cached/offline renders working.
    # AzureService itself requires credentials only when a clip is not cached.
    configure_azure_speech_environment(voice_id, require_credentials=False)
    return {
        "voice": voice_id,
        "style": VOICE_STYLES.get(voice_id),
        # Preserve the narration pipeline's existing 48 kHz MP3 contract.
        "output_format": AZURE_OUTPUT_FORMAT,
    }


# ── SSML helpers ──────────────────────────────────────────────────────


def ssml(
    text: str,
    rate: str = VOICE_RATE,
    locale: str = VOICE_LOCALE,
) -> str:
    """Wrap *text* in the selected voice's language + prosody envelope.

    This is the one place in the project where the locale tag and the
    prosody rate live.  All scene files should call this instead of
    building the XML by hand.

    Args:
        text: The narration body, which may already contain inner SSML
              tags (bookmarks, breaks, say-as, phonemes, etc.).
        rate: Prosody rate override — defaults to the project-wide
              VOICE_RATE derived from VOICE_CONFIGS[VOICE_ID].
        locale: SSML locale override — defaults to the selected voice's
                locale (``fr-CA`` for standard voices, ``fr-FR`` for MAI).
    """
    return f"<lang xml:lang='{locale}'><prosody rate='{rate}'>{text}</prosody></lang>"


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
