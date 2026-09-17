# Phase 2 visual audit — master status

Audit branch: `audit-video-visual-2026-09`

Production base: `0c4556ab07e8ae700c1556148374a83c0808cef1`

Fresh audit-render commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`

## Current audited status

| ID | Capsule | Render | Collisions | Boundaries | Visibility | Animation | Timing | Verdict |
|---|---|---|---|---|---|---|---|---|
| P01 | Variables et polynômes | PASS | **FAIL** | PASS | PASS* | **FAIL** | PASS* | **REVISE** |
| P02 | Inéquations et nombres négatifs | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P03 | Racine carrée et valeur absolue | **BLOCKED** | N/R | N/R | N/R | N/R | N/R | **BLOCKED** |
| P04 | Domaine et image d'une fonction | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P05 | Modèles affines et quadratiques | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P06 | Lire les propriétés d'un graphe | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P07 | Fonction définie par morceaux | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P08 | Opérations sur les fonctions | PASS | PASS | **FAIL** | **FAIL** | PASS | PASS* | **REVISE** |
| P09 | Composition de fonctions | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P10 | Fonction réciproque | **BLOCKED** | N/R | N/R | N/R | N/R | N/R | **BLOCKED** |
| P11 | Racines et hauteur zéro | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P12 | Multiplicité des racines | PASS | PASS* | **FAIL** | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P13 | Compléter le carré | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P14 | Exponentielles et logarithmes | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P15 | Principe fondamental du dénombrement | PASS | PASS | **FAIL** | **FAIL** | PASS | PASS* | **REVISE** |
| P16 | Permutation, arrangement et combinaison | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P17 | Répétitions en dénombrement | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P18 | Déplacement et composantes | PASS | PASS | **FAIL** | **FAIL** | PASS | PASS* | **REVISE** |
| P19 | Opérations sur les vecteurs | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P20 | Vecteurs dans R² et R³ | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |

Current tally for P01–P20: **10 REVISE, 8 PASS*, 2 BLOCKED**.

`N/R` = not reviewed because no auditable render exists.

`PASS*` = passed the silent low-quality structural visual stage but still requires the applicable final-resolution and/or narrated-master checks.

## Confirmed defects

| Finding | Severity | Capsule | Time | Summary |
|---|---|---|---|---|
| `VIS-P01-001` | P1 | P01 | 17.50–17.75 s | Outgoing formula annotations and incoming definition cross and become unreadable. |
| `VIS-P04-001` | P1 | P04 | 56.1–56.3 s; 64.6–64.8 s; ~66.2 s | Unrelated text morphs pass through scrambled, unreadable glyph states. |
| `VIS-P05-001` | P1 | P05 | ~31.0–31.4 s | Specific-to-general quadratic formula morph passes through a scrambled, unreadable state. |
| `VIS-P08-001` | P1 | P08 | ~7.5–8.5 s | The common-domain annotation extends beyond the right frame edge and is visibly truncated. |
| `VIS-P11-001` | P1 | P11 | ~31.4–31.7 s | Polynomial formula turns into opaque black glyph clusters during a transition. |
| `VIS-P12-001` | P1 | P12 | persistent | Main title reaches both horizontal frame edges and is clipped / lacks any safe margin. |
| `VIS-P12-002` | P1 | P12 | ~11.5 s | Formula transition produces a scrambled black intermediate state. |
| `VIS-P15-001` | P1 | P15 | ~2.5–4.5 s | Opening title is substantially wider than the frame and is clipped on both sides. |
| `VIS-P16-001` | P1 | P16 | ~16.4–16.6 s | Concrete arrangement calculation morphs into the general formula through scrambled glyphs. |
| `VIS-P17-001` | P1 | P17 | ~20.4–20.5 s | Section subtitle morph passes through a scrambled, unreadable state. |
| `VIS-P18-001` | P1 | P18 | ~12.5–13.5 s | Right-hand explanatory box extends off-frame and its sentence is truncated. |

## Render blockers

| Capsule | Blocker |
|---|---|
| P03 | Headless audit render reaches Azure credential setup and terminates before an MP4 is produced. |
| P10 | Scene layout validator aborts rendering: `[act 3] layout overlap between left derivation and inverse result`. |

## Audit discipline

- A scene is not visually passed from source inspection alone.
- Current low-quality renders are used to locate structural defects; small-text/thin-line concerns must be rechecked at final resolution.
- Narration synchronization is `NOT REVIEWED` in silent audit renders.
- Suspicious transitions are rescanned at sub-second cadence before being classified as defects.
- Only minimal confirmed evidence is retained; full videos and frame dumps remain temporary Actions artifacts.
