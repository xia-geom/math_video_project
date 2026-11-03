# MAT0339 — lot distinct de capsules 66–73

**Origine : audit du 1 novembre 2026.** Les huit capsules 66–73 sont séparées
dans une proposition de modification en brouillon, dépendant de la branche de
la PR #27. La PR #27 conserve les capsules 44–65, leurs améliorations et la
correction vérifiée de la transition de 48. Son [suivi d’audit](../2026-11-01/AUDIT.md)
et son registre sont hérités sans modification dans cette branche.

Le lot distinct contient les huit scènes et notices, les huit entrées du
catalogue, les correspondances avec le livre, les index générés et les attentes
de tests portant sur le catalogue étendu. Les identités, classes publiques,
prérequis et numéros existants sont conservés. La dépendance entre propositions
est réelle : 66 utilise le prérequis 47, 72 utilise 53 et 54, et 73 utilise 56.

## Provenance des preuves

Ce document et le [registre extrait](verification.json) présentent **des preuves
historiques**, sans annoncer de nouveaux tests ou rendus après séparation.
Les résultats des contrôles exécutés sur les branches séparées sont consignés
dans des rapports distincts.

Le [registre original complet](https://github.com/xia-geom/math_video_project/blob/340d438f954bcee1cefbbed951ea4187aa600d94/reports/error_capsules/2026-11-01/verification.json)
et l’[audit combiné original](https://github.com/xia-geom/math_video_project/blob/340d438f954bcee1cefbbed951ea4187aa600d94/reports/error_capsules/2026-11-01/AUDIT.md)
restent accessibles au commit immuable `340d438f954bcee1cefbbed951ea4187aa600d94`.
L’extrait conserve sans modifier leurs valeurs les huit fiches de capsules,
leurs références de relecture indépendante, les contrôles de syntaxe concernés
et les deux encodages remplacés de 69 et 70.

Les 214 états de construction et 133 images inspectées figurant dans ces huit
fiches appartiennent à l’audit d’origine. Les signatures comprennent le
catalogue entier à 73 entrées et toutes les autres entrées déclarées. Elles
ne sont pas recalculées pour transformer une preuve historique en nouveau
résultat. Les mentions « current » et « all30 » conservées décrivent
uniquement l’audit combiné. Les chemins d’artefacts sont ceux du travail
d’origine; les médias et caches ne sont pas ajoutés à Git.

Les totaux combinés de 254 tests du cours, 64 tests du livre et 30 rendus
silencieux restent des résultats de cet audit original. Ils ne sont pas
réattribués à cette extraction de huit capsules. Les preuves de livraison
mixte et du catalogue PDF restent consultables dans le registre intégral.

L’[analyse de complémentarité](gap-analysis.json) est déplacée **octet pour
octet** depuis le commit d’origine. Elle documente l’examen des 65 entrées
antérieures, les 14 sujets envisagés et les six propositions non retenues.
Ses chemins, formulations et états de livraison décrivent le travail avant
séparation; ce n’est pas un constat nouveau sur la branche. Aucun sujet
supplémentaire n’est implémenté par cette opération.

## Huit diagnostics conservés

| Capsule | Objectif et hypothèse essentielle | Repères du livre |
|---|---|---|
| 66 | Conserver la positivité de chaque argument lors d’une condensation de logarithmes; filtrer les solutions candidates. | Manuel 6.4, 6.8; cahier 6.4B |
| 67 | Distinguer fonction réciproque et inverse numérique d’une valeur, avec leurs domaines propres. | Manuel 3.5; cahier 3.5A, prolongement 3.5C |
| 68 | Distinguer composante signée, projection vectorielle et longueur; vérifier le résidu perpendiculaire et le vecteur de direction non nul. | Manuel 9.4, 9.7; cahier 9.7A–B |
| 69 | Compter « au moins un » par complément et le distinguer d’« exactement un »; préciser répétition et zéro initial. | Manuel 7.6, 7.9; cahier 7.6A |
| 70 | Inclure le coût dans chaque gain net et distinguer espérance et résultat garanti. | Manuel 8.6, 8.9; cahier 8.6A–C |
| 71 | Distinguer région admissible non bornée et objectif non borné; prouver atteinte, absence ou unicité de l’optimum. | Manuel 13.4, 13.7; cahier 13.4B et synthèse S2, transferts |
| 72 | Distinguer demi-période et période à partir d’extrema explicitement consécutifs. | Manuel 17.7–17.8; cahier 17.7A et synthèse S1 |
| 73 | Appliquer la décroissance exponentielle à l’écart à l’équilibre; contrôler les seuils accessibles. | Manuel 6.8; cahier 6.8C, adaptations |

Les notices distinguent exemples repris et adaptations. Chaque scène conserve
son objectif, ses prérequis, son texte français, un autocontrôle distinct,
une pause de réflexion de six secondes et sa correction.

La référence intégrée du livre reste l’édition du 10 octobre 2026 au commit
`4d451c37d483d763e33683a7fb683d1e0fdde62d`. L’audit avait consulté séparément
la révision du 17 octobre au commit `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`,
dans la PR #29 alors non fusionnée. En 72, la consécutivité des extrema est
explicitement posée; la notice distingue cette clarification du texte intégré.
Cette séparation ne modifie aucun chapitre du livre.

## Statut de revue

Les deux propositions restent **en brouillon**. Les nouvelles entrées gardent
le statut `authored` et le catalogue garde `release_ready: false`. Les preuves
historiques portent sur des aperçus silencieux et des échantillons d’images;
elles ne certifient ni chaque image intermédiaire ni un visionnage continu.
Synthèse vocale, écoute, durée narrée, visionnage humain continu, résolution
finale et approbation de diffusion restent à accomplir. Aucune vidéo n’est
publiée à l’occasion de cette séparation.

## Validation après séparation

Voir les [résultats réellement exécutés sur cette branche](../2026-11-01-split/BATCH_66_73.md), distincts des preuves historiques ci-dessus.
