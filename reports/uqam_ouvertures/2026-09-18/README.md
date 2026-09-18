# UQAM — ouvertures interdisciplinaires : révision texte + photographies

**Date :** 18 septembre 2026  
**Branche :** `feat/uqam-ouvertures-copy-photos-20260918`

## Demande

La révision répond à trois points :

1. polir le message français;
2. ne plus parler de certificat;
3. remplacer les deux petits crops du diaporama par des photographies UQAM de meilleure qualité et éviter la répétition visuelle.

## Texte — avant / après

### Avant

> Les maths ouvrent des portes. Deux ans à temps plein en maths ou en statistique : une majeure. Puis un certificat : communication, finance, économique ou informatique. Un bac en sciences. Plusieurs horizons. À l’UQAM.

### Après

> Les maths ouvrent des portes. Après deux ans à temps plein en mathématiques ou en statistique, on peut obtenir une majeure. Puis, le parcours s’ouvre vers la communication, la finance, l’économie ou l’informatique. Plusieurs horizons, à l’UQAM.

### Décisions éditoriales

- `certificat` est supprimé de la narration et de l’écran;
- `Un bac en sciences` est également retiré, car la source montre un certificat dans le mécanisme du baccalauréat par cumul : si ce mécanisme n’est plus expliqué, le film ne doit pas laisser croire que la majeure seule décrit le diplôme complet;
- `économique` devient `économie` parce que le film parle maintenant d’un domaine d’ouverture, et non du libellé exact d’un certificat;
- `Deux ans à temps plein...` devient `Après deux ans à temps plein...` pour rendre la phrase plus naturelle;
- `on peut obtenir une majeure` remplace la formulation télégraphique `une majeure`.

## Nouveau storyboard

| Temps | Visuel | Message |
|---|---|---|
| 0–3 s | Pavillon Président-Kennedy | Les maths ouvrent des portes. |
| 3–10 s | Activité mathématique | Après 2 ans à temps plein / une majeure en maths ou statistique |
| 10–16 s | Pôle mathématique | Un parcours ouvert vers / Communication · Finance / Économie · Informatique |
| 16–20 s | Vie étudiante UQAM | Plusieurs horizons. / À l’UQAM. / math.uqam.ca |

Il n’y a plus aucune répétition d’image entre les quatre plans.

## Photographies remplacées

### Anciennes images

| Fichier | Dimensions |
|---|---:|
| `slide_01_students_math.jpg` | 384 × 216 |
| `slide_01_uqam_building.jpg` | 256 × 144 |

Ces images étaient agrandies jusqu’à 1920 × 1080. Le pavillon subissait donc un agrandissement d’environ 7,5 fois sur chaque dimension.

### Nouvelles images

| Fichier | Dimensions | Source | Crédit |
|---|---:|---|---|
| `assets/uqam_promo/president_kennedy.jpg` | 2560 × 1706 | Banque de photos, Salle de presse UQAM | Photo UQAM |
| `assets/uqam_promo/classroom_math.jpg` | 1600 × 1067 | Actualités UQAM — compétition de mathématiques | Mireille Soboya |
| `assets/uqam_promo/research_math.jpg` | 2000 × 1333 | Actualités UQAM — pôle mathématique | Nathalie St-Pierre |
| `assets/uqam_promo/support_students.jpg` | 2000 × 1333 | Actualités UQAM — accueil étudiant | Nathalie St-Pierre |

Ces quatre fichiers existaient déjà dans le dépôt principal et étaient déjà accompagnés d’un manifeste de source et d’empreintes SHA-256. La révision les réutilise plutôt que d’ajouter des copies binaires supplémentaires.

### Source institutionnelle vérifiée

La Banque de photos de la Salle de presse UQAM propose explicitement la photo du pavillon Président-Kennedy en **haute résolution** et demande la mention « Photo UQAM » :

- https://salledepresse.uqam.ca/banque-de-photos/photos-de-pavillons/
- https://salledepresse.uqam.ca/wp-content/uploads/sites/16/2022/01/PK_hr-scaled.jpg

Le Service des communications indique également que sa banque de photos centralise des images haute résolution d’étudiantes et étudiants, diplômés, professeurs, événements, pavillons, salles de cours et laboratoires :

- https://servicecom.uqam.ca/information-pratique/banque-de-photos-uqam.html

Pour les images d’Actualités UQAM, les crédits de photographe sont enregistrés; l’autorisation formelle de republication n’est pas inférée automatiquement.

## Contrats techniques ajoutés

La révision change `project.json` au schéma 3 et ajoute les contrôles suivants :

- quatre photos UQAM exactes sont attendues;
- chaque plan doit utiliser une photo différente;
- une photo déclarée sous 1600 × 900 est refusée;
- les empreintes SHA-256 des images sont vérifiées avant rendu;
- les crédits et URLs de source sont obligatoires;
- le mot `certificat` est interdit dans la narration de cette version;
- le film ne peut pas réintroduire `bac en sciences` ou `baccalauréat` sans rétablir et expliquer le mécanisme omis;
- le builder inclut maintenant les quatre photos partagées et `assets/uqam_promo/sources.json` dans ses empreintes de fraîcheur.

## Composition

- quatre visuels distincts;
- crédits photo discrets en haut à droite;
- au plus trois lignes de message par plan;
- fondus croisés courts entre les photos;
- aucun retour à la grille de cartes de la première version;
- master propre et SRT séparé comme auparavant.

## Fichiers modifiés

- `miscellaneous/bac_sciences_ouvertures_fr/project.json`
- `miscellaneous/bac_sciences_ouvertures_fr/project.py`
- `miscellaneous/bac_sciences_ouvertures_fr/bac_sciences_ouvertures_fr_scene.py`
- `miscellaneous/bac_sciences_ouvertures_fr/build.py`
- `miscellaneous/bac_sciences_ouvertures_fr/README.md`
- `miscellaneous/bac_sciences_ouvertures_fr/sources/accueil_septembre_2026.md`
- `tests/test_uqam_ouvertures.py`
- ce rapport

## Validation

La branche doit passer le workflow dédié `UQAM — ouvertures 20 s`, qui compile, lint, exécute les tests, produit un nouvel aperçu muet 1080p et, si les secrets Azure sont disponibles dans le contexte autorisé, produit aussi une version narrée de revue.

La validation visuelle et l’écoute complète restent distinctes de la réussite technique du workflow.
