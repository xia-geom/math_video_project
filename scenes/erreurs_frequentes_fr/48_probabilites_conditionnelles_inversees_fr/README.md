# 48 — Probabilités conditionnelles inversées

Objectif : choisir le groupe de référence avant le dénominateur et distinguer \(P(M\mid F)\) de \(P(F\mid M)\).

Sources : manuel MAT0339, § 8.3 « Probabilité conditionnelle » et § 8.8
« Le conditionnement avec des effectifs concrets » ; cahier, exercice 8.3 B
(deuxième question). Sources actives :
`books/mat0339/sources/manual/chapters/ch08.tex` et
`books/mat0339/sources/workbook/chapters/ch08.tex`, édition du 10 octobre 2026,
également vérifiées dans la révision du 17 octobre. Les effectifs de la classe
sont repris exactement : 18 femmes dont 6 en maths, 12 hommes dont 3 en maths.
Le contre-exemple est \(1/3\ne2/3\).

Animation : les points représentent les 30 personnes. Le cadre sélectionne les femmes ; les neuf personnes en maths sont ensuite regroupées sans modifier leur identité. Le numérateur reste six alors que le dénominateur passe de dix-huit à neuf.

Le second exemple reprend le modèle fictif de la section 8.8 : 10 000 personnes,
dont 2 % malades, avec sensibilité de 95 % et taux de faux positifs de 4 %.
Les effectifs sont 200 malades, dont 190 positifs, et 9 800 non-malades, dont
392 positifs. Un cadre sélectionne successivement la ligne des malades et la
colonne des tests positifs. Ainsi \(P(+\mid M)=190/200=95\%\), tandis que
\(P(M\mid+)=190/582\approx32{,}65\%\). La scène annonce explicitement qu’il
s’agit d’un modèle fictif ; les taux ne décrivent pas un test réel.

Autocontrôle original : club de 20 membres, 8 pianistes, 5 violonistes, 3 pratiquant les deux. Réponses \(3/8\) et \(3/5\), après une pause de réflexion de six secondes.

Classe : `ProbabilitesConditionnellesInverseesFR`. La narration utilise `TeachingScene`, le profil partagé et une seule ouverture UQAM. `MANIM_DISABLE_VOICEOVER=1` demande explicitement un aperçu silencieux. Aucun rendu silencieux ne certifie une livraison avec voix. Les vérifications réalisées pour le lot figurent dans son rapport daté.
