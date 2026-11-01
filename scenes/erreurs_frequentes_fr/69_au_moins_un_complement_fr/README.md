# 69 — Au moins un ne signifie pas exactement un

**Objectif :** compter chaque chaîne une seule fois; distinguer « au moins un »
et « exactement un », puis utiliser un complément ou des cas disjoints.
Prérequis : principe du produit et dénombrement des chaînes avec répétition.

L'exemple de transfert compte les codes de trois chiffres de 0 à 9, avec
répétitions et zéro initial autorisés. Le comptage erroné `3 × 10²` marque un
zéro : 070 est compté deux fois, 000 trois fois. La multiplicité variable
empêche une simple division par un facteur commun. Le complément donne
`10³ − 9³ = 271`, contre `3 × 9² = 243` pour exactement un zéro.
La partition 729 + 243 + 27 + 1 vérifie les deux résultats.

**Autocontrôle :** chaînes binaires de longueur 8 : au moins un 1 donne
`2⁸ − 1 = 255`; exactement un 1 donne 8. La question précède une pause de
six secondes et une page de correction distincte. Elle reprend le cahier 7.6A
et ajoute la comparaison « exactement un ».

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch07.tex`, sections 7.6 et 7.9
  (`manual:section:07.06`, `manual:section:07.09`), comptage par complément.
- `books/mat0339/sources/workbook/chapters/ch07.tex`, exercice 7.6A.
- Édition intégrée à `main` : `4d451c37d483d763e33683a7fb683d1e0fdde62d`.
  Révision éditoriale consultée séparément : `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`.

La capsule 20 présente déjà l'union de deux événements. Celle-ci ajoute le
piège de la position marquée et la multiplicité variable, avec un complément
sur les chaînes : elle ne répète pas simplement la formule d'une union.

**Classe :** `AuMoinsUnComplementFR`. Une ouverture UQAM, narration française
et sous-titres via `TeachingScene`. `MANIM_DISABLE_VOICEOVER=1` produit une
prévisualisation silencieuse; cette prévisualisation ne certifie ni la durée
parlée, ni l'écoute, ni l'autorisation de publication. Médias générés hors Git.
