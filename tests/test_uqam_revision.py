"""Regression checks for the September UQAM revision, including real pixels."""
from __future__ import annotations
import importlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
LONG = ROOT / "miscellaneous/uqam-baccalaureat-mathematiques-cheminements"
SHORT = ROOT / "miscellaneous/bac_math_uqam_fr"
sys.path.insert(0, str(LONG))
sys.path.insert(0, str(SHORT))

from tools.uqam_video_review import contrast_ratio, crop_box, photo_credit_inventory, review_times, validate_subtitles
import program_data
import program_data_v4 as data
import render_v4 as render
import v4_photos
import v4_storyboard_data as storyboard
import v4_visuals
import bac_math_uqam_fr_scene as promo
import build_release as release


def test_four_grids_have_attributed_120_cells():
    assert {p['source_page'] for p in data.PROGRAMS.values()} == {9, 13, 18, 22}
    courses = [c for p in data.PROGRAMS.values() for semester in p['semesters'] for c in semester]
    assert len(courses) == 120
    assert all(c.source_version == '2026-07-24' and c.official_titles for c in courses)
    assert all(c.codes or c.kind == 'block' for c in courses)


def test_current_corrections_do_not_mutate_historical_data():
    assert program_data.PROGRAMS['math']['semesters'][3][3].title == 'Formes différentielles'
    assert data.PROGRAMS['math']['semesters'][3][3].codes == ('MAT2411',)
    assert data.PROGRAMS['stat']['semesters'][1][2].kind == 'block'
    assert data.PROGRAMS['stat']['semesters'][3][3].codes == ('MAT1260',)
    geometry = next(s for s in storyboard.BRANCH_SEGMENTS['v4_06_fundamental_mathematics'] if s.id == 'geometry')
    analysis = next(s for s in storyboard.BRANCH_SEGMENTS['v4_06_fundamental_mathematics'] if s.id == 'analysis')
    assert (3, 3) not in [(c.row, c.column) for c in geometry.courses]
    assert (3, 3) in [(c.row, c.column) for c in analysis.courses]


def test_intro_variants_and_option_context_are_explicit():
    for key in ('info_math', 'info_stat'):
        cell = data.PROGRAMS[key]['semesters'][0][4]
        assert cell.kind == 'alternative' and 'INF1120' in cell.codes
    assert data.PROGRAMS['info_stat']['semesters'][5][0].kind == 'block_selection'


def test_all_pinned_v4_assets_and_guide_hashes():
    for path, expected, label in render._static_hash_checks():
        assert path.is_file(), label
        assert render.sha256_file(path) == expected, label
    assert render.V4['source']['course_map_source_year'] == '2026–2027'
    assert v4_visuals.GUIDE_COVER_PATH.name == 'uqam-guide-cover-2026-2027.png'


def test_authorial_clock_and_voice_profiles_are_preserved():
    runtimes = render.build_runtimes()
    assert len(runtimes) == 11
    assert sum(r.duration for r in runtimes) == 283
    assert runtimes[0].duration == 15
    assert runtimes[-1].duration == 22
    assert render.V4_NARRATION['voice'] == 'fr-CA-SylvieNeural'
    assert render.V4_NARRATION['rate'] == '-10%'
    assert promo.PROMO_VOICE == release.MAI_VOICE_2


@pytest.mark.parametrize('focal', [(0,0), (0.5,0.5), (1,1)])
def test_cover_crop_preserves_bounds_and_aspect(focal):
    left, top, right, bottom = crop_box((2560,1706), (1920,1080), focal)
    assert 0 <= left < right <= 2560
    assert 0 <= top < bottom <= 1706
    assert abs((right-left)/(bottom-top)-16/9) < 0.002


@pytest.mark.parametrize('focal', [(-1,0), (1.1,0), (float('nan'),0)])
def test_cover_crop_rejects_invalid_focus(focal):
    with pytest.raises(ValueError):
        crop_box((2560,1706), (1920,1080), focal)


def test_v4_photo_crossfade_is_not_frozen_by_frame_cache():
    render.configure_render_profile('720p30', artifact_tag='ci-review')
    runtime = render.build_runtimes()[0]
    frame = render.make_frame(runtime)
    end = render.aligned_actions(runtime)['photo_intro'][1]
    first = frame(0.5)
    transition = frame(end-0.2)
    after = frame(end+0.2)
    assert first.shape == (720,1280,3)
    assert not np.array_equal(first, transition)
    assert not np.array_equal(transition, after)
    assert np.array_equal(after, v4_visuals.draw_scene(runtime.spec.id, end+0.2, runtime.duration, render.aligned_actions(runtime)))
    render.configure_render_profile('720p30')


def test_photographic_end_follows_real_cue_start():
    runtime = render.build_runtimes()[0]
    runtime.metadata = {'cues':[{'start_ticks_100ns':int(t*10_000_000)} for t in (0.35,7.25,10.5)]}
    assert render.aligned_actions(runtime)['photo_intro'][1] == 7.25


def test_small_copy_and_credit_panels_have_contrast():
    assert contrast_ratio(promo.MID_GREY, '#FFFFFF') >= 4.5
    assert contrast_ratio('#18212B', '#FFFFFF') >= 7


def test_parent_and_child_use_the_same_custom_configuration(monkeypatch):
    monkeypatch.setattr(release, 'PROMO_RATE', '-3%')
    monkeypatch.setattr(release, 'CTA_URL', 'https://math.uqam.ca/programmes/premier-cycle/')
    monkeypatch.setattr(release, 'CTA_DISPLAY', 'math.uqam.ca')
    monkeypatch.setattr(release, 'configure_azure_speech_environment', lambda _: release.MAI_VOICE_2_REGION)
    environment = release.prepare_render_environment()
    assert environment['UQAM_PROMO_RATE'] == release.PROMO_RATE
    assert environment['UQAM_PROMO_CTA_URL'] == release.CTA_URL
    assert environment['UQAM_PROMO_CTA_DISPLAY'] == release.CTA_DISPLAY
    code = 'import bac_math_uqam_fr_scene as s; import json; print(json.dumps([s.PROMO_RATE,s.CTA_URL,s.CTA_DISPLAY]))'
    environment['PYTHONPATH'] = str(ROOT) + ':' + str(SHORT)
    output = subprocess.check_output([sys.executable, '-c', code], env=environment, text=True, cwd=ROOT)
    assert json.loads(output.strip().splitlines()[-1]) == [release.PROMO_RATE, release.CTA_URL, release.CTA_DISPLAY]


def test_photo_credit_inventory_is_per_asset_and_not_blanket_approval():
    assets = {'assets':[{'kind':'image','filename':'pk.jpg','credit':'Photo UQAM','rights_status':'source policy'}]}
    shots = [{'filename':'pk.jpg','start':0,'end':6,'displayed_credit':'Photo UQAM'}]
    record = photo_credit_inventory(assets,shots)[0]
    assert record['occurrences'][0]['displayed_credit'] == record['expected_credit']
    assert record['institutional_approval'] == 'not inferred'
    assert len(review_times(shots,10)) >= 5


@pytest.mark.parametrize('body', [
    '2\n00:00:00,000 --> 00:00:01,000\nBonjour.\n',
    '1\n00:61:00,000 --> 00:61:02,000\nBonjour.\n',
    '1\n00:00:00,000 --> 00:00:02,000\n<break/>Bonjour.\n',
    '1\n00:00:02,000 --> 00:00:01,000\nBonjour.\n',
    '1\n00:00:00,000 --> 00:00:02,000\n\n',
])
def test_subtitle_negative_cases(tmp_path, body):
    path = tmp_path/'bad.srt'
    path.write_text(body)
    with pytest.raises(RuntimeError):
        validate_subtitles(path, 10)


def test_fast_subtitles_are_flagged_not_certified(tmp_path):
    path = tmp_path/'fast.srt'
    path.write_text('1\n00:00:00,000 --> 00:00:00,200\nUne phrase à relire.\n')
    result = validate_subtitles(path, 2)
    assert result['reading_warnings'][0]['issue'] == 'reading_speed'
    assert result['human_review'] == 'pending'


def test_music_fails_explicitly_if_future_duration_exceeds_coverage(monkeypatch):
    monkeypatch.setattr(render, 'TARGET_DURATION', 400)
    with pytest.raises(RuntimeError, match='Music coverage'):
        render.background_music_filter()
