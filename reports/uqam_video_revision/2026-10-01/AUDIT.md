# Audit des deux vidéos UQAM — 1er octobre 2026

**Décision : montage visuel accepté pour intégration ; diffusion finale non validée.** Les deux rendus examinés sont explicitement muets. La narration réelle, son alignement avec les sous-titres et une éventuelle musique ne sont pas validés par cet audit.

## Preuves examinées

- PR : #20, `fix/uqam-two-films-redesign-20260930`.
- Source effectivement rendue et testée : `36cbbe987d22b7d60f83628d1f21f885547d16fd`, confirmée par `tested_commit.txt` dans l’archive de contrôle.
- Exécution : [UQAM — two introductory films, run 36809812184](https://github.com/xia-geom/math_video_project/actions/runs/36809812184).
- Archive : `uqam-two-films-review.zip`, dossier `review_artifacts/uqam_ouvertures/` ; vidéos, images extraites des plans et transitions, chronologies, manifestes et `tests.xml`.
- Résultat du rapport JUnit : **60 tests, aucune erreur, aucun échec, aucun test ignoré**. Ces résultats proviennent du travail CI archivé, pas d’une nouvelle exécution locale après les ajouts documentaires.
- `two_films_checks.json` : sciences **29,00 s**, mathématiques **75,95 s**, contrôles de chronologie réussis ; `listening_review: not_performed`, `release_ready: false`.

L’examen visuel porte sur les images encodées fournies pour les plans et les transitions, confrontées aux textes et aux chronologies. Il ne remplace pas un visionnage avec la future piste sonore.

## Comparaison avec les commentaires

Les repères temporels des commentaires désignent les anciennes versions : les plans sont déplacés dans les nouveaux montages.

| Demande | Résultat vérifié |
| --- | --- |
| Sciences : maximum 30 secondes | Aperçu de 29,00 s ; il reste nécessaire de vérifier cette limite sur le futur fichier avec narration. |
| Sciences : supprimer la surveillance de concours | Remplacement par un atelier public de mathématiques : échanges autour d’une activité, crédit et contexte explicites. |
| Sciences : supprimer la photo de personnes alignées | Cette image n’est plus dans la capsule ; le parcours est expliqué directement par les écrans « Certificat ou mineure » et « Baccalauréat en sciences ». |
| Sciences : informatique puis diplôme | Informatique figure parmi les ouvertures, suivie de « Pour obtenir un baccalauréat en sciences ». Le montage conserve la distinction majeure + complément compatible, sans promettre que toute combinaison est admissible. |
| Sciences : conclusion personnalisée | « Plusieurs horizons à l’UQAM : une formation personnalisée pour bâtir votre avenir. » sur une photo d’accueil étudiant. |
| Sciences : rythme et transitions | Cinq étapes lisibles ; transitions de 0,75 s dans la chronologie ; conclusion de 19,5 à 29 s, dont une tenue finale déclarée de 2 s. |
| Mathématiques : introduction chaleureuse | La source de narration contient exactement la phrase demandée, de « À l’UQAM » à « à votre écoute ». L’écran d’ouverture en reprend une version courte. |
| Mathématiques : retirer le portrait et les petites mentions grisées | Absents des images du montage révisé ; remplacement par une scène d’échange et des formulations courtes. |
| Mathématiques : ralentir la recherche, ajouter STATQAM | Introduction séparée aux stages, puis trois cartes stables CIRGET / LaCIM / STATQAM. Les centres ne sont pas accumulés dans le précédent passage rapide. |
| Mathématiques : expliquer STATQAM | Texte parlé : « STATQAM développe la recherche en statistique et en science des données. » Il n’est pas présenté comme une association étudiante. |
| Mathématiques : mentorat | « Le mentorat par les étudiants plus avancés » dans le texte parlé, et formulation correspondante à l’écran. |
| Mathématiques : Montréal en fond | Photographie de Montréal sous un voile blanc distinct, texte foncé et crédit protégé. La photo figure effectivement dans le manifeste et les images finales. |

Aucun débordement manifeste ni collision entre texte et photographie n’a été repéré dans les images de contrôle examinées. Les crédits restent séparés du message principal. Le montage mathématique privilégie désormais le temps de lecture ; aucune limite de 30 secondes n’avait été demandée pour ce second film.

## Photographies et traçabilité

Les nouvelles photographies, leurs URL, crédits, empreintes et restrictions sont documentés dans `assets/uqam_promo/sources.json` et le script de récupération. Le relevé explicatif vérifié est [EDITORIAL_SOURCES.md](../../../../assets/uqam_promo/EDITORIAL_SOURCES.md).

L’atelier de 2019 ne doit pas être présenté comme un cours ordinaire ; l’accueil étudiant de 2025 ne doit pas être présenté comme une séance réelle de mentorat. La photo de Montréal est de Quintin Soloviev, sous CC BY 4.0, avec recadrage et voile signalés. Pour les images publiées par l’UQAM, l’autorisation formelle de republication reste à documenter avant diffusion.

## Limites et état des contrôles

Les travaux `UQAM — scoped source checks`, `UQAM — two introductory films` et `UQAM revision` sont réussis pour le commit rendu. Le travail global `smoke` est en échec : **ne pas présenter l’ensemble de la CI du dépôt comme vert**. Aucun contournement de protection de branche ni changement des tests globaux n’est autorisé par ce rapport.

Les deux ajouts de cet audit sont documentaires : ils ne modifient pas les sources vidéo du commit rendu. Les aperçus portent la mention « APERÇU MUET — VOIX NON INCLUSE ». L’intégration du code dans `main` ne constitue ni une approbation institutionnelle, ni une validation sonore, ni une publication des films.

Avant diffusion : produire la narration réelle selon la procédure du dépôt, écouter les deux films, vérifier la synchronisation et la durée finale de la capsule sciences, puis documenter les autorisations photographiques. La musique reste facultative et absente des aperçus examinés.
