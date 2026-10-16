# Révision du 10 octobre 2026 — manuel, chapitres 10 à 17

Les huit chapitres ont été relus intégralement. Leurs titres de chapitre et de
section, leurs 58 identifiants de section et leur niveau mathématique sont
conservés. Les sources d'août et les PDF de septembre restent inchangés.

## Corrections mathématiques et figures

| Constat | Source active | Correction et contrôle |
|---|---|---|
| AUD-06 | [ch13.tex, §13.6](../sources/manual/chapters/ch13.tex) | Région de sommets `(0,0)`, `(6,0)`, `(5,3)`, `(0,8)`; calcul de l'intersection et tableau des profits `0,420,470,320`. Niveau optimal de pente `−7/4`. |
| AUD-07 | [ch13.tex, §13.5](../sources/manual/chapters/ch13.tex) | Contraintes numériques explicites pour le polygone; objectif `3x+2y`; calcul des deux intersections; niveaux parallèles et maximum `72/5` en `(16/5,12/5)`. |
| AUD-09 | [ch14.tex, §14.6](../sources/manual/chapters/ch14.tex) | Triangle de côté `2`, hauteur `√3`; arcs de `60°` à la base et `30°` au sommet; carré d'angle droit au pied de la hauteur. |
| AUD-15 | [ch11.tex, §11.6](../sources/manual/chapters/ch11.tex) | Deux familles issues de `(u,v) → (2u+v,v)`: `x−y=2c` et `y=c`. Même échelle dans les deux panneaux; traits pleins et interrompus distinguent les familles sans couleur. |
| AUD-18 | [ch17.tex, §17.5](../sources/manual/chapters/ch17.tex) | Période temporelle, longueur d'onde, unités, fréquence, phase constante et dérivation de `v=ω/k=λ/T`. Exemple enseigné distinct de l'exercice du cahier, avec le même type de modèle. |
| Hypothèse de rotation | [ch17.tex, §17.1, 17.2 et 17.8](../sources/manual/chapters/ch17.tex) | Rotation uniforme explicite; sens antihoraire de l'exemple initial; distinction déplacement/position angulaire et valeur absolue de la vitesse. |
| Figure SSA | [ch15.tex, §15.4](../sources/manual/chapters/ch15.tex) | Deux intersections exactes du rayon d'angle `30°` avec le cercle de centre `(5,0)` et de rayon `3`; les anciens points dessinés n'appartenaient pas au cercle. |

Les huit tests dans
[test_revision_manual_b.py](../tests/test_revision_manual_b.py) lisent les
coordonnées et segments du TEX actif. Ils recalculent indépendamment les
intersections admissibles, les valeurs de l'objectif, les normales communes
aux niveaux, les images des deux familles de grille, les rapports du triangle,
les intersections SSA et les répétitions spatio-temporelles des ondes.

Commande exécutée :

```sh
python3 -m unittest discover -s books/mat0339/tests -p test_revision_manual_b.py -v
```

Résultat : **8 tests réussis**. Le contrôle d'onde inclut le cas du cahier
`y=3 sin(2πx/5−4πt)` : `λ=5 m`, `T=0,5 s`, `v=10 m/s` vers les `x` croissants.

## Relecture du français

| Chapitres | Changements de rédaction |
|---|---|
| 10–12 | Formulations directes pour les représentations, les normales, les opérations sur les lignes et les pivots; explication de la réversibilité de l'élimination; suppression des commentaires valorisant la méthode. |
| 13 | Consignes liées aux variables, unités, demi-plans et profits; remplacement des jugements généraux sur les erreurs par des contrôles précis; justification du maximum sur la frontière. |
| 14–15 | Explications des rapports et des conversions sans slogans sur la mémorisation; correspondance côté-angle opposé explicite; consigne de conserver la précision avant l'arrondi. |
| 16–17 | Sens concret des paramètres, translation vers la gauche ou la droite selon le signe, distinction durée/distance; modèles présentés avec leurs hypothèses et leurs limites d'observation. |

Les huit encadrés de fin répétaient les définitions et méthodes immédiatement
précédentes; ils ont été retirés. Les exemples, contre-exemples, avertissements
mathématiques et contrôles utiles sont conservés. Les changements ont été faits
par passage, sans remplacement global de vocabulaire.

## Inspection du rendu et clôture des constats

Le premier contrôle de mise en page a porté sur toutes les pages physiques
**117 à 198**, au moyen des planches de quatre pages rendues à 65 dpi. Les
anomalies visibles suivantes ont ensuite été corrigées : tableau trop étroit
en 15.2, étiquettes touchant des traits dans les figures d'élimination et SSA,
annotation opaque sur les niveaux d'objectif, étiquette d'angle trop proche de
son arc, et indications de période masquant le sommet de deux sinusoïdes.

Après compilation, les pages **128, 138–140, 148–152, 159–161, 165–170 et
187–191** ont été rendues à 130 dpi et réexaminées. Le dernier ajustement de
l'étiquette `h`, page 190, a été vérifié sur les pages **189–191** après la
dernière compilation. Aucune collision ni coupure restante n'a été observée
dans ce périmètre. Le contrôle des en-têtes, géré dans le préambule commun,
est inclus dans le [rapport général](revision-2026-10-10.md).

La comparaison des pixels entre les deux derniers rendus a aussi signalé une
redistribution du texte aux pages **171–172**. Ces deux pages du PDF final ont
été inspectées à 65 dpi dans `build/review-2026-10-10/manual-final-65/` : exemples,
formules de sinus et de cosinus, listes et encadré poursuivi d'une page à l'autre
restent lisibles, sans collision ni coupure de contenu. Aucune retouche
supplémentaire n'a été nécessaire.

| Constat | Page physique / imprimée | Résultat du contrôle final |
|---|---|---|
| AUD-06 | 151 / 141 | Remplissage raccordé en `(5,3)`; contraintes, objectif et tableau cohérents. Traits plein, interrompu et mixte lisibles en niveaux de gris. Clos pour cette édition. |
| AUD-07 | 149 / 139 | Niveaux parallèles, sommet optimal identifié, aucune annotation sur les tracés. Contrôle couleur et niveaux de gris réussi. Clos pour cette édition. |
| AUD-09 | 160 / 150 | `30°` au sommet sur son arc; `60°` à la base; angle droit et longueurs visibles. Contrôle couleur et niveaux de gris réussi. Clos pour cette édition. |
| AUD-15 | 128 / 118 | Les deux familles de grille et les images des vecteurs de base sont visibles à une même échelle. Contrôle couleur et niveaux de gris réussi. Clos pour cette édition. |
| AUD-18 | 187–188 / 177–178 | Fréquence, période temporelle, longueur d'onde et unités définies; vitesse déduite d'une phase constante avant l'exemple et l'exercice du cahier. Clos pour cette édition. |
| Compléments graphiques | 139, 166, 169, 189–190 | Trait de rappel, tableau à deux colonnes, étiquettes SSA et périodes dégagés. |

Les pages **128, 149, 151, 160, 169, 188 et 190** ont aussi été inspectées en
niveaux de gris à 130 dpi. Les preuves locales sont dans
`build/review-2026-10-10/manual-b-final/` : `page-NNN.png` pour la couleur,
`page-NNN-gray.png` pour le monochrome. Ces rendus de contrôle restent hors Git.

PDF final contrôlé : `dist/MAT0339_manuel_2026-10-10.pdf`, **198 pages**,
SHA-256 `d27238c6cfbf8556dd61f257f40d0288a7b8a6313ecef18db07a42bffc8dbe16`.
Les huit tests ciblés ont réussi après les corrections; les résultats de
compilation et de vérification globale sont consignés séparément dans le
rapport général. Cette clôture concerne les défauts identifiés et les pages
examinées; elle ne constitue pas une approbation institutionnelle ni une
certification mathématique exhaustive du manuel.
