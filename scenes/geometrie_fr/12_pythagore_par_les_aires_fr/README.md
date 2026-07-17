# Pythagore Whiteboard (FR) - Manim

Animation courte (environ 40s) qui démontre le théorème de Pythagore par une preuve d'aire.

- fond blanc
- traits noirs
- un seul accent bleu
- sous-titres/captions concis
- voix off FR via Azure Speech (manim-voiceover)

## Files

- `12_pythagore_par_les_aires_fr_scene.py`: scène Manim (`PythagoreAireFR`)
- `subtitles_fr.srt`: sous-titres externes concis
- `.env` (optionnel): `SPEECH_KEY` et `SPEECH_REGION`

## Render

Preview rapide:

```bash
./.venv/bin/manim -pql scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py PythagoreAireFR
```

Rendu avec voix Azure:

```bash
./scripts/render.sh scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py PythagoreAireFR ql
```

1080p:

```bash
./.venv/bin/manim -pqh scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py PythagoreAireFR -r 1920,1080
```

Sortie vidéo attendue:

- `media/videos/12_pythagore_par_les_aires_fr_scene/480p15/PythagoreAireFR.mp4` (preview)
- `media/videos/12_pythagore_par_les_aires_fr_scene/1080p60/PythagoreAireFR.mp4` (haute qualité)
- `scenes/geometrie_fr/12_pythagore_par_les_aires_fr/PythagoreAireFR_uncompressed.wav` (audio PCM non compressé)
