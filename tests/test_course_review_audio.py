"""Regression proposal for silent/sample audio finding closure bypass."""
import copy
import unittest

from tools.course_review import (
    AUDIO_CHECKS,
    affected_checks,
    close_finding,
    empty_lesson,
    record_check,
    replace_artifact,
    revalidate_audio_closures,
)


class AudioFindingClosureTests(unittest.TestCase):
    def setUp(self):
        self.lesson = empty_lesson({'lesson_id': 'example', 'order': 1, 'title': 'Example'},
                                   {'scenes/example_scene.py': 'current-source'})
        self.artifact = {'video_sha256': 'replacement', 'provenance': 'current',
                         'has_audio': True, 'audio_mode': 'azure_review', 'dimensions': [1920, 1080]}
        replace_artifact(self.lesson, self.artifact)
        self.lesson['artifacts'] = [self.artifact]
        self.finding = {'id': 'audio', 'status': 'awaiting_verification', 'fixed_by': 'A',
                        'affected_checks': ['narration', 'timing'],
                        'original_video_sha256': 'defective-original'}
        self.lesson['findings'] = [self.finding]
        self.proof = {'reviewer': 'B', 'checked_at': '2026-10-11', 'evidence': ['affected-frame.png'],
                      'input_signature': self.lesson['input_signature'], 'video_sha256': 'replacement',
                      'method': 'sampled_frames', 'coverage': 'samples', 'acceptance_passed': True}

    def add_audio_checks(self, lesson=None, changes=None):
        lesson = lesson or self.lesson
        for name in AUDIO_CHECKS:
            lesson['checks'][name] = {**self.proof, 'status': 'passed',
                                      'method': 'full_listening' if name == 'narration' else 'full_av_review',
                                      'coverage': 'complete', 'evidence': ['dated-listening-log.md'],
                                      **(changes or {})}

    def test_audio_findings_cannot_close_from_samples_on_silent_or_narrated_artifact(self):
        for audio in (True, False):
            with self.subTest(audio=audio):
                artifact = {**self.artifact, 'has_audio': audio,
                            'audio_mode': 'azure_review' if audio else 'silent_preview'}
                with self.assertRaises(ValueError):
                    close_finding(self.lesson, 'audio', self.proof, artifact)
        self.assertEqual(self.finding['status'], 'awaiting_verification')

    def test_silent_media_rejected_even_when_persisted_audio_checks_claim_pass(self):
        self.add_audio_checks()
        for change in ({'has_audio': False}, {'audio_mode': 'silent_preview'}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                close_finding(self.lesson, 'audio', self.proof, {**self.artifact, **change})

    def test_audio_proxies_incomplete_stale_and_fixer_checks_rejected(self):
        for change in ({'method': 'sampled_frames'}, {'method': 'transcript_review'},
                       {'method': 'player_ended'}, {'method': 'full_playback'},
                       {'coverage': 'samples'}, {'reviewer': 'A'}, {'reviewer': ''},
                       {'evidence': []}, {'checked_at': ''}, {'input_signature': 'old'},
                       {'video_sha256': 'old'}, {'status': 'not_checked'}):
            with self.subTest(change=change):
                lesson = copy.deepcopy(self.lesson)
                self.add_audio_checks(lesson, change)
                with self.assertRaises(ValueError):
                    close_finding(lesson, 'audio', self.proof, self.artifact)
                self.assertEqual(lesson['findings'][0]['status'], 'awaiting_verification')

    def test_audio_requirements_follow_each_explicit_scope(self):
        for name in AUDIO_CHECKS:
            with self.subTest(name=name):
                lesson = copy.deepcopy(self.lesson)
                lesson['findings'][0]['affected_checks'] = [name]
                self.add_audio_checks(lesson)
                other = next(value for value in AUDIO_CHECKS if value != name)
                lesson['checks'][other] = {'status': 'not_checked'}
                close_finding(lesson, 'audio', self.proof, self.artifact)
                self.assertEqual(lesson['findings'][0]['status'], 'closed')

    def test_genuine_current_independent_audio_checks_allow_mixed_closure(self):
        self.finding['affected_checks'] += ['displayed_math', 'readability']
        for name in AUDIO_CHECKS:
            review = {**self.proof, 'status': 'passed', 'coverage': 'complete',
                      'method': 'full_listening' if name == 'narration' else 'full_av_review',
                      'evidence': ['actual-listening-log.md']}
            record_check(self.lesson, name, review, self.artifact)
        close_finding(self.lesson, 'audio', self.proof, self.artifact)
        self.assertEqual(self.finding['status'], 'closed')
        self.assertEqual(self.finding['verification']['coverage'], 'samples')
        self.assertEqual(self.lesson['checks']['motion']['status'], 'not_checked')
        self.assertFalse(self.lesson['narrated_complete'])

    def test_narrow_visual_closure_does_not_invent_listening_or_whole_playback(self):
        self.finding['affected_checks'] = ['readability', 'motion']
        silent = {**self.artifact, 'has_audio': False, 'audio_mode': 'silent_preview'}
        close_finding(self.lesson, 'audio', self.proof, silent)
        self.assertEqual(self.finding['status'], 'closed')
        self.assertTrue(all(self.lesson['checks'][name]['status'] == 'not_checked'
                            for name in ('motion', 'narration', 'timing')))

    def test_unknown_and_malformed_scopes_are_conservative_including_unhashable_values(self):
        for value in (None, [], 'readability', ['misspelled'], [['readability']], [{}], [True]):
            with self.subTest(value=value):
                self.finding['affected_checks'] = value
                self.assertTrue(set(AUDIO_CHECKS) <= affected_checks(self.finding))
                with self.assertRaises(ValueError):
                    close_finding(self.lesson, 'audio', self.proof, self.artifact)
        self.finding.pop('affected_checks')
        with self.assertRaises(ValueError):
            close_finding(self.lesson, 'audio', self.proof, self.artifact)

    def test_persisted_pregate_audio_closure_reopens_and_retains_original_proof(self):
        self.finding.update(status='closed', verification=copy.deepcopy(self.proof))
        revalidate_audio_closures(self.lesson)
        self.assertEqual(self.finding['status'], 'awaiting_verification')
        self.assertEqual(self.finding['verification'], self.proof)
        self.assertIn('review', self.finding['closure_blocked_reason'])

    def test_persisted_visual_closure_survives_without_fake_whole_checks(self):
        self.finding.update(status='closed', affected_checks=['readability'],
                            verification=copy.deepcopy(self.proof))
        revalidate_audio_closures(self.lesson)
        self.assertEqual(self.finding['status'], 'closed')
        self.assertEqual(self.finding['verification'], self.proof)

    def test_scope_expansion_reopens_sigma_style_visual_closure(self):
        self.finding['affected_checks'] = ['displayed_math', 'readability', 'motion']
        close_finding(self.lesson, 'audio', self.proof, self.artifact)
        self.finding['affected_checks'] += ['narration', 'timing']
        revalidate_audio_closures(self.lesson)
        self.assertEqual(self.finding['status'], 'awaiting_verification')
        self.assertEqual(self.finding['verification'], self.proof)

    def test_audio_closure_remains_closed_when_current_independent_audio_checks_exist(self):
        self.add_audio_checks()
        close_finding(self.lesson, 'audio', self.proof, self.artifact)
        revalidate_audio_closures(self.lesson)
        self.assertEqual(self.finding['status'], 'closed')

    def test_revalidation_rejects_disappeared_or_stale_artifact(self):
        self.add_audio_checks()
        close_finding(self.lesson, 'audio', self.proof, self.artifact)
        self.lesson['artifacts'] = [{**self.artifact, 'provenance': 'stale'}]
        revalidate_audio_closures(self.lesson)
        self.assertEqual(self.finding['status'], 'awaiting_verification')
