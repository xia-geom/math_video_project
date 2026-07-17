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
manim -pql scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py PythagoreAireFR

# High-quality export (1080p)
manim -pqh scenes/geometrie_fr/12_pythagore_par_les_aires_fr/12_pythagore_par_les_aires_fr_scene.py PythagoreAireFR
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
| `algebre_et_polynomes_fr/` | `02_variables_et_polynomes_fr/`, `07_completer_le_carre_fr/`, `annulation_fractions_fr/`, `inequations_nombre_negatif_fr/`, `racine_carree_valeur_absolue_fr/` |
| `fonctions_et_graphiques_fr/` | `04_domaine_et_image_fr/`, `06_modeles_affines_et_quadratiques_fr/`, `09_lire_les_proprietes_d_un_graphe_fr/`, `composition_fonctions_fr/`, `fonction_par_morceaux_fr/`, `fonction_reciproque_fr/`, `multiplicite_racines_fr/`, `operations_fonctions_fr/`, `racine_hauteur_zero_fr/` |
| `exponentielles_et_logarithmes_fr/` | `11_logarithmes_fr/` |
| `geometrie_fr/` | `12_pythagore_par_les_aires_fr/`, `circle_area/` |
| `notations_fr/` | `14_notation_sigma_fr/` |
| `trigonometrie_fr/` | `13_du_cercle_au_sinus_fr/` |
| `identite_visuelle/` | `uqam_bumper/` |
| `erreurs_frequentes_fr/` | `01_implication_et_equivalence_fr/`, `03_racine_d_un_produit_fr/`, `05_egalite_de_fonctions_fr/`, `08_solutions_parasites_fr/`, `10_ordre_de_composition_fr/` |

## Featured Production Scenes — Pedagogical Order

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

Early-stage or exploratory work lives under `experiments/`:
`fourier_series/`, `legendre_transform/`, `lorenz/`, `linear_transform/`, `law_of_cosines/`.

## Voiceover (Azure)

All scenes use **`fr-CA-SylvieNeural`** as the standard voice. Voice configuration is centralised in `tools/tts.py` — do not hardcode voice names or SSML helpers in individual scene files.

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
