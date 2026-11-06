# 60 — Déterminant nul : aucune solution ou une infinité ?

**Objectif :** distinguer singularité et compatibilité d'un système réel.
Prérequis : déterminant en dimension deux, élimination et règle de Cramer.

Le système du cahier \(2x+3y=1\), \(4x+6y=5\) a un déterminant nul
mais aucune solution. En remplaçant le second membre par \(k\), l'élimination
donne \(0=k-2\). Pour \(k=2\), les solutions sont
\((x,y)=(t,(1-2t)/3)\), avec \(t\in\mathbb R\); sinon le système
est incompatible. L'animation conserve les mêmes coefficients pendant que
la seconde droite passe d'une parallèle distincte à la première droite.
Les deux axes utilisent la même échelle géométrique.

Une page distincte vérifie que \(0=0\) n'efface pas la première équation :
le couple \((0,0)\) n'est pas solution. La capsule rappelle aussi que
les quotients de Cramer sont indéfinis lorsque \(D=0\), y compris pour
un quotient formel \(0/0\).

**Autocontrôle du cahier, synthèse S1 du chapitre 12 :**
\(x+ky=1\), \(kx+y=1\), en ciblant les valeurs singulières.
Après six secondes de réflexion, la réponse donne \(D=1-k^2\).
Pour \(k=1\), les solutions sont \((t,1-t)\); pour \(k=-1\),
additionner les équations donne \(0=2\), donc aucune solution.

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch12.tex`, sections 12.7 à
  12.9 (`manual:section:12.07`, `12.08`, `12.09`).
- `books/mat0339/sources/workbook/chapters/ch12.tex`, exercices 12.3 C,
  12.4 A, 12.7 A et synthèse S1.
- Édition intégrée à `main` au commit
  `4d451c37d483d763e33683a7fb683d1e0fdde62d`; vérification également
  contre la révision éditoriale `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`.

**Classe :** `DeterminantNulCompatibiliteFR`. Narration française par
`TeachingScene`, une ouverture UQAM et six secondes de réflexion avant
la réponse. `MANIM_DISABLE_VOICEOVER=1` choisit explicitement le mode
silencieux. Médias générés hors Git; rendu, écoute et publication sont
des étapes distinctes.
