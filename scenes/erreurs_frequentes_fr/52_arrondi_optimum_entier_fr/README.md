# 52 — Arrondi et optimum entier

**Objectif :** distinguer optimum continu, faisabilité après arrondi et preuve
d'optimalité entière. Prérequis : contraintes linéaires, région réalisable,
évaluation d'une fonction objectif.

Le modèle du manuel impose \(2x+y\le8\), \(x+2y\le8\) et des quantités
non négatives, avec profit \(30x+40y\). Les profits aux quatre sommets,
\(0,120,160,560/3\), justifient d’abord le maximum continu.
Le point continu \((8/3,8/3)\) ne peut pas être arrondi à \((3,3)\).
Les 17 points entiers réalisables sont tous pris en compte ; \((2,3)\)
réalise l’optimum entier 180. Arrondir vers le bas donne un point réalisable
\((2,2)\), mais son profit de 140 prouve qu’un arrondi réalisable n’est pas
nécessairement optimal. Le graphique emploie des unités
identiques sur les deux axes. Une droite de niveau se déplace avant le test
visuel de l'arrondi. L'ancienne étiquette du sommet est retirée du groupe
graphique après son fondu, afin de ne pas réapparaître près du point arrondi
lors de la sortie de page.

**Autocontrôle :** \(x+y\le5{,}5\), quantités entières non négatives, profit
\(2x+y\) ; pause de six secondes avant la preuve du maximum 10 en \((5,0)\).

**Sources :** manuel MAT0339, §13.1–13.3, notamment « Principe d’optimalité
aux sommets » ; cahier, chapitre 13, synthèse S3 pour la question de transfert
vers les variables entières. Les sources actives sont
`books/mat0339/sources/manual/chapters/ch13.tex` et
`books/mat0339/sources/workbook/chapters/ch13.tex`, édition du 10 octobre 2026,
également vérifiées dans la révision du 17 octobre.

**Classe :** `ArrondiOptimumEntierFR`. Narration et sous-titres passent par
`TeachingScene`; `MANIM_DISABLE_VOICEOVER=1` sélectionne explicitement une
prévisualisation silencieuse. Aucune synthèse vocale ni publication n'est
déclenchée par l'import du module.
