"""Real pinned-detector checks; CI explicitly runs these after installing Gitleaks."""

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import public_audit as audit


@unittest.skipUnless(os.environ.get('GITLEAKS_BIN'), 'Set GITLEAKS_BIN for real detector integration')
class GitleaksIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        self.root = self.folder / 'repo'
        self.root.mkdir()
        self.config = self.folder / 'gitleaks.toml'
        self.config.write_text('[extend]\nuseDefault = true\n')
        source = self.root / 'tools/ssml/tokenizer.py'
        source.parent.mkdir(parents=True)
        source.write_text('value = 1\n')
        self.data = {'input_sha256': {'tools/ssml/tokenizer.py': hashlib.sha256(source.read_bytes()).hexdigest()}}
        self.synthetic_key = hashlib.sha256(b'synthetic credential fixture only').hexdigest()
        self.document = self.root / 'reports/review.json'
        self.document.parent.mkdir()
        self.write_document()

    def write_document(self, with_secret=False):
        data = {**self.data, **({'api_key': self.synthetic_key} if with_secret else {})}
        self.document.write_text(json.dumps(data, indent=2) + '\n')

    def scan(self, history=False):
        return audit.scan_secrets(os.environ['GITLEAKS_BIN'], self.root,
                                  self.folder / 'scan.json', self.config, history,
                                  source_root=self.root)

    def test_real_directory_scan_clears_only_verified_hashes(self):
        self.write_document(with_secret=True)
        blocked = self.scan()
        self.assertEqual(blocked['status'], 'findings')
        self.assertEqual(blocked['findings'], 1)
        self.assertEqual(blocked['verified_source_fingerprints'], 1)
        self.assertNotIn(self.synthetic_key, json.dumps(blocked))
        self.write_document()
        clean = self.scan()
        self.assertEqual(clean['status'], 'passed')
        self.assertEqual(clean['raw_findings'], 1)
        self.assertEqual(clean['verified_source_fingerprints'], 1)

    def test_deleted_secret_still_blocks_real_history_scan(self):
        def git(*args):
            subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

        git('init', '-q')
        git('config', 'user.name', 'Synthetic')
        git('config', 'user.email', 'test@users.noreply.github.com')
        for with_secret in (False, True, False):
            self.write_document(with_secret)
            git('add', '.')
            git('commit', '-qm', 'Synthetic fixture')
        summary = self.scan(history=True)
        self.assertEqual(summary['status'], 'findings')
        self.assertEqual(summary['findings'], 1)
        self.assertGreaterEqual(summary['verified_source_fingerprints'], 1)
        self.assertNotIn(self.synthetic_key, json.dumps(summary))

    def test_directory_root_alias_preserves_fingerprint_proof(self):
        alias = self.folder / 'repository-alias'
        alias.symlink_to(self.root, target_is_directory=True)
        self.write_document(with_secret=True)
        summary = audit.scan_secrets(os.environ['GITLEAKS_BIN'], alias,
                                     self.folder / 'scan.json', self.config, source_root=alias)
        self.assertEqual(summary['status'], 'findings')
        self.assertEqual(summary['findings'], 1)
        self.assertEqual(summary['verified_source_fingerprints'], 1)
        self.assertNotIn(self.synthetic_key, json.dumps(summary))


if __name__ == '__main__':
    unittest.main()
