# Sans remise : actualiser les probabilités conditionnelles

Capsule 63, identifiant stable `tirages_sans_remise`, classe
`TiragesSansRemiseFR`. Le [catalogue unique](../../../curriculum/programme_principal_fr.yaml)
fixe son numéro, ses prérequis et son état de production.

## Objectif

Décrire la composition restante du sac, multiplier les probabilités
conditionnelles le long d'un chemin, puis additionner les chemins favorables
disjoints. Chaque boule restante a la même chance d'être tirée.

## Exemples et contrôles

Le modèle du manuel 8.9 contient cinq boules rouges et trois bleues. Sans remise,
\[
P(R_1\cap R_2)=\frac58\frac47=\frac5{14},\qquad
P(\text{une de chaque})=\frac58\frac37+\frac38\frac57=\frac{15}{28}.
\]

Une distinction essentielle est explicitée : sans connaître le premier
résultat, \(P(R_2)=5/8\), tandis que \(P(R_2\mid R_1)=4/7\).
L'égalité des probabilités marginales ne prouve donc pas l'indépendance.
Avec remise et un nouveau choix uniforme indépendant, la probabilité de deux
rouges devient \((5/8)^2=25/64\).

Le contrôle utilise le sac de trois rouges et deux bleues du manuel 8.3, avec
une question de transfert : obtenir une boule de chaque couleur. Les deux
chemins donnent \(3/5\cdot2/4+2/5\cdot3/4=3/5\). La réponse suit une pause
de réflexion de six secondes.

## Références actuelles

Manuel 8.3 et 8.9; cahier 8.3C pour la règle du produit. Les questions de
transfert sont distinguées des exercices repris à l'identique. La référence
intégrée est l'édition du 10 octobre 2026 dans Git, commit `4d451c3`; la révision
du 17 octobre proposée au commit `e418c5e` a également été consultée.

La source comporte une narration française et utilise le mode silencieux
explicite pour la prévisualisation. Le bilan réel de rendu et de vérification
est dans le [rapport du lot](../../../reports/error_capsules/2026-10-31/AUDIT.md).
