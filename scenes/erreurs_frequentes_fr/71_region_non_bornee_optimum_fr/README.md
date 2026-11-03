# 71 — Région non bornée : l’optimum peut exister

Objectif : distinguer une région réalisable non bornée d’une fonction objectif
non bornée dans le sens recherché, puis justifier l’atteinte d’un optimum.
Les variables sont réelles; aucun arrondi ni contrainte d’intégralité n’est ajouté.

Sources : manuel MAT0339, sections 13.4 et 13.7, notamment « Région vide, non
bornée et optimum multiple »; cahier 13.4 B et synthèse du chapitre 13, S2.
Les chapitres actifs sont `books/mat0339/sources/manual/chapters/ch13.tex` et
`books/mat0339/sources/workbook/chapters/ch13.tex`, identiques dans le livre
intégré du 10 octobre 2026 et la révision du 17 octobre consultée.

L’exemple principal est un transfert original :
\(D=\{(x,y)\in\mathbb R^2:x\ge0,\ y\ge0,\ x+y\ge2\}\).
La famille \((t,2)\), pour \(t\ge0\), prouve que cette région est non bornée.
Le dessin est une fenêtre explicitement annoncée; deux flèches prolongent ses
frontières véritables. Les axes ont des échelles unitaires identiques.

Sur cette même région :

- le minimum de \(x+y\) vaut \(2\), sur tout le segment
  \(\{(s,2-s):0\le s\le2\}\);
- le maximum de \(-x-y\) vaut \(-2\), sur le même segment;
- \(x+y\) n’a pas de maximum, car sa valeur en \((t,2)\) vaut \(t+2\).

Une droite de niveau se déplace jusqu’au segment optimal, puis un point parcourt
ce segment. La preuve algébrique distingue une borne atteinte d’une valeur qui
augmente sans limite; l’infini n’est jamais présenté comme une valeur atteinte.

Autocontrôle original, avec six secondes de réflexion : sous
\(x,y\ge0\), \(2x+y\ge6\), minimiser \(C=3x+2y\).
L’identité \(C=\tfrac32(2x+y)+\tfrac12y\ge9\) prouve la borne.
L’égalité impose \(2x+y=6\) et \(y=0\), donc l’unique optimum est
\((3,0)\), de valeur \(9\). La famille \((3+t,0)\) prouve que la région
reste non bornée.

Classe publique : `RegionNonBorneeOptimumFR`. Neuf pages, narration française
avec `TeachingScene`, profil partagé et une seule ouverture UQAM.
`MANIM_DISABLE_VOICEOVER=1` demande explicitement un aperçu silencieux.
Les contrôles de construction, d’encodage, d’écoute et de diffusion restent
distincts et sont consignés dans le rapport daté du lot.
