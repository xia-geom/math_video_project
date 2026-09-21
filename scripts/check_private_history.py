"""Block reintroduction of known private reports in outgoing commit history.

Metadata-only scan: no private file bodies or matching text are printed. This is
not a universal secret scanner. Used by the opt-in local pre-push hook.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

BLOCKED = frozenset({'70ccebc1ed8e9953b42fed7f96cc8bf94d99a998',
                     '52cb3e29b6d8c311437d98a2811f6ab0af6996ba'})


def forbidden(path: str) -> bool:
    p = PurePosixPath(path.replace('\\', '/').casefold())
    return p.name == 'azure_audit.md' or 'azure_billing_history' in p.parts


def check(root: Path, revisions: list[str]) -> dict:
    root = root.resolve()
    def git(*args: str) -> bytes:
        return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)
    if git('rev-parse', '--is-shallow-repository').strip() != b'false':
        raise ValueError('Full history is needed for the pre-push privacy guard')
    resolved = []
    for rev in revisions:
        if not re.fullmatch(r'[0-9a-f]{40,64}|HEAD', rev):
            raise ValueError('Use HEAD or an exact commit hash')
        resolved.append(git('rev-parse', '--verify', rev + '^{commit}').decode().strip())
    if not resolved:
        return {'status': 'passed', 'revisions_checked': 0, 'findings': []}
    objects = set(git('rev-list', '--objects', '--no-object-names', *resolved, '--').decode().splitlines())
    paths = git('log', '-z', '--format=', '--name-only', *resolved, '--').split(b'\0')
    bad_paths = {p.decode('utf-8', 'surrogateescape').lstrip('\n') for p in paths if p}
    bad_paths = {p for p in bad_paths if forbidden(p)}
    reasons = []
    if objects & BLOCKED:
        reasons.append('known_private_report_in_history')
    if bad_paths:
        reasons.append('private_report_path_in_history')
    return {'status': 'blocked' if reasons else 'passed', 'revisions_checked': len(resolved),
            'findings': reasons, 'matched_path_count': len(bad_paths),
            'scope': 'outgoing reachable history, not GitHub caches or edited/renamed unknown content'}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--pre-push', action='store_true')
    parser.add_argument('--revision', default='HEAD')
    args = parser.parse_args(argv)
    try:
        revisions = [args.revision]
        if args.pre_push:
            revisions = []
            for row in sys.stdin:
                parts = row.split()
                if len(parts) != 4:
                    raise ValueError('Malformed pre-push input')
                if set(parts[1]) != {'0'}:
                    revisions.append(parts[1])
        report = check(args.root, revisions)
        print(json.dumps(report))
        return int(report['status'] != 'passed')
    except (OSError, ValueError, subprocess.CalledProcessError):
        print(json.dumps({'status': 'blocked', 'reason': 'Unable to verify outgoing history; no content printed'}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
