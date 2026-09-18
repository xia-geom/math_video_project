# Les maths ouvrent des portes — capsule UQAM d’environ 20 secondes

Troisième vidéo de la [collection UQAM](../README.md), parallèle aux films existants de présentation longue et de promotion générale.

## Direction éditoriale — révision du 18 septembre 2026

La capsule ne décrit plus le mécanisme complet du baccalauréat par cumul. Elle se concentre sur un message plus simple :

> **Après deux ans à temps plein en mathématiques ou en statistique, on peut obtenir une majeure et ouvrir son parcours vers d’autres domaines.**

Le mot **certificat** n’est plus prononcé ni affiché. La capsule ne prétend donc plus expliquer comment se complète le B.Sc. par cumul. Cette distinction est documentée dans [la fiche de traçabilité](sources/accueil_septembre_2026.md).

## Narration française

> Les maths ouvrent des portes. Après deux ans à temps plein en mathématiques ou en statistique, on peut obtenir une majeure. Et ouvrir son parcours vers la communication, la finance, l’économie ou l’informatique. Plusieurs horizons. À l’UQAM.

Le texte narré, les sous-titres, le texte écran, les choix de photographies et le minutage ont une source de vérité commune : [project.json](project.json).

## Storyboard révisé

| Temps cible | Photo de fond | Texte à l’écran |
|---|---|---|
| 0–3 s | Pavillon Président-Kennedy | **Les maths ouvrent des portes.** |
| 3–10 s | Activité mathématique à l’UQAM | **Après 2 ans à temps plein** / une majeure en maths ou statistique |
| 10–16 s | Pôle mathématique du Complexe des sciences | Ouvrir son parcours vers / **Communication · Finance** / **Économie · Informatique** |
| 16–20 s | Vie étudiante à l’UQAM | **Plusieurs horizons.** / À l’UQAM. / math.uqam.ca |

Chaque plan utilise désormais une photographie différente.

## Photographies

Les deux petits crops extraits de la page 1 du diaporama ont été retirés de la composition. Ils ne faisaient que 384 × 216 et 256 × 144 pixels et devenaient visiblement flous une fois agrandis à 1920 × 1080.

La capsule réutilise quatre photographies UQAM déjà archivées dans le dépôt avec source, crédit, dimensions et empreinte SHA-256 :

| Fichier partagé | Dimensions | Crédit | Usage dans la capsule |
|---|---:|---|---|
| `assets/uqam_promo/president_kennedy.jpg` | 2560 × 1706 | Photo UQAM | ouverture institutionnelle |
| `assets/uqam_promo/classroom_math.jpg` | 1600 × 1067 | Mireille Soboya | activité mathématique |
| `assets/uqam_promo/research_math.jpg` | 2000 × 1333 | Nathalie St-Pierre | ouverture du parcours |
| `assets/uqam_promo/support_students.jpg` | 2000 × 1333 | Nathalie St-Pierre | conclusion / vie étudiante |

Le manifeste partagé [assets/uqam_promo/sources.json](../../assets/uqam_promo/sources.json) conserve les pages sources et le statut de droits connu. La photo du pavillon Président-Kennedy provient de la Banque de photos de la Salle de presse UQAM, qui la propose en téléchargement haute résolution avec la mention obligatoire « Photo UQAM ». Pour les photographies provenant d’Actualités UQAM, les crédits sont connus et affichés dans la capsule; la permission formelle de republication n’est pas déduite automatiquement.

Le contrat du projet refuse maintenant toute photographie déclarée sous 1600 pixels de largeur ou 900 pixels de hauteur et refuse aussi la répétition d’une même photo entre les quatre plans.

## Message académique

La page 21 du document fourni soutient la distinction entre majeure en mathématiques et majeure en statistique. La formulation « deux ans à temps plein » reste le cadrage demandé dans le brief et n’est pas présentée comme une garantie universelle de durée.

La page 23 montre les domaines communication, économique, finance et informatique associés au parcours. Puisque la capsule ne nomme plus les certificats, l’écran emploie le nom disciplinaire naturel **économie** plutôt que l’étiquette « économique » du schéma.

La page 22 montre bien un certificat dans le mécanisme du baccalauréat par cumul. Ce point reste documenté dans la fiche de source, mais il est volontairement **omis du film**. En conséquence, la nouvelle narration ne dit plus « Un bac en sciences » : elle évite de présenter un mécanisme incomplet comme s’il suffisait à décrire tout le diplôme.

## Style visuel

La règle reste :

> **une photographie UQAM + une idée courte à la fois.**

Il n’y a pas de grille de cartes, de boîtes administratives ou de texte permanent. Les crédits photo apparaissent discrètement dans le coin supérieur droit. Un voile sombre local au plan protège la lisibilité sans masquer complètement les photographies.

Les transitions passent maintenant directement d’une photographie à la suivante par un fondu croisé court, plutôt que par une extinction puis une réapparition séparées.

## Technique

La capsule conserve le workflow existant : Manim Community, `VoiceoverScene`, Azure `AzureService` et les fonctions communes de `tools/tts.py`. Le profil promotionnel reste `MAI-Voice-2`, débit `+2%`.

Il n’y a pas de musique dans cette version. Le MP4 propre reste la référence éditoriale; le SRT est conservé séparément et une variante sous-titrée sert à la revue.

## Construire

Aperçu muet 1080p :

```bash
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode silent --quality qh
```

Rendu narré de contrôle :

```bash
# SPEECH_KEY et SPEECH_REGION doivent être disponibles dans l’environnement.
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode azure --quality qh
```

## Contrôles

`project.py` refuse notamment :

- un storyboard qui ne totalise pas 20 secondes;
- la répétition d’une photographie entre deux plans;
- une photographie non enregistrée, altérée ou inférieure au seuil 1600 × 900;
- plus de trois lignes de message à l’écran;
- la présence du mot « certificat » dans la narration révisée;
- une narration qui prétend expliquer le baccalauréat complet alors que son mécanisme a été volontairement omis;
- des sous-titres qui ne correspondent pas à la narration;
- des références de pages non enregistrées.

Le builder inclut maintenant les quatre photographies partagées et leur manifeste de sources dans les empreintes de fraîcheur du rendu.

## État de livraison

Un aperçu muet réussi ne vaut pas validation de la voix Azure ni autorisation institutionnelle. `release_ready` reste faux tant que le rendu narré, l’écoute complète, la revue visuelle et la validation éditoriale ne sont pas effectués.
