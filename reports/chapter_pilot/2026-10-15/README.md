# Pilote de chapitrage — 15 octobre 2026

Les sources des leçons **15 — Fonctions rationnelles** et **43 — Annulation
dans les fractions** intègrent le traitement demandé. Deux prévisualisations
muettes ont réellement été rendues et inspectées par échantillonnage. Le
catalogue français des 43 vidéos est compilé et ses trois pages ont été
inspectées. **Le pilote narré reste à valider : les identifiants Azure sont
absents de cet environnement.** Aucun livrable n'est déclaré prêt à publier.

## Modifications livrées

- Ouverture unique : titre, objectif et signature de la Faculté des sciences
  en bas à gauche. Les autres 41 leçons conservent leur ouverture existante.
- Helpers réutilisables dans `tools/teaching_chapters.py`, avec limites de
  cadre, séquence de chapitres contrôlée, maintien de lecture et narration
  terminée avant la disparition de la carte. Les quatre frontières sont
  écrites explicitement dans chaque scène pilote.
- Même plan aux quatre étapes; seul le chapitre entrant est en gras. Les
  lignes ont une position gauche fixe. Une courte transition est prévue à
  chaque rappel, sans récitation du plan complet.
- Palette pédagogique assombrie, titres et marges cohérents, récapitulatifs.
  Dans la capsule 43, les valeurs interdites apparaissent avant l'égalité
  simplifiée; les trois diagnostics se succèdent à une taille lisible.
- [Catalogue LaTeX autonome](../../../books/mat0339/curriculum/catalogue-videos.tex)
  et [méthode de correspondance](../../../books/mat0339/docs/catalogue-videos-2026-10-15.md).
  Les associations vivent dans `catalogue_references` de `video-map.json`,
  indexées par les identités stables du catalogue unifié. Manuel et cahier ont
  des colonnes distinctes. Les 43 entrées existantes y figurent une fois;
  aucun lien de visionnement, chemin de fichier ou code QR n'y apparaît.
- [Banque priorisée de conceptions erronées](../../../curriculum/misconceptions_prioritaires_fr.md)
  : six candidats avec raisonnement incorrect, correction, sources primaires,
  exercices pertinents, couverture existante et décision éditoriale. Les
  mécanismes documentés et les erreurs plausibles sont distingués. L'ordre
  proposé ne représente pas une mesure locale de fréquence et ne commande
  aucune nouvelle vidéo.

Les identités, les profils de voix dans `tools/tts.py`, les sources pédagogiques
du livre et les audits historiques sont préservés. Aucun export de navigation
ou changement de lecteur n'a été ajouté. Les temps cités ci-dessous servent
uniquement de preuves internes de contrôle.

## Sources et contraste

La [référence officielle de signature](https://coeurdessciences.uqam.ca/wp-content/uploads/lg_Faculte-sciences-interne-COUL-1.jpg)
a été inspectée. Aucun fichier maître vectoriel officiel accessible n'a été
obtenu. La reconstruction en tracés natifs est donc explicitement
**approximative**; voir la
[provenance et les limites](../../../assets/branding/FACULTY_SCIENCE_PROVENANCE.md).
La comparaison du rendu Manim avec la référence donne une intersection sur
union du premier plan de 98,86 % et une erreur RGB moyenne de 1,246/255.
Ces mesures ne constituent pas une approbation institutionnelle. Le chargement
SVG utilise un fichier temporaire privé pour éviter une collision entre deux
rendus simultanés; un test concurrent reproduit et protège ce cas.

La [référence AudioEye](https://www.audioeye.com/fr/color-contrast-checker/)
indique 4,5:1 pour le contraste normal et 7:1 pour le contraste renforcé.
Les rapports ci-dessous sont calculés localement par luminance sRGB; ils ne
sont pas présentés comme une certification du site AudioEye.

| Usage pédagogique | Couleur sur blanc | Rapport |
|---|---|---:|
| Texte principal | `#18212B` | 16,26:1 |
| Accent et titres | `#185A85` | 7,39:1 |
| Erreur, avec indication textuelle | `#A12622` | 7,46:1 |
| Correction, avec indication textuelle | `#216E39` | 6,26:1 |

Les combinaisons avec les panneaux teintés sont également testées au seuil
4,5:1. Les couleurs historiques de la signature sont préservées; elles ne
servent pas de texte pédagogique. Le sens des corrections est renforcé par
les mots, formules et encadrés, et ne dépend pas uniquement de la couleur.

Les correspondances du catalogue ont été comparées aux scènes, aux exemples
guidés et aux sections actives des deux livres. Un renvoi ciblé signifie une
correspondance de notion, pas une couverture complète des exercices. Les
renvois par chapitre ou transversaux sont conservés quand une section précise
n'est pas justifiée. Exemples : vidéo 15, manuel §§ 5.2–5.4 et cahier
§§ 5.1–5.3; vidéo 43, § 2.2 des deux documents; vidéo 37, complément
transversal. La banque fournit les références bibliographiques et distingue
les études effectivement lues du contexte consulté uniquement par résumé.

## Rendus de référence

Tous les chemins de cette section sont relatifs à la racine du dépôt.
Les livrables et les preuves générées restent dans `review_artifacts/`, ignoré
par Git. Les rendus initiaux et l'essai intermédiaire sont conservés; **la
version à examiner est `final_v2`**.

| Vidéo | Prévisualisation finale | Durée | Format |
|---|---|---:|---|
| 15 | `review_artifacts/chapter_pilot/2026-10-15/final_v2/15/media/videos/480p15/15_chapter_pilot_silent.mp4` | 271,467 s | 854 × 480, 15 i/s, sans audio |
| 43 | `review_artifacts/chapter_pilot/2026-10-15/final_v2/43/media/videos/480p15/43_chapter_pilot_silent.mp4` | 130,600 s | 854 × 480, 15 i/s, sans audio |

Empreintes SHA-256 des fichiers réellement rendus :

- 15 : `ec057d46ad63d35a869d5c48d3c03d8006e1b8670faf178757ca10f59a930b20`
- 43 : `091b3f39c353c08cdcc182d90b58d278fe88a5d0206233641f7b74f1933adb1a`
- Catalogue PDF : `97d538edcc875786e68bf436fc3e86cc01cba1bc3641d63bcb7a7de8f7ba3520`

Le PDF est `review_artifacts/teaching_navigation/catalogue/catalogue-videos.pdf`.
Chaque dossier vidéo contient `STATUS.json`, `ffprobe.json`, les empreintes
des entrées, le texte de narration prévu, les cartes horodatées, un index des
images encodées et les planches de contrôle. Les empreintes d'entrée finales
ont été comparées aux fichiers actuels. Les temps de narration de ces rendus
muets ne prédisent pas les durées de la synthèse vocale réelle.

## Relectures indépendantes et corrections

Trois agents ChatGPT distincts ont reçu le matériel rendu et le catalogue,
selon trois rôles. Ils n'ont pas consulté les rapports des autres avant leur
avis initial. Ce sont des simulations de relecture, **pas des observations
d'étudiants réels ni une preuve d'apprentissage**.

- [Bases algébriques fragiles](review_weak_algebra.md) : narration annonçant
  une courbe absente de l'image, et restrictions révélées après simplification.
- [Application mécanique des règles](review_mechanical_rules.md) : contrôle
  du raisonnement, des domaines et de la correspondance avec les sections.
- [Révision rapide](review_quick_revision.md) : orientation, lisibilité,
  cohérence du plan et consultation du catalogue.

Les rapports conservent l'avis initial et ajoutent une vérification finale
avec les empreintes des nouveaux fichiers. Ils détaillent les planches,
images natives, textes et pages réellement inspectés. Les 119 images encodées
échantillonnées couvrent les deux ouvertures, les huit cartes, les étapes
pédagogiques et les fins; elles ne représentent pas chaque image des vidéos.

Corrections corroborées et vérifiées sur la version finale :

1. Le plan reste aligné lors du passage en gras de sa plus longue ligne. Les
   huit cartes finales ont été revues individuellement, par exemple vidéo 15
   à 6,300 s, 29,233 s, 52,567 s et 72,900 s.
2. Dans la vidéo 43, les restrictions sont visibles à 61,443 s et 79,710 s,
   avant les égalités simplifiées à 65,310 s et 83,443 s. Le récapitulatif à
   124,443 s commence aussi par les valeurs interdites de l'expression initiale.
3. La narration écrite de la vidéo 15 demande désormais explicitement un
   croquis sur papier dans les deux exemples concernés; elle ne prétend plus
   qu'une courbe est affichée. La vérification porte sur le texte prévu et
   les images à 134,177 s et 196,243 s, pas sur un audio absent.

Aucun nouveau défaut mathématique, d'orientation ou de lisibilité corroboré
n'est resté ouvert dans ce périmètre échantillonné. Les suggestions facultatives
des rôles restent des suggestions, notamment les horodatages de navigation,
explicitement exclus du pilote par le brief.

## Validation et limites d'acceptation

| Contrôle | Résultat et portée |
|---|---|
| Syntaxe et vérification des sources | Réussis; `git diff --check` propre. |
| Tests vidéo ciblés | 108 tests et 36 sous-tests; autre ensemble d'intégration : 70 tests et 14 sous-tests. |
| Régressions finales | 10 tests de signature, dont le nouveau cas concurrent; 50 tests de révision après le contrôle par identités stables. Ces relances recouvrent une partie des ensembles précédents. |
| Livre et catalogue | `make verify` : 64 tests; 17 chapitres et 126 sections alignés; sorties générées à jour. |
| Compilation LaTeX | Compilateur intégré et `pdflatex` réussis; trois pages; aucun avertissement de débordement; aucune annotation PDF. |
| Inspection du PDF | Les trois pages rasterisées ont été examinées; 01–43 présents une fois dans l'ordre. |
| Rendus effectifs | Les deux prévisualisations finales sont encodées et lisibles par `ffprobe`; Manim 0.19.0. |
| Inspection d'images encodées | Réussie sur les 119 images échantillonnées; aucune sortie de marge détectée aux états contrôlés. |
| Synchronisation logique | Tests du cycle narration/maintien/disparition réussis avec une horloge simulée; transitions écrites présentes. |
| Synthèse vocale réelle | **Bloquée : identifiants Azure absents.** Profil existant conservé, aucune voix substituée. |
| Lecture continue en mouvement | **Non effectuée.** L'inspection d'images fixes ne la remplace pas. |
| Écoute et synchronisation audiovisuelle réelle | **Non effectuées.** Nécessitent les rendus narrés. |
| Validation institutionnelle de la signature | **En attente.** Reconstruction approximative identifiée. |
| Acceptation du pilote et déploiement élargi | **En attente de revue humaine.** Aucune publication ni livraison Drive. |

La seule alerte des tests ciblés est la dépréciation préexistante de
`pkg_resources` dans `manim_voiceover`. Aucun contrôle de base d'un autre
projet n'a été désactivé. Le runtime de travail est
`/tmp/math-final-review-venv/bin/python`; l'environnement `.venv-review`
local ne terminait pas son import Manim.

Pour reproduire le catalogue :

```sh
python3 books/mat0339/scripts/video_map.py --write
make -C books/mat0339 verify
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=review_artifacts/teaching_navigation/catalogue books/mat0339/curriculum/catalogue-videos.tex
```

Les scripts de contrôle ponctuels `render_chapter_pilot.py` et
`extract_chapter_review.py` sont conservés avec les preuves locales dans
`review_artifacts/chapter_pilot/2026-10-15/`. Ils produisent explicitement des
prévisualisations muettes, pas des livrables narrés. La reprise de l'acceptation
nécessite le rendu avec le service et le profil existants, puis l'écoute
complète, la lecture en mouvement et la validation de la synchronisation.

Les fichiers sources de cette tâche sont destinés à un checkpoint Git local
limité à ces modifications. Les médias générés et les photographies sans
rapport avec ce pilote n'en font pas partie. Aucun push n'est prévu, conformément
à l'exclusion de publication dans le brief.
