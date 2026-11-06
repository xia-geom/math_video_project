"""Source-fingerprint exceptions require proof, not a matching filename alone."""

import copy
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import public_audit as audit


class FingerprintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source_name = 'tools/ssml/tokenizer.py'
        self.source = self.root / self.source_name
        self.source.parent.mkdir(parents=True)
        self.source.write_text('value = 1\n')
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.document = self.root / 'reports/review.json'
        self.document.parent.mkdir()
        self.write_document({'input_sha256': {self.source_name: self.digest}})

    def write_document(self, data):
        self.document.write_text(json.dumps(data, indent=2) + '\n')
        line = next(i for i, text in enumerate(self.document.read_text().splitlines(), 1)
                    if self.source_name in text)
        self.finding = {'RuleID': 'generic-api-key', 'File': 'reports/review.json',
                        'StartLine': line, 'EndLine': line}

    def verifier(self, history=False):
        return audit.SourceFingerprints(self.root, history=history)

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args],
                                       stderr=subprocess.DEVNULL).decode().strip()

    def commit(self):
        self.git('add', '.')
        self.git('-c', 'user.name=Synthetic', '-c', 'user.email=test@users.noreply.github.com',
                 'commit', '-qm', 'Synthetic fixture')
        return self.git('rev-parse', 'HEAD')

    def test_valid_provenance_and_absolute_directory_path(self):
        for field in ('inputs', 'input_sha256', 'current_input_sha256'):
            with self.subTest(field=field):
                self.write_document({'lessons': [{'nested': {field: {self.source_name: self.digest}}}]})
                self.assertTrue(self.verifier().verified(self.finding))
                self.assertTrue(self.verifier().verified({**self.finding, 'File': str(self.document)}))

    def test_wrong_value_or_unrecognized_mapping_stays_blocking(self):
        for data in ({'input_sha256': {self.source_name: '0' * 64}},
                     {'credentials': {self.source_name: self.digest}}):
            with self.subTest(data=list(data)):
                self.write_document(data)
                self.assertFalse(self.verifier().verified(self.finding))

    def test_unproven_findings_are_not_suppressed(self):
        for change in ({'RuleID': 'other-provider-key'}, {'StartLine': 999, 'EndLine': 999},
                       {'StartLine': True}, {'EndLine': 99}, {'File': '../reports/review.json'},
                       {'File': '/outside/reports/review.json'}, {'File': 'reports/review.txt'}):
            with self.subTest(change=change):
                self.assertFalse(self.verifier().verified({**self.finding, **change}))
        self.source.unlink()
        self.assertFalse(self.verifier().verified(self.finding))

    def test_changed_source_is_not_a_verified_fingerprint(self):
        self.source.write_text('value = 2\n')
        self.assertFalse(self.verifier().verified(self.finding))

    def test_symlinks_and_symlink_parents_are_not_read(self):
        outside = self.root / 'outside.py'
        outside.write_bytes(self.source.read_bytes())
        self.source.unlink()
        self.source.symlink_to(outside)
        self.assertFalse(self.verifier().verified(self.finding))
        self.source.unlink()
        self.source.parent.rmdir()
        replacement = self.root / 'replacement'
        replacement.mkdir()
        (replacement / 'tokenizer.py').write_bytes(outside.read_bytes())
        self.source.parent.symlink_to(replacement, target_is_directory=True)
        self.assertFalse(self.verifier().verified(self.finding))

    def test_malformed_json_and_extra_line_content_remain_blocking(self):
        self.document.write_text(self.document.read_text() + 'invalid json')
        self.assertFalse(self.verifier().verified(self.finding))
        self.write_document({'input_sha256': {self.source_name: self.digest}})
        text = self.document.read_text().replace('"' + self.digest + '"',
                                                '"' + self.digest + '", "api_key": "synthetic"')
        self.document.write_text(text)
        self.assertFalse(self.verifier().verified(self.finding))

    def test_history_proof_uses_the_finding_commit(self):
        self.git('init', '-q')
        first = self.commit()
        old_finding = {**self.finding, 'Commit': first}
        self.source.write_text('value = 2\n')
        second = self.commit()
        self.assertTrue(self.verifier(history=True).verified(old_finding))
        self.assertFalse(self.verifier(history=True).verified({**old_finding, 'Commit': second}))
        self.assertFalse(self.verifier(history=True).verified({**old_finding, 'Commit': 'HEAD'}))
        self.source.unlink()
        self.source.symlink_to('../../README.md')
        third = self.commit()
        self.assertFalse(self.verifier(history=True).verified({**old_finding, 'Commit': third}))

    def test_summary_keeps_other_findings_and_reports_verification_count(self):
        report = self.root / 'scanner.json'
        secret = {**self.finding, 'RuleID': 'other-provider-key', 'Secret': 'DO_NOT_PRINT'}
        report.write_text(json.dumps([self.finding, secret]))
        result = subprocess.CompletedProcess([], 23, b'DO_NOT_PRINT', b'DO_NOT_PRINT')
        with patch.object(audit.subprocess, 'run', return_value=result):
            summary = audit.scan_secrets('fake', self.root, report, self.root / 'config',
                                         source_root=self.root)
        self.assertEqual(summary['status'], 'findings')
        self.assertEqual(summary['raw_findings'], 2)
        self.assertEqual(summary['verified_source_fingerprints'], 1)
        self.assertEqual(summary['findings'], 1)
        self.assertNotIn('DO_NOT_PRINT', json.dumps(summary))

    def test_surface_scans_do_not_enable_fingerprint_exceptions(self):
        report = self.root / 'scanner.json'
        original = copy.deepcopy(self.finding)
        report.write_text(json.dumps([original]))
        with patch.object(audit.subprocess, 'run', return_value=subprocess.CompletedProcess([], 23)):
            summary = audit.scan_secrets('fake', self.root, report, self.root / 'config')
        self.assertEqual(summary['findings'], 1)
        self.assertEqual(summary['verified_source_fingerprints'], 0)
        self.assertEqual(original, self.finding)


if __name__ == '__main__':
    unittest.main()
