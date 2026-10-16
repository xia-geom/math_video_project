# 52 — Arrondi et optimum entier

**Objectif :** distinguer optimum continu, faisabilité après arrondi et preuve
d'optimalité entière. Prérequis : contraintes linéaires, région réalisable,
évaluation d'une fonction objectif.

Le modèle de référence impose `2x+y <= 8`, `x+2y <= 8` et des quantités
non négatives, avec profit `30x+40y`. Le point continu `(8/3,8/3)` ne peut pas
être arrondi à `(3,3)`. Les 17 points entiers réalisables sont tous pris en
compte; `(2,3)` réalise l'optimum entier 180. Le graphique emploie des unités
identiques sur les deux axes. Une droite de niveau se déplace avant le test
visuel de l'arrondi.

**Autocontrôle :** `x+y <= 5.5`, quantités entières non négatives, profit
`2x+y`; pause de six secondes avant la preuve du maximum 10 en `(5,0)`.

**Sources :** manuel MAT0339, §13.3 « Principe d'optimalité aux sommets »;
cahier, chapitre 13, synthèse S3. Les noms de fichiers de référence sont
`MAT0339_manuel_audite_20260801_0101.tex` et
`MAT0339_cahier_exercices_par_section_20260802_2105.tex`.

**Classe :** `ArrondiOptimumEntierFR`. Narration et sous-titres passent par
`TeachingScene`; `MANIM_DISABLE_VOICEOVER=1` sélectionne explicitement une
prévisualisation silencieuse. Aucune synthèse vocale ni publication n'est
déclenchée par l'import du module.
