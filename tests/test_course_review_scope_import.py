"""Dated classifications preserve evidence without granting listening approval."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.course_review import ingest_reviews, ingest_workers
from tools.course_catalog import ROOT
from tools.course_review import empty_lesson, finding_definition_signature, replace_artifact


class ScopeImportTests(unittest.TestCase):
    def setUp(self):
        self.inputs = {'scenes/example_scene.py': 'source'}
        self.lesson = empty_lesson({'lesson_id': 'example', 'order': 1, 'title': 'Example'}, self.inputs)
        self.artifact = {'video_sha256': 'current', 'provenance': 'current',
                         'has_audio': False, 'audio_mode': 'silent_preview'}
        replace_artifact(self.lesson, self.artifact)
        self.lesson['artifacts'] = [self.artifact]
        self.finding = {'id': 'f1', 'fixed_by': 'A', 'status': 'awaiting_verification',
                        'description': 'A corrected label', 'closure_condition': 'Inspect its replacement.'}
        self.lesson['findings'] = [self.finding]
        self.proof = {'finding_id': 'f1', 'reviewer': 'B', 'checked_at': '2026-10-10',
                      'evidence': ['actual-frame.png'], 'input_signature': self.lesson['input_signature'],
                      'video_sha256': 'current', 'acceptance_passed': True,
                      'coverage': 'samples', 'method': 'sampled_frames'}
        self.scope = {'finding_id': 'f1', 'reviewer': 'C', 'checked_at': '2026-10-11',
                      'evidence': ['worker.json'], 'rationale': 'Only label clearance was corrected.',
                      'finding_definition_sha256': finding_definition_signature(self.finding),
                      'affected_checks': ['readability', 'motion']}

    @staticmethod
    def write(path, row):
        path.write_text(json.dumps({'reviews': [{'lesson_id': 'example', **row}]}))
        return path

    def test_scope_classification_precedes_closure_in_either_argument_order(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            scopes = self.write(folder / 'scopes.json', {'finding_scopes': [self.scope]})
            closures = self.write(folder / 'closures.json', {'closures': [self.proof]})
            for paths in ([closures, scopes], [scopes, closures]):
                with self.subTest(paths=[p.name for p in paths]):
                    lesson = copy.deepcopy(self.lesson)
                    ingest_reviews(paths, {'example': lesson})
                    finding = lesson['findings'][0]
                    self.assertEqual(finding['status'], 'closed')
                    self.assertEqual(finding['verification'], self.proof)
                    self.assertEqual(finding['scope_review'], self.scope)
                    self.assertTrue(all(c['status'] == 'not_checked' for c in lesson['checks'].values()))
                    self.assertFalse(lesson['visual_complete'])
                    self.assertFalse(lesson['narrated_complete'])

    def test_invalid_definition_or_scope_narrowing_cannot_change_existing_requirement(self):
        for invalid in ({**self.scope, 'finding_definition_sha256': 'wrong'}, self.scope):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as temp:
                lesson = copy.deepcopy(self.lesson)
                lesson['findings'][0]['affected_checks'] = ['readability', 'narration', 'timing']
                before = copy.deepcopy(lesson['findings'][0])
                path = self.write(Path(temp) / 'scopes.json', {'finding_scopes': [invalid]})
                with self.assertRaises(ValueError):
                    ingest_reviews([path], {'example': lesson})
                self.assertEqual(lesson['findings'][0], before)

    def test_insufficient_historical_audio_closure_is_retained_rejected_without_crash(self):
        self.finding['affected_checks'] = ['readability']
        expanded = {**self.scope, 'affected_checks': ['readability', 'narration', 'timing']}
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            closure = self.write(folder / 'closure.json', {'closures': [self.proof]})
            scope = self.write(folder / 'scope.json', {'finding_scopes': [expanded]})
            for _ in range(2):
                ingest_reviews([closure, scope], {'example': self.lesson})
            self.assertEqual(self.finding['status'], 'awaiting_verification')
            history = [item for item in self.lesson['review_history'] if item['kind'] == 'closure']
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0]['review'], self.proof)
            self.assertEqual(history[0]['acceptance'], 'rejected')
            self.assertIn('completed', history[0]['reason'])
            self.assertEqual(self.lesson['checks']['narration']['status'], 'not_checked')

    def test_persisted_scope_survives_same_worker_report_reimport_without_overlay_argument(self):
        original = copy.deepcopy(self.finding)
        original['affected_checks'] = ['readability']
        self.lesson['findings'] = [copy.deepcopy(original)]
        expanded = {**self.scope, 'affected_checks': ['readability', 'narration', 'timing']}
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            scope = self.write(folder / 'scope.json', {'finding_scopes': [expanded]})
            ingest_reviews([scope], {'example': self.lesson})
            worker = folder / 'worker.json'
            worker.write_text(json.dumps({'worker': 'A', 'checked_at': '2026-10-10', 'lessons': [{
                'lesson_id': 'example', 'source_sha256': 'source', 'input_sha256': self.inputs,
                'source_review': 'passed', 'findings': [original]}]}))
            for _ in range(2):
                with patch('scripts.course_review.relative', return_value='worker.json'):
                    ingest_workers([worker], {'example': self.lesson}, '2026-10-11')
                ingest_reviews([], {'example': self.lesson})
                finding = self.lesson['findings'][0]
                self.assertEqual(finding['affected_checks'], expanded['affected_checks'])
                self.assertEqual(finding['scope_review'], expanded)
                self.assertEqual(finding['status'], 'awaiting_verification')

    def test_real_dated_scopes_preserve_all_83_proofs_and_zero_complete_lessons(self):
        historical = ROOT / 'reports/course_review/2026-10-10'
        scope_path = ROOT / 'reports/course_review/2026-10-11/finding_scopes.json'
        ledger = json.loads((historical / 'current/review.json').read_text())
        lessons = {lesson['lesson_id']: lesson for lesson in ledger['lessons']}
        scope_rows = json.loads(scope_path.read_text())['reviews']
        self.assertEqual(sum(len(row['finding_scopes']) for row in scope_rows), 15)
        before = {(key, finding['id']): copy.deepcopy(finding['verification'])
                  for key, lesson in lessons.items() for finding in lesson['findings']
                  if finding['status'] == 'closed'}
        self.assertEqual(len(before), 83)
        # Reimport actual historical proofs, with the classification file last.
        ingest_reviews([*(historical / f'reviews_{worker}.json' for worker in 'abc'), scope_path], lessons)
        after = {(key, finding['id']): finding['verification']
                 for key, lesson in lessons.items() for finding in lesson['findings']
                 if finding['status'] == 'closed'}
        self.assertEqual(after, before)
        self.assertEqual(len(lessons), 43)
        self.assertFalse(any(lesson['visual_complete'] for lesson in lessons.values()))
        self.assertFalse(any(lesson['narrated_complete'] for lesson in lessons.values()))
        sigma = next(f for f in lessons['notation_sigma']['findings'] if f['id'] == 'C-37-SIGMA-TARGETS')
        self.assertEqual(sigma['status'], 'awaiting_verification')
        self.assertTrue({'narration', 'timing'} <= set(sigma['affected_checks']))

    def test_current_audio_checks_precede_closures_regardless_of_argument_order(self):
        fixture = self
        fixture.artifact.update(has_audio=True, audio_mode='azure_review')
        fixture.finding['affected_checks'] = ['narration', 'timing']
        checks = {name: {**fixture.proof, 'status': 'passed', 'coverage': 'complete',
                         'evidence': ['actual-listening-log.md'], 'method': method}
                  for name, method in [('narration', 'full_listening'), ('timing', 'full_av_review')]}
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            audio = fixture.write(folder / 'audio.json', {'checks': checks})
            closure = fixture.write(folder / 'closure.json', {'closures': [fixture.proof]})
            for paths in ([closure, audio], [audio, closure]):
                with self.subTest(paths=[p.name for p in paths]):
                    lesson = copy.deepcopy(fixture.lesson)
                    ingest_reviews(paths, {'example': lesson})
                    self.assertEqual(lesson['findings'][0]['status'], 'closed')
                    self.assertEqual(lesson['findings'][0]['verification'], fixture.proof)
