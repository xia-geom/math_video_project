"""Synthesize once with the existing Azure adapter, measure, then freeze audio.

No retries to fish for a shorter take; no tempo filters; no audio sent elsewhere.
A rejected timing plan retains its exact clips for inspection and reuse.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from miscellaneous.bac_sciences_ouvertures_fr.project import ROOT


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audio_info(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    data = json.loads(result.stdout)
    tracks = [s for s in data["streams"] if s["codec_type"] == "audio"]
    duration = float(data["format"]["duration"])
    if len(tracks) != 1 or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Expected a nonempty single-track narration file")
    return {"duration_seconds": duration, "channels": tracks[0]["channels"],
            "sample_rate": int(tracks[0]["sample_rate"])}


def selection(spec: dict) -> tuple[str, str, str, str]:
    from tools.tts import VOICE_LOCALES, resolve_voice

    selector = os.getenv("UQAM_OUVERTURES_VOICE", os.getenv(
        "UQAM_PROMO_VOICE", os.getenv("MANIM_VOICE", spec["voice_selector"])))
    voice = resolve_voice(selector)
    return selector, voice, os.getenv("UQAM_OUVERTURES_RATE", spec["voice_rate"]), VOICE_LOCALES.get(voice, "fr-CA")


def prepare_narration(spec: dict, output: Path, cache: Path | None = None) -> dict:
    from tools.tts import azure_service_kwargs, configure_azure_speech_environment, ssml

    selector, voice, rate, locale = selection(spec)
    options = azure_service_kwargs(voice)
    helper_hash = sha256(ROOT / "tools/tts.py")
    cache = cache or Path(os.getenv(
        "UQAM_OUVERTURES_AUDIO_CACHE", str(ROOT / "media/voiceovers/uqam_ouvertures_frozen")))
    output.mkdir(parents=True, exist_ok=True)
    result = {"provider": "AzureService", "voice_selector": selector, "voice": voice,
              "rate": rate, "locale": locale, "tts_helper_sha256": helper_hash,
              "audio_modified": False, "listening_review": "pending", "clips": []}
    # Write incremental metadata so even a failed request leaves useful evidence.
    metadata = output / "audio.json"
    for beat in spec["beats"]:
        wrapped = ssml(beat["text"], rate=rate, locale=locale)
        request = {"version": 1, "ssml": wrapped, "config": options, "tts_helper_sha256": helper_hash}
        key = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()
        directory = cache / key
        record_path = directory / "record.json"
        reused = record_path.is_file()
        if reused:
            record = json.loads(record_path.read_text(encoding="utf-8"))
            source = directory / "take.mp3"
            if record["request"] != request or sha256(source) != record["sha256"]:
                raise ValueError("Frozen audio cache integrity failure; no automatic resynthesis")
        else:
            configure_azure_speech_environment(voice, require_credentials=True)
            from manim_voiceover.services.azure import AzureService

            directory.mkdir(parents=True, exist_ok=True)
            lock = directory / ".generating"
            try:
                with lock.open("x", encoding="utf-8") as handle:
                    handle.write("One explicit Azure attempt in progress.\n")
            except FileExistsError as exc:
                raise RuntimeError(f"Audio generation already in progress: {directory}") from exc
            try:
                service = AzureService(**options, cache_dir=directory)
                data = service.generate_from_text(wrapped, path="take.mp3")
                source = directory / data["original_audio"]
                if source.resolve() != (directory / "take.mp3").resolve():
                    raise ValueError("Unexpected Azure output path")
                info = audio_info(source)
                record = {"request": request, "sha256": sha256(source), **info}
                temporary = record_path.with_suffix(".tmp")
                temporary.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                temporary.replace(record_path)
            finally:
                lock.unlink(missing_ok=True)
        measured = audio_info(source)
        target = output / f"{beat['id']}.mp3"
        if target.exists():
            raise FileExistsError(f"Refusing to overwrite narration: {target}")
        shutil.copyfile(source, target)
        result["clips"].append({"id": beat["id"], "path": target.name,
                                "text": beat["text"], "ssml": wrapped, "cache_key": key,
                                "cache_reused": reused, "sha256": sha256(target), **measured})
        metadata.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def verify_package(spec: dict, path: Path) -> dict:
    """Offline render input: exact texts, selected voice, helper, hashes and duration."""
    package = json.loads(path.read_text(encoding="utf-8"))
    _, voice, rate, locale = selection(spec)
    if [c["id"] for c in package["clips"]] != [b["id"] for b in spec["beats"]]:
        raise ValueError("Wrong narration order")
    if (package["voice"], package["rate"], package["locale"]) != (voice, rate, locale):
        raise ValueError("Narration package does not match the selected voice/rate/locale")
    if package["tts_helper_sha256"] != sha256(ROOT / "tools/tts.py"):
        raise ValueError("Shared narration helper changed since synthesis")
    for beat, clip in zip(spec["beats"], package["clips"], strict=True):
        if clip["text"] != beat["text"]:
            raise ValueError("Narration is stale relative to the script")
        audio = (path.parent / clip["path"]).resolve()
        if audio.parent != path.parent.resolve() or sha256(audio) != clip["sha256"]:
            raise ValueError("Narration file path/hash mismatch")
        if abs(audio_info(audio)["duration_seconds"] - clip["duration_seconds"]) > 0.001:
            raise ValueError("Narration duration differs from the measured package")
    return package
