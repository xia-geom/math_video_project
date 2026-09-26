"""Find known financial-report copies in retained Actions artifacts and logs.

Read-only by default. --apply deletes only positively matched artifact payloads or
run logs. Never prints matched content. Limits and inaccessible items are explicit;
this does not inspect pictures, PDFs, external downloads or GitHub PR caches.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = 'xia-geom/math_video_project'
PREFIX = 'repos/' + REPO + '/'
BLOBS = ('70ccebc1ed8e9953b42fed7f96cc8bf94d99a998', '52cb3e29b6d8c311437d98a2811f6ab0af6996ba')
MAX_ZIP = 100 * 1024 * 1024
MAX_TEXT = 4 * 1024 * 1024
TEXT_TYPES = {'.md', '.txt', '.log', '.json', '.jsonl', '.csv', '.tsv', '.yml', '.yaml', '.py', '.tex', '.srt', '.xml', '.html'}


def gh(endpoint: str, method: str = 'GET') -> bytes:
    if not endpoint.startswith(PREFIX):
        raise ValueError('Wrong repository')
    result = subprocess.run(['gh', 'api', '--hostname', 'github.com', '--method', method, endpoint],
                            capture_output=True, timeout=120)
    if result.returncode:
        raise RuntimeError('GitHub resource unavailable or permission denied')
    return result.stdout


def download(endpoint: str) -> bytes:
    if not endpoint.startswith(PREFIX):
        raise ValueError('Wrong repository')
    with tempfile.TemporaryFile() as stream:
        result = subprocess.run(['gh', 'api', '--hostname', 'github.com', endpoint],
                                stdout=stream, stderr=subprocess.PIPE, timeout=120)
        if result.returncode:
            raise RuntimeError('Download unavailable')
        if stream.tell() > MAX_ZIP:
            raise ValueError('Download exceeds audit size limit')
        stream.seek(0)
        return stream.read()


def normal(line: str) -> str:
    line = re.sub(r'\x1b\[[0-9;]*m', '', line)
    line = re.sub(r'^\d{4}-\d\d-\d\dT\S+\s+', '', line)
    return ' '.join(line.strip().lstrip('+-').split())


def line_hash(line: str) -> str:
    return hashlib.sha256(normal(line).encode()).hexdigest()


def signatures(originals: list[bytes]) -> tuple[set[str], set[str]]:
    whole, lines = set(), set()
    for raw in originals:
        whole.add(hashlib.sha256(raw).hexdigest())
        for line in raw.decode('utf-8').splitlines():
            if len(line) >= 80 and re.search(r'(?i)(?:CAD|USD|billing|credit|subscription|invoice|cost).*\d', line):
                lines.add(line_hash(line))
    if not whole or len(lines) < 2:
        raise ValueError('Reference fingerprints unavailable; no deletions allowed')
    return whole, lines


def matches(raw: bytes, whole: set[str], lines: set[str]) -> bool:
    if hashlib.sha256(raw).hexdigest() in whole:
        return True
    if b'\0' in raw[:8192]:
        return False
    hits = {line_hash(line) for line in raw.decode('utf-8', 'replace').splitlines()} & lines
    return len(hits) >= 2


def inspect_zip(raw: bytes, whole: set[str], lines: set[str], depth: int = 0) -> dict:
    result = {'match': False, 'text_members_scanned': 0, 'members_not_scanned': 0}
    if depth > 2 or len(raw) > MAX_ZIP:
        result['members_not_scanned'] = 1
        return result
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        budget = 64 * 1024 * 1024
        for member in archive.infolist():
            if member.is_dir():
                continue
            suffix = Path(member.filename).suffix.lower()
            if suffix not in TEXT_TYPES | {'.zip'} or member.file_size > MAX_TEXT or member.file_size > budget or member.flag_bits & 1:
                result['members_not_scanned'] += 1
                continue
            budget -= member.file_size
            content = archive.read(member)
            if suffix == '.zip':
                child = inspect_zip(content, whole, lines, depth + 1)
                result['match'] = result['match'] or child['match']
                for key in ('text_members_scanned', 'members_not_scanned'):
                    result[key] += child[key]
            else:
                result['text_members_scanned'] += 1
                result['match'] = result['match'] or matches(content, whole, lines)
    return result


def pages(endpoint: str, field: str) -> list[dict]:
    values = []
    for page in range(1, 101):
        separator = '&' if '?' in endpoint else '?'
        response = json.loads(gh(endpoint + separator + f'per_page=100&page={page}'))
        chunk = response[field]
        values.extend(chunk)
        if len(chunk) < 100 or len(values) >= response['total_count']:
            return values
    raise ValueError('Pagination limit reached; full list not obtained')


def execute(apply: bool, checkpoint=None) -> dict:
    originals = [base64.b64decode(json.loads(gh(PREFIX + 'git/blobs/' + oid))['content']) for oid in BLOBS]
    whole, lines = signatures(originals)
    del originals
    report = {'repository': REPO, 'mode': 'apply' if apply else 'audit', 'positively_matched': [],
              'deleted': [], 'unavailable_or_limited': [], 'artifacts_scanned': 0, 'run_logs_scanned': 0,
              'expired_artifacts': 0, 'text_members_scanned': 0, 'members_not_scanned': 0,
              'raw_content_published': False}
    artifacts = pages(PREFIX + 'actions/artifacts', 'artifacts')
    runs = pages(PREFIX + 'actions/runs?status=completed', 'workflow_runs')
    report['artifact_records'] = len(artifacts)
    report['completed_run_records'] = len(runs)
    work = []
    for artifact in artifacts:
        if artifact['expired']:
            report['expired_artifacts'] += 1
        elif artifact['size_in_bytes'] > MAX_ZIP:
            report['unavailable_or_limited'].append({'kind':'artifact','id':artifact['id'],'reason':'size_limit'})
        else:
            work.append(('artifact', artifact['id'], PREFIX + f"actions/artifacts/{artifact['id']}/zip"))
    for run in runs:
        if str(run['id']) != os.getenv('GITHUB_RUN_ID', ''):
            work.append(('logs', run['id'], PREFIX + f"actions/runs/{run['id']}/logs"))
    def inspect_item(item):
        kind, identity, endpoint = item
        try:
            return kind, identity, inspect_zip(download(endpoint), whole, lines)
        except (RuntimeError, ValueError, OSError, zipfile.BadZipFile, subprocess.TimeoutExpired):
            return kind, identity, None
    report['inventory_processing_complete'] = False
    report['resources_attempted'] = 0
    if checkpoint:
        checkpoint(report)
    with ThreadPoolExecutor(max_workers=4) as executor:
        for kind, identity, scanned in executor.map(inspect_item, work):
            report['resources_attempted'] += 1
            if scanned is None:
                report['unavailable_or_limited'].append({'kind':kind,'id':identity,'reason':'unavailable_or_limit'})
            else:
                report['artifacts_scanned' if kind == 'artifact' else 'run_logs_scanned'] += 1
                for key in ('text_members_scanned', 'members_not_scanned'):
                    report[key] += scanned[key]
                if scanned['match']:
                    finding = {'kind': kind, 'id': identity}
                    report['positively_matched'].append(finding)
                    if apply:
                        target = PREFIX + (f'actions/artifacts/{identity}' if kind == 'artifact' else f'actions/runs/{identity}/logs')
                        try:
                            gh(target, 'DELETE')
                            report['deleted'].append(finding)
                        except (RuntimeError, subprocess.TimeoutExpired):
                            report['unavailable_or_limited'].append({'kind':kind,'id':identity,'reason':'matched_but_deletion_denied'})
            if checkpoint:
                checkpoint(report)
    report['inventory_processing_complete'] = True
    report['limits'] = 'Only known-report fingerprints in readable text; binary media, oversized members and external copies not cleared.'
    report['complete_privacy_clearance'] = False
    return report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        report = execute(args.apply, lambda value: args.output.write_text(json.dumps(value, indent=2) + '\n'))
    except (RuntimeError, ValueError, OSError, KeyError, subprocess.TimeoutExpired) as exc:
        report = {'status': 'blocked', 'reason': str(exc), 'complete_privacy_clearance': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 2 if report.get('status') == 'blocked' else 0


if __name__ == '__main__':
    raise SystemExit(main())
