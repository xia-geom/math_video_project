# Math Video Project

Collection of Manim Community scenes for a French math-education video series, built with Manim Community and optional Azure TTS narration (whiteboard style, minimalist visuals). A self-driven project to produce rigorous, visually clean math explanations for French-speaking students.

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
# Low-quality preview (fast, auto-opens)
manim -pql scenes/geometrie_fr/pythagore_whiteboard_fr/pythagore_scene.py PythagoreAireFR

# High-quality export (1080p)
manim -pqh scenes/geometrie_fr/pythagore_whiteboard_fr/pythagore_scene.py PythagoreAireFR
```

### Audit a rendered video

```bash
./.venv/bin/python scripts/audit_video.py \
  --scene scenes/<category>/<topic>/<topic>_scene.py \
  --class <SceneClass> \
  --video dist/<SceneClass>/<SceneClass>.mp4 \
  --out reports/video_audits/<SceneClass>_audit.md

# Render low-quality silent previews and audit every CI production scene.
./.venv/bin/python scripts/audit_all_scenes.py
```

## Scene Organization

Production scenes use this layout:

```text
scenes/<category_slug>/<topic_slug>/<topic_slug>_scene.py
```

| Category | Topic folders |
|----------|---------------|
| `algebre_et_polynomes_fr/` | `annulation_fractions_fr/`, `complete_the_square_fr/`, `inequations_nombre_negatif_fr/`, `racine_carree_valeur_absolue_fr/`, `variables_et_polynomes/` |
| `fonctions_et_graphiques_fr/` | `composition_fonctions_fr/`, `fonction_par_morceaux_fr/`, `fonction_reciproque_fr/`, `fonctions_domaine_image_fr/`, `graph_properties_fr/`, `modeles_lineaires_quadratiques_fr/`, `multiplicite_racines_fr/`, `operations_fonctions_fr/`, `racine_hauteur_zero_fr/` |
| `exponentielles_et_logarithmes_fr/` | `logarithme_fr/` |
| `geometrie_fr/` | `circle_area/`, `pythagore_whiteboard_fr/` |
| `notations_fr/` | `sigma_sum_whiteboard_fr/` |
| `trigonometrie_fr/` | `trigonometry_fr/` |
| `identite_visuelle/` | `uqam_bumper/` |
| `erreurs_frequentes_fr/` | `composition_non_commutative_fr/`, `egalite_fonctions_fr/`, `equations_carre_solutions_parasites_fr/`, `implication_equivalence_fr/`, `racine_produit_hypotheses_fr/` |

## Featured Production Scenes

| Scene class | Directory | Description |
|-------------|-----------|-------------|
| `PythagoreAireFR` | `scenes/geometrie_fr/pythagore_whiteboard_fr/` | Pythagorean theorem — area proof, FR narration |
| `SigmaSommeBoucleFR` | `scenes/notations_fr/sigma_sum_whiteboard_fr/` | Sigma notation with worked example |
| `FonctionsDomaineImageFR` | `scenes/fonctions_et_graphiques_fr/fonctions_domaine_image_fr/` | Unified introduction to functions, domain, codomain, image, and graph reading |
| `ModelesLineairesQuadratiques` | `scenes/fonctions_et_graphiques_fr/modeles_lineaires_quadratiques_fr/` | Linear/affine and quadratic models |
| `VariablesEtPolynomes` | `scenes/algebre_et_polynomes_fr/variables_et_polynomes/` | Variables and polynomials |
| `GraphProperties` | `scenes/fonctions_et_graphiques_fr/graph_properties_fr/` | Graph properties (increasing, even/odd, periodic) |
| `CompleteTheSquare` | `scenes/algebre_et_polynomes_fr/complete_the_square_fr/` | Completing the square |
| `Logarithme` | `scenes/exponentielles_et_logarithmes_fr/logarithme_fr/` | Logarithm inverse, graphs, and properties |
| `SineCurveUnitCircle` | `scenes/trigonometrie_fr/trigonometry_fr/` | Sine curve from the unit circle |
| `CarreEtSolutionsParasitesFR` | `scenes/erreurs_frequentes_fr/equations_carre_solutions_parasites_fr/` | Squaring equations and rejecting extraneous solutions |
| `ImplicationEtEquivalenceFR` | `scenes/erreurs_frequentes_fr/implication_equivalence_fr/` | Implication, converse statements, and equivalence |
| `EgaliteDeFonctionsFR` | `scenes/erreurs_frequentes_fr/egalite_fonctions_fr/` | Equality of functions: formulas, domains, codomains, and images |
| `CompositionNonCommutativeFR` | `scenes/erreurs_frequentes_fr/composition_non_commutative_fr/` | Function composition: why order matters |
| `RacineProduitHypothesesFR` | `scenes/erreurs_frequentes_fr/racine_produit_hypotheses_fr/` | Product rule for square roots and its required hypotheses |

## Experiments

Early-stage or exploratory work lives under `experiments/`:
`fourier_series/`, `legendre_transform/`, `lorenz/`, `linear_transform/`, `law_of_cosines/`.

## Voiceover (Azure)

All scenes use **`fr-CA-SylvieNeural`** as the standard voice. Voice configuration is centralised in `tools/tts.py` — do not hardcode voice names or SSML helpers in individual scene files.

```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
# Pythagore scene (MP4 + SRT + uncompressed WAV)
./scenes/geometrie_fr/pythagore_whiteboard_fr/render_voice_ssml.sh
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
