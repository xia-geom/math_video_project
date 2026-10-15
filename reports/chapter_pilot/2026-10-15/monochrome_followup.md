# Suivi visuel — encre unique et suppression du compteur d'étape

À la demande du propriétaire après inspection des prévisualisations, les deux
pilotes utilisent désormais une seule encre noire pour les textes pédagogiques,
formules, titres, courbes et bordures. Les panneaux restent neutres et clairs.
La signature de la Faculté conserve les couleurs de sa référence.

Le pied de carte « Étape N sur 4 » est supprimé. Le plan conserve les mêmes
quatre chapitres, dans le même ordre, avec le seul chapitre entrant en gras.
Les étapes mathématiques du récapitulatif sont conservées. Aucun contenu
mathématique, aucune narration ni durée de lecture n'a changé.

La personnalisation des panneaux de la leçon 15 couvre aussi les exemples
guidés et les exercices. Les autres leçons gardent leur couleur par défaut;
une seconde lecture du diff n'a trouvé aucun chemin de couleur oublié ni
collision de méthode avec les autres scènes.

## Preuves de cette révision

Les nouveaux rendus se trouvent sous
`review_artifacts/chapter_pilot/2026-10-15/monochrome_v3/` :

| Pilote | Fichier relatif à ce dossier | Durée | SHA-256 |
|---|---|---:|---|
| 15 | `15/media/videos/480p15/15_chapter_pilot_silent.mp4` | 271,467 s | `8f9807b7bf925d231280eab7fcb491d90b80eebd768bda4ee1d8bf5ee1b49722` |
| 43 | `43/media/videos/480p15/43_chapter_pilot_silent.mp4` | 130,600 s | `45d32a847217e0f4b87a9b51262f948fd53c3bf3c6662d63ee6e18edda689093` |

- Syntaxe : compilation des quatre modules modifiés réussie.
- Tests ciblés : **58 réussis et 36 sous-tests réussis**, avec la dépréciation
  préexistante de `pkg_resources` comme seule alerte; `git diff --check` propre.
- Rendus effectifs : les deux MP4 sont produits à 854 × 480, 15 i/s, sans audio.
  Les empreintes de leurs sources correspondent aux fichiers actuels.
- Extraction : 55 images de la vidéo 15 et 58 de la vidéo 43. Les 105 images
  hors ouverture ont été contrôlées numériquement : différence maximale entre
  canaux RGB égale à zéro, donc aucun reste de couleur dans ces échantillons.
- Contrôle de contenu : aucun « Étape » dans les étiquettes capturées; les
  quatre frontières de chaque pilote sont conservées. Noir sur blanc : 21:1;
  le test des fonds légèrement teintés reste supérieur à 4,5:1.
- Inspection visuelle directe : récapitulatif 43 à 130,510 s, chapitre 3 de 43
  à 51,233 s, chapitre 3 de 15 à 52,567 s, ouverture 15 à 1,100 s, et planche
  des exemples de 15 à 112,177–197,110 s. Le gras, les encadrés et le point
  exclu conservent le sens sans codage par couleur.

Les données de contrôle figurent dans `style-validation.json`, les index
d'images et les `STATUS.json` de ce dossier. Le journal des tests est
`review_artifacts/chapter_pilot/2026-10-15/tests-monochrome.log`.

Ces vérifications concernent des prévisualisations muettes et des images
échantillonnées. La lecture continue en mouvement, l'écoute, la synchronisation
audiovisuelle réelle et l'approbation institutionnelle restent non validées,
comme dans le rapport initial. Le catalogue et la banque ne sont pas modifiés.
Les anciens rendus et rapports sont conservés, les nouveaux médias restent
hors Git, et aucun push ni transfert Drive n'est effectué.
