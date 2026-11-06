#!/usr/bin/env python3
"""Prepare a local historical listening queue or validate exported human decisions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.listening_review import prepare_queue, validate_decisions  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', type=Path, default=ROOT / 'reports/narration_quality/2026-10-15/offline_revision.json')
    commands = parser.add_subparsers(dest='command', required=True)
    prepare = commands.add_parser('prepare')
    prepare.add_argument('--report', type=Path, required=True)
    prepare.add_argument('--output', type=Path, required=True)
    prepare.add_argument('--lessons', required=True, help='Comma-separated stable catalogue lesson IDs.')
    validate = commands.add_parser('validate')
    validate.add_argument('--queue', type=Path, required=True)
    validate.add_argument('--decisions', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding='utf-8'))
        expected = record['existing_audio_analysis']['output_report_sha256']
        if args.command == 'prepare':
            output = args.output.resolve()
            if not output.is_relative_to(ROOT / 'review_artifacts'):
                raise ValueError('Listening packages must stay under ignored review_artifacts/.')
            manifest = prepare_queue(args.report, expected, output, [x.strip() for x in args.lessons.split(',')])
            result = {'status': 'prepared_for_human_review', 'flags': len(manifest['flags']),
                      'videos': len(manifest['videos']), 'listening': 'not_performed', 'release_ready': False}
        else:
            result = validate_decisions(args.queue, json.loads(args.decisions.read_text(encoding='utf-8')), expected)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'blocked', 'reason': str(error), 'release_ready': False}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
