"""Historical reconciliation never manufactures complete playback/listening passes."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.course_evidence import bound_record, ingest_coherence, ingest_narration, overview
from tools.course_review import empty_lesson, sha256


class ProductionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.movie = self.root / 'review_artifacts/lesson.mp4'
        self.movie.parent.mkdir()
        self.movie.write_bytes(b'synthetic identity fixture; not encoded media')
        self.inputs = {'scenes/lesson_scene.py': 'a' * 64, 'tools/shared.py': 'b' * 64}
        self.runtime = {'manim': '0.19.0', 'Pillow': '11.3.0'}
        self.lesson = empty_lesson({'lesson_id': 'lesson', 'order': 1, 'title': 'Synthetic'}, self.inputs)
        self.hash = sha256(self.movie)
        self.status = {'lesson_id': 'lesson', 'input_sha256': self.inputs,
                       'runtime_versions': self.runtime, 'video_sha256': self.hash, 'render': 'passed'}
        self.status_path = self.root / 'review_artifacts/STATUS.json'
        self.status_path.write_text(json.dumps(self.status))
        self.report = self.root / 'coherence.json'
        self.report.write_text(json.dumps({'mode': 'silent_preview', 'lessons': [
            {'lesson_id': 'lesson', 'video_path': 'review_artifacts/lesson.mp4',
             'video_sha256': self.hash, 'origin_status': 'review_artifacts/STATUS.json'}]}))

    def record(self, **changes):
        args = dict(path='review_artifacts/lesson.mp4', expected=self.hash,
                    inputs=self.inputs, runtime=self.runtime, current_runtime=self.runtime)
        return bound_record(self.root, self.lesson, **(args | changes))

    def test_shared_input_runtime_and_movie_replacement_invalidate_freshness(self):
        self.assertEqual(self.record()['state'], 'fresh')
        self.assertEqual(self.record(inputs=self.inputs | {'tools/shared.py': 'c' * 64})['state'], 'stale')
        self.assertEqual(self.record(runtime={'manim': 'different'})['state'], 'stale')
        self.movie.write_bytes(b'replaced')
        self.assertEqual(self.record()['state'], 'stale')
        self.movie.unlink()
        self.assertEqual(self.record()['state'], 'unavailable')

    def test_incomplete_or_missing_runtime_never_becomes_fresh(self):
        for change in ({'inputs': {}}, {'runtime': None}, {'runtime': {'manim': '0.19.0'}},
                       {'current_runtime': {'manim': None}},
                       {'inputs': {'scenes/lesson_scene.py': 'a' * 64}}):
            with self.subTest(change=change):
                self.assertEqual(self.record(**change)['state'], 'unreviewed')
        self.assertEqual(self.record(path='../outside.mp4')['state'], 'unavailable')

    def test_coherence_import_preserves_unreviewed_checks_and_original_identity(self):
        before = copy.deepcopy(self.lesson['checks'])
        ingest_coherence(self.report, {'lesson': self.lesson}, self.root, self.runtime)
        self.assertEqual(self.lesson['checks'], before)
        record = self.lesson['production_context'][0]
        self.assertEqual(record['state'], 'fresh')
        self.assertEqual(record['expected_sha256'], self.hash)
        self.assertEqual(record['report_sha256'], sha256(self.report))
        self.assertEqual(record['coverage'], 'sampled_encoded_frames')
        self.assertEqual(overview(self.lesson)['motion'], 'unreviewed')
        self.assertEqual(overview(self.lesson)['narration'], 'unreviewed')

    def test_origin_disagreement_and_unknown_lesson_are_rejected(self):
        self.status['video_sha256'] = '0' * 64
        self.status_path.write_text(json.dumps(self.status))
        ingest_coherence(self.report, {'lesson': self.lesson}, self.root, self.runtime)
        self.assertEqual(self.lesson['production_context'][0]['state'], 'stale')
        with self.assertRaisesRegex(ValueError, 'Unknown or duplicate'):
            ingest_coherence(self.report, {}, self.root, self.runtime)

    def test_narration_screen_never_counts_as_listening_even_with_matching_bytes(self):
        report = self.root / 'narration.json'
        report.write_text(json.dumps({'existing_audio_analysis': {
            'output_report': 'review_artifacts/lesson.mp4', 'output_report_sha256': self.hash,
            'summary': {'affected_lessons': ['lesson']}}, 'changed_lessons': []}))
        ingest_narration(report, {'lesson': self.lesson}, self.root)
        self.assertEqual(self.lesson['production_context'][0]['state'], 'unreviewed')
        self.assertEqual(self.lesson['checks']['narration']['status'], 'not_checked')
        self.movie.unlink()
        ingest_narration(report, {'lesson': self.lesson}, self.root)
        self.assertEqual(overview(self.lesson)['narration_screen'], 'unavailable')
