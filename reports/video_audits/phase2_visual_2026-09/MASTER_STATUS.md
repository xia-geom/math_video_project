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

`N/R` = not reviewed because no auditable render exists.

`PASS*` = passed the silent low-quality structural visual stage but still requires the applicable final-resolution and/or narrated-master checks.

## Confirmed defects

| Finding | Severity | Capsule | Time | Summary |
|---|---|---|---|---|
| `VIS-P01-001` | P1 | P01 | 17.50–17.75 s | Outgoing formula annotations and incoming definition cross and become unreadable. |
| `VIS-P04-001` | P1 | P04 | 56.1–56.3 s; 64.6–64.8 s; ~66.2 s | Unrelated text morphs pass through scrambled, unreadable glyph states. |
| `VIS-P05-001` | P1 | P05 | ~31.0–31.4 s | The transform from the specific quadratic example to the general quadratic formula passes through a scrambled, unreadable formula state. |

## Render blockers

| Capsule | Blocker |
|---|---|
| P03 | Headless audit render reaches Azure credential setup and terminates at an interactive credential prompt. |

## Audit discipline

- A scene is not visually passed from source inspection alone.
- Current low-quality renders are used to locate structural defects; small-text/thin-line concerns must be rechecked at final resolution.
- Narration synchronization is `NOT REVIEWED` in silent audit renders.
- Only minimal confirmed evidence is retained; full videos and frame dumps remain temporary Actions artifacts.
