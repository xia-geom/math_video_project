# Storyboard V4 — aperçu du baccalauréat en mathématiques

## Portée

La V4 présente un aperçu institutionnel du baccalauréat en mathématiques de
l’UQAM. Les cartes de cours reconstruisent uniquement le **cheminement
recommandé — début à l’automne — 5 cours/session**. Le guide
officiel demeure la source de référence pour les autres rythmes, les départs
en hiver, les préalables et les choix de cours.

Le texte du guide 2026–2027 fourni avec cette révision confirme les
formulations générales. Ses grilles sont toutefois des PDF externes non
fournis : les positions de cours restent donc rattachées à leur audit source,
sans millésime affiché dans la vidéo.

La durée est déterminée par la synthèse Azure naturelle et le temps de lecture
des éléments visuels. Elle n’est pas ajustée pour atteindre quatre minutes :
les onze scènes totalisent 283 secondes (4 min 43 s).

## Principes visuels

- Utiliser l’appellation officielle « concentration informatique ».
- Employer « Informatique / programmation » pour l’enseignement commun.
- Montrer uniquement les cours représentatifs, sur la ligne de leur session
  recommandée.
- Nommer les six lignes :
  « 1re année · Automne », « 1re année · Hiver »,
  « 2e année · Automne », « 2e année · Hiver »,
  « 3e année · Automne » et « 3e année · Hiver ».
- Laisser les six lignes de session et les titres des cours assurer directement
  la lecture des cartes, sans scène explicative ni panneau « Lecture de la
  carte ».
- Employer le logo UQAM fourni dans `assets/identity/`; l’autorisation de
  diffusion publique doit être confirmée par l’éditeur.
- Éviter les textes dorés à faible contraste et les petites annotations
  marginales.
- Faire apparaître les lettres légèrement floues, puis parfaitement nettes.
- N’afficher aucun millésime dans les titres, les cartes ou les noms des
  livrables courants; la miniature officielle du guide demeure inchangée.
- Terminer par une carte institutionnelle sombre utilisant le logo UQAM local
  sans le reconstruire ni le recolorer.

## Horloge des scènes

| No | Scène | Durée | Intention |
|---:|---|---:|---|
| 1 | `v4_01_opening` | 15 s | Présenter le programme et les trois concentrations directement. |
| 2 | `v4_03_course_load` | 20 s | Distinguer les rythmes et indiquer où retrouver le guide. |
| 3 | `v4_04_complementary_column` | 21 s | Montrer les choix intégrés et la diversification disciplinaire. |
| 4 | `v4_05_common_to_specialization` | 17,5 s | Situer les fondements en première année et la spécialisation en deuxième année. |
| 5 | `v4_06_fundamental_mathematics` | 35,5 s | Présenter analyse, algèbre, géométrie et topologie. |
| 6 | `v4_07_statistics` | 38 s | Présenter données, modèles, incertitude et apprentissage. |
| 7 | `v4_08_mathematics_computing` | 24 s | Présenter les deux profils et leur noyau informatique commun. |
| 8 | `v4_09_computing_profiles` | 32 s | Comparer directement les deux profils informatiques. |
| 9 | `v4_10_comparison` | 36 s | Comparer les objets d’étude et lire explicitement la synthèse. |
| 10 | `v4_11_guide` | 22 s | Diriger vers le guide officiel et ses variantes. |
| 11 | `v4_12_conclusion` | 22 s | Conclure sur la portée des mathématiques et l’accompagnement de l’équipe. |

## Narration et sous-titres

`voiceover_v4_fr.txt` est l’unique source de narration. Chaque ligne est une
phrase et devient un repère Azure ainsi qu’un sous-titre distinct. Les
sous-titres occupent au plus deux lignes de 44 caractères. La version révisée
comprend 55 phrases courtes, dont onze consacrées au noyau informatique et aux
deux profils et quatre à la conclusion.

La synthèse utilise `fr-CA-SylvieNeural` à un débit uniforme de `-10 %`, avec
350 ms de silence initial, 180 ms entre les phrases, au moins 800 ms de silence
final et une normalisation à −18,5 dBFS. La voix n’est ni accélérée ni étirée.
Si une prise naturelle ne tient pas dans une scène, le rendu échoue afin que
la scène soit prolongée explicitement.

## Conclusion et fin

La conclusion affiche en grand le logo UQAM officiel et le message :
« Les mathématiques pour comprendre le monde. Une formation pour construire
votre avenir. » La composition demeure fixe pendant trois secondes. Toute
transition de sortie doit atteindre entièrement la couleur de fond à son point
final.


## Révision du 14 septembre 2026

Données V4 uniquement : guide 2026–2027, version du 24 juillet, pages 9, 13, 18, 22. MAT2411 relève des équations; la géométrie ne sélectionne plus cette case. Président-Kennedy ouvre la première scène jusqu’à la deuxième phrase; le pôle mathématique ouvre la conclusion jusqu’à la troisième phrase. Les horloges restent à 15 et 22 secondes, total 283 secondes. Les fenêtres photo sont alignées sur les phrases réelles; le cache tient compte des fondus. Crédits sur panneaux opaques; aucun témoignage personnel n’est inféré des images.
