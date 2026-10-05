# Les maths ouvrent des portes — capsule UQAM de 29 secondes

Troisième vidéo de la [collection UQAM](../README.md), parallèle à la présentation longue et à la promotion générale du bac en mathématiques. Ce projet conserve son renderer, son profil vocal et son historique.

**Révision active du 3 octobre 2026 :** le scénario présente le parcours majeure + certificat ou mineure compatible vers un baccalauréat en sciences par cumul. La cible du storyboard muet est **29 secondes**, avec une durée narrée admise de **28 à 30 secondes**, conclusion et logo compris. Le texte ci-dessous est la proposition exacte de l’utilisateur; sa copie écran et les six photographies des deux capsules ont été approuvées avant la nouvelle synthèse Azure.

**Révision visuelle du 5 octobre 2026 :** à la demande de l’utilisateur, l’ouverture montre maintenant une conversation souriante devant le Complexe des sciences; le deuxième plan montre un échange naturel lors d’Avant-première. Ces sélections remplacent les photos NorthSec et Métamorphose. Les trois photos sont présentées dans un panneau lumineux, avec le texte à gauche et les crédits hors de l’image. La narration approuvée du 3 octobre reste identique.

## Narration et sous-titres

> À l’UQAM, combinez les maths avec vos autres intérêts. Commencez par une majeure en mathématiques ou en statistique, généralement en deux ans à temps plein. Complétez-la par un certificat ou une mineure compatible, en communication, finance, économie ou informatique. Ce parcours peut mener à un baccalauréat en sciences par cumul. Une formation à votre image, pour construire votre avenir.

[project.json](project.json) est la source de vérité de la narration, des sous-titres, de la copie écran, des photographies et du storyboard. Les sous-titres reprennent exactement la narration, avec deux lignes au maximum; les retours à la ligne ne modifient pas le texte. La narration porte les précisions, ce qui permet de raccourcir la copie écran.

## Storyboard actif

| Temps de l’aperçu muet | Idée | Copie écran |
|---|---|---|
| 0–4 s | Associer ses intérêts | Les maths / et vos intérêts |
| 4–11 s | Commencer par une majeure | Une majeure / Maths ou statistique / En général, 2 ans à temps plein |
| 11–18,5 s | Choisir un complément compatible | Un complément compatible / Communication · Finance / Économie · Informatique |
| 18,5–22,5 s | Comprendre le diplôme visé | Baccalauréat en sciences / par cumul |
| 22,5–27,5 s | Construire son parcours et consulter le programme | Une formation / à votre image / math.uqam.ca |
| 27,5–29 s | Signature institutionnelle | Logo officiel UQAM sur fond blanc |

Ces bornes sont celles du **storyboard muet**, pas des mesures de la nouvelle voix. En mode Azure, les durées réelles de chaque phrase sont mesurées avant le rendu; `allocate_slots()` conserve la voix sans accélération et réserve au moins deux secondes après la dernière phrase. Si l’ensemble dépasse 30 secondes, le build échoue et le texte doit être révisé avec l’utilisateur.

## Mise en page et transitions

Les photographies restent fixes. Le plan de la majeure sépare la photo du texte; le parcours et le diplôme utilisent deux cartes typographiques sur fond blanc. Leur changement se fait par une coupe directe de la copie : aucun fondu blanc entre les deux idées, aucune superposition des deux messages. Pour les changements de photos, le nouveau fond couvre l’ancien avant son retrait; les messages s’échangent séparément.

Le site `math.uqam.ca` est visible dans le dernier plan avant le logo. `show_photo_credits: false` retire les crédits de l’image; leurs textes complets restent dans les sources et le manifeste du rendu. L’aperçu muet porte toujours la mention « APERÇU MUET — VOIX NON INCLUSE » au premier plan.

## Photographies et provenance

Les fichiers actifs sont déclarés dans `project.json`, avec SHA-256, dimensions décodées, source, crédit et placement. Leur inventaire partagé se trouve dans [assets/uqam_promo/sources.json](../../assets/uqam_promo/sources.json); la [politique photographique](../../assets/uqam_promo/PHOTO_POLICY.md) donne la priorité à la Banque de photos de la Salle de presse UQAM.

Photographies actives après la révision demandée le 5 octobre; aucune n’est utilisée dans la capsule maths active :

| Plan | Fichier | Contexte et crédit |
|---|---|---|
| Ouverture | `vie_etudiante_sciences_uqam.jpg` | Conversation sur la pelouse du Complexe des sciences, provenant de la page officielle Vie étudiante. Crédit institutionnel : Faculté des sciences · UQAM; photographe individuel non indiqué. Ce n’est pas une séance de travail mathématique. |
| Majeure, panneau photo | `avant_premiere_2026.jpg` | Échange de personnes nouvellement admises et de leurs proches avec des représentants universitaires lors d’Avant-première, 25 avril 2026, Centre de design. Photo : Clémence Lesné. Ce n’est pas un cours de maths ni un groupe suivant le parcours par cumul. |
| Conclusion | `bouturage_2026.jpg` | Activité de bouturage de la rentrée hivernale 2026; photo Nathalie St-Pierre. Ambiance de vie universitaire, sans la qualifier de cours de biologie. |

La sélection éditoriale de l’utilisateur est enregistrée séparément des droits de republication et de l’approbation institutionnelle de diffusion. Ne pas remettre `classroom_math.jpg` ou `research_math.jpg` dans cette capsule; ces images ont été rejetées pour ce récit. Une photo de faible résolution est limitée au panneau, jamais agrandie en plein écran 1080p. Aucun statut de programme n’est attribué aux personnes photographiées.

## Portée des affirmations

La [fiche de traçabilité](sources/accueil_septembre_2026.md) relie les affirmations aux pages 7 et 21–23 du document d’accueil et aux ressources officielles déjà consignées. « Généralement en deux ans à temps plein » décrit une durée type de la majeure. Le complément doit être compatible; « peut mener » ne garantit ni une combinaison donnée ni une admission automatique. Les quatre domaines sont des exemples, pas une liste d’intitulés administratifs. La majeure seule n’est pas présentée comme un baccalauréat.

## Voix, musique et construction

Le profil promotionnel reste **MAI-Voice-2, débit +2 %**, via `tools/tts.py`, `VoiceoverScene` et `AzureService`. Le cache vocal persistant est `media/voiceovers`; les cinq phrases gardent exactement le même SSML. Ne pas substituer une voix ou accélérer un enregistrement pour satisfaire la durée.

Le builder produit un master voix seule. La musique est ajoutée à une variante séparée par `scripts/mix_uqam_music_review.py`; ce mix conserve ses propres mesures, sources et crédits. La présence d’une musique seule ne prouve jamais qu’un rendu contient une narration Azure.

```bash
# Aperçu muet pour revue de la copie et des plans.
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode silent --quality ql

# Après revue de la copie; SPEECH_KEY et SPEECH_REGION dans l’environnement.
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode azure --quality qh

.venv-ouvertures/bin/python -m pytest tests/test_uqam_ouvertures.py -q
```

Le build écrit un dossier neuf sous `dist/bac_sciences_ouvertures_fr/` : MP4 propre, variante sous-titrée, SRT, timeline, manifeste, contrôles de flux et images de revue. En mode Azure, un WAV de narration est également conservé. Les médias générés restent hors Git. Le builder ne publie ni sur Drive ni sur une plateforme.

## Contrôles et livraison

Les contrats vérifient le parcours complet, le total du storyboard de 29 secondes, la limite narrée de 30 secondes, la réserve finale, les sous-titres exacts, les références de sources, l’intégrité et les dimensions réelles des photos, puis les flux et le minutage de l’export. La scène contrôle les bornes et collisions du texte rendu.

Un test de code, un aperçu muet, un rendu Azure, une inspection d’images, une écoute complète et une autorisation institutionnelle sont des preuves différentes. Le manifeste conserve `release_ready: false`; la nouvelle narration, son écoute et l’autorisation de diffusion ne sont pas déduites d’un aperçu de copie.

## Historique séparé

- **17 septembre 2026 :** première capsule courte issue du document d’accueil; les petites images extraites de sa couverture ont ensuite été retirées.
- **18–20 septembre 2026 :** version de 20 secondes centrée sur la majeure et les domaines d’ouverture. Elle omettait volontairement le certificat et le B.Sc. Cette décision est historique et ne décrit plus le scénario actif.
- **1er octobre 2026 :** version de 29 secondes réintroduisant le certificat ou la mineure compatible et le B.Sc. par cumul; fin avec logo officiel.
- **3 octobre 2026 :** narration proposée par l’utilisateur, copie écran raccourcie, CTA rétabli et suppression du blanc entre les deux cartes du parcours. La copie écran et les photographies ont été approuvées par l’utilisateur; la nouvelle voix conserve sa revue séparée.
- **5 octobre 2026 :** remplacement des deux premières photos, trois panneaux lumineux avec texte séparé, fin plus concise et crédits retirés de l’image. Les dossiers Drive 01, 02 et 03 conservent uniquement leurs vidéos; les sources, crédits et preuves restent dans le projet local.

Les rendus et rapports datés antérieurs restent des traces de leurs propres versions.
