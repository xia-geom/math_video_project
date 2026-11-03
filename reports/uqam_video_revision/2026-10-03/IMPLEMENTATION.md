# Deux capsules UQAM — révision du 3 octobre 2026

## Résultat

Le texte sciences, les écrans et les six photographies ont reçu la validation
éditoriale demandée. Le choix musical initial A, *Life of Riley*, a ensuite été
remplacé par **Birds — Corbyn Kites**, à la demande de l'utilisateur.

| Capsule | Rendu 16:9 | Export Instagram | Voix |
|---|---|---|---|
| Mathématiques | 66,317 s, 1920 × 1080, 60 images/s | 1080 × 1920, 30 images/s | MAI-Voice-2, +6 % uniformément |
| Ouvertures sciences | 29,000 s, 1920 × 1080, 60 images/s | 29,000 s, 1080 × 1920, 30 images/s | MAI-Voice-2, +2 %, profil conservé |

Les quatre exports sont dans `dist/uqam_revision_20261003/final/` :

- `uqam_math_birds_20261003.mp4`
- `uqam_math_birds_instagram_20261003.mp4`
- `uqam_sciences_birds_20261003.mp4`
- `uqam_sciences_birds_instagram_20261003.mp4`

Les masters voix seule sont conservés dans les répertoires de rendu propres à
chaque capsule. Les anciennes versions et le troisième film restent conservés.

## Modifications effectivement rendues

- **Sciences :** récit intérêts → majeure → complément compatible → diplôme par
  cumul; les deux ans concernent la majeure. La narration exacte validée comporte
  59 mots et cinq prises, mesurées à 24,552 s au total. Le logo et les maintiens
  tiennent dans les 29 s sans couper la voix. Les écrans portent une idée courte.
- **Maths :** même voix et mêmes mots, débit uniformément +6 %. Visages visibles
  à l'ouverture avec Ludopolis; accueil souriant en fin de film. L'atelier de
  mathématiques apparaît une fois. La bibliothèque reste stable pendant les deux
  prises d'accompagnement. Le contexte et le crédit de chaque photo restent exacts.
- **Photos distinctes :** sciences utilise NorthSec, Métamorphose et l'atelier de
  bouturage; aucun de ces fichiers n'apparaît dans le nouveau film maths.
  Sources, crédits complets et restrictions dans [PHOTOS.md](PHOTOS.md).
- **Transitions :** remplacement direct des textes sur un fond blanc conservé;
  retrait de toute la famille du texte sortant. Le dernier correctif a été motivé
  par un échec réel du contrôle Manim : des lignes de conclusion introduites
  individuellement restaient à l'écran après le retrait de leur groupe.
- **Sous-titres :** fond lisible dans le master sciences sous-titré. Instagram
  conserve toute l'image 16:9 et présente de grands sous-titres de deux lignes
  maximum. Les longues prises sont subdivisées à partir de leurs bornes mesurées,
  proportionnellement au nombre de mots, avec pauses conservées; ce n'est pas un
  alignement vocal mot à mot. Les SRT des masters ne sont pas réécrits.

## Musique et provenance

Le fichier MP3 complet de 120 s est proposé au téléchargement par
[Happy Soul Music](https://happysoulmusic.com/audio/birds_-_corbyn_kites-mp3/).
La page annonce un usage personnel et commercial gratuit avec crédit à l'artiste.
Le fichier fait 4 802 388 octets, se décode entièrement et porte l'empreinte
`eeed79746172b9c1d9af167f9a5b2694489bf4fd7914c80a556432356678d427`.
La source et la portée exacte de cette annonce tierce sont enregistrées dans
[BIRDS_SOURCE.json](BIRDS_SOURCE.json). Une confirmation des conditions par le
détenteur des droits pour la diffusion prévue reste ouverte. Aucune licence
Creative Commons n'est inventée pour cette piste.

Le mixeur accepte désormais un manifeste par enregistrement : titre, auteur,
source, conditions annoncées, lien de téléchargement, date de revue et SHA-256.
Il rejette une piste dont les octets ne correspondent pas à son attribution.
Les comparaisons A/B de 20 s restent archivées dans `music_selection.json`.

Le mix utilise une cible voix de −19 LUFS et une cible musique de −25 LUFS avant
réduction pendant la parole, avec fondus de 0,75 s et 2 s. Aucun changement de
vitesse ou de timing n'est appliqué au mixage. Les paquets vidéo des masters
restent identiques. Son final : AAC stéréo, 48 kHz.

| Mix 16:9 | Niveau intégré mesuré | Crête réelle |
|---|---|---|
| Maths | −19,38 LUFS | −4,31 dBTP |
| Sciences | −19,58 LUFS | −5,04 dBTP |

## Validation réellement effectuée

- Syntaxe des huit fichiers d'implémentation contrôlée.
- **68 tests ciblés réussis** : capsules, géométrie, changement de texte, identité
  du fichier musical, vrai mix FFmpeg synthétique et sous-titres Instagram.
- Deux rendus Azure réels en haute résolution avec les profils existants.
- Décodage complet des exports et contrôles de streams, durées et crêtes.
- Maths : 48 images de contrôle encodées et 54 échantillons de transition
  inspectés. Aucun ancien texte, transition blanche parasite ou collision entre
  texte et panneau photo. Six comparaisons photographiques : déplacement (0, 0).
- Sciences : cinq scènes sous-titrées, transitions, logo et CTA inspectés;
  36 images autour du changement blanc : aucune image vide. Les trois photos
  restent fixes durant leurs maintiens.
- Instagram : vérification H.264/yuv420p, 30 images/s, GOP fermé, AAC 128 kbit/s,
  48 kHz, lecture progressive; images encodées et comparaison du son avec le mix
  d'origine à trois positions pour chaque capsule.

Ces vérifications sont une inspection d'images et des mesures techniques.
**Lecture continue, écoute complète au casque et sur téléphone, approbation
institutionnelle et autorisation de diffusion ne sont pas certifiées.** Aucun
upload Instagram ou publication institutionnelle n'a été effectué.

## Livraison et historique

Destination autorisée : dossier local `My Drive/UQAM-apercu-programme`, dans les
deux sous-dossiers existants et leurs versions du `2026-10-03`. Les nouveaux
exports, sous-titres, crédits complets, manifestes et preuves techniques y sont
copiés avec vérification SHA-256 : **24 fichiers vérifiés, dont quatre vidéos**.
Les textes prononcés sont aussi livrés dans `MATH_NARRATION.txt` et
`SCIENCES_NARRATION.txt`, à côté des vidéos et dans ce dossier de rapport.
Leur texte est vérifié exactement contre les SRT des masters livrés; les
versions 16:9 et Instagram utilisent la même narration. Les historiques
enregistrent le lien et l'empreinte SHA-256 du fichier TXT de chaque capsule.
Les fichiers `versions.json` et l'index local
sont actualisés. La copie locale ne prouve pas la fin de la synchronisation cloud.

Les médias générés, nouveaux JPEG et MP3 restent hors des nouveaux commits Git.
Le checkpoint comprend uniquement les sources, contrôles et rapports inspectés.
