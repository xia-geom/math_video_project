# Les maths ouvrent des portes — capsule UQAM d’environ 20 secondes

Troisième vidéo de la [collection UQAM](../README.md), parallèle aux films existants de présentation longue et de promotion générale.

## Direction révisée après audit

La première version était techniquement propre mais trop chargée pour une capsule de 20 secondes : plusieurs cartes, titres, sous-titres et qualificatifs entraient en concurrence avec le message. La révision adopte une règle simple :

> **une photographie UQAM + une idée courte à la fois.**

Il n’y a plus de grille de cartes, de boîtes de certificats ni de texte administratif permanent. L’identité UQAM vient directement de **deux photographies de la page 1 du diaporama fourni** : le groupe devant le tableau de mathématiques et le pavillon Président-Kennedy éclairé la nuit. Les deux crops sont versionnés dans le projet et contrôlés par SHA-256.

La page 1 sert à l’identité visuelle; les pages 21–23 servent au contenu du parcours. Voir [la fiche de traçabilité](sources/accueil_septembre_2026.md).

## Message

Une formation en mathématiques ou en statistique peut constituer une base scientifique avant une ouverture vers une autre discipline. Le parcours montré reste : **majeure en mathématiques/statistique, certificat complémentaire, puis B.Sc. Sciences**.

« Deux ans » décrit le parcours type à temps plein demandé dans le brief; ce n’est pas présenté comme la durée totale garantie du baccalauréat.

## Narration française

> Les maths ouvrent des portes. Deux ans à temps plein en maths ou en statistique : une majeure. Puis un certificat : communication, finance, économique ou informatique. Un bac en sciences. Plusieurs horizons. À l’UQAM.

Le texte narré, les sous-titres, le texte écran, le choix de photo et le minutage ont une source de vérité commune : [project.json](project.json).

## Storyboard minimal

| Temps cible | Photo de fond | Texte à l’écran |
|---|---|---|
| 0–4 s | Pavillon UQAM, page 1 | **Les maths ouvrent des portes.** |
| 4–9 s | Groupe au tableau, page 1 | **2 ans en maths ou statistique** / à temps plein → une majeure |
| 9–16 s | Même photo étudiante, sans nouvelle carte | Puis, un certificat / **Communication · Finance** / **Économique · Informatique** |
| 16–20 s | Pavillon UQAM, page 1 | **Un bac en sciences.** / **Plusieurs horizons.** / math.uqam.ca |

La répétition contrôlée de deux photos est intentionnelle : elle évite le diaporama de quatre ou cinq images et ancre immédiatement la capsule à l’UQAM.

## Images

Les seuls fichiers image propres à cette capsule sont :

```text
assets/
├── slide_01_students_math.jpg
└── slide_01_uqam_building.jpg
```

Ce sont des crops 16:9 de photographies contenues dans la couverture du PDF fourni. Ils ne sont pas remplacés par des banques d’images ou par les photos d’autres productions UQAM du dépôt.

Les photos sont assombries par un voile dans Manim afin de laisser deux ou trois lignes de texte lisibles. Aucun logo officiel supplémentaire n’est superposé; l’inscription UQAM visible sur le pavillon fait partie de la photographie source.

Le **MP4 propre** est le rendu éditorial de référence pour cette direction minimaliste. Le fichier SRT reste disponible pour l’accessibilité et les plateformes qui gèrent les sous-titres séparément. Le MP4 avec sous-titres incrustés est conservé comme variante de contrôle, mais il répète forcément une partie du texte déjà affiché à l’écran et n’est donc pas la version visuelle recommandée.

## Technique

La capsule conserve le workflow existant : Manim Community, `VoiceoverScene`, Azure `AzureService` et les fonctions communes de `tools/tts.py`. Le profil promotionnel reste `MAI-Voice-2`, débit `+2%`. Aucun changement n’est appliqué aux voix des leçons ou aux deux autres films.

Il n’y a pas de musique dans cette version. Les sous-titres de revue sont générés depuis la chronologie réelle et utilisent un fond sombre semi-transparent adapté aux photographies.

## Installer dans un environnement isolé

Depuis la racine du dépôt, après installation de Cairo/Pango et FFmpeg :

```bash
python3 -m venv .venv-ouvertures
.venv-ouvertures/bin/python -m pip install -r miscellaneous/bac_sciences_ouvertures_fr/requirements.txt
```

## Construire

Aperçu muet, explicitement marqué comme tel :

```bash
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode silent --quality qh
```

Rendu narré de contrôle :

```bash
# SPEECH_KEY et SPEECH_REGION doivent être disponibles dans l’environnement.
# Le profil MAI du dépôt utilise SPEECH_REGION=canadacentral.
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode azure --quality qh
```

Les anciens noms d’environnement Azure restent pris en charge par `tools/tts.py`. Aucun secret ne doit être écrit dans Git, `project.json` ou un rapport.

## Contrôles

`project.py` refuse :
- un storyboard qui ne totalise pas 20 secondes;
- un beat utilisant autre chose que l’une des deux photos enregistrées;
- plus de trois lignes de texte écran;
- une photo absente ou dont le SHA-256 diffère;
- des sous-titres qui ne correspondent pas à la narration;
- des références de pages non enregistrées.

Le builder ajoute les photographies aux empreintes de sources, refuse les rendus périmés et produit un MP4 propre, un MP4 sous-titré, un SRT, la chronologie réelle, des images de contrôle, `ffprobe.json`, le journal et un manifeste.

## État de livraison

Un aperçu muet réussi ne vaut pas validation de la voix Azure ni autorisation institutionnelle. `release_ready` reste faux tant que le rendu narré, l’écoute complète et la validation éditoriale ne sont pas effectués.
