"""Finalize independently scoped regression contracts after the migration.

Historical matrix hashes remain checked. Intentional photo and wording changes
have explicit replacement expectations rather than deleting regression checks.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
LONG = ROOT / "miscellaneous/uqam-baccalaureat-mathematiques-cheminements"
REPORT = ROOT / "reports/uqam_video_revision/2026-09-14"


def replace_once(path, old, new):
    text = path.read_text()
    if old in text:
        path.write_text(text.replace(old, new))
    elif new not in text:
        raise RuntimeError(f"Missing migration contract in {path}: {old[:80]}")


def visual_review_fixes():
    visuals = LONG / 'v4_visuals.py'
    text = visuals.read_text()
    if 'def guide_cover_box()' not in text:
        helper = '''def guide_cover_box() -> tuple[float, float, float, float]:
    """Match the frame and shadow to the source aspect ratio, not an old cover."""
    source = guide_cover()
    factor = min(334 / source.width, 516 / source.height)
    return (88, 116, 88 + source.width * factor, 116 + source.height * factor)


'''
        text = text.replace('def _draw_guide(\n', helper + 'def _draw_guide(\n', 1)
        text = text.replace('    cover_box = (88, 116, 422, 632)', '    cover_box = guide_cover_box()', 1)
        visuals.write_text(text)
    replace_once(LONG / 'voiceover_v4_fr.txt',
                 'La première année est commune aux trois concentrations.',
                 'En première année, les concentrations partagent plusieurs enseignements fondamentaux.')
    builder = ROOT / 'miscellaneous/bac_math_uqam_fr/build_release.py'
    replace_once(builder,
        '        "- Sound: MAI-Voice-2, Canada Central; hook at 0%, main narration at +2%; AAC 48 kHz mono; no music",',
        '''        f"- Sound: MAI-Voice-2, Canada Central; hook at {manifest['configuration']['hook_rate']}, main narration at {manifest['configuration']['narration_rate']}; AAC 48 kHz mono; no music",''')
    # Independent pixel and narration checks preserve the prior source contracts.
    tests = LONG / 'tests/test_render_v4.py'
    text = tests.read_text()
    if 'class RenderedGuideRevisionTests' not in text:
        addition = '''

class RenderedGuideRevisionTests(unittest.TestCase):
    def test_guide_frame_and_shadow_match_the_actual_landscape_source(self) -> None:
        left, top, right, bottom = v4_visuals.guide_cover_box()
        source = v4_visuals.guide_cover()
        self.assertAlmostEqual((right - left) / (bottom - top), source.width / source.height)
        self.assertLess(bottom, 450)
        self.assertLessEqual(right - left, 334)

    def test_old_portrait_shadow_is_absent_in_rendered_pixels(self) -> None:
        render_v4.configure_render_profile("720p30")
        runtime = next(item for item in render_v4.build_runtimes() if item.spec.id == "v4_11_guide")
        frame = render_v4.make_frame(runtime)(14.0)
        expected = np.array(v4_visuals._new_canvas().convert("RGB"))
        self.assertTrue(np.array_equal(frame[600, 200], expected[600, 200]))

    def test_first_year_copy_does_not_claim_identical_concentrations(self) -> None:
        source = (ROOT / "voiceover_v4_fr.txt").read_text()
        self.assertIn("partagent plusieurs enseignements fondamentaux", source)
        self.assertNotIn("La première année est commune aux trois concentrations.", source)
'''
        anchor = 'if __name__ == "__main__":'
        text = text.replace(anchor, addition + '\n\n' + anchor) if anchor in text else text + addition
        tests.write_text(text)
    tests = ROOT / 'tests/test_uqam_promo.py'
    text = tests.read_text()
    if 'def test_build_report_uses_effective_narration_configuration' not in text:
        text += '''

def test_build_report_uses_effective_narration_configuration() -> None:
    manifest = {
        "outputs": {"video": {"path": "review.mp4"}},
        "validation": {
            "media": {"duration_seconds": 80.0},
            "loudness_after": {"integrated_lufs": -18.5, "true_peak_dbfs": -1.3},
            "subtitles": {"caption_count": 25},
        },
        "configuration": {"hook_rate": "-1%", "narration_rate": "-3%"},
        "built_at": "test-fixture", "normalization_applied": False,
    }
    report = release.build_report_text(manifest)
    assert "hook at -1%" in report
    assert "main narration at -3%" in report
    assert "main narration at +2%" not in report
'''
        tests.write_text(text)
    (REPORT / 'visual_review_followup.md').write_text('''# Render inspection follow-up

Evidence: GitHub Actions run 34928345764, tested source bb11f8c47f7efae862d7010d3cb532f117ed2db3. Both suites passed (41 short/new tests, 84 long-version tests, 350 subtests). Complete visual-only encodes and all 15 contact sheets were inspected, with the guide frame also inspected at native 1080p. This is sampled-frame inspection, not a full narrated-film viewing or listening approval.

The guide frame revealed a real defect introduced by the cover update: its shadow still had the previous portrait dimensions. The frame and shadow now use the actual source aspect ratio. Added independent geometry and rendered-pixel regression tests. Also changed the first-year wording to say the concentrations share several fundamental courses, not that the entire first year is identical, and changed the short-film build report to read the effective narration rates from its manifest. These fixes require a new workflow run; the prior evidence is not retroactively a pass for them.

No overlap or clipping was identified in the sampled stable pavilion, mathematics-course, support or conclusion frames. Dissolves contain intentional brief superposition; end-to-end review with actual narration and subtitles remains pending. Real speech synthesis was blocked by absent configured Speech credentials. No institutional approval or publication is inferred.
''')


def main():
    module = LONG / 'program_data_v4.py'
    text = module.read_text()
    anchor = 'from program_data import PROGRAMS as HISTORICAL_PROGRAMS'
    if 'INFO_THEMES as HISTORICAL_INFO_THEMES' not in text:
        text = text.replace(anchor, anchor + '\nfrom program_data import INFO_THEMES as HISTORICAL_INFO_THEMES')
        text += '\n# Shared theme labels are copied, not mutated across renderer versions.\nINFO_THEMES = deepcopy(HISTORICAL_INFO_THEMES)\n'
        module.write_text(text)
    sys.path.insert(0, str(LONG))
    import program_data
    import program_data_v4
    expected = {key: [[c.title for c in s] for s in p['semesters']] for key,p in program_data.PROGRAMS.items()}
    expected['math'][3][3] = 'Équations aux dérivées partielles'
    expected['stat'][1][2] = "Cours d'option"
    expected['stat'][3][3] = 'Algèbre linéaire II'
    actual = {key: [[c.title for c in s] for s in p['semesters']] for key,p in program_data_v4.PROGRAMS.items()}
    if actual != expected:
        raise RuntimeError('V4 changes exceed or contradict the reviewed three-cell diff')
    digest = hashlib.sha256(json.dumps(expected, ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    path = LONG/'tests/test_render_v4.py'
    text = path.read_text()
    text = re.sub(r'(AUDITED_COURSE_TITLE_MATRIX_SHA256 = \(\s*")[a-f0-9]{64}("\s*\))', lambda m:m[1]+digest+m[2], text)
    text = text.replace('test_audited_semester_and_course_title_matrix_is_unchanged', 'test_audited_2026_2027_v4_course_matrix_matches_snapshot')
    if 'def test_historical_course_matrix_remains_unchanged' not in text:
        anchor = 'class CourseMapNamingContractTests(unittest.TestCase):\n'
        addition = '''    def test_historical_course_matrix_remains_unchanged(self) -> None:
        from program_data import PROGRAMS as historical
        matrix = {key: [[course.title for course in semester] for semester in program["semesters"]] for key, program in historical.items()}
        digest = hashlib.sha256(json.dumps(matrix, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        self.assertEqual(digest, "612645771a6cd1f89074ec199fe30597f5a48c188c9c53728ae1bfbf0ed16a72")

'''
        if anchor not in text:
            raise RuntimeError('Missing test-class anchor')
        text = text.replace(anchor, anchor+addition)
    path.write_text(text)
    (REPORT/'course_matrix_snapshot.json').write_text(json.dumps({'historical_sha256':'612645771a6cd1f89074ec199fe30597f5a48c188c9c53728ae1bfbf0ed16a72', 'current_sha256':digest,'change_count':3,'source_year':'2026–2027'},indent=2)+'\n')
    for name in ('bac_math_uqam_fr_scene.py', 'build_release.py'):
        replace_once(ROOT/'miscellaneous/bac_math_uqam_fr'/name,
                     'from promo_beats import NARRATION_BEATS',
                     'from miscellaneous.bac_math_uqam_fr.promo_beats import NARRATION_BEATS')
    replace_once(LONG/'render_v4.py',
        '        if t < v4_photos.end_time(runtime.spec.id, actions):\n            return None  # Includes photographic crossfade; never reuse a stale still.',
        '        photo_end = v4_photos.end_time(runtime.spec.id, actions)\n        if photo_end > 0 and t < photo_end:\n            if t <= photo_end - min(0.5, photo_end / 3):\n                return (-1,)  # Stable photograph before its crossfade.\n            return None  # Crossfade pixels differ on consecutive frames.')
    replace_once(LONG/'tests/test_render_v4.py',
        '        first = frame(0.35)\n        second = frame(0.35 + 1 / 60)',
        '        transition = render_v4.aligned_actions(runtime)["photo_intro"][1] - 0.35\n        first = frame(transition)\n        second = frame(transition + 1 / 60)')
    replace_once(LONG/'tests/test_v4_audio.py',
        '        self.assertIn("ouvrent des portes", conclusion)\n        self.assertIn("construire votre avenir", conclusion)',
        '        self.assertIn("pôle mathématique", conclusion)\n        self.assertIn("préparer votre parcours", conclusion)\n        self.assertIn("baccalauréat en mathématiques", conclusion)')
    visual_review_fixes()
    print('V4_SNAPSHOT',digest)

if __name__ == '__main__':
    main()
