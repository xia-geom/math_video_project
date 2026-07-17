# Math Video Project

Collection of Manim Community scenes for a French math-education video series, with optional Azure TTS narration. The project favors rigorous explanations, minimalist whiteboard visuals, progressive animation, and concise French captions.

## Project Status

| Area | Current state |
|------|---------------|
| Main curriculum | 14 numbered scenes in pedagogical order |
| Common mathematical errors | 5 scenes under `scenes/erreurs_frequentes_fr/` |
| All scene sources | 25 Python scene files under `scenes/` |
| CI smoke-render registry | 11 scenes |
| Exploratory work | 8 Python sketches split between `experiments/sketches/` and `experiments/wip/` |
| Video audit | Local, network-free audit tooling with reports under `reports/video_audits/` |

The numbered folders `01_...` through `14_...` define the recommended viewing order. Scene class names remain stable and are used as the public render interface and output-directory names.

The CI matrix currently covers 10 of the 14 numbered curriculum scenes plus the supplementary `CircleAreaFR` scene. The four curriculum scenes not yet registered in CI are identified in the common-errors section below.

## Setup

### Prerequisites

Install these system-level tools before the Python steps:

| Tool | Purpose | Install |
|------|---------|---------|
| Python ≥ 3.11 | Runtime | [python.org](https://www.python.org/downloads/) or `brew install python` |
| LaTeX (TeX Live / MiKTeX) | Rendering math formulas | `brew install --cask mactex` (macOS) / `apt install texlive-full` (Linux) |
| FFmpeg | Video encoding | `brew install ffmpeg` / `apt install ffmpeg` |
| Cairo & Pango | Vector graphics | `brew install cairo pango` / `apt install libcairo2-dev libpango1.0-dev` |

### Install

```bash
# 1. Clone and enter the repo
git clone <repo-url>
cd math_video_project

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# .venv\Scripts\activate       # Windows

# 3. Install all Python dependencies
pip install -e .

# For development tools (linter, type-checker):
pip install -e ".[dev]"
```

### Environment variables (voiceover only)

Scenes with Azure TTS narration need two credentials.  
Copy the example file and fill in your values:

```bash
cp .env.example .env
# then edit .env with your Azure Speech key and region
```

| Variable | Description |
|----------|-------------|
| `SPEECH_KEY` | Azure Cognitive Services Speech key |
| `SPEECH_REGION` | Azure region (e.g. `eastus`, `canadacentral`) |

Scenes without voiceover work fine without a `.env` file.

### Render a scene

```bash
# Low-quality preview copied to dist/PythagoreAireFR/
./scripts/render.sh \
  scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py \
  PythagoreAireFR ql

# High-quality export (1080p60)
./scripts/render.sh \
  scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py \
  PythagoreAireFR qh
```

The quality argument is `ql` (480p15), `qm` (720p30), or `qh` (1080p60). The helper clears stale outputs and writes the final MP4, plus SRT and uncompressed WAV outputs when available, to `dist/<SceneClass>/`.

### Audit a rendered video

```bash
./.venv/bin/python scripts/audit_video.py \
  --scene scenes/<category>/<topic>/<topic>_scene.py \
  --class <SceneClass> \
  --video dist/<SceneClass>/<SceneClass>.mp4 \
  --out reports/video_audits/<SceneClass>_audit.md

# Render low-quality silent previews and audit all 11 CI-registered scenes.
./.venv/bin/python scripts/audit_all_scenes.py

# Re-audit existing videos without rendering.
./.venv/bin/python scripts/audit_all_scenes.py --no-render
```

The latest batch summary is stored in [`reports/video_audits/INDEX.md`](reports/video_audits/INDEX.md).

## Scene Organization

Scene sources typically use this layout:

```text
scenes/<category_slug>/<topic_slug>/<topic_slug>_scene.py
```

| Category | Topic folders |
|----------|---------------|
| `algebre_et_polynomes_fr/` | `02_variables_et_polynomes_fr/`, `07_completer_le_carre_fr/`, `annulation_fractions_fr/`, `inequations_nombre_negatif_fr/`, `racine_carree_valeur_absolue_fr/` |
| `fonctions_et_graphiques_fr/` | `04_domaine_et_image_fr/`, `06_modeles_affines_et_quadratiques_fr/`, `09_lire_les_proprietes_d_un_graphe_fr/`, `composition_fonctions_fr/`, `fonction_par_morceaux_fr/`, `fonction_reciproque_fr/`, `multiplicite_racines_fr/`, `operations_fonctions_fr/`, `racine_hauteur_zero_fr/` |
| `exponentielles_et_logarithmes_fr/` | `11_logarithmes_fr/` |
| `geometrie_fr/` | `12_pythagore_par_les_aires_fr/`, `circle_area/` |
| `notations_fr/` | `14_notation_sigma_fr/` |
| `trigonometrie_fr/` | `13_du_cercle_au_sinus_fr/` |
| `identite_visuelle/` | `uqam_bumper/` |
| `erreurs_frequentes_fr/` | `01_implication_et_equivalence_fr/`, `03_racine_d_un_produit_fr/`, `05_egalite_de_fonctions_fr/`, `08_solutions_parasites_fr/`, `10_ordre_de_composition_fr/` |

## Common Mathematical Errors

The `scenes/erreurs_frequentes_fr/` category contains lessons intentionally organized around a tempting but invalid mathematical step. It is not a catch-all folder for every scene that mentions a mistake. Each lesson exposes the misconception, gives a counterexample or failed argument, and finishes with a reliable replacement method.

| No. | Lesson | Scene class | Misconception addressed |
|----:|--------|-------------|-------------------------|
| 01 | Implication and equivalence | `ImplicationEtEquivalenceFR` | Treating an implication as though its converse were automatic |
| 03 | Square root of a product | `RacineProduitHypothesesFR` | Using `sqrt(ab) = sqrt(a)sqrt(b)` without checking its hypotheses |
| 05 | Equality of functions | `EgaliteDeFonctionsFR` | Deciding equality from a formula or image alone, without the domain and codomain |
| 08 | Extraneous solutions | `CarreEtSolutionsParasitesFR` | Assuming that squaring an equation is a reversible step |
| 10 | Order of composition | `CompositionNonCommutativeFR` | Assuming `f ∘ g = g ∘ f` because ordinary multiplication is commutative |

At present, scene 03 is in the CI smoke-render matrix; scenes 01, 05, 08, and 10 are part of the curriculum but are not yet registered in that matrix.

## Main Curriculum — Pedagogical Order

| No. | Scene class | Scene file | Description |
|----:|-------------|------------|-------------|
| 01 | `ImplicationEtEquivalenceFR` | `scenes/erreurs_frequentes_fr/01_implication_et_equivalence_fr/01_implication_et_equivalence_fr_scene.py` | Implication, converse statements, and equivalence |
| 02 | `VariablesEtPolynomes` | `scenes/algebre_et_polynomes_fr/02_variables_et_polynomes_fr/02_variables_et_polynomes_fr_scene.py` | Variables and polynomials |
| 03 | `RacineProduitHypothesesFR` | `scenes/erreurs_frequentes_fr/03_racine_d_un_produit_fr/03_racine_d_un_produit_fr_scene.py` | Product rule for square roots and its required hypotheses |
| 04 | `FonctionsDomaineImageFR` | `scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py` | Functions, domain, codomain, image, and graph reading |
| 05 | `EgaliteDeFonctionsFR` | `scenes/erreurs_frequentes_fr/05_egalite_de_fonctions_fr/05_egalite_de_fonctions_fr_scene.py` | Equality of functions: formulas, domains, codomains, and images |
| 06 | `ModelesLineairesQuadratiques` | `scenes/fonctions_et_graphiques_fr/06_modeles_affines_et_quadratiques_fr/06_modeles_affines_et_quadratiques_fr_scene.py` | Linear/affine and quadratic models |
| 07 | `CompleteTheSquare` | `scenes/algebre_et_polynomes_fr/07_completer_le_carre_fr/07_completer_le_carre_fr_scene.py` | Completing the square |
| 08 | `CarreEtSolutionsParasitesFR` | `scenes/erreurs_frequentes_fr/08_solutions_parasites_fr/08_solutions_parasites_fr_scene.py` | Squaring equations and rejecting extraneous solutions |
| 09 | `GraphProperties` | `scenes/fonctions_et_graphiques_fr/09_lire_les_proprietes_d_un_graphe_fr/09_lire_les_proprietes_d_un_graphe_fr_scene.py` | Graph properties (increasing, even/odd, periodic) |
| 10 | `CompositionNonCommutativeFR` | `scenes/erreurs_frequentes_fr/10_ordre_de_composition_fr/10_ordre_de_composition_fr_scene.py` | Function composition: why order matters |
| 11 | `Logarithme` | `scenes/exponentielles_et_logarithmes_fr/11_logarithmes_fr/11_logarithmes_fr_scene.py` | Logarithm inverse, graphs, and properties |
| 12 | `PythagoreAireFR` | `scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py` | Pythagorean theorem — area proof, FR narration |
| 13 | `SineCurveUnitCircle` | `scenes/trigonometrie_fr/13_du_cercle_au_sinus_fr/13_du_cercle_au_sinus_fr_scene.py` | Sine curve from the unit circle |
| 14 | `SigmaSommeBoucleFR` | `scenes/notations_fr/14_notation_sigma_fr/14_notation_sigma_fr_scene.py` | Sigma notation with worked example |

## Experiments

Early-stage work is kept outside production scenes:

- `experiments/sketches/`: Fourier series, sorting, hyperbolic cone-to-cusp, linear transformations, and the Lorenz system.
- `experiments/wip/`: hairy-ball theorem, Legendre transform, and law of cosines.
- `archive/`: superseded scenes and retired utilities kept for historical reference.

## Voiceover (Azure)

Azure-narrated scenes use **`fr-CA-SylvieNeural`** as the standard voice. Voice configuration is centralised in `tools/tts.py`; individual scenes should not hardcode voice names or duplicate shared SSML helpers. The Sigma scene can also use its prerecorded local narration asset.

```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
# Pythagore scene
./scripts/render.sh scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py PythagoreAireFR qh
```

To switch voice at render time:

```bash
MANIM_VOICE=fr-CA-JeanNeural manim -pql scenes/.../my_scene.py MyScene
```

Available voices (all tuned to `-14%` prosody rate):

| Voice ID | Character |
|----------|-----------|
| `fr-CA-SylvieNeural` | Female — series default |
| `fr-CA-JeanNeural` | Male, natural delivery |
| `fr-CA-AntoineNeural` | Male, expressive |
| `fr-CA-ThierryNeural` | Male, clear diction |

## TTS / SSML utilities (`tools/tts.py`)

All pronunciation logic lives in a single module. Import what you need:

```python
from tools.tts import VOICE_ID, VOICE_RATE, ssml, char, chars, strip_ssml
from tools.tts import ET, PLUS, A, B, C, P, Q, T, X, Y
```

| Export | Purpose |
|--------|---------|
| `VOICE_CONFIGS` | Dict mapping voice IDs to prosody rates |
| `VOICE_ID` / `VOICE_RATE` | Resolved from `$MANIM_VOICE` env var |
| `ssml(text, rate)` | Wraps text in `<lang xml:lang='fr-CA'><prosody rate='...'>` |
| `char(c)` | `<say-as interpret-as='characters'>c</say-as>` |
| `chars(*letters)` | Space-joined `char()` tokens for multi-letter products |
| `strip_ssml(text)` | Strips all XML tags — use for `subcaption=` |
| `ET` | French liaison break: `<break time='150ms'/> et <break time='100ms'/>` |
| `PLUS` | Forces /plys/ IPA — prevents Azure dropping the final *s* |
| `A B C P Q T X Y` | Pre-built `char()` tokens for common math variables |
