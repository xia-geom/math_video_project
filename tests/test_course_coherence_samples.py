"""Keep reviewer evidence immutable when encoded sampling is repeated."""
import json

import pytest

from scripts import inspect_course_coherence as inspection


def test_extraction_cannot_overwrite_a_reviewed_sample_set(tmp_path, monkeypatch):
    movie = tmp_path / 'lesson.mp4'
    movie.write_bytes(b'fixture bytes; no decoding should be attempted')
    folder = tmp_path / '15'
    folder.mkdir()
    status = {'render': 'passed', 'video_path': str(movie),
              'video_sha256': inspection.sha256(movie), 'input_sha256': {}, 'duration': 10}
    (folder / 'STATUS.json').write_text(json.dumps(status))
    (folder / 'cards.json').write_text('[]')
    (folder / 'checkpoints.json').write_text('[]')
    reviewed = folder / 'sample_sets' / 'review_v1'
    reviewed.mkdir(parents=True)
    evidence = reviewed / 'sample-review.json'
    evidence.write_text('{"visual_inspection":"reviewed","finding":"keep this evidence"}')
    before = evidence.read_bytes()
    monkeypatch.setattr(inspection, 'input_hashes', lambda entry: {})

    with pytest.raises(ValueError, match='Preserve existing samples'):
        inspection.inspect(folder, {'lesson_id': 'stable-lesson', 'order': 15}, 'review_v1')

    assert evidence.read_bytes() == before
    assert sorted(p.name for p in reviewed.iterdir()) == ['sample-review.json']
