"""Public source snapshots must not collect unstaged private scratch material."""
import json
import subprocess
import zipfile
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

from scripts import course_audit
from tools import course_review

SCENE = 'scenes/algebre_fr/01_example_fr/01_example_fr_scene.py'
ENTRY = {'scene_file': SCENE}


def git(root, *arguments):
    subprocess.run(['git', '-C', str(root), *arguments], check=True, capture_output=True)


def write(root, name, content):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return path


@pytest.fixture
def repository(tmp_path, monkeypatch):
    root = tmp_path / 'repository'
    root.mkdir()
    git(root, 'init', '-q')
    write(root, 'README.md', 'Synthetic project documentation.\n')
    write(root, SCENE, 'class Example:\n    revision = 1\n')
    git(root, 'add', '--', 'README.md', SCENE)
    monkeypatch.setattr(course_audit, 'ROOT', root)
    output = root / 'review_artifacts' / 'attempt'
    output.mkdir(parents=True)
    return root, output


def test_snapshot_keeps_modified_tracked_sources_and_excludes_untracked_files(repository):
    root, output = repository
    changed = 'class Example:\n    revision = 2\n'
    write(root, SCENE, changed)
    private = write(root, 'docs/private/synthetic_notes.txt', 'Synthetic private fixture.\n')
    draft = write(root, 'docs/unrelated_draft.md', 'Unreviewed draft fixture.\n')

    course_audit.snapshot(output, [ENTRY])

    with zipfile.ZipFile(output / 'source.zip') as archive:
        assert archive.namelist() == ['README.md', SCENE]
        assert archive.read(SCENE) == changed.encode('utf-8')
    assert private.read_text() == 'Synthetic private fixture.\n'
    assert draft.read_text() == 'Unreviewed draft fixture.\n'


def test_snapshot_rejects_force_added_private_file_before_archiving(repository):
    root, output = repository
    write(root, '.gitignore', 'docs/private/\n')
    private = write(root, 'docs/private/synthetic_notes.txt', 'Synthetic private fixture.\n')
    git(root, 'add', '-f', '--', str(private.relative_to(root)))

    with pytest.raises(ValueError, match='private_data_directory'):
        course_audit.snapshot(output, [ENTRY])

    assert not (output / 'source.zip').exists()
    assert private.read_text() == 'Synthetic private fixture.\n'


@pytest.mark.parametrize('outside', [False, True])
def test_snapshot_rejects_tracked_file_symlinks(repository, tmp_path, outside):
    root, output = repository
    target_root = tmp_path if outside else root
    target = write(target_root, 'target.md', 'Synthetic link target.\n')
    link = root / 'docs' / 'linked.md'
    link.parent.mkdir()
    link.symlink_to(target)
    git(root, 'add', '--', 'docs/linked.md')

    with pytest.raises(ValueError, match='symlink'):
        course_audit.snapshot(output, [ENTRY])

    assert not (output / 'source.zip').exists()
    assert target.read_text() == 'Synthetic link target.\n'


def test_snapshot_rejects_symlink_parent_of_tracked_file(repository, tmp_path):
    root, output = repository
    write(root, 'docs/reference/guide.md', 'Tracked guide.\n')
    git(root, 'add', '--', 'docs/reference/guide.md')
    (root / 'docs/reference').rename(root / 'original_reference')
    external = tmp_path / 'external'
    target = write(external, 'guide.md', 'Synthetic external fixture.\n')
    (root / 'docs/reference').symlink_to(external, target_is_directory=True)

    with pytest.raises(ValueError, match='symlink'):
        course_audit.snapshot(output, [ENTRY])

    assert not (output / 'source.zip').exists()
    assert target.read_text() == 'Synthetic external fixture.\n'


def test_snapshot_blocks_required_untracked_dependency(repository):
    root, output = repository
    write(root, SCENE, 'from tools.required_helper import value\nclass Example: pass\n')
    helper = write(root, 'tools/required_helper.py', 'value = 1\n')

    with pytest.raises(ValueError, match='untracked:.*required_helper.py'):
        course_audit.snapshot(output, [ENTRY])

    assert not (output / 'source.zip').exists()
    assert helper.read_text() == 'value = 1\n'
    git(root, 'add', '--', 'tools/required_helper.py')
    course_audit.snapshot(output, [ENTRY])
    with zipfile.ZipFile(output / 'source.zip') as archive:
        assert archive.read('tools/required_helper.py') == b'value = 1\n'


@pytest.mark.parametrize('symlink', [False, True])
def test_untracked_import_is_rejected_before_parsing_or_hashing(repository, tmp_path,
                                                               monkeypatch, symlink):
    root, output = repository
    write(root, SCENE, 'from tools.required_helper import value\nclass Example: pass\n')
    helper = root / 'tools' / 'required_helper.py'
    helper.parent.mkdir()
    if symlink:
        target = write(tmp_path, 'outside.py', 'Synthetic private marker: invalid Python ???\n')
        helper.symlink_to(target)
    else:
        target = write(root, 'tools/required_helper.py', 'Synthetic private marker: invalid Python ???\n')
    original_read = Path.read_text
    original_hash = course_review.sha256

    def read(path, *args, **kwargs):
        assert path.resolve() != target.resolve(), 'Unreviewed input must not be parsed.'
        return original_read(path, *args, **kwargs)

    def digest(path):
        assert path.resolve() != target.resolve(), 'Unreviewed input must not be hashed.'
        return original_hash(path)

    monkeypatch.setattr(Path, 'read_text', read)
    monkeypatch.setattr(course_review, 'sha256', digest)
    with pytest.raises(ValueError, match='symlink' if symlink else 'untracked:') as error:
        course_audit.snapshot(output, [ENTRY])

    assert 'Synthetic private marker' not in str(error.value)
    assert not (output / 'source.zip').exists()


def test_untracked_data_is_rejected_before_hashing(repository, monkeypatch):
    root, output = repository
    data = write(root, 'curriculum/practice_questions.yaml', 'Synthetic unreviewed data.\n')
    original_hash = course_review.sha256

    def digest(path):
        assert path != data, 'Unreviewed data must not be hashed.'
        return original_hash(path)

    monkeypatch.setattr(course_review, 'sha256', digest)
    with pytest.raises(ValueError, match='untracked:.*practice_questions.yaml'):
        course_audit.snapshot(output, [ENTRY])

    assert not (output / 'source.zip').exists()


def test_snapshot_rejects_outside_required_source(repository, tmp_path):
    _, output = repository
    outside = write(tmp_path, 'outside.py', 'Synthetic external content.\n')

    with pytest.raises(ValueError, match='outside the repository'):
        course_audit.snapshot(output, [{'scene_file': str(outside)}])

    assert not (output / 'source.zip').exists()


def test_snapshot_preserves_existing_archive(repository):
    _, output = repository
    destination = output / 'source.zip'
    destination.write_bytes(b'Original review evidence.')

    with pytest.raises(FileExistsError):
        course_audit.snapshot(output, [ENTRY])

    assert destination.read_bytes() == b'Original review evidence.'


@pytest.mark.parametrize('symlink', [False, True])
def test_audit_stops_before_tests_or_rendering_when_snapshot_is_blocked(repository, tmp_path,
                                                                      monkeypatch, symlink):
    root, _ = repository
    output = root / 'review_artifacts' / 'blocked'
    write(root, SCENE, 'from tools.required_helper import value\nclass Example: pass\n')
    helper = root / 'tools' / 'required_helper.py'
    if symlink:
        target = write(tmp_path, 'outside.py', 'Synthetic private marker: invalid Python ???\n')
        helper.parent.mkdir()
        helper.symlink_to(target)
    else:
        write(root, 'tools/required_helper.py', 'Synthetic private marker: invalid Python ???\n')
    entry = {**ENTRY, 'lesson_id': 'example', 'order': 1}
    monkeypatch.setattr(course_audit, 'load_catalog', lambda *args, **kwargs: ({}, [entry]))
    monkeypatch.setattr(course_audit.sys, 'argv', ['course_audit.py', '--no-render',
                                                '--skip-tests', '--output', str(output)])
    for key in ('MANIM_DISABLE_VOICEOVER', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'):
        monkeypatch.setenv(key, 'initial-test-value')
    original = subprocess.check_output

    def metadata(command, *args, **kwargs):
        if command == ['git', 'rev-parse', 'HEAD']:
            return 'synthetic-base\n'
        return original(command, *args, **kwargs)

    monkeypatch.setattr(course_audit.subprocess, 'check_output', metadata)
    checks = Mock(side_effect=AssertionError('Tests must not start after a blocked snapshot.'))
    pool = Mock(side_effect=AssertionError('Construction/rendering must not start.'))
    monkeypatch.setattr(course_audit, 'run', checks)
    monkeypatch.setattr(course_audit.concurrent.futures, 'ThreadPoolExecutor', pool)

    assert course_audit.main() == 1

    status = json.loads((output / 'STATUS.json').read_text())
    assert status['source_snapshot'] == 'blocked'
    assert ('symlink' if symlink else 'untracked:') in status['reason']
    assert 'Synthetic private marker' not in status['reason']
    assert not (output / 'source.zip').exists()
    checks.assert_not_called()
    pool.assert_not_called()


@pytest.mark.parametrize('unsafe', ['tracked_symlink', 'untracked_private_scene', 'untracked_manifest'])
def test_real_catalogue_preflight_blocks_before_reading_unsafe_sources(repository, monkeypatch,
                                                                     capsys, unsafe):
    root, _ = repository
    output = root / 'review_artifacts' / 'real-loader-blocked'
    entry = {**ENTRY, 'lesson_id': 'example', 'legacy_id': 'P01', 'order': 1,
             'track': 'programme', 'module': 'Algèbre', 'title': 'Example',
             'delivery_slug': 'example_fr', 'scene_class': 'Example', 'coverage': 'Example',
             'prerequisites': [], 'requires_narration': True, 'status': 'source'}
    marker = 'Synthetic private source marker: invalid Python ???\n'
    if unsafe != 'untracked_manifest':
        target = write(root, 'scenes/private/01_example_fr/01_example_fr_scene.py', marker)
        if unsafe == 'tracked_symlink':
            (root / SCENE).rename(root / 'original_scene.py')
            (root / SCENE).symlink_to(target)
        else:
            entry['scene_file'] = target.relative_to(root).as_posix()
    manifest_name = 'curriculum/programme_principal_fr.yaml'
    manifest = write(root, manifest_name, yaml.safe_dump(
        {'version': 3, 'expected_counts': {'programme': 1}, 'entries': [entry]}))
    if unsafe == 'untracked_manifest':
        target = manifest
        manifest.write_text(marker)
    else:
        git(root, 'add', '--', manifest_name)

    original_read = Path.read_text
    original_bytes = Path.read_bytes

    def read(path, *args, **kwargs):
        assert path.resolve() != target.resolve(), 'Unsafe catalogue/source must not be parsed.'
        return original_read(path, *args, **kwargs)

    def read_bytes(path):
        assert path.resolve() != target.resolve(), 'Unsafe source must not be hashed.'
        return original_bytes(path)

    monkeypatch.setattr(Path, 'read_text', read)
    monkeypatch.setattr(Path, 'read_bytes', read_bytes)
    monkeypatch.setattr(course_audit.sys, 'argv', ['course_audit.py', '--no-render',
                                                '--skip-tests', '--output', str(output)])
    for key in ('MANIM_DISABLE_VOICEOVER', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'):
        monkeypatch.setenv(key, 'initial-test-value')
    catalogue = Mock(wraps=course_audit.load_catalog)
    checks = Mock(side_effect=AssertionError('Tests must not start after failed preflight.'))
    pool = Mock(side_effect=AssertionError('Construction/rendering must not start.'))
    monkeypatch.setattr(course_audit, 'load_catalog', catalogue)
    monkeypatch.setattr(course_audit, 'run', checks)
    monkeypatch.setattr(course_audit.concurrent.futures, 'ThreadPoolExecutor', pool)

    assert course_audit.main() == 1

    status = json.loads((output / 'STATUS.json').read_text())
    assert status['source_snapshot'] == 'blocked'
    expected = {'tracked_symlink': 'symlink', 'untracked_private_scene': 'private_data_directory',
                'untracked_manifest': 'untracked:'}[unsafe]
    assert expected in status['reason']
    assert marker.strip() not in status['reason']
    assert marker.strip() not in ''.join(capsys.readouterr())
    assert not (output / 'source.zip').exists()
    assert catalogue.call_count == (0 if unsafe == 'tracked_symlink' else 1)
    checks.assert_not_called()
    pool.assert_not_called()
