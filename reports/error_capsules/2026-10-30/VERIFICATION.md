# MAT0339 — Vérification du premier lot de capsules

**Date : 30 octobre 2026.** Les quatorze capsules 44–57 disposent de sources
implémentées et de prévisualisations silencieuses vérifiées. Le
[plan éditorial](PLAN.md) donne les objectifs et références; le
[relevé vérifiable](verification.json) conserve les empreintes des sources,
des entrées de rendu et des vidéos, les durées et le périmètre des contrôles.

## Référence du livre

La référence intégrée est l’édition du **10 octobre 2026**, dans `main` au
commit `4d451c37d483d763e33683a7fb683d1e0fdde62d`. La révision du **17 octobre**,
commit `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, a été consultée dans la
PR #29, encore non fusionnée. Les anciennes pièces jointes d’août ne constituent
pas la source de ce lot. Le présent travail ne fusionne pas la PR #29.

## Résultats et portée

- **Quatorze rendus silencieux** de \(854\times480\) pixels, à 15 images par
  seconde, sans piste audio. Le décodage complet de chaque flux par FFmpeg a
  réussi. Les empreintes des sources et des entrées de chacun des quatorze
  rendus correspondent aux fichiers finaux.
- **320 états de construction** examinés : aucun candidat automatique de
  chevauchement entre textes ni de dépassement des marges. Cette mesure porte
  sur les états stables des animations, pas sur chaque image intermédiaire.
- **64 images extraites des vidéos finales effectivement inspectées**, dont
  des images de mouvement et des transitions choisies. Les nombres ci-dessous
  comptent les images inspectées, pas tous les fichiers extraits par les outils.
- **237 tests ciblés du cours et 24 sous-tests**, puis **64 tests du livre**,
  réussis. L’analyse syntaxique et Ruff sur les quatorze sources finales, la
  cohérence du catalogue et le contrôle des espaces Git ont réussi.
- Le **catalogue vidéo PDF de quatre pages** a été compilé et inspecté sans
  défaut de mise en page relevé.

Les tests ciblés du cours ont précédé les derniers déplacements d’étiquettes
dans les capsules 52 et 54. Après ces deux retouches de position, la validation
a porté sur leurs états de construction, de nouveaux rendus, les images
concernées et les empreintes finales. L’analyse syntaxique, Ruff et le contrôle
des espaces ont ensuite été répétés sur les sources finales.

## Mesures par capsule

La durée est celle de la **prévisualisation silencieuse**, arrondie au centième
de seconde. Elle ne mesure pas la durée d’une narration. Les valeurs exactes
et les empreintes sont dans le relevé JSON.

| No | Sujet | États de construction | Images finales inspectées | Durée de l’aperçu (s) |
|---|---|---:|---:|---:|
| 44 | Division par une inconnue | 21 | 3 | 37,73 |
| 45 | Signe du dénominateur | 28 | 7 | 46,87 |
| 46 | Pourcentages successifs | 23 | 4 | 41,40 |
| 47 | Logarithme d’une somme | 23 | 3 | 43,40 |
| 48 | Probabilités conditionnelles inversées | 29 | 7 | 75,20 |
| 49 | Indépendance et incompatibilité | 23 | 3 | 55,00 |
| 50 | Trajet et déplacement | 20 | 3 | 52,60 |
| 51 | Carré d’une matrice | 19 | 3 | 47,93 |
| 52 | Arrondi et optimum entier | 23 | 7 | 42,67 |
| 53 | Amplitude et maximum | 18 | 4 | 33,53 |
| 54 | Déphasage et factorisation | 18 | 4 | 33,53 |
| 55 | Fréquence et vitesse angulaire | 23 | 5 | 41,20 |
| 56 | Existence du temps de doublement | 25 | 5 | 45,27 |
| 57 | Période, longueur d’onde et propagation | 27 | 6 | 46,87 |
| **Total** | **14 capsules** | **320** | **64** | **643,20** |

Chaque capsule comporte une pause de réflexion de six secondes avant la
réponse à son exercice. Les textes enregistrés pour la narration totalisent
6 530 mots; ce comptage n’est ni une synthèse vocale ni une mesure de durée
parlée.

## Corrections issues de la vérification

- **52 :** la droite de niveau traversait une partie de l’étiquette du sommet
  \((8/3,8/3)\). L’étiquette a été déplacée vers la droite; la nouvelle vidéo a
  été inspectée au même instant, à 14,5 secondes.
- **54 :** une étiquette \(x=\pi/2\) touchait la courbe. Elle a été décalée
  vers la gauche, puis la capsule a été reconstruite, rendue et inspectée à
  nouveau.
- **53 :** les conditions de la formule générale de l’amplitude sont
  explicites : coefficient \(B\ne0\), avec la variable parcourant les réels.

Les anciens rendus restent des traces de travail; seules les vidéos identifiées
par les empreintes finales du relevé JSON fondent le bilan ci-dessus.

## Reproduire les contrôles

Depuis la racine du dépôt, avec l’environnement `.venv` installé. L’environnement
de rendu vérifié utilise Manim 0.19.0, manim-voiceover 0.3.7 et Pillow 11.3.0;
les autres versions enregistrées figurent dans le relevé JSON.

```bash
.venv/bin/python tools/course_catalog.py check
.venv/bin/python -m pytest -q \
  tests/test_course_catalog.py tests/test_render_curriculum.py \
  tests/test_course_timing.py tests/test_course_review.py \
  tests/test_public_workflow_policy.py tests/test_expanded_teaching.py \
  tests/test_teaching_revision.py tests/test_course_boundaries.py \
  tests/test_syllabus_expansion.py
PATH="$PWD/.venv/bin:$PATH" make -C books/mat0339 verify
git diff --check
```

Exemple de construction de la capsule 52 : `--entry` emploie l’index du
catalogue à partir de zéro. Choisir un nouveau dossier de sortie pour préserver
les vérifications précédentes.

```bash
MANIM_DISABLE_VOICEOVER=1 .venv/bin/python scripts/teaching_revision/review.py \
  --entry 51 --all-states --output review_artifacts/recheck_52/construction
```

Pour produire une nouvelle prévisualisation avec les empreintes, les mesures
de flux et les images de contrôle du moteur de rendu existant :

```bash
.venv/bin/python - <<'PY'
from datetime import datetime, timezone
from pathlib import Path
from scripts.render_syllabus_expansion import render_one
from tools.course_catalog import load_catalog

_, entries = load_catalog()
entry = next(e for e in entries if e['lesson_id'] == 'arrondi_optimum_entier')
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
output = Path('review_artifacts') / ('recheck_52_' + stamp)
output.mkdir(parents=True, exist_ok=False)
result = render_one(entry, output, 'silent', 'ql')
raise SystemExit(0 if result['render'] == 'passed' else 1)
PY
```

Le contrôle de décodage complet d’un MP4 s’effectue avec
`ffmpeg -v error -xerror -i CHEMIN_DU_MP4 -f null -`. Une inspection visuelle
requiert ensuite de regarder les images extraites aux instants pertinents;
un décodage réussi ne réalise pas cette inspection.

## Étapes restantes

La synthèse vocale, la vérification de la durée narrée, le visionnement intégral
du mouvement et l’écoute restent à réaliser. Les aperçus accélérés servent à
examiner la structure et la disposition des éléments. Le statut
`release_ready` reste `false`; aucune approbation de diffusion n’est déduite
des contrôles techniques. Les vidéos, images et caches générés restent hors
du code source Git.
