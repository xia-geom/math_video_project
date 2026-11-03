# 64 — Vecteur normal et vecteur directeur

**Objectif :** distinguer le vecteur normal lu dans une équation cartésienne
d'une direction permettant de parcourir la droite. Prérequis : coordonnées,
addition de vecteurs, produit scalaire et test d'appartenance d'un point.

L'exemple du manuel \(2x-3y=6\) donne le normal \(\vec n=(2,-3)\)
et le directeur \(\vec v=(3,2)\). Depuis \(P=(3,0)\), un point animé
suit successivement les deux déplacements : \(P+\vec v=(6,2)\) reste
sur la droite; \(P+\vec n=(5,-3)\) donne \(19\ne6\) après substitution.
Les axes utilisent la même échelle géométrique pour préserver visuellement
la perpendicularité. Les flèches, leurs symboles et un angle droit
distinguent les deux rôles au-delà de leur couleur.

La justification générale part de \(Ax_0+By_0=C\) et du déplacement
\(P+t\vec v\). La substitution donne \(C+t(Av_x+Bv_y)\), qui reste
égal à \(C\) pour tout \(t\in\mathbb R\) exactement lorsque
\((A,B)\cdot\vec v=0\). Les conditions \((A,B)\ne(0,0)\) et
\(\vec v\ne\vec0\) sont explicites. Le choix \((-B,A)\), son
opposé ou tout multiple non nul convient comme directeur. Les multiples
non nuls du normal restent également normaux.

Le cas vertical \(2x=6\) est traité sans calcul de pente : normal
\((2,0)\), directeur \((0,1)\), paramétrisation
\((x,y)=(3,0)+t(0,1)\). La capsule comporte neuf pages distinctes.

**Autocontrôle :** exercice 10.2 A du cahier,
\(3x-2y+7=0\), avec vérification supplémentaire depuis
\(P=(-1,2)\). Une pause de six secondes précède la réponse séparée :
\(\vec n=(3,-2)\), \(\vec v=(2,3)\), produit scalaire nul,
puis \(P+\vec v=(1,5)\), qui satisfait la même équation.
Les points de contrôle et les déplacements animés sont des développements
pédagogiques de l'exemple et de l'exercice du livre.

**Sources actives dans Git :**

- [Manuel, chapitre 10](../../../books/mat0339/sources/manual/chapters/ch10.tex),
  §10.2 « Vecteur normal » et §10.7 « Choisir et exploiter une représentation ».
- [Cahier, chapitre 10](../../../books/mat0339/sources/workbook/chapters/ch10.tex),
  exercices 10.2 A–C.
- Édition du 10 octobre intégrée à `main`, commit
  `4d451c37d483d763e33683a7fb683d1e0fdde62d`, comparée à la révision
  du 17 octobre, commit `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`.
  Les passages utilisés sont identiques dans ces deux états; la seconde
  révision reste distincte de `main` au moment de l'écriture.

**Identité stable :** `vecteur_normal_directeur`.
**Classe :** `VecteurNormalDirecteurFR`. Narration française et sous-titres
par `TeachingScene`; une seule ouverture UQAM. `MANIM_DISABLE_VOICEOVER=1`
sélectionne explicitement une prévisualisation silencieuse, dont la durée
ne représente pas celle de la narration. L'import ne déclenche ni synthèse
vocale ni publication. Les médias générés restent hors Git.
