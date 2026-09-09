from __future__ import annotations

from pathlib import Path
import tempfile
import unittest
import wave

import v4_audio
import v4_narration


FORBIDDEN_PHRASE = "Une base largement commune"


def valid_source() -> str:
    """Build a compact valid source with V4's exact scene/cue contract."""

    sections = []
    for scene_index, scene_id in enumerate(
        v4_narration.EXPECTED_SCENE_IDS,
        start=1,
    ):
        cues = [
            f"Phrase {scene_index}, repère {cue_index}."
            for cue_index in range(
                1,
                v4_narration.EXPECTED_CUE_COUNTS[scene_id] + 1,
            )
        ]
        sections.append(f"[{scene_id}]\n" + "\n".join(cues))
    return "\n\n".join(sections) + "\n"


def as_engine_narration(
    scene: v4_narration.NarrationScene,
) -> v4_audio.Narration:
    """Adapt the V4 authored source to the version-neutral Azure engine."""

    return v4_audio.Narration(scene.scene_id, scene.cues)


def write_pcm_wav(
    path: Path,
    *,
    duration_ms: int,
    rate: int = 48_000,
) -> None:
    frames = round(rate * duration_ms / 1000)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(b"\0\0" * frames)


class NarrationSourceTests(unittest.TestCase):
    def test_source_has_exact_order_and_sentence_level_cue_counts(self) -> None:
        parsed = v4_narration.load_narration()

        self.assertEqual(
            tuple(parsed),
            v4_narration.EXPECTED_SCENE_IDS,
        )
        self.assertEqual(
            {scene_id: len(scene.cues) for scene_id, scene in parsed.items()},
            v4_narration.EXPECTED_CUE_COUNTS,
        )
        self.assertEqual(sum(len(scene.cues) for scene in parsed.values()), 55)
        self.assertNotIn("v4_02_reading_the_table", parsed)

    def test_computing_narration_states_the_shared_core_and_profile_differences(self) -> None:
        computing = v4_narration.NARRATIONS[
            "v4_08_mathematics_computing"
        ].text
        profiles = v4_narration.NARRATIONS[
            "v4_09_computing_profiles"
        ].text

        self.assertIn("partagent le même noyau de cours", computing)
        self.assertIn("structures de données", computing)
        self.assertIn("bases de données ou les systèmes", computing)
        self.assertIn("théorie des groupes", profiles)
        self.assertIn("théorie des anneaux", profiles)
        self.assertIn("Statistique II", profiles)
        self.assertIn("Régression", profiles)
        self.assertIn("apprentissage statistique", profiles)
        self.assertIn("demeure commun aux deux profils", profiles)

    def test_julien_revision_and_conclusion_are_present(self) -> None:
        all_text = " ".join(
            scene.text for scene in v4_narration.NARRATIONS.values()
        )
        conclusion = v4_narration.NARRATIONS["v4_12_conclusion"].text
        self.assertIn("site du Département de mathématiques", all_text)
        self.assertIn("d’autres disciplines", all_text)
        self.assertIn("En deuxième année", all_text)
        self.assertIn("La concentration mathématiques fondamentales", all_text)
        self.assertIn("La concentration statistique", all_text)
        self.assertIn("deux profils", all_text)
        self.assertIn("méthodes que l’on souhaite maîtriser", all_text)
        self.assertIn("ouvrent des portes", conclusion)
        self.assertIn("construire votre avenir", conclusion)

    def test_every_cue_fits_at_most_two_short_subtitle_lines(self) -> None:
        for scene in v4_narration.NARRATIONS.values():
            for cue in scene.cues:
                with self.subTest(scene=scene.scene_id, cue=cue):
                    lines = v4_narration.wrap_subtitle(cue)
                    self.assertIn(len(lines), (1, 2))
                    self.assertLessEqual(
                        max(map(len, lines)),
                        v4_narration.SUBTITLE_LINE_WIDTH,
                    )

    def test_forbidden_repetitive_phrase_is_absent(self) -> None:
        source = v4_narration.NARRATION_PATH.read_text(encoding="utf-8")
        self.assertNotIn(FORBIDDEN_PHRASE.casefold(), source.casefold())

    def test_rejects_missing_unknown_duplicate_and_non_sentence_cues(self) -> None:
        source = valid_source()
        first_id = v4_narration.EXPECTED_SCENE_IDS[0]
        last_id = v4_narration.EXPECTED_SCENE_IDS[-1]
        last_section = (
            f"[{last_id}]\n"
            + "\n".join(
                f"Phrase {len(v4_narration.EXPECTED_SCENE_IDS)}, repère {index}."
                for index in range(
                    1,
                    v4_narration.EXPECTED_CUE_COUNTS[last_id] + 1,
                )
            )
            + "\n"
        )
        cases = (
            source.replace(last_section, ""),
            source + "\n[v4_12_unknown]\nInconnue.\n",
            source + f"\n[{first_id}]\nEncore.\n",
            source.replace(
                "Phrase 1, repère 1.",
                "Phrase sans ponctuation",
                1,
            ),
            source.replace(
                "Phrase 1, repère 1.",
                "Première phrase. Deuxième phrase.",
                1,
            ),
        )
        for broken in cases:
            with self.subTest(broken=broken[-100:]):
                with self.assertRaises(v4_narration.NarrationError):
                    v4_narration.parse_narration_text(broken)


class AzurePolicyTests(unittest.TestCase):
    def test_policy_is_uniform_sylvie_at_measured_rate(self) -> None:
        policy = v4_narration.V4_AUDIO_POLICY

        self.assertEqual(policy.provider, "azure")
        self.assertEqual(policy.voice, "fr-CA-SylvieNeural")
        self.assertEqual(policy.locale, "fr-CA")
        self.assertEqual(policy.rate, "-10%")
        self.assertEqual(policy.lead_silence_ms, 350)
        self.assertEqual(policy.intercue_break_ms, 180)
        self.assertEqual(policy.minimum_tail_silence_ms, 800)
        self.assertEqual(policy.target_dbfs, -18.5)
        self.assertIsNone(policy.target_duration_ms)
        self.assertFalse(policy.allow_time_stretch)
        self.assertFalse(policy.allow_speed_up)

    def test_ssml_uses_uniform_rate_breaks_and_bookmarks(self) -> None:
        scene = as_engine_narration(
            v4_narration.NARRATIONS["v4_01_opening"]
        )
        policy = v4_narration.V4_AUDIO_POLICY
        config = v4_audio.AzureConfig(
            voice=policy.voice,
            locale=policy.locale,
            rate=policy.rate,
            lead_silence_ms=policy.lead_silence_ms,
            tail_silence_ms=policy.minimum_tail_silence_ms,
            intercue_break_ms=policy.intercue_break_ms,
            target_dbfs=policy.target_dbfs,
        )

        ssml = v4_audio.build_azure_ssml(scene, config)
        self.assertIn('<voice name="fr-CA-SylvieNeural">', ssml)
        self.assertIn('<prosody rate="-10%">', ssml)
        self.assertEqual(
            ssml.count('<break time="180ms"/>'),
            len(scene.cues) - 1,
        )
        self.assertEqual(ssml.count("<bookmark "), len(scene.cues))

    def test_engine_refuses_to_speed_or_stretch_overlong_speech(self) -> None:
        narration = v4_audio.Narration(
            "v4_audio_fit_test",
            ("Une phrase de validation.",),
        )
        policy = v4_narration.V4_AUDIO_POLICY
        config = v4_audio.AzureConfig(
            voice=policy.voice,
            locale=policy.locale,
            rate=policy.rate,
            lead_silence_ms=policy.lead_silence_ms,
            tail_silence_ms=policy.minimum_tail_silence_ms,
            intercue_break_ms=policy.intercue_break_ms,
            target_duration_ms=2_500,
            target_dbfs=policy.target_dbfs,
            output_format="Riff48Khz16BitMonoPcm",
        )

        def overlong(_ssml: str, output: Path) -> dict[str, int]:
            write_pcm_wav(output, duration_ms=2_000)
            return {"cue_000": 0}

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "scene.wav"
            with self.assertRaisesRegex(
                v4_audio.SynthesisError,
                "does not fit the authored scene duration",
            ):
                v4_audio.generate_azure(
                    narration,
                    output,
                    config=config,
                    raw_synthesizer=overlong,
                )
            self.assertFalse(output.exists())
            self.assertFalse(v4_audio.voice_metadata_path(output).exists())

    def test_v4_facade_cache_contract_uses_narration_digest(self) -> None:
        scene = as_engine_narration(
            v4_narration.NARRATIONS["v4_09_computing_profiles"]
        )
        policy = v4_narration.V4_AUDIO_POLICY
        config = v4_audio.AzureConfig(
            voice=policy.voice,
            locale=policy.locale,
            rate=policy.rate,
            lead_silence_ms=policy.lead_silence_ms,
            tail_silence_ms=policy.minimum_tail_silence_ms,
            intercue_break_ms=policy.intercue_break_ms,
            target_dbfs=policy.target_dbfs,
        )

        first = v4_audio.cache_key(scene, config)
        changed = v4_audio.Narration(
            scene.scene_id,
            scene.cues[:-1] + ("Une formulation modifiée.",),
        )
        second = v4_audio.cache_key(changed, config)
        self.assertRegex(scene.digest, r"^[0-9a-f]{64}$")
        self.assertNotEqual(first, second)

    def test_v4_cache_and_cues_invalidate_when_transcript_changes(self) -> None:
        narration = as_engine_narration(
            v4_narration.NARRATIONS["v4_01_opening"]
        )
        policy = v4_narration.V4_AUDIO_POLICY
        config = v4_audio.AzureConfig(
            voice=policy.voice,
            locale=policy.locale,
            rate=policy.rate,
            lead_silence_ms=policy.lead_silence_ms,
            tail_silence_ms=policy.minimum_tail_silence_ms,
            intercue_break_ms=policy.intercue_break_ms,
            target_duration_ms=4_000,
            target_dbfs=policy.target_dbfs,
            output_format="Riff48Khz16BitMonoPcm",
        )

        def synthesize(_ssml: str, output: Path) -> dict[str, int]:
            write_pcm_wav(output, duration_ms=2_000)
            return {
                "cue_000": 0,
                "cue_001": 6_000_000,
                "cue_002": 12_000_000,
            }

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "scene.wav"
            metadata = v4_audio.generate_azure(
                narration,
                output,
                config=config,
                raw_synthesizer=synthesize,
            )
            self.assertEqual(
                metadata,
                v4_audio.validate_existing(
                    narration,
                    output,
                    config=config,
                ),
            )
            intervals = v4_audio.subtitle_intervals(narration, metadata)
            self.assertEqual(len(intervals), len(narration.cues))
            self.assertLessEqual(intervals[-1].end, 4.0)

            changed = v4_audio.Narration(
                narration.scene_id,
                narration.cues[:-1] + ("Une formulation modifiée.",),
            )
            with self.assertRaises(v4_audio.StaleAudioError):
                v4_audio.validate_existing(
                    changed,
                    output,
                    config=config,
                )


if __name__ == "__main__":
    unittest.main()
