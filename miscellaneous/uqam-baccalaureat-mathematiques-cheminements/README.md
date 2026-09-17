# Cheminements du baccalauréat en mathématiques de l’UQAM

Package reproductible d’une vidéo française présentant trois concentrations du
baccalauréat en mathématiques :

- mathématiques fondamentales;
- statistique;
- concentration informatique, profils Mathématiques et Statistique
  (Science des données).

Dans tout le package, « math-info » est uniquement un raccourci informel. Le nom
officiel affiché est **concentration informatique**.

## Versions incluses

Le package conserve trois chaînes de rendu distinctes :

- **V2**, le rendu historique de cartes de cheminement, piloté par
  `render_video.py`, `voiceover_fr.txt`, `build/` et `dist/`;
- **V3**, un aperçu narratif moderne de **3 min 35 s exactement**, composé de
  **11 scènes**, piloté par `render_v3.py`, `storyboard-v3.md`,
  `v3_storyboard_data.py`, `voiceover_v3_fr.txt`, `build/v3/` et `dist/v3/`.
- **V4**, la révision éditoriale et visuelle de **4 min 43 s**, composée de
  **11 scènes**, pilotée par `render_v4.py`, `storyboard-v4.md`,
  `v4_storyboard_data.py` et `voiceover_v4_fr.txt`. Elle conserve un master
  720p30 dans `dist/v4/` et un master natif 1080p60 dans
  `dist/v4-1080p60/`.

Les instructions V2 et V3 restent valides. Les chaînes V4, V3 et V2 utilisent
des répertoires distincts et ne s’écrasent pas.

## Périmètre éditorial V2

Les cartes animées et les tableaux exportés représentent exclusivement :

> Cheminement recommandé — début à l’automne — 5 cours/session — 2025–2026

Le guide officiel contient aussi des cheminements commençant à l’hiver, des
charges de quatre cours par session et une variante de certification A.Stat.
Ces variantes ne sont pas représentées dans la vidéo; voir [AUDIT.md](AUDIT.md).

La vidéo sert à donner une orientation visuelle. Elle ne remplace pas le guide
officiel et ne formule aucune promesse sur l’admission, l’offre future de cours,
les carrières ou l’accréditation.

## Périmètre éditorial V3

V3 présente l’organisation générale du programme, les charges possibles de
quatre ou cinq cours, la base largement commune, les trois concentrations et les
deux profils de la concentration informatique. Le minutage est fixé à
**215 secondes**, soit **3:35**, à raison de **11 scènes**.

Le système visuel est clair, neutre et contemporain. L’ouverture a été
redessinée; les libellés importants apparaissent d’abord légèrement flous puis
deviennent nets, sans déformer les glyphes. Les révélations sémantiques sont
alignées sur les repères de narration Azure, tandis que l’horloge absolue de
chaque scène reste définie dans `v3_storyboard_data.py`.

## Installation reproductible

Le fichier `project-manifest.toml` est la source canonique du champ
`project.source_year`, du libellé du cheminement, des paramètres de rendu, de la
voix Azure, des chemins d’artefacts et des versions attendues.

Prérequis :

- Python 3.11 à 3.13 (Python 3.13.5 est la version de référence);
- FFmpeg et FFprobe 6 ou plus récents (FFmpeg 8.0.1 est la référence);
- encodeurs FFmpeg `libx264` et `aac`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python render_video.py --check
```

`requirements.txt` énumère les dépendances directes. `requirements.lock`
reproduit l’environnement complet validé sous Python 3.13.5. La commande
`--check` vérifie Python, les versions Python épinglées, FFmpeg/FFprobe, les
encodeurs, les hachages des sources et actifs, ainsi que la structure de
`voiceover_fr.txt`.

## Narration V2

`voiceover_fr.txt` est l’unique source de narration et de sous-titres. Chaque
section porte l’identifiant exact d’une scène et chaque ligne non vide forme un
repère de sous-titre court, au niveau de la phrase.

La narration de diffusion utilise Azure Speech, avec les paramètres du
manifeste (`fr-CA-SylvieNeural`, débit `-14%`). Après avoir fourni
`SPEECH_KEY` et `SPEECH_REGION` :

```bash
.venv/bin/python render_video.py --tts azure
```

Chaque fichier `build/audio/<scene>.wav` est accompagné de
`build/audio/<scene>.voice.json`. Ce fichier latéral enregistre notamment le
hachage de la narration, le fournisseur, la voix, le débit, la durée et le
hachage audio. Le mode par défaut, `--tts existing`, valide strictement cette
paire : une narration absente, modifiée ou incohérente provoque une erreur
explicite et ne déclenche jamais un repli silencieux vers eSpeak.

eSpeak reste disponible uniquement pour un brouillon explicitement demandé :

```bash
.venv/bin/python render_video.py --tts espeak
```

## Rendu V2

Rendu complet, après préparation de tous les segments Azure :

```bash
.venv/bin/python render_video.py --tts existing
```

Le rendu de référence est 1280 × 720, H.264/AAC, 24 images/s, au format
`yuv420p`.

Pour préparer et rendre une seule scène :

```bash
.venv/bin/python render_video.py --scene 04_info_profiles --tts azure
```

Avec `--scene`, seules la narration et la vidéo de la scène demandée sont
préparées. Les autres narrations, les tableaux, l’assemblage, le storyboard et
le SRT complet ne sont pas produits.

## Narration et synchronisation V3

`voiceover_v3_fr.txt` est l’unique source de narration et de sous-titres V3.
Chaque ligne non vide est une phrase courte et devient un repère SRT d’au plus
deux lignes.

La voix de diffusion est Azure Speech **`fr-CA-SylvieNeural`**. Une balise
Azure est placée avant chaque phrase; les temps exacts retournés par Azure
pilotent les sous-titres et les révélations visuelles. Aucun minutage fondé sur
le nombre de mots n’est utilisé.

Chaque segment synthétisé est décodé, normalisé et conservé en PCM mono 16 bits
à **48 kHz**, avec exactement la durée de sa scène. Les 11 segments sont
concaténés sur l’horloge exacte de 215 secondes, sans rééchantillonnage. La
bande-son maîtresse PCM n’est encodée en AAC qu’une seule fois lors de
l’assemblage final.

Chaque WAV V3 possède un fichier `.voice.json` contenant notamment le hachage
de la narration, la configuration Azure, les repères de phrase et le hachage de
l’audio. `--tts existing` valide strictement cette paire. Un texte modifié, un
repère absent, une mauvaise durée ou un mauvais format invalide le cache et
provoque une erreur explicite. V3 ne possède aucun repli vers eSpeak.

## Commandes V3

Vérifier l’environnement, les actifs, le storyboard, les 11 scènes et les
images d’essai :

```bash
.venv/bin/python render_v3.py --check
```

Après avoir défini `SPEECH_KEY` et `SPEECH_REGION`, générer ou régénérer toute
la narration Azure, sans rendre la vidéo :

```bash
.venv/bin/python render_v3.py --tts azure --audio-only
```

Rendre une seule scène avec son audio Azure déjà validé :

```bash
.venv/bin/python render_v3.py \
  --scene v3_08_mathematics_computing \
  --tts existing
```

Exporter uniquement les 11 aperçus fixes et leur planche-contact, sans préparer
l’audio :

```bash
.venv/bin/python render_v3.py --previews-only
```

`--scene <identifiant> --previews-only` limite cet export à une scène. Pour
rendre les 11 scènes puis produire tous les livrables V3 :

```bash
.venv/bin/python render_v3.py --tts existing
```

Après un rendu scène par scène, valider les caches et les 11 segments existants,
puis effectuer uniquement l’assemblage :

```bash
.venv/bin/python render_v3.py --tts existing --assemble-only
```

Le rendu V3 est **1280 × 720**, **30 images/s**, H.264/AAC et `yuv420p`.
L’assemblage produit une durée exacte de **3:35**.

Tests V3 :

```bash
.venv/bin/python -m unittest tests.test_v3_audio tests.test_render_v3
```

## Révision V4

V4 répond aux problèmes de compréhension relevés dans V3. L’ouverture nomme
immédiatement le programme et ses trois concentrations. La formulation
répétitive « Une base largement commune » est supprimée; une seule transition,
« Des enseignements communs à la spécialisation », explique la progression.

La scène autonome consacrée à la lecture de la carte a été retirée. Les
panneaux répétés « LECTURE DE LA CARTE » ont également été supprimés : les
repères semestriels utiles restent intégrés directement aux scènes concernées.

Les scènes de concentration ne montrent plus une matrice vide de 30 cellules.
Elles présentent uniquement les cours représentatifs, placés sur six lignes
explicitement nommées de « 1re année · Automne » à « 3e année · Hiver ».
Ces libellés intégrés rendent la progression immédiatement lisible sans
légende supplémentaire.

Le panneau de droite complète chaque domaine par un schéma vectoriel sobre :
fonction, table algébrique, transformation géométrique, échantillonnage,
régression, analyses avancées, programmation, tri ou architecture en couches.
Chaque schéma se construit une seule fois pendant le repère narratif existant,
puis demeure fixe; aucune animation décorative ou répétitive n’est utilisée.

La concentration informatique présente d’abord le noyau commun aux deux
profils — programmation, structures de données, algorithmique, bases de données
ou systèmes — puis les approfondissements propres aux profils Mathématiques et
Statistique.

La fonction et sa tangente sont désormais dérivées de la même expression
analytique afin que leur point de contact soit exact. La vidéo se termine par
une carte institutionnelle sombre, avec le logo UQAM officiel en grand et le
message consacré à la compréhension du monde et à la construction de l’avenir.

La durée de **283 secondes (4:43)** résulte de la synthèse Azure mesurée et
du temps de lecture; elle n’a pas été étirée pour atteindre une durée ronde.
`voiceover_v4_fr.txt` contient **55 phrases formelles**, chacune liée à un
repère de narration vérifié et à un sous-titre court. La voix demeure
`fr-CA-SylvieNeural`, à un débit uniforme de `-10 %`; aucune accélération ou
compression temporelle de la voix n’est admise.

Deux profils de rendu isolés sont disponibles. Le profil par défaut produit
un master en 1280 × 720 à 30 images/s. Le profil `1080p60` dessine
directement les polices, traits, ombres et actifs en 1920 × 1080 à
60 images/s; il ne redimensionne jamais une image 720p terminée. Les rendus
produits à partir des sources 4.3 partagent la narration Azure ralentie et les
mêmes 55 sous-titres. Le master 720p30 publié avec la version 4.1 demeure
conservé, inchangé, comme livrable historique.

Les titres, cartes et noms de livrables V4 sont sans millésime. Le nouveau
`assets/sources/uqam-guide-etudiant-2026-2027.tex` documente les formulations
générales; ses grilles externes n’étant pas jointes, les positions de cours ne
sont pas présentées comme une révision 2026–2027. La miniature officielle du
guide reste affichée telle quelle.

### Commandes V4

Vérifier les sources, les paramètres, les scènes et des images d’essai :

```bash
.venv/bin/python render_v4.py --check
```

Générer la narration Azure V4 :

```bash
.venv/bin/python render_v4.py --tts azure --audio-only
```

Tester le profil partagé MAI-Voice-2 sans remplacer le master ni son cache :

```bash
SPEECH_REGION=canadacentral \
MANIM_VOICE=MAI-Voice-2 \
.venv/bin/python render_v4.py \
  --render-profile 1080p60 \
  --artifact-tag MAI-Voice-2_YYYYMMDD_HHMMSS_TZ \
  --background-music \
  --tts azure
```

La clé demeure uniquement dans `SPEECH_KEY` (ou l’alias historique déjà
configuré). Le sélecteur partagé applique la voix française MAI, sa locale
`fr-FR`, un débit modérément ralenti de `-3 %` et le transport MP3 mono 48 kHz.
MAI ne retournant actuellement pas les événements de repère du SDK, chaque
phrase est synthétisée comme un segment distinct. Ses limites PCM exactes
pilotent les sous-titres et les révélations visuelles; les pauses de 180 ms et
l’horloge V4 restent inchangées, sans estimation par nombre de mots.

L’option `--background-music` utilise la piste Pixabay épinglée dans le
manifeste. Deux passages sont reliés par un fondu croisé de quatre secondes,
puis le lit musical est atténué de 18 dB, légèrement creusé autour de la bande
de la parole et abaissé pendant la narration. Le début et la fin sont fondus;
le master narratif PCM demeure inchangé et le mix final reste mono à 48 kHz.

Exporter les aperçus sans préparer l’audio :

```bash
.venv/bin/python render_v4.py --previews-only
```

Rendre une seule scène :

```bash
.venv/bin/python render_v4.py \
  --scene v4_08_mathematics_computing \
  --tts existing
```

Rendre les onze scènes et assembler les livrables :

```bash
.venv/bin/python render_v4.py --tts existing
```

Rendre le master natif 1080p60 sans remplacer le master 720p30 :

```bash
.venv/bin/python render_v4.py \
  --render-profile 1080p60 \
  --tts existing
```

Vérifier uniquement le profil natif :

```bash
.venv/bin/python render_v4.py --render-profile 1080p60 --check
```

Tests V4 :

```bash
.venv/bin/python -m unittest tests.test_v4_audio tests.test_render_v4
```

## Organisation et artefacts

- `project-manifest.toml` : manifeste canonique et versions;
- `program_data.py` : données éditables des cheminements;
- `voiceover_fr.txt` : narration et repères de sous-titres;
- `render_video.py` : rendu, audio, exports et validations;
- `storyboard-v3.md` : storyboard éditorial V3;
- `v3_storyboard_data.py` : horloge exacte et actions des 11 scènes V3;
- `voiceover_v3_fr.txt` : source unique de narration V3;
- `v3_audio.py` : synthèse Azure, repères, cache et PCM V3;
- `v3_visuals.py` : système visuel et dessins V3;
- `render_v3.py` : orchestration, rendu, sous-titres et assemblage V3;
- `storyboard-v4.md` : storyboard éditorial V4;
- `v4_storyboard_data.py` : horloge lisible et placements V4;
- `voiceover_v4_fr.txt` : source unique de narration V4;
- `v4_narration.py` : validation de la narration et politique vocale V4;
- `v4_audio.py` : façade V4 du moteur Azure à repères;
- `v4_visuals.py` : scènes et progression semestrielle V4;
- `render_v4.py` : orchestration, rendu, sous-titres et assemblage V4;
- `assets/sources/` : guide PDF dont le hachage est vérifié;
- `assets/identity/` : actif d’identité UQAM et provenance;
- `assets/fonts/` : polices Noto redistribuables;
- `build/audio/` : audio intermédiaire et fichiers `.voice.json`;
- `build/scenes/` : scènes vidéo intermédiaires;
- `dist/` : livrables normalisés et manifeste de construction;
- `dist/tables/` : tableaux PNG et SVG éditables;
- `build/v3/audio/` : PCM V3 et fichiers `.voice.json`;
- `build/v3/scenes/` : 11 segments vidéo V3;
- `dist/v3/previews/` : aperçus fixes V3;
- `dist/v3/` : livrables V3 et `build-manifest-v3.json`.
- `build/v4/audio/` : PCM V4 et fichiers `.voice.json`;
- `build/v4/scenes/` : 11 segments vidéo V4;
- `dist/v4/previews/` : aperçus fixes V4;
- `dist/v4/` : livrables V4 et `build-manifest-v4.json`.
- `build/v4-1080p60/scenes/` : 11 segments natifs 1080p60;
- `dist/v4-1080p60/` : master natif, aperçus et
  `build-manifest-v4-1080p60.json`.

Le nom de base des livrables principaux est :

```text
uqam-baccalaureat-mathematiques-cheminements-recommandes-automne-5-cours-2025-2026-fr-ca
```

Le rendu complet produit :

- `<nom>.mp4`;
- `<nom>.srt`, avec des repères courts d’au plus deux lignes;
- `<nom>-storyboard.png`;
- `build-manifest.json`, avec les hachages des entrées, de l’audio et des
  sorties;
- quatre cartes dans `dist/tables/`, chacune en PNG et en SVG comportant de
  vrais éléments texte éditables.

Le nom de base V3 est :

```text
uqam-baccalaureat-mathematiques-apercu-programme-2025-2026-fr-ca-v3
```

Les livrables V3 correspondants se trouvent dans `dist/v3/` : MP4, SRT,
planche-contact, aperçus individuels et `build-manifest-v3.json`.

Le nom de base V4 est :

```text
uqam-baccalaureat-mathematiques-apercu-programme-fr-ca-v4
```

Les livrables V4 correspondants se trouvent dans `dist/v4/`.

Les cartes portent les noms normalisés suivants :

```text
uqam-cheminement-mathematiques-fondamentales-automne-5-cours-2025-2026
uqam-cheminement-statistique-automne-5-cours-2025-2026
uqam-cheminement-concentration-informatique-profil-mathematiques-automne-5-cours-2025-2026
uqam-cheminement-concentration-informatique-profil-statistique-automne-5-cours-2025-2026
```

## Identité UQAM

L’actif placé dans `assets/identity/` provient du site officiel de l’UQAM; son
URL d’origine, son hachage et la politique d’utilisation sont consignés dans le
manifeste. Cette provenance ne constitue pas une autorisation de publication.
V3 et V4 utilisent ce même actif institutionnel et un visuel de couverture
dérivé du guide PDF officiel vérifié, dont le chemin et le hachage figurent
aussi dans le manifeste.

Avant toute diffusion publique, l’éditeur doit confirmer son droit d’utiliser
le logo conformément à la politique de l’UQAM :
<https://servicecom.uqam.ca/normes-et-directives/logo-uqam-et-normes-graphiques.html>.
Le drapeau d’autorisation reste explicitement
`identity.authorization = "publisher-must-confirm"`.


## Révision V4 — 14 septembre 2026

La nouvelle V4 utilise `program_data_v4.py` et le PDF officiel complet 2026–2027. Les paragraphes historiques ci-dessus concernant les grilles 2025–2026 ne décrivent plus cette révision. V2/V3 et `program_data.py` restent historiques. Le millésime absent du titre ne constitue pas une garantie d’actualité : vérifier le manifeste avant diffusion. Les sorties de revue utilisent un `--artifact-tag` et ne remplacent pas les masters. Voir `../../reports/uqam_video_revision/2026-09-14/PLAN.md` et les artefacts du workflow UQAM revision.
