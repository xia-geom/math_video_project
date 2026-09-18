# Math Video Project

Collection of Manim Community scenes for a French math-education video series, with optional Azure TTS narration. The project favors rigorous explanations, minimalist whiteboard visuals, progressive animation, and concise French captions.

## Project Status

| Area | Current state |
|------|---------------|
| Main programme | 27 numbered videos in pedagogical order |
| Common errors | 6 videos in a separate collection |
| All scene sources | 34 Python scene files under `scenes/` |
| CI smoke-render registry | 20 scenes |
| Exploratory work | 8 Python sketches split between `experiments/sketches/` and `experiments/wip/` |
| Video audit | Local, network-free audit tooling with reports under `reports/video_audits/` |

The programme combines the 24 syllabus lessons with two geometry lessons and sigma notation as positions 25–27. The six common-error lessons remain in their own collection. Scene class names remain stable and are used as the public render interface and output-directory names.

The manifest at `curriculum/programme_principal_fr.yaml` is the source of truth for ordering, packaging, Drive routing, and syllabus coverage.

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
# Low-quality preview copied to dist/16_pythagore_par_les_aires_fr/
./scripts/render.sh \
  scenes/geometrie_fr/16_pythagore_par_les_aires_fr/16_pythagore_par_les_aires_fr_scene.py \
  PythagoreAireFR ql

# High-quality export (1080p60)
./scripts/render.sh \
  scenes/geometrie_fr/16_pythagore_par_les_aires_fr/16_pythagore_par_les_aires_fr_scene.py \
  PythagoreAireFR qh
```

The quality argument is `ql` (480p15), `qm` (720p30), or `qh` (1080p60). The helper clears stale outputs and writes the final MP4, plus SRT and uncompressed WAV outputs when available, to `dist/<topic_slug>/`. Manim still renders the class supplied on the command line; only the deliverable names come from the scene's parent folder.

### Render the curriculum

```bash
# Silent 480p previews of the nine newly integrated lessons
./.venv/bin/python scripts/render_curriculum.py \
  --track programme --quality ql --render --disable-voiceover \
  --order 15 --order 16 --order 17 \
  --order 18 --order 19 --order 20 --order 21 --order 22 --order 23

# Resumable narrated 1080p render; existing geometry and notation renders are reused
./.venv/bin/python scripts/render_curriculum.py \
  --track programme --quality qh --render --resume

# Validate and build the 27-video programme plus the six common-error videos
./.venv/bin/python scripts/render_curriculum.py \
  --track all --quality qh --validate --package --drive
```

Local packages are written to `dist/programme_principal_fr/` and
`dist/erreurs_frequentes_fr/`. Drive receives only MP4 files, under
`Math Video Project/1 - Programme principal/` and `2 - Erreurs fréquentes/`.
Unclassified scene renders remain local.

### Audit a rendered video

```bash
./.venv/bin/python scripts/audit_video.py \
  --scene scenes/<category>/<topic>/<topic>_scene.py \
  --class <SceneClass> \
  --video dist/<topic_slug>/<topic_slug>.mp4 \
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
| `algebre_et_polynomes_fr/` | `01_variables_et_polynomes_fr/`, `02_inequations_nombre_negatif_fr/`, `03_racine_carree_et_valeur_absolue_fr/`, `13_completer_le_carre_fr/` |
| `fonctions_et_graphiques_fr/` | `04_domaine_et_image_fr/`, `05_modeles_affines_et_quadratiques_fr/`, `06_lire_les_proprietes_d_un_graphe_fr/`, `07_fonction_par_morceaux_fr/`, `08_operations_sur_les_fonctions_fr/`, `09_composition_de_fonctions_fr/`, `10_fonction_reciproque_fr/`, `11_racines_et_hauteur_zero_fr/`, `12_multiplicite_des_racines_fr/` |
| `exponentielles_et_logarithmes_fr/` | `14_logarithmes_fr/` |
| `probabilites_fr/` | `15_principe_fondamental_du_denombrement_fr/`, `16_permutation_arrangement_combinaison_fr/`, `17_repetitions_en_denombrement_fr/` |
| `vecteurs_fr/` | `18_deplacement_et_composantes_fr/`, `19_operations_sur_les_vecteurs_fr/`, `20_vecteurs_dans_r2_et_r3_fr/` |
| `matrices_fr/` | `21_lire_et_appliquer_une_matrice_fr/`, `22_operations_sur_les_matrices_fr/`, `23_determinant_et_matrice_inverse_fr/` |
| `geometrie_fr/` | `15_aire_du_cercle_fr/`, `16_pythagore_par_les_aires_fr/` |
| `notations_fr/` | `18_notation_sigma_fr/` |
| `trigonometrie_fr/` | `24_du_cercle_au_sinus_fr/` |
| `identite_visuelle/` | `00_identite_uqam/` |
| `erreurs_frequentes_fr/` | `01_implication_et_equivalence_fr/`, `02_racine_d_un_produit_fr/`, `03_egalite_de_fonctions_fr/`, `04_solutions_parasites_fr/`, `05_ordre_de_composition_fr/`, `06_annulation_dans_les_fractions_fr/` |

## Common Mathematical Errors

The `scenes/erreurs_frequentes_fr/` category contains lessons intentionally organized around a tempting but invalid mathematical step. It is not a catch-all folder for every scene that mentions a mistake. Each lesson exposes the misconception, gives a counterexample or failed argument, and finishes with a reliable replacement method.

| No. | Lesson | Scene class | Misconception addressed |
|----:|--------|-------------|-------------------------|
| 01 | Implication and equivalence | `ImplicationEtEquivalenceFR` | Treating an implication as though its converse were automatic |
| 02 | Square root of a product | `RacineProduitHypothesesFR` | Using `sqrt(ab) = sqrt(a)sqrt(b)` without checking its hypotheses |
| 03 | Equality of functions | `EgaliteDeFonctionsFR` | Deciding equality from a formula or image alone, without the domain and codomain |
| 04 | Extraneous solutions | `CarreEtSolutionsParasitesFR` | Assuming that squaring an equation is a reversible step |
| 05 | Order of composition | `CompositionNonCommutativeFR` | Assuming `f ∘ g = g ∘ f` because ordinary multiplication is commutative |
| 06 | Cancellation in fractions | `AnnulationFractionsFR` | Cancelling matching terms across addition or subtraction instead of complete factors |

At present, common-error scene 02 is in the CI smoke-render matrix; scenes 01 and 03–06 are not yet registered.

## Main Curriculum — Pedagogical Order

| No. | Scene class | Scene file | Description |
|----:|-------------|------------|-------------|
| 01 | `VariablesEtPolynomes` | `scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py` | Variables and polynomials |
| 02 | `InequationsNombreNegatifFR` | `scenes/algebre_et_polynomes_fr/02_inequations_nombre_negatif_fr/02_inequations_nombre_negatif_fr_scene.py` | Inequalities and multiplication by a negative number |
| 03 | `RacineCarreeValeurAbsolueFR` | `scenes/algebre_et_polynomes_fr/03_racine_carree_et_valeur_absolue_fr/03_racine_carree_et_valeur_absolue_fr_scene.py` | Square roots and absolute value |
| 04 | `FonctionsDomaineImageFR` | `scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py` | Functions, domain, codomain, image, and graph reading |
| 05 | `ModelesLineairesQuadratiques` | `scenes/fonctions_et_graphiques_fr/05_modeles_affines_et_quadratiques_fr/05_modeles_affines_et_quadratiques_fr_scene.py` | Linear/affine and quadratic models |
| 06 | `GraphProperties` | `scenes/fonctions_et_graphiques_fr/06_lire_les_proprietes_d_un_graphe_fr/06_lire_les_proprietes_d_un_graphe_fr_scene.py` | Graph properties (increasing, even/odd, periodic) |
| 07 | `FonctionParMorceauxFR` | `scenes/fonctions_et_graphiques_fr/07_fonction_par_morceaux_fr/07_fonction_par_morceaux_fr_scene.py` | Piecewise-defined functions |
| 08 | `OperationsFonctionsFR` | `scenes/fonctions_et_graphiques_fr/08_operations_sur_les_fonctions_fr/08_operations_sur_les_fonctions_fr_scene.py` | Arithmetic operations on functions |
| 09 | `CompositionFonctionsFR` | `scenes/fonctions_et_graphiques_fr/09_composition_de_fonctions_fr/09_composition_de_fonctions_fr_scene.py` | Function composition |
| 10 | `FonctionReciproqueFR` | `scenes/fonctions_et_graphiques_fr/10_fonction_reciproque_fr/10_fonction_reciproque_fr_scene.py` | Inverse functions |
| 11 | `RacineHauteurZeroFR` | `scenes/fonctions_et_graphiques_fr/11_racines_et_hauteur_zero_fr/11_racines_et_hauteur_zero_fr_scene.py` | Roots as graph intersections with height zero |
| 12 | `MultipliciteRacinesFR` | `scenes/fonctions_et_graphiques_fr/12_multiplicite_des_racines_fr/12_multiplicite_des_racines_fr_scene.py` | Multiplicity of polynomial roots |
| 13 | `CompleteTheSquare` | `scenes/algebre_et_polynomes_fr/13_completer_le_carre_fr/13_completer_le_carre_fr_scene.py` | Completing the square |
| 14 | `Logarithme` | `scenes/exponentielles_et_logarithmes_fr/14_logarithmes_fr/14_logarithmes_fr_scene.py` | Logarithm inverse, graphs, and properties |
| 15 | `PrincipeFondamentalDenombrementFR` | `scenes/probabilites_fr/15_principe_fondamental_du_denombrement_fr/15_principe_fondamental_du_denombrement_fr_scene.py` | Fundamental counting principle |
| 16 | `PermutationArrangementCombinaisonFR` | `scenes/probabilites_fr/16_permutation_arrangement_combinaison_fr/16_permutation_arrangement_combinaison_fr_scene.py` | Permutations, arrangements, and combinations |
| 17 | `RepetitionsDenombrementFR` | `scenes/probabilites_fr/17_repetitions_en_denombrement_fr/17_repetitions_en_denombrement_fr_scene.py` | Reusable choices and repeated objects |
| 18 | `VecteursDeplacementComposantesFR` | `scenes/vecteurs_fr/18_deplacement_et_composantes_fr/18_deplacement_et_composantes_fr_scene.py` | Displacements, components, and norm |
| 19 | `OperationsVecteursFR` | `scenes/vecteurs_fr/19_operations_sur_les_vecteurs_fr/19_operations_sur_les_vecteurs_fr_scene.py` | Vector operations |
| 20 | `VecteursR2R3FR` | `scenes/vecteurs_fr/20_vecteurs_dans_r2_et_r3_fr/20_vecteurs_dans_r2_et_r3_fr_scene.py` | Vectors, distances, and midpoints in R² and R³ |
| 21 | `MatricesLireEtAppliquerFR` | `scenes/matrices_fr/21_lire_et_appliquer_une_matrice_fr/21_lire_et_appliquer_une_matrice_fr_scene.py` | Reading and applying a matrix |
| 22 | `OperationsMatricesFR` | `scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py` | Matrix operations and composition |
| 23 | `DeterminantEtMatriceInverseFR` | `scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py` | Determinants and inverse matrices |
| 24 | `SineCurveUnitCircle` | `scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py` | Sine curve from the unit circle |
| 25 | `CircleAreaFR` | `scenes/geometrie_fr/15_aire_du_cercle_fr/15_aire_du_cercle_fr_scene.py` | Visual derivation of the circle-area formula |
| 26 | `PythagoreAireFR` | `scenes/geometrie_fr/16_pythagore_par_les_aires_fr/16_pythagore_par_les_aires_fr_scene.py` | Geometric proof of the Pythagorean theorem |
| 27 | `SigmaSommeBoucleFR` | `scenes/notations_fr/18_notation_sigma_fr/18_notation_sigma_fr_scene.py` | Reading and expanding sigma notation |

Geometry and sigma notation occupy positions 25–27 of the programme manifest. The six common-error lessons use their own 01–06 sequence.

## Experiments

Early-stage work is kept outside production scenes:

- `experiments/sketches/`: Fourier series, sorting, hyperbolic cone-to-cusp, linear transformations, and the Lorenz system.
- `experiments/wip/`: hairy-ball theorem, Legendre transform, and law of cosines.
- `archive/`: superseded scenes and retired utilities kept for historical reference.

## Teaching production standard

See [docs/TEACHING_STANDARD.md](docs/TEACHING_STANDARD.md) for legible panels, sequential explanations, the MAI teaching profile, measured bookmark timing, and the single UQAM opening.

## Voiceover (Azure)

Teaching scenes now use the existing **`MAI-Voice-2`** profile at **`-3%`**, through `tools/teaching_voiceover.py`, as their standard voice. Voice configuration is centralised in `tools/tts.py`; individual scenes should not hardcode voice names or duplicate shared SSML helpers. The Sigma scene can also use its prerecorded local narration asset.

```bash
export SPEECH_KEY=...
export SPEECH_REGION=...
# Pythagore scene
./scripts/render.sh scenes/geometrie_fr/16_pythagore_par_les_aires_fr/16_pythagore_par_les_aires_fr_scene.py PythagoreAireFR qh
```

To switch voice at render time:

```bash
MANIM_VOICE=fr-CA-JeanNeural manim -pql scenes/.../my_scene.py MyScene
```

To explicitly select the shared MAI teaching profile, use the friendly
`MAI-Voice-2` selector. The project maps it to the published French voice
`fr-FR-Soleil:MAI-Voice-2` and requires the configured Speech resource to be
in `canadacentral`:

```bash
SPEECH_REGION=canadacentral MANIM_VOICE=MAI-Voice-2 \
  ./scripts/render.sh scenes/.../my_scene.py MyScene ql
```

MAI-Voice-2 uses Microsoft's Azure Speech SDK and SSML, just like the existing
neural voices. Its neutral profile uses a moderately paced `-3%` rate and the
existing punctuation/SSML pauses so the scene's measured narration timing and
video synchronization continue to drive the render. The published French MAI
voice has no calm or narration-specific style, so the neutral setting is
intentional and leaves varied intonation to MAI's native delivery. MAI-Voice-2
is currently in public preview and has no service-level agreement. See Microsoft's
[MAI-Voice documentation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/mai-voices)
and [Azure Speech region matrix](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/regions).

Available voices:

| Selector / voice ID | Rate | Character |
|---------------------|------|-----------|
| `fr-CA-SylvieNeural` | `-14%` | Legacy profile; explicit override |
| `fr-CA-JeanNeural` | `-14%` | Male, natural delivery |
| `fr-CA-AntoineNeural` | `-14%` | Male, expressive |
| `fr-CA-ThierryNeural` | `-14%` | Male, clear diction |
| `MAI-Voice-2` (`fr-FR-Soleil:MAI-Voice-2`) | `-3%` | Female, high-fidelity long-form narration |

## TTS / SSML utilities (`tools/tts.py`)

All pronunciation logic lives in a single module. Import what you need:

```python
from tools.tts import VOICE_ID, VOICE_RATE, ssml, char, chars, strip_ssml
from tools.tts import ET, PLUS, A, B, C, P, Q, T, X, Y
```

| Export | Purpose |
|--------|---------|
| `VOICE_CONFIGS` | Dict mapping voice IDs to prosody rates |
| `VOICE_ID` / `VOICE_RATE` | Resolved from `$MANIM_VOICE`; supports the `MAI-Voice-2` alias |
| `azure_service_kwargs()` | Bridges environment-only Azure settings and preserves the 48 kHz output profile |
| `ssml(text, rate)` | Wraps text in the selected voice locale and prosody rate |
| `char(c)` | `<say-as interpret-as='characters'>c</say-as>` |
| `chars(*letters)` | Space-joined `char()` tokens for multi-letter products |
| `strip_ssml(text)` | Strips all XML tags — use for `subcaption=` |
| `ET` | French liaison break: `<break time='150ms'/> et <break time='100ms'/>` |
| `PLUS` | Forces /plys/ IPA — prevents Azure dropping the final *s* |
| `A B C P Q T X Y` | Pre-built `char()` tokens for common math variables |
