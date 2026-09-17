from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock

import numpy as np
from PIL import Image

from program_data_v4 import INFO_THEMES, PROGRAMS
import render_v4
from theme import CATEGORY_STYLE
import v4_narration
import v4_storyboard_data as storyboard


PATHWAY_LABEL = (
    "Cheminement recommandé — début à l’automne — "
    "5 cours/session"
)
SEMESTER_LABELS = (
    "1re année · Automne",
    "1re année · Hiver",
    "2e année · Automne",
    "2e année · Hiver",
    "3e année · Automne",
    "3e année · Hiver",
)
FORBIDDEN_PHRASE = "Une base largement commune"
AUDITED_COURSE_TITLE_MATRIX_SHA256 = (
    "e6c984551aca1c528cfb16cae31aec1a6cb941fd8d77470a101055bc783480f3"
)


def visible_storyboard_text() -> tuple[str, ...]:
    values: list[str] = [
        storyboard.PATHWAY_LABEL,
        *storyboard.SEMESTER_LABELS,
    ]
    for scene in storyboard.SCENES:
        values.extend((scene.title, scene.subtitle))
    for segments in storyboard.BRANCH_SEGMENTS.values():
        for segment in segments:
            values.extend((segment.heading, segment.description))
            values.extend(course.title for course in segment.courses)
    for narration in v4_narration.NARRATIONS.values():
        values.extend(narration.cues)
    return tuple(values)


class CourseMapNamingContractTests(unittest.TestCase):
    def test_historical_course_matrix_remains_unchanged(self) -> None:
        from program_data import PROGRAMS as historical
        matrix = {key: [[course.title for course in semester] for semester in program["semesters"]] for key, program in historical.items()}
        digest = hashlib.sha256(json.dumps(matrix, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, "612645771a6cd1f89074ec199fe30597f5a48c188c9c53728ae1bfbf0ed16a72")

    def test_all_programs_have_normalized_full_and_short_titles(self) -> None:
        expected = {
            "math": (
                "Concentration mathématiques fondamentales",
                "Concentration mathématiques fondamentales",
            ),
            "stat": ("Concentration statistique", "Concentration statistique"),
            "info_math": (
                "Concentration informatique — profil mathématiques",
                "Concentration informatique",
            ),
            "info_stat": (
                "Concentration informatique — profil statistique",
                "Concentration informatique",
            ),
        }

        self.assertEqual(
            {
                key: (program["title"], program["short_title"])
                for key, program in PROGRAMS.items()
            },
            expected,
        )
        self.assertTrue(
            all(
                program["title"].startswith("Concentration ")
                for program in PROGRAMS.values()
            )
        )

    def test_theme_metadata_uses_valid_programs_and_neutral_category(
        self,
    ) -> None:
        categories = {
            course.category
            for program in PROGRAMS.values()
            for semester in program["semesters"]
            for course in semester
        }

        self.assertNotIn("ethics", categories)
        self.assertNotIn("ethics", CATEGORY_STYLE)
        self.assertIn("context", categories)
        self.assertIn("context", CATEGORY_STYLE)
        self.assertTrue(
            all(theme["program"] in PROGRAMS for theme in INFO_THEMES)
        )
        profiles = next(
            theme for theme in INFO_THEMES if theme["id"] == "profiles"
        )
        self.assertEqual(profiles["program"], "info_math")
        self.assertIn("science des données", profiles["phrase"])
        self.assertNotIn("Science des données", profiles["phrase"])

    def test_audited_2026_2027_v4_course_matrix_matches_snapshot(self) -> None:
        title_matrix = {
            key: [
                [course.title for course in semester]
                for semester in program["semesters"]
            ]
            for key, program in PROGRAMS.items()
        }
        serialized = json.dumps(
            title_matrix,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()

        self.assertEqual(
            sum(
                len(semester)
                for program in PROGRAMS.values()
                for semester in program["semesters"]
            ),
            120,
        )
        self.assertEqual(
            hashlib.sha256(serialized).hexdigest(),
            AUDITED_COURSE_TITLE_MATRIX_SHA256,
        )


class StoryboardContractTests(unittest.TestCase):
    def test_scene_clock_is_contiguous_and_naturally_sized(self) -> None:
        scenes = storyboard.SCENES

        self.assertEqual(len(scenes), 11)
        self.assertEqual(scenes[0].start, 0.0)
        for current, following in zip(scenes, scenes[1:]):
            with self.subTest(scene=current.id):
                self.assertGreater(current.duration, 0.0)
                self.assertEqual(current.end, following.start)
        self.assertGreater(scenes[-1].duration, 0.0)

        authored_total = sum(scene.duration for scene in scenes)
        self.assertEqual(storyboard.TOTAL_DURATION_SECONDS, authored_total)
        self.assertEqual(storyboard.TOTAL_DURATION_SECONDS, scenes[-1].end)
        self.assertEqual(authored_total, 283.0)
        self.assertGreaterEqual(authored_total, 200.0)
        self.assertLessEqual(authored_total, 330.0)

    def test_scene_order_and_cue_contract_agree(self) -> None:
        self.assertEqual(
            tuple(scene.id for scene in storyboard.SCENES),
            v4_narration.EXPECTED_SCENE_IDS,
        )
        for scene in storyboard.SCENES:
            with self.subTest(scene=scene.id):
                self.assertEqual(
                    len(v4_narration.NARRATIONS[scene.id].cues),
                    v4_narration.EXPECTED_CUE_COUNTS[scene.id],
                )

    def test_actions_fit_scenes_and_conclusion_has_a_final_still_hold(self) -> None:
        for scene in storyboard.SCENES:
            active_end = scene.duration - scene.final_still_hold
            for action in scene.actions:
                with self.subTest(scene=scene.id, action=action.action):
                    self.assertGreaterEqual(action.start, 0.0)
                    self.assertGreater(action.end, action.start)
                    self.assertLessEqual(action.end, active_end)
        self.assertEqual(storyboard.SCENES[-1].id, "v4_12_conclusion")
        self.assertGreaterEqual(storyboard.SCENES[-1].final_still_hold, 3.0)
        self.assertEqual(
            storyboard.SCENE_BY_ID["v4_11_guide"].final_still_hold,
            0.0,
        )

    def test_pathway_and_semester_labels_are_explicit_without_a_reading_scene(self) -> None:
        self.assertEqual(storyboard.PATHWAY_LABEL, PATHWAY_LABEL)
        self.assertEqual(storyboard.SEMESTER_LABELS, SEMESTER_LABELS)
        self.assertNotIn(
            "v4_02_reading_the_table",
            storyboard.SCENE_BY_ID,
        )
        self.assertNotIn(
            "v4_02_reading_the_table",
            render_v4.v4_visuals.DRAWERS,
        )
        self.assertNotIn(
            "v4_02_reading_the_table",
            render_v4.SEMANTIC_CUE_ACTIONS,
        )
        visual_source = Path(render_v4.v4_visuals.__file__).read_text(
            encoding="utf-8"
        )
        self.assertNotIn("LECTURE DE LA CARTE", visual_source)

    def test_visible_copy_and_current_artifact_names_are_undated(self) -> None:
        visible = "\n".join(visible_storyboard_text())
        self.assertNotIn("2025–2026", visible)
        self.assertNotIn("2026–2027", visible)
        visual_source = Path(render_v4.v4_visuals.__file__).read_text(
            encoding="utf-8"
        )
        self.assertNotIn("APERÇU DU PROGRAMME · 2025", visual_source)
        self.assertNotIn("Mathématiques et statistique · 2025", visual_source)
        self.assertNotIn("2025-2026", render_v4.ARTIFACT_STEM)

    def test_every_displayed_course_resolves_to_its_audited_semester(self) -> None:
        self.assertEqual(
            set(storyboard.BRANCH_SEGMENTS),
            {
                "v4_06_fundamental_mathematics",
                "v4_07_statistics",
                "v4_08_mathematics_computing",
            },
        )
        for scene_id, segments in storyboard.BRANCH_SEGMENTS.items():
            scene_actions = {
                action.action
                for action in storyboard.SCENE_BY_ID[scene_id].actions
            }
            for segment in segments:
                with self.subTest(scene=scene_id, segment=segment.id):
                    self.assertIn(segment.program_key, PROGRAMS)
                    self.assertIn(segment.action, scene_actions)
                    self.assertTrue(segment.courses)
                semesters = PROGRAMS[segment.program_key]["semesters"]
                for placement in segment.courses:
                    expected = semesters[placement.row][placement.column].title
                    with self.subTest(
                        scene=scene_id,
                        segment=segment.id,
                        row=placement.row,
                        column=placement.column,
                    ):
                        self.assertEqual(placement.title, expected)
                        self.assertEqual(
                            placement.semester_label,
                            SEMESTER_LABELS[placement.row],
                        )

    def test_repetitive_common_base_phrase_is_absent_from_visible_copy(self) -> None:
        folded = "\n".join(visible_storyboard_text()).casefold()
        self.assertNotIn(FORBIDDEN_PHRASE.casefold(), folded)
        self.assertNotIn("math-info", folded)
        self.assertIn("concentration informatique", folded)
        self.assertEqual(
            storyboard.SCENE_BY_ID[
                "v4_05_common_to_specialization"
            ].title,
            "Des enseignements communs à la spécialisation",
        )

    def test_opening_states_the_program_and_three_concentrations_directly(self) -> None:
        opening = storyboard.SCENE_BY_ID["v4_01_opening"]
        self.assertEqual(opening.title, "Baccalauréat en mathématiques")
        self.assertEqual(
            {action.action for action in opening.actions},
            {
                "show_kicker",
                "show_title",
                "show_math_card",
                "show_statistics_card",
                "show_computing_card",
            },
        )
        self.assertFalse(
            {
                "draw_connecting_line",
                "reveal_mathematical_symbols",
                "show_curve",
                "show_dots",
                "show_braces",
            }
            & {action.action for action in opening.actions}
        )


class DomainIllustrationTests(unittest.TestCase):
    def setUp(self) -> None:
        render_v4.configure_render_profile("720p30")

    def tearDown(self) -> None:
        render_v4.configure_render_profile("720p30")

    def test_every_branch_has_exactly_one_domain_illustration(self) -> None:
        expected = {
            (scene_id, segment.id)
            for scene_id, segments in storyboard.BRANCH_SEGMENTS.items()
            for segment in segments
        }
        self.assertEqual(
            set(render_v4.v4_visuals.DOMAIN_ILLUSTRATORS),
            expected,
        )
        self.assertEqual(len(expected), 9)

    def test_professional_examples_are_semantically_valid(self) -> None:
        modulus = render_v4.v4_visuals.ALGEBRA_MODULUS
        expected_table = tuple(
            tuple((row + column) % modulus for column in range(modulus))
            for row in range(modulus)
        )
        self.assertEqual(render_v4.v4_visuals.ALGEBRA_TABLE, expected_table)
        self.assertEqual(
            render_v4.v4_visuals.ALGORITHM_OUTPUT,
            tuple(sorted(render_v4.v4_visuals.ALGORITHM_INPUT)),
        )
        self.assertEqual(
            sorted(render_v4.v4_visuals.ALGORITHM_OUTPUT),
            sorted(render_v4.v4_visuals.ALGORITHM_INPUT),
        )
        self.assertEqual(
            render_v4.v4_visuals.SYSTEM_LAYERS,
            ("APPLICATION", "SERVICE", "DONNÉES"),
        )

    def test_analysis_tangent_is_derived_from_the_displayed_function(self) -> None:
        visuals = render_v4.v4_visuals
        x = visuals.ANALYSIS_TANGENT_X
        self.assertAlmostEqual(
            visuals._analysis_tangent_y(x),
            visuals._analysis_curve_y(x),
            places=9,
        )
        step = 1e-3
        numerical = (
            visuals._analysis_curve_y(x + step)
            - visuals._analysis_curve_y(x - step)
        ) / (2 * step)
        self.assertAlmostEqual(
            numerical,
            visuals._analysis_curve_slope(x),
            places=6,
        )

    def test_conclusion_uses_a_large_unmodified_official_logo(self) -> None:
        render_v4.configure_render_profile("1080p60")
        logo = render_v4.v4_visuals.official_logo()
        self.assertEqual(logo.size, (460, 152))
        rendered_width = round(
            render_v4.v4_visuals.CONCLUSION_LOGO_WIDTH
            * render_v4.v4_visuals.RENDER_SCALE
        )
        self.assertGreaterEqual(rendered_width, 460)
        frame = render_v4.v4_visuals.draw_scene("v4_12_conclusion", 18.0)
        self.assertEqual(frame.shape, (1080, 1920, 3))

    def test_illustrations_stay_inside_right_panel_at_both_sizes(self) -> None:
        logical_box = render_v4.v4_visuals.DOMAIN_ILLUSTRATION_BOX
        self.assertGreaterEqual(logical_box[1], 397)
        self.assertLessEqual(logical_box[3], 536)
        for profile in ("720p30", "1080p60"):
            render_v4.configure_render_profile(profile)
            scale = render_v4.WIDTH / 1280
            bounds = (
                round(logical_box[0] * scale),
                round(logical_box[1] * scale),
                round(logical_box[2] * scale),
                round(logical_box[3] * scale),
            )
            for key in render_v4.v4_visuals.DOMAIN_ILLUSTRATORS:
                with self.subTest(profile=profile, illustration=key):
                    layer = render_v4.v4_visuals._draw_domain_illustration(
                        *key,
                        accent=render_v4.v4_visuals.MATH,
                        pale=render_v4.v4_visuals.PALE_MATH,
                        reveal=1.0,
                    )
                    bbox = layer.getchannel("A").getbbox()
                    self.assertIsNotNone(bbox)
                    assert bbox is not None
                    self.assertGreaterEqual(bbox[0], bounds[0] - 1)
                    self.assertGreaterEqual(bbox[1], bounds[1] - 1)
                    self.assertLessEqual(bbox[2], bounds[2] + 2)
                    self.assertLessEqual(bbox[3], bounds[3] + 2)

    def test_each_illustration_has_real_60fps_reveal_motion(self) -> None:
        render_v4.configure_render_profile("1080p60")
        frame_step = (1 / 60) / 0.55
        for key in render_v4.v4_visuals.DOMAIN_ILLUSTRATORS:
            with self.subTest(illustration=key):
                first = render_v4.v4_visuals._draw_domain_illustration(
                    *key,
                    accent=render_v4.v4_visuals.MATH,
                    pale=render_v4.v4_visuals.PALE_MATH,
                    reveal=0.50,
                )
                second = render_v4.v4_visuals._draw_domain_illustration(
                    *key,
                    accent=render_v4.v4_visuals.MATH,
                    pale=render_v4.v4_visuals.PALE_MATH,
                    reveal=0.50 + frame_step,
                )
                self.assertFalse(
                    np.array_equal(np.asarray(first), np.asarray(second))
                )

    def test_branch_handoffs_never_double_expose_segments(self) -> None:
        for scene_id, segments in storyboard.BRANCH_SEGMENTS.items():
            actions = render_v4.v4_visuals.normalise_actions(scene_id, None)
            names = [segment.action for segment in segments]
            for index in range(1, len(names)):
                window = actions[names[index]]
                for fraction in (0.25, 0.50, 0.75):
                    moment = window.start + fraction * (
                        window.end - window.start
                    )
                    weights = render_v4.v4_visuals._phased_segment_weights(
                        actions,
                        names,
                        moment,
                    )
                    with self.subTest(
                        scene=scene_id,
                        transition=names[index],
                        fraction=fraction,
                    ):
                        self.assertLessEqual(
                            sum(weight > 0 for weight in weights),
                            1,
                        )
                        if fraction < 0.5:
                            self.assertGreater(weights[index - 1], 0)
                            self.assertEqual(weights[index], 0)
                        elif fraction > 0.5:
                            self.assertEqual(weights[index - 1], 0)
                            self.assertGreater(weights[index], 0)
                        else:
                            self.assertEqual(weights[index - 1], 0)
                            self.assertEqual(weights[index], 0)

    def test_branch_hold_is_static_and_uses_frame_cache(self) -> None:
        render_v4.configure_render_profile("1080p60")
        runtime = next(
            item
            for item in render_v4.build_runtimes()
            if item.spec.id == "v4_06_fundamental_mathematics"
        )
        actions = render_v4.aligned_actions(runtime)
        end = actions["show_analysis"][1]
        original = render_v4.v4_visuals.draw_scene
        with mock.patch.object(
            render_v4.v4_visuals,
            "draw_scene",
            wraps=original,
        ) as draw:
            frame = render_v4.make_frame(runtime)
            first = frame(end + 0.20)
            second = frame(end + 0.40)

        self.assertEqual(draw.call_count, 1)
        np.testing.assert_array_equal(first, second)

    def test_computing_illustration_clears_for_profile_transition(self) -> None:
        runtime = next(
            item
            for item in render_v4.build_runtimes()
            if item.spec.id == "v4_08_mathematics_computing"
        )
        actions = render_v4.aligned_actions(runtime)
        transition_start, transition_end = actions["show_profiles_transition"]
        transparent = Image.new(
            "RGBA",
            (render_v4.WIDTH, render_v4.HEIGHT),
            (0, 0, 0, 0),
        )
        before = render_v4.v4_visuals.draw_scene(
            runtime.spec.id,
            transition_start - 0.20,
            runtime.duration,
            actions,
        )
        midpoint = (transition_start + transition_end) / 2
        at_midpoint = render_v4.v4_visuals.draw_scene(
            runtime.spec.id,
            midpoint,
            runtime.duration,
            actions,
        )
        after = render_v4.v4_visuals.draw_scene(
            runtime.spec.id,
            transition_end + 0.20,
            runtime.duration,
            actions,
        )
        with mock.patch.object(
            render_v4.v4_visuals,
            "_draw_domain_illustration",
            return_value=transparent,
        ):
            without_before = render_v4.v4_visuals.draw_scene(
                runtime.spec.id,
                transition_start - 0.20,
                runtime.duration,
                actions,
            )
            without_midpoint = render_v4.v4_visuals.draw_scene(
                runtime.spec.id,
                midpoint,
                runtime.duration,
                actions,
            )
            without_after = render_v4.v4_visuals.draw_scene(
                runtime.spec.id,
                transition_end + 0.20,
                runtime.duration,
                actions,
            )

        self.assertFalse(np.array_equal(before, without_before))
        np.testing.assert_array_equal(at_midpoint, without_midpoint)
        np.testing.assert_array_equal(after, without_after)

    def test_all_native_primitives_route_through_scaled_draw(self) -> None:
        source = Path(render_v4.v4_visuals.__file__).read_text(encoding="utf-8")
        self.assertEqual(source.count("ImageDraw.Draw("), 1)


class RuntimeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.runtimes = render_v4.build_runtimes()

    def test_runtime_clock_and_sentence_cues_match_authored_sources(self) -> None:
        self.assertEqual(
            [runtime.spec.id for runtime in self.runtimes],
            list(v4_narration.EXPECTED_SCENE_IDS),
        )
        self.assertEqual(
            sum(runtime.duration for runtime in self.runtimes),
            storyboard.TOTAL_DURATION_SECONDS,
        )
        self.assertEqual(
            sum(len(runtime.narration.cues) for runtime in self.runtimes),
            v4_narration.TOTAL_CUE_COUNT,
        )

    def test_every_runtime_subtitle_fits_two_short_lines(self) -> None:
        for runtime in self.runtimes:
            for cue in runtime.narration.cues:
                with self.subTest(scene=runtime.spec.id, cue=cue):
                    lines = render_v4.wrap_subtitle(cue)
                    self.assertIn(len(lines), (1, 2))
                    self.assertLessEqual(
                        max(map(len, lines)),
                        v4_narration.SUBTITLE_LINE_WIDTH,
                    )

    def test_uniform_azure_config_pads_each_authored_scene_clock(self) -> None:
        for runtime in self.runtimes:
            config = render_v4.azure_config(runtime)
            with self.subTest(scene=runtime.spec.id):
                self.assertEqual(config.voice, "fr-CA-SylvieNeural")
                self.assertEqual(config.locale, "fr-CA")
                self.assertEqual(config.rate, "-10%")
                self.assertEqual(config.lead_silence_ms, 350)
                self.assertEqual(config.intercue_break_ms, 180)
                self.assertGreaterEqual(config.tail_silence_ms, 800)
                self.assertEqual(config.target_dbfs, -18.5)
                self.assertEqual(
                    config.target_duration_ms,
                    round(runtime.duration * 1000),
                )
                self.assertGreater(
                    config.target_duration_ms,
                    config.lead_silence_ms + config.tail_silence_ms,
                )

    def test_mai_selector_uses_shared_french_narration_profile(self) -> None:
        config = render_v4.azure_config(
            self.runtimes[0],
            voice="MAI-Voice-2",
        )

        self.assertEqual(config.voice, "fr-FR-Soleil:MAI-Voice-2")
        self.assertEqual(config.locale, "fr-FR")
        self.assertEqual(config.rate, "-3%")
        self.assertEqual(
            config.output_format,
            "Audio48Khz192KBitRateMonoMp3",
        )
        self.assertEqual(
            config.timing_mode,
            render_v4.v4_audio.TIMING_MODE_CUE_SEGMENTS,
        )
        self.assertEqual(config.intercue_break_ms, 180)
        self.assertEqual(
            config.target_duration_ms,
            round(self.runtimes[0].duration * 1000),
        )

    def test_scene_selection_keeps_original_index_and_rejects_unknown(self) -> None:
        selected = render_v4.select_runtimes(
            self.runtimes,
            "v4_08_mathematics_computing",
        )
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0][0], 7)
        self.assertIs(selected[0][1], self.runtimes[6])
        with self.assertRaisesRegex(SystemExit, "Unknown scene"):
            render_v4.select_runtimes(self.runtimes, "not_a_scene")

    def test_main_prepares_only_requested_scene(self) -> None:
        requested = "v4_07_statistics"
        with (
            mock.patch.object(
                sys,
                "argv",
                ["render_v4.py", "--scene", requested, "--audio-only"],
            ),
            mock.patch.object(
                render_v4,
                "check_environment",
                return_value={"python": "test"},
            ),
            mock.patch.object(render_v4, "prepare_audio") as prepare,
            mock.patch("sys.stdout", new_callable=io.StringIO),
        ):
            render_v4.main()

        prepare.assert_called_once()
        prepared = list(prepare.call_args.args[0])
        self.assertEqual(
            [runtime.spec.id for runtime in prepared],
            [requested],
        )
        self.assertEqual(prepare.call_args.kwargs["tts"], "existing")


class ArtifactAndOutputTests(unittest.TestCase):
    def test_v4_artifacts_are_isolated_from_v2_and_v3(self) -> None:
        self.assertEqual(
            render_v4.BUILD_DIR.relative_to(render_v4.ROOT),
            Path("build/v4"),
        )
        self.assertEqual(
            render_v4.AUDIO_DIR.relative_to(render_v4.ROOT),
            Path("build/v4/audio"),
        )
        self.assertEqual(
            render_v4.SCENE_DIR.relative_to(render_v4.ROOT),
            Path("build/v4/scenes"),
        )
        self.assertEqual(
            render_v4.DIST_DIR.relative_to(render_v4.ROOT),
            Path("dist/v4"),
        )
        self.assertEqual(
            render_v4.PREVIEW_DIR.relative_to(render_v4.ROOT),
            Path("dist/v4/previews"),
        )
        self.assertTrue(render_v4.ARTIFACT_STEM.endswith("-v4"))

    def test_release_codec_contract_is_h264_aac_yuv420p(self) -> None:
        self.assertEqual(render_v4.WIDTH, 1280)
        self.assertEqual(render_v4.HEIGHT, 720)
        self.assertEqual(render_v4.FPS, 30)
        self.assertEqual(render_v4.V4_RENDER["video_codec"], "libx264")
        self.assertEqual(render_v4.V4_RENDER["audio_codec"], "aac")
        self.assertEqual(render_v4.V4_RENDER["pixel_format"], "yuv420p")

    def test_background_music_mix_is_looped_ducked_and_mono(self) -> None:
        music = render_v4.V4_MUSIC
        self.assertIsNotNone(music)
        self.assertTrue(render_v4.MUSIC_PATH.is_file())
        self.assertEqual(
            render_v4.sha256_file(render_v4.MUSIC_PATH),
            music["sha256"],
        )

        graph = render_v4.background_music_filter()
        self.assertIn("pan=mono", graph)
        self.assertIn("acrossfade=d=4:c1=qsin:c2=qsin", graph)
        self.assertIn("atrim=duration=283", graph)
        self.assertIn("volume=-18dB", graph)
        self.assertIn("sidechaincompress", graph)
        self.assertIn("asplit=2[narration][sidechain]", graph)
        self.assertIn("dropout_transition=0", graph)
        self.assertIn("alimiter=limit=0.841395", graph)

    def test_build_provenance_records_the_shared_selector(self) -> None:
        record = render_v4.artifact_record(render_v4.PROJECT_TTS_PATH)

        self.assertEqual(record["path"], "tools/tts.py")
        self.assertEqual(record["path_base"], "repository_root")
        self.assertEqual(record["sha256"], render_v4.sha256_file(
            render_v4.PROJECT_TTS_PATH
        ))

    def test_conclusion_holds_then_fades_fully_to_background(self) -> None:
        runtime = render_v4.build_runtimes()[-1]
        frame = render_v4.make_frame(runtime)
        hold = runtime.spec.final_still_hold
        at_hold_start = frame(runtime.duration - hold)
        at_fade_start = frame(
            runtime.duration
            - render_v4.FINAL_FADE_SECONDS
            - render_v4.FINAL_BACKGROUND_HOLD_SECONDS
        )
        during_fade = frame(
            runtime.duration
            - render_v4.FINAL_BACKGROUND_HOLD_SECONDS
            - render_v4.FINAL_FADE_SECONDS / 2
        )
        at_background = frame(
            runtime.duration - render_v4.FINAL_BACKGROUND_HOLD_SECONDS
        )
        at_endpoint = frame(runtime.duration)
        expected_background = np.asarray(
            Image.new(
                "RGB",
                (render_v4.WIDTH, render_v4.HEIGHT),
                render_v4.v4_visuals.BACKGROUND,
            ),
            dtype=np.uint8,
        )

        self.assertEqual(
            at_hold_start.shape,
            (render_v4.HEIGHT, render_v4.WIDTH, 3),
        )
        self.assertEqual(at_hold_start.dtype, np.uint8)
        np.testing.assert_array_equal(at_hold_start, at_fade_start)
        self.assertFalse(np.array_equal(at_hold_start, during_fade))
        self.assertFalse(np.array_equal(during_fade, expected_background))
        np.testing.assert_array_equal(at_background, expected_background)
        np.testing.assert_array_equal(at_endpoint, expected_background)


class Native1080p60ProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        render_v4.configure_render_profile("720p30")

    def tearDown(self) -> None:
        render_v4.configure_render_profile("720p30")

    def test_variant_paths_and_native_contract_are_isolated(self) -> None:
        render_v4.configure_render_profile("1080p60")

        self.assertEqual(render_v4.RENDER_PROFILE, "1080p60")
        self.assertEqual((render_v4.WIDTH, render_v4.HEIGHT), (1920, 1080))
        self.assertEqual(render_v4.FPS, 60)
        self.assertEqual(
            render_v4.BUILD_DIR.relative_to(render_v4.ROOT),
            Path("build/v4-1080p60"),
        )
        self.assertEqual(
            render_v4.AUDIO_DIR.relative_to(render_v4.ROOT),
            Path("build/v4/audio"),
        )
        self.assertEqual(
            render_v4.DIST_DIR.relative_to(render_v4.ROOT),
            Path("dist/v4-1080p60"),
        )
        self.assertTrue(render_v4.ARTIFACT_STEM.endswith("-v4-1080p60"))
        self.assertEqual(
            render_v4.BUILD_MANIFEST_NAME,
            "build-manifest-v4-1080p60.json",
        )
        self.assertTrue(render_v4.PROFILE_CONFIG["native_render"])
        self.assertFalse(render_v4.PROFILE_CONFIG["post_scale"])

    def test_artifact_tag_isolates_audio_scenes_and_release_outputs(self) -> None:
        tag = "MAI-Voice-2_20260831_230000_EDT"
        render_v4.configure_render_profile("1080p60", artifact_tag=tag)

        self.assertEqual(
            render_v4.BUILD_DIR.relative_to(render_v4.ROOT),
            Path(f"build/v4-1080p60-{tag}"),
        )
        self.assertEqual(
            render_v4.AUDIO_DIR.relative_to(render_v4.ROOT),
            Path(f"build/v4-{tag}/audio"),
        )
        self.assertEqual(
            render_v4.DIST_DIR.relative_to(render_v4.ROOT),
            Path(f"dist/v4-1080p60-{tag}"),
        )
        self.assertTrue(render_v4.ARTIFACT_STEM.endswith(tag))
        self.assertEqual(
            render_v4.BUILD_MANIFEST_NAME,
            f"build-manifest-v4-1080p60-{tag}.json",
        )

    def test_artifact_tag_rejects_path_syntax(self) -> None:
        with self.assertRaisesRegex(ValueError, "Artifact tag"):
            render_v4.configure_render_profile(
                "1080p60",
                artifact_tag="../replace-master",
            )

    def test_native_frame_is_not_a_resized_720p_frame(self) -> None:
        scene_id = "v4_09_computing_profiles"
        render_v4.configure_render_profile("720p30")
        low = render_v4.v4_visuals.draw_scene(scene_id, 27.0)

        render_v4.configure_render_profile("1080p60")
        high = render_v4.v4_visuals.draw_scene(scene_id, 27.0)
        upscaled = np.asarray(
            Image.fromarray(low).resize(
                (1920, 1080),
                Image.Resampling.LANCZOS,
            )
        )

        self.assertEqual(high.shape, (1080, 1920, 3))
        self.assertEqual(render_v4.v4_visuals.font(32).size, 48)
        self.assertFalse(np.array_equal(high, upscaled))

    def test_60fps_samples_unique_transition_frames(self) -> None:
        render_v4.configure_render_profile("1080p60")
        runtime = render_v4.build_runtimes()[0]
        frame = render_v4.make_frame(runtime)

        transition = render_v4.aligned_actions(runtime)["photo_intro"][1] - 0.35
        first = frame(transition)
        second = frame(transition + 1 / 60)

        self.assertFalse(np.array_equal(first, second))
        self.assertEqual(
            sum(round(item.duration * render_v4.FPS) for item in render_v4.build_runtimes()),
            16_980,
        )

    def test_static_holds_reuse_one_native_frame(self) -> None:
        render_v4.configure_render_profile("1080p60")
        runtime = render_v4.build_runtimes()[0]
        original = render_v4.v4_visuals.draw_scene
        with mock.patch.object(
            render_v4.v4_visuals,
            "draw_scene",
            wraps=original,
        ) as draw:
            frame = render_v4.make_frame(runtime)
            at_start = frame(0.0)
            during_hold = frame(0.1)

        self.assertEqual(draw.call_count, 1)
        np.testing.assert_array_equal(at_start, during_hold)




class RenderedGuideRevisionTests(unittest.TestCase):
    def test_guide_frame_and_shadow_match_the_actual_landscape_source(self) -> None:
        left, top, right, bottom = render_v4.v4_visuals.guide_cover_box()
        source = render_v4.v4_visuals.guide_cover()
        self.assertAlmostEqual((right - left) / (bottom - top), source.width / source.height)
        self.assertLess(bottom, 450)
        self.assertLessEqual(right - left, 334)

    def test_old_portrait_shadow_is_absent_in_rendered_pixels(self) -> None:
        render_v4.configure_render_profile("720p30")
        runtime = next(item for item in render_v4.build_runtimes() if item.spec.id == "v4_11_guide")
        frame = render_v4.make_frame(runtime)(14.0)
        expected = np.array(render_v4.v4_visuals._new_canvas().convert("RGB"))
        self.assertTrue(np.array_equal(frame[600, 200], expected[600, 200]))

    def test_first_year_copy_does_not_claim_identical_concentrations(self) -> None:
        source = (render_v4.ROOT / "voiceover_v4_fr.txt").read_text()
        self.assertIn("partagent plusieurs cours fondamentaux", source)
        self.assertNotIn("La première année est commune aux trois concentrations.", source)


if __name__ == "__main__":
    unittest.main()
