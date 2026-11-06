# Conclusion commune des deux pilotes

Le propriétaire a choisi le même schéma de fin pour les deux vidéos :
**récapitulatif, invitation à s'exercer, carte finale**. Le helper
`play_lesson_closing` de `tools/teaching_chapters.py` réalise désormais :

1. « À retenir » : trois idées propres à la leçon, en encre noire; maintien
   complet d'au moins huit secondes et jusqu'à la fin de la narration.
2. « À vous » : reprendre un exemple déjà corrigé, sans regarder sa correction;
   même disposition titre, consigne, formule et tâche; maintien d'au moins huit
   secondes et jusqu'à la fin de la narration.
3. « Fin de la capsule » : titre de la leçon et signature de la Faculté dans
   la même position qu'à l'ouverture; maintien d'au moins trois secondes et
   jusqu'à la fin de la narration. Cette carte reste visible dans la dernière
   image encodée, sans disparition vers un écran vide.

L'ancienne conclusion de la vidéo 43 est remplacée, pas doublée. Les quatre
actions antérieures restent présentes dans les trois idées : valeurs interdites,
factorisation et simplification des facteurs, conservation des restrictions.
La vidéo 15 conserve sa vérification finale avant la nouvelle synthèse.
Les profils de voix, les autres 41 vidéos, le catalogue et la banque d'erreurs
ne changent pas. Aucun compteur d'étape ne revient.

## Contenu réutilisé

- 15 : `h(x)=(x²−4)/(x²−x−2)`, déjà corrigé dans l'exercice « garder les
  exclusions ». La tâche porte sur le domaine et le trou. Vérification :
  domaine excluant −1 et 2; trou en `(2, 4/3)`.
- 43 : `x(x+2)/[x(x+5)]`, déjà corrigé dans la capsule. La tâche demande de
  simplifier et conserver les valeurs interdites. Vérification :
  `(x+2)/(x+5)`, avec `x ≠ 0` et `x ≠ −5`.

## Vérification

Les rendus courants sont sous
`review_artifacts/chapter_pilot/2026-10-15/coherent_ending_v4/`.

| Pilote | MP4 complet relatif à ce dossier | Durée | SHA-256 |
|---|---|---:|---|
| 15 | `15/media/videos/480p15/15_chapter_pilot_silent.mp4` | 291,867 s | `75d23ee828268fe5350a6f8a423dc565c9280b42a37f300f1a45d4f96bbae07a` |
| 43 | `43/media/videos/480p15/43_chapter_pilot_silent.mp4` | 143,933 s | `b35a96a9501022f84483ecf831e619ecbf6153fa5de2b0f8c04a40035ada716a` |

Les extraits `15/15_ending_silent.mp4` et `43/43_ending_silent.mp4` isolent
les fins pour faciliter la comparaison. Leurs empreintes, celles des sources,
les événements et les images sélectionnées figurent dans
`closing-validation.json`. Ces extraits proviennent des MP4 réellement rendus.

- Syntaxe des trois modules modifiés et `git diff --check` : réussis.
- Tests ciblés : **78 tests et 36 sous-tests réussis**. Seule alerte : la
  dépréciation préexistante de `pkg_resources`.
- Rendus : deux prévisualisations muettes effectives, 854 × 480, 15 i/s;
  empreintes d'entrée concordantes avec les sources actuelles.
- Événements : ouverture, quatre chapitres, récapitulatif, pratique, fin;
  maintiens 8/8/3 secondes contrôlés. Dernier état contenant la carte finale.
- Inspection visuelle : les trois cartes finales de chaque vidéo ont été
  ouvertes à leur taille native, notamment 15 à 271,967 / 280,767 / 291,777 s
  et 43 à 124,033 / 132,833 / 143,843 s. Pas de débordement ni de chevauchement.
- Relecture indépendante : un rôle ChatGPT « bases algébriques fragiles » a
  inspecté ces six mêmes images et vérifié les deux exercices, sans relever
  de défaut concret. Un autre agent a contrôlé les sources et le cycle de
  narration. Aucun de ces avis n'est une observation d'apprentissage réel.

La narration écrite utilise le profil existant, mais sa synthèse et son écoute
restent bloquées par l'absence d'identifiants Azure. Lecture continue,
synchronisation audiovisuelle réelle et approbation institutionnelle restent
non validées. Les médias sont ignorés par Git; le checkpoint conserve les
sources et les preuves textuelles seulement. Aucun push ni transfert Drive.
