# MAT0339 — banque de trois séries semestrielles

Date de travail : 6 septembre 2026.

Cette banque contient trois séries, A, B et C. Chaque série comprend trois examens pour couvrir un semestre complet. Chaque examen comporte six questions et totalise 100 points.

## Découpage de travail

- Examen 1 : chapitres 1 à 6 — algèbre, fonctions, modèles quadratiques et rationnels, exponentielles et logarithmes.
- Examen 2 : chapitres 7 à 12 — dénombrement, probabilités, vecteurs, droites et plans, matrices et systèmes.
- Examen 3 : chapitres 13 à 17 — programmation linéaire et trigonométrie, avec une question cumulative.

Les durées, coupures de chapitres et modalités sont provisoires. Les trois séries visent une couverture comparable, mais l’équivalence statistique de difficulté n’a pas encore été établie. Les corrigés et barèmes sont destinés à l’enseignant.

## PDF compilés

Chaque série possède un recueil étudiant des trois sujets et un recueil enseignant des trois corrigés :

- [Série A — trois sujets](releases/MAT0339_serie_A_trois_examens_sujets.pdf)
- [Série A — trois corrigés](releases/MAT0339_serie_A_trois_examens_corriges.pdf)
- [Série B — trois sujets](releases/MAT0339_serie_B_trois_examens_sujets.pdf)
- [Série B — trois corrigés](releases/MAT0339_serie_B_trois_examens_corriges.pdf)
- [Série C — trois sujets](releases/MAT0339_serie_C_trois_examens_sujets.pdf)
- [Série C — trois corrigés](releases/MAT0339_serie_C_trois_examens_corriges.pdf)

Les PDF individuels restent dans `releases/serie_A/`, `releases/serie_B/` et `releases/serie_C/`. Le fichier `releases/SHA256SUMS.txt` enregistre leurs empreintes.

## Organisation

```text
books/mat0339/exams/2026-09-06/
  README.md
  examens_manifest.json
  sources/
    serie_A/
      examen_1_sujet.tex
      examen_1_corrige.tex
      examen_2_sujet.tex
      examen_2_corrige.tex
      examen_3_sujet.tex
      examen_3_corrige.tex
    serie_B/
    serie_C/
  releases/
    serie_A/               # six PDF individuels
    serie_B/
    serie_C/
    MAT0339_serie_A_trois_examens_sujets.pdf
    MAT0339_serie_A_trois_examens_corriges.pdf
    MAT0339_serie_B_trois_examens_sujets.pdf
    MAT0339_serie_B_trois_examens_corriges.pdf
    MAT0339_serie_C_trois_examens_sujets.pdf
    MAT0339_serie_C_trois_examens_corriges.pdf
    SHA256SUMS.txt
    manifest.json
```

Les sources ont été générées et vérifiées localement avant leur archivage. Elles restent des propositions pédagogiques et doivent être relues après toute modification du manuel ou du calendrier de cours. La compilation vérifie que les 18 fichiers TeX produisent des PDF; elle ne prouve pas à elle seule l’équivalence de difficulté des trois séries.
