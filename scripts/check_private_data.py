"""Reject known private files in the Git index without printing their contents.

This is a narrow prevention check, not a full secret/privacy scanner or a history
purge. It includes already-tracked and force-added files, regardless of ignore rules.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path, PurePosixPath

# Existing report object IDs allow detection of unchanged copies under other names.
# These are Git blob fingerprints, not credentials or reproduced financial data.
BLOCKED_BLOBS = frozenset({
    '70ccebc1ed8e9953b42fed7f96cc8bf94d99a998',
    '52cb3e29b6d8c311437d98a2811f6ab0af6996ba',
})


def path_reason(name: str) -> str | None:
    """Match components, including case variants, without banning technical guides."""
    path = PurePosixPath(name.replace('\\', '/').casefold())
    parts = path.parts
    if path.name == 'azure_audit.md' or 'azure_billing_history' in parts:
        return 'personal_billing_report'
    if 'private' in parts or any(a == 'data' and b == 'raw' for a, b in zip(parts, parts[1:])):
        return 'private_data_directory'
    if path.name != '.env.example' and (path.name == '.env' or path.name.startswith('.env.')):
        return 'local_environment_file'
    if path.name in {'credentials.json', 'token.json', 'id_rsa', 'id_ed25519'}:
        return 'credential_file'
    if path.suffix in {'.p12', '.pfx', '.key', '.sqlite', '.sqlite3'} or '.sqlite-' in path.name or '.sqlite3-' in path.name:
        return 'private_key_or_database'
    return None


def check_index(root: Path, blocked_blobs: frozenset[str] = BLOCKED_BLOBS) -> dict:
    """Read Git index metadata only; no file bodies, cloud access or subprocess shell."""
    root = root.resolve()
    top = subprocess.check_output(
        ['git', '-C', str(root), 'rev-parse', '--show-toplevel'], stderr=subprocess.PIPE
    ).decode().strip()
    if Path(top).resolve() != root:
        raise ValueError('Run from or point --root to the repository root')
    records = subprocess.check_output(
        ['git', '-C', str(root), 'ls-files', '--stage', '-z'], stderr=subprocess.PIPE
    )
    findings, count = [], 0
    for record in records.split(b'\0'):
        if not record:
            continue
        metadata, raw_path = record.split(b'\t', 1)
        _mode, oid, stage = metadata.decode('ascii').split()
        name = raw_path.decode('utf-8', 'surrogateescape')
        count += 1
        reason = path_reason(name)
        if stage != '0':
            reason = 'unresolved_index_conflict'
        elif oid in blocked_blobs:
            reason = 'unchanged_copy_of_private_report'
        if reason:
            findings.append({'path': name, 'reason': reason})
    return {'version': 1, 'scope': 'current_git_index', 'tracked_records_checked': count,
            'status': 'blocked' if findings else 'passed', 'findings': findings,
            'history_cleaned': False,
            'limitations': 'Does not detect all renamed/edited private content or inspect history, logs, artifacts, media or external copies.'}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    try:
        report = check_index(args.root)
    except (OSError, ValueError, subprocess.CalledProcessError):
        print(json.dumps({'status': 'error', 'reason': 'Could not inspect the repository index; not a clean scan.'}))
        return 2
    # Escape control characters; report locations, never matching source content.
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 1 if report['findings'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
