#!/usr/bin/env python3
"""Package a narrated landscape film for Instagram with timed, readable captions.

Requires FFmpeg/ffprobe and Pillow. The complete source picture is fitted into a
1080x1920 canvas; narration and caption timestamps are never sped up or shifted.
This makes a local review artifact and does not upload or approve publication.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "assets/uqam_promo/fonts/Roboto-VariableFont_wdth,wght.ttf"
CANVAS = (1080, 1920)
VIDEO_Y, VIDEO_HEIGHT = 430, 608
CAPTION_SIZE, CAPTION_WIDTH, CAPTION_Y = 58, 880, 1260
BACKGROUND, NAVY, BLUE = "#F2F7FA", "#0B3A5D", "#007EB5"


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_streams", "-show_format",
                          "-of", "json", str(path)).stdout)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def font(size, weight=600):
    face = ImageFont.truetype(str(FONT), size)
    face.set_variation_by_axes([weight, 100])
    return face


def wrap_two_lines(text, face, width):
    words = text.split()
    if not words:
        raise ValueError("Empty title or caption")
    if face.getlength(" ".join(words)) <= width:
        return [" ".join(words)]
    candidates = []
    for split in range(1, len(words)):
        lines = [" ".join(words[:split]), " ".join(words[split:])]
        widths = [face.getlength(line) for line in lines]
        if max(widths) <= width:
            candidates.append((abs(widths[0] - widths[1]), lines))
    if not candidates:
        raise ValueError(f"Text exceeds two readable lines; split its SRT cue: {text}")
    return min(candidates, key=lambda candidate: candidate[0])[1]


def time_seconds(value):
    h, m, s, ms = map(int, re.split(r"[:,.]", value))
    if m >= 60 or s >= 60:
        raise ValueError(f"Invalid SRT time: {value}")
    return h * 3600 + m * 60 + s + ms / 1000


def read_cues(path, duration):
    cues, previous_end = [], 0.0
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            raise ValueError("Expected numbered SRT cues")
        match = re.fullmatch(r"(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*"
                             r"(\d{2}:\d{2}:\d{2}[,.]\d{3})", lines[1].strip())
        if not match:
            raise ValueError(f"Unsupported SRT timing: {lines[1]}")
        start, end = (time_seconds(value) for value in match.groups())
        if not 0 <= start < end <= duration + 0.001 or start < previous_end - 0.001:
            raise ValueError("SRT cues must be ordered, non-overlapping and inside the video")
        text = " ".join(" ".join(lines[2:]).split())
        if any(character in text for character in "{}\\"):
            raise ValueError("SRT must contain plain text, without ASS control characters")
        cues.append({"start": start, "end": end, "text": text})
        previous_end = end
    if not cues:
        raise ValueError("At least one SRT cue is required")
    return cues


def ass_time(seconds):
    centiseconds = round(seconds * 100)
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    whole_seconds, fractional = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{whole_seconds:02d}.{fractional:02d}"


def portrait_cues(cues):
    """Split long cards within measured cue bounds, without claiming word alignment."""
    face, derived = font(CAPTION_SIZE, 700), []
    for index, cue in enumerate(cues, 1):
        words, chunks = cue["text"].split(), []
        cursor = 0
        while cursor < len(words):
            end = cursor + 1
            wrap_two_lines(words[cursor], face, CAPTION_WIDTH)
            while end < len(words):
                try:
                    wrap_two_lines(" ".join(words[cursor:end + 1]), face, CAPTION_WIDTH)
                except ValueError:
                    break
                end += 1
            chunks.append(words[cursor:end])
            cursor = end
        # Balance adjacent cards so a final word does not flash for a fraction
        # of a second. Prefer a punctuation boundary when equally readable.
        for pair in range(len(chunks) - 2, -1, -1):
            combined = chunks[pair] + chunks[pair + 1]
            options = []
            for split in range(1, len(combined)):
                left, right = combined[:split], combined[split:]
                try:
                    wrap_two_lines(" ".join(left), face, CAPTION_WIDTH)
                    wrap_two_lines(" ".join(right), face, CAPTION_WIDTH)
                except ValueError:
                    continue
                punctuation = left[-1].endswith((",", ".", ";", ":", "!", "?"))
                imbalance = abs(len(left) - len(right))
                options.append(((imbalance - 2 * punctuation, not punctuation, imbalance), left, right))
            if options:
                _, chunks[pair], chunks[pair + 1] = min(options, key=lambda item: item[0])
        elapsed_words, previous_end = 0, cue["start"]
        for position, chunk in enumerate(chunks):
            elapsed_words += len(chunk)
            end = (cue["end"] if position == len(chunks) - 1 else
                   cue["start"] + (cue["end"] - cue["start"]) * elapsed_words / len(words))
            derived.append({"start": previous_end, "end": end, "text": " ".join(chunk),
                            "source_cue": index, "timing_estimated_within_source_cue": len(chunks) > 1})
            previous_end = end
    if " ".join(cue["text"] for cue in derived) != " ".join(cue["text"] for cue in cues):
        raise RuntimeError("Portrait caption splitting changed the spoken word sequence")
    return derived


def write_srt(path, cues):
    def timestamp(seconds):
        value = round(seconds * 1000)
        h, value = divmod(value, 3600000)
        m, value = divmod(value, 60000)
        s, ms = divmod(value, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    path.write_text("\n\n".join(
        f"{i}\n{timestamp(cue['start'])} --> {timestamp(cue['end'])}\n"
        + "\n".join(cue["lines"]) for i, cue in enumerate(cues, 1)) + "\n", encoding="utf-8")


def write_ass(path, cues):
    face = font(CAPTION_SIZE, 700)
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Roboto,{CAPTION_SIZE},&H005D3A0B,&H005D3A0B,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,1,0,0,5,100,100,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for cue in cues:
        lines = wrap_two_lines(cue["text"], face, CAPTION_WIDTH)
        cue["lines"] = lines
        cue["max_line_width_pixels"] = max(face.getlength(line) for line in lines)
        text = r"\N".join(lines)
        events.append(f"Dialogue: 0,{ass_time(cue['start'])},{ass_time(cue['end'])},"
                      f"Caption,,0,0,0,,{{\\an5\\pos(540,{CAPTION_Y})}}{text}")
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def write_canvas(path, title):
    image = Image.new("RGB", CANVAS, BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 1080, 18), fill=BLUE)
    title_font = font(64, 600)
    title_lines = wrap_two_lines(title, title_font, 900)
    for index, line in enumerate(title_lines):
        y = 270 + (index - (len(title_lines) - 1) / 2) * 82
        draw.text((540, y), line, font=title_font, fill=NAVY, anchor="mm")
    draw.rectangle((496, 1125, 584, 1131), fill=BLUE)
    draw.text((540, 1575), "math.uqam.ca", font=font(48, 500), fill=NAVY, anchor="mm")
    image.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, type=Path)
    parser.add_argument("--subtitles", required=True, type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.video, args.subtitles, args.output = (p.resolve() for p in
                                             (args.video, args.subtitles, args.output))
    if args.output.exists():
        raise FileExistsError(args.output)
    source = probe(args.video)
    video = next(s for s in source["streams"] if s["codec_type"] == "video")
    audio = next((s for s in source["streams"] if s["codec_type"] == "audio"), None)
    if audio is None:
        raise ValueError("A narrated input with an audio stream is required")
    duration = float(video["duration"])
    if abs(video["width"] / video["height"] - 16 / 9) > 0.01:
        raise ValueError("Expected a 16:9 source film")
    original_cues = read_cues(args.subtitles, duration)
    cues = portrait_cues(original_cues)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="uqam-instagram-") as tmp:
        scratch = Path(tmp)
        canvas, subtitles = scratch / "canvas.png", scratch / "captions.ass"
        write_canvas(canvas, args.title)
        write_ass(subtitles, cues)
        write_srt(args.output.with_suffix(".portrait.srt"), cues)
        # Fixed scratch names keep user paths outside the FFmpeg filter grammar.
        font_dir = scratch / "fonts"
        font_dir.mkdir()
        shutil.copyfile(FONT, font_dir / "Roboto.ttf")
        graph = (f"[0:v:0]scale=1080:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease:"
                 f"force_divisible_by=2,pad=1080:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2:"
                 "color=0xF2F7FA,setsar=1[landscape];"
                 f"[1:v:0][landscape]overlay=0:{VIDEO_Y}:shortest=1,"
                 "ass=filename=captions.ass:fontsdir=fonts,fps=30,format=yuv420p[portrait]")
        result = run("ffmpeg", "-hide_banner", "-nostats", "-n", "-i", str(args.video),
                     "-loop", "1", "-framerate", "30", "-i", str(canvas),
                     "-filter_complex", graph, "-map", "[portrait]", "-map", "0:a:0",
                     "-map_metadata", "0", "-c:v", "libx264", "-preset", "fast",
                     "-crf", "20", "-profile:v", "high", "-level:v", "4.1",
                     "-g", "60", "-keyint_min", "60", "-sc_threshold", "0",
                     "-flags", "+cgop", "-x264-params", "open-gop=0",
                     "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "2",
                     "-af", f"apad=whole_dur={duration},atrim=duration={duration}",
                     "-t", str(duration), "-movflags", "+faststart", str(args.output), cwd=tmp)
        args.output.with_suffix(".ffmpeg.log").write_text(result.stderr)
        shutil.copyfile(canvas, args.output.with_suffix(".canvas.png"))
        shutil.copyfile(subtitles, args.output.with_suffix(".ass"))
    output = probe(args.output)
    out_video = next(s for s in output["streams"] if s["codec_type"] == "video")
    out_audio = next(s for s in output["streams"] if s["codec_type"] == "audio")
    expected = {"width": 1080, "height": 1920, "codec_name": "h264",
                "pix_fmt": "yuv420p", "r_frame_rate": "30/1"}
    if any(out_video[key] != value for key, value in expected.items()):
        raise RuntimeError("Portrait output video does not meet the format contract")
    if out_audio["codec_name"] != "aac" or out_audio["sample_rate"] != "48000":
        raise RuntimeError("Portrait output audio does not meet the format contract")
    if abs(float(output["format"]["duration"]) - duration) > 0.05:
        raise RuntimeError("Portrait packaging changed the film duration")
    decoded = run("ffmpeg", "-v", "error", "-i", str(args.output), "-f", "null", "-")
    if decoded.stderr.strip():
        raise RuntimeError(decoded.stderr)
    source_credits = args.video.with_suffix(".credits.txt")
    output_credits = args.output.with_suffix(".credits.txt")
    if source_credits.exists():
        shutil.copyfile(source_credits, output_credits)
    manifest = {
        "status": "local_instagram_review_not_release", "input_video": str(args.video),
        "input_video_sha256": sha256(args.video), "input_srt": str(args.subtitles),
        "input_srt_sha256": sha256(args.subtitles), "font_sha256": sha256(FONT),
        "credits_sidecar": output_credits.name if source_credits.exists() else None,
        "credits_sha256": sha256(output_credits) if source_credits.exists() else None,
        "title": args.title, "cta": "math.uqam.ca", "canvas": list(CANVAS),
        "source_crop": "none; entire picture fitted with aspect ratio retained",
        "video_area": [0, VIDEO_Y, 1080, VIDEO_Y + VIDEO_HEIGHT],
        "caption_area": [100, 1135, 980, 1415], "caption_font_size": CAPTION_SIZE,
        "caption_max_lines": max(len(cue["lines"]) for cue in cues), "cues": cues,
        "original_cues": original_cues,
        "portrait_srt": args.output.with_suffix(".portrait.srt").name,
        "caption_word_sequence_preserved": True,
        "caption_timing_method": "Original measured cue bounds; long cues subdivided by word count",
        "caption_word_timing_estimated": any(cue["timing_estimated_within_source_cue"] for cue in cues),
        "caption_word_timing_forced_aligned": False,
        "caption_timing_precision_seconds": 0.01, "permanent_caption_card": False,
        "duration_seconds": float(output["format"]["duration"]),
        "video": out_video, "audio": out_audio, "closed_gop_requested": True,
        "audio_processing": "AAC re-encode at 128 kbps; only pad/trim to video length",
        "speech_speed_changed": False, "full_decode": "passed", "listening_review": "not_performed",
        "institutional_approval": "not_inferred", "release_ready": False,
        "output_file": args.output.name, "output_sha256": sha256(args.output),
        "ffmpeg_version": run("ffmpeg", "-version").stdout.splitlines()[0],
    }
    args.output.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(args.output), "duration": manifest["duration_seconds"],
                      "caption_max_lines": manifest["caption_max_lines"], "full_decode": "passed"}))


if __name__ == "__main__":
    main()
