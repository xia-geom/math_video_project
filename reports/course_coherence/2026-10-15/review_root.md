# Revue des images encodées — leçons 16 à 29

L’agent principal a inspecté les planches de toutes les cartes d’ouverture,
de chapitre, de récapitulatif, de pratique et de fin, ainsi que les états
intermédiaires échantillonnés des 14 MP4. Les dernières images encodées ont
été comparées dans une planche commune. Les empreintes et horodatages
inspectés sont consignés dans `root_review_samples.json`.

Ces scènes ont été écrites par un autre agent. Cette inspection porte sur des
images réellement extraites des vidéos 854 × 480, 15 i/s. Elle ne constitue
ni une lecture continue, ni une écoute, ni une étude d’apprentissage.

## Défaut corrigé

- **21, 40,377 s** : le libellé AB conservé était rendu à 32 % d’opacité,
  environ 2,2:1 sur blanc. L’étiquette reste maintenant noire et opaque;
  seule la flèche inactive reste atténuée. L’image native du nouveau rendu
  `attempt_03/21`, au même instant, confirme la lisibilité du libellé,
  de BA = −AB et des coordonnées. Les cartes et la dernière image du
  nouveau rendu ont également été inspectées.

## Vérifications et limites

- Les exemples vus conservent leurs hypothèses et leurs calculs : temps
  continu/entier de croissance; dénombrement avec ou sans ordre; cas disjoints;
  répétitions; probabilités; opérations vectorielles; équations de droite et
  de plan; produits matriciels; déterminant et inverse; élimination et Cramer.
- Les trois ou quatre chapitres gardent leur ordre et seul le chapitre courant
  est en gras. Les fins reprennent un exemple déjà corrigé et gardent la
  carte finale visible. Aucun compteur « Étape N sur … » ne réapparaît.
- **26, 14,300 et 51,200 s**, images natives supplémentaires : l’amorce et le
  produit matrice-vecteur sont lisibles. Deux vignettes sélectionnées près
  de la fin d’un fondu ne suffisaient pas à inspecter ces contenus; ces deux
  images supplémentaires ont levé l’ambiguïté. L’outil d’échantillonnage
  privilégie désormais le plus long maintien pour un même contenu.
- Les planches et les images natives examinées ne révèlent pas d’autre
  défaut mathématique ou de lisibilité corroboré. Cela n’atteste pas tous
  les états de chaque animation ni une synchronisation audio réelle.

Aucun appel Azure, aucune livraison et aucune approbation institutionnelle.
