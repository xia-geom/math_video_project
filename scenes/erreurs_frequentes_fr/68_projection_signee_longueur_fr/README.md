# 68 — Une projection signée n’est pas une longueur

Objectif : distinguer la composante signée d’un vecteur, sa projection vectorielle
et la longueur de cette projection. La projection porte sur toute la droite
\(\mathbb R\vec v\), et non sur la seule demi-droite positive.

Sources : manuel MAT0339, sections 9.4 et 9.7, et cahier 9.7 A–B, dans
`books/mat0339/sources/manual/chapters/ch09.tex` et
`books/mat0339/sources/workbook/chapters/ch09.tex`. Ces passages sont identiques
dans le livre intégré du 10 octobre 2026 et la révision du 17 octobre consultée.

L’exemple principal est un transfert original : \(\vec u=(-3,2)\),
\(\vec v=(2,0)\). Le produit scalaire vaut \(-6\), la composante signée
\(c=(\vec u\cdot\vec v)/\|\vec v\|=-3\), le projeté \((-3,0)\)
et sa longueur \(3\). Une descente perpendiculaire relie l’extrémité de
\(\vec u\) à son projeté; les deux axes utilisent exactement la même échelle.
Le reste \((0,2)\) est orthogonal à \(\vec v\).

La formule vectorielle est justifiée à partir de \(\vec p=\alpha\vec v\) et
\((\vec u-\vec p)\cdot\vec v=0\). L’hypothèse \(\vec v\ne\vec0\)
autorise la division par \(\|\vec v\|^2\). Inverser l’orientation de la
même droite change le signe de la composante, sans changer le vecteur projeté
ni sa longueur. Le cas \(\vec u=\vec0\) est explicitement admis.

Autocontrôle : exemple exact du cahier 9.7 B, \(\vec u=(3,4)\),
\(\vec v=(1,2)\), avec une pause de six secondes. Réponses : composante
\(11/\sqrt5\), projeté \((11/5,22/5)\), longueur \(11/\sqrt5\).
Le reste \((4/5,-2/5)\) a un produit scalaire nul avec \(\vec v\).

Classe publique : `ProjectionSigneeLongueurFR`. Dix pages, narration française
avec `TeachingScene`, service partagé et une seule ouverture UQAM.
`MANIM_DISABLE_VOICEOVER=1` demande explicitement un aperçu silencieux;
un tel aperçu ne certifie ni l’écoute ni une livraison narrée. Les contrôles
effectués sont consignés dans le rapport daté du lot.
