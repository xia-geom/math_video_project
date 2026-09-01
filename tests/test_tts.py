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


def test_mai_voice_alias_resolves_to_published_french_voice() -> None:
    assert tts.resolve_voice("MAI-Voice-2") == tts.MAI_VOICE_2
    assert tts.VOICE_CONFIGS[tts.MAI_VOICE_2] == "-3%"
    assert tts.VOICE_LOCALES[tts.MAI_VOICE_2] == "fr-FR"
    assert tts.VOICE_STYLES[tts.MAI_VOICE_2] is None


def test_mai_environment_selector_drives_default_ssml_profile() -> None:
    env = os.environ.copy()
    env["MANIM_VOICE"] = "MAI-Voice-2"
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from tools import tts; "
                "assert tts.VOICE_ID == tts.MAI_VOICE_2; "
                "assert tts.VOICE_RATE == '-3%'; "
                "assert tts.VOICE_LOCALE == 'fr-FR'; "
                "assert tts.ssml('Test').startswith("
                "\"<lang xml:lang='fr-FR'><prosody rate='-3%'>\")"
            ),
        ],
        check=True,
        env=env,
    )


def test_ssml_can_use_mai_locale_and_moderate_rate() -> None:
    rendered = tts.ssml("Une équation.", rate="-3%", locale="fr-FR")

    assert rendered.startswith("<lang xml:lang='fr-FR'><prosody rate='-3%'>")
    assert rendered.endswith("</prosody></lang>")


def test_mai_environment_bridges_current_and_legacy_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_azure_environment(monkeypatch)
    monkeypatch.setenv("SPEECH_KEY", "placeholder")
    monkeypatch.setenv("SPEECH_REGION", "CanadaCentral")

    assert tts.configure_azure_speech_environment(tts.MAI_VOICE_2) == "canadacentral"
    assert "AZURE_SUBSCRIPTION_KEY" in os.environ
    assert os.environ["AZURE_SERVICE_REGION"] == "canadacentral"
    assert tts.azure_service_kwargs(tts.MAI_VOICE_2) == {
        "voice": tts.MAI_VOICE_2,
        "style": None,
        "output_format": tts.AZURE_OUTPUT_FORMAT,
    }


def test_cached_render_configuration_does_not_require_credentials(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_azure_environment(monkeypatch)

    assert tts.azure_service_kwargs(tts.MAI_VOICE_2)["voice"] == tts.MAI_VOICE_2


def test_mai_environment_rejects_a_different_region(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_azure_environment(monkeypatch)
    monkeypatch.setenv("SPEECH_KEY", "placeholder")
    monkeypatch.setenv("SPEECH_REGION", "eastus")

    with pytest.raises(RuntimeError, match="canadacentral"):
        tts.configure_azure_speech_environment(tts.MAI_VOICE_2)
