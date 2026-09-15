"""Finalize independently scoped regression snapshots after the guarded migration.

Run before committing the migrated source. The historical hash stays in the
suite; the reviewed three-cell change creates a separately pinned V4 snapshot.
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
    # Explicit audit changes, independently specified rather than inferred from
    # whichever values the new renderer happens to emit.
    expected['math'][3][3] = 'Équations aux dérivées partielles'
    expected['stat'][1][2] = "Cours d'option"
    expected['stat'][3][3] = 'Algèbre linéaire II'
    actual = {key: [[c.title for c in s] for s in p['semesters']] for key,p in program_data_v4.PROGRAMS.items()}
    if actual != expected:
        raise RuntimeError('V4 course-title changes exceed or contradict the reviewed three-cell diff')
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
    print('V4_SNAPSHOT',digest)

if __name__ == '__main__':
    main()
