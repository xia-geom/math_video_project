# Pythagore Whiteboard (FR) - Manim

Animation courte (environ 40s) qui démontre le théorème de Pythagore par une preuve d'aire.

- fond blanc
- traits noirs
- un seul accent bleu
- sous-titres/captions concis
- voix off FR via Azure Speech (manim-voiceover)

## Files

- `pythagore_scene.py`: scène Manim (`PythagoreAireFR`)
- `subtitles_fr.srt`: sous-titres externes concis
- `.env` (optionnel): `SPEECH_KEY` et `SPEECH_REGION`

## Render

Preview rapide:

```bash
./.venv/bin/manim -pql pythagore_whiteboard_fr/pythagore_scene.py PythagoreAireFR
```

Rendu voix Azure + SSML + WAV non compressé:

```bash
./pythagore_whiteboard_fr/render_voice_ssml.sh
```

1080p:

```bash
./.venv/bin/manim -pqh pythagore_whiteboard_fr/pythagore_scene.py PythagoreAireFR -r 1920,1080
```

Sortie vidéo attendue:

- `media/videos/pythagore_scene/480p15/PythagoreAireFR.mp4` (preview)
- `media/videos/pythagore_scene/1080p60/PythagoreAireFR.mp4` (haute qualité)
- `pythagore_whiteboard_fr/PythagoreAireFR_uncompressed.wav` (audio PCM non compressé)
