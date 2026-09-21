"""Checks for the five workflows hardened here, not all repository administration."""

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FILES = ('smoke.yml', 'public-audit.yml', 'teaching-revision.yml',
         'uqam-revision.yml', 'uqam-ouvertures.yml')
MANUAL_MAIN = "github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main'"


def read_workflow(name):
    # BaseLoader keeps GitHub's `on` key a string instead of YAML 1.1 boolean True.
    return yaml.load((ROOT / '.github/workflows' / name).read_text(), Loader=yaml.BaseLoader)


class PublicWorkflowPolicyTests(unittest.TestCase):
    def test_five_workflows_are_read_only_on_pull_requests(self):
        for name in FILES:
            with self.subTest(name=name):
                d = read_workflow(name)
                self.assertIn('pull_request', d['on'])
                self.assertNotIn('pull_request_target', d['on'])
                self.assertEqual(d['permissions']['contents'], 'read')
                self.assertTrue(all(v == 'read' for v in d['permissions'].values()))
                for job in d['jobs'].values():
                    self.assertTrue(all(v in ('read', 'none') for v in job.get('permissions', {}).values()))

    def test_actions_are_pinned_and_checkout_retains_no_credentials(self):
        for name in FILES:
            for job in read_workflow(name)['jobs'].values():
                self.assertGreater(int(job['timeout-minutes']), 0)
                for step in job['steps']:
                    if 'uses' in step:
                        self.assertRegex(step['uses'], r'^[\w./-]+@[0-9a-f]{40}$')
                        if step['uses'].startswith('actions/checkout@'):
                            self.assertEqual(step['with']['persist-credentials'], 'false')

    def test_every_cloud_secret_is_guarded_before_step_execution(self):
        count = 0
        for name in FILES:
            d = read_workflow(name)
            self.assertNotIn('secrets.', str(d.get('env', {})))
            for job in d['jobs'].values():
                self.assertNotIn('secrets.', str(job.get('env', {})))
                for step in job['steps']:
                    if 'secrets.' not in str(step):
                        continue
                    count += 1
                    suffix = " && inputs.mode == 'azure'" if name == 'uqam-ouvertures.yml' else ' && inputs.narrated_review == true'
                    self.assertIn(step.get('if'), (MANUAL_MAIN + suffix, MANUAL_MAIN + suffix + " && steps.speech.outputs.available == 'true'"))
                    self.assertNotIn('secrets.', step.get('run', ''))
        self.assertEqual(count, 4)

    def test_paid_narration_is_not_default_dispatch_behavior(self):
        for name in ('teaching-revision.yml', 'uqam-revision.yml'):
            self.assertEqual(read_workflow(name)['on']['workflow_dispatch']['inputs']['narrated_review']['default'], 'false')
        self.assertEqual(read_workflow('uqam-ouvertures.yml')['on']['workflow_dispatch']['inputs']['mode']['default'], 'silent')

    def test_smoke_registry_and_existing_checks_are_not_disabled(self):
        jobs = read_workflow('smoke.yml')['jobs']
        self.assertEqual(len(jobs['render']['strategy']['matrix']['include']), 20)
        self.assertIn('ruff check .', [s.get('run') for s in jobs['lint']['steps']])
        self.assertEqual(jobs['render']['needs'], ['lint', 'compile'])
        self.assertNotIn('continue-on-error', jobs['lint'])
        self.assertIn('python -m py_compile', str(jobs['compile']))

    def test_secret_scan_covers_all_prs_and_never_uploads_raw_matches(self):
        d = read_workflow('public-audit.yml')
        self.assertFalse(d['on']['pull_request'])
        steps = d['jobs']['audit']['steps']
        self.assertTrue(any('refs/remotes/audit-pr-heads/*' in s.get('run', '') for s in steps))
        self.assertTrue(any('sha256sum --check --strict' in s.get('run', '') for s in steps))
        uploads = [s for s in steps if s.get('uses', '').startswith('actions/upload-artifact@')]
        self.assertEqual(len(uploads), 1)
        self.assertTrue(uploads[0]['with']['path'].endswith('/public-audit-summary.json'))


if __name__ == '__main__':
    unittest.main()
