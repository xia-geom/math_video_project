# 72 — Deux extrêmes ne donnent pas toujours une période

Objectif : identifier les extrêmes consécutifs d’une sinusoïde non constante
pour distinguer une demi-période d’une période complète, puis valider le
modèle aux instants observés.

Sources : manuel MAT0339, § 17.7 « Construire un modèle périodique à partir
d’observations » et § 17.8 « Construire et valider un modèle périodique » ;
cahier, synthèse du chapitre 17, S1, et exercice 17.7 A. Fichiers actifs :
`books/mat0339/sources/manual/chapters/ch17.tex` et
`books/mat0339/sources/workbook/chapters/ch17.tex`, édition du 10 octobre
2026, commit `4d451c37d483d763e33683a7fb683d1e0fdde62d`.

**Hypothèses explicites et provenance.** Les valeurs du cahier sont
conservées, mais l’édition du 10 octobre ne précise pas que le minimum de
la marée est le suivant ni que les trois maxima de 17.7 A sont consécutifs.
La révision proposée le 17 octobre dans la PR #29, commit
`e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, ajoute exactement ces précisions.
La capsule les annonce comme hypothèses nécessaires ; elle ne les attribue
pas au libellé antérieur. Une marée réelle n’est pas supposée exactement
sinusoïdale en dehors du modèle choisi.

Exemple travaillé : maximum de 4,8 m à 3 h, puis **minimum suivant** de
0,8 m à 9,2 h. Le point animé descend au minimum, puis retrouve le maximum
suivant à 15,4 h. Ainsi, \(T/2=6{,}2\) h, \(T=12{,}4\) h,
\(D=2{,}8\) m et \(A=2\) m. Le modèle
\(h(t)=2{,}8+2\cos(2\pi(t-3)/12{,}4)\) reproduit ces trois valeurs.
Choisir la période erronée 6,2 h prédirait un maximum à 9,2 h.

La condition « suivant » est justifiée : pour un minimum ultérieur
quelconque, \(\Delta t=(j+1/2)T\), \(j\in\mathbb N_0\). Une même
séparation de 6,2 h permet donc, par exemple, les périodes 12,4 h et
\(12{,}4/3\) h si l’on ignore combien d’extrêmes ont été manqués. La règle
\(T/2\) n’est pas affirmée pour tout phénomène périodique.

Autocontrôle : maxima **consécutifs** à 2, 10 et 18 h, hauteur maximale
15 m et minimale 3 m. Une pause de six secondes précède la réponse séparée :
\(T=8\) h, \(D=9\) m, \(A=6\) m et
\(h(t)=9+6\cos(\pi(t-2)/4)\). La vérification donne
\(h(2)=15\), \(h(6)=3\), \(h(10)=15\). Les unités explicites de cet
autocontrôle sont un choix pédagogique ajouté aux valeurs du cahier.

Classe : `ExtremaDemiPeriodeFR`. La scène utilise `TeachingScene`, le
profil de narration partagé et une seule ouverture UQAM.
`MANIM_DISABLE_VOICEOVER=1` sélectionne un aperçu silencieux ; cet aperçu
ne certifie pas une livraison narrée. Les vérifications effectuées sont
consignées dans le rapport du lot.
