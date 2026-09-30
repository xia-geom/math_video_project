# Les maths ouvrent des portes — capsule UQAM de 20 secondes

Troisième vidéo de la [collection UQAM](../README.md), indépendante des deux autres films. Le scénario, les sous-titres, le minutage et les sources photographiques sont définis dans [project.json](project.json).

## Message conservé

La révision visuelle du 30 septembre 2026 conserve exactement la narration révisée du 18 septembre :

> Les maths ouvrent des portes. Après deux ans à temps plein en mathématiques ou en statistique, on peut obtenir une majeure. Puis, le parcours s’ouvre vers la communication, la finance, l’économie ou l’informatique. Plusieurs horizons, à l’UQAM.

Le mot **certificat** n’est ni prononcé ni affiché. La capsule ne prétend donc pas expliquer le mécanisme complet du baccalauréat par cumul. La formule « deux ans à temps plein » reste le cadrage du brief, pas une garantie universelle. Les pages 21 et 23 du document fourni soutiennent les messages; la page 22 reste une référence de contexte et la page 7 fournit l’adresse du département. Voir [la fiche de traçabilité](sources/accueil_septembre_2026.md).

## Six photographies, quatre messages

| Temps | Photographie | Texte à l’écran |
|---|---|---|
| 0–3 s | Pavillon des Sciences biologiques | Les maths ouvrent des portes. |
| 3–6,5 s | Activité mathématique à l’UQAM | Après 2 ans à temps plein / une majeure en maths ou statistique |
| 6,5–10 s | Pôle mathématique | Même texte, sans nouvelle animation du message. |
| 10–13 s | Rencontre à la Salle des marchés de l’ESG UQAM | Un parcours ouvert vers / Communication · Finance / Économie · Informatique |
| 13–16 s | Studio Indie Asylum | Même texte, maintenu. |
| 16–20 s | Accueil de la communauté étudiante | Plusieurs horizons. / À l’UQAM. / math.uqam.ca |

Les fondus photographiques durent **0,9 seconde**. La photographie sortante reste opaque sous la suivante : aucun passage par le noir et aucun double voile. Les textes sortant et entrant ne se superposent jamais. Le zoom est limité à **2,4 %**, le recadrage est borné et les **1,25 dernières secondes restent fixes**. La mention d’aperçu muet est placée au-dessus des photographies, et non derrière.

La composition garde une photographie plein écran et une idée courte à la fois, sans grille de cartes ni boîtes administratives. Les messages des séquences centrales sont abaissés pour mieux dégager les visages. Les crédits restent visibles en haut à droite, séparés de la mention d’aperçu muet et de la zone des sous-titres.

## Photographies et droits

Les quatre sources déjà archivées sont conservées :

| Fichier partagé | Dimensions natives | Crédit |
|---|---:|---|
| `sciences_biologiques_uqam.jpg` | 2560 × 1706 | Photo : UQAM |
| `classroom_math.jpg` | 1600 × 1067 | Mireille Soboya |
| `research_math.jpg` | 2000 × 1333 | Nathalie St-Pierre |
| `support_students.jpg` | 2000 × 1333 | Nathalie St-Pierre |

Le manifeste partagé [sources.json](../../assets/uqam_promo/sources.json) documente ces fichiers. La photo du pavillon provient de la [banque officielle UQAM](https://salledepresse.uqam.ca/banque-de-photos/photos-de-pavillons/). Les petits crops historiques des diapositives ne sont pas réintroduits.

Deux nouvelles sources ont été téléchargées, décodées et inspectées à **2000 × 1333** chacune :

- [Salle des marchés, 2022](https://actualites.uqam.ca/2022/reseautage-a-la-salle-des-marches-esg-uqam/), photo : Nathalie St-Pierre. Il s’agit d’une rencontre, pas d’un cours garanti aux étudiants en mathématiques.
- [Visite du studio Indie Asylum, 2024](https://actualites.uqam.ca/2024/visite-studio-jeux-video-indie-asylum/), photo : Nathalie St-Pierre. Le studio est hors campus; il n’est pas présenté comme un laboratoire de l’UQAM. Son nom apparaît dans le crédit.

La photo récente de la [Bibliothèque des sciences](https://bibliotheques.uqam.ca/nouvelles/top-6-des-meilleurs-endroits-pour-etudier-aux-bibliotheques/) a été écartée : **1024 × 538**, trop petite pour le traitement plein écran demandé. Aucun agrandissement artificiel n’est présenté comme une source haute résolution.

`project.json` conserve les URL exactes, les dimensions décodées, les empreintes SHA-256, les crédits et le contexte des deux ajouts. Leur permission formelle de réutilisation promotionnelle reste à confirmer. La présence d’une photo sur un site de l’UQAM n’est pas assimilée à une autorisation de diffusion de ce film. Aucun fichier vidéo ni aucune nouvelle photographie téléchargée n’est ajouté à l’historique Git.

## Préparer et construire

Depuis la racine du dépôt, avec l’environnement décrit dans `requirements.txt` :

```bash
PYTHONPATH=. python miscellaneous/bac_sciences_ouvertures_fr/review_photos.py --output review_artifacts/uqam_ouvertures/photo_research
python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode silent --quality qh
```

La première commande prépare les photographies manquantes et vérifie leurs empreintes; les deux nouvelles photos sont placées dans `media/bac_sciences_ouvertures_fr/photos/`. Le rendu lui-même n’accède pas au réseau. Les sources présentes mais altérées ne sont pas remplacées silencieusement.

Pour une revue narrée explicitement demandée, une fois les identifiants Azure disponibles :

```bash
python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode azure --quality qh
```

Manim Community, `VoiceoverScene`, `AzureService` et les fonctions communes de `tools/tts.py` restent utilisés. Le profil est toujours `MAI-Voice-2`, débit `+2%`. Il n’y a pas de musique. Aucun nouvel essai Azure n’est inclus dans cette révision visuelle. Le MP4 propre est la référence de composition; le SRT et le MP4 sous-titré restent des sorties séparées.

## Contrôles et fichiers

`visual_timing.py` définit le fondu avec fond opaque, les changements de texte sans chevauchement et les inserts photographiques à l’intérieur des quatre plages de narration. `project.py` contrôle la durée totale, la non-répétition des photos, les dimensions réelles, les empreintes, les recadrages, le mouvement limité, la brièveté du texte et la correspondance exacte des sous-titres.

Le builder enregistre le minutage mesuré, les rectangles de texte, les six photographies utilisées, les versions et les empreintes des sources. Les tests vérifient aussi que le fondu ne révèle jamais le fond noir et que deux messages ne se superposent jamais.

Un aperçu muet réussi ne vaut ni écoute de la voix Azure ni autorisation institutionnelle. `release_ready` reste faux tant que la revue éditoriale, les permissions et, pour une version narrée, l’écoute complète ne sont pas validées. Les autres films, le programme des cours et les livres restent hors du périmètre de cette modification.
