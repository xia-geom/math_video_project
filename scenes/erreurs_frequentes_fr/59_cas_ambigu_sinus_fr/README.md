# 59 — Deux côtés et un angle : zéro, un ou deux triangles

**Objectif :** former les candidats de la loi des sinus puis vérifier
qu'ils définissent des triangles non aplatis. Prérequis : côtés opposés,
loi des sinus, arcsinus et somme des angles d'un triangle.

L'exemple principal est celui du manuel : \(A=30^\circ\), \(a=7\),
\(b=10\). Dans la figure, \(A\) et \(C\) sont fixes; \(B\) doit
appartenir à une demi-droite issue de \(A\) et au cercle de centre
\(C\), de rayon \(a\). Les deux intersections sont construites avec
la même échelle horizontale et verticale. Leurs bases valent
\(5\sqrt3+2\sqrt6\) et \(5\sqrt3-2\sqrt6\), toutes deux positives.
La loi des sinus donne les angles \(B_1=\arcsin(5/7)\) et
\(B_2=180^\circ-B_1\); chacun laisse un angle \(C\) positif.

Avec \(A=30^\circ\), \(b=10\), la hauteur critique est \(5\).
Les variantes \(a=4\), \(a=5\), \(a=7\) et \(a=10\) expliquent
respectivement aucun triangle, un triangle tangent, deux triangles et
un seul triangle après rejet d'une intersection en \(A\).
La règle générale exige \(A+B<180^\circ\). Le cas \(k=1\), où
\(k=b\sin A/a\), ne donne un triangle que si \(A<90^\circ\).

**Autocontrôle original :** \(A=120^\circ\), \(a=b=6\). Les angles
candidats \(B=60^\circ\) et \(B=120^\circ\) donnent un troisième
angle nul ou négatif. Aucun triangle non aplati n'existe. La réponse
apparaît sur une page séparée après six secondes de réflexion.

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch15.tex`, sections 15.4 et
  15.5 (`manual:section:15.04`, `manual:section:15.05`).
- `books/mat0339/sources/workbook/chapters/ch15.tex`, exercice 15.5 B
  et synthèse S3. Les variantes et l'autocontrôle sont des transferts.
- Le manuel intégré à `main`, commit
  `4d451c37d483d763e33683a7fb683d1e0fdde62d`, contient l'exemple principal.
  La correction éditoriale `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`
  précise explicitement le cas \(k=1\) et l'exclusion des intersections
  dégénérées; la capsule tient compte de ces précisions.

**Classe :** `CasAmbiguSinusFR`. Narration française par le service partagé,
une ouverture UQAM, géométrie sans déformation des échelles.
`MANIM_DISABLE_VOICEOVER=1` sélectionne la prévisualisation silencieuse.
Médias générés hors Git; narration et publication restent des étapes
distinctes de l'écriture et du rendu silencieux.
