# 73 — La demi-vie de l’écart à l’équilibre

Objectif : appliquer la demi-vie à l’écart entre la température d’un objet
et la température ambiante constante, puis vérifier qu’un seuil demandé
est atteignable dans le domaine temporel du modèle.

Sources : manuel MAT0339, § 6.8, sous-section « Refroidissement : un modèle
avec valeur d’équilibre » ; cahier, exercice 6.8 C. Fichiers actifs :
`books/mat0339/sources/manual/chapters/ch06.tex` et
`books/mat0339/sources/workbook/chapters/ch06.tex`, édition du 10 octobre
2026, commit `4d451c37d483d763e33683a7fb683d1e0fdde62d`. La révision du
17 octobre proposée dans la PR #29, commit
`e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, explicite les minutes, l’unité
de \(k\) et le fait que le modèle reste strictement au-dessus de l’ambiante.
Ces conditions sont annoncées dans la capsule.

**Adaptations originales.** Le manuel utilise exactement
\(T(t)=20+70e^{-0{,}18t}\), avec température initiale 90 °C et seuil
35 °C atteint après environ 8,56 minutes. La capsule conserve la structure
mais choisit \(T(t)=20+60\,2^{-t/10}\), \(t\ge0\) en minutes, pour
rendre les demi-vies visibles. Ces valeurs ne sont pas présentées comme
les données exactes de l’exercice du livre.

Le graphique animé mesure la barre verticale depuis l’ambiante 20 °C,
puis suit l’objet à 0, 10 et 20 minutes. L’écart \(E(t)=T(t)-20\) passe
de 60 à 30 puis 15 °C ; la température passe de 80 à 50 puis 35 °C.
Les nombres du compteur animé sont arrondis à l’entier pendant le mouvement ;
les valeurs aux instants expliqués sont exactes. Le compteur ne représente
pas une mesure expérimentale.

Le passage de **80 à 40 °C** est une autre question : il demande de diviser
l’écart par trois et prend \(10\ln(3)/\ln(2)\approx15{,}85\) minutes.
La capsule parle de la lecture en degrés Celsius ; elle ne présente pas
un rapport de températures Celsius comme un rapport d’énergies physiques.

Le modèle général est \(T(t)=T_a+(T_0-T_a)e^{-kt}\), avec
\(t\ge0\), \(k>0\), ambiante constante et \(T_0>T_a\) pour le cas de
refroidissement étudié. L’écart positif a demi-vie \(\tau=\ln2/k\).
Dans l’adaptation, \(k=\ln2/10\,\mathrm{min}^{-1}\). Si \(T_0=T_a\),
la température est constante ; le cas de réchauffement depuis une valeur
inférieure n’est pas traité comme un refroidissement.

Pour tout temps fini \(t\ge0\), \(20<T(t)\le80\). L’équilibre 20 °C
est approché sans être atteint exactement ; un seuil inférieur est impossible
dans ce modèle. Un seuil \(20<C\le80\) donne
\(t=10\log_2(60/(C-20))\). Un seuil supérieur à 80 donnerait un temps
négatif hors du domaine. Une lecture arrondie à l’équilibre est distinguée
de l’égalité mathématique exacte.

Autocontrôle distinct, également adapté :
\(T(t)=10+60\,2^{-t/4}\), \(t\ge0\) en minutes. Après une pause de
six secondes, la page de réponse donne \(T(4)=40\) °C et le temps pour
atteindre 25 °C, soit 8 minutes : l’écart 15 est le quart de l’écart initial
60. La substitution finale valide le résultat.

Classe : `RefroidissementEcartEquilibreFR`. La scène utilise `TeachingScene`,
le profil de narration partagé et une seule ouverture UQAM.
`MANIM_DISABLE_VOICEOVER=1` sélectionne un aperçu silencieux ; les
vérifications du lot ne constituent pas une certification de livraison narrée.
