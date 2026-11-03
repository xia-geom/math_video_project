"""Render actual source visuals on explicit test clocks, without audio.

Review filenames, metadata and contact sheets distinguish these from released
masters. No TTS credentials, substitute voice or network calls are used here.
"""
from __future__ import annotations

# Local renderers require the repository and project import paths below.
# ruff: noqa: E402
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LONG = ROOT / 'miscellaneous/uqam-baccalaureat-mathematiques-cheminements'
SHORT = ROOT / 'miscellaneous/bac_math_uqam_fr'
OUT = ROOT / 'review_artifacts/uqam'
for directory in (ROOT, LONG, SHORT):
    sys.path.insert(0, str(directory))
import render_v4 as v4

from miscellaneous.bac_math_uqam_fr.review import build_visual_preview
from tools.uqam_video_review import review_times


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))


def extract(path, times, destination):
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    duration = float(probe(path)['format']['duration'])
    for i, timestamp in enumerate(sorted(set(times))):
        timestamp = min(max(timestamp, 0), duration - 0.1)
        image = destination / f'{i:03d}_{timestamp:07.3f}.jpg'
        subprocess.run(['ffmpeg','-y','-v','error','-ss',str(timestamp),'-i',str(path),'-frames:v','1','-q:v','2',str(image)], check=True)
        with Image.open(image) as im:
            if im.size not in ((1280,720),(1920,1080)):
                raise RuntimeError('Unexpected encoded frame dimensions')
        records.append({'time':timestamp,'path':str(image.relative_to(OUT)), 'sha256':hashlib.sha256(image.read_bytes()).hexdigest()})
    return records


def contact(records, name):
    font = ImageFont.truetype(str(LONG/'assets/fonts/NotoSans-Regular.ttf'), 14)
    for offset in range(0,len(records),12):
        batch = records[offset:offset+12]
        board = Image.new('RGB',(960, ((len(batch)+2)//3)*208),'white')
        draw = ImageDraw.Draw(board)
        for i, row in enumerate(batch):
            with Image.open(OUT/row['path']) as source:
                thumb = source.copy()
                thumb.thumbnail((312,176))
                x,y = (i%3)*320,(i//3)*208
                board.paste(thumb,(x+4,y))
                draw.text((x+4,y+179),f"{row['time']:.3f} s — visual-only",font=font,fill='black')
        board.save(OUT/f'{name}_{offset//12:02d}.jpg',quality=88)


def long_review():
    v4.configure_render_profile('720p30',artifact_tag='ci-review')
    runtimes = v4.build_runtimes()
    video = OUT/'v4_VISUAL_ONLY_283s_720p30.mp4'
    pipe = subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','30','-i','-','-an','-c:v','libx264','-preset','ultrafast','-crf','23','-pix_fmt','yuv420p',str(video)],stdin=subprocess.PIPE)
    times, rendered_frames = [], 0
    try:
        for runtime in runtimes:
            frame = v4.make_frame(runtime)
            windows = v4.aligned_actions(runtime)
            local = {0.5, runtime.duration/2, runtime.duration-0.5}
            for start,end in windows.values():
                for timestamp in (start-1/30,start,start+1/30,end-1/30,end,end+1/30):
                    if 0 <= timestamp < runtime.duration:
                        local.add(timestamp)
            times.extend(runtime.spec.start+t for t in sorted(local))
            count = round(runtime.duration*30)
            for i in range(count):
                pipe.stdin.write(frame(i/30).tobytes())
                rendered_frames += 1
            print(f'V4_RENDERED {runtime.spec.id} {count} frames', flush=True)
    finally:
        pipe.stdin.close()
    if pipe.wait() != 0 or rendered_frames != 8490:
        raise RuntimeError('V4 visual-only encode failed or wrong frame count')
    metadata = probe(video)
    if abs(float(metadata['format']['duration'])-283) > 0.04:
        raise RuntimeError('V4 encoded timeline differs from 283 seconds')
    key = [0.5,5.4,5.8,6.1,261.5,266.4,266.8,267.1,281.5,282.5]
    records = extract(video, times[::3]+key, OUT/'v4_encoded_frames')
    contact(records,'v4_contact')
    (OUT/'v4_review.json').write_text(json.dumps({'mode':'visual_only_no_audio','frame_count':rendered_frames,'probe':metadata,'all_transition_times':times,'sampled_encoded_frames':records},indent=2))


def short_review():
    report = build_visual_preview(OUT / 'short', 'qh')
    timeline = json.loads((OUT / 'short/timeline.json').read_text())
    city = next(a for a in timeline['acts'] if a['act'] == 'montreal')
    science_complex = next(s for s in timeline['shots'] if s['filename'] == 'president_kennedy_no_vehicles.png' and s['start'] >= city['start'] - 0.01)
    assert science_complex['end'] - science_complex['start'] >= 9.0, 'Science-complex photo left before the fixture speech unit ended'
    research = next(s for s in timeline['states'] if s['state'] == 'research_cards')
    units = [u for u in timeline['speech_units'] if u['segment'] == 'research' and u['index'] > 0]
    assert len(units) == 3 and research['end'] - research['start'] >= 12
    assert all(research['start'] <= u['speech_end'] <= research['end'] for u in units)
    path = OUT / 'short/bac_math_uqam_fr_silent_preview.mp4'
    duration = float(probe(path)['format']['duration'])
    records = extract(path, review_times(timeline['shots'], duration, 60), OUT / 'short_encoded_frames')
    contact(records, 'short_contact')
    report['sampled_encoded_frames'] = records
    (OUT / 'short_review.json').write_text(json.dumps(report, indent=2))


def source_snapshot():
    sources = [*LONG.glob('*.py'), *SHORT.glob('*.py'), *LONG.glob('*.toml'), *LONG.glob('voiceover*.txt'), *LONG.glob('tests/*.py'), *ROOT.glob('tests/test_uqam*.py'), ROOT/'tools/uqam_video_review.py', Path(__file__)]
    for source in sources:
        target = OUT/'source_snapshot'/source.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(source,target)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    source_snapshot()
    status = {'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), 'visual_only_render':'running','real_narration':'not run by this script','listening':'pending','institutional_approval':'not inferred'}
    (OUT/'STATUS.json').write_text(json.dumps(status,indent=2))
    long_review()
    native = OUT / 'native_v4_frames'
    native.mkdir(exist_ok=True)
    v4.configure_render_profile('1080p60', artifact_tag='ci-native-review')
    for runtime in v4.build_runtimes():
        for index, timestamp in enumerate((0.5,runtime.duration/2,runtime.duration-0.5)):
            pixels = v4.make_frame(runtime)(timestamp)
            assert pixels.shape == (1080,1920,3)
            Image.fromarray(pixels).save(native/f'{runtime.spec.id}_{index}.jpg',quality=92)
    v4.configure_render_profile('720p30',artifact_tag='ci-review')
    short_review()
    status['visual_only_render'] = 'passed'
    status['native_1080p_frames'] = 33
    status['encoded_frame_sampling'] = 'passed automated extraction; manual inspection pending'
    (OUT/'STATUS.json').write_text(json.dumps(status,indent=2))
    print('REVIEW_ARTIFACTS',OUT,flush=True)


if __name__ == '__main__':
    main()
