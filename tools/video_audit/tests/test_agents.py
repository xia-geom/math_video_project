from pathlib import Path

from tools.video_audit.agents import AuditContext, SourceScriptAgent
from tools.video_audit.source import load_source


def test_source_script_agent_reports_bookmarks_without_waits(tmp_path: Path) -> None:
    scene = tmp_path / "scene.py"
    scene.write_text(
        '''
from manim_voiceover import VoiceoverScene
import tools.tts as tts
from tools.branding import play_uqam_intro

script = [{
    "caption": "Court",
    "ssml": tts.ssml("<bookmark mark='draw'/> Bonjour")
}]

class DemoScene(VoiceoverScene):
    def construct(self):
        play_uqam_intro(self)
        self.set_speech_service(None)
''',
        encoding="utf-8",
    )
    context = AuditContext(
        project_root=tmp_path,
        scene_path=scene,
        scene_class="DemoScene",
        video_path=tmp_path / "demo.mp4",
        out_path=tmp_path / "audit.md",
        artifacts_dir=tmp_path / "frames",
        source=load_source(scene),
    )

    result = SourceScriptAgent().run(context)

    assert any(item.title == "Bookmarks without waits" for item in result.findings)


def test_source_script_agent_accepts_subcaption_and_manual_pacing(tmp_path: Path) -> None:
    scene = tmp_path / "scene.py"
    scene.write_text(
        '''
from manim_voiceover import VoiceoverScene
import tools.tts as tts
from tools.branding import play_uqam_intro

class DemoScene(VoiceoverScene):
    def narrated(self, text):
        with self.voiceover(text=tts.ssml(text), subcaption=tts.strip_ssml(text)):
            pass

    def construct(self):
        play_uqam_intro(self)
        with self.narrated("Bonjour"):
            self.play_paced(None, run_time=1.0)
            self.wait_paced(1.0)
''',
        encoding="utf-8",
    )
    context = AuditContext(
        project_root=tmp_path,
        scene_path=scene,
        scene_class="DemoScene",
        video_path=tmp_path / "demo.mp4",
        out_path=tmp_path / "audit.md",
        artifacts_dir=tmp_path / "frames",
        source=load_source(scene),
    )

    result = SourceScriptAgent().run(context)
    titles = {item.title for item in result.findings}

    assert "Plain captions not detected" not in titles
    assert "SSML narration not detected" not in titles
    assert "No SSML bookmarks detected" not in titles
    assert "Manual narration pacing detected" in titles
