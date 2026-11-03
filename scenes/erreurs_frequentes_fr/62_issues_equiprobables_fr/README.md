# Des résultats possibles ne sont pas forcément équiprobables

Capsule 62, identifiant stable `issues_equiprobables`, classe
`IssuesEquiprobablesFR`. Le [catalogue unique](../../../curriculum/programme_principal_fr.yaml)
fixe son numéro, ses prérequis et son état de production.

## Objectif

Justifier les probabilités des issues élémentaires avant d'employer le rapport
des nombres de cas. Une catégorie peut regrouper plusieurs issues; le nombre
de catégories ne détermine pas leur probabilité.

## Exemples et contrôles

- Deux lancers indépendants d'une pièce équilibrée : les quatre suites
  \(FF,FP,PF,PP\) ont chacune probabilité \(1/4\). Le nombre de piles prend
  les valeurs \(0,1,2\) avec probabilités \(1/4,1/2,1/4\).
- Deux dés équilibrés, indépendants et distinguables : les 36 couples sont
  équiprobables. Une somme de 7 a six réalisations; une somme de 2 en a une.
- Variante avec \(P(P)=0{,}6\) et lancers indépendants : une seule pile a
  probabilité \(0{,}4\cdot0{,}6+0{,}6\cdot0{,}4=0{,}48\).
- Exercice de contrôle : \(P(S\ge10)=(3+2+1)/36=1/6\). Les six couples sont
  montrés dans la grille après une pause de réflexion de six secondes.

Les cartes, barres et grilles représentent des probabilités calculées à partir
du modèle. Elles ne sont pas les résultats d'une simulation empirique.

## Références actuelles

Manuel 8.2 et 8.9; cahier 8.2B–C et variante de 8.4C. La référence intégrée est
l'édition du 10 octobre 2026 dans Git, commit `4d451c3`; la révision du
17 octobre proposée au commit `e418c5e` a également été consultée. Les anciennes
pièces jointes d'août ne sont pas la base de cette capsule.

La source comporte une narration française et utilise le mode silencieux
explicite pour la prévisualisation. Le bilan réel de rendu et de vérification
est dans le [rapport du lot](../../../reports/error_capsules/2026-10-31/AUDIT.md).
