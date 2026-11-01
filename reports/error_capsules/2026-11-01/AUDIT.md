# MAT0339 — audit conservé des capsules 44–65 et correction de 48

**Audit d’origine : 1 novembre 2026. Périmètre de la PR #27 après séparation :
capsules 44–65, avec la correction vérifiée de la transition de 48.** Les huit
capsules 66–73, leur extension du catalogue et leur analyse de complémentarité
sont examinées dans une proposition distincte dépendant de cette branche.

Ce document présente les éléments historiques pertinents de l’audit combiné.
Il **n’annonce pas de nouveaux tests ni de nouveaux rendus après séparation**.
Les résultats de validation des branches séparées figurent dans le
[rapport de séparation](../2026-11-01-split/PR27.md).

## Conservation et portée des preuves

L’[audit original complet](https://github.com/xia-geom/math_video_project/blob/340d438f954bcee1cefbbed951ea4187aa600d94/reports/error_capsules/2026-11-01/AUDIT.md)
et son [registre intégral](https://github.com/xia-geom/math_video_project/blob/340d438f954bcee1cefbbed951ea4187aa600d94/reports/error_capsules/2026-11-01/verification.json)
restent conservés au commit immuable `340d438f954bcee1cefbbed951ea4187aa600d94`.
L’[analyse de complémentarité du lot 66–73](https://github.com/xia-geom/math_video_project/blob/340d438f954bcee1cefbbed951ea4187aa600d94/reports/error_capsules/2026-11-01/gap-analysis.json)
reste également accessible dans ce commit; elle ne fait plus partie du périmètre
courant de la PR #27.

Le [registre extrait](verification.json) conserve sans modification des valeurs
les 22 fiches de capsules 44–65, la comparaison indépendante avant/après de 48,
les deux références d’audit de sources correspondantes, leurs contrôles de
syntaxe historiques et l’essai de rendu remplacé de 57. Les références aux
artefacts désignent les chemins de travail de l’audit original; ces médias et
caches ne sont pas ajoutés à Git. Leurs empreintes ne prouvent pas leur présence
dans une nouvelle copie du dépôt.

**Les signatures de rendu historiques contiennent le catalogue entier à
73 entrées.** Le catalogue réduit à 65 entrées a une autre empreinte. Même
lorsqu’une source de scène est inchangée, ces anciens rendus ne sont donc pas
des validations des entrées courantes de la branche séparée. Les mentions
« current » ou « all30 » conservées dans les fiches décrivent uniquement
l’audit combiné d’origine. Aucun résultat historique ni aucune empreinte n’a
été réécrit pour donner l’apparence d’une nouvelle exécution.

Les totaux combinés de 254 tests du cours, 64 tests du livre et 30 rendus
silencieux appartiennent à cet audit original. Ils ne sont pas réattribués au
périmètre réduit. Les preuves propres aux capsules 66–73 et les références
mixtes de livraison restent consultables dans le registre intégral.

## Sources du livre

Le manuel et le cahier intégrés sont l’édition du 10 octobre 2026, au commit
`4d451c37d483d763e33683a7fb683d1e0fdde62d`. L’audit avait consulté séparément
la révision du 17 octobre, commit `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`,
dans la PR #29 alors non fusionnée. Les anciennes pièces jointes ne fondent
pas ce contrôle. Cette séparation ne modifie aucun chapitre du livre.

Les lots 44–57 et 58–65 ainsi que les corrections du premier audit restent
dans la PR #27; voir l’[audit du 31 octobre](../2026-10-31/AUDIT.md).

## Correction conservée de la capsule 48

La scène utilise neuf personnes suivant les mathématiques : six femmes et
trois hommes. Dans l’ancien encodage, les 21 points exclus et les légendes
« 18 femmes » et « 12 hommes » réapparaissaient au début du fondu sortant,
aux images 408 et 410, soit 27,200 et 27,333333 secondes.

Le fondu avait été appliqué à un groupe temporaire, alors que les objets
retirés restaient membres de leurs groupes propriétaires. La correction
détache les points des groupes femmes/hommes et les deux légendes de leurs
groupes de population. Le fondu ne conserve ensuite que les neuf personnes
du groupe conditionnel. Les calculs et le texte parlé restent identiques.

Le registre conserve la fermeture indépendante de ce défaut, avec les
empreintes des deux vidéos et des quatre images avant/après. Cette preuve
historique porte précisément sur les deux instants déclarés; elle ne certifie
pas un visionnage continu. Le code corrigé et sa notice sont conservés dans
cette branche.

La relecture historique des 22 capsules portait sur les domaines, hypothèses,
cas limites, unités, calculs et scripts. Les autres sources 44–65 n’avaient
pas été modifiées sans défaut concret. Les corrections de transitions du
lot précédent sont conservées.

## Statut de revue

La PR #27 reste **en brouillon**. Les sources sont rédigées pour revue et le
catalogue conserve `release_ready: false`. Les preuves extraites concernent
des aperçus silencieux et des échantillons d’images, pas une acceptation
audiovisuelle narrée. Synthèse vocale, écoute, durée narrée, visionnage humain
continu, résolution finale et approbation de diffusion restent à accomplir.
Cette séparation ne publie aucune vidéo.
