from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

import numpy as np


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE_ROOT))

import render_video as renderer  # noqa: E402


def narration_source_without_section(source: str, scene_id: str) -> str:
    """Remove one complete INI-like narration section from a valid source."""
    output: list[str] = []
    skipping = False
    for line in source.splitlines():
        if line == f"[{scene_id}]":
            skipping = True
            continue
        if skipping and re.fullmatch(r"\[[a-z0-9_]+\]", line):
            skipping = False
        if not skipping:
            output.append(line)
    return "\n".join(output) + "\n"


def narration_source_with_empty_section(source: str, scene_id: str) -> str:
    """Keep a section header but remove every cue below it."""
    output: list[str] = []
    skipping_cues = False
    for line in source.splitlines():
        if line == f"[{scene_id}]":
            output.append(line)
            skipping_cues = True
            continue
        if skipping_cues and re.fullmatch(r"\[[a-z0-9_]+\]", line):
            skipping_cues = False
        if not skipping_cues:
            output.append(line)
    return "\n".join(output) + "\n"


def make_scene(
    scene_id: str = "01_intro",
    cues: tuple[str, ...] = ("Une phrase courte.", "Une autre phrase courte."),
    duration: float = 8.0,
) -> renderer.Scene:
    return renderer.Scene(
        scene_id=scene_id,
        program_key="intro",
        title="Titre",
        phrase="Phrase",
        narration=renderer.Narration(scene_id, cues),
        visual="intro",
        highlight=[],
        labels=[],
        duration=duration,
    )


class NarrationParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.valid_source = renderer.NARRATION_PATH.read_text(encoding="utf-8")

    def parse_text(self, source: str) -> dict[str, renderer.Narration]:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "voiceover_fr.txt"
            path.write_text(source, encoding="utf-8")
            return renderer.load_narration(path)

    def assert_invalid(self, source: str, message_fragment: str) -> None:
        with self.assertRaisesRegex(ValueError, re.escape(message_fragment)):
            self.parse_text(source)

    def test_authoritative_source_has_exactly_the_fourteen_expected_scene_ids(self) -> None:
        narrations = renderer.load_narration()
        self.assertEqual(tuple(narrations), renderer.expected_scene_ids())
        self.assertEqual(len(narrations), 14)
        self.assertGreater(sum(len(item.cues) for item in narrations.values()), 14)
        for narration in narrations.values():
            self.assertTrue(narration.cues)
            for cue in narration.cues:
                self.assertTrue(cue.endswith((".", "?", "!", "…")))
                wrapped = renderer.wrap_subtitle(cue)
                self.assertLessEqual(len(wrapped), 2)
                self.assertTrue(all(len(line) <= 42 for line in wrapped))

    def test_duplicate_section_is_rejected(self) -> None:
        self.assert_invalid(
            self.valid_source + "\n[01_intro]\nTexte dupliqué.\n",
            "Duplicate narration section [01_intro]",
        )

    def test_missing_unknown_and_empty_sections_are_rejected(self) -> None:
        cases = {
            "missing: 01_intro": narration_source_without_section(
                self.valid_source, "01_intro"
            ),
            "unknown: 99_extra": (
                self.valid_source + "\n[99_extra]\nSection inconnue.\n"
            ),
            "empty: 01_intro": narration_source_with_empty_section(
                self.valid_source, "01_intro"
            ),
        }
        for expected_message, source in cases.items():
            with self.subTest(expected_message=expected_message):
                self.assert_invalid(source, expected_message)

    def test_text_before_header_and_unpunctuated_cue_are_rejected(self) -> None:
        self.assert_invalid(
            "Texte orphelin.\n" + self.valid_source,
            "Narration text before the first section",
        )
        unpunctuated = self.valid_source.replace(
            "L’UQAM offre trois concentrations au baccalauréat en mathématiques.",
            "L’UQAM offre trois concentrations au baccalauréat en mathématiques",
            1,
        )
        self.assert_invalid(
            unpunctuated,
            "Narration cue must end in sentence punctuation",
        )


class ExistingAudioTests(unittest.TestCase):
    def write_cache(
        self,
        directory: Path,
        scene: renderer.Scene,
        *,
        narration_digest: str | None = None,
    ) -> Path:
        audio_path = directory / f"{scene.scene_id}.wav"
        audio = (
            renderer.AudioSegment.silent(duration=1000, frame_rate=48000)
            .set_channels(1)
            .set_sample_width(2)
        )
        exported = audio.export(audio_path, format="wav")
        exported.close()
        metadata = {
            "schema": 1,
            "scene_id": scene.scene_id,
            "narration_sha256": narration_digest or scene.narration.digest,
            "audio_sha256": renderer.sha256_file(audio_path),
            "provider": "azure",
            "voice": "test-voice",
            "rate": "-14%",
            "duration_ms": len(audio),
        }
        renderer.voice_metadata_path(audio_path).write_text(
            json.dumps(metadata),
            encoding="utf-8",
        )
        return audio_path

    def test_existing_mode_accepts_matching_cache_without_any_synthesis(self) -> None:
        scene = make_scene()
        with tempfile.TemporaryDirectory() as temp_dir:
            voice_dir = Path(temp_dir)
            self.write_cache(voice_dir, scene)
            with (
                mock.patch.object(renderer, "VOICE_DIR", voice_dir),
                mock.patch.object(renderer, "synthesize_espeak") as espeak,
                mock.patch.object(renderer, "synthesize_azure") as azure,
                mock.patch.object(
                    renderer.AudioSegment,
                    "from_wav",
                    return_value=mock.MagicMock(__len__=lambda _: 1000),
                ),
            ):
                renderer.prepare_audio([scene], tts="existing")

            espeak.assert_not_called()
            azure.assert_not_called()
            self.assertAlmostEqual(scene.duration, 1.0, places=3)
            self.assertEqual(scene.audio_path, voice_dir / "01_intro.wav")

    def test_existing_mode_fails_for_missing_audio_without_espeak_fallback(self) -> None:
        scene = make_scene()
        with tempfile.TemporaryDirectory() as temp_dir:
            voice_dir = Path(temp_dir)
            with (
                mock.patch.object(renderer, "VOICE_DIR", voice_dir),
                mock.patch.object(renderer, "synthesize_espeak") as espeak,
                self.assertRaisesRegex(RuntimeError, "missing or stale"),
            ):
                renderer.prepare_audio([scene], tts="existing")
            espeak.assert_not_called()

    def test_transcript_change_invalidates_existing_audio(self) -> None:
        original_scene = make_scene()
        changed_scene = make_scene(cues=("Le texte a changé.",))
        with tempfile.TemporaryDirectory() as temp_dir:
            voice_dir = Path(temp_dir)
            self.write_cache(
                voice_dir,
                changed_scene,
                narration_digest=original_scene.narration.digest,
            )
            with (
                mock.patch.object(renderer, "VOICE_DIR", voice_dir),
                mock.patch.object(renderer, "synthesize_espeak") as espeak,
                self.assertRaisesRegex(RuntimeError, "missing or stale"),
            ):
                renderer.prepare_audio([changed_scene], tts="existing")
            espeak.assert_not_called()


class SceneSelectionTests(unittest.TestCase):
    def test_select_scenes_preserves_original_index_and_rejects_unknown_id(self) -> None:
        scenes = [
            make_scene("01_intro"),
            make_scene("02_math_analysis"),
            make_scene("05_closing"),
        ]
        selected = renderer.select_scenes(scenes, "02_math_analysis")
        self.assertEqual(selected, [(2, scenes[1])])
        with self.assertRaisesRegex(SystemExit, "Unknown scene: absent"):
            renderer.select_scenes(scenes, "absent")

    def test_scene_cli_prepares_only_the_requested_scene(self) -> None:
        scenes = [make_scene("01_intro"), make_scene("05_closing")]
        output = Path("/tmp/uqam-selected-scene.mp4")
        with (
            mock.patch.object(sys, "argv", ["render_video.py", "--scene", "05_closing"]),
            mock.patch.object(renderer, "build_scenes", return_value=scenes),
            mock.patch.object(renderer, "check_environment", return_value={}),
            mock.patch.object(renderer, "prepare_audio") as prepare_audio,
            mock.patch.object(renderer, "render_scene", return_value=output) as render_scene,
            mock.patch.object(renderer, "validate_video"),
            mock.patch.object(renderer, "render_table_stills") as render_tables,
            mock.patch.object(renderer, "write_srt") as write_srt,
            mock.patch.object(renderer, "build_storyboard") as storyboard,
            mock.patch("builtins.print"),
        ):
            renderer.main()

        self.assertEqual(prepare_audio.call_args.args[0], [scenes[1]])
        render_scene.assert_called_once_with(scenes[1], 2, renderer.FPS)
        render_tables.assert_not_called()
        write_srt.assert_not_called()
        storyboard.assert_not_called()


class SubtitleTests(unittest.TestCase):
    def test_sentence_cues_get_contiguous_short_intervals(self) -> None:
        scene = make_scene(
            cues=(
                "Première phrase, volontairement concise.",
                "Deuxième phrase, affichée séparément.",
                "Troisième et dernière phrase.",
            ),
            duration=10.0,
        )
        intervals = renderer.subtitle_intervals(scene)
        self.assertEqual(len(intervals), 3)
        self.assertAlmostEqual(
            intervals[0][0], renderer.LEAD_SILENCE_MS / 1000, places=3
        )
        self.assertAlmostEqual(
            intervals[-1][1],
            scene.duration - renderer.TAIL_SILENCE_MS / 1000,
            places=3,
        )
        for index, (start, end, text) in enumerate(intervals):
            self.assertLess(start, end)
            if index:
                self.assertAlmostEqual(start, intervals[index - 1][1], places=6)
            lines = text.splitlines()
            self.assertLessEqual(len(lines), 2)
            self.assertTrue(all(len(line) <= 42 for line in lines))

    def test_srt_has_one_block_per_sentence_and_monotonic_times(self) -> None:
        scenes = [
            make_scene(
                "01_intro",
                ("Première phrase.", "Deuxième phrase."),
                duration=6.0,
            ),
            make_scene(
                "05_closing",
                ("Troisième phrase.", "Quatrième phrase."),
                duration=6.0,
            ),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.object(renderer, "DIST_DIR", Path(temp_dir)):
                path = renderer.write_srt(scenes)
            blocks = path.read_text(encoding="utf-8").strip().split("\n\n")

        self.assertEqual(len(blocks), 4)
        previous_end = -1
        timestamp_pattern = re.compile(
            r"^(\d{2}:\d{2}:\d{2},\d{3}) --> "
            r"(\d{2}:\d{2}:\d{2},\d{3})$"
        )

        def milliseconds(value: str) -> int:
            hours, minutes, rest = value.split(":")
            seconds, millis = rest.split(",")
            return (
                int(hours) * 3_600_000
                + int(minutes) * 60_000
                + int(seconds) * 1000
                + int(millis)
            )

        for expected_number, block in enumerate(blocks, start=1):
            lines = block.splitlines()
            self.assertEqual(lines[0], str(expected_number))
            match = timestamp_pattern.fullmatch(lines[1])
            self.assertIsNotNone(match)
            start, end = (milliseconds(value) for value in match.groups())
            self.assertGreaterEqual(start, previous_end)
            self.assertGreater(end, start)
            previous_end = end
            subtitle_lines = lines[2:]
            self.assertLessEqual(len(subtitle_lines), 2)
            self.assertTrue(all(len(line) <= 42 for line in subtitle_lines))


class FadeTests(unittest.TestCase):
    def test_final_sample_is_fully_background(self) -> None:
        scene = make_scene(duration=5.0)
        final_sample = scene.duration - 1 / renderer.FPS
        self.assertEqual(renderer.scene_opacity(0.0, scene.duration, renderer.FPS), 0.0)
        self.assertEqual(
            renderer.scene_opacity(final_sample, scene.duration, renderer.FPS),
            0.0,
        )
        self.assertGreater(
            renderer.scene_opacity(scene.duration / 2, scene.duration, renderer.FPS),
            0.99,
        )

        foreground = np.zeros((renderer.HEIGHT, renderer.WIDTH, 3), dtype=np.uint8)
        expected_background = np.asarray(renderer.base_background().convert("RGB"))
        with mock.patch.object(renderer, "draw_intro", return_value=foreground):
            frame = renderer.make_frame(scene)(final_sample)
        np.testing.assert_array_equal(frame, expected_background)


class SvgTableTests(unittest.TestCase):
    def test_svg_contains_thirty_editable_labelled_cells_and_no_raster(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "table.svg"
            renderer.render_table_svg("math", path)
            root = ET.parse(path).getroot()

        namespace = {"svg": renderer.SVG_NS}
        cells = root.findall(".//svg:g[@class='course-cell']", namespace)
        self.assertEqual(len(cells), 30)
        self.assertEqual(
            {cell.get("id") for cell in cells},
            {
                f"cell-{row}-{column}"
                for row in range(1, 7)
                for column in range(1, 6)
            },
        )
        for cell in cells:
            self.assertTrue(cell.get("data-full-title"))
            labels = cell.findall("./svg:text[@class='course-label']", namespace)
            self.assertEqual(len(labels), 1)
            tspans = labels[0].findall("./svg:tspan", namespace)
            self.assertTrue(tspans)
            self.assertTrue(all((tspan.text or "").strip() for tspan in tspans))

        all_text = [
            "".join(element.itertext()).strip()
            for element in root.findall(".//svg:text", namespace)
        ]
        self.assertIn(renderer.PATHWAY_LABEL, all_text)
        self.assertEqual(
            renderer.PATHWAY_LABEL,
            "Cheminement recommandé — début à l’automne — "
            "5 cours/session — 2025–2026",
        )
        self.assertFalse(root.findall(".//svg:image", namespace))
        serialized = ET.tostring(root, encoding="unicode")
        self.assertNotIn("data:image", serialized)


if __name__ == "__main__":
    unittest.main()
