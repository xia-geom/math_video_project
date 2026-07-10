from pathlib import Path

from tools.video_audit.source import (
    count_animation_calls,
    has_class,
    has_final_wait,
    has_plain_caption_source,
    has_ssml_narration,
    load_source,
)


def test_load_source_extracts_bookmarks_waits_and_captions(tmp_path: Path) -> None:
    scene = tmp_path / "scene.py"
    scene.write_text(
        '''
class DemoScene:
    pass

script = [{
    "caption": "Court sous-titre",
    "ssml": "<bookmark mark='start'/> Bonjour"
}]

def render(self):
    self.wait_until_bookmark("start")
''',
        encoding="utf-8",
    )

    info = load_source(scene)

    assert has_class(info, "DemoScene")
    assert info.bookmarks == ["start"]
    assert info.waits == ["start"]
    assert info.captions == [("Court sous-titre", 6)]


def test_source_helpers_accept_repo_narration_patterns(tmp_path: Path) -> None:
    scene = tmp_path / "scene.py"
    scene.write_text(
        '''
import tools.tts as tts
ssml = tts.ssml

class DemoScene:
    def narrated(self, text):
        with self.voiceover(text=ssml(text), subcaption=tts.strip_ssml(text)):
            pass

    def construct(self):
        self.play_paced(None, run_time=1.0)
        self.wait_paced(2.0)
''',
        encoding="utf-8",
    )

    info = load_source(scene)

    assert has_plain_caption_source(info)
    assert has_ssml_narration(info)
    assert count_animation_calls(info) == 1
    assert has_final_wait(info)
