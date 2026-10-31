# MAT0339 — examens révisés du 10 octobre 2026

Cette édition de travail reprend les trois séries A, B et C du 6 septembre. Les neuf examens conservent chacun six questions, 100 points et leur durée proposée (120, 120 et 150 minutes). Les 54 questions et 165 sous-questions ont été relues en comparant chaque sujet à son corrigé. Les durées, modalités et l’équivalence de difficulté restent à valider par l’enseignant.

Les sources historiques, les PDF et les manifestes du [6 septembre](../2026-09-06/README.md) sont conservés intégralement. [provenance.json](provenance.json) enregistre les empreintes des 46 fichiers historiques; le test de préservation vérifie leurs octets. Les présents fichiers sont de nouveaux brouillons, sans publication ni approbation institutionnelle.

## Améliorations et relecture

Aucune nouvelle erreur de résultat n’a été décelée dans la banque d’examens. Les améliorations rendent les démarches plus explicites : premier temps réel d’un seuil exponentiel et contrôle aux entiers voisins, unités des quantités, substitution dans les logarithmes, choix d’une pulsation positive, lecture des demi-plans et distinction succès/échec. Les valeurs exactes restent utilisées jusqu’à l’arrondi demandé.

[review.json](review.json) donne les contrôles de chacune des 54 questions, leurs sous-questions et les empreintes exactes des sources relues. Les tests recalculent les fractions, domaines et signes, seuils, permutations, probabilités par énumération, projections, produits matriciels, familles de solutions, sommets admissibles, angles, racines trigonométriques et niveaux de sinusoïdes. Les trois premiers examens restent ancrés aux chapitres 1–6, les suivants aux chapitres 7–12, les derniers aux chapitres 13–17 avec réinvestissement cumulatif.

Le contrôle mathématique est distinct de l’inspection graphique. Les détails de cette dernière figurent dans la rubrique `visual_review` du registre. Les tests ne sont ni une preuve formelle de chaque phrase ni une validation de l’équivalence pédagogique entre séries.

## Reproduire les PDF locaux

Depuis la racine du dépôt, avec Python 3.11+, LaTeX et Poppler :

```sh
python3 -m unittest discover -s books/mat0339/tests -p test_exams_revision.py -v
python3 books/mat0339/scripts/build_exams.py --pdf-python /chemin/vers/python-avec-pypdf
```

Omettre `--pdf-python` si le Python courant possède `pypdf`. Le script utilise `latexmk`, pdfLaTeX avec `-no-shell-escape`, une date de contenu fixe et `pdfinfo`. Il produit 18 PDF individuels de six pages et six recueils de dix-huit pages. Chaque question occupe une page; la pagination recommence à chaque examen dans les recueils, où les signets permettent de sélectionner les examens.

Les intermédiaires, journaux et le manifeste de compilation sont sous `books/mat0339/build/exams/2026-10-10/`. Les PDF et leur manifeste avec empreintes sont sous `books/mat0339/dist/exams/2026-10-10/`. Ces emplacements sont ignorés par Git. Aucun fichier n’est écrit dans `releases/` ni envoyé vers un stockage externe. La reproductibilité dépend des versions TeX et pypdf enregistrées dans le manifeste.

## Recueils locaux

Ces liens fonctionnent après compilation :

| Série | Sujets étudiants | Corrigés enseignants |
|---|---|---|
| A | [Trois sujets](../../dist/exams/2026-10-10/MAT0339_serie_A_trois_examens_sujets.pdf) | [Trois corrigés](../../dist/exams/2026-10-10/MAT0339_serie_A_trois_examens_corriges.pdf) |
| B | [Trois sujets](../../dist/exams/2026-10-10/MAT0339_serie_B_trois_examens_sujets.pdf) | [Trois corrigés](../../dist/exams/2026-10-10/MAT0339_serie_B_trois_examens_corriges.pdf) |
| C | [Trois sujets](../../dist/exams/2026-10-10/MAT0339_serie_C_trois_examens_sujets.pdf) | [Trois corrigés](../../dist/exams/2026-10-10/MAT0339_serie_C_trois_examens_corriges.pdf) |
