"""Review gates must survive stale sources, partial media and parallel authors."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from tools.course_catalog import load_catalog
from tools.course_review import (
    close_finding,
    empty_lesson,
    input_hashes,
    record_check,
    refresh_lesson,
    replace_artifact,
    sha256,
    summarize,
    unresolved_finding,
    validate_coverage,
)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.entry = {'lesson_id': 'example', 'order': 1, 'title': 'Example'}
        self.inputs = {'scenes/example_scene.py': 'source', 'tools/layout.py': 'shared'}
        self.lesson = empty_lesson(self.entry, self.inputs)
        self.artifact = {'video_sha256': 'movie', 'provenance': 'current',
                         'has_audio': True, 'audio_mode': 'azure_review',
                         'dimensions': [1920, 1080]}
        replace_artifact(self.lesson, self.artifact)
        self.review = {'status': 'passed', 'reviewer': 'B', 'checked_at': '2026-10-10',
                       'evidence': ['frames/changed.png'], 'coverage': 'complete',
                       'input_signature': self.lesson['input_signature'],
                       'video_sha256': 'movie', 'method': 'full_playback'}

    def test_catalogue_coverage_has_43_unique_identities(self):
        entries = load_catalog()[1]
        self.assertEqual(len(entries), 43)
        validate_coverage(entries, entries)
        with self.assertRaises(ValueError):
            validate_coverage(entries[:-1], entries)
        with self.assertRaises(ValueError):
            validate_coverage([*entries[:-1], entries[0]], entries)

    def test_scene_or_shared_input_changes_invalidate_checks_and_closures(self):
        for path in self.inputs:
            lesson = copy.deepcopy(self.lesson)
            record_check(lesson, 'motion', self.review, self.artifact)
            lesson['findings'] = [{'id': 'f1', 'status': 'closed'}]
            changed = {**self.inputs, path: 'changed'}
            self.assertTrue(refresh_lesson(lesson, changed))
            self.assertEqual(lesson['checks']['motion']['status'], 'stale')
            self.assertEqual(lesson['findings'][0]['status'], 'awaiting_verification')
            self.assertIsNone(lesson['current_artifact'])

    def test_samples_cannot_pass_full_motion(self):
        for change in ({'coverage': 'samples'}, {'method': 'sampled_frames'}):
            with self.assertRaises(ValueError):
                record_check(self.lesson, 'motion', {**self.review, **change}, self.artifact)

    def test_silent_or_audio_missing_cannot_pass_listening(self):
        for change in ({'has_audio': False}, {'audio_mode': 'silent_preview'}):
            with self.assertRaises(ValueError):
                record_check(self.lesson, 'narration', {**self.review, 'method': 'full_listening'},
                             {**self.artifact, **change})

    def test_incomplete_review_cannot_pass_displayed_mathematics(self):
        with self.assertRaises(ValueError):
            record_check(self.lesson, 'displayed_math', {**self.review, 'coverage': 'source_only'}, self.artifact)

    def test_old_or_other_artifact_cannot_contribute_passes(self):
        with self.assertRaises(ValueError):
            record_check(self.lesson, 'motion', {**self.review, 'video_sha256': 'other'},
                         {**self.artifact, 'video_sha256': 'other'})
        with self.assertRaises(ValueError):
            record_check(self.lesson, 'motion', self.review, {**self.artifact, 'provenance': 'stale'})

    def test_new_narrated_movie_reopens_visual_review(self):
        record_check(self.lesson, 'motion', self.review, self.artifact)
        replace_artifact(self.lesson, {**self.artifact, 'video_sha256': 'replacement'})
        self.assertEqual(self.lesson['checks']['motion']['status'], 'stale')
        self.assertFalse(self.lesson['visual_complete'])

    def test_old_failures_and_blockers_are_also_invalidated_when_inputs_change(self):
        self.lesson['checks']['readability'] = {'status': 'failed', 'reason': 'Old overlap'}
        self.lesson['checks']['narration'] = {'status': 'blocked', 'reason': 'Old silent movie'}
        refresh_lesson(self.lesson, {'scenes/example_scene.py': 'replacement'})
        self.assertEqual(self.lesson['checks']['readability']['status'], 'stale')
        self.assertEqual(self.lesson['checks']['narration']['status'], 'stale')

    def test_closure_requires_independent_reviewer_and_replacement_evidence(self):
        self.lesson['findings'] = [{'id': 'f1', 'fixed_by': 'A', 'status': 'awaiting_verification'}]
        closure = {**self.review, 'acceptance_passed': True}
        for change in ({'reviewer': 'A'}, {'evidence': []}, {'video_sha256': 'old'},
                       {'input_signature': 'old'}, {'acceptance_passed': False}):
            with self.assertRaises(ValueError):
                close_finding(self.lesson, 'f1', {**closure, **change}, self.artifact)
        close_finding(self.lesson, 'f1', closure, self.artifact)
        self.assertEqual(self.lesson['findings'][0]['status'], 'closed')

    def test_uncorrected_finding_or_original_video_cannot_be_closed(self):
        closure = {**self.review, 'acceptance_passed': True}
        for finding in ({'id': 'f1', 'fixed_by': 'A', 'status': 'open'},
                        {'id': 'f1', 'fixed_by': 'A', 'status': 'awaiting_verification',
                         'original_video_sha256': 'movie'}):
            self.lesson['findings'] = [finding]
            with self.assertRaises(ValueError):
                close_finding(self.lesson, 'f1', closure, self.artifact)

    def test_automated_checks_alone_cannot_complete_a_lesson(self):
        record_check(self.lesson, 'source_math', self.review)
        record_check(self.lesson, 'technical', self.review, self.artifact)
        summarize(self.lesson)
        self.assertFalse(self.lesson['visual_complete'])
        self.assertFalse(self.lesson['narrated_complete'])
        self.assertFalse(self.lesson['release_ready'])

    def test_audio_only_blocker_keeps_visual_and_narrated_completion_separate(self):
        from tools.course_review import VISUAL_CHECKS
        for name in VISUAL_CHECKS:
            method = 'display_size_review' if name == 'final_resolution' else self.review['method']
            record_check(self.lesson, name, {**self.review, 'method': method}, self.artifact)
        self.lesson['findings'] = [{'id': 'audio', 'status': 'awaiting_verification',
                                   'affected_checks': ['narration', 'timing']}]
        summarize(self.lesson)
        self.assertTrue(self.lesson['visual_complete'])
        self.assertFalse(self.lesson['narrated_complete'])
        for scope in ({}, {'affected_checks': []}, {'affected_checks': ['misspelled']}):
            self.lesson['findings'] = [{'id': 'unclassified', 'status': 'open', **scope}]
            summarize(self.lesson)
            self.assertFalse(self.lesson['visual_complete'])

    def test_final_resolution_requires_actual_display_size_inspection(self):
        with self.assertRaises(ValueError):
            record_check(self.lesson, 'final_resolution', self.review, self.artifact)
        with self.assertRaises(ValueError):
            record_check(self.lesson, 'final_resolution', {
                **self.review, 'method': 'display_size_review', 'coverage': 'sampled_frames'}, self.artifact)
        record_check(self.lesson, 'final_resolution', {**self.review, 'method': 'display_size_review'}, self.artifact)

    def test_only_explicit_minor_cosmetic_deferral_is_resolved(self):
        allowed = {'status': 'deferred', 'severity': 'minor',
                   'category': 'cosmetic', 'deferred_by': 'owner'}
        for changes in ({'severity': 'major'}, {'deferred_by': None},
                        {'deferred_by': '   '}, {'deferred_by': True},
                        {'deferred_by': {'name': 'owner'}},
                        {'category': None}, {'category': 'mathematics'},
                        {'category': 'runtime'}, {'status': 'open'}):
            with self.subTest(changes=changes):
                self.assertTrue(unresolved_finding({**allowed, **changes}))
        self.assertFalse(unresolved_finding(allowed))

    def test_dependency_closure_and_asset_changes_are_hashed_without_importing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name, source in {'scenes/a/a_scene.py': 'from tools.layout import panel\n',
                                 'tools/layout.py': 'from tools import nested\n',
                                 'tools/nested.py': 'raise RuntimeError("must not execute")\n',
                                 'assets/branding/logo.png': 'image'}.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source)
            before = input_hashes({'scene_file': 'scenes/a/a_scene.py'}, root)
            self.assertIn('tools/nested.py', before)
            (root / 'assets/branding/logo.png').write_text('replacement')
            self.assertNotEqual(before, input_hashes({'scene_file': 'scenes/a/a_scene.py'}, root))

    def test_old_worker_report_cannot_reapprove_changed_data(self):
        from scripts.course_review import ingest_workers
        with tempfile.TemporaryDirectory() as temp:
            source_inputs = {'scenes/example_scene.py': 'source', 'tools/layout.py': 'new-shared'}
            refresh_lesson(self.lesson, source_inputs)
            path = Path(temp) / 'worker.json'
            path.write_text(json.dumps({'worker': 'A', 'lessons': [{
                'lesson_id': 'example', 'source_sha256': 'source',
                'input_sha256': self.inputs, 'source_review': 'passed'}]}))
            # Test the boundary independently of the repository-local report path formatter.
            from unittest.mock import patch
            with patch('scripts.course_review.relative', return_value='worker.json'):
                ingest_workers([path], {'example': self.lesson}, '2026-10-10')
            self.assertEqual(self.lesson['checks']['source_math']['status'], 'stale')

    def test_worker_cannot_close_its_own_finding_through_import(self):
        from unittest.mock import patch

        from scripts.course_review import ingest_workers
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'worker.json'
            path.write_text(json.dumps({'worker': 'A', 'lessons': [{
                'lesson_id': 'example', 'source_sha256': 'source',
                'input_sha256': self.inputs, 'source_review': 'passed',
                'findings': [{'id': 'self-closed', 'status': 'closed'}]}]}))
            with patch('scripts.course_review.relative', return_value='worker.json'):
                with self.assertRaisesRegex(ValueError, 'independent'):
                    ingest_workers([path], {'example': self.lesson}, '2026-10-10')

    def test_worker_source_states_remain_distinct(self):
        from unittest.mock import patch

        from scripts.course_review import ingest_workers
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'worker.json'
            for state in ('not_checked', 'blocked', 'failed', 'stale', 'passed'):
                with self.subTest(state=state):
                    path.write_text(json.dumps({'worker': 'A', 'lessons': [{
                        'lesson_id': 'example', 'source_sha256': 'source',
                        'input_sha256': self.inputs, 'source_review': state}]}))
                    with patch('scripts.course_review.relative', return_value='worker.json'):
                        ingest_workers([path], {'example': self.lesson}, '2026-10-10')
                    self.assertEqual(self.lesson['checks']['source_math']['status'], state)

    def test_same_video_hash_does_not_select_a_stale_artifact_for_closure(self):
        from scripts.course_review import ingest_reviews
        self.lesson['artifacts'] = [{**self.artifact, 'provenance': 'stale'}, self.artifact]
        self.lesson['findings'] = [{'id': 'f1', 'fixed_by': 'A', 'status': 'awaiting_verification'}]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'reviews.json'
            path.write_text(json.dumps({'reviews': [{
                'lesson_id': 'example', 'closures': [{**self.review, 'finding_id': 'f1',
                                                     'acceptance_passed': True}]}]}))
            ingest_reviews([path], {'example': self.lesson})
            self.assertEqual(self.lesson['findings'][0]['status'], 'closed')

    def test_old_review_import_is_retained_as_stale_without_reapproving_replacement(self):
        from scripts.course_review import ingest_reviews
        self.lesson['artifacts'] = [self.artifact]
        self.lesson['findings'] = [{'id': 'f1', 'fixed_by': 'A', 'status': 'awaiting_verification'}]
        old = {**self.review, 'video_sha256': 'old-movie'}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'reviews.json'
            path.write_text(json.dumps({'reviews': [{
                'lesson_id': 'example', 'checks': {'motion': old},
                'closures': [{**old, 'finding_id': 'f1', 'acceptance_passed': True}]}]}))
            for _ in range(2):
                ingest_reviews([path], {'example': self.lesson})
            self.assertEqual(self.lesson['checks']['motion']['status'], 'not_checked')
            self.assertEqual(self.lesson['findings'][0]['status'], 'awaiting_verification')
            self.assertEqual(len(self.lesson['review_history']), 2)
            self.assertTrue(all(r['applicability'] == 'stale' for r in self.lesson['review_history']))


class ArtifactInspectionTests(unittest.TestCase):
    def test_input_output_and_stream_provenance_cannot_be_forged_by_status(self):
        from unittest.mock import patch

        from scripts.course_review import inspect_artifact
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            source = root / 'scene.py'
            helper = root / 'helper.py'
            source.write_text('original source')
            helper.write_text('original dependency')
            folder = root / 'output'
            folder.mkdir()
            movie = folder / 'lesson.mp4'
            movie.write_bytes(b'encoded movie')
            entry = {'scene_file': 'scene.py'}
            inputs = {'scene.py': sha256(source), 'helper.py': sha256(helper)}
            status = {'source_sha256': inputs['scene.py'], 'input_sha256': inputs,
                      'video_sha256': sha256(movie), 'render': 'passed',
                      'quality': 'ql', 'mode': 'silent_preview',
                      'runtime_versions': {'manim': '0.19.0', 'numpy': '2.4.0'}}
            media = {'streams': [{'codec_type': 'video', 'width': 854,
                                   'height': 480, 'r_frame_rate': '15/1'}],
                     'format': {'duration': '10'}}
            with patch('scripts.course_review.ROOT', root), patch(
                    'scripts.course_review.renderer_runtime_versions',
                    return_value=status['runtime_versions'], create=True), patch(
                    'scripts.course_review.subprocess.check_output', return_value=json.dumps(media)):
                def probe(s):
                    return inspect_artifact(folder / 'STATUS.json', s, entry, inputs)
                self.assertEqual(probe(status)['provenance'], 'current')
                incomplete = {**status, 'input_sha256': {'scene.py': inputs['scene.py']}}
                self.assertEqual(probe(incomplete)['provenance'], 'recorded_inputs_match')
                conflicting = {**status, 'source_sha256': 'different-source'}
                self.assertEqual(probe(conflicting)['provenance'], 'conflicting_source_records')
                tampered = {**status, 'video_sha256': 'different-movie'}
                self.assertEqual(probe(tampered)['provenance'], 'output_mismatch')
                upgraded = {**status, 'runtime_versions': {'manim': '99.0', 'numpy': '2.4.0'}}
                self.assertEqual(probe(upgraded)['provenance'], 'runtime_mismatch')
                unknown = {k: v for k, v in status.items() if k != 'runtime_versions'}
                self.assertEqual(probe(unknown)['provenance'], 'runtime_unknown')
                partial = {**status, 'runtime_versions': {'manim': '0.19.0'}}
                self.assertEqual(probe(partial)['provenance'], 'runtime_mismatch')
                with patch('scripts.course_review.renderer_runtime_versions', return_value={'manim': None}):
                    self.assertEqual(probe(status)['provenance'], 'runtime_unavailable')
                helper.write_text('changed dependency')
                self.assertEqual(probe(status)['provenance'], 'stale')
                helper.write_text('original dependency')
                self.assertEqual(probe({**status, 'mode': 'azure_review'})['provenance'], 'failed')


if __name__ == '__main__':
    unittest.main()
