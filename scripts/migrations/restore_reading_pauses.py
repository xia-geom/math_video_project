"""Apply this inspected timing follow-up once, then remove this change tool."""
import hashlib
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
    'docs/TEACHING_STANDARD.md': '5ff3c78ebbfbb48ff95eb5a0c97e216f60fb26ebf2690d5172173b27aa8c19ec',
    'scripts/course_audit.py': '607bb0333e48381a35d4c910531a9b79d2ddcb31fd323a905b0d804f2a59ee01',
    'scripts/render_curriculum.py': 'aae84de72646006ecd816ee6fafefc7dcd0cced919244f5cfaad1a9cc2e594f2',
    'scripts/render_syllabus_expansion.py': '04dce5f9d074c1cd5771587cf9818ce58f1441e488fc3feb69b51d3424a6fe81',
}
SCENE_HASHES = {
    'S01': 'e30e3e6c49189ab1dc92d04e150d0f5cb976c723b5f2f38446bbccf350d250ee',
    'S02': '65ba2682b9ce09d4463f90ca07cfb3ec3baf54c1164b5def2cfdfe4215dd915f',
    'S03': '216b9c5d0d1bdbfeb2a2f45044f423f08c68131200bca7dcb091c0ec1d95a976',
    'S04': '26b11ca478806686b7ca9eaaf5d2c5ac5db978a7ff9d958fd9e20919079ebf12',
    'S05': '548748144cfcb56d2260f1349ef1ffad496e108f6dd944806ff4fc13a8db853d',
    'S06': 'feb7b484ddc6442c5f24b90b587a541bb6ffca1a5d600ebb5c39373a546c9fe4',
    'S07': '7efff481e22336a442a51c4cd22fafdbd8fa0d3037eaa73de185390368d0fead',
    'S08': '888810be5ea012b23722be27684f4f62f4872ee4973c23b6ad9e8f00af5f026c',
    'S09': 'fe9646b82b6ec89cf03b3a80534225725d1aa0a62eabb8b06f1000b5847082e7',
    'S10': '2c866d44de1aaacd3f26cc95af8e4c166fdbd411569fbfddefa074c90a7a55c0',
}
entries = yaml.safe_load((ROOT / 'curriculum/programme_principal_fr.yaml').read_text())['entries']
for entry in entries:
    if entry['legacy_id'] in SCENE_HASHES:
        EXPECTED[entry['scene_file']] = SCENE_HASHES[entry['legacy_id']]
for name, expected in EXPECTED.items():
    if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
        raise SystemExit('Inspected source changed; refusing to overwrite: ' + name)


def replace(path, old, new):
    target = ROOT / path
    text = target.read_text()
    if text.count(old) != 1:
        raise ValueError('Changed edit anchor: ' + path + ': ' + repr(old[:60]))
    target.write_text(text.replace(old, new, 1))


for entry in entries:
    if entry['legacy_id'] not in SCENE_HASHES:
        continue
    target = ROOT / entry['scene_file']
    text = target.read_text()
    if 'pause_after=' in text or 'hold=6)' not in text:
        raise ValueError('Unexpected self-check source: ' + entry['lesson_id'])
    before, after = text.rsplit('hold=6)', 1)
    target.write_text(before + 'hold=6, pause_after=6)' + after)

path = 'scripts/render_syllabus_expansion.py'
replace(path, 'import ast\n', '')
replace(path, 'import re\n', '')
replace(path, 'ROOT = Path(__file__).resolve().parents[1]\n', "ROOT = Path(__file__).resolve().parents[1]\nsys.path.insert(0, str(ROOT))\nfrom tools.course_timing import (  # noqa: E402\n    assess_duration, load_duration_policy, seconds, validate_timing_records,\n)\n")
replace(path, "'tools/branding.py', 'assets/branding/uqam_logo.png', 'pyproject.toml')", "'tools/branding.py', 'assets/branding/uqam_logo.png', 'pyproject.toml',\n          'tools/course_timing.py', 'curriculum/duration_policy.yaml')")
replace(path, "    if len(video) != 1 or float(info.get('format', {}).get('duration', 0)) <= 0:\n", "    duration = seconds(info.get('format', {}).get('duration'))\n    if len(video) != 1:\n")
replace(path, "    return float(info['format']['duration']), bool(audio)", '    return duration, bool(audio)')
replace(path, "    env['PYTHONPATH'] = str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')", "    env['PYTHONPATH'] = str(ROOT) + os.pathsep + env.get('PYTHONPATH', '')\n    env['TEACHING_TIMING_PATH'] = str((dest / 'teaching_timing.json').resolve())\n    result['shared_sha256'] = {name: digest(ROOT / name) for name in SHARED}")
replace(path, '        duration, has_audio = inspect_streams(info, mode)', '''        duration, has_audio = inspect_streams(info, mode)
        result['duration_review'] = assess_duration(
            duration, mode=label, has_audio=has_audio, policy=load_duration_policy())
        if result['duration_review']['status'] == 'outside_range':
            raise RuntimeError('Narrated duration is outside the documented course range.')
        timing_file = dest / 'teaching_timing.json'
        result['pacing_review'] = {'status': 'not_instrumented', 'records': 0}
        if timing_file.is_file():
            records = json.loads(timing_file.read_text(encoding='utf-8'))
            errors = validate_timing_records(records, mode=label)
            if records and float(records[-1]['end']) > duration + 0.10:
                errors.append('Recorded timing exceeds the encoded video duration.')
            result['pacing_review'] = {'status': 'failed' if errors else 'recorded',
                                      'records': len(records), 'errors': errors,
                                      'mode': label}
            if errors:
                raise RuntimeError('; '.join(errors))''')

path = 'scripts/render_curriculum.py'
replace(path, 'from tools.course_catalog import load_catalog  # noqa: E402\n', 'from tools.course_catalog import load_catalog  # noqa: E402\nfrom tools.course_timing import assess_duration, load_duration_policy, seconds  # noqa: E402\n')
replace(path, '        duration = float(metadata.get("format", {}).get("duration", 0))\n        if duration <= 0:\n            errors.append("duration is not positive")', '''        duration = seconds(metadata.get("format", {}).get("duration"))
        if require_audio and audio_streams:
            timing = assess_duration(duration, mode="azure_review", has_audio=True,
                                     policy=load_duration_policy())
            if timing["status"] == "outside_range":
                errors.append("narrated duration is outside the documented course range")''')

path = 'scripts/course_audit.py'
replace(path, "'tests/test_public_audit.py', 'tests/test_public_workflow_policy.py', 'tools/video_audit/tests',", "'tests/test_public_audit.py', 'tests/test_public_workflow_policy.py', 'tools/video_audit/tests',\n        'tests/test_course_timing.py', 'tests/test_course_boundaries.py', 'tests/test_course_visual_followup.py',")
replace(path, "              'publication': False, 'release_ready': False, 'listening': 'not_performed'}", "              'publication': False, 'release_ready': False, 'listening': 'not_performed',\n              'narrated_duration_review': 'not_assessable_from_silent_preview'}")

replace('docs/TEACHING_STANDARD.md', '## One UQAM opening\n', '''## Duration and pacing

Narration remains the pacing reference from `AGENT.md`, section 6. Course videos
need consistent teaching depth and reading time, not identical elapsed lengths.
The inspected course guides and syllabus do **not** specify a numeric minimum or
maximum. `curriculum/duration_policy.yaml` records that missing numeric target
explicitly; a promotion's 20 seconds, 60–90 seconds or 4:43 must not be borrowed.
A future numeric range must cite the owner's agreed source before it is enforced.

In `TeachingScene.explain`, `hold` is the minimum time for fully revealed content
in both silent and narrated modes. Narrated execution waits for the real speech
context to finish. `pause_after` is a separate, intentional reflection interval
after that context. The ten syllabus self-checks retain their originally authored
six-second thinking interval after the spoken question, before its answer.
Do not replace these rules with a global speed factor, clipped speech, duplicated
explanations or blank padding added merely to reach a target duration.

Silent previews keep their accelerated structural timing. Their runtime cannot
certify a narrated lesson's length. The review runner records the encoded length,
audio mode, source/service hashes and, for shared teaching scenes, the actual
explanation clock in `teaching_timing.json`. Duration, speech/visual synchronization,
full-motion readability and listening are distinct review results. A numeric
range check, even when configured, cannot establish the other results.

## One UQAM opening
''')
Path('/tmp/course_timing_changed.json').write_text(json.dumps(list(EXPECTED)))
print('Applied only the inspected source edits:', len(EXPECTED))
