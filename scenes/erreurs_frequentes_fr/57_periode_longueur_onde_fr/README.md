# 57 — Période, longueur d'onde et vitesse

**Objectif :** distinguer une répétition spatiale d'une répétition temporelle,
puis relier les deux par la vitesse de propagation. Prérequis : fonction
sinus, période, radians et unités.

L'exemple du manuel \(y(x,t)=2\sin(\pi x-2\pi t)\) est lu de deux
façons. Une photographie à \(t=0\) donne \(\lambda=2\,\mathrm{m}\);
un enregistrement à \(x=0\) donne \(T=1\,\mathrm{s}\). Les axes sont
étiquetés avec la variable et son unité. Des flèches mesurent les écarts
entre deux crêtes ou deux maxima **consécutifs**.

L'animation suit une même crête en bleu et la hauteur à une position fixe
en noir, pendant une seconde du modèle affichée au ralenti. La crête avance
de deux mètres; l'observateur fixe voit un cycle vertical. Ces deux mouvements
ne doivent pas être confondus. Une page relie ensuite ce déplacement au calcul :
la phase constante \(\pi x-2\pi t=\pi/2\) donne \(x(t)=1/2+2t\) pour
la crête suivie. Avec \(+2\pi t\), elle donne \(x(t)=1/2-2t\), ce qui
justifie le sens opposé sans règle de signe à mémoriser isolément. Les objets
dynamiques appartiennent à leur page et leurs mises à jour sont arrêtées
avant de changer de page. Le compteur remplacé par la vitesse est retiré
du groupe de sa page avant le fondu de sortie, pour éviter sa réapparition.
Chaque graphe identifie aussi la hauteur
\(y\) en mètres sur son axe vertical.

Pour \(y=A\sin(kx-\omega t+\varphi)\), sous les hypothèses
\(A\ne0\), \(k>0\), \(\omega>0\), la capsule explique
\(\lambda=2\pi/k\), \(T=2\pi/\omega\), \(f=1/T\) et
\(v=\lambda/T=\omega/k\). Le signe \(+\omega t\) inverse le sens
de propagation. Deux ondes ayant la même photographie à \(t=0\) mais
des fréquences différentes montrent pourquoi une courbe spatiale seule
ne détermine pas la période temporelle.

**Autocontrôle du cahier, exercice 17.5 A :**
\(y(x,t)=3\sin(2\pi x/5-4\pi t)\), avec \(x,y\) en mètres
et \(t\) en secondes. Après six secondes de réflexion, une page séparée
donne amplitude \(3\,\mathrm{m}\), longueur d'onde
\(5\,\mathrm{m}\), période \(1/2\,\mathrm{s}\), fréquence
\(2\,\mathrm{Hz}\) et vitesse \(10\,\mathrm{m/s}\), vers les
\(x\) croissants. Les valeurs et leurs unités sont justifiées, avec les
coefficients explicitement exprimés en \(\mathrm{rad/m}\) pour \(k\) et
en \(\mathrm{rad/s}\) pour \(\omega\).

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch17.tex`, section 17.5,
  `manual:section:17.05`, « Interprétation ondulatoire »; sous-sections
  « Période temporelle et longueur d'onde » et « Suivre une même phase ».
- `books/mat0339/sources/workbook/chapters/ch17.tex`, section 17.5,
  `workbook:section:17.05`, exercices A–C.
- Édition du 10 octobre intégrée à `main` au commit
  `4d451c37d483d763e33683a7fb683d1e0fdde62d`, comparée à la révision
  éditoriale du 17 octobre, commit
  `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`. Les passages utilisés sont
  inchangés dans cette seconde révision, encore distincte de `main` au
  moment de cette mise à jour.

**Classe :** `PeriodeLongueurOndeFR`. Narration française et sous-titres
par `TeachingScene`, avec le service d'enseignement partagé.
`MANIM_DISABLE_VOICEOVER=1` sélectionne une prévisualisation silencieuse;
sa durée ne représente pas celle de la narration. Aucun rendu ni appel
de synthèse ne se produit à l'import. Les médias générés restent hors Git.
