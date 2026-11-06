#!/usr/bin/env python3
"""Select smoke renders from catalogue dependencies; uncertainty selects all."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.course_catalog import load_catalog  # noqa: E402
from tools.course_review import input_hashes  # noqa: E402


def documentation(path):
    return path in {'README.md', 'AGENTS.md', 'ARCHITECTURE.md', 'SECURITY.md', 'THIRD_PARTY_NOTICES.md'} or (
        path.endswith('.md') and path.startswith(('docs/', 'reports/', 'curriculum/')))


def select(entries, changed, root=ROOT):
    def result(selected, reason, unknown=()):
        return {'schema_version': 1, 'reason': reason, 'changed_paths': changed,
                'unknown_paths': list(unknown), 'catalogue_count': len(entries),
                'selected_count': len(selected), 'lesson_ids': [e['lesson_id'] for e in selected],
                'matrix': {'include': [{'file': e['scene_file'], 'class': e['scene_class']}
                                       for e in selected]}}

    if changed is None:
        return result(entries, 'Full scope: no reliable comparison, or explicitly requested.')
    if any(not isinstance(p, str) or not p or PurePosixPath(p).is_absolute()
           or '..' in PurePosixPath(p).parts or '\\' in p or '\n' in p for p in changed):
        return result(entries, 'Full scope: an unrecognized changed path cannot be classified.')
    active = set(changed) - {p for p in changed if documentation(p)}
    if not active:
        return result([], 'No render inputs changed; documentation-only or empty diff.')
    try:
        dependencies = {e['lesson_id']: set(input_hashes(e, root)) for e in entries}
    except (OSError, ValueError, SyntaxError):
        return result(entries, 'Full scope: dependency analysis could not establish a complete input set.')
    known = set().union(*dependencies.values())
    unknown = active - known
    if unknown:
        return result(entries, 'Full scope: changed paths are outside known render dependencies.', sorted(unknown))
    affected = [e for e in entries if dependencies[e['lesson_id']] & active]
    return result(affected, 'Selected every lesson whose recorded dependency closure intersects the diff.')


def changed_paths(event, root=ROOT):
    """Use exact Git object IDs, never branch names or shell-interpolated input."""
    pull = event.get('pull_request')
    base = pull.get('base', {}).get('sha') if pull else event.get('before')
    head = pull.get('head', {}).get('sha') if pull else event.get('after')
    if any(not isinstance(sha, str) or not re.fullmatch(r'[0-9a-f]{40}', sha)
           or sha == '0' * 40 for sha in (base, head)):
        return None
    try:
        if pull:
            base = subprocess.check_output(['git', 'merge-base', base, head], cwd=root,
                                           stderr=subprocess.DEVNULL, text=True).strip()
        raw = subprocess.check_output(['git', 'diff', '--name-only', '-z', '--no-renames',
                                       base, head, '--'], cwd=root, stderr=subprocess.DEVNULL)
        return sorted(set(raw.decode('utf-8').rstrip('\0').split('\0'))) if raw else []
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--event-path', type=Path)
    parser.add_argument('--changed-path', action='append')
    parser.add_argument('--full', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    _, entries = load_catalog()
    changed = args.changed_path
    if args.full:
        changed = None
    elif args.event_path:
        changed = changed_paths(json.loads(args.event_path.read_text(encoding='utf-8')))
    record = select(entries, changed)
    record['release_approval'] = False
    payload = json.dumps(record, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding='utf-8')
    if os.environ.get('GITHUB_OUTPUT'):
        with Path(os.environ['GITHUB_OUTPUT']).open('a', encoding='utf-8') as stream:
            stream.write('matrix=' + json.dumps(record['matrix']) + '\n')
            stream.write(f"selected_count={record['selected_count']}\n")
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a', encoding='utf-8') as stream:
            stream.write(f"Selected {record['selected_count']}/{record['catalogue_count']} lessons. "
                         f"{record['reason']}\n")
    print(payload, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
