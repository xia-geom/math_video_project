# 51 — Le carré d’une matrice

Objectif : interpréter une puissance comme un produit matriciel et comme la répétition d’une transformation.

Sources : manuel MAT0339, § 11.3 « Produit matriciel » et § 11.4 « Matrice identité et puissances » ; cahier, exercice 11.4 B. L’exemple reprend exactement \(A=\begin{pmatrix}1&1\\0&1\end{pmatrix}\), avec \(A^2=\begin{pmatrix}1&2\\0&1\end{pmatrix}\) et \(A^3=\begin{pmatrix}1&3\\0&1\end{pmatrix}\).

Animation : la première ligne et la deuxième colonne expliquent l’entrée supérieure droite du produit. La transformation \((x,y)\mapsto(x+y,y)\) agit ensuite deux fois sur le même quadrillage, devant des axes fixes de même échelle. Le point \((0,1)\) passe par \((1,1)\), puis \((2,1)\).

Autocontrôle : calculer \(A^3\) et l’image de \((0,1)\). Réponse : \((3,1)\), après une pause de six secondes. L’opération entrée par entrée est montrée comme la tentation erronée, jamais comme la définition de la puissance.

Classe : `CarreMatriceFR`. `TeachingScene` fournit la narration et les sous-titres ; l’ouverture UQAM est unique. `MANIM_DISABLE_VOICEOVER=1` sélectionne explicitement le mode silencieux. Les vérifications techniques du lot ne valent pas approbation de diffusion.

Sources Git contrôlées : [manuel, chapitre 11](../../../books/mat0339/sources/manual/chapters/ch11.tex) et [cahier, chapitre 11](../../../books/mat0339/sources/workbook/chapters/ch11.tex). Le [plan du lot](../../../reports/error_capsules/2026-10-30/PLAN.md) distingue l’édition du 10 octobre intégrée et la révision éditoriale du 17 octobre consultée.
