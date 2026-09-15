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

    # Support both direct execution and importlib loading from repository root.
    for name in ('bac_math_uqam_fr_scene.py', 'build_release.py'):
        replace_once(ROOT/'miscellaneous/bac_math_uqam_fr'/name,
                     'from promo_beats import NARRATION_BEATS',
                     'from miscellaneous.bac_math_uqam_fr.promo_beats import NARRATION_BEATS')

    # A static photographic hold SHOULD be cached; its crossfade MUST NOT be.
    replace_once(LONG/'render_v4.py',
        '        if t < v4_photos.end_time(runtime.spec.id, actions):\n            return None  # Includes photographic crossfade; never reuse a stale still.',
        '        photo_end = v4_photos.end_time(runtime.spec.id, actions)\n        if photo_end > 0 and t < photo_end:\n            if t <= photo_end - min(0.5, photo_end / 3):\n                return (-1,)  # Stable photograph before its crossfade.\n            return None  # Crossfade pixels differ on consecutive frames.')
    replace_once(LONG/'tests/test_render_v4.py',
        '        first = frame(0.35)\n        second = frame(0.35 + 1 / 60)',
        '        transition = render_v4.aligned_actions(runtime)["photo_intro"][1] - 0.35\n        first = frame(transition)\n        second = frame(transition + 1 / 60)')
    replace_once(LONG/'tests/test_v4_audio.py',
        '        self.assertIn("ouvrent des portes", conclusion)\n        self.assertIn("construire votre avenir", conclusion)',
        '        self.assertIn("pôle mathématique", conclusion)\n        self.assertIn("préparer votre parcours", conclusion)\n        self.assertIn("baccalauréat en mathématiques", conclusion)')

    # Native-size evidence complements the complete 720p review encodes.
    review = ROOT/'scripts/uqam_revision/render_review.py'
    text = review.read_text()
    if 'native_v4_frames' not in text:
        anchor = '    long_review()\n    short_review()'
        replacement = '''    long_review()
    native = OUT / "native_v4_frames"
    native.mkdir(exist_ok=True)
    v4.configure_render_profile("1080p60", artifact_tag="ci-native-review")
    for runtime in v4.build_runtimes():
        for index, time in enumerate((0.5, runtime.duration / 2, runtime.duration - 0.5)):
            pixels = v4.make_frame(runtime)(time)
            assert pixels.shape == (1080, 1920, 3)
            Image.fromarray(pixels).save(native / f"{runtime.spec.id}_{index}.jpg", quality=92)
    v4.configure_render_profile("720p30", artifact_tag="ci-review")
    short_review()'''
        if anchor not in text:
            raise RuntimeError('Review sequence anchor missing')
        review.write_text(text.replace(anchor,replacement))
    print('V4_SNAPSHOT',digest)

if __name__ == '__main__':
    main()
