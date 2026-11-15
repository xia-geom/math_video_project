from __future__ import annotations

import os
import subprocess
import sys

import pytest

from tools import tts


def _clear_azure_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "SPEECH_KEY",
        "SPEECH_REGION",
        "AZURE_SUBSCRIPTION_KEY",
        "AZURE_SERVICE_REGION",
    ):
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("selector,voice", [
    ("MAI-Voice-2", tts.MAI_VOICE_2),
    ("MAI-Voice-2.1", tts.MAI_VOICE_2_1),
])
def test_mai_voice_alias_resolves_to_published_french_voice(selector, voice) -> None:
    assert tts.resolve_voice(selector) == voice
    assert tts.VOICE_CONFIGS[voice] == "-3%"
    assert tts.VOICE_LOCALES[voice] == "fr-FR"
    assert tts.VOICE_STYLES[voice] is None


@pytest.mark.parametrize("selector,voice,rate,locale", [
    (None, tts.MAI_VOICE_2_1, "-3%", "fr-FR"),
    ("MAI-Voice-2.1", tts.MAI_VOICE_2_1, "-3%", "fr-FR"),
    (tts.MAI_VOICE_2_1, tts.MAI_VOICE_2_1, "-3%", "fr-FR"),
    ("MAI-Voice-2", tts.MAI_VOICE_2, "-3%", "fr-FR"),
    ("fr-CA-JeanNeural", "fr-CA-JeanNeural", "-14%", "fr-CA"),
])
def test_environment_selector_drives_default_ssml_profile(selector, voice, rate, locale) -> None:
    env = os.environ.copy()
    env.pop("MANIM_VOICE", None)
    if selector is not None:
        env["MANIM_VOICE"] = selector
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from tools import tts; "
                f"assert tts.VOICE_ID == {voice!r}; "
                f"assert tts.VOICE_RATE == {rate!r}; "
                f"assert tts.VOICE_LOCALE == {locale!r}; "
                f"assert tts.ssml('Test') == {tts.ssml('Test', rate=rate, locale=locale)!r}"
            ),
        ],
        check=True,
        env=env,
    )


def test_ssml_can_use_mai_locale_and_moderate_rate() -> None:
    rendered = tts.ssml("Une équation.", rate="-3%", locale="fr-FR")

    assert rendered.startswith("<lang xml:lang='fr-FR'><prosody rate='-3%'>")
    assert rendered.endswith("</prosody></lang>")


@pytest.mark.parametrize("voice", [tts.MAI_VOICE_2, tts.MAI_VOICE_2_1])
def test_mai_environment_bridges_current_and_legacy_names(
    monkeypatch: pytest.MonkeyPatch, voice,
) -> None:
    _clear_azure_environment(monkeypatch)
    monkeypatch.setenv("SPEECH_KEY", "placeholder")
    monkeypatch.setenv("SPEECH_REGION", "CanadaCentral")

    assert tts.configure_azure_speech_environment(voice) == "canadacentral"
    assert "AZURE_SUBSCRIPTION_KEY" in os.environ
    assert os.environ["AZURE_SERVICE_REGION"] == "canadacentral"
    assert tts.azure_service_kwargs(voice) == {
        "voice": voice,
        "style": None,
        "output_format": tts.AZURE_OUTPUT_FORMAT,
    }


@pytest.mark.parametrize("voice", [tts.MAI_VOICE_2, tts.MAI_VOICE_2_1])
def test_cached_render_configuration_does_not_require_credentials(
    monkeypatch: pytest.MonkeyPatch, voice,
) -> None:
    _clear_azure_environment(monkeypatch)

    assert tts.azure_service_kwargs(voice)["voice"] == voice


@pytest.mark.parametrize("voice", [tts.MAI_VOICE_2, tts.MAI_VOICE_2_1])
def test_mai_environment_rejects_a_different_region(
    monkeypatch: pytest.MonkeyPatch, voice,
) -> None:
    _clear_azure_environment(monkeypatch)
    monkeypatch.setenv("SPEECH_KEY", "placeholder")
    monkeypatch.setenv("SPEECH_REGION", "eastus")

    with pytest.raises(RuntimeError, match="canadacentral"):
        tts.configure_azure_speech_environment(voice)


@pytest.mark.parametrize("voice,expected", [
    (tts.MAI_VOICE_2, True),
    (tts.MAI_VOICE_2_1, True),
    ("fr-CA-JeanNeural", False),
    ("fr-FR-Soleil:MAI-Voice-2.10", False),
    ("fr-FR-Soleil:MAI-Voice-2.1-Flash", False),
])
def test_mai_family_detection_is_exact(voice, expected) -> None:
    assert tts.is_mai_voice(voice) is expected
