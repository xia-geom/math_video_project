# 72 — Deux extrêmes ne donnent pas toujours une période

Objectif : identifier les extrêmes consécutifs d’une sinusoïde non constante
pour distinguer une demi-période d’une période complète, puis valider le
modèle aux instants observés.

Sources actuelles : manuel MAT0339, annexe A, § A.7 « Construire un modèle
périodique à partir d’observations » et § A.8 « Construire et valider un
modèle périodique » ; cahier, synthèse de l’annexe A, S1, et exercice A.7,
partie A. Voir les sources du [manuel](../../../books/mat0339/sources/manual/appendices/circular_motion.tex)
et du [cahier](../../../books/mat0339/sources/workbook/appendices/circular_motion.tex),
édition de travail du 6 novembre 2026. Les identifiants historiques `17.7`
et `17.8` sont conservés ; seul leur affichage devient `A.7` et `A.8`,
conformément à la [migration documentée](../../../books/mat0339/docs/section-migration-2026-11-06.md).
Le chapitre 17 actuel porte sur les nombres complexes.

**Hypothèses explicites et provenance.** Les valeurs du cahier sont
conservées. L’édition du 10 octobre 2026, commit
`4d451c37d483d763e33683a7fb683d1e0fdde62d`, ne précisait pas que le minimum
de la marée était le suivant ni que les trois maxima de l’ancien exercice
17.7 A étaient consécutifs. La révision du 17 octobre, PR #29, commit
`e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, a ajouté ces précisions,
reprises dans les sources actuelles de l’annexe A. La capsule les annonce
comme hypothèses nécessaires ; elle ne les attribue pas au libellé
antérieur. Une marée réelle n’est pas supposée exactement sinusoïdale en
dehors du modèle choisi.

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
