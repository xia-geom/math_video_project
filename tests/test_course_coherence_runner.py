"""Keep silent course review scheduling within the documented render limit."""
from unittest.mock import MagicMock, Mock

import pytest

from scripts import render_course_coherence as runner


@pytest.mark.parametrize(('arguments', 'workers'), [([], 2), (['--jobs', '1'], 1),
                                                  (['--jobs', '2'], 2)])
def test_render_pool_uses_allowed_concurrency(tmp_path, monkeypatch, arguments, workers):
    output = tmp_path / 'review_artifacts' / 'attempt'
    entries = [{'order': number, 'lesson_id': f'lesson_{number}'} for number in range(1, 4)]
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    monkeypatch.setattr(runner, 'load_catalog', lambda: ({}, entries))
    monkeypatch.setattr(runner.sys, 'argv', ['render_course_coherence.py', '--output',
                                          str(output), *arguments])
    executor = MagicMock()
    executor.return_value.__enter__.return_value.map.side_effect = (
        lambda function, selected: map(function, selected)
    )
    monkeypatch.setattr(runner, 'ThreadPoolExecutor', executor)
    launch = Mock(return_value=Mock(returncode=0))
    monkeypatch.setattr(runner.subprocess, 'run', launch)

    assert runner.main() == 0

    executor.assert_called_once_with(max_workers=workers)
    assert launch.call_count == len(entries)
    assert [call.args[0][-1] for call in launch.call_args_list] == [
        entry['lesson_id'] for entry in entries
    ]
    assert all(call.kwargs['cwd'] == tmp_path for call in launch.call_args_list)
    assert sorted(path.name for path in output.iterdir()) == ['01', '02', '03']


@pytest.mark.parametrize('jobs', ['0', '3', '4'])
def test_invalid_concurrency_is_rejected_before_rendering(tmp_path, monkeypatch, capsys, jobs):
    output = tmp_path / 'review_artifacts' / 'attempt'
    monkeypatch.setattr(runner, 'ROOT', tmp_path)
    monkeypatch.setattr(runner.sys, 'argv', ['render_course_coherence.py', '--output',
                                          str(output), '--jobs', jobs])
    catalogue = Mock()
    executor = Mock()
    launch = Mock()
    monkeypatch.setattr(runner, 'load_catalog', catalogue)
    monkeypatch.setattr(runner, 'ThreadPoolExecutor', executor)
    monkeypatch.setattr(runner.subprocess, 'run', launch)

    with pytest.raises(SystemExit) as error:
        runner.main()

    assert error.value.code == 2
    assert 'invalid choice' in capsys.readouterr().err
    catalogue.assert_not_called()
    executor.assert_not_called()
    launch.assert_not_called()
    assert not output.exists()
