# Course coherence — quick revision review

Review timestamp: 2026-10-16 01:12:23 UTC (local review date: 2026-10-15, America/Toronto).
Baseline: Git HEAD `2b3977d48cf3cf5adcfa4677182d493479dfc89f`.

This is a simulated quick-revision perspective plus a source audit, not a study with real students. Encoded lessons 15, 30 and 43 were reviewed independently of their implementation. The reviewer previously implemented lessons 16–29; the all-course AST check includes that range but is not a blind independent review of it. The root reviewer separately inspects its encoded videos.

## Result and scope limits

No new blocking defect was found in the sampled encoded opening, chapter, body and closing states of lessons 15, 30 and 43. The source audit confirms a shared structure in all 43 lessons without changing public scene identities or existing voice/profile selection. The catalogue remains unchanged and lists all 43 lessons with separate manual and workbook references.

This is **sampled, silent review**. I did not watch complete motion, listen to narration, call Azure, or certify institutional branding/release approval. All three probed MP4s contain one 854×480 video stream and no audio stream. Intended narration and source context-manager lifetime were inspected; that is not listening or audio synchronization acceptance. The Faculty signature is the existing code reconstruction (`logo_exact=false`), not a newly certified exact official asset.

A separate root finding in lesson 21 was acted on during this review: the instructional AB label was being faded to opacity 0.32 while comparing the opposite vector. At the root's explicit request I removed only `label_ab.animate.set_opacity(0.32)`; the inactive arrow may still fade. Syntax and whitespace checks passed. Corrected scene SHA256: `0b933cb0e83a6d2d8026c084470e17ba8eb16595d180fdc0a306d66be64ecf74`. The root reported the original issue at 40.377 s. **Encoded verification of that correction belongs to the root's rerender and is not claimed here.** No other source was edited during this review.

## Encoded evidence and findings

The current `scripts/inspect_course_coherence.py` was run for orders 15, 30 and 43 in `attempt_02`. It rehashed each MP4 and verified the render's complete input fingerprint against current inputs before extracting samples. I independently recalculated the MP4 hashes and probed stream metadata. All six card/body contact sheets were read. Additional native frames are enumerated below.

| Lesson | Actual encoded MP4 SHA256 | Duration | Samples from inspection script |
|---|---|---:|---:|
| 15 | `75d23ee828268fe5350a6f8a423dc565c9280b42a37f300f1a45d4f96bbae07a` | 291.866667 s | 28 |
| 30 | `8f58f6fb23c84d92aaf877148a3fed06e1b8c2c392749fab68c8029bfce2610a` | 313.866667 s | 26 |
| 43 | `b35a96a9501022f84483ecf831e619ecbf6153fa5de2b0f8c04a40035ada716a` | 143.933333 s | 28 |

- **15, navigation:** `frame_002` at 6.300 s, `frame_006` at 29.233 s, `frame_009` at 52.567 s and `frame_012` at 72.900 s show the same four chapter names and order. The list keeps its left edge and only the active row changes to bold. No step-counter footer is present. `frame_000` at 1.100 s shows a readable title/objective and lower-left Faculty signature.
- **15, mathematical revision:** the additional stable frame at 18.576667 s explicitly shows the domain ℝ\{1}. At 38.910 s the two branches remain separate and the dashed asymptotes are distinguishable by line style and labels. At 71.310 s the empty circle at (1,2) is visible without the coordinate label covering the point. The worked-practice domain at 228.310 s excludes both −1 and 2; the simplified expression at 243.310 s still carries both restrictions. `frame_020` at 258.310 s gives h(2) undefined and the limit 4/3. This supports the closing prompt's requested hole (2,4/3), rather than introducing an uncorrected new example.
- **15, closing:** `frame_022` at 271.967 s shows three concise takeaways; `frame_024` at 280.767 s reprises h(x)=(x²−4)/(x²−x−2); `frame_027` at 291.777 s still holds the final card. No overlap or clipping was observed in these states. The source's paper-sketch instructions for the supplementary examples explicitly say “sur papier”; they do not falsely describe an absent animated sketch.
- **30, comparison:** `frame_000` at 1.100 s, `frame_020` at 293.967 s, `frame_022` at 302.767 s and `frame_025` at 313.777 s use the same opening and closing grammar. The practice includes both objective and constraints; the earlier body contact at 292.377 s shows z=18 but x+y=7>5, so the learner can revisit the already-corrected admissibility error.
- **43, comparison:** `frame_000` at 1.100 s, `frame_022` at 124.033 s, `frame_024` at 132.833 s and `frame_027` at 143.843 s match the same structure. Native `frame_008` at 37.110 s shows the common-factor justification with the top heading fully visible; no top cropping or collision is present. The body contact at 65.310 s retains x≠0 and x≠−5 after cancellation, matching the closing practice. Factor-versus-term meaning is carried by expressions, labels and structure, rather than hues.

The audit records show 4.0 s fully-visible openings, 4.0 s for the first chapter and 3.0 s for later chapter reminders, 8.0 s for recap, 8.0 s for the practice prompt, and 3.0 s for the held final card. These repeated-card intervals are adequate for this reviewer's quick-revision reading of the inspected text; they are not a measured learner study. The shared helper waits for the narration context to exit before fading a card, so the authored minimum is not a forced audio cutoff. Longer practice work still requires pausing, as the intended narration requests.

Confirmed new defects in this encoded scope: **none**. Optional design preferences were not treated as defects. Complete motion, every intermediate fade and audio remain outside this acceptance.

## All-43 source audit against HEAD

All 43 catalogue scene files were parsed and compared to HEAD. Public scene class names and base-class ASTs are unchanged. Azure/service/profile-construction calls and voice/speed/prosody/rate constants are unchanged; `tools/tts.py` and `tools/teaching_voiceover.py` are byte-identical to HEAD. New card narrators feed the scene's existing narration adapter with the expected string/dictionary structure.

Every scene contains exactly one shared opening call and one shared closing call, and no old bumper call. Each authored `CHAPTERS` tuple has 3 or 4 nonempty, unique entries. Direct or wrapper call sites cover indices 0 through n−1 once, in authored order, always passing the same constant tuple. The shared helper additionally rejects changed order or nonsequential activation at runtime. These are conceptual boundaries, not automatic page counting. The helper pins the left edge and styles only the active row bold.

No “Étape N sur 4” footer exists in the current chapter helper or scene prose. Lesson 17's “Étape 1 — sandwich” / “Étape 2 — boisson” are labels for the two actual choices in the counting example, not a chapter progress counter. No false references to blue/red/etc. on-screen curves remain in scene prose. In lesson 20's unchanged `curriculum/worked_examples/modeles_probabilistes.yaml`, red/blue **balls in the probability problem** remain meaningful categories; those color words are not instructions to render teaching text in different hues.

For mathematical stability, I compared added/removed math-like string literals, numerical/function lambdas and top-level helpers. All lambdas remain identical after excluding styling keyword changes. The changed top-level helpers (`sixths`, `section_heading`, and circle wedge construction) retain their calculation/counting geometry; differences are color/fill/heading styling. Removed formulas are principally old recap representations, while the lesson body retains the corresponding worked definitions and calculations. Specific checks included domain restrictions and square roots (3,5,10,39,41), arrangement/combination/permutation formulas (18), vector/matrix examples (21–29), sigma/product (37), and composition (42). Lesson 16's continuous/integer answer remains explicit and mathematically consistent; lesson 27's Mx=b inverse connection remains in the recap. This is a source-difference review, not a fresh proof of every mathematical claim in all 43 lessons.

All 43 closings have three lesson-specific takeaways and reprise an existing worked or practice situation. Where the new prompt combines previously displayed pieces, it asks the same calculation (for example 36's area identity). Lesson 1's prompt is derived from its existing expression constants and final evaluation input; it is not a separately hardcoded new example.

| No. | Chapters | Reprised situation checked |
|---:|---:|---|
| 01 | 4 | expression affine déjà évaluée |
| 02 | 4 | −3x < 6 |
| 03 | 4 | √((-4)²) et u² = 16 |
| 04 | 4 | (-2)² − 3/2 ÷ 3/4 |
| 05 | 4 | domaines de 1/(x−2) et √(x−3) |
| 06 | 4 | 3x−2, x²+1 et 1/x |
| 07 | 4 | x²−2x−3 : racines et minimum |
| 08 | 4 | tarif par morceaux : C(1), C(2,4) |
| 09 | 4 | somme et différence en x=1 |
| 10 | 4 | f(x)=x+1, g(t)=√t |
| 11 | 4 | f(x)=2x+1 : réciproque |
| 12 | 3 | (x−2)(x+1) : racines |
| 13 | 4 | ½(x+2)(x−1)² : multiplicités |
| 14 | 4 | x²+6x+2 : forme canonique |
| 15 | 4 | (x²−4)/(x²−x−2) : domaine et trou |
| 16 | 4 | 2^t = 10^6 : temps continu et entier |
| 17 | 3 | 3 sandwichs × 2 boissons |
| 18 | 4 | podium de 3 parmi 5 |
| 19 | 4 | BANANE : objets identiques |
| 20 | 4 | dé équilibré : union de A et B |
| 21 | 3 | A=(-3,-1), B=(1,2) |
| 22 | 4 | u=(2,-1,3), v=(-1,4,2) |
| 23 | 3 | A=(-2,-1), B=(2,2) |
| 24 | 4 | Q=(1,1,4) dans le plan Π |
| 25 | 4 | matrice [[2,1],[1,3]] appliquée à (4,2) |
| 26 | 4 | A=[[1,1],[0,1]], p=(1,2) |
| 27 | 4 | A=[[1,1],[0,2]] : déterminant/inverse |
| 28 | 4 | x+y=7, x−y=1 |
| 29 | 4 | 2x+y=5, x−y=1 par Cramer |
| 30 | 3 | z=3x+2y, point (4,3), contraintes données |
| 31 | 3 | sin(π/2), sin(3π/2) sur le cercle |
| 32 | 3 | triangle 3–4–5 : angle opposé au côté 4 |
| 33 | 3 | deux côtés et angle compris : choix de loi |
| 34 | 3 | arccos(−1/2), arcsin(2) |
| 35 | 3 | base πr et hauteur r |
| 36 | 3 | (a+b)² = 2ab+c² |
| 37 | 4 | somme des 2i+1 de 0 à 4 |
| 38 | 3 | x²=4 implique-t-il x=2 ? |
| 39 | 3 | a=b=−1 : existence des racines |
| 40 | 3 | u(x)=x², v(x)=|x| : même image ? |
| 41 | 3 | √(x+2)=x : tester −1 et 2 |
| 42 | 3 | f(x)=2x+1, g(x)=x², entrée 2 |
| 43 | 4 | x(x+2)/[x(x+5)] et restrictions |

## Catalogue and book lookup

The existing three-page PDF and all three rendered pages were inspected. Fresh `pdftotext -layout` extraction returns 01–43 exactly once in order. The LaTeX source, unified YAML and generated CSV are byte-identical to HEAD. The PDF hash matches its existing verification record. The 37 course-notion entries and 6 common-error entries remain present. “Manuel” and “Cahier” are distinct columns, including differing references; the introductory warning explicitly says to read them separately.

| Reviewed lesson | Manual lookup | Workbook lookup |
|---|---|---|
| 15 — rational functions | §§ 5.2, 5.3, 5.4 | §§ 5.1, 5.2, 5.3 |
| 30 — linear programming | §§ 13.1, 13.2, 13.3 | §§ 13.1, 13.2, 13.3 |
| 43 — cancellation | § 2.2 | § 2.2 |

The visible table also preserves purposeful distinctions such as lesson 39 manual §1.4 versus workbook §1.6, and lesson 40 manual §3.1 versus workbook §2.2. Chapters/transversal fallbacks for 35–37 remain explicitly qualified. No new navigation defect was found. I verified the catalogue's existing references, not every exercise inside the entire manual/workbook.

Catalogue provenance:

- `books/mat0339/curriculum/catalogue-videos.tex` — SHA256 `4afb8905f3dbf4b2a85f3e2f91e9a6414bfcfec4c1884c3e0b285c8513731f4c`.
- `review_artifacts/teaching_navigation/catalogue/catalogue-videos.pdf` — SHA256 `97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520`.
- `curriculum/programme_principal_fr.yaml` — SHA256 `8b59407d4ec129628801e01e344f0ffc53f45e6825fec939cc635d90052cd6cf`.
- `curriculum/playlist.csv` — SHA256 `a45eef509e37e8643d9205322f273c2bbf64c31998bec8258437cda561a14f55`.

## Exact inspected artifacts

All paths below are relative to `/Users/xiaxiao/Desktop/video/math_video_project_clean`.

For each `review_artifacts/course_coherence/2026-10-15/attempt_02/{15,30,43}/`, inspected `STATUS.json`, `cards.json`, `checkpoints.json`, `frame_index.json`, `cards_00.png`, `body_00.png`; used the exact MP4 named in that STATUS for hashing, probing and extraction. The contact sheets expose all structural-readable samples and 12 stable body samples per lesson. Native-size inspections, distinct from those contact-sheet inspections:

- Lesson 15, `frames/`: `frame_000.png` (1.100 s), `frame_002.png` (6.300 s), `frame_006.png` (29.233 s), `frame_009.png` (52.567 s), `frame_012.png` (72.900 s), `frame_022.png` (271.967 s), `frame_024.png` (280.767 s), `frame_027.png` (291.777 s).
- Lesson 30, `frames/`: `frame_000.png` (1.100 s), `frame_020.png` (293.967 s), `frame_022.png` (302.767 s), `frame_025.png` (313.777 s).
- Lesson 43, `frames/`: `frame_000.png` (1.100 s), `frame_008.png` (37.110 s), `frame_022.png` (124.033 s), `frame_024.png` (132.833 s), `frame_027.png` (143.843 s).
- Lesson 15 extra frames extracted from the same verified MP4: `frames/extra_domain_hold.png` (18.576667 s), `frames/extra_asymptotes_hold.png` (38.910000 s), `frames/extra_hole_hold.png` (71.310000 s), `frames/extra_practice_domain_hold.png` (228.310000 s), `frames/extra_practice_restrictions_hold.png` (243.310000 s).

Catalogue files inspected: `books/mat0339/curriculum/catalogue-videos.tex`; `review_artifacts/teaching_navigation/catalogue/catalogue-videos.pdf`, `catalogue-videos.txt`, `verification.json`, `page-1.png`, `page-2.png`, `page-3.png`. The fresh PDF text extraction went to stdout; no catalogue asset was modified.

Source/helper inspection: all catalogue scene files listed below (AST and changed-formula review, not a claim of line-by-line inspection of every unchanged line); `tools/teaching_chapters.py`, `tools/teaching_layout.py`, `tools/expanded_teaching.py`, `scripts/inspect_course_coherence.py`; narration API/profile comparison for `tools/tts.py`, `tools/teaching_voiceover.py`; practice/example lookup in `curriculum/practice_questions.yaml`, `curriculum/worked_examples/fonctions_rationnelles.yaml`, `curriculum/worked_examples/modeles_probabilistes.yaml`, and `curriculum/worked_examples/operations_nombres_reels.yaml`. Repository and PDF-skill instructions were also read. No other reviewer's report was used as evidence for the independent 15/30/43 visual findings.

## Source snapshot

The following final AST snapshot supersedes earlier transient hashes during concurrent work. A later source edit requires reevaluation of the affected entry; this report does not bless future edits.

| No. | Exact scene file | SHA256 |
|---:|---|---|
| 01 | `scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py` | `aeba8895eeaff6e8c0ce6b8b9303850df3435b343ae918fa01a84857b57293be` |
| 02 | `scenes/algebre_et_polynomes_fr/02_inequations_nombre_negatif_fr/02_inequations_nombre_negatif_fr_scene.py` | `2634851e2d6ca4818c75b63578b8e58ff7f0d7334e6493cbf362669a1b9b9a2d` |
| 03 | `scenes/algebre_et_polynomes_fr/03_racine_carree_et_valeur_absolue_fr/03_racine_carree_et_valeur_absolue_fr_scene.py` | `b27bb8cea7bba153e77a41456c8ad321d52550b9dd37211297311e28f8ddaaee` |
| 04 | `scenes/algebre_et_polynomes_fr/04_operations_nombres_reels_fr/04_operations_nombres_reels_fr_scene.py` | `573828f5885b38699d271a7d88776ce248edbcc528cc315e6b0de43817fe2dbd` |
| 05 | `scenes/fonctions_et_graphiques_fr/05_domaine_et_image_fr/05_domaine_et_image_fr_scene.py` | `87c19e47f114cdcd89f2ba90b21bcf0c3b527f132315126ec826ac3a8c578f6a` |
| 06 | `scenes/fonctions_et_graphiques_fr/06_modeles_affines_et_quadratiques_fr/06_modeles_affines_et_quadratiques_fr_scene.py` | `b22a29ac1610036b7e593c481f1d2c3fa5beda258c2649c2f407370fbae5cb46` |
| 07 | `scenes/fonctions_et_graphiques_fr/07_lire_les_proprietes_d_un_graphe_fr/07_lire_les_proprietes_d_un_graphe_fr_scene.py` | `63a64d78997abed2ff0ee84c109897374d6bb43aa3aedd274d503281ebfb521f` |
| 08 | `scenes/fonctions_et_graphiques_fr/08_fonction_par_morceaux_fr/08_fonction_par_morceaux_fr_scene.py` | `8627ff53ad763465b791de891f3e15271a646ca92f648e7116d7f7a7cb50ab67` |
| 09 | `scenes/fonctions_et_graphiques_fr/09_operations_sur_les_fonctions_fr/09_operations_sur_les_fonctions_fr_scene.py` | `c150129bef96951a640e844b9314671b9c44632e2bd36e66672019a8084ea642` |
| 10 | `scenes/fonctions_et_graphiques_fr/10_composition_de_fonctions_fr/10_composition_de_fonctions_fr_scene.py` | `02a4489e6c36399baade9bafb82f2ea84f32d455daaf40ece9f75a6a855d54f5` |
| 11 | `scenes/fonctions_et_graphiques_fr/11_fonction_reciproque_fr/11_fonction_reciproque_fr_scene.py` | `24f86a9eba19cb2c1539a87cf959ce86de270948c47ab8b540b3bf0839de3c64` |
| 12 | `scenes/fonctions_et_graphiques_fr/12_racines_et_hauteur_zero_fr/12_racines_et_hauteur_zero_fr_scene.py` | `98f17b847987485c2b8bd2d6b1e0afe67cb2f58870bab10cfd606d5308818a13` |
| 13 | `scenes/fonctions_et_graphiques_fr/13_multiplicite_des_racines_fr/13_multiplicite_des_racines_fr_scene.py` | `79476ad8ef37e08ba3915c2b34721229b55e9a0920ad0fd9b1b7c360ac7e521d` |
| 14 | `scenes/algebre_et_polynomes_fr/14_completer_le_carre_fr/14_completer_le_carre_fr_scene.py` | `9e47a6a93f402c6eb99291bda159ba9570221db6f879d4a2d1a5fcc7b4eca6a8` |
| 15 | `scenes/fonctions_et_graphiques_fr/15_fonctions_rationnelles_fr/15_fonctions_rationnelles_fr_scene.py` | `ebf7adffb3e73b6bcbe2cfb4a57e6edd3028fc70d9252f0c709b29995cdbda7b` |
| 16 | `scenes/exponentielles_et_logarithmes_fr/16_logarithmes_fr/16_logarithmes_fr_scene.py` | `89077d9185538cbad1e024dba0c9d301ea98c8db1491bf42aeae226c0bbb39d6` |
| 17 | `scenes/probabilites_fr/17_principe_fondamental_du_denombrement_fr/17_principe_fondamental_du_denombrement_fr_scene.py` | `53718d48f393e9e4e06e05d409b0e372d52108369669b467b1c015ae1045fd9d` |
| 18 | `scenes/probabilites_fr/18_permutation_arrangement_combinaison_fr/18_permutation_arrangement_combinaison_fr_scene.py` | `b49de9697b75c4dfd13e473a38849a22b4984930461e32215921748f9d81bc78` |
| 19 | `scenes/probabilites_fr/19_repetitions_en_denombrement_fr/19_repetitions_en_denombrement_fr_scene.py` | `c24c45bcd964aa4be85a19be95807a7ee319df68804a85da20656232b6e40c96` |
| 20 | `scenes/probabilites_fr/20_modeles_probabilistes_fr/20_modeles_probabilistes_fr_scene.py` | `7f0c1f86302fa067447a303375ee140408a93d0e7249b32ac8dda7a66b4aedca` |
| 21 | `scenes/vecteurs_fr/21_deplacement_et_composantes_fr/21_deplacement_et_composantes_fr_scene.py` | `0b933cb0e83a6d2d8026c084470e17ba8eb16595d180fdc0a306d66be64ecf74` |
| 22 | `scenes/vecteurs_fr/22_operations_sur_les_vecteurs_fr/22_operations_sur_les_vecteurs_fr_scene.py` | `c5aa44e8836305ec3b1db1f0ad09ecd1160ac02a7af599ff1fd506ae8a91522a` |
| 23 | `scenes/vecteurs_fr/23_vecteurs_dans_r2_et_r3_fr/23_vecteurs_dans_r2_et_r3_fr_scene.py` | `8bd939435b25fed6fe2f34f0caeb371c5f2e02924840c1bee7ca1e107f7aba2d` |
| 24 | `scenes/vecteurs_fr/24_equations_droite_plan_fr/24_equations_droite_plan_fr_scene.py` | `58e71ced83492b4acb827c11eb28f8a400dc2c71190d91b57e2c7260f15fa5a1` |
| 25 | `scenes/matrices_fr/25_lire_et_appliquer_une_matrice_fr/25_lire_et_appliquer_une_matrice_fr_scene.py` | `3f35036f236d595371c0964d911304406120011bcb790678e388bb337ed04b45` |
| 26 | `scenes/matrices_fr/26_operations_sur_les_matrices_fr/26_operations_sur_les_matrices_fr_scene.py` | `f6ad6185965e1891aeabdf44fa79bc47f0313eb56a7e60fb7ad3901e6fd40aa0` |
| 27 | `scenes/matrices_fr/27_determinant_et_matrice_inverse_fr/27_determinant_et_matrice_inverse_fr_scene.py` | `dd5ee3222df0bd4a8ea5c54987f03695f134e052e4cd31e5972a283bf219ed98` |
| 28 | `scenes/matrices_fr/28_elimination_variables_fr/28_elimination_variables_fr_scene.py` | `a96b741005f967f6f79adc39ee7c8a0b3b6997d2a20708747383a766fda6f2f9` |
| 29 | `scenes/matrices_fr/29_regle_cramer_fr/29_regle_cramer_fr_scene.py` | `12855e921d276547a9b07d306181c29696d3dff817a696431538b8315d0a2b17` |
| 30 | `scenes/matrices_fr/30_programmation_lineaire_fr/30_programmation_lineaire_fr_scene.py` | `85430aa3998be614b704ecd3ba065721a1a8bcd6b71e69d436992ba8e62c3931` |
| 31 | `scenes/trigonometrie_fr/31_du_cercle_au_sinus_fr/31_du_cercle_au_sinus_fr_scene.py` | `9639776fa04caca193fd943a13700cff7138009fc1bb692931c72aa1175e4028` |
| 32 | `scenes/trigonometrie_fr/32_trigonometrie_triangle_fr/32_trigonometrie_triangle_fr_scene.py` | `b91ff7b2da863383ecdc9ccc9b49756f356e3f049c3615d23ced75f7a7fdc9b3` |
| 33 | `scenes/trigonometrie_fr/33_lois_sinus_cosinus_fr/33_lois_sinus_cosinus_fr_scene.py` | `da7fb6106c5fa59fa83e507338ebbeb46ec7eba456547eb282e4d7f2bc21763a` |
| 34 | `scenes/trigonometrie_fr/34_fonctions_trigonometriques_inverses_fr/34_fonctions_trigonometriques_inverses_fr_scene.py` | `5c2b420b5fb74e9890d0010ff869e231f4e58276ce82cd8d44124d1e030fc323` |
| 35 | `scenes/geometrie_fr/35_aire_du_cercle_fr/35_aire_du_cercle_fr_scene.py` | `a4a1f6cc098191b1917ce3439da66dafe827c226f4f04beffb08cd3020b02454` |
| 36 | `scenes/geometrie_fr/36_pythagore_par_les_aires_fr/36_pythagore_par_les_aires_fr_scene.py` | `b9761df81c9b310f5dad264dff6e7e197fd0623bdf628af9ce243fbf731af115` |
| 37 | `scenes/notations_fr/37_notation_sigma_fr/37_notation_sigma_fr_scene.py` | `c04df82650dcd2e5f4ff8051c26aed4f608115e9610ea379839bf2298453f3bd` |
| 38 | `scenes/erreurs_frequentes_fr/38_implication_et_equivalence_fr/38_implication_et_equivalence_fr_scene.py` | `229575c79b2294f440ae46330aaaeca7cd624ed0efed7c3c2d7b68d92799d265` |
| 39 | `scenes/erreurs_frequentes_fr/39_racine_d_un_produit_fr/39_racine_d_un_produit_fr_scene.py` | `95d3f60438173a379d2133d6c78c1ad41fab76aef278a5ca3c64afe7fbea7bf9` |
| 40 | `scenes/erreurs_frequentes_fr/40_egalite_de_fonctions_fr/40_egalite_de_fonctions_fr_scene.py` | `358c229470e7559ebdd708fcad8b072a4d3ed115e3843b6c74825e3871e2eb69` |
| 41 | `scenes/erreurs_frequentes_fr/41_solutions_parasites_fr/41_solutions_parasites_fr_scene.py` | `d9aeeab469df1d571552388287de3efb69a57603bef1dffc4a013edac761939e` |
| 42 | `scenes/erreurs_frequentes_fr/42_ordre_de_composition_fr/42_ordre_de_composition_fr_scene.py` | `cbc74463d6fc4e203bae939369c44a5e8a367af7d9c35a6be9a963b4048e6460` |
| 43 | `scenes/erreurs_frequentes_fr/43_annulation_dans_les_fractions_fr/43_annulation_dans_les_fractions_fr_scene.py` | `348ddc611d5f2a659eff137c4a787a147fb6fd208a59c7278dc6e45007673769` |

Additional audited source hashes:

- `tools/teaching_chapters.py` — `d3bf2a9152a2e3aaf8e0703e7d520730ea6b974499558db7d75a478a3e859117`.
- `tools/teaching_layout.py` — `36e4eaf7afd177f7883877da68db0c63898fec50da537a53ab7dcb87b2c68c17`.
- `tools/expanded_teaching.py` — `f3c913ce67638611c793ef356770d825f869cda5fa3504feaeecb9daed49279c`.
- `tools/tts.py` — `ac809dd446d6e22218a5540e7249b458ee3a82871fa19cabe560b94f8cb6aab5`.
- `tools/teaching_voiceover.py` — `8b9b6600a03dbb3ad51d0ca827ee4542ade99554ecffb36138e96055077a041c`.
- `scripts/inspect_course_coherence.py` — `bcef79cffa3b0861da0f93ad3e8a3cddb0aa6a562dd741420216c45e3bede673`.
- `curriculum/practice_questions.yaml` — `136345dd683050e53d0c5cd66302d04b30942cd558ffd2ea985cadca0ecfc934`.
- `curriculum/worked_examples/fonctions_rationnelles.yaml` — `c3318126455706cbfdb5ce3a641dae20f014a730a5a86877cf2cead191b02e04`.
- `curriculum/worked_examples/modeles_probabilistes.yaml` — `ef6f455d08a8df2a9a90bdd99a9dac42ac94b4fa133583f9f1aa0373e64d692a`.
