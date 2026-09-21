"""Read-only publication audit. Prints counts/locations, never matched secrets.

Run against a full clone with gitleaks on PATH. Git history and current tracked
files are scanned separately. Optional GitHub sampling is bounded and reports
its exclusions. This is not a legal clearance or a proof of no sensitive data.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request

MAX_BLOB = 20 * 1024 * 1024
LOCAL_PATH = re.compile(r"(?:/Users/|/home/)(?!runner(?:/|\b)|user(?:/|\b)|example(?:/|\b)|username(?:/|\b))[^/\s<>]+/")


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.DEVNULL)


def credential_path(name: str) -> bool:
    p = Path(name)
    return ((p.name == '.env' or p.name.startswith('.env.')) and p.name != '.env.example') or p.name in {
        'credentials.json', 'token.json', 'id_rsa', 'id_ed25519', '.npmrc', '.pypirc'
    } or p.suffix.lower() in {'.p12', '.pfx', '.key'}


def history_inventory(root: Path) -> dict:
    if git(root, 'rev-parse', '--is-shallow-repository').strip() != b'false':
        raise ValueError('Full history is required; shallow clone refused')
    objects = git(root, 'rev-list', '--objects', '--all').splitlines()
    parsed = [line.decode('utf-8', 'replace').split(' ', 1) for line in objects]
    names = {parts[0]: parts[1] for parts in parsed if len(parts) == 2}
    proc = subprocess.run(['git', '-C', str(root), 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)'],
                          input=b'\n'.join(p[0].encode() for p in parsed), capture_output=True, check=True)
    blobs = [(x[0], int(x[2])) for line in proc.stdout.decode().splitlines()
             if len(x := line.split()) == 3 and x[1] == 'blob']
    sensitive_names = sorted({name for name in names.values() if credential_path(name)})
    local_locations, binary_count, oversized, text_count = set(), 0, 0, 0
    # One git process, and each distinct historical blob is examined once.
    reader = subprocess.Popen(['git', '-C', str(root), 'cat-file', '--batch'], stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        for oid, size in blobs:
            if size > MAX_BLOB:
                oversized += 1
                continue
            reader.stdin.write((oid + '\n').encode())
            reader.stdin.flush()
            header = reader.stdout.readline().split()
            if len(header) != 3 or header[1] != b'blob':
                raise ValueError('Unexpected git object stream')
            content = reader.stdout.read(int(header[2]))
            if reader.stdout.read(1) != b'\n':
                raise ValueError('Incomplete git object stream')
            if b'\0' in content[:8192]:
                binary_count += 1
                continue
            text_count += 1
            if LOCAL_PATH.search(content.decode('utf-8', 'replace')):
                local_locations.add(names.get(oid, 'unnamed-object:' + oid[:12]))
    finally:
        reader.stdin.close()
        reader.stdout.close()
        reader.wait(timeout=10)
    emails = set(git(root, 'log', '--all', '--format=%ae%n%ce').decode('utf-8', 'replace').splitlines())
    return {
        'commits': int(git(root, 'rev-list', '--count', '--all')),
        'refs': len(git(root, 'for-each-ref', '--format=%(refname)').splitlines()),
        'distinct_blobs': len(blobs), 'text_blobs_examined': text_count,
        'binary_blobs_not_manually_reviewed': binary_count, 'oversized_blobs_skipped': oversized,
        'credential_like_historical_paths': sensitive_names,
        'personal_local_path_file_count': len(local_locations),
        'personal_local_path_files': sorted(local_locations),
        'non_noreply_commit_email_count': sum('noreply' not in e.lower() for e in emails if e),
        'scope': 'Fetched refs only; unreachable objects, deleted remote refs and external forks are not covered.'
    }


def scan_secrets(executable: str, target: Path, report: Path, config: Path, history: bool = False) -> dict:
    args = [executable, 'git' if history else 'dir', str(target), '--config', str(config),
            '--redact=100', '--no-banner', '--no-color', '--exit-code=23',
            '--report-format=json', '--report-path', str(report)]
    if history:
        args += ['--log-opts=--all --full-history']
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
    # Do not echo scanner output: even redacted reports contain unrelated metadata.
    if result.returncode not in (0, 23) or not report.is_file():
        return {'status': 'scanner_error', 'exit_code': result.returncode, 'findings': None}
    findings = json.loads(report.read_text()) or []
    return {'status': 'findings' if findings else 'passed', 'findings': len(findings),
            'rules': dict(Counter(x['RuleID'] for x in findings)),
            'locations': sorted({f"{x.get('File', '')}:{x.get('StartLine', '')}" for x in findings})}


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme != 'https':
            raise ValueError('Non-HTTPS redirect refused')
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if urllib.parse.urlsplit(newurl).hostname != 'api.github.com':
            redirected.remove_header('Authorization')
        return redirected


def github_surface(repo: str, destination: Path, token: str, run_limit: int = 10) -> dict:
    """GET-only bounded sample. Raw responses stay in temporary local files."""
    if not re.fullmatch(r'[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+', repo) or repo.split('/')[-1] in {'.', '..'}:
        raise ValueError('Invalid repository selector')
    destination.mkdir()
    opener = urllib.request.build_opener(SafeRedirect())
    failures, stats = [], Counter()

    def request(endpoint: str, label: str, binary: bool = False):
        url = 'https://api.github.com/repos/' + repo + '/' + endpoint
        headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'math-video-public-audit'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        try:
            with opener.open(urllib.request.Request(url, headers=headers), timeout=25) as response:
                raw = response.read(MAX_BLOB + 1)
            if len(raw) > MAX_BLOB:
                failures.append({'resource': label, 'reason': 'size_limit'})
                return None
            (destination / (label + '.txt')).write_bytes(raw)
            stats['responses_scanned'] += 1
            return raw if binary else json.loads(raw)
        except (urllib.error.URLError, ValueError) as exc:
            failures.append({'resource': label, 'reason': 'http_' + str(getattr(exc, 'code', 'unavailable'))})
            return None

    # Bound pagination; record whether a limit was hit, never silently call it complete.
    for endpoint, label in [('issues?state=all', 'issues'), ('issues/comments?', 'issue-comments'),
                            ('pulls/comments?', 'review-comments')]:
        for page in range(1, 6):
            separator = '&' if '?' in endpoint and not endpoint.endswith('?') else ''
            values = request(endpoint + separator + f'per_page=100&page={page}', f'{label}-{page}')
            if not isinstance(values, list):
                break
            stats[label] += len(values)
            if len(values) < 100:
                break
            if page == 5:
                failures.append({'resource': label, 'reason': 'pagination_limit'})
    runs = request(f'actions/runs?status=completed&per_page={run_limit}', 'recent-runs')
    if runs:
        stats['completed_runs_available'] = runs['total_count']
        for run in runs['workflow_runs']:
            stats['completed_runs_sampled'] += 1
            jobs = request(f"actions/runs/{run['id']}/jobs?per_page=100", f"jobs-{run['id']}")
            if jobs:
                if jobs['total_count'] > len(jobs['jobs']):
                    failures.append({'resource': f"jobs-{run['id']}", 'reason': 'pagination_limit'})
                for job in jobs['jobs']:
                    if job['conclusion'] == 'skipped':
                        continue
                    raw = request(f"actions/jobs/{job['id']}/logs", f"log-{job['id']}", True)
                    if raw is not None:
                        stats['job_logs_scanned'] += 1
    artifacts = request('actions/artifacts?per_page=100', 'artifacts-metadata')
    if artifacts:
        stats['artifact_metadata_seen'] = len(artifacts['artifacts'])
        stats['artifacts_total'] = artifacts['total_count']
    request('releases?per_page=100', 'releases')
    stats['files_with_personal_local_paths'] = sum(bool(LOCAL_PATH.search(p.read_text(errors='replace'))) for p in destination.glob('*.txt'))
    return {'counts': dict(stats), 'unavailable_or_limited': failures,
            'scope': 'Issue/PR bodies, issue/review comments (up to 500 each), latest completed runs and accessible job logs. Artifact metadata only.',
            'not_reviewed': ['older logs', 'artifact payloads', 'binary media', 'PR review-submission bodies', 'external links and forks']}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--gitleaks', required=True)
    parser.add_argument('--github-repository')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    report = {'schema_version': 1, 'audit_head': git(root, 'rev-parse', 'HEAD').decode().strip()}
    with tempfile.TemporaryDirectory(prefix='public-audit-') as tmp:
        temp = Path(tmp)
        config = temp / 'gitleaks.toml'
        config.write_text('[extend]\nuseDefault = true\n')
        report['history'] = history_inventory(root)
        report['history_secret_scan'] = scan_secrets(args.gitleaks, root, temp / 'history.json', config, True)
        current = temp / 'tracked'
        current.mkdir()
        for name in git(root, 'ls-files', '-z').decode().split('\0'):
            if not name:
                continue
            source = root / name
            if source.is_symlink():
                continue
            if source.is_file():
                dest = current / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
        report['tracked_secret_scan'] = scan_secrets(args.gitleaks, current, temp / 'tracked.json', config)
        if args.github_repository:
            report['github_surface'] = github_surface(args.github_repository, temp / 'surface', os.getenv('GH_TOKEN', ''))
            report['surface_secret_scan'] = scan_secrets(args.gitleaks, temp / 'surface', temp / 'surface.json', config)
        report['assurance'] = 'Automated scoped audit, not a guarantee of no secrets, privacy clearance, media-rights approval or production readiness.'
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(report, indent=2))
        scans = [v for k, v in report.items() if k.endswith('_secret_scan')]
        return 1 if any(x['status'] != 'passed' for x in scans) else 0


if __name__ == '__main__':
    raise SystemExit(main())
