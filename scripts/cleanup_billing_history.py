"""Targeted, verified history cleanup in a disposable mirror.

Default: trial only. Publication requires explicit --publish and an expected main
SHA. Never overwrites another ref that moved during the trial. Does not delete
PRs, rewrite unrelated text, rotate credentials, or promise GitHub cache removal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

REPOSITORY = 'xia-geom/math_video_project'
URL = 'https://github.com/' + REPOSITORY + '.git'
BLOCKED = frozenset({'70ccebc1ed8e9953b42fed7f96cc8bf94d99a998',
                     '52cb3e29b6d8c311437d98a2811f6ab0af6996ba'})


def run(args: list[str], cwd: Path | None = None, data: bytes | None = None) -> bytes:
    result = subprocess.run(args, cwd=cwd, input=data, capture_output=True, timeout=600)
    if result.returncode:
        # Do not echo Git/filter output: old file contents or credentials may occur.
        raise RuntimeError(f'Command failed ({args[0]}, exit {result.returncode}); no raw output published')
    return result.stdout


def git(repo: Path, *args: str) -> bytes:
    return run(['git', '-C', str(repo), *args])


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def private_path(path: str) -> bool:
    p = PurePosixPath(path.replace('\\', '/').casefold())
    return p.name == 'azure_audit.md' or 'azure_billing_history' in p.parts


def refs(repo: Path) -> dict[str, str]:
    return {name: oid for oid, name in (line.split(' ', 1) for line in
            git(repo, 'for-each-ref', '--format=%(objectname) %(refname)').decode().splitlines())}


def writable(values: dict[str, str]) -> dict[str, str]:
    return {k: v for k, v in values.items() if k.startswith(('refs/heads/', 'refs/tags/'))}


def remote_refs(url: str) -> dict[str, str]:
    lines = run(['git', 'ls-remote', '--heads', '--tags', url]).decode().splitlines()
    return {name: oid for oid, name in (line.split('\t', 1) for line in lines) if not name.endswith('^{}')}


def tree(repo: Path, commit: str) -> dict[str, tuple[str, str, str]]:
    values = {}
    for row in git(repo, 'ls-tree', '-rz', '--full-tree', commit).split(b'\0'):
        if row:
            metadata, name = row.split(b'\t', 1)
            values[name.decode('utf-8', 'surrogateescape')] = tuple(metadata.decode().split())
    return values


def clean_tree(values: dict[str, tuple[str, str, str]], blocked: set[str]) -> dict:
    return {p: v for p, v in values.items() if not private_path(p) and v[2] not in blocked}


def verification(old_trees: dict, new_trees: dict, mapping: dict, blocked: set[str]) -> dict:
    if set(mapping) != set(old_trees):
        raise ValueError('Incomplete commit mapping')
    for old, original in old_trees.items():
        target = mapping[old]
        if target == '0' * 40 or target not in new_trees:
            raise ValueError('Unexpected dropped commit')
        if clean_tree(original, blocked) != new_trees[target]:
            raise ValueError('Non-billing tree content changed')
    return {'commits_verified': len(old_trees), 'non_billing_tree_preservation': True}


def build_plan(before: dict[str, str], after: dict[str, str]) -> list[dict]:
    old, new = writable(before), writable(after)
    if old.keys() != new.keys():
        raise ValueError('A branch or tag was unexpectedly added or lost')
    return [dict(ref=ref, before=oid, after=new[ref]) for ref, oid in sorted(old.items()) if new[ref] != oid]


def publish(repo: Path, before: dict, plan: list[dict], url: str, expected_main: str) -> dict:
    if before.get('refs/heads/main') != expected_main:
        raise ValueError('Main does not match the explicitly approved source')
    # Ref count/fingerprints checked immediately before atomic lease-protected push.
    if remote_refs(url) != writable(before):
        raise ValueError('Remote branch/tag changed during trial; nothing published')
    if not plan:
        return {'status': 'already_clean', 'updated_refs': 0}
    command = ['git', '-C', str(repo), 'push', '--atomic', '--no-verify']
    command += ['--force-with-lease=' + p['ref'] + ':' + p['before'] for p in plan]
    command += [url] + [p['after'] + ':' + p['ref'] for p in plan]
    run(command)
    expected = dict(writable(before))
    expected.update({p['ref']: p['after'] for p in plan})
    if remote_refs(url) != expected:
        raise ValueError('Post-publication ref verification mismatch')
    return {'status': 'published', 'updated_refs': len(plan), 'remote_refs_verified': True}


def trial(source: str, output: Path, do_publish: bool = False, expected_main: str | None = None) -> dict:
    if output.exists():
        raise ValueError('Use a fresh report directory')
    if do_publish and (source != URL or not expected_main or not re.fullmatch(r'[0-9a-f]{40}', expected_main)):
        raise ValueError('Publication restricted to the named repository and exact expected main')
    output.mkdir(parents=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix='private-history-cleanup-') as work:
        repo = Path(work) / 'mirror.git'
        run(['git', 'clone', '--mirror', source, str(repo)])
        before = refs(repo)
        if source == URL:
            git(repo, 'fetch', 'origin', '+refs/pull/*/head:refs/pull/*/head')
            before = refs(repo)
            if writable(before) != remote_refs(source):
                raise ValueError('Remote moved while acquiring the mirror')
        commits = git(repo, 'rev-list', '--all', '--topo-order', '--reverse').decode().splitlines()
        original = {oid: tree(repo, oid) for oid in commits}
        removed_paths, blocked = set(), set(BLOCKED)
        for values in original.values():
            for name, metadata in values.items():
                if private_path(name):
                    removed_paths.add(name)
                    if metadata[1] == 'blob':
                        blocked.add(metadata[2])
        # Include byte-identical renamed copies, without printing financial content.
        for values in original.values():
            removed_paths.update(name for name, meta in values.items() if meta[2] in blocked)
        before_tip_trees = {ref: tree(repo, ref) for ref in writable(before)}
        blocked_file = Path(work) / 'blocked-object-ids'
        blocked_file.write_text('\n'.join(sorted(blocked)) + '\n')
        command = ['git', '-C', str(repo), 'filter-repo', '--sensitive-data-removal', '--no-fetch', '--force',
                   '--prune-empty', 'never', '--prune-degenerate', 'never', '--invert-paths',
                   '--strip-blobs-with-ids', str(blocked_file)]
        for path in sorted(removed_paths):
            command += ['--path', path]
        mapping_path = repo / 'filter-repo' / 'commit-map'
        if removed_paths:
            filter_output = run(command)
            # Output is inspected for metadata only, never uploaded in raw form.
            mapping = {old: new for old, new in (line.split() for line in mapping_path.read_text().splitlines()[1:] if line.strip())}
        else:
            filter_output = b''
            mapping = {oid: oid for oid in commits}
            mapping_path.parent.mkdir(exist_ok=True)
            mapping_path.write_text('old new\n' + ''.join(f'{oid} {oid}\n' for oid in commits))
        new_trees = {oid: tree(repo, oid) for oid in set(mapping.values()) if oid != '0' * 40}
        checked = verification(original, new_trees, mapping, blocked)
        after = refs(repo)
        plan = build_plan(before, after)
        for ref, old_tree in before_tip_trees.items():
            if clean_tree(old_tree, blocked) != tree(repo, ref):
                raise ValueError('Branch/tag tip preservation mismatch')
        remaining = set(git(repo, 'rev-list', '--objects', '--all', '--no-object-names').decode().splitlines()) & blocked
        if remaining:
            raise ValueError('Forbidden report blobs remain reachable')
        first_changed = []
        inverse = {new: old_id for old_id, new in mapping.items()}
        for old in commits:
            if mapping[old] == old:
                continue
            parents = git(repo, 'cat-file', '-p', mapping[old]).split(b'\n\n', 1)[0].splitlines()
            old_parents = [line.split()[1].decode() for line in parents if line.startswith(b'parent ')]
            if all(mapping.get(inverse.get(p, p), p) == inverse.get(p, p) for p in old_parents):
                first_changed.append(old)
        affected_prs = sorted(int(ref.split('/')[2]) for ref in before if re.fullmatch(r'refs/pull/\d+/head', ref)
                              and before[ref] != after.get(ref))
        report = dict(schema_version=1, repository=REPOSITORY, mode='trial',
                      original_main=before.get('refs/heads/main'), rewritten_main=after.get('refs/heads/main'),
                      original_writable_refs_sha256=fingerprint(writable(before)),
                      rewritten_writable_refs_sha256=fingerprint(writable(after)),
                      removed_path_count=len(removed_paths), removed_blob_versions=len(blocked & set(
                          meta[2] for values in original.values() for meta in values.values())),
                      removed_paths=sorted(removed_paths), changed_commit_count=sum(k != v for k, v in mapping.items()),
                      writable_ref_updates=plan, affected_pr_heads=affected_prs,
                      first_changed_commits=first_changed, forbidden_blobs_remaining=0, **checked,
                      lfs_warning_detected=b'LFS Objects Orphaned' in filter_output,
                      cache_and_pr_purge='GitHub Support decision required; not performed by this script',
                      external_clones='Not accessible; re-clone/rebase instructions required')
        if do_publish:
            report['publication'] = publish(repo, before, plan, source, expected_main)
            report['mode'] = 'published' if report['publication']['status'] == 'published' else 'already_clean'
        else:
            report['publication'] = {'status': 'not_requested'}
        (output / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
        (output / 'commit-map.txt').write_text(mapping_path.read_text())
        support = ['# GitHub Support cleanup request', '', 'Repository: ' + REPOSITORY,
                   'Sensitive personal financial reports were removed from current main.',
                   'Publication status: ' + report['mode'] + '.',
                   'First changed commits: ' + ', '.join(first_changed),
                   'Affected PR heads: ' + ', '.join(map(str, affected_prs)),
                   'Please assess removal of affected PR references/cached views and server garbage collection.',
                   'No credentials or financial report text are attached. User-owned clones must be refreshed.',
                   'Support eligibility and completion have not been assumed.']
        (output / 'support-request.md').write_text('\n'.join(support) + '\n')
        return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default=URL)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--expected-main')
    args = parser.parse_args(argv)
    try:
        report = trial(args.source, args.output, args.publish, args.expected_main)
        print(json.dumps(report, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status': 'blocked', 'error': str(exc), 'no_clearance_claim': True}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
