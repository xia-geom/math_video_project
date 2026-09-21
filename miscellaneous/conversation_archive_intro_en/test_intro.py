"""Product claims, timing and build boundaries; no paid service or personal data."""
import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("archive_intro_build", HERE / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class ProductIntroTests(unittest.TestCase):
    def test_english_silent_timeline(self):
        story = build.story()
        self.assertEqual(story["language"], "en")
        self.assertEqual(story["mode"], "silent_captioned_preview")
        self.assertEqual(sum(b["seconds"] for b in story["beats"]), 70)

    def test_scene_has_every_authored_beat(self):
        tree = ast.parse((HERE / "conversation_archive_intro_en_scene.py").read_text())
        scene = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        methods = {n.name for n in scene.body if isinstance(n, ast.FunctionDef)}
        self.assertTrue({"beat_" + b["id"] for b in build.story()["beats"]} <= methods)

    def test_storage_roadmap_is_not_a_release_claim(self):
        beat = build.story()["beats"][5]
        self.assertEqual(beat["claim_status"], "target_not_shipped_in_source_commit")
        source = (HERE / "conversation_archive_intro_en_scene.py").read_text()
        self.assertIn("TARGET ARCHITECTURE", source)
        self.assertIn("not yet shipped in this baseline", source)

    def test_subtitles_end_at_seventy_seconds(self):
        captions, transcript = build.accessibility(build.story())
        self.assertIn("00:01:00,000 --> 00:01:10,000", captions)
        self.assertEqual(captions.count(" --> "), 7)
        self.assertIn("without waiting", transcript)

    def test_no_voice_or_network_fallback(self):
        tree = ast.parse((HERE / "conversation_archive_intro_en_scene.py").read_text())
        imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        self.assertIn("manim", imports)
        self.assertFalse(any("azure" in name or "voiceover" in name for name in imports))

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "existing"
            path.mkdir()
            (path / "keep.txt").write_text("keep")
            with self.assertRaises(FileExistsError), patch.object(build.subprocess, "run") as run:
                build.build(path)
            run.assert_not_called()
            self.assertEqual((path / "keep.txt").read_text(), "keep")

    def test_content_check_does_not_render(self):
        with patch.object(build.subprocess, "run") as run, patch("builtins.print"):
            self.assertEqual(build.main(["--check"]), 0)
        run.assert_not_called()

    def test_invalid_quality_rejected(self):
        with self.assertRaises(ValueError):
            build.build(Path("never-created"), "invalid")

    def test_video_probe_rejects_accidental_audio(self):
        payload = {"streams": [{"codec_type": "video"}, {"codec_type": "audio"}], "format": {"duration": "70"}}
        with patch.object(build.subprocess, "run") as run:
            run.return_value.stdout = json.dumps(payload)
            with self.assertRaises(ValueError):
                build.inspect_video(Path("invented.mp4"), "ql", 70)

    def test_caption_reading_budget(self):
        for beat in build.story()["beats"]:
            self.assertLessEqual(len(beat["caption"].split()) / beat["seconds"], 3.5)


if __name__ == "__main__":
    unittest.main()
