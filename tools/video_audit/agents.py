from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from tools.video_audit import media as media_tools
from tools.video_audit import source as source_tools
from tools.video_audit.paths import canonical_video_path

SEVERITY_ORDER = {
    "blocker": 0,
    "warning": 1,
    "polish": 2,
    "info": 3,
}


@dataclass(frozen=True)
class Finding:
    agent: str
    severity: str
    category: str
    title: str
    detail: str
    fix: str
    location: str | None = None
    timestamp: str | None = None

    def sort_key(self) -> tuple[int, str, str]:
        return (SEVERITY_ORDER.get(self.severity, 99), self.agent, self.title)


@dataclass
class AuditContext:
    project_root: Path
    scene_path: Path
    scene_class: str
    video_path: Path
    out_path: Path
    artifacts_dir: Path
    silent_preview: bool = False
    metadata: dict = field(default_factory=dict)
    source: object | None = None
    media: object | None = None


@dataclass
class AgentResult:
    agent: str
    findings: list[Finding] = field(default_factory=list)


class AuditAgent(Protocol):
    name: str

    def run(self, context: AuditContext) -> AgentResult:
        ...


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def finding(
    agent: str,
    severity: str,
    category: str,
    title: str,
    detail: str,
    fix: str,
    *,
    location: str | None = None,
    timestamp: str | None = None,
) -> Finding:
    return Finding(
        agent=agent,
        severity=severity,
        category=category,
        title=title,
        detail=detail,
        fix=fix,
        location=location,
        timestamp=timestamp,
    )


class SourceScriptAgent:
    name = "SourceScriptAgent"

    def run(self, context: AuditContext) -> AgentResult:
        findings: list[Finding] = []
        source = context.source
        if source is None:
            return AgentResult(self.name, [finding(self.name, "blocker", "source", "Source not loaded", "The source file could not be read.", "Check the --scene path.")])

        rel_scene = relpath(source.path, context.project_root)
        if source.tree is None:
            findings.append(finding(self.name, "blocker", "source", "Python syntax error", "The scene file could not be parsed as Python.", "Run py_compile and fix the syntax error.", location=rel_scene))
            return AgentResult(self.name, findings)

        class_line = source_tools.class_line(source, context.scene_class)
        if class_line is None:
            findings.append(finding(self.name, "blocker", "source", "Scene class missing", f"`{context.scene_class}` was not found in the scene file.", "Create or rename the renderable scene class.", location=rel_scene))
        else:
            findings.append(finding(self.name, "info", "source", "Scene class found", f"`{context.scene_class}` is defined.", "No action needed.", location=f"{rel_scene}:{class_line}"))

        external_audio = source_tools.has_external_audio_workflow(source)
        if external_audio:
            findings.append(
                finding(
                    self.name,
                    "info",
                    "voiceover",
                    "External audio workflow detected",
                    "The scene uses optional local audio files and Manim subcaptions rather than Azure TTS.",
                    "No action needed unless this scene should be migrated to the shared TTS workflow.",
                    location=rel_scene,
                )
            )

        checks = [
            ("play_uqam_intro", r"play_uqam_intro\(", "UQAM intro not detected", "Import `play_uqam_intro` and call it near the start of `construct()`."),
        ]
        if not external_audio:
            checks.insert(0, ("tools.tts", r"tools\.tts|from tools import tts", "Shared TTS helper not used", "Import and use `tools.tts` for voice, SSML, and character pronunciation."))
        for category, pattern, title, fix in checks:
            if not re.search(pattern, source.text):
                findings.append(finding(self.name, "warning", category, title, f"The source did not match `{pattern}`.", fix, location=rel_scene))

        if not source_tools.has_plain_caption_source(source):
            findings.append(
                finding(
                    self.name,
                    "warning",
                    "captions",
                    "Plain captions not detected",
                    "The source does not expose script captions, subcaptions, or on-screen caption helpers.",
                    "Use plain captions via `caption`, `subcaption=`, `add_subcaption(...)`, or a `_show_caption(...)` helper.",
                    location=rel_scene,
                )
            )

        if "VoiceoverScene" in source.text and not external_audio and not source_tools.has_ssml_narration(source):
            findings.append(
                finding(
                    self.name,
                    "warning",
                    "ssml",
                    "SSML narration not detected",
                    "The source does not call `tts.ssml(...)` or an alias around voiceover text.",
                    "Wrap Azure narration text with `tts.ssml(...)` while keeping plain captions separate.",
                    location=rel_scene,
                )
            )

        if "VoiceoverScene" not in source.text and not external_audio:
            findings.append(finding(self.name, "warning", "voiceover", "VoiceoverScene not detected", "The scene may not support the standard narrated workflow.", "Use `VoiceoverScene` or document why this video is intentionally silent.", location=rel_scene))

        if not external_audio and not re.search(r"MANIM_DISABLE_VOICEOVER|_voiceover_enabled|Missing Azure|without narration", source.text):
            findings.append(finding(self.name, "warning", "voiceover", "Silent fallback not detected", "Smoke renders may fail when Azure credentials or network access are unavailable.", "Add the optional voiceover setup pattern used by production scenes.", location=rel_scene))

        bookmark_set = set(source.bookmarks)
        wait_set = set(source.waits)
        missing_waits = sorted(bookmark_set - wait_set)
        extra_waits = sorted(wait_set - bookmark_set)
        if not bookmark_set:
            if source_tools.has_manual_pacing(source):
                findings.append(
                    finding(
                        self.name,
                        "info",
                        "sync",
                        "Manual narration pacing detected",
                        "The scene uses paced narration helpers instead of SSML bookmarks.",
                        "No action needed unless tight word-level animation sync is required.",
                        location=rel_scene,
                    )
                )
            elif external_audio:
                findings.append(
                    finding(
                        self.name,
                        "info",
                        "sync",
                        "Fixed-timing caption workflow detected",
                        "The scene uses timed Manim captions instead of SSML bookmarks.",
                        "No action needed unless tight word-level animation sync is required.",
                        location=rel_scene,
                    )
                )
            else:
                findings.append(finding(self.name, "warning", "sync", "No SSML bookmarks detected", "The narration has no explicit sync points.", "Add `<bookmark mark='...'>` markers and wait for them around key animations.", location=rel_scene))
        elif missing_waits:
            findings.append(finding(self.name, "warning", "sync", "Bookmarks without waits", f"{len(missing_waits)} bookmark(s) are never waited for: {', '.join(missing_waits[:8])}.", "Either add `wait_until_bookmark(...)` calls or remove unused bookmarks.", location=rel_scene))
        if extra_waits:
            findings.append(finding(self.name, "warning", "sync", "Waits without bookmarks", f"{len(extra_waits)} wait(s) reference missing bookmarks: {', '.join(extra_waits[:8])}.", "Fix the bookmark names so narration and animation stay synchronized.", location=rel_scene))

        long_captions = [(caption, line) for caption, line in source.captions if len(caption) > 55]
        if long_captions:
            sample = "; ".join(f"line {line}: {caption[:70]!r}" for caption, line in long_captions[:4])
            findings.append(finding(self.name, "warning", "captions", "Long captions detected", f"{len(long_captions)} caption(s) exceed the 55-character guideline. {sample}", "Shorten captions or split the narration into smaller voiceover blocks.", location=rel_scene))

        if "self.voiceover(" in source.text and "subcaption=" not in source.text:
            findings.append(finding(self.name, "warning", "captions", "Voiceover without subcaption", "The scene calls `self.voiceover(...)` but no `subcaption=` was found.", "Pass plain captions via `subcaption=` for SRT generation.", location=rel_scene))

        findings.extend(self._legacy_ssml_check(context))
        return AgentResult(self.name, findings)

    def _legacy_ssml_check(self, context: AuditContext) -> list[Finding]:
        checker = context.project_root / "tools" / "ssml_sync_check.py"
        if not checker.exists():
            return []
        try:
            result = subprocess.run(
                [str(context.project_root / ".venv" / "bin" / "python"), str(checker), str(context.scene_path)],
                cwd=context.project_root,
                capture_output=True,
                text=True,
                timeout=20,
            )
        except Exception as exc:
            return [finding(self.name, "polish", "sync", "Legacy SSML checker could not run", str(exc), "Run `tools/ssml_sync_check.py` manually if this scene uses its older constants.")]
        if result.returncode == 0:
            return [finding(self.name, "info", "sync", "Legacy SSML checker passed", "The existing `tools/ssml_sync_check.py` returned success.", "No action needed.")]
        output = (result.stdout + result.stderr).strip().replace("\n", " ")
        if "Missing constant" in output:
            return [
                finding(
                    self.name,
                    "info",
                    "sync",
                    "Legacy SSML checker not applicable",
                    "The existing `tools/ssml_sync_check.py` expects older scene-specific constants that this scene does not expose.",
                    "No action needed unless this scene is intended to use the legacy constants.",
                )
            ]
        return [finding(self.name, "polish", "sync", "Legacy SSML checker not clean", output[:500] or "No output.", "Treat this as advisory unless the scene uses that checker’s expected constants.")]


class RenderMetadataAgent:
    name = "RenderMetadataAgent"

    def run(self, context: AuditContext) -> AgentResult:
        findings: list[Finding] = []
        info = context.media
        rel_video = relpath(context.video_path, context.project_root)
        if info is None:
            return AgentResult(self.name, [finding(self.name, "blocker", "render", "Video metadata unavailable", "The MP4 could not be probed.", "Verify the --video path and ffprobe installation.", location=rel_video)])

        if not info.has_video:
            findings.append(finding(self.name, "blocker", "render", "No video stream", "ffprobe did not find a video stream.", "Re-render the scene.", location=rel_video))
        if info.duration <= 5:
            findings.append(finding(self.name, "blocker", "duration", "Video is too short", f"Duration is {info.duration:.1f}s.", "Re-render and confirm the full scene is included.", location=rel_video))
        elif info.duration < 20:
            findings.append(finding(self.name, "warning", "duration", "Short video", f"Duration is {info.duration:.1f}s.", "Confirm this is intentional for the concept.", location=rel_video))

        if info.width and info.height:
            ratio = info.width / info.height
            if abs(ratio - (16 / 9)) > 0.03:
                findings.append(finding(self.name, "warning", "format", "Non-16:9 frame", f"Resolution is {info.width}x{info.height}.", "Use the standard 16:9 Manim frame/export settings.", location=rel_video))
            if info.height < 720:
                severity = "info" if context.silent_preview else "polish"
                findings.append(finding(self.name, severity, "format", "Preview-resolution render", f"Resolution is {info.width}x{info.height}.", "Expected for low-quality silent previews; use `qh` or `-r 1920,1080` for final review.", location=rel_video))

        if info.frame_rate is not None and info.frame_rate < 15:
            findings.append(finding(self.name, "warning", "format", "Low frame rate", f"Frame rate is {info.frame_rate:.2f} fps.", "Render at least 15 fps for preview and 30/60 fps for final export.", location=rel_video))

        expected = canonical_video_path(context.project_root, context.scene_path)
        if context.video_path.resolve() != expected.resolve():
            findings.append(finding(self.name, "polish", "render", "Non-standard dist path", f"Expected `{relpath(expected, context.project_root)}`.", "Use `scripts/render.sh` so outputs land in the standard dist directory.", location=rel_video))

        frame_rate = f"{info.frame_rate:.2f}" if info.frame_rate is not None else "unknown"
        findings.append(finding(self.name, "info", "render", "Metadata summary", f"Duration {info.duration:.1f}s, resolution {info.width}x{info.height}, frame rate {frame_rate} fps.", "No action needed.", location=rel_video))
        return AgentResult(self.name, findings)


class VisualFrameAgent:
    name = "VisualFrameAgent"

    def run(self, context: AuditContext) -> AgentResult:
        findings: list[Finding] = []
        info = context.media
        if info is None:
            return AgentResult(self.name, [])
        if not media_tools.has_ffmpeg():
            return AgentResult(self.name, [finding(self.name, "blocker", "visual", "ffmpeg/ffprobe missing", "Frame sampling requires ffmpeg and ffprobe.", "Install ffmpeg or run the audit on a machine that has it.")])
        try:
            analysis = media_tools.sample_frames(context.video_path, info.duration, context.artifacts_dir)
        except Exception as exc:
            return AgentResult(self.name, [finding(self.name, "warning", "visual", "Frame sampling failed", str(exc), "Check that ffmpeg can decode this MP4.")])

        if analysis.contact_sheet is not None:
            findings.append(finding(self.name, "info", "visual", "Contact sheet generated", "Sampled frames were written for visual review.", "Open the contact sheet when reviewing visual layout.", location=relpath(analysis.contact_sheet, context.project_root)))

        blank_indexes = [
            idx + 1
            for idx, (mean, contrast) in enumerate(zip(analysis.mean_luma, analysis.contrast))
            if contrast < 2.5 or mean < 3 or mean > 252
        ]
        if blank_indexes:
            findings.append(finding(self.name, "warning", "visual", "Blank or near-flat sampled frames", f"Frame sample(s) {blank_indexes} look blank or nearly flat.", "Inspect the contact sheet and adjust scene timing or object visibility."))

        if analysis.contrast and sum(analysis.contrast) / len(analysis.contrast) < 18:
            findings.append(finding(self.name, "warning", "visual", "Low average contrast", "Sampled frames have low grayscale contrast.", "Use stronger black strokes/text or reduce pale fills."))

        if analysis.adjacent_diff and max(analysis.adjacent_diff) < 1.5 and info.duration > 10:
            findings.append(finding(self.name, "warning", "visual", "Video appears near-static", "Adjacent sampled frames are almost identical.", "Confirm animations are visible and the render is not stuck on one frame."))

        return AgentResult(self.name, findings)


class AudioCaptionAgent:
    name = "AudioCaptionAgent"

    def run(self, context: AuditContext) -> AgentResult:
        findings: list[Finding] = []
        info = context.media
        rel_video = relpath(context.video_path, context.project_root)
        if info is None:
            return AgentResult(self.name, [])

        if not info.has_audio:
            severity = "info" if context.silent_preview else "warning"
            findings.append(finding(self.name, severity, "audio", "No audio stream", "The MP4 has no audio stream.", "This is expected for silent previews; render with Azure credentials for final narration.", location=rel_video))
        else:
            try:
                stats = media_tools.audio_stats(context.video_path)
                findings.append(finding(self.name, "info", "audio", "Audio summary", f"Audio duration {stats.duration_seconds:.1f}s, average {stats.dbfs:.1f} dBFS, peak {stats.max_dbfs:.1f} dBFS.", "No action needed.", location=rel_video))
                if stats.max_dbfs > -1.0:
                    findings.append(finding(self.name, "warning", "audio", "Audio peak too hot", f"Peak is {stats.max_dbfs:.1f} dBFS.", "Lower gain so the final WAV peak is <= -1 dBFS.", location=rel_video))
                if stats.dbfs < -35:
                    findings.append(finding(self.name, "warning", "audio", "Audio average is quiet", f"Average level is {stats.dbfs:.1f} dBFS.", "Normalize or adjust TTS/render volume.", location=rel_video))
            except Exception as exc:
                findings.append(finding(self.name, "warning", "audio", "Audio analysis failed", str(exc), "Check ffmpeg/pydub support for this MP4.", location=rel_video))

        srt_path = context.video_path.with_suffix(".srt")
        entries = media_tools.parse_srt(srt_path)
        if not srt_path.exists():
            severity = "info" if context.silent_preview else "warning"
            findings.append(finding(self.name, severity, "captions", "No SRT beside MP4", f"`{relpath(srt_path, context.project_root)}` does not exist.", "Expected for silent previews; render with voiceover/subcaptions for final caption QA.", location=relpath(srt_path, context.project_root)))
        elif not entries:
            findings.append(finding(self.name, "warning", "captions", "SRT has no parseable entries", "The SRT exists but no timestamp entries were parsed.", "Regenerate or fix the SRT file.", location=relpath(srt_path, context.project_root)))
        elif info.duration and entries[-1][1] > info.duration + 2:
            findings.append(finding(self.name, "warning", "captions", "SRT extends beyond video", f"Last subtitle ends at {entries[-1][1]:.1f}s but video is {info.duration:.1f}s.", "Regenerate subtitles after the final render.", location=relpath(srt_path, context.project_root)))
        else:
            findings.append(finding(self.name, "info", "captions", "SRT timing parsed", f"Parsed {len(entries)} subtitle entries.", "No action needed.", location=relpath(srt_path, context.project_root)))

        return AgentResult(self.name, findings)


class PedagogyAccessibilityAgent:
    name = "PedagogyAccessibilityAgent"

    def run(self, context: AuditContext) -> AgentResult:
        findings: list[Finding] = []
        source = context.source
        if source is None:
            return AgentResult(self.name, [])
        rel_scene = relpath(source.path, context.project_root)
        lower = source.text.lower()

        if not source_tools.has_plain_caption_source(source):
            findings.append(finding(self.name, "warning", "accessibility", "No caption text found in source", "The audit did not find script captions or on-screen caption helpers.", "Add plain French captions for every narration block.", location=rel_scene))

        visual_terms = ["graphe", "droite", "parabole", "axe", "sommet", "tableau", "flèche", "point"]
        if ("Axes(" in source.text or ".plot(" in source.text) and not any(term in lower for term in visual_terms):
            findings.append(finding(self.name, "warning", "accessibility", "Graph visuals may not be verbally described", "The source uses axes/plots but the narration text does not include common graph-description words.", "Describe important graph features in the narration or transcript.", location=rel_scene))

        if not source_tools.has_final_wait(source):
            findings.append(finding(self.name, "polish", "timing", "Final pause not detected", "The last part of the scene may exit immediately after the final animation.", "End with `self.wait(1.0)` or longer.", location=rel_scene))

        if source_tools.count_animation_calls(source) < 5:
            findings.append(finding(self.name, "warning", "pedagogy", "Few animation beats", "The source has very few `self.play(...)` calls.", "Confirm the video is not just a static slide deck.", location=rel_scene))

        color_tokens = re.findall(r"\b(?:ACCENT|WARN|GOOD|QUAD|YELLOW|RED|GREEN|BLUE|ORANGE|TEAL)\b", source.text)
        if len(set(color_tokens)) >= 3:
            findings.append(finding(self.name, "polish", "accessibility", "Color-coded meaning should be double encoded", "The scene uses several semantic colors.", "Ensure every color distinction is also labeled with text, shape, position, or stroke style.", location=rel_scene))

        return AgentResult(self.name, findings)
