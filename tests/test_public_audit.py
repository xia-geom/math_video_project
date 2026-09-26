"""Offline, synthetic checks for audit redaction and bounded source inspection."""

import importlib.util
import json
import subprocess
import tempfile
import unittest
import urllib.request
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    'public_audit', Path(__file__).resolve().parents[1] / 'scripts/public_audit.py'
)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class PublicAuditTests(unittest.TestCase):
    def test_environment_examples_are_not_secret_files(self):
        self.assertFalse(audit.credential_path('.env.example'))
        self.assertTrue(audit.credential_path('nested/.env.local'))
        self.assertTrue(audit.credential_path('credentials.json'))

    def test_credential_report_never_contains_match_values(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'report.json'
            p.write_text(json.dumps([{'RuleID': 'synthetic-rule', 'File': 'config.py', 'StartLine': 2,
                                      'Secret': 'DO_NOT_PRINT', 'Match': 'DO_NOT_PRINT',
                                      'Email': 'private@example.org'}]))
            result = subprocess.CompletedProcess([], 23, b'DO_NOT_PRINT', b'DO_NOT_PRINT')
            with patch.object(audit.subprocess, 'run', return_value=result):
                summary = audit.scan_secrets('fake', Path(folder), p, Path(folder)/'config')
            self.assertEqual(summary['findings'], 1)
            self.assertNotIn('DO_NOT_PRINT', json.dumps(summary))
            self.assertNotIn('private@', json.dumps(summary))

    def test_scanner_failure_is_not_a_clean_scan(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(audit.subprocess, 'run', return_value=subprocess.CompletedProcess([], 2, b'', b'')):
                value = audit.scan_secrets('fake', Path(folder), Path(folder)/'absent', Path(folder)/'config')
            self.assertEqual(value['status'], 'scanner_error')
            self.assertIsNone(value['findings'])

    def test_history_includes_deleted_file_without_printing_personal_path(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args):
                return subprocess.check_output(['git', '-C', folder, *args], stderr=subprocess.DEVNULL)
            git('init')
            git('config', 'user.name', 'Synthetic')
            git('config', 'user.email', 'test@users.noreply.github.com')
            (root / '.env').write_text('placeholder=true\n')
            (root / 'notes.txt').write_text('/Users/synthetic-person/private-note.txt\n')
            git('add', '.')
            git('commit', '-m', 'Initial fixture')
            git('rm', '.env')
            git('commit', '-m', 'Remove fixture')
            summary = audit.history_inventory(root)
            self.assertEqual(summary['commits'], 2)
            self.assertIn('.env', summary['credential_like_historical_paths'])
            self.assertIn('notes.txt', summary['personal_local_path_files'])
            self.assertNotIn('synthetic-person', json.dumps(summary))

    def test_redirect_does_not_leak_github_authorization(self):
        req = urllib.request.Request('https://api.github.com/resource', headers={'Authorization': 'Bearer synthetic'})
        redirect = audit.SafeRedirect().redirect_request(req, None, 302, 'redirect', {}, 'https://example.org/log')
        self.assertIsNone(redirect.get_header('Authorization'))
        with self.assertRaises(ValueError):
            audit.SafeRedirect().redirect_request(req, None, 302, 'redirect', {}, 'http://example.org/log')

    def test_rejects_invalid_repo_before_network(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                audit.github_surface('../wrong', Path(folder)/'surface', '')


if __name__ == '__main__':
    unittest.main()
