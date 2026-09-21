"""Offline checks for pre-push prevention, content matching and owner handoff."""
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


h = load('check_private_history')
a = load('cleanup_exposed_artifacts')
o = load('enable_safety_settings')
SYNTHETIC = (
    'Synthetic invoice record, created only for a test: this fictional project spent CAD 123.45 for an invented test period.\n'
    'Synthetic credit record, created only for a test: this fictional project received CAD 67.89 for an invented test period.\n'
).encode()


def archive(name, body):
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(name, body)
    return out.getvalue()


class SafetyFinishTests(unittest.TestCase):
    def test_source_fingerprints_are_not_plaintext(self):
        whole, lines = a.signatures([SYNTHETIC])
        self.assertTrue(all(len(x) == 64 for x in whole | lines))
        self.assertNotIn('123.45', str(whole | lines))

    def test_two_exact_known_lines_needed_for_partial_match(self):
        whole, lines = a.signatures([SYNTHETIC])
        self.assertFalse(a.matches(SYNTHETIC.splitlines()[0], whole, lines))
        self.assertTrue(a.matches(b'Other log text\n' + SYNTHETIC, whole, lines))

    def test_timestamps_do_not_hide_logged_copy(self):
        whole, lines = a.signatures([SYNTHETIC])
        log = b'\n'.join(b'2026-09-21T00:00:00Z ' + line for line in SYNTHETIC.splitlines())
        self.assertTrue(a.matches(log, whole, lines))

    def test_nested_source_archive_inspected_without_extracting(self):
        whole, lines = a.signatures([SYNTHETIC])
        raw = archive('source.zip', archive('renamed.md', SYNTHETIC))
        result = a.inspect_zip(raw, whole, lines)
        self.assertTrue(result['match'])
        self.assertEqual(result['text_members_scanned'], 1)

    def test_private_name_alone_does_not_delete_fixture(self):
        whole, lines = a.signatures([SYNTHETIC])
        result = a.inspect_zip(archive('azure_audit.md', b'Harmless invented placeholder'), whole, lines)
        self.assertFalse(result['match'])

    def test_binary_members_not_claimed_scanned(self):
        whole, lines = a.signatures([SYNTHETIC])
        result = a.inspect_zip(archive('clip.mp4', b'demo'), whole, lines)
        self.assertEqual(result['members_not_scanned'], 1)
        self.assertEqual(result['text_members_scanned'], 0)

    def test_wrong_repository_api_refused(self):
        with self.assertRaises(ValueError):
            a.gh('repos/someone/else/actions/artifacts')

    def test_owner_settings_preview_makes_no_api_call(self):
        with patch.object(o, 'api') as call, patch('builtins.print'):
            self.assertEqual(o.main([]), 0)
        call.assert_not_called()

    def test_missing_admin_stops_before_mutations(self):
        with patch.object(o, 'api', return_value={'permissions': {'admin': False}}) as call, patch('builtins.print'):
            self.assertEqual(o.main(['--apply']), 2)
        self.assertEqual(len(call.call_args_list), 1)
        self.assertEqual(call.call_args.args[0], 'GET')

    def test_ruleset_preserves_single_maintainer_and_forbids_bypass(self):
        spec = json.loads((ROOT/'.github/rulesets/private-data-safety.json').read_text())
        self.assertEqual(spec['bypass_actors'], [])
        self.assertEqual(spec['conditions']['ref_name']['include'], ['refs/heads/main'])
        types = {rule['type'] for rule in spec['rules']}
        self.assertTrue({'deletion','non_fast_forward','pull_request','required_status_checks'} <= types)

    def test_pre_push_sees_file_even_after_later_removal(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args):
                return subprocess.check_output(['git','-C',str(root),*args],stderr=subprocess.DEVNULL)
            git('init','-b','main')
            git('config','user.name','Synthetic')
            git('config','user.email','fixture@users.noreply.github.com')
            (root/'scene.py').write_text('pass\n')
            git('add','scene.py')
            git('commit','-m','Fixture')
            self.assertEqual(h.check(root,['HEAD'])['status'],'passed')
            (root/'azure_audit.md').write_text('A synthetic private fixture.\n')
            git('add','azure_audit.md')
            git('commit','-m','Fixture report')
            git('rm','azure_audit.md')
            git('commit','-m','Remove fixture')
            result = h.check(root,['HEAD'])
            self.assertEqual(result['status'],'blocked')
            self.assertNotIn('A synthetic',str(result))


if __name__ == '__main__':
    unittest.main()
