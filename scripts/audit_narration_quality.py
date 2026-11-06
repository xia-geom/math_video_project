#!/usr/bin/env python3
"""Screen hash-bound narration audio offline; never synthesize or trim.

Modes: --videos-root + --provenance-root [--video-glob '*.mp4'];
--manifest pairs.json; or --provenance provenance.json [--video video.mp4].
The JSON manifest has a pairs list of video/provenance paths, relative to itself.
The output directory must be new. No flags does not validate pronunciation.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.narration_quality import (  # noqa: E402
    AuditConfig,
    AuditError,
    audit_pairs,
    discover_pairs,
    load_manifest,
    pair_from_provenance,
    write_report,
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--videos-root', type=Path)
    mode.add_argument('--manifest', type=Path)
    mode.add_argument('--provenance', type=Path)
    parser.add_argument('--provenance-root', type=Path)
    parser.add_argument('--video', type=Path, help='Explicit video for standalone --provenance.')
    parser.add_argument('--video-glob', default='*.mp4', help='Recursive video selection in root mode.')
    parser.add_argument('--output', type=Path, required=True, help='New directory; existing audits are preserved.')
    parser.add_argument('--noise-db', type=float, default=-40.0)
    parser.add_argument('--min-silence', type=float, default=2.0)
    parser.add_argument('--boundary-tolerance', type=float, default=0.25)
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--fail-on-review', action='store_true', help='Exit 2 when internal or boundary intervals need review.')
    args = parser.parse_args(argv)
    if bool(args.videos_root) != bool(args.provenance_root):
        parser.error('--videos-root and --provenance-root must be supplied together')
    if args.video and not args.provenance:
        parser.error('--video requires --provenance')
    try:
        if args.output.exists():
            raise AuditError(f'Output already exists; choose a new directory: {args.output}')
        config = AuditConfig(args.noise_db, args.min_silence, args.boundary_tolerance, args.jobs)
        if args.videos_root:
            pairs = discover_pairs(args.videos_root, args.provenance_root, args.video_glob)
        elif args.manifest:
            pairs = load_manifest(args.manifest)
        else:
            pairs = [pair_from_provenance(args.provenance, args.video)]
        report = audit_pairs(pairs, config=config)
        write_report(report, args.output)
    except (AuditError, OSError, ValueError, TypeError, KeyError) as exc:
        error = {'schema_version': 1, 'status': 'error', 'error': str(exc),
                 'pronunciation': 'not_assessed', 'listening': 'not_performed', 'release_ready': False}
        if not args.output.exists():
            try:
                write_report(error, args.output)
            except (OSError, AuditError):
                pass
        print(json.dumps(error, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({'status': report['status'], **report['summary'],
                      'report': str((args.output / 'report.json').resolve()),
                      'pronunciation': 'not_assessed'}, ensure_ascii=False))
    return 2 if args.fail_on_review and report['status'] == 'review_required' else 0


if __name__ == '__main__':
    raise SystemExit(main())
