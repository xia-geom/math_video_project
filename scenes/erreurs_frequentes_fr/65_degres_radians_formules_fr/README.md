# 65 — Degrés dans les formules en radians

Objectif : identifier l’unité exigée par une formule ou par le mode d’une
calculatrice, convertir au besoin, puis vérifier la fraction du cercle et
les unités du résultat.

Sources : manuel MAT0339, § 14.1 « Degrés et radians », § 14.6 « Pourquoi
les radians simplifient les formules » et § 14.7 « Mesurer et lire une
rotation » ; cahier, exercices 14.6 A et 14.7 B–C. Les fichiers actifs sont
`books/mat0339/sources/manual/chapters/ch14.tex` et
`books/mat0339/sources/workbook/chapters/ch14.tex`, édition du 10 octobre
2026, commit `4d451c37d483d763e33683a7fb683d1e0fdde62d`. Ces passages ont
également été vérifiés dans la révision du 17 octobre, commit
`e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, encore proposée dans la PR #29.

L’exemple initial est une adaptation originale de la conversion de
\(60^\circ\) du manuel : avec \(r=6\,\mathrm{cm}\), la substitution erronée
\(6\times60=360\,\mathrm{cm}\) dépasse la circonférence entière
\(12\pi\,\mathrm{cm}\). Un point parcourt réellement un sixième de cercle
pendant que le rayon tourne. La conversion \(60^\circ=\pi/3\,\mathrm{rad}\)
donne l’arc \(s=2\pi\,\mathrm{cm}\), puis l’aire du secteur
\(\mathcal A=6\pi\,\mathrm{cm}^2\).

Les formules \(s=r\theta\) et \(\mathcal A=r^2\theta/2\) sont annoncées
avec \(r>0\) et \(0\leq\theta\leq2\pi\), où \(\theta\) est la mesure
en radians d’un secteur ordinaire. L’arc est distingué de la corde ; les
rotations orientées ou les tours supplémentaires ne sont pas confondus
avec cette aire de secteur. La fraction du tour justifie aussi les versions
des formules en degrés.

Le diagnostic de calculatrice reprend C14.7 C : en mode DEG, une saisie
\(\pi/6\) est interprétée comme \((\pi/6)^\circ\), et son sinus vaut
environ \(0{,}0091\). Les deux calculs corrects sont une saisie \(\pi/6\)
en mode RAD ou une saisie \(30\) en mode DEG, tous deux donnant \(1/2\).
Le symbole \(\pi\) ne sélectionne pas à lui seul le mode de la calculatrice.

Autocontrôle C14.7 B, avec les valeurs exactes du cahier et sans unité
de longueur imposée : \(r=4\), \(\theta=5\pi/6\). Après une pause de
six secondes, les réponses sont \(s=10\pi/3\) et
\(\mathcal A=20\pi/3\), contrôlées par la fraction \(5/12\) du cercle.
La narration distingue les unités de longueur et d’aire.

Classe : `DegresRadiansFormulesFR`. La scène utilise `TeachingScene`,
le profil de narration partagé et une seule ouverture UQAM.
`MANIM_DISABLE_VOICEOVER=1` sélectionne explicitement un aperçu silencieux.
Un tel aperçu ne certifie pas une livraison narrée ; les contrôles
effectivement réalisés figurent dans le rapport du lot.
