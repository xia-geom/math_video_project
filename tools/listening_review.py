"""Prepare local listening evidence and validate human decisions against exact media.

No screening result or flag decision passes a course-ledger listening check.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
from datetime import datetime
from pathlib import Path

HASH = re.compile(r'^[0-9a-f]{64}$')
LESSON = re.compile(r'^[a-z0-9_]+$')
FLAG_DISPOSITIONS = {'intentional_pause', 'audio_defect', 'needs_more_review'}
VIDEO_DISPOSITIONS = {'no_issue_observed', 'issues_observed', 'needs_more_review'}
HISTORICAL_NOTICE = (
    'Historical audio from the October 13 review, screened October 15. '
    'It predates later wording changes. These files are not current-source approval.'
)


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':')).encode()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def screen_report(path, expected_hash):
    require(isinstance(expected_hash, str) and bool(HASH.fullmatch(expected_hash)),
            'An authoritative report SHA-256 is required.')
    require(digest(path) == expected_hash, 'The authoritative screening report changed.')
    report = json.loads(Path(path).read_text(encoding='utf-8'))
    require(isinstance(report.get('flags'), list) and isinstance(report.get('videos'), list),
            'Screening report lacks flag/video records.')
    return report


def finite_seconds(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def records(report, report_hash, lessons):
    require(isinstance(lessons, list) and bool(lessons) and len(lessons) == len(set(lessons))
            and all(isinstance(name, str) and LESSON.fullmatch(name) for name in lessons),
            'Select distinct stable lesson IDs.')
    videos = {}
    for row in report['videos']:
        name = row['lesson_id']
        require(name not in videos, 'Duplicate lesson in screening video records.')
        videos[name] = row
    require(set(lessons) <= videos.keys(), 'A selected lesson is absent from the report.')
    selected_videos, flags, candidates = [], [], {}
    for name in lessons:
        video = videos[name]
        video_hash = video['video_sha256']
        require(bool(HASH.fullmatch(video_hash)), 'Invalid video digest.')
        binding = {'lesson_id': name, 'video_sha256': video_hash, 'report_sha256': report_hash}
        video_id = identity(binding)
        copied = f'media/video/{name}_{video_hash}.mp4'
        selected_videos.append({'video_id': video_id, 'binding': binding,
                                'title': video.get('title', name), 'file': copied})
        candidates[copied] = {'sha256': video_hash, 'kind': 'video', 'paths': [video['video_path']]}
    for flag in report['flags']:
        name = flag['lesson_id']
        if name not in lessons:
            continue
        video = videos[name]
        require(flag['video_sha256'] == video['video_sha256'], 'Flag/video identity disagreement.')
        require(type(flag['voiceover_index']) is int and flag['voiceover_index'] >= 0,
                'Invalid voiceover index.')
        require(bool(HASH.fullmatch(flag['audio_sha256'])), 'Invalid audio digest.')
        require(all(finite_seconds(flag.get(key)) for key in (
            'start_seconds', 'end_seconds', 'clip_duration_seconds',
            'video_start_seconds', 'video_end_seconds')),
            'Intervals must contain finite nonnegative seconds.')
        require(flag['start_seconds'] < flag['end_seconds'] <= flag['clip_duration_seconds'] + 0.001,
                'Flag interval is outside its unchanged audio clip.')
        require(flag['video_start_seconds'] < flag['video_end_seconds'], 'Invalid video interval.')
        paths = flag.get('audio_paths')
        require(isinstance(paths, list) and paths and all(isinstance(p, str) for p in paths),
                'Flag has no original audio paths.')
        suffix = Path(paths[0]).suffix.lower()
        require(suffix in {'.mp3', '.wav', '.m4a', '.ogg'}, 'Unsupported original audio format.')
        copied = f"media/audio/{flag['audio_sha256']}{suffix}"
        binding = {key: flag[key] for key in (
            'lesson_id', 'video_sha256', 'audio_sha256', 'voiceover_index',
            'start_seconds', 'end_seconds', 'video_start_seconds', 'video_end_seconds')}
        binding['report_sha256'] = report_hash
        flags.append({'flag_id': identity(binding), 'binding': binding,
                      'plain_text': flag.get('plain_text', ''), 'audio_file': copied,
                      'video_id': next(v['video_id'] for v in selected_videos if v['binding']['lesson_id'] == name),
                      'screening_flags': flag.get('flags', [])})
        candidate = candidates.setdefault(copied, {'sha256': flag['audio_sha256'],
                                                    'kind': 'audio', 'paths': []})
        candidate['paths'] = sorted(set(candidate['paths']) | set(paths))
    require(len({flag['flag_id'] for flag in flags}) == len(flags), 'Duplicate screening flag identity.')
    require(bool(flags), 'Selected lessons have no screening flags.')
    return selected_videos, flags, candidates


def local_member(folder, name):
    require(isinstance(name, str) and not Path(name).is_absolute() and '..' not in Path(name).parts,
            'Queue member must be a relative path.')
    path = Path(folder) / name
    require(path.resolve().is_relative_to(Path(folder).resolve()) and not path.is_symlink(),
            'Queue member cannot escape the package or be a symlink.')
    return path


def prepare_queue(report_path, expected_hash, output, lessons):
    report_path, output = Path(report_path).resolve(), Path(output)
    require(not output.exists(), 'Use a new queue directory; existing evidence is never overwritten.')
    report = screen_report(report_path, expected_hash)
    videos, flags, candidates = records(report, expected_hash, lessons)
    media = {}
    for name, item in candidates.items():
        sources = [Path(p).resolve() for p in item['paths'] if Path(p).is_file()]
        source = next((p for p in sources if digest(p) == item['sha256']), None)
        require(source is not None, 'Original selected media is missing or changed; no queue created.')
        media[name] = {'sha256': item['sha256'], 'kind': item['kind'], 'source_path': str(source)}
    manifest = {'schema_version': 1, 'report_sha256': expected_hash,
                'source_report': str(report_path), 'report_file': 'screen-report.json',
                'lesson_ids': lessons, 'notice': HISTORICAL_NOTICE,
                'videos': videos, 'flags': flags, 'media': media,
                'listening': 'not_performed', 'release_ready': False}
    manifest['queue_id'] = identity(manifest)
    output.mkdir(parents=True)
    shutil.copyfile(report_path, output / manifest['report_file'])
    for name, item in media.items():
        target = local_member(output, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item['source_path'], target)
        require(digest(target) == item['sha256'] and digest(item['source_path']) == item['sha256'],
                'Media changed during copying; discard the incomplete queue.')
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (output / 'index.html').write_text(review_html(manifest), encoding='utf-8')
    validate_queue(output, expected_hash)
    for path in output.rglob('*'):
        if path.is_file():
            path.chmod(0o444)
    return manifest


def validate_queue(folder, expected_hash):
    folder = Path(folder)
    manifest = json.loads(local_member(folder, 'manifest.json').read_text(encoding='utf-8'))
    require(manifest.get('schema_version') == 1 and manifest.get('report_sha256') == expected_hash,
            'Queue does not belong to the authoritative report.')
    require(manifest.get('notice') == HISTORICAL_NOTICE and manifest.get('listening') == 'not_performed'
            and manifest.get('release_ready') is False, 'Queue must retain its historical, unreviewed boundary.')
    core = {key: value for key, value in manifest.items() if key != 'queue_id'}
    require(identity(core) == manifest.get('queue_id'), 'Queue manifest identity changed.')
    report = screen_report(manifest['source_report'], expected_hash)
    screen_report(local_member(folder, manifest['report_file']), expected_hash)
    videos, flags, candidates = records(report, expected_hash, manifest['lesson_ids'])
    require(manifest['videos'] == videos and manifest['flags'] == flags,
            'Queue records differ from the authoritative screening identities.')
    require(set(manifest['media']) == set(candidates), 'Queue media coverage changed.')
    for name, expected in candidates.items():
        stored = manifest['media'][name]
        original = Path(stored['source_path']).resolve()
        require(str(original) in {str(Path(p).resolve()) for p in expected['paths']},
                'Queue names an unrecorded original media path.')
        require(stored['sha256'] == expected['sha256'] and stored['kind'] == expected['kind'],
                'Queue media identity changed.')
        require(original.is_file() and digest(original) == expected['sha256'],
                'Original media is missing or replaced; decisions are stale.')
        copied = local_member(folder, name)
        require(copied.is_file() and digest(copied) == expected['sha256'],
                'Copied media is missing or replaced; decisions are stale.')
    require(local_member(folder, 'index.html').read_text(encoding='utf-8') == review_html(manifest),
            'Queue HTML changed; regenerate a new package from authoritative evidence.')
    return manifest


def human_record(record):
    require(all(isinstance(record.get(key), str) and record[key].strip()
                for key in ('reviewer', 'reason', 'checked_at')), 'A named reviewer, reason and date are required.')
    try:
        date = datetime.fromisoformat(record['checked_at'].replace('Z', '+00:00'))
    except ValueError as error:
        raise ValueError('Review date must be an ISO timestamp.') from error
    require(date.tzinfo is not None, 'Review timestamp must include a timezone.')


def validate_decisions(folder, decisions, expected_hash):
    manifest = validate_queue(folder, expected_hash)
    require(isinstance(decisions, dict) and decisions.get('schema_version') == 1
            and decisions.get('queue_id') == manifest['queue_id']
            and decisions.get('report_sha256') == expected_hash, 'Decisions target a different queue/report.')
    require(set(decisions) == {'schema_version', 'queue_id', 'report_sha256', 'decisions', 'full_video_reviews'},
            'Unexpected decision-document fields; no approval status may be imported.')
    flags = {row['flag_id']: row for row in manifest['flags']}
    videos = {row['video_id']: row for row in manifest['videos']}
    for field in ('decisions', 'full_video_reviews'):
        require(isinstance(decisions.get(field), list), 'Decision groups must be lists.')
    seen = set()
    for row in decisions['decisions']:
        require(isinstance(row, dict), 'Decision must be a mapping.')
        key = row.get('flag_id')
        require(isinstance(key, str) and key in flags and key not in seen, 'Unknown or duplicate flag decision.')
        seen.add(key)
        require(set(row) == {'flag_id', 'binding', 'reviewer', 'reason', 'checked_at', 'disposition', 'listened'},
                'Unexpected flag-decision fields; flags cannot record full-video approval.')
        require(row['binding'] == flags[key]['binding'], 'Flag decision binding changed.')
        require(row['listened'] is True, 'Flag decision requires actual boolean listened=true.')
        require(row['disposition'] in FLAG_DISPOSITIONS, 'Unknown flag disposition.')
        human_record(row)
    reviewed = set()
    for row in decisions['full_video_reviews']:
        require(isinstance(row, dict), 'Full-video review must be a mapping.')
        key = row.get('video_id')
        require(isinstance(key, str) and key in videos and key not in reviewed, 'Unknown or duplicate full-video review.')
        reviewed.add(key)
        require(set(row) == {'video_id', 'binding', 'reviewer', 'reason', 'checked_at', 'disposition',
                             'listened_entire_video', 'watched_entire_video'}, 'Unexpected full-video review fields.')
        require(row['binding'] == videos[key]['binding'], 'Full-video binding changed.')
        require(row['listened_entire_video'] is True and row['watched_entire_video'] is True,
                'Full-video records require separate complete listening and viewing confirmations.')
        require(row['disposition'] in VIDEO_DISPOSITIONS, 'Unknown full-video disposition.')
        human_record(row)
    return {'status': 'validated_bindings', 'flag_decisions': len(seen), 'pending_flags': len(flags) - len(seen),
            'full_video_reviews': len(reviewed), 'ledger_checks_updated': False, 'release_ready': False,
            'notice': HISTORICAL_NOTICE}


def review_html(manifest):
    """Self-contained local UI; no requests, uploads, or generated decisions."""
    visible = {key: manifest[key] for key in ('queue_id', 'report_sha256', 'notice', 'videos', 'flags')}
    payload = json.dumps(visible, ensure_ascii=False).replace('<', '\\u003c')
    return _HTML.replace('__QUEUE_DATA__', payload)


_HTML = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; media-src 'self' file:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'">
<title>Historical narration listening review</title>
<style>
body{font:16px/1.5 system-ui,sans-serif;max-width:1050px;margin:32px auto;padding:0 22px;background:#f7f6f2;color:#202522}
h1{font-size:2rem;margin-bottom:8px}h2{margin-top:35px}h3{font-size:1.1rem}.notice{padding:18px;background:#fff1d5;border-left:4px solid #926100}
section,article{background:white;border:1px solid #d7ddd8;border-radius:8px;padding:20px;margin:18px 0}article{background:#f8faf8}
video{display:block;width:100%;max-height:520px;background:#111}audio{width:100%;margin:10px 0}label{display:block;margin:12px 0}input[type=text],textarea,select{box-sizing:border-box;width:100%;font:inherit;padding:9px;border:1px solid #97a69c;border-radius:4px}textarea{min-height:80px}
button{font:inherit;padding:10px 16px;border:0;border-radius:4px;background:#23563e;color:white;cursor:pointer}.secondary{background:#e6eee8;color:#183b2b}small{overflow-wrap:anywhere;color:#55635b}#message{white-space:pre-wrap;font-weight:600}.toolbar{position:sticky;top:0;background:#f7f6f2;padding:12px 0;z-index:1;border-bottom:1px solid #ccc}
</style>
<h1>Historical narration listening review</h1><p id="notice" class="notice"></p>
<p>Listen to each unchanged utterance, use the full historical video for context, and record your own reason. Screening flags are listening candidates. Nothing is pre-approved.</p>
<label>Reviewer name<input id="reviewer" type="text" autocomplete="name"></label>
<div class="toolbar"><button id="export">Export entered decisions as JSON</button> <span id="count"></span><div id="message" role="status"></div></div>
<main id="lessons"></main>
<script>
'use strict'; const queue=__QUEUE_DATA__;
document.getElementById('notice').textContent=queue.notice;
document.getElementById('count').textContent=queue.flags.length+' flags · '+queue.videos.length+' complete historical videos';
const el=(tag,text)=>{const n=document.createElement(tag); if(text!==undefined)n.textContent=text;return n;};
function choice(options){const s=el('select');s.append(el('option','Choose a disposition'));s.firstChild.value='';for(const [value,label] of options){const o=el('option',label);o.value=value;s.append(o);}return s;}
function checkbox(label){const l=el('label');const input=el('input');input.type='checkbox';l.append(input,document.createTextNode(' '+label));return {label:l,input};}
const flagForms=[],videoForms=[];
for(const video of queue.videos){
 const section=el('section');section.append(el('h2',video.title));
 section.append(el('small','Complete historical video · SHA-256 '+video.binding.video_sha256));
 const player=el('video');player.controls=true;player.preload='metadata';player.src=video.file;section.append(player);
 for(const flag of queue.flags.filter(f=>f.video_id===video.video_id)){
  const article=el('article');const b=flag.binding;
  article.append(el('h3','Utterance '+b.voiceover_index+' · flagged audio interval '+b.start_seconds.toFixed(2)+'–'+b.end_seconds.toFixed(2)+' seconds'));
  article.append(el('p',flag.plain_text));article.append(el('small','Flag '+flag.flag_id));
  const audio=el('audio');audio.controls=true;audio.preload='metadata';audio.src=flag.audio_file;article.append(audio);
  const context=el('button','Go to interval in full video');context.className='secondary';context.type='button';context.onclick=()=>{player.currentTime=Math.max(0,b.video_start_seconds-2);player.scrollIntoView({behavior:'smooth',block:'center'});};article.append(context);
  const disposition=choice([['intentional_pause','Intentional pause'],['audio_defect','Audio defect'],['needs_more_review','Needs more review']]);
  const reason=el('textarea');reason.placeholder='Reason, including what you heard and relevant context';
  const listened=checkbox('I listened to this utterance and its flagged interval.');
  article.append(disposition,reason,listened.label);section.append(article);flagForms.push({flag,disposition,reason,listened:listened.input});
 }
 const complete=el('details');complete.append(el('summary','Separate complete-video review (optional)'));
 complete.append(el('p','Only record this after viewing and listening to the entire historical video. Flag decisions never fill this record. This does not approve current source or publication.'));
 const disposition=choice([['no_issue_observed','No issue observed in complete review'],['issues_observed','Issues observed'],['needs_more_review','Needs more review']]);
 const reason=el('textarea');reason.placeholder='Reason and observations from the complete video';
 const listened=checkbox('I listened to the entire video.');const watched=checkbox('I watched the entire video.');
 complete.append(disposition,reason,listened.label,watched.label);section.append(complete);videoForms.push({video,disposition,reason,listened:listened.input,watched:watched.input});document.getElementById('lessons').append(section);
}
document.getElementById('export').onclick=()=>{
 const message=document.getElementById('message');try{
  const reviewer=document.getElementById('reviewer').value.trim();if(!reviewer)throw Error('Enter your reviewer name.');
  const checked_at=new Date().toISOString(),decisions=[],full_video_reviews=[];
  for(const f of flagForms){if(!f.disposition.value&&!f.reason.value.trim()&&!f.listened.checked)continue;
   if(!f.disposition.value||!f.reason.value.trim()||!f.listened.checked)throw Error('Complete the disposition, reason and listening confirmation for every started flag decision.');
   decisions.push({flag_id:f.flag.flag_id,binding:f.flag.binding,reviewer,reason:f.reason.value.trim(),checked_at,disposition:f.disposition.value,listened:true});}
  for(const f of videoForms){if(!f.disposition.value&&!f.reason.value.trim()&&!f.listened.checked&&!f.watched.checked)continue;
   if(!f.disposition.value||!f.reason.value.trim()||!f.listened.checked||!f.watched.checked)throw Error('Complete both whole-video confirmations, disposition and reason for each started complete review.');
   full_video_reviews.push({video_id:f.video.video_id,binding:f.video.binding,reviewer,reason:f.reason.value.trim(),checked_at,disposition:f.disposition.value,listened_entire_video:true,watched_entire_video:true});}
  if(!decisions.length&&!full_video_reviews.length)throw Error('No decisions entered. Listen and review before exporting.');
  const result={schema_version:1,queue_id:queue.queue_id,report_sha256:queue.report_sha256,decisions,full_video_reviews};
  const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)+'\\n'],{type:'application/json'}));const a=el('a');a.href=url;a.download='listening-decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  message.textContent='Exported '+decisions.length+' flag decisions and '+full_video_reviews.length+' separate complete-video reviews. Validate the file against unchanged original and copied media.';
 }catch(error){message.textContent=error.message;}
};
</script></html>
'''
