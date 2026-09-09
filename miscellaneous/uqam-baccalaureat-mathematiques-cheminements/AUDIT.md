# Audit éditorial, visuel et technique

## Statut des versions

Les sections historiques ci-dessous auditent le rendu de cartes **V2**
(`render_video.py`). La section « V3 — aperçu narratif de 3:35 » audite la
nouvelle chaîne, qui possède ses propres sources, horloges et répertoires. La
présence de la chaîne V3 dans le package ne constitue pas, à elle seule, une
preuve qu’un master V3 final a été rendu et approuvé.

## Source et portée

Source locale vérifiée :

`assets/sources/uqam-guide-personne-etudiante-mathematiques-statistique-2025-2026.pdf`

- titre : *Guide de la personne étudiante 2025–2026 (mathématiques et
  statistique)*;
- date de production du PDF : 23 octobre 2025;
- 34 pages;
- SHA-256 :
  `af4f30d925a5f481af3931e9b85741d0a563abb8f83944f9ae148e9c162a5be9`.

Le millésime `2025–2026` est défini une seule fois dans
`project-manifest.toml`. Les quatre cartes reconstruites représentent :

> Cheminement recommandé — début à l’automne — 5 cours/session — 2025–2026

Pages sources des cartes retenues :

| Carte | Page du guide |
| --- | ---: |
| concentration mathématiques fondamentales | 9 |
| concentration statistique | 13 |
| concentration informatique — profil Mathématiques | 18 |
| concentration informatique — profil Statistique | 22 |

Le guide offre d’autres combinaisons qu’il ne faut pas confondre avec ces
cartes :

| Concentration | Automne, 5 cours | Automne, 4 cours | Hiver, 5 cours | Hiver, 4 cours |
| --- | ---: | ---: | ---: | ---: |
| mathématiques fondamentales | 9 | 10 | 11 | 12 |
| statistique | 13 | 15 | 16 | 17 |
| informatique — profil Mathématiques | 18 | 19 | 20 | 21 |
| informatique — profil Statistique | 22 | 23 | 24 | 25 |

La page 14 présente séparément la variante de certification A.Stat., début à
l’automne, cinq cours par session. Elle n’est pas représentée.

## Terminologie et contenu

- Le nom officiel employé est **concentration informatique**.
- « math-info » est traité uniquement comme un raccourci informel.
- La puce commune est **Informatique / programmation**, et non simplement
  « Programmation ».
- Pour les concentrations mathématiques fondamentales et statistique, le guide
  permet `INF1120 — Programmation I` ou `INF1035 — Informatique pour les
  sciences`.
- Dans la concentration informatique, `INF1120` appartient au parcours
  informatique; le contexte des cours complémentaires de première session est
  conservé dans les données de la carte.
- La narration parle donc d’une **base largement commune**, sans prétendre que
  tous les emplacements de première année sont identiques.

La scène « Deux profils » montre directement les différences plutôt qu’une
grille anonyme :

- profil Mathématiques : `MAT2250 — Théorie des groupes` et
  `MAT2260 — Théorie des anneaux`;
- profil Statistique (Science des données) : `STT2000 — Statistique II` et
  `STT2120 — Régression`.

Les regroupements visuels — analyse, algèbre, géométrie, modèles, apprentissage,
algorithmique, systèmes, etc. — sont des synthèses éditoriales. Ils ne sont pas
présentés comme des blocs officiels du programme.

## Cartes et exports

Les 30 cellules de chaque tableau reconstruit reçoivent leurs coordonnées de
libellé lors de l’export statique; les PNG ne sont donc plus des grilles vides.
Chaque carte est exportée dans `dist/tables/` :

- en PNG pour l’aperçu et la diffusion;
- en SVG éditable, avec formes et éléments `<text>` natifs plutôt qu’une image
  matricielle incorporée.

Chaque carte affiche explicitement le libellé du cheminement, son titre officiel
et la page source. Les quatre noms de base normalisés sont consignés dans le
README.

## Narration et sous-titres — V2

`voiceover_fr.txt` est la seule source textuelle utilisée par le moteur de rendu.
Le code refuse les sections manquantes, inconnues, dupliquées ou vides. Chaque
ligne doit constituer une phrase ponctuée et devient un repère SRT court; le
retour à la ligne est limité à deux lignes de 42 caractères au plus.

L’audio de diffusion est généré par Azure Speech. Chaque WAV doit posséder un
fichier `.voice.json` valide contenant le hachage de la narration et de l’audio.
Une modification de transcription invalide donc automatiquement l’audio
existant. `--tts existing` échoue clairement quand cette paire manque ou devient
obsolète; aucun repli eSpeak n’est implicite.

Avec `--scene`, la sélection intervient avant la préparation audio : seule la
scène demandée est préparée et rendue. Le mode scène ne reconstruit ni les
tableaux, ni le film complet, ni son SRT ou son storyboard.

## Lisibilité et identité

La palette corrige les contrastes faibles du prototype :

- or foncé `#8A6500` sur fond clair, environ 4,8:1;
- texte secondaire `#4F5C65` sur fond clair, environ 6,2:1.

Le rendu emploie des polices Noto incluses et vérifiées par hachage afin d’éviter
les substitutions de polices qui avaient produit des lettres floues ou
fragmentées.

Le faux marquage composé d’un carré coloré et du mot « UQAM » a été retiré.
L’en-tête utilise un actif provenant du site officiel de l’UQAM, dont l’URL
d’origine et les hachages figurent dans `project-manifest.toml`.

Important : l’origine officielle du fichier ne vaut pas autorisation de
diffusion. Le champ `identity.authorization` vaut `publisher-must-confirm`.
Avant publication, l’éditeur doit confirmer l’usage auprès de l’UQAM et
respecter sa politique :
<https://servicecom.uqam.ca/normes-et-directives/logo-uqam-et-normes-graphiques.html>.

## Reproductibilité et validation — V2

Le manifeste de projet fixe :

- les dimensions 1280 × 720;
- la cadence de 24 images/s;
- H.264/AAC et `yuv420p`;
- la voix Azure, le débit, le niveau sonore cible et les silences;
- les versions Python, FFmpeg et des dépendances directes;
- les chemins et hachages du guide, de l’identité et des polices.

`render_video.py --check` vérifie les versions et les actifs avant tout rendu.
Après un rendu complet, le fichier `dist/build-manifest.json` consigne les
hachages des entrées, des segments audio et des livrables ainsi que le résultat
FFprobe. Le contrôle vidéo exige un flux H.264 1280 × 720 à 24 images/s et un
flux audio AAC.

Le fondu final est calculé en temps et atteint intégralement la couleur de fond à
la dernière image échantillonnée; il ne conserve plus une image résiduelle à son
point terminal.

## V3 — aperçu narratif de 3:35

### Sources et horloge

Le storyboard V3 est conservé dans `storyboard-v3.md`; son hachage est fixé dans
`project-manifest.toml`. `v3_storyboard_data.py` traduit ce storyboard en
**11 scènes** dont les durées totalisent exactement **215 secondes (3:35)**.
Cette horloge absolue reste indépendante de la longueur estimée du texte.

Le rendu attendu est **1280 × 720 à 30 images/s**, H.264/AAC et `yuv420p`.
Les intermédiaires V3 sont isolés dans `build/v3/`; les aperçus, sous-titres,
master et manifeste de construction V3 sont destinés à `dist/v3/`. Les
répertoires V2 `build/` et `dist/` restent distincts.

### Narration, repères et cache

`voiceover_v3_fr.txt` est la seule source textuelle de narration V3. Ses phrases
sont courtes, ponctuées et conçues pour produire des repères SRT d’au plus deux
lignes de 42 caractères. La synthèse utilise Azure Speech avec
`fr-CA-SylvieNeural`.

Le SSML insère un repère avant chaque phrase. Les temps Azure, exprimés en
unités de 100 ns, sont conservés dans les fichiers `.voice.json` et servent
directement aux sous-titres et aux révélations sémantiques. Aucun calcul de
durée par nombre de mots n’est permis.

Après synthèse, chaque scène est normalisée et stockée comme PCM mono 16 bits à
48 kHz, avec exactement le nombre d’échantillons exigé par son horloge. Les
segments forment une bande maîtresse PCM de 215 secondes sans
rééchantillonnage. L’audio du master final est encodé une seule fois en AAC
pendant l’assemblage.

Le mode `--tts existing` vérifie le texte, la voix, le débit, les repères, les
silences, le format, la durée et les hachages. Toute divergence rend le cache
obsolète et produit une erreur explicite avec une commande de régénération.
Contrairement au brouillon V2 explicitement demandé avec `--tts espeak`, V3 ne
possède aucun repli eSpeak.

### Scènes et lisibilité

L’ouverture V3 emploie une composition plus moderne et plus sobre. Les libellés
animés commencent légèrement flous puis deviennent nets par filtrage du calque
de texte matriciel; la police elle-même n’est pas mise à l’échelle, ce qui évite
les glyphes déformés observés dans le prototype.

Les scènes expliquent directement la lecture du tableau, la charge de cours, la
colonne complémentaire, la base commune, les trois concentrations, les deux
profils informatiques, leur comparaison et le guide officiel. Les différences
de profils sont montrées comme contenu, et non comme une grille anonyme.

### Identité et provenance

V3 reprend `assets/identity/uqam-logo-officiel-blanc.png`, dérivé de l’actif
SVG obtenu sur le site officiel de l’UQAM. L’URL de provenance, la politique
d’utilisation et les hachages sont consignés dans le manifeste.

La scène finale s’appuie sur
`assets/sources/uqam-guide-cover-2025-2026.png`, dérivé du guide PDF officiel
vérifié. Le manifeste conserve également son chemin et son hachage; le PDF
source, son millésime et son propre hachage restent la référence documentaire.

Cette provenance ne vaut pas autorisation de diffusion. Le champ
`identity.authorization` reste `publisher-must-confirm`; l’éditeur doit obtenir
ou confirmer l’autorisation UQAM avant toute distribution publique.

### Contrôles reproductibles

`render_v3.py --check` contrôle les dépendances, encodeurs, hachages, sources de
narration, 11 identifiants de scène, total de 215 secondes, dimensions, cadence
et images échantillons. Les tests V3 couvrent notamment :

- l’ordre et le minutage exacts des scènes;
- la sélection d’une seule scène avant toute préparation audio;
- les sous-titres courts et les repères Azure;
- l’invalidation du cache existant;
- le PCM 48 kHz de durée exacte et sa concaténation;
- l’alignement des actions visuelles sur les phrases;
- le maintien de la dernière image du guide.

Le master V3 a été rendu et validé techniquement : 6 450 images, 215 secondes,
H.264/AAC, `yuv420p`, 48 kHz mono, 46 repères SRT et maintien final sans fondu.
Les hachages reproductibles sont consignés dans
`dist/v3/build-manifest-v3.json`. Cette validation technique ne constitue pas
une approbation éditoriale humaine ni l’autorisation de diffusion UQAM.

## Limites de l’audit

Ce package ne confirme pas :

- l’autorisation de diffusion publique du logo;
- l’offre réelle d’un cours lors d’une session future;
- les conditions d’admission;
- les débouchés, préférences ou garanties de carrière;
- l’admissibilité individuelle à une accréditation.

Pour ces points, consulter les sources institutionnelles à jour et obtenir les
autorisations nécessaires avant publication.

## V4 — progression semestrielle et narration formelle

### Correction éditoriale

V4 retire entièrement la formule répétitive « Une base largement commune ».
Une seule scène intitulée « Des enseignements communs à la spécialisation »
explique la transition. L’ouverture ne recourt plus à des symboles abstraits :
elle présente directement le baccalauréat en mathématiques et les trois
concentrations. La comparaison finale porte uniquement sur leurs objets
d’étude et leurs outils distinctifs.

La narration française compte 55 phrases au registre institutionnel. Chaque
phrase constitue un repère Azure et un sous-titre d’au plus deux lignes de
44 caractères. `voiceover_v4_fr.txt` est l’unique source du texte parlé.

### Signification des positions de cours

La scène autonome de lecture de la carte a été supprimée, tout comme les
panneaux « LECTURE DE LA CARTE » répétés dans les scènes de concentration. Les
matrices anonymes restent absentes. Dans les trois scènes de concentration,
seules les cartes représentatives sont visibles et leur ligne porte l’un des
six libellés suivants :

- 1re année · Automne;
- 1re année · Hiver;
- 2e année · Automne;
- 2e année · Hiver;
- 3e année · Automne;
- 3e année · Hiver.

Les libellés de session sont intégrés à chaque ligne; aucun commentaire de
lecture supplémentaire n’est nécessaire. Chaque titre est résolu directement
à partir des coordonnées auditées dans `program_data.py`.

Le libellé visible est désormais
« Cheminement recommandé — début à l’automne — 5 cours/session », sans
millésime. Le nouveau guide TeX fourni est identifié comme 2026–2027, mais ses
grilles sont des PDF externes absents du dossier. Les positions de cours ne
sont donc pas relabellisées 2026–2027; leur provenance antérieure reste
consignée hors écran. Les autres variantes sont mentionnées, mais ne sont pas
reconstruites.

### Illustrations disciplinaires

Les panneaux de droite contiennent neuf schémas vectoriels déterministes,
directement liés au domaine présenté. Ils représentent une fonction et sa
tangente calculée au même point analytique, une table d’addition modulo 3, une correspondance géométrique, un
échantillonnage, une régression avec bande d’incertitude, trois sorties
d’analyse avancée, une séquence d’instructions, un tri et une architecture en
couches. Leur construction est bornée par les repères d’action existants; ils
ne bouclent pas et deviennent entièrement fixes après leur révélation.

### Concentration informatique et profils

La narration distingue explicitement le noyau informatique commun aux deux
profils — programmation, structures de données, algorithmique, bases de données
ou systèmes — de leurs approfondissements disciplinaires. Le profil
Mathématiques ajoute notamment la théorie des groupes, la théorie des anneaux
et des cours de spécialisation; le profil Statistique ajoute Statistique II,
Régression, la statistique informatique et l’apprentissage statistique.

### Horloge et audio

Les onze durées, choisies après mesure de la narration et selon le temps de
lecture, totalisent 283 secondes (4:43). Quatre minutes ne constituent pas une
cible. La voix Azure demeure `fr-CA-SylvieNeural`, au débit uniforme de `-10 %`,
avec 350 ms de silence initial, 180 ms entre les phrases, au moins 800 ms de
silence final et une normalisation à −18,5 dBFS.

Le moteur ajoute uniquement du silence pour atteindre l’horloge visuelle. Il ne
modifie pas la vitesse de la voix et échoue si la prise naturelle ne tient pas
dans une scène. Les repères Azure pilotent les sous-titres et les révélations
sémantiques. La dernière scène réserve d’abord une composition fixe, puis
s’efface complètement vers le fond et conserve ce fond propre à la fin.

### Isolation, contrôle et identité

Le master 720p30 demeure isolé dans `build/v4/` et `dist/v4/`. Le profil
`1080p60` écrit séparément dans `build/v4-1080p60/` et
`dist/v4-1080p60/`; la révision précédente de ce profil est archivée avant
remplacement et le livrable 720p30 n’est jamais écrasé. Le canevas logique
1280 × 720 est transformé avant rasterisation : les coordonnées, polices,
traits, rayons, flous et actifs sont dessinés nativement à l’échelle 1,5 sur
un canevas 1920 × 1080. Aucun redimensionnement pleine image n’est appliqué.

La cadence native de 60 images/s échantillonne les transitions à des instants
distincts; elle ne duplique pas les images du master 30 images/s. Pour
283 secondes, le contrat du nouveau master est de 16 980 images. Le master
720p30 historique de la version 4.1 demeure conservé à 6 840 images avec sa
narration d’origine; il n’est pas remplacé par cette révision 1080p60.

`storyboard-v4.md`,
`v4_storyboard_data.py`, `voiceover_v4_fr.txt` et les paramètres `[v4]` du
manifeste définissent la version de façon reproductible.

V4 emploie le même actif UQAM de provenance officielle et le même visuel de
guide vérifié. La conclusion affiche ce logo sans reconstruction ni
recoloration, sur un fond sombre à fort contraste. Cette provenance ne
constitue toujours pas une autorisation :
`identity.authorization` demeure `publisher-must-confirm`.
