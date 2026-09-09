# Journal des changements

## 4.3.0 — révision éditoriale et conclusion institutionnelle

- Retrait des millésimes dans l’ouverture, les cartes, le titre du guide et
  les noms des livrables V4; la miniature officielle du PDF reste inchangée.
- Intégration des remarques éditoriales sur le guide étudiant, les cinq cours,
  la diversification, la première année commune, la spécialisation en deuxième
  année et les formulations propres aux trois concentrations.
- Ajout de la synthèse parlée de la comparaison et prolongation de la scène
  afin que son message final demeure lisible.
- Reconstruction analytique de la fonction et de sa tangente, avec un point de
  contact exact au lieu d’un segment de droite indépendant.
- Ajout d’une onzième scène de conclusion utilisant en grand le logo UQAM
  officiel local et le message proposé sur la portée des mathématiques.
- Passage à **55 phrases**, **283 secondes (4:43)** et **16 980 images** dans
  le master natif 1080p60, toujours avec Azure à `-10 %`.
- Ajout du guide TeX 2026–2027 comme source générale, sans attribuer ce
  millésime aux grilles externes absentes du fichier fourni.

## 4.2.0 — narration plus posée

- Ralentissement uniforme de la voix Azure `fr-CA-SylvieNeural`, de `-5 %` à
  `-10 %`, sans étirement ni modification du texte.
- Prolongation de six scènes serrées afin de préserver au moins 800 ms de
  silence final; les dix scènes totalisent désormais **234 secondes (3:54)**.
- Régénération des repères Azure, des sous-titres et de toutes les animations
  qui leur sont liées dans le master natif 1080p60.
- Conservation inchangée du master 720p30 de la version 4.1 et archivage du
  précédent master 1080p60 avant remplacement.

## 4.1.0 — parcours resserré et profils clarifiés

- Suppression de la scène autonome de lecture de la carte et des panneaux
  répétés « LECTURE DE LA CARTE » dans les scènes de concentration.
- Révision de la narration de la concentration informatique : le noyau commun
  est présenté avant les différences entre les profils Mathématiques et
  Statistique.
- Passage à **10 scènes**, **228 secondes (3:48)** et **46 phrases** de
  narration, sans modifier les chaînes V2 et V3.
- Ajout d’un profil natif **1920 × 1080 à 60 images/s**, isolé du master
  1280 × 720 à 30 images/s et rendu directement à l’échelle 1,5 sans
  post-redimensionnement.
- Le dernier plan s’efface désormais complètement vers la couleur de fond et
  conserve ce fond propre jusqu’à la fin du fichier encodé.
- Les panneaux de droite des trois concentrations comprennent désormais neuf
  schémas vectoriels sobres et synchronisés : fonction et table algébrique,
  transformation géométrique, échantillonnage et modèles, puis programmation,
  algorithmique et architecture informatique.

## 4.0.0 — progression semestrielle et narration formelle

### Compréhension et image

- Remplacement de l’ouverture abstraite par une présentation directe du
  programme et des trois concentrations.
- Suppression des matrices de cours anonymes et des cellules vides.
- Ajout de six lignes explicites, de « 1re année · Automne » à
  « 3e année · Hiver », avec les cours représentatifs à leur session auditée.
- Ajout d’une légende qui définit le sens des positions verticale et
  horizontale.
- Refonte de la scène des deux profils afin de montrer directement leurs
  approfondissements distinctifs.
- Comparaison finale limitée aux différences d’objets d’étude et d’outils.

### Texte et narration

- Suppression de toutes les occurrences de
  « Une base largement commune ».
- Ajout d’une seule transition formelle :
  « Des enseignements communs à la spécialisation ».
- `voiceover_v4_fr.txt` devient la source unique de 49 phrases de narration.
- Nouvelle synthèse Azure `fr-CA-SylvieNeural` à `-5 %`, avec 350 ms de silence
  initial, 180 ms entre les phrases et au moins 800 ms de silence final.
- Interdiction de l’accélération et de l’étirement temporel de la voix; une
  prise trop longue provoque une erreur.

### Durée et reproductibilité

- Horloge lisible de 11 scènes totalisant **242 secondes (4:02)**, déterminée
  par la synthèse mesurée et le contenu plutôt que par une cible ronde.
- Ajout de `storyboard-v4.md`, `v4_storyboard_data.py`, `v4_narration.py`,
  `v4_audio.py`, `v4_visuals.py` et `render_v4.py`.
- Isolation des intermédiaires et livrables dans `build/v4/` et `dist/v4/`.
- Ajout d’une section `[v4]` au manifeste et de tests V4 pour la narration,
  les positions de cours, les scènes, les caches et les sorties.

## 3.0.0 — storyboard et chaîne de rendu V3

Cette entrée décrit l’ajout de la chaîne V3. Le master final a été rendu et
validé techniquement à 6 450 images et 215 secondes; son approbation éditoriale
et l’autorisation de diffusion UQAM restent distinctes.

### Format et storyboard

- Ajout d’un storyboard précis de **11 scènes** et d’une horloge fixe de
  **215 secondes (3:35)**.
- Nouveau rendu **1280 × 720 à 30 images/s**, H.264/AAC et `yuv420p`.
- Isolation des intermédiaires et livrables dans `build/v3/` et `dist/v3/`,
  sans écraser V2.
- Ajout d’un mode d’aperçus fixes indépendant de la narration.

### Image

- Nouvelle ouverture moderne sur fond clair et système visuel neutre.
- Animation des libellés par un passage du flou au net sur le calque de texte,
  sans mise à l’échelle destructrice des glyphes.
- Les révélations sémantiques des concentrations et des profils suivent les
  repères exacts des phrases.
- La scène finale présente le guide officiel et se termine sur une image fixe,
  sans fondu résiduel.

### Narration et sous-titres

- `voiceover_v3_fr.txt` devient l’unique source de narration V3.
- La narration est divisée en phrases courtes destinées à des repères SRT d’au
  plus deux lignes.
- Azure Speech `fr-CA-SylvieNeural` insère et retourne un repère exact avant
  chaque phrase; aucun minutage par nombre de mots n’est utilisé.
- Chaque scène est normalisée en PCM mono 16 bits, 48 kHz, avec une durée
  exactement égale à son horloge; les 11 segments sont concaténés sans
  rééchantillonnage et la bande maîtresse n’est encodée en AAC qu’à
  l’assemblage final.
- Le cache `.voice.json` est strictement lié au texte, à la configuration, aux
  repères et au fichier audio. `--tts existing` échoue explicitement si une
  donnée manque ou diverge.
- Aucun repli eSpeak n’existe dans la chaîne V3.

### Identité, sources et validation

- V3 utilise l’actif d’identité provenant du site officiel de l’UQAM et un
  visuel de couverture dérivé du guide PDF officiel vérifié; leurs chemins,
  provenances et hachages sont consignés dans le manifeste.
- L’autorisation de diffusion publique n’est pas présumée :
  `identity.authorization` reste `publisher-must-confirm`.
- Ajout de commandes distinctes pour la vérification, la synthèse Azure seule,
  les aperçus, une scène, le rendu complet et l’assemblage seul.
- Ajout de tests pour les horloges, la sélection de scène, les repères Azure,
  l’invalidation du cache, le PCM exact, les sous-titres et l’alignement visuel.

## 1.0.0 — package reproductible

### Contenu et terminologie

- Le périmètre est désormais libellé explicitement :
  **« Cheminement recommandé — début à l’automne — 5 cours/session —
  2025–2026 »**.
- Le nom officiel **concentration informatique** remplace
  « mathématiques-informatique »; « math-info » ne subsiste que comme raccourci
  informel.
- La puce commune « Programmation » devient
  **« Informatique / programmation »** pour refléter l’alternative `INF1120` ou
  `INF1035` dans les concentrations mathématiques fondamentales et statistique.
- La formulation « base largement commune » est conservée afin de ne pas
  présenter les cheminements de première année comme strictement identiques.
- La scène « Deux profils » montre maintenant les cours qui différencient
  directement les profils Mathématiques et Statistique (Science des données).

### Image et accessibilité

- Le premier écran et l’en-tête ont été modernisés.
- Le faux marquage UQAM construit avec un carré et du texte a été remplacé par
  un actif provenant du site officiel de l’UQAM.
- Les couleurs or et grise ont été foncées pour améliorer le contraste sur fond
  clair.
- Les polices Noto sont intégrées au package et vérifiées par hachage afin de
  stabiliser le rendu des lettres.
- Le fondu final atteint désormais entièrement la couleur de fond.

### Narration et sous-titres

- `voiceover_fr.txt` devient l’unique source de narration.
- Les sous-titres sont divisés en repères courts au niveau de la phrase, limités
  à deux lignes.
- La narration de diffusion est régénérée par Azure Speech.
- Chaque WAV possède un fichier `.voice.json` avec les hachages de narration et
  d’audio, le fournisseur, la voix, le débit et la durée.
- Une modification du texte invalide l’audio mis en cache.
- `--tts existing` échoue explicitement si l’audio est absent ou obsolète; il ne
  bascule plus silencieusement vers eSpeak.

### Rendu et livrables

- Les noms du package et des artefacts ont été normalisés.
- `project-manifest.toml` centralise l’année source, le cheminement, les actifs,
  les paramètres de narration, le rendu et les versions.
- `requirements.txt` et `requirements.lock` documentent respectivement les
  dépendances directes et l’environnement complet.
- `--check` vérifie Python, FFmpeg/FFprobe, les dépendances, encodeurs, actifs et
  narration.
- `--scene` prépare uniquement la scène demandée et ignore l’assemblage complet,
  les autres narrations et les tableaux.
- Le rendu passe à **24 images/s**, 1280 × 720, H.264/AAC.
- `render_table_stills()` transmet désormais toutes les coordonnées de libellé;
  les cartes statiques ne sont plus des grilles vides.
- Chaque carte reconstruite est exportée en PNG et en SVG éditable.
- Les intermédiaires sont placés dans `build/`; les livrables normalisés, le SRT,
  le storyboard, les tables et `build-manifest.json` sont placés dans `dist/`.

### Gouvernance de l’identité

- Le manifeste consigne l’URL officielle de provenance et les hachages de
  l’actif UQAM.
- Aucune autorisation de diffusion publique n’est revendiquée. Le diffuseur doit
  confirmer son droit d’utilisation selon la politique de l’UQAM avant
  publication.

## Prototype antérieur

- Durée portée d’environ 90 secondes à environ trois minutes.
- Listes de cours denses remplacées par des cartes de cheminement
  reconstruites.
- Barre de sous-titre permanente retirée.
- Une idée principale et peu de cellules lisibles sont montrées dans la plupart
  des scènes.
- Ajout des thèmes d’analyse, algèbre, géométrie, collecte, modélisation,
  apprentissage statistique, programmation, algorithmique, systèmes et profils.
