from __future__ import annotations

import io
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest import mock
import wave

import numpy as np

import render_v3
import v3_audio
import v3_visuals


def write_constant_pcm(path: Path, duration: float, sample: int) -> int:
    """Write an exact 48 kHz, 16-bit mono PCM segment for assembly tests."""

    frame_count = round(duration * 48_000)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(48_000)
        output.setcomptype("NONE", "not compressed")
        output.writeframes(struct.pack("<h", sample) * frame_count)
    return frame_count


def metadata_with_starts(*starts: float) -> dict[str, object]:
    return {
        "cues": [
            {
                "start_ticks_100ns": round(
                    start * v3_audio.TICKS_PER_SECOND
                )
            }
            for start in starts
        ]
    }


class RuntimeSourceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtimes = render_v3.build_runtimes()

    def test_exact_scene_clock_and_sentence_cue_count(self) -> None:
        self.assertEqual(len(self.runtimes), 11)
        self.assertEqual(
            [runtime.spec.id for runtime in self.runtimes],
            list(v3_audio.EXPECTED_SCENE_IDS),
        )
        self.assertEqual(
            sum(runtime.duration for runtime in self.runtimes),
            215.0,
        )
        self.assertEqual(
            sum(len(runtime.narration.cues) for runtime in self.runtimes),
            46,
        )

    def test_every_authored_subtitle_fits_two_short_lines(self) -> None:
        for runtime in self.runtimes:
            for cue in runtime.narration.cues:
                with self.subTest(scene=runtime.spec.id, cue=cue):
                    lines = render_v3.wrap_subtitle(cue)
                    self.assertIn(len(lines), (1, 2))
                    self.assertLessEqual(max(map(len, lines)), 42)

    def test_scene_selection_keeps_original_index_and_rejects_unknown(self) -> None:
        selected = render_v3.select_runtimes(
            self.runtimes,
            "v3_08_mathematics_computing",
        )
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0][0], 8)
        self.assertIs(selected[0][1], self.runtimes[7])
        with self.assertRaisesRegex(SystemExit, "Unknown scene"):
            render_v3.select_runtimes(self.runtimes, "not_a_scene")

    def test_main_prepares_only_requested_scene(self) -> None:
        requested = "v3_07_statistics"
        with (
            mock.patch.object(
                sys,
                "argv",
                ["render_v3.py", "--scene", requested, "--audio-only"],
            ),
            mock.patch.object(
                render_v3,
                "check_environment",
                return_value={"python": "test"},
            ),
            mock.patch.object(render_v3, "prepare_audio") as prepare,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            render_v3.main()

        prepare.assert_called_once()
        prepared = list(prepare.call_args.args[0])
        self.assertEqual(
            [runtime.spec.id for runtime in prepared],
            [requested],
        )
        self.assertEqual(prepare.call_args.kwargs["tts"], "existing")


class AzureConfigurationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtimes = render_v3.build_runtimes()

    def test_manifest_drives_exact_scene_configs(self) -> None:
        opening = render_v3.azure_config(self.runtimes[0], voice="test-voice")
        regular = render_v3.azure_config(self.runtimes[1], voice="test-voice")

        self.assertEqual(opening.voice, "test-voice")
        self.assertEqual(
            opening.rate,
            render_v3.V3_NARRATION["scene_rates"]["v3_01_opening"],
        )
        self.assertEqual(regular.rate, "-2%")
        self.assertEqual(opening.intercue_break_ms, 120)
        self.assertEqual(regular.intercue_break_ms, 120)
        self.assertEqual(opening.target_duration_ms, 7_000)
        self.assertEqual(regular.target_duration_ms, 16_000)
        self.assertEqual(opening.lead_silence_ms, 300)
        self.assertEqual(opening.tail_silence_ms, 600)
        self.assertEqual(opening.target_dbfs, -18.5)

    def test_existing_audio_failure_never_falls_back_to_synthesis(self) -> None:
        runtime = self.runtimes[0]
        with tempfile.TemporaryDirectory() as temporary:
            runtime.audio_path = Path(temporary) / "missing.wav"
            with (
                mock.patch.object(
                    render_v3,
                    "AUDIO_DIR",
                    Path(temporary),
                ),
                mock.patch.object(
                    v3_audio,
                    "validate_existing",
                    side_effect=v3_audio.StaleAudioError(
                        "recording is absent or stale"
                    ),
                ) as validate,
                mock.patch.object(v3_audio, "generate_azure") as generate,
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "Regenerate this exact segment",
                ):
                    render_v3.prepare_audio([runtime], tts="existing")

        validate.assert_called_once()
        generate.assert_not_called()


class BookmarkAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtimes = render_v3.build_runtimes()

    def test_all_default_actions_survive_and_semantic_actions_align(self) -> None:
        for runtime in self.runtimes:
            starts = tuple(
                1.0 + 1.25 * index
                for index in range(len(runtime.narration.cues))
            )
            runtime.metadata = metadata_with_starts(*starts)
            actual = render_v3.aligned_actions(runtime)
            defaults = {
                action.action: (action.start, action.end)
                for action in v3_visuals.DEFAULT_ACTIONS[runtime.spec.id]
            }
            semantic = render_v3.SEMANTIC_CUE_ACTIONS.get(
                runtime.spec.id,
                {},
            )

            with self.subTest(scene=runtime.spec.id):
                self.assertEqual(set(actual), set(defaults))
                for action, default_window in defaults.items():
                    if (
                        runtime.spec.id == "v3_05_common_foundation"
                        and action == "highlight_foundation"
                    ):
                        self.assertEqual(
                            actual[action],
                            (starts[1], starts[3]),
                        )
                    elif action in semantic:
                        start = starts[semantic[action]]
                        self.assertEqual(
                            actual[action],
                            (start, start + 0.5),
                        )
                    else:
                        self.assertEqual(actual[action], default_window)

    def test_late_guide_bookmark_cannot_break_final_hold(self) -> None:
        runtime = self.runtimes[-1]
        runtime.metadata = metadata_with_starts(1, 2, 3, 4, 13, 14)
        actual = render_v3.aligned_actions(runtime)
        self.assertEqual(actual["show_url"], (12.0, 12.5))


class PcmAssemblyTests(unittest.TestCase):
    def test_master_audio_concatenates_all_exact_scene_clocks(self) -> None:
        runtimes = render_v3.build_runtimes()
        with tempfile.TemporaryDirectory() as temporary:
            audio_dir = Path(temporary) / "audio"
            audio_dir.mkdir()
            expected_boundaries: list[tuple[int, int]] = []
            running_frames = 0
            for index, runtime in enumerate(runtimes, start=1):
                runtime.audio_path = audio_dir / f"{runtime.spec.id}.wav"
                expected_boundaries.append((running_frames, index))
                running_frames += write_constant_pcm(
                    runtime.audio_path,
                    runtime.duration,
                    index,
                )

            master_path = audio_dir / "master.wav"
            with (
                mock.patch.object(render_v3, "AUDIO_DIR", audio_dir),
                mock.patch.object(
                    render_v3,
                    "MASTER_AUDIO_PATH",
                    master_path,
                ),
            ):
                result = render_v3.build_master_audio(runtimes)

            self.assertEqual(result, master_path)
            self.assertEqual(running_frames, 215 * 48_000)
            with wave.open(str(master_path), "rb") as master:
                self.assertEqual(master.getnchannels(), 1)
                self.assertEqual(master.getsampwidth(), 2)
                self.assertEqual(master.getframerate(), 48_000)
                self.assertEqual(master.getnframes(), running_frames)
                for frame, expected_sample in expected_boundaries:
                    master.setpos(frame)
                    sample = struct.unpack("<h", master.readframes(1))[0]
                    self.assertEqual(sample, expected_sample)


class FinalHoldTests(unittest.TestCase):
    def test_guide_is_pixel_identical_through_final_two_seconds(self) -> None:
        runtime = render_v3.build_runtimes()[-1]
        frame = render_v3.make_frame(runtime)
        at_hold_start = frame(runtime.duration - 2.0)
        near_endpoint = frame(runtime.duration - 1 / render_v3.FPS)
        at_endpoint = frame(runtime.duration)

        self.assertEqual(
            at_hold_start.shape,
            (render_v3.HEIGHT, render_v3.WIDTH, 3),
        )
        self.assertEqual(at_hold_start.dtype, np.uint8)
        np.testing.assert_array_equal(at_hold_start, near_endpoint)
        np.testing.assert_array_equal(at_hold_start, at_endpoint)


if __name__ == "__main__":
    unittest.main()
