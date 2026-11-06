# 70 — Espérance : gain net et résultat incertain

**Objectif :** définir la variable aléatoire, inclure le coût de chaque partie
et interpréter l'espérance sans en faire une garantie.
Prérequis : probabilités d'issues disjointes et moyenne pondérée.

Le jeu du cahier 8.6B coûte 4 $ et verse 20 $ avec probabilité 0,1, rien sinon.
Les gains nets sont 16 $ et −4 $, donc l'espérance vaut −2 $, et non 2 $.
Un second calcul vérifie `E(versement) − 4 = 2 − 4 = −2`.
Les deux probabilités totalisent 1; la participation est payée dans tous les cas.

La valeur −2 $ ne peut pas être le gain net d'une partie. Dix parties ne
fixent pas non plus le résultat : pour K versements, le gain total est
`20K − 40`. Son espérance −20 $ n'impose pas K = 1. L'interprétation à long
terme est explicitement rattachée à des répétitions indépendantes avec les
mêmes règles; aucune durée réelle de narration n'est inférée d'une attente.

**Autocontrôle original :** un dé équilibré, participation de 1 $, versement
de 6 $ sur un six et 0 $ sinon. Après six secondes de réflexion, la correction
donne les gains possibles 5 $ et −1 $, l'espérance nulle, et précise que ce
jeu est équitable au sens de l'espérance sans garantir un gain nul.

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch08.tex`, sections 8.6 et 8.9
  (`manual:section:08.06`, `manual:section:08.09`), espérance et interprétation.
- `books/mat0339/sources/workbook/chapters/ch08.tex`, exercices 8.6A–C,
  avec l'exemple principal repris de 8.6B; autocontrôle original de transfert.
- Édition intégrée à `main` : `4d451c37d483d763e33683a7fb683d1e0fdde62d`.
  Révision éditoriale consultée séparément : `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`.

**Classe :** `EsperanceGainNetFR`. Une ouverture UQAM, narration française
et sous-titres via `TeachingScene`. `MANIM_DISABLE_VOICEOVER=1` produit une
prévisualisation silencieuse. L'écoute et la publication restent des étapes
distinctes; médias générés hors Git.
