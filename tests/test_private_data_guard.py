"""Invented metadata and files only; never copy real billing records into tests."""
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    'private_data_guard', Path(__file__).resolve().parents[1] / 'scripts/check_private_data.py'
)
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)


class PrivateDataGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.PIPE)

    def add(self, name, content='invented fixture\n', force=False):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        self.git('add', *(['-f'] if force else []), '--', name)

    def test_clean_index_passes_without_commits(self):
        self.add('README.md')
        self.assertEqual(guard.check_index(self.root)['status'], 'passed')

    def test_known_billing_paths_block_in_any_case_or_parent(self):
        for name in ('azure_audit.md', 'backup/AZURE_AUDIT.MD', 'reports/azure_billing_history/INDEX.md',
                     'elsewhere/Azure_Billing_History/invoice.csv'):
            with self.subTest(name=name):
                self.assertEqual(guard.path_reason(name), 'personal_billing_report')

    def test_force_added_file_is_detected(self):
        self.add('.gitignore', 'reports/azure_billing_history/\n')
        self.add('reports/azure_billing_history/INDEX.md', force=True)
        self.assertEqual(guard.check_index(self.root)['status'], 'blocked')

    def test_already_tracked_file_not_hidden_by_ignore(self):
        self.add('azure_audit.md')
        self.add('.gitignore', 'azure_audit.md\n')
        self.assertEqual(guard.check_index(self.root)['status'], 'blocked')

    def test_worktree_deletion_not_enough_until_staged(self):
        self.add('azure_audit.md')
        (self.root / 'azure_audit.md').unlink()
        self.assertEqual(guard.check_index(self.root)['status'], 'blocked')
        self.git('add', '-u')
        self.assertEqual(guard.check_index(self.root)['status'], 'passed')

    def test_original_object_cannot_be_reintroduced_by_rename(self):
        self.add('innocent.md', 'synthetic report; not actual personal data\n')
        oid = self.git('hash-object', 'innocent.md').decode().strip()
        report = guard.check_index(self.root, frozenset({oid}))
        self.assertEqual(report['findings'][0]['reason'], 'unchanged_copy_of_private_report')

    def test_untracked_private_local_file_is_not_uploaded_or_read(self):
        (self.root / 'azure_audit.md').write_text('local-only fixture\n')
        self.assertEqual(guard.check_index(self.root)['status'], 'passed')

    def test_templates_and_technical_docs_allowed(self):
        for name in ('.env.example', 'nested/.env.example', 'docs/billing-guide.md',
                     'tests/test_private_data_guard.py', 'SECURITY.md'):
            self.assertIsNone(guard.path_reason(name))

    def test_other_known_private_storage_blocked(self):
        for name in ('.env', '.env.local', 'data/raw/grades.csv', 'private/notes.md', 'credentials.json',
                     'nested/token.json', 'id_ed25519', 'key.pfx', 'archive.sqlite3', 'archive.sqlite-wal'):
            with self.subTest(name=name):
                self.assertIsNotNone(guard.path_reason(name))

    def test_output_contains_no_file_contents(self):
        self.add('azure_audit.md', 'SYNTHETIC_PRIVATE_CONTENT_NEVER_ECHO\n')
        output = io.StringIO()
        with redirect_stdout(output):
            status = guard.main(['--root', str(self.root)])
        self.assertEqual(status, 1)
        self.assertNotIn('SYNTHETIC_PRIVATE_CONTENT_NEVER_ECHO', output.getvalue())
        self.assertFalse(json.loads(output.getvalue())['history_cleaned'])

    def test_non_repo_fails_closed(self):
        with tempfile.TemporaryDirectory() as elsewhere, redirect_stdout(io.StringIO()):
            self.assertEqual(guard.main(['--root', elsewhere]), 2)

    def test_subdirectory_cannot_hide_sibling_files(self):
        self.add('azure_audit.md')
        (self.root / 'nested').mkdir()
        with self.assertRaises(ValueError):
            guard.check_index(self.root / 'nested')

    def test_filename_controls_are_json_escaped(self):
        self.add('private/unusual\nname.txt')
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(guard.main(['--root', str(self.root)]), 1)
        self.assertIn('unusual\\nname', output.getvalue())


if __name__ == '__main__':
    unittest.main()
