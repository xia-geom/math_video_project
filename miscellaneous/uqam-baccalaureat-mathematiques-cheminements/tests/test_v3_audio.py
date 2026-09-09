from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import wave

import v3_audio


def valid_source() -> str:
    sections = []
    for index, scene_id in enumerate(v3_audio.EXPECTED_SCENE_IDS):
        cues = [f"Phrase {index + 1}."]
        if index == 8:
            cues = [
                "La concentration informatique propose deux profils.",
                "Le profil mathématiques approfondit les structures.",
                "Le profil statistique ajoute la science des données.",
            ]
        sections.append(f"[{scene_id}]\n" + "\n".join(cues))
    return "\n\n".join(sections) + "\n"


def write_pcm_wav(path: Path, duration_ms: int = 1000, rate: int = 48_000) -> None:
    frames = round(rate * duration_ms / 1000)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\0\0" * frames)


def write_padded_pcm_tone(
    path: Path,
    *,
    lead_ms: int = 100,
    tone_ms: int = 300,
    tail_ms: int = 300,
    rate: int = 48_000,
) -> None:
    lead_frames = round(rate * lead_ms / 1000)
    tone_frames = round(rate * tone_ms / 1000)
    tail_frames = round(rate * tail_ms / 1000)
    sample = (4096).to_bytes(2, "little", signed=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(
            b"\0\0" * lead_frames
            + sample * tone_frames
            + b"\0\0" * tail_frames
        )


class NarrationParsingTests(unittest.TestCase):
    def test_parses_exact_eleven_scene_ids_and_sentence_cues(self) -> None:
        parsed = v3_audio.parse_narration_text(valid_source())
        self.assertEqual(tuple(parsed), v3_audio.EXPECTED_SCENE_IDS)
        self.assertEqual(len(parsed), 11)
        self.assertEqual(len(parsed["v3_09_computing_profiles"].cues), 3)

    def test_rejects_missing_unknown_duplicate_and_non_sentence_cues(self) -> None:
        source = valid_source()
        cases = (
            source.replace("[v3_11_guide]\nPhrase 11.\n", ""),
            source + "\n[v3_12_unknown]\nInconnue.\n",
            source + "\n[v3_01_opening]\nEncore.\n",
            source.replace("Phrase 1.", "Phrase sans ponctuation"),
            source.replace("Phrase 1.", "Première phrase. Deuxième phrase."),
        )
        for broken in cases:
            with self.subTest(broken=broken[-80:]):
                with self.assertRaises(v3_audio.NarrationError):
                    v3_audio.parse_narration_text(broken)


class SsmlTests(unittest.TestCase):
    def test_bookmark_precedes_each_escaped_cue(self) -> None:
        narration = v3_audio.Narration(
            "v3_01_opening",
            ("Un < deux.", "Deux & trois."),
        )
        ssml = v3_audio.build_azure_ssml(narration, v3_audio.AzureConfig())
        first = ssml.index('<bookmark mark="cue_000"/>')
        first_text = ssml.index("Un &lt; deux.")
        second = ssml.index('<bookmark mark="cue_001"/>')
        second_text = ssml.index("Deux &amp; trois.")
        self.assertLess(first, first_text)
        self.assertLess(first_text, second)
        self.assertLess(second, second_text)


class AudioCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.narration = v3_audio.Narration(
            "v3_09_computing_profiles",
            (
                "La concentration propose deux profils.",
                "Le profil mathématiques approfondit les structures.",
                "Le profil statistique ajoute la science des données.",
            ),
        )
        self.config = v3_audio.AzureConfig(
            lead_silence_ms=350,
            tail_silence_ms=750,
        )

    @staticmethod
    def fake_synthesizer(ssml: str, output: Path) -> dict[str, int]:
        assert ssml.index("cue_000") < ssml.index("cue_001") < ssml.index("cue_002")
        write_pcm_wav(output, duration_ms=2000)
        return {
            "cue_000": 0,
            "cue_001": 4_000_000,
            "cue_002": 11_000_000,
        }

    def test_offline_generation_records_exact_bookmark_starts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            audio_path = Path(temp) / "scene.wav"
            metadata = v3_audio.generate_azure(
                self.narration,
                audio_path,
                config=self.config,
                raw_synthesizer=self.fake_synthesizer,
            )
            starts = [
                cue["start_ticks_100ns"]
                for cue in metadata["cues"]
            ]
            self.assertEqual(starts, [3_500_000, 7_500_000, 14_500_000])
            self.assertEqual(
                [cue["start_ms"] for cue in metadata["cues"]],
                [350.0, 750.0, 1450.0],
            )
            self.assertEqual(metadata["speech"]["end_ticks_100ns"], 23_500_000)
            self.assertEqual(metadata, v3_audio.validate_existing(
                self.narration,
                audio_path,
                config=self.config,
            ))

    def test_native_bookmark_mode_keeps_one_request_and_legacy_cache_identity(self) -> None:
        calls: list[str] = []

        def synthesize(ssml: str, output: Path) -> dict[str, int]:
            calls.append(ssml)
            return self.fake_synthesizer(ssml, output)

        with tempfile.TemporaryDirectory() as temp:
            audio_path = Path(temp) / "scene.wav"
            metadata = v3_audio.generate_azure(
                self.narration,
                audio_path,
                config=self.config,
                raw_synthesizer=synthesize,
            )

        self.assertEqual(len(calls), 1)
        self.assertNotIn("timing_mode", self.config.cache_dict())
        self.assertEqual(
            metadata["timing"],
            {
                "mode": v3_audio.TIMING_MODE_AZURE_BOOKMARKS,
                "source": "azure_bookmark_events",
            },
        )

    def test_live_synthesis_retries_transient_azure_failures(self) -> None:
        calls = 0

        def transient(
            ssml: str,
            output: Path,
            _config: v3_audio.AzureConfig,
        ) -> dict[str, int]:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise v3_audio.SynthesisError("temporary Azure timeout")
            return self.fake_synthesizer(ssml, output)

        with (
            tempfile.TemporaryDirectory() as temp,
            mock.patch.object(
                v3_audio,
                "azure_synthesize_raw",
                side_effect=transient,
            ),
            mock.patch.object(v3_audio.time, "sleep") as sleep,
        ):
            metadata = v3_audio.generate_azure(
                self.narration,
                Path(temp) / "scene.wav",
                config=self.config,
            )

        self.assertEqual(calls, 3)
        self.assertEqual(sleep.call_args_list, [mock.call(1), mock.call(2)])
        self.assertEqual(metadata["scene_id"], self.narration.scene_id)

    def test_cue_segment_mode_uses_exact_pcm_boundaries_and_validates_source(self) -> None:
        config = v3_audio.AzureConfig(
            lead_silence_ms=100,
            tail_silence_ms=300,
            intercue_break_ms=200,
            timing_mode=v3_audio.TIMING_MODE_CUE_SEGMENTS,
        )
        calls: list[str] = []

        def synthesize(ssml: str, output: Path) -> dict[str, int]:
            calls.append(ssml)
            write_padded_pcm_tone(output)
            return {}

        with tempfile.TemporaryDirectory() as temp:
            audio_path = Path(temp) / "scene.wav"
            metadata = v3_audio.generate_azure(
                self.narration,
                audio_path,
                config=config,
                raw_synthesizer=synthesize,
            )

            self.assertEqual(len(calls), len(self.narration.cues))
            self.assertTrue(all(ssml.count("<bookmark ") == 1 for ssml in calls))
            self.assertEqual(
                [cue["start_ticks_100ns"] for cue in metadata["cues"]],
                [1_000_000, 8_200_000, 15_400_000],
            )
            self.assertEqual(metadata["audio"]["frame_count"], 113_280)
            self.assertEqual(
                metadata["timing"],
                {
                    "mode": v3_audio.TIMING_MODE_CUE_SEGMENTS,
                    "source": "pcm_cue_segment_boundaries",
                },
            )
            self.assertEqual(
                metadata["synthesis_config"]["timing_mode"],
                v3_audio.TIMING_MODE_CUE_SEGMENTS,
            )
            self.assertEqual(
                metadata["synthesis_config"]["cue_segmentation"],
                {
                    "version": 1,
                    "edge_window_ms": 10,
                    "relative_threshold_db": -35.0,
                    "retained_lead_ms": 40,
                    "retained_tail_ms": 180,
                },
            )
            self.assertEqual(
                metadata,
                v3_audio.validate_existing(
                    self.narration,
                    audio_path,
                    config=config,
                ),
            )

            metadata_path = v3_audio.voice_metadata_path(audio_path)
            tampered = json.loads(metadata_path.read_text(encoding="utf-8"))
            tampered["timing"]["source"] = "unverified_estimate"
            metadata_path.write_text(json.dumps(tampered), encoding="utf-8")
            with self.assertRaises(v3_audio.StaleAudioError):
                v3_audio.validate_existing(
                    self.narration,
                    audio_path,
                    config=config,
                )

    def test_subtitles_use_bookmarks_and_final_speech_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            audio_path = Path(temp) / "scene.wav"
            metadata = v3_audio.generate_azure(
                self.narration,
                audio_path,
                config=self.config,
                raw_synthesizer=self.fake_synthesizer,
            )
            intervals = v3_audio.subtitle_intervals(self.narration, metadata)
            self.assertEqual(
                [(cue.start, cue.end) for cue in intervals],
                [(0.35, 0.75), (0.75, 1.45), (1.45, 2.35)],
            )
            self.assertEqual(
                intervals[-1].end,
                metadata["speech"]["end_ticks_100ns"] / v3_audio.TICKS_PER_SECOND,
            )

    def test_transcript_config_audio_and_metadata_changes_are_stale(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            audio_path = Path(temp) / "scene.wav"
            v3_audio.generate_azure(
                self.narration,
                audio_path,
                config=self.config,
                raw_synthesizer=self.fake_synthesizer,
            )
            changed = v3_audio.Narration(
                self.narration.scene_id,
                self.narration.cues[:-1] + ("Une autre phrase.",),
            )
            with self.assertRaises(v3_audio.StaleAudioError):
                v3_audio.validate_existing(changed, audio_path, config=self.config)
            with self.assertRaises(v3_audio.StaleAudioError):
                v3_audio.validate_existing(
                    self.narration,
                    audio_path,
                    config=v3_audio.AzureConfig(rate="-10%"),
                )

            with audio_path.open("ab") as handle:
                handle.write(b"tamper")
            with self.assertRaises(v3_audio.StaleAudioError):
                v3_audio.validate_existing(
                    self.narration, audio_path, config=self.config
                )

            # Regenerate, then alter an exact cue timestamp in metadata.
            v3_audio.generate_azure(
                self.narration,
                audio_path,
                config=self.config,
                raw_synthesizer=self.fake_synthesizer,
            )
            metadata_path = v3_audio.voice_metadata_path(audio_path)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["cues"][1]["start_ms"] += 1
            metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaises(v3_audio.StaleAudioError):
                v3_audio.validate_existing(
                    self.narration, audio_path, config=self.config
                )

    def test_failed_generation_preserves_existing_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            audio_path = Path(temp) / "scene.wav"
            metadata_path = v3_audio.voice_metadata_path(audio_path)
            audio_path.write_bytes(b"old-audio")
            metadata_path.write_text("old-metadata", encoding="utf-8")

            def fail(_ssml: str, _output: Path) -> dict[str, int]:
                raise RuntimeError("offline failure")

            with self.assertRaisesRegex(RuntimeError, "offline failure"):
                v3_audio.generate_azure(
                    self.narration,
                    audio_path,
                    config=self.config,
                    raw_synthesizer=fail,
                )
            self.assertEqual(audio_path.read_bytes(), b"old-audio")
            self.assertEqual(
                metadata_path.read_text(encoding="utf-8"),
                "old-metadata",
            )

    def test_missing_or_out_of_order_bookmarks_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            audio_path = Path(temp) / "scene.wav"

            def missing(_ssml: str, output: Path) -> dict[str, int]:
                write_pcm_wav(output, duration_ms=2000)
                return {"cue_000": 0, "cue_001": 4_000_000}

            with self.assertRaises(v3_audio.SynthesisError):
                v3_audio.generate_azure(
                    self.narration,
                    audio_path,
                    config=self.config,
                    raw_synthesizer=missing,
                )

            def unordered(_ssml: str, output: Path) -> dict[str, int]:
                write_pcm_wav(output, duration_ms=2000)
                return {
                    "cue_000": 0,
                    "cue_001": 9_000_000,
                    "cue_002": 8_000_000,
                }

            with self.assertRaises(v3_audio.SynthesisError):
                v3_audio.generate_azure(
                    self.narration,
                    audio_path,
                    config=self.config,
                    raw_synthesizer=unordered,
                )


if __name__ == "__main__":
    unittest.main()
