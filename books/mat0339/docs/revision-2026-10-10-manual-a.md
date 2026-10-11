# Révision du 10 octobre 2026 — manuel, chapitres 1 à 9

## Portée

Les neuf chapitres ont été lus intégralement dans leurs sources actives. Les retouches portent sur la justesse, les conditions d'application, les figures signalées et la formulation destinée aux étudiants. Les titres de chapitres et de sections, les étiquettes et l'ordre sont conservés. Les archives d'août et les instantanés de septembre ne sont pas modifiés.

La révision de langue remplace les commentaires sur la qualité de l'explication par des explications directes : opération à effectuer, raison, domaine et contrôle. Elle conserve les exemples, les démonstrations et les comparaisons utiles. Il ne s'agit pas d'une substitution automatique de mots ni d'une certification de chaque formule du manuel.

## Constats de septembre traités dans les sources

| Constat | Sections | Modification et contrôle attendu |
|---|---|---|
| AUD-08 | 5.2, 5.3, 5.4 | Classification au moyen du quotient entièrement réduit. Deux graphes contrastent `x²/x` et `x/x²`, avec le même domaine initial excluant zéro. Contrôle indépendant des valeurs et du trou `(2,4/3)` de l'autre exemple. |
| AUD-10 | 1.1 | Rectangle intérieur élargi; symbole `N` et exemples placés dans deux zones distinctes. Espaces verticaux agrandis après la première inspection. Absence de collision confirmée en couleur et en niveaux de gris, page physique 13. |
| AUD-11 | 1.5 | Ligne de cote relevée au-dessus des noms des points; graduations, noms et distance occupent des niveaux distincts. Accolade inférieure abaissée après l'inspection détaillée pour la séparer des graduations. Vérification finale en couleur et en niveaux de gris, page physique 16. |
| AUD-12 | 2.7 | Boîtes positionnées explicitement, flèche entre leurs bords et annotation séparée au-dessus. Vérification en couleur et en niveaux de gris, page physique 28. |
| AUD-13 | 5.1, 5.2 | Légendes placées sous les dessins, hors des tracés, avec traits de rappel. Les courbes de 5.1 sont limitées au cadre. Les figures répétées de 5.2 sont remplacées par le contraste trou/asymptote. Vérification en couleur et en niveaux de gris, page physique 61. |
| AUD-14 | 8.8 | Diagramme remplacé par un tableau d'effectifs avec marges : `(190,10,200)`, `(392,9408,9800)`, total `(582,9418,10000)`. Comparaison explicite des dénominateurs `582` et `200`. Les sommes et la probabilité conditionnelle sont testées. |
| AUD-20 | 2.5, 2.8 | Domaine et condition nécessaire de signe séparés. Pour `sqrt(x+1)=x−1`, zéro est défini mais rejeté comme solution; pour `sqrt(2x+3)=x`, le domaine commence en `−3/2` et la condition de signe impose ensuite `x≥0`. Candidats vérifiés. |
| AUD-21 | 6.1, 6.6, 6.7, 6.8 | Doublement futur réservé à une quantité initiale positive et un facteur supérieur à 1. Rapport réservé à une quantité initiale non nulle. Logarithme réservé à des valeurs positives. Cas constants, décroissance et demi-vie explicités. Les tests couvrent croissance, décroissance, facteur 1 et quantité nulle. |

Ces modifications ne ferment pas rétroactivement les constats portant sur les PDF du 5 septembre. La compilation et la revue visuelle de la nouvelle édition sont consignées séparément par le responsable de la révision.

## Autres corrections vérifiées pendant la lecture

- **REV-A-01, 4.6 : courbes et formules.** Les graphes annoncés comme `x²` et `(x+3)²−4` utilisaient un facteur `0,65` non annoncé. Les tracés utilisent désormais les formules du texte; le sommet et l'identité de translation sont testés.
- **REV-A-02, 6.7 : modèle logarithmique.** Le dessin de `ln Q` n'utilisait pas les coefficients du modèle voisin `Q(t)=0,55(1,65)^t`. Le nouveau tracé utilise `ln(0,55)+t ln(1,65)`; les deux expressions sont vérifiées sur plusieurs temps, dont zéro où le logarithme est négatif.
- **REV-A-03, 9.6–9.8 : projection.** La composante signée est distinguée de la longueur non négative. Le grand vecteur du dessin est nommé `v`, avec `e=v/||v||`, au lieu d'être présenté comme unitaire sans l'être à l'échelle du dessin. Le cas d'une projection négative est testé. Les deux vecteurs nuls sont distingués du cas où deux vecteurs colinéaires engendrent une droite.
- **Précisions locales :** pas constant pour les différences finies (4.5–4.7), bornes entières `0≤k≤n` pour les arrangements et combinaisons (7.3–7.4), limites d'application de l'arbre de décision (7.7), nombre de prolongements pour le principe multiplicatif (7.9), dés équilibrés et lancers indépendants avant le dénombrement équiprobable (8.2, 8.9). Ces précisions n'ajoutent pas de nouveau thème au cours.

## Retouches de langue

| Chapitre | Passages retouchés |
|---|---|
| 1 | 1.1, 1.5, 1.6, 1.7 : ensembles, lecture de la droite, justification des signes, contrôles. |
| 2 | 2.2, 2.5–2.8 : factorisation, domaines, choix de méthode et rédaction des équivalences. |
| 3 | Introduction; 3.1, 3.3, 3.5–3.8 : formulation directe, exemples et lecture des morceaux. |
| 4 | Introduction; 4.5–4.7 : différences finies, données, résidus, contexte et formule quadratique. |
| 5 | 5.1–5.4 : domaine, réduction, vocabulaire des graphes et ordre de l'étude. |
| 6 | 6.1, 6.5–6.8 : taux, facteurs, logarithmes, temps caractéristiques et hypothèses. |
| 7 | 7.3–7.4, 7.6–7.9 : choix successifs, complément, double comptage et ordre. |
| 8 | 8.2, 8.5, 8.7–8.9 : expérience, chemins, effectifs, conditionnement et simulations. |
| 9 | 9.6–9.8 : déplacements, composante signée, projection et combinaisons linéaires. |

## Vérification propre à ce lot

- `python3 -m unittest discover -s books/mat0339/tests -p test_revision_manual_a.py -v` : **8 tests réussis**.
- `git diff --check` limité aux sources et au test de ce lot : **réussi**.
- Comparaison des titres, étiquettes et ordre des sections avec `HEAD` pour les neuf chapitres : **identiques**. Vérification de l'emboîtement des environnements TEX : **réussie**; ce contrôle ne remplace pas la compilation.
- Compilation du manuel : déléguée au responsable, sans compilation concurrente dans ce lot.
- Première inspection graphique : planches de contact à 65 ppp couvrant les **pages physiques 1 à 116** du manuel compilé; inspection à 130 ppp des pages **13, 26, 27, 51, 54, 61, 74, 75, 98, 99 et 111**. Le tableau de Bayes, les deux cas de simplification rationnelle et la projection signée sont lisibles. Aucun débordement de texte n'a été relevé dans ce parcours.
- Retouches issues de cette inspection : espacement vertical supplémentaire dans les ensembles emboîtés (1.1); légendes de balance et d'équivalence séparées des traits (2.6); légendes hors des courbes (4.5, 4.6, 5.1, 6.6, 6.7); contraste des six cases favorables, numérotation des résultats et annotation hors de la grille (8.7).
- Après recompilation : nouveau rendu à 130 ppp des **pages physiques 12–17, 25–29, 50–55, 60–63, 73–76, 97–100 et 110–112**, soit 32 pages. Les figures retouchées ont été revues en détail et les pages voisines sur six planches de contact. Aucun texte tronqué ni débordement n'a été relevé. Les pages **13, 16, 28, 61 et 99** ont aussi été inspectées en niveaux de gris. Ce contrôle a conduit à une dernière retouche de l'accolade en 1.5.
- Vérification finale après cette dernière compilation : **pages 15–17** revues à 130 ppp, dont la page **16 en couleur et en niveaux de gris**; l'accolade est séparée des nombres. La grille de dés de la page **98** a aussi été contrôlée en niveaux de gris : six cases distinctes, résultats numérotés et légende lisible. Aucun défaut restant relevé dans ces pages. Les images de contrôle sont conservées dans `build/review-2026-10-10/manual/`, sans ajout aux archives de diffusion.
- Contrôle complémentaire après comparaison des rendus : les **pages physiques 56–59**, dont le texte s'est déplacé à la suite des retouches de figures du chapitre 4, ont été inspectées dans le rendu final à 65 ppp (`build/review-2026-10-10/manual-final-65/`). Formules, tableau comparatif, liste de contrôles et synthèse sont lisibles et restent dans les marges; aucun chevauchement ni texte tronqué relevé. Ce contrôle porte à **36** le nombre de pages finales ciblées après le premier parcours.
- Relecture institutionnelle, couverture exhaustive du programme et conformité PDF/UA : non déclarées.

## Empreintes du lot vérifié

Manuel de 198 pages examiné après la dernière compilation : `MAT0339_manuel_2026-10-10.pdf`, SHA-256 `d27238c6cfbf8556dd61f257f40d0288a7b8a6313ecef18db07a42bffc8dbe16`.

| Source | SHA-256 |
|---|---|
| `ch01.tex` | `572515a5fe59c5440575a01e37953c18481efec40acc2a8561b3f75f1df0cfd9` |
| `ch02.tex` | `9783a9ce6838524a5d8e75d04bdf5b1d436ae7d72d4c5ed05c7402b361eef478` |
| `ch03.tex` | `d00fde33e4d36240560f545165e7ba89a8cfcd1089d0ab2d884784664a2ca009` |
| `ch04.tex` | `a8ce20974236004df1b1804c550ed6dfd892aa87b4a18119df62caa914016b7d` |
| `ch05.tex` | `b262037064c322eae2ece527674e89f3823ed11c223647ba66a12460c70502dc` |
| `ch06.tex` | `425496f0a45c29dabc687516c44f64bf7d3121d3acfe69bf29d1f80f537d4bae` |
| `ch07.tex` | `4c38cf9831d0e796c9bf192230e0da165c0904bde36d339ebb4cb60a4e4f3e4f` |
| `ch08.tex` | `b394ecf837c614fdde8dc0be357265f46f9d2c2c009d71872737ee0e51e7ae2e` |
| `ch09.tex` | `5c99b89f9eb52114a288460193d1606edecc8fce374362549c142edd5f480f01` |
