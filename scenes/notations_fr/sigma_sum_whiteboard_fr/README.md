# Sigma Whiteboard (FR) - Manim

This folder contains a full Manim scene for a ~90-second educational whiteboard-style video in French about sigma notation with a worked numeric example.

- 16:9 layout
- white background + black writing
- calm pacing, minimalist animation
- French subtitles integrated on-screen and as subcaption track
- French voiceover audio included (no background music)

## Files

- `sigma_sum_scene.py`: main Manim scene (`SigmaSommeBoucleFR`)
- `narration_fr.txt`: narration script in French
- `subtitles_fr.srt`: external subtitle file matching the timeline
- `assets/voix_off_fr.wav`: generated French voiceover used by the scene
- `assets/tts_script_fr.txt`: TTS source text used for voiceover generation
- `generate_voiceover.sh`: regenerate the French TTS voiceover

## Voiceover input

The scene auto-loads the first file found among:

- `assets/voix_off_fr.wav`
- `assets/voix_off_fr.mp3`
- `assets/voiceover_fr.wav`
- `assets/voiceover_fr.mp3`

The included `assets/voix_off_fr.wav` is already wired in.

To regenerate it on macOS:

```bash
./sigma_sum_whiteboard_fr/generate_voiceover.sh
```

## Render commands

Low quality preview:

```bash
./.venv/bin/manim -pql sigma_sum_whiteboard_fr/sigma_sum_scene.py SigmaSommeBoucleFR
```

1080p render (16:9):

```bash
./.venv/bin/manim -pqh sigma_sum_whiteboard_fr/sigma_sum_scene.py SigmaSommeBoucleFR -r 1920,1080
```

## Notes

- Keep narration around 90 seconds for best sync.
- On-screen subtitles are already added by the scene.
- `subtitles_fr.srt` can also be used in post-production if needed.
- The current version uses a concrete example: `\sum_{i=0}^{4}(2i+1) = 25`.
