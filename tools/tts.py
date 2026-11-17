"""
tools/tts.py
============
Single source of truth for all TTS / SSML configuration used across
every scene and experiment in this project.

This module keeps configuration independent of the rendering and audit runtime.

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
    MANIM_VOICE=MAI-Voice-2.1 manim -pql scenes/.../my_scene.py MyScene

The teaching default is MAI-Voice-2.1, with the existing -3% teaching rate.

``MAI-Voice-2.1`` selects Microsoft's French ``fr-FR-Soleil:MAI-Voice-2.1``
voice. The explicit ``MAI-Voice-2`` alias retains the earlier model.
Both use the Azure Speech SDK/SSML pipeline and this project's existing
``canadacentral`` deployment policy, not a service-wide region restriction.

Future integration
------------------
The numeric-sync checks in tools/ssml_sync_check.py are planned to be
migrated here so they can import VOICE_CONFIGS directly instead of
maintaining a parallel list.
"""

import os
import re
import xml.etree.ElementTree as ElementTree
from html import unescape
from xml.sax.saxutils import escape, quoteattr

# ── Voice configuration ────────────────────────────────────────────────
# MAI teaching standard plus explicit opt-in legacy fr-CA profiles.
# Rate is a negative percentage that slows the voice to a comfortable
# teaching pace (Azure TTS reads noticeably fast by default).

MAI_VOICE_2 = "fr-FR-Soleil:MAI-Voice-2"
MAI_VOICE_2_1 = "fr-FR-Soleil:MAI-Voice-2.1"
# Keep the established deployment policy for both supported MAI versions.
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
    MAI_VOICE_2_1: "-3%",
}

VOICE_LOCALES: dict[str, str] = {
    MAI_VOICE_2: "fr-FR",
    MAI_VOICE_2_1: "fr-FR",
}

# Neutral is the chosen teaching profile for both MAI versions:
# the model supplies its native expressive intonation,
# while the authored punctuation and SSML breaks control pedagogical pauses.
VOICE_STYLES: dict[str, str | None] = {
    MAI_VOICE_2: None,
    MAI_VOICE_2_1: None,
}

VOICE_ALIASES: dict[str, str] = {
    "mai-voice-2": MAI_VOICE_2,
    "mai-voice-2.1": MAI_VOICE_2_1,
}

DEFAULT_VOICE = MAI_VOICE_2_1


def resolve_voice(selection: str | None = None) -> str:
    """Resolve a friendly selector or an Azure voice ShortName."""

    selected = (selection or os.getenv("MANIM_VOICE") or DEFAULT_VOICE).strip()
    return VOICE_ALIASES.get(selected.casefold(), selected)


def is_mai_voice(voice_id: str) -> bool:
    """Return whether the resolved voice selects a supported MAI model."""

    return voice_id.endswith((":MAI-Voice-2", ":MAI-Voice-2.1"))


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
            or a MAI model violates this project's Canada Central policy.
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
        raise RuntimeError(
            f"This project's MAI deployment requires SPEECH_REGION={MAI_VOICE_2_REGION}"
        )

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

PRONUNCIATION_POLICY_VERSION = "fr_math_letters_v1"
FRENCH_LETTER_NAMES = {
    "a": "a", "b": "bé", "c": "cé", "d": "dé", "e": "e", "f": "effe",
    "g": "gé", "h": "ache", "i": "i", "j": "ji", "k": "ka", "l": "elle",
    "m": "emme", "n": "enne", "o": "o", "p": "pé", "q": "ku", "r": "erre",
    "s": "esse", "t": "té", "u": "u", "v": "vé", "w": "double vé",
    "x": "iks", "y": "i grec", "z": "zède",
}

# Do not treat French a/y, elisions (l', d’, c’…) or hyphenated words as
# mathematical symbols. Ambiguous a/y must be marked explicitly by the author.
_ISOLATED_LETTER = re.compile(r"(?<![\w'’\-])([A-Za-z])(?![\w'’\-])")
_XML_TAG = re.compile(r'''<!--.*?-->|<\?.*?\?>|<(?:[^>'"]|'[^']*'|"[^"]*")*>''', re.S)
_ATOMIC_PRONUNCIATION = {"sub", "say-as", "phoneme"}
_WORDS_AND_PUNCTUATION = re.compile(r"\w+(?:['’\-]\w+)*|[^\w\s]", re.UNICODE)
_VOWEL_SOUNDS = {
    "a": "a", "à": "a", "â": "a", "e": "e", "euh": "e", "i": "i",
    "o": "o", "ô": "o", "au": "o", "aux": "o", "u": "u",
}


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].rsplit(":", 1)[-1]


def _speech_fragment(text: str) -> ElementTree.Element:
    """Parse SSML without changing its spelling or bookmark coordinates."""
    root = ElementTree.fromstring(
        '<root xmlns:mstts="https://www.w3.org/2001/mstts">' + text + '</root>'
    )
    for element in root.iter():
        if _local_name(element.tag) in _ATOMIC_PRONUNCIATION and len(element):
            raise ValueError(
                f"SSML <{_local_name(element.tag)}> must contain text only; "
                "put bookmarks and breaks outside pronunciation elements."
            )
    return root


def _spelled_letters(text: str) -> str | None:
    """Expand a legacy character directive only when every symbol is known."""
    letters = ''.join(text.split())
    if letters and letters.isascii() and all(c.lower() in FRENCH_LETTER_NAMES for c in letters):
        return ' '.join(FRENCH_LETTER_NAMES[c.lower()] for c in letters)
    return None


def _prepare_plain_text(text: str) -> str:
    plain = unescape(text)
    prepared = _ISOLATED_LETTER.sub(
        lambda match: (
            match[1] if match[1] in {"a", "y"}
            else FRENCH_LETTER_NAMES[match[1].lower()]
        ),
        plain,
    )
    return text if prepared == plain else escape(prepared)


def prepare_math_speech(text: str) -> str:
    """Resolve French math letter names before MAI synthesis.

    Explicit aliases are authoritative. Existing phonemes and non-character
    say-as directives are opaque. Only text nodes are normalized; attributes,
    bookmark names and unchanged markup retain their original bytes. Captions
    must continue to use the authored input, not this synthesized form.
    """
    _speech_fragment(text)
    tags = list(_XML_TAG.finditer(text))
    pieces, cursor, index = [], 0, 0
    while index < len(tags):
        token = tags[index]
        pieces.append(_prepare_plain_text(text[cursor:token.start()]))
        opening = re.match(r"<([\w:-]+)\b", token[0])
        name = _local_name(opening[1]) if opening else None
        if name in _ATOMIC_PRONUNCIATION:
            # Work on the full text-only element so an alias is never expanded
            # twice. Comments can occur before the matching closing tag.
            if not token[0].rstrip().endswith('/>'):
                index += 1
                while tags[index][0].startswith(('<!--', '<?')):
                    index += 1
            end = tags[index].end()
            original = text[token.start():end]
            element = _speech_fragment(original)[0]
            replacement = None
            if name == "sub":
                replacement = element.get("alias")
            elif name == "say-as" and element.get("interpret-as") == "characters":
                replacement = _spelled_letters(element.text or "")
            pieces.append(original if replacement is None else escape(replacement))
            cursor = end
        else:
            pieces.append(token[0])
            cursor = token.end()
        index += 1
    pieces.append(_prepare_plain_text(text[cursor:]))
    return ''.join(pieces)


def validate_pronunciation(text: str) -> None:
    """Reject adjacent identical vowel words involving a mathematical letter.

    This catches authored collisions such as « A a » or « A à », including
    across transparent wrappers/bookmarks. It does not remove words, infer all
    French phonetics, or claim to detect repetitions in generated audio.
    Punctuation, sentence boundaries and explicit breaks separate the sounds.
    """
    root = _speech_fragment(text)
    previous: tuple[str, bool] | None = None

    def words(value: str, *, marked: bool = False, infer: bool = True) -> None:
        nonlocal previous
        for match in _WORDS_AND_PUNCTUATION.finditer(value):
            word = match[0]
            is_letter = marked or (
                infer and len(word) == 1 and word in "AEIOUeiou"
            )
            sound = _VOWEL_SOUNDS.get(word.casefold())
            if (previous and sound and sound == _VOWEL_SOUNDS.get(previous[0].casefold())
                    and (is_letter or previous[1])):
                raise ValueError(
                    f"Repeated vowel around a mathematical letter: {previous[0]!r} {word!r}. "
                    "Rephrase the sentence or author punctuation/a break between the sounds."
                )
            previous = (word, is_letter)

    def visit(element: ElementTree.Element) -> None:
        nonlocal previous
        name = _local_name(element.tag)
        has_pause = name == "break" and element.get("strength") != "none"
        if name == "break" and "time" in element.attrib:
            duration = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:ms|s)", element.attrib["time"])
            has_pause = bool(duration and float(duration[1]) > 0)
        if has_pause or name in {"p", "s"}:
            previous = None
        if name in _ATOMIC_PRONUNCIATION:
            surface = element.text or ""
            if name == "sub":
                alias = element.get("alias", surface)
                symbol = surface.strip()
                known = (len(symbol) == 1 and symbol.lower() in FRENCH_LETTER_NAMES
                         and alias == FRENCH_LETTER_NAMES[symbol.lower()])
                words(alias, marked=known, infer=False)
            elif name == "say-as" and element.get("interpret-as") == "characters":
                spelled = _spelled_letters(surface)
                words(spelled or surface, marked=spelled is not None, infer=False)
            else:
                # Author-supplied phonetics and other directives are authoritative.
                previous = None
            return
        words(element.text or "")
        for child in element:
            visit(child)
            words(child.tail or "")
        if name in {"p", "s"}:
            previous = None

    visit(root)


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
    """Give one Latin math letter an explicit French spoken name.

    Use for single-letter math variables (a, b, x, y, …) so that Azure
    does not try to pronounce them as French words.

    The written letter and its case remain intact for captions. The teaching
    adapter expands the alias into ordinary French before MAI synthesis.
    """
    if (not isinstance(c, str) or len(c) != 1 or not c.isascii()
            or c.lower() not in FRENCH_LETTER_NAMES):
        raise ValueError("char() expects one ASCII Latin letter (a-z or A-Z).")
    return f"<sub alias={quoteattr(FRENCH_LETTER_NAMES[c.lower()])}>{escape(c)}</sub>"


def chars(*letters: str) -> str:
    """Return space-joined char() tokens for two or more letters.

    Avoids the pitfall of putting multi-letter strings inside a single
    say-as tag, which Azure sometimes reads as a word.

    Example:
        chars('a', 'b')  →  "<sub …>a</sub> <sub …>b</sub>"
    """
    return " ".join(char(c) for c in letters)


def strip_ssml(text: str) -> str:
    """Strip XML/SSML tags, leaving the authored notation for captions.

    Use this to derive a clean subtitle / subcaption string from an SSML
    narration string so you don't have to maintain both separately.

    Example:
        strip_ssml("<lang xml:lang='fr-CA'>Bonjour <break time='100ms'/></lang>")
        →  "Bonjour"
    """
    return unescape(_XML_TAG.sub("", text)).replace("  ", " ").strip()


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
