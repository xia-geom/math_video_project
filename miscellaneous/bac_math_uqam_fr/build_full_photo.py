#!/usr/bin/env python3
"""Alternate full-photo cut, using the exact October 22 mixed soundtrack.

Pillow lays out existing registered photos and text; FFmpeg encodes the pictures
and copies the AAC stream without resynthesis, mixing, or a duration change.
This is a local review export. It does not replace the Manim scene or publish.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets/uqam_promo"
FONT = ASSETS / "fonts/Roboto-VariableFont_wdth,wght.ttf"
SOURCE = ROOT / "dist/uqam_revision_20261022/final_voice_update/uqam_math_birds_20261022_102838.mp4"
SOURCE_SHA256 = "6763f42db0e242fbca4fcac764233bb5d6cc2e6f3703ee5d4c71868f81c40b77"
SIZE, FPS, FRAME_COUNT = (1920, 1080), 60, 3965
DURATION = FRAME_COUNT / FPS
TRANSITION_FRAMES = 36


def line(text, y, size=84, weight=700, color=255):
    return {"text": text, "x": 96, "y": y, "size": size,
            "weight": weight, "color": color}


def research_lines(active):
    lines = [line("La recherche, dès le bac", 180, 76)]
    for index, (name, detail) in enumerate([
        ("CIRGET", "Géométrie et topologie"),
        ("LaCIM", "Combinatoire et informatique mathématique"),
        ("STATQAM", "Statistique et science des données"),
    ]):
        shade = 255 if index == active else 210
        lines.extend([line(name, 350 + 200 * index, 62, 700, shade),
                      line(detail, 430 + 200 * index, 46, 400, shade)])
    return lines


# These anchors come from the rendered October 4 speech clock, retained by the
# October 22 soundtrack repair. Quantization is at most half a video frame.
# They are not estimates based on word counts. The final audio length wins over
# the loose Manim semantic timeline's slightly longer pre-packaging endpoint.
STATES = [
    {"id": "opening", "start": 0, "photo": "sciences_biologiques_uqam.jpg", "focal_y": .72,
     "lines": [line("Des maths de haut niveau", 450),
               line("Une université à votre écoute", 570, 54, 400)]},
    {"id": "learning", "start": 4.966667, "photo": "ludopolis_2026.jpg",
     "lines": [line("Apprendre ensemble", 710),
               line("Petits groupes · Travaux pratiques", 815, 50, 400),
               line("Travail supervisé", 880, 50, 400),
               line("Vie de campus · Ludopolis, 2026", 982, 28, 400)]},
    {"id": "research_intro", "start": 13.508667, "photo": "research_math.jpg", "veil": .60,
     "lines": [line("La recherche, dès le bac", 400),
               line("Stages d’été en recherche", 520, 54, 400)]},
    {"id": "cirget", "start": 18.442, "photo": "research_math.jpg", "veil": .60,
     "lines": research_lines(0)},
    {"id": "lacim", "start": 22.57, "photo": "research_math.jpg", "veil": .60,
     "lines": research_lines(1)},
    {"id": "statqam", "start": 25.474, "photo": "research_math.jpg", "veil": .60,
     "lines": research_lines(2)},
    {"id": "support", "start": 30.437333, "photo": "redaction_sciences_2026_no_red_bag.png",
     "lines": [line("Échanger autour des maths", 100),
               line("Trouver ses repères", 220, 54, 400)]},
    {"id": "library", "start": 34.120667, "photo": "redaction_sciences_2026_no_red_bag.png",
     "lines": [line("Bibliothèque des sciences", 100),
               line("Travailler seul ou en équipe", 220, 54, 400)]},
    {"id": "location", "start": 38.344667, "photo": "president_kennedy_no_vehicles.png", "focal_y": .20,
     "lines": [line("Quartier des spectacles", 470),
               line("Métro Place-des-Arts", 605, 56, 400)]},
    {"id": "community", "start": 45.828, "photo": "accueil_hiver_2026.jpg",
     "lines": [line("Une communauté accueillante", 765, 80),
               line("Ouverte sur le monde", 875, 54, 400),
               line("Accueil d’hiver · vie de campus", 982, 28, 400)]},
]

SUMMARY = [line("Des maths de haut niveau.", 350, 76),
           line("Un milieu à votre écoute.", 465, 56, 400),
           line("De multiples accès à la recherche.", 565, 56, 400),
           line("Au cœur de Montréal.", 680, 76)]
for index, start in enumerate([50.661333, 52.278, 54.111333, 56.399333]):
    STATES.append({"id": f"summary_{index + 1}", "start": start,
                   "photo": "montreal_skyline_2026.jpg", "lines": SUMMARY[:index + 1]})
STATES.append({"id": "call_to_action", "start": 57.932333,
               "photo": "montreal_skyline_2026.jpg",
               "lines": [line("Aller loin, sans avancer seul.", 390, 84),
                         line("Baccalauréat en mathématiques", 515, 54, 400),
                         line("Découvrir le programme", 655, 38, 400),
                         line("etudier.uqam.ca", 720, 56)]})


def sha256(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def probe(path):
    return json.loads(run("ffprobe", "-v", "error", "-show_format", "-show_streams",
                          "-of", "json", str(path)))


def validate_source(path):
    if sha256(path) != SOURCE_SHA256:
        raise ValueError("Expected the verified October 22 maths export; soundtrack differs")
    info = probe(path)
    audio = [s for s in info["streams"] if s["codec_type"] == "audio"]
    if len(audio) != 1 or audio[0]["codec_name"] != "aac":
        raise ValueError("Exactly one existing AAC soundtrack is required")
    if abs(float(info["format"]["duration"]) - DURATION) > .001:
        raise ValueError("Soundtrack source has a different duration")
    return info


def frame_anchors(states=STATES):
    anchors = [round(state["start"] * FPS) for state in states] + [FRAME_COUNT]
    if anchors[0] != 0 or any(b <= a for a, b in zip(anchors, anchors[1:])):
        raise ValueError("States must cover the film with strictly increasing frame anchors")
    if any(b - a < TRANSITION_FRAMES for a, b in zip(anchors, anchors[1:])):
        raise ValueError("A state is shorter than its transition")
    return anchors


def font(size, weight):
    face = ImageFont.truetype(str(FONT), size)
    face.set_variation_by_axes([weight, 100])
    return face


def copy_layer(state):
    layer = Image.new("RGBA", SIZE)
    draw = ImageDraw.Draw(layer)
    boxes = []
    for item in state["lines"]:
        face = font(item["size"], item["weight"])
        xy = (item["x"], item["y"])
        box = draw.textbbox(xy, item["text"], font=face, anchor="lt")
        if box[0] < 70 or box[1] < 54 or box[2] > SIZE[0] - 70 or box[3] > SIZE[1] - 54:
            raise ValueError(f"Copy exceeds safe frame: {state['id']}: {item['text']}")
        for prior in boxes:
            if box[0] < prior[2] and box[2] > prior[0] and box[1] < prior[3] and box[3] > prior[1]:
                raise ValueError(f"Copy overlaps: {state['id']}")
        boxes.append(box)
        shade = item["color"]
        draw.text(xy, item["text"], font=face, fill=(shade, shade, shade, 255), anchor="lt")
    return layer, boxes


def photo_layer(state):
    path = ASSETS / state["photo"]
    with Image.open(path) as source:
        image = ImageOps.fit(ImageOps.exif_transpose(source).convert("RGB"), SIZE,
                             method=Image.Resampling.LANCZOS,
                             centering=(.5, state.get("focal_y", .5)))
    return Image.blend(image, Image.new("RGB", SIZE, "black"), state.get("veil", .52))


def compose(background, overlay, opacity=1):
    if opacity < 1:
        overlay = overlay.copy()
        overlay.putalpha(overlay.getchannel("A").point(lambda a: round(a * opacity)))
    image = background.copy()
    image.paste(overlay, mask=overlay.getchannel("A"))
    return image


def audio_digest(path):
    """Hash decoded PCM with identical decoder settings, independently of MP4 metadata."""
    return run("ffmpeg", "-v", "error", "-i", str(path), "-map", "0:a:0",
               "-c:a", "pcm_s16le", "-f", "hash", "-hash", "sha256", "-").strip()


def prepare(output_dir):
    records = {record["filename"]: record for record in
               json.loads((ASSETS / "sources.json").read_text())["assets"]}
    prepared, used = [], {}
    frames = output_dir / "frames"
    frames.mkdir(parents=True)
    for state in STATES:
        record = records[state["photo"]]
        if not record.get("credit") or sha256(ASSETS / state["photo"]) != record["sha256"]:
            raise ValueError(f"Missing credit or stale asset inventory: {state['photo']}")
        used[state["photo"]] = record
        background = photo_layer(state)
        overlay, boxes = copy_layer(state)
        composite = compose(background, overlay)
        composite.save(frames / (state["id"] + ".jpg"), quality=94)
        prepared.append((background, overlay, composite.tobytes(), boxes))
    return prepared, used


def render(source, output_dir, prepared):
    output = output_dir / "uqam_math_full_photo.mp4"
    command = ["ffmpeg", "-hide_banner", "-nostats", "-v", "warning", "-n",
               "-f", "rawvideo", "-pixel_format", "rgb24", "-video_size", "1920x1080",
               "-framerate", str(FPS), "-i", "pipe:0", "-i", str(source),
               "-map", "0:v:0", "-map", "1:a:0", "-map_metadata", "-1",
               "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "copy", "-movflags", "+faststart", "-metadata",
               "title=UQAM — Mathématiques — Version plein écran photographique",
               "-metadata", "comment=Local review. Photos and Birds by Corbyn Kites: see CREDITS.txt.",
               str(output)]
    anchors = frame_anchors()
    with (output_dir / "encode.log").open("w") as log:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
        try:
            for index, (background, overlay, static, _) in enumerate(prepared):
                print(f"Rendering {index + 1}/{len(prepared)}: {STATES[index]['id']}", flush=True)
                same_photo = index > 0 and STATES[index]["photo"] == STATES[index - 1]["photo"]
                old_copy = [{k: v for k, v in item.items() if k != "color"}
                            for item in STATES[max(0, index - 1)]["lines"]]
                new_copy = [{k: v for k, v in item.items() if k != "color"}
                            for item in STATES[index]["lines"]]
                additive_copy = all(item in new_copy for item in old_copy)
                old_background, old_overlay = prepared[max(0, index - 1)][:2]
                duration = anchors[index + 1] - anchors[index]
                for local in range(duration):
                    if local >= TRANSITION_FRAMES:
                        frame = static
                    else:
                        progress = local / (TRANSITION_FRAMES - 1)
                        if index == 0:
                            frame = compose(background, overlay, progress).tobytes()
                        elif same_photo and additive_copy:
                            # Only typography changes, so the photograph cannot flash.
                            frame = compose(background, Image.blend(old_overlay, overlay, progress)).tobytes()
                        else:
                            mixed = background if same_photo else Image.blend(old_background, background, progress)
                            # Fade old copy out before bringing new copy in. The photo
                            # stays visible throughout; two messages never overlap.
                            if progress < .30:
                                mixed = compose(mixed, old_overlay, 1 - progress / .30)
                            elif progress > .55:
                                mixed = compose(mixed, overlay, (progress - .55) / .45)
                            frame = mixed.tobytes()
                    process.stdin.write(frame)
            process.stdin.close()
            if process.wait() != 0:
                raise RuntimeError(f"Encoding failed; see {output_dir / 'encode.log'}")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
    return output


def verify(source, output):
    info = probe(output)
    video = next(stream for stream in info["streams"] if stream["codec_type"] == "video")
    if (video["width"], video["height"]) != SIZE or int(video["nb_frames"]) != FRAME_COUNT:
        raise ValueError("Unexpected video dimensions or frame count")
    if abs(float(info["format"]["duration"]) - DURATION) > .001:
        raise ValueError("Encoded duration changed")
    run("ffmpeg", "-v", "error", "-xerror", "-i", str(output), "-f", "null", "-")
    original, exported = audio_digest(source), audio_digest(output)
    if original != exported:
        raise ValueError("The copied soundtrack changed")
    return {"full_decode": "passed", "soundtrack_pcm_identical": True,
            "soundtrack_pcm_sha256": original, "ffprobe": info}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--frames-only", action="store_true")
    args = parser.parse_args()
    validate_source(args.source)
    frame_anchors()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    prepared, used = prepare(args.output_dir)
    credits = ["Crédits — UQAM, variante photographique plein écran", "",
               "Narration et musique : piste exacte du montage du 22 octobre 2026.",
               "Voix MAI-Voice-2 à +6 %, aucune nouvelle synthèse.",
               "Musique : Birds — Corbyn Kites.",
               "Source : https://happysoulmusic.com/audio/birds_-_corbyn_kites-mp3/",
               "Conditions : https://happysoulmusic.com/album/corbyn-kites/",
               "Usage de revue locale; autorisation de diffusion à confirmer.", ""]
    for name, record in used.items():
        credits.extend([name, "Crédit : " + record["credit"],
                        "Source : " + record["source_page"],
                        "Contexte : " + record.get("use", ""),
                        "Adaptation de cette version : recadrage 16:9, voile noir, texte blanc.",
                        "Retouches antérieures conservées pour les dérivés déjà répertoriés."])
        if record.get("license_url"):
            credits.append("Licence : " + record["license_url"])
        credits.append("")
    credits.extend(["Photos de vie de campus : aucune identification des participants comme",
                    "étudiants en mathématiques, enseignants ou membres des centres de recherche.",
                    "Aucune approbation du photographe ou de l’institution n’est impliquée."])
    (args.output_dir / "CREDITS.txt").write_text("\n".join(credits) + "\n", encoding="utf-8")
    manifest = {"status": "local_review_not_release", "source_sha256": sha256(args.source),
                "builder_sha256": sha256(__file__), "font_sha256": sha256(FONT),
                "source_video": str(args.source.resolve()), "duration_seconds": DURATION,
                "fps": FPS, "frame_count": FRAME_COUNT, "dimensions": SIZE,
                "audio_operation": "copy existing AAC stream; no TTS or mixing",
                "assets": used, "states": STATES, "frame_anchors": frame_anchors(),
                "layout_bounds": {state["id"]: item[3] for state, item in zip(STATES, prepared)},
                "full_listening": "not_performed", "visual_review": "pending",
                "institutional_approval": "not_established", "release_ready": False}
    if not args.frames_only:
        output = render(args.source, args.output_dir, prepared)
        manifest["verification"] = verify(args.source, output)
        manifest["output_sha256"] = sha256(output)
        manifest["output_file"] = output.name
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(args.output_dir, flush=True)


if __name__ == "__main__":
    main()
