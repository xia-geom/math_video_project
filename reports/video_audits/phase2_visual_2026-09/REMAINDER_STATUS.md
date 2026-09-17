# Phase 2 visual audit — remainder status

Branch: `audit-video-visual-remainder-2026-09`

Production base: `0c4556ab07e8ae700c1556148374a83c0808cef1`

Audit-render source commit: `74d8ea7f6762401d8b6b618154bf262ae3826828`

## Ownership split

This branch deliberately audits **P21–P27 and E01–E06 only**. P05–P20 are owned by the parallel `audit-video-visual-2026-09` branch and are not duplicated here. P01–P04 were completed before the split and remain in the earlier evidence branch.

## Status

| ID | Capsule | Render | Collisions | Boundaries | Visibility | Animation | Timing | Verdict |
|---|---|---|---|---|---|---|---|---|
| P21 | Lire et appliquer une matrice | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P22 | Opérations sur les matrices | PASS | **FAIL** | PASS | **FAIL** | PASS | **FAIL** | **REVISE** |
| P23 | Déterminant et matrice inverse | PASS | PASS* | **FAIL** | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P24 | Du cercle unité à la fonction sinus | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P25 | Aire du cercle | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| P26 | Pythagore par les aires | PASS | **FAIL** | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| P27 | Notation sigma | PASS | PASS* | PASS | **FAIL** | **FAIL** | PASS* | **REVISE** |
| E01 | Implication et équivalence | **BLOCKED** | N/R | N/R | N/R | N/R | N/R | **BLOCKED** |
| E02 | Racine d'un produit | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| E03 | Égalité de fonctions | **BLOCKED** | N/R | N/R | N/R | N/R | N/R | **BLOCKED** |
| E04 | Solutions parasites | **BLOCKED** | N/R | N/R | N/R | N/R | N/R | **BLOCKED** |
| E05 | Ordre de composition | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |
| E06 | Annulation dans les fractions | PASS | PASS | PASS | PASS* | PASS | PASS* | **PASS*** |

**Tally:** 6 REVISE, 4 PASS*, 3 BLOCKED.

## Confirmed findings

| Finding | Severity | Capsule | Time | Summary |
|---|---|---|---|---|
| `VIS-P21-001` | P1 | P21 | 10.1–10.2 s | Section-title morph passes through unreadable glyphs. |
| `VIS-P22-001` | P1 | P22 | 2.4–6.4 s | Opening title and question remain superimposed for several seconds. |
| `VIS-P23-001` | P1 | P23 | 2.0–5.2 s | Opening title is wider than frame and clipped on both sides. |
| `VIS-P23-002` | P1 | P23 | 74.4–74.7 s | Matrix-product formula morph becomes scrambled before resolving. |
| `VIS-P24-001` | P1 | P24 | 17.6–17.8 s; 30.4–30.6 s | Repeated section-heading morphs pass through unreadable states. |
| `VIS-P26-001` | P1 | P26 | 25.2–25.5 s | Outgoing derivation and incoming identity overlap into a dense formula block. |
| `VIS-P27-001` | P1 | P27 | 21.6–21.8 s; 26.5–26.7 s; 40.6–40.9 s | Repeated explanatory-caption morphs become unreadable. |

## Render blockers

E01, E03 and E04 all reach Azure voiceover credential setup during a supposedly silent headless render and terminate with `EOFError` before producing an MP4. They remain unreviewed visually until that path is fixed.

## Audit discipline

- No scene is passed from source inspection alone.
- Successful videos were scanned densely at 2 fps; suspicious transitions were rescanned at 10 fps.
- `PASS*` is provisional structural approval only; final-resolution visibility and narrated-master synchronization remain separate checks.
- Only one small evidence frame per confirmed defect family is retained; MP4s/contact sheets remain temporary artifacts.
