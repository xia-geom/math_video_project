"""Owner-run GitHub administration using existing gh authentication, not CI keys.

Defaults are preview-only. --apply requires administrative permissions, creates
one additive named ruleset, enables private reporting and secret push protection,
and verifies responses. Existing unrelated rules/protections are never disabled.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

REPO = 'xia-geom/math_video_project'


def api(method: str, path: str, body=None):
    args = ['gh', 'api', '--hostname', 'github.com', '--method', method, path,
            '-H', 'Accept: application/vnd.github+json']
    payload = None
    if body is not None:
        args += ['--input', '-']
        payload = json.dumps(body).encode()
    result = subprocess.run(args, input=payload, capture_output=True)
    if result.returncode:
        raise RuntimeError('GitHub administration request failed; use an owner-authorized gh login. No token printed.')
    return json.loads(result.stdout) if result.stdout.strip() else None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    plan = json.loads((root / '.github/rulesets/private-data-safety.json').read_text())
    try:
        if not args.apply:
            print(json.dumps({'repository': REPO, 'ruleset': plan, 'private_reporting': 'enable',
                              'secret_scanning': 'enable', 'push_protection': 'enable',
                              'performed': False}, indent=2))
            return 0
        repo = api('GET', 'repos/' + REPO)
        if not repo.get('permissions', {}).get('admin'):
            raise RuntimeError('Administrator access is required; no settings changed.')
        checks = api('GET', 'repos/' + REPO + '/commits/main/check-runs?per_page=100')['check_runs']
        for item in plan['rules'][-1]['parameters']['required_status_checks']:
            matches = [c for c in checks if c['name'] == item['context'] and c['app']['slug'] == 'github-actions']
            if not matches or not any(c.get('conclusion') == 'success' for c in matches):
                raise RuntimeError('Expected safety checks have not passed on current main; no protections weakened.')
            item['integration_id'] = matches[0]['app']['id']
        existing = api('GET', 'repos/' + REPO + '/rulesets?includes_parents=false&per_page=100')
        matches = [r for r in existing if r['name'] == plan['name']]
        if len(matches) > 1:
            raise RuntimeError('Multiple named rulesets need manual review.')
        if matches:
            saved = api('GET', 'repos/' + REPO + '/rulesets/' + str(matches[0]['id']))
            if any(saved.get(k) != v for k, v in plan.items()):
                raise RuntimeError('Existing named ruleset differs; review it instead of replacing protections.')
        else:
            saved = api('POST', 'repos/' + REPO + '/rulesets', plan)
        verified = api('GET', 'repos/' + REPO + '/rulesets/' + str(saved['id']))
        if verified.get('enforcement') != 'active':
            raise RuntimeError('Ruleset activation not verified.')
        api('PUT', 'repos/' + REPO + '/private-vulnerability-reporting')
        api('PATCH', 'repos/' + REPO, {'security_and_analysis': {
            'secret_scanning': {'status': 'enabled'},
            'secret_scanning_push_protection': {'status': 'enabled'}
        }})
        reporting = api('GET', 'repos/' + REPO + '/private-vulnerability-reporting')
        security = api('GET', 'repos/' + REPO).get('security_and_analysis', {})
        ok = reporting.get('enabled') is True and all(security.get(k, {}).get('status') == 'enabled'
                for k in ('secret_scanning', 'secret_scanning_push_protection'))
        print(json.dumps({'ruleset_id': saved['id'], 'ruleset_active': True,
                          'private_reporting_and_secret_protection_verified': ok}))
        return 0 if ok else 2
    except (OSError, KeyError, ValueError, RuntimeError) as exc:
        print(json.dumps({'status': 'incomplete', 'reason': str(exc),
                          'note': 'Some additive settings may have succeeded; rerun does not remove existing protections.'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
