"""Synthetic invariants for the narrow financial-report cleanup."""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('cleanup', Path(__file__).resolve().parents[1] / 'scripts/cleanup_billing_history.py')
c = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(c)


class CleanupTests(unittest.TestCase):
    def test_only_billing_paths_removed(self):
        self.assertTrue(c.private_path('reports/azure_billing_history/INDEX.md'))
        self.assertTrue(c.private_path('Archive/AZURE_AUDIT.MD'))
        self.assertFalse(c.private_path('docs/PRIVATE_DATA_BOUNDARY.md'))
        self.assertFalse(c.private_path('scenes/money_math.py'))

    def test_only_private_blobs_or_paths_filtered(self):
        values = {'scene.py': ('100644','blob','code'), 'renamed.md': ('100644','blob','secret'),
                  'azure_audit.md': ('100644','blob','old-secret')}
        self.assertEqual(c.clean_tree(values, {'secret'}), {'scene.py': values['scene.py']})

    def test_changed_code_is_not_accepted(self):
        old = {'a': {'scene.py': ('100644','blob','good')}}
        new = {'b': {'scene.py': ('100644','blob','different')}}
        with self.assertRaises(ValueError):
            c.verification(old, new, {'a':'b'}, set())

    def test_incomplete_mapping_fails(self):
        with self.assertRaises(ValueError):
            c.verification({'a':{}}, {}, {}, set())

    def test_dropped_commit_fails(self):
        with self.assertRaises(ValueError):
            c.verification({'a':{}}, {}, {'a':'0'*40}, set())

    def test_branch_or_tag_loss_fails(self):
        with self.assertRaises(ValueError):
            c.build_plan({'refs/heads/main':'a', 'refs/tags/v1':'b'}, {'refs/heads/main':'c'})

    def test_pr_refs_are_not_published(self):
        before = {'refs/heads/main':'a','refs/pull/1/head':'b'}
        after = {'refs/heads/main':'c','refs/pull/1/head':'d'}
        self.assertEqual(c.build_plan(before,after), [dict(ref='refs/heads/main',before='a',after='c')])

    def test_changed_remote_ref_stops_publication(self):
        before={'refs/heads/main':'a'}
        with patch.object(c,'remote_refs',return_value={'refs/heads/main':'newer'}), patch.object(c,'run') as call:
            with self.assertRaises(ValueError):
                c.publish(Path('.'),before,[dict(ref='refs/heads/main',before='a',after='b')],c.URL,'a')
            call.assert_not_called()

    def test_push_is_atomic_and_leased(self):
        before={'refs/heads/main':'a'}
        with patch.object(c,'remote_refs',side_effect=[before,{'refs/heads/main':'b'}]), patch.object(c,'run') as call:
            report=c.publish(Path('.'),before,[dict(ref='refs/heads/main',before='a',after='b')],c.URL,'a')
        args=call.call_args.args[0]
        self.assertIn('--atomic',args)
        self.assertIn('--force-with-lease=refs/heads/main:a',args)
        self.assertNotIn('--mirror',args)
        self.assertEqual(report['status'],'published')

    def test_wrong_main_stops_before_network(self):
        with patch.object(c,'remote_refs') as call:
            with self.assertRaises(ValueError):
                c.publish(Path('.'),{'refs/heads/main':'a'},[],c.URL,'wrong')
            call.assert_not_called()

    def test_no_publish_to_another_repository(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                c.trial('https://github.com/example/other.git',Path(root)/'report',True,'a'*40)

    @unittest.skipUnless(shutil.which('git-filter-repo'), 'Full integration runs in CI with pinned git-filter-repo')
    def test_full_synthetic_trial_preserves_code_branch_tag_and_history(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            src=root/'source'
            src.mkdir()
            def git(*args):
                return c.git(src,*args)
            git('init','-b','main')
            git('config','user.name','Synthetic')
            git('config','user.email','fixture@users.noreply.github.com')
            (src/'scene.py').write_text('print("teaching")\n')
            git('add','scene.py')
            git('commit','-m','Fixture code')
            git('branch','preserve-this')
            (src/'azure_audit.md').write_text('Invented private test record; no real data.\n')
            git('add','azure_audit.md')
            git('commit','-m','Fixture private report')
            git('tag','fixture-tag')
            before=git('rev-parse','HEAD')
            report=c.trial(str(src),root/'report')
            self.assertEqual(report['commits_verified'],2)
            self.assertTrue(report['non_billing_tree_preservation'])
            self.assertEqual(report['forbidden_blobs_remaining'],0)
            self.assertEqual(report['publication']['status'],'not_requested')
            self.assertEqual(git('rev-parse','HEAD'),before)
            self.assertTrue((src/'azure_audit.md').is_file())

    def test_clean_mirror_does_not_require_filtering(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            src=root/'source'
            src.mkdir()
            c.git(src,'init','-b','main')
            c.git(src,'config','user.name','Synthetic')
            c.git(src,'config','user.email','fixture@users.noreply.github.com')
            (src/'scene.py').write_text('pass\n')
            c.git(src,'add','scene.py')
            c.git(src,'commit','-m','Fixture')
            report=c.trial(str(src),root/'report')
            self.assertEqual(report['changed_commit_count'],0)
            self.assertEqual(report['writable_ref_updates'],[])


if __name__ == '__main__':
    unittest.main()
