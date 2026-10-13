"""Exercise the exact checksum allowance with the pinned real scanner, offline."""
import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts import public_audit as audit

SCANNER = os.getenv('GITLEAKS_BIN') or shutil.which('gitleaks')
ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(SCANNER, 'Requires the checksum-verified Gitleaks binary')
class PublicChecksumAllowlistTests(unittest.TestCase):
    def test_only_known_checksum_lines_in_known_paths_are_allowed(self):
        # Source-derived fixture; no genuine credential is used or printed.
        metadata = {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in ('tools/ssml/tests/test_tokenizer.py', 'tools/ssml/tokenizer.py')
        }
        rows = [f'{json.dumps(key)}: {json.dumps(value)},' for key, value in metadata.items()]
        synthetic = hashlib.sha256(b'inert positive scanner fixture').hexdigest()
        reviewed = 'reports/course_review/2026-10-10/current/review.json'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            default = root / 'default.toml'
            default.write_text('[extend]\nuseDefault = true\n')
            configured = root / 'configured.toml'
            configured.write_text(audit.PUBLIC_SCAN_CONFIG)

            def scan(case, path, lines, config):
                target = root / case
                file = target / path
                file.parent.mkdir(parents=True)
                file.write_text('\n'.join(lines) + '\n')
                return audit.scan_secrets(SCANNER, target, root / (case + '.json'), config)

            self.assertEqual(scan('baseline', reviewed, rows, default)['findings'], 2)
            self.assertEqual(scan('known', reviewed, rows, configured)['findings'], 0)
            adjacent = scan('adjacent', reviewed, [*rows, f'"api_key": "{synthetic}"'], configured)
            self.assertEqual(adjacent['findings'], 1)
            self.assertEqual(adjacent['rules'], {'generic-api-key': 1})
            self.assertTrue(adjacent['locations'][0].endswith(':3'))
            self.assertEqual(scan('outside', 'reports/unreviewed.json', rows, configured)['findings'], 2)
            self.assertEqual(scan('changed', reviewed,
                [f'"tools/ssml/tokenizer.py": "{synthetic}"'], configured)['findings'], 1)
            swapped = [
                f'{json.dumps(key)}: {json.dumps(value)},'
                for key, value in zip(metadata, reversed(list(metadata.values())), strict=True)
            ]
            self.assertEqual(scan('wrong_pair', reviewed, swapped, configured)['findings'], 2)
            extra = [rows[0] + f' "api_key": "{synthetic}"']
            self.assertGreaterEqual(scan('extra_key_same_line', reviewed, extra, configured)['findings'], 1)
            # Directory scans report absolute paths; suffix scoping intentionally
            # accepts a nested copy, but only these same two exact harmless lines.
            self.assertEqual(scan('nested_known', 'nested/' + reviewed, rows, configured)['findings'], 0)
            self.assertEqual(scan('nested_adjacent', 'nested/' + reviewed,
                [*rows, f'"api_key": "{synthetic}"'], configured)['findings'], 1)


if __name__ == '__main__':
    unittest.main()
