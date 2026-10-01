# Deux capsules UQAM — audit et brief de refonte

**30 septembre 2026 — audit des sources et préparation du montage.**

Base inspectée : `main`, commit `4bf45e080d22e069f541f669f4cc1cb2ba283890`. Ce document transforme les retours éditoriaux en modifications précises et en critères de réception. **Il ne signifie pas que les scènes ont été modifiées ou que de nouveaux MP4 ont été produits.** Les fichiers vidéo commentés n'ont pas été relus intégralement pendant cet audit; les observations de rendu provenant des commentaires sont distinguées des constats dans le code.

Périmètre : `miscellaneous/bac_sciences_ouvertures_fr/` et `miscellaneous/bac_math_uqam_fr/`. Le film long sur les cheminements, les cours, la voix partagée et les archives restent hors périmètre des modifications.

Sources photographiques : [catalogue vérifié et réserves d'utilisation](../../../assets/uqam_promo/PHOTO_CANDIDATES.md). Les identifiants P01–P10 et M01–M02 ci-dessous renvoient à ce catalogue.

## 1. Ce qui doit changer en priorité

1. **Raconter un parcours plutôt qu'enchaîner des images institutionnelles.** Une activité mathématique compréhensible, une ouverture vers d'autres domaines, puis un diplôme clairement expliqué dans la première capsule. Dans la seconde : exigence, accompagnement, recherche, vie à Montréal.
2. **Corriger le texte réellement prononcé.** Dans la capsule maths, une partie du texte apparent est remplacée à l'importation par `promo_beats.py`. STATQAM est nommé, mais sa description n'est pas prononcée par les unités effectives.
3. **Changer les contrôles avec le scénario.** Les anciens tests défendent une capsule de vingt secondes sans baccalauréat, la présence du portrait supprimé et une conclusion sans photo. Ils doivent vérifier les nouvelles demandes et la lisibilité, pas figer les anciens choix.

La durée maximale de **30 secondes concerne seulement `bac_sciences_ouvertures_fr`**. La capsule maths conserve son format plus long; son builder vérifie actuellement une durée de 60 à 90 secondes.

## 2. Couverture de tous les commentaires

Les repères horaires désignent les versions commentées. Pour la nouvelle version, retrouver la scène par son sens et enregistrer les nouvelles bornes dans la timeline; ne pas appliquer aveuglément les anciens horaires.

| Repère | État constaté dans les sources ou retour reçu | Modification et réception attendues |
|---|---|---|
| Sciences, 0:05 | `classroom_math.jpg`, source liée à une compétition; impression de surveillance signalée | Retirer de cette capsule. Examiner P02 ou obtenir une activité récente via P01. Pas de salle d'examen ni de mise en scène d'une surveillance. |
| Sciences, 0:13 | `research_math.jpg` utilisé pour illustrer les ouvertures; groupe aligné jugé incompréhensible | Retirer de cette séquence. Utiliser une interaction autour d'un ordinateur ou une transition graphique simple entre les domaines. Pas de remplacement par un autre groupe posé. |
| Sciences, 0:17 | La mention du baccalauréat est absente et interdite par `project.py` | Réintroduire le baccalauréat en sciences avec le mécanisme majeure + certificat ou mineure. Ne pas faire croire que la majeure seule est le bac. |
| Sciences, 0:21 | La conclusion actuelle se limite à « Plusieurs horizons, à l'UQAM » | Retenir « Plusieurs horizons à l’UQAM : une formation personnalisée pour bâtir votre avenir. » La narration peut porter la phrase entière; l'écran peut la distribuer en lignes courtes. |
| Sciences, durée | Storyboard de 20 secondes, acceptation de 18 à 22 secondes | Cible de travail : 29 secondes, transitions et fin comprises; export final de 30 secondes maximum, sans couper la voix. |
| Sciences, musique | `music` vaut `null`; pas de mixage dans ce builder | Préparer une variante avec musique instrumentale entraînante mais discrète, source et droits documentés; conserver aussi la voix seule. Le choix musical reste à faire, aucune piste n'est approuvée par ce brief. |
| Maths, début | Accroche actuelle différente | Prononcer exactement : « À l'UQAM, faites des maths de haut niveau dans une université chaleureuse et à votre écoute ! » Éviter d'afficher toute cette phrase en un seul bloc. |
| Maths, 0:10 | Portrait et nom de Lisa Berger encore utilisés, fichier encore requis par le builder et les tests | Supprimer du film le portrait et son cartouche. Privilégier une interaction étudiante, P02/P03 ou photo d'archives appropriée; ne pas attribuer un nom ou un statut inventé aux personnes. Conserver l'ancien fichier pour les builds historiques. |
| Maths, 0:21 | « approche de la Faculté » et « dans les concentrations » subsistent; le milieu est devenu « accompagner les apprentissages » | Supprimer les trois petites explications secondaires sous « petits groupes », « travaux pratiques », « travail supervisé », y compris la formulation intermédiaire actuelle. Garder des intitulés lisibles, pas des sous-légendes remplacées par d'autres. |
| Maths, 0:24 | L'ancien premier écran CIRGET/LaCIM a déjà été simplifié dans `main`; séquence recherche encore en deux étapes | Ne pas réintroduire les acronymes dans le premier écran. D'abord montrer la possibilité de recherche; ensuite présenter les trois centres sur un seul écran stable. La suppression demandée ici n'est pas une interdiction de nommer CIRGET/LaCIM plus tard. |
| Maths, 0:33 | STATQAM existe déjà dans les cartes et dans la narration effective, mais sans phrase descriptive prononcée | Ajouter effectivement « STATQAM développe la recherche en statistique et en science des données. » Utiliser P06 pour le sens exact. |
| Maths, « Deux portes d'entrée » | La source récente dit déjà « Trois domaines » | Utiliser « Trois portes d’entrée vers la recherche », avec CIRGET, LaCIM et STATQAM. Ne pas confondre ces portes avec des voies d'admission. |
| Maths, 0:44 | « mentorat par les pairs » subsiste | Remplacer à l'écran et dans la voix par « le mentorat par les étudiants plus avancés ». Réorganiser la ligne longue plutôt que réduire excessivement la police. |
| Maths, fin | `act_close` ne contient pas de photo de Montréal | Ajouter M01 ou M02 derrière la conclusion, après validation du fichier, avec un voile séparé qui garde le texte opaque et lisible. Ne pas estomper le texte en appliquant l'opacité au groupe entier. |

Toutes les cases de mise en œuvre restent **à réaliser et à vérifier**; les formulations « déjà » décrivent uniquement la base inspectée, pas de nouvelles modifications de ce commit.

## 3. Constats techniques au-delà des commentaires

### Confirmés à la lecture des sources

- **Deux sources de narration dans la capsule maths.** La boucle sur `NARRATION_BEATS` remplace `NARRATION_SEGMENTS` pour recherche, Montréal et conclusion. Modifier uniquement la longue description initiale du centre ne change donc pas le résultat. Conserver une seule source éditoriale effective et vérifier les textes transmis au service vocal et au SRT.
- **Le budget de temps sciences peut s'allonger.** La scène réserve le maximum entre la durée du plan et la durée de la voix avec marge. Changer simplement `target_seconds` en 30 ne garantit pas un film de 30 secondes. Mesurer d'abord la narration, réserver la fin, puis adapter les pauses et le texte; conserver le rejet d'un dépassement.
- **La musique ne s'active pas avec une valeur JSON.** Le builder ne dispose pas du mixage correspondant et inscrit encore `music: None` dans son manifeste. Brancher explicitement le mixage et enregistrer la configuration réellement utilisée. Une piste musicale seule ne doit jamais valoir preuve de narration Azure.
- **Le cadre photo sciences est dimensionné par la largeur seulement.** Cela fonctionne pour les images actuelles, mais peut découvrir le fond avec un panorama plus large. Utiliser le principe de remplissage/recadrage déjà présent dans `tools/uqam_video_review.py`, avec contrôle du point d'intérêt.
- **Le contrôle de résolution sciences lit les dimensions déclarées.** Le contrôle compare une empreinte et un en-tête JPEG, puis les dimensions écrites dans le JSON; il ne décode pas les dimensions. Vérifier les pixels réels, puis la taille utile après recadrage. Ne pas transformer une petite image en « haute résolution » en modifiant ses métadonnées.
- **L'inventaire d'assets est périmé sur certains statuts.** `SOURCES.md` indique notamment des fichiers « missing » que l'arbre Git actuel contient, comme `campus_central_uqam.jpg` et `bibliotheque_sciences_2026.jpg`. Régénérer l'inventaire depuis les fichiers contrôlés; ne pas annoncer leur absence à partir de ce seul document.
- **Des tests protègent désormais des décisions obsolètes.** `test_uqam_ouvertures.py` impose vingt secondes et interdit « baccalauréat »; `test_uqam_promo.py` attend Lisa Berger et interdit une photo pleine page dans la conclusion. Remplacer ces attentes par des assertions du nouveau brief, tout en conservant les contrôles de source, de sous-titres et d'intégrité.

### Risques à tester dans le rendu, non constatés sur un nouvel export

- Les fondus simultanés du groupe entier peuvent produire un creux de luminosité et superposer deux textes. Séparer photographie, voile, crédits et texte : faire entrer le nouveau fond au-dessus de l'ancien encore opaque, puis retirer l'ancien; ne pas superposer les deux messages principaux.
- Le repère « aperçu muet » de sciences est ajouté avant les photos plein écran. Vérifier qu'il reste au premier plan sur chaque plan; l'ordre d'ajout seul ne suffit pas à constituer une preuve de visibilité.
- Les longues nouvelles lignes (« étudiants plus avancés », conclusion personnalisée) peuvent déborder ou empiéter sur les sous-titres. Tester les objets effectivement dessinés et le recadrage final, pas seulement des limites en nombre de caractères.
- Les cartes de recherche doivent rester lisibles pendant les descriptions. Ne pas les retirer dès la fin d'une courte animation ou d'une seule phrase d'introduction.

## 4. Nouveau montage proposé — sciences

**But : comprendre un choix de formation, pas mémoriser une liste administrative.** Cinq séquences de sens, mais pas nécessairement cinq photos différentes. Un même fond peut rester pendant l'explication du diplôme.

| Temps de travail | Idée principale | Traitement visuel |
|---|---|---|
| 0–3 s | Les maths ouvrent des portes | Identité UQAM immédiate; une accroche courte sur une image de campus ou une activité clairement située. |
| 3–10 s | Une majeure en maths ou statistique | Photo d'activité P02 ou archives; mettre en évidence la majeure et le parcours type à temps plein, sans évoquer un bac obtenu en deux ans. |
| 10–18 s | Une formation complémentaire | Interaction sur ordinateur au campus montréalais, ou progression typographique sobre. Présenter communication, finance, économie et informatique en deux lignes, pas quatre nouvelles photos successives. |
| 18–22 s | Un baccalauréat en sciences par cumul | Garder le contexte précédent. Faire apparaître le résultat après la majeure et le certificat/mineure; pas de diagramme administratif chargé. |
| 22–29 s | Votre avenir à l'UQAM | Conclusion personnalisée et appel à consulter le programme; garder le dernier écran au moins deux secondes après la fin de la parole, dans le budget global. |

Les bornes sont un **objectif de montage**, non des durées mesurées. Il faudra déplacer les bornes si les phrases enregistrées l'exigent, sans dépasser le maximum final.

### Proposition de narration à tester

> Les maths ouvrent des portes. Après deux ans à temps plein en mathématiques ou en statistique, vous pouvez obtenir une majeure. Combinez-la à un certificat ou une mineure, en communication, finance, économie ou informatique, pour obtenir un baccalauréat en sciences. Plusieurs horizons à l’UQAM : une formation personnalisée pour bâtir votre avenir.

Cette proposition remet le mécanisme de cumul dans la phrase plutôt que d'ajouter isolément « baccalauréat ». Elle reste à valider avec le programme, notamment pour le choix et les intitulés des compléments. La durée de deux ans est un parcours type, non une garantie individuelle. Les quatre domaines sont des exemples d'ouverture, non une promesse d'admission automatique dans un autre programme.

Sources académiques consultées en complément du registre du dépôt : [majeure en mathématiques, note et grade par cumul](https://etudier.uqam.ca/programme/majeure-mathematiques) et [présentation des programmes de premier cycle du Département](https://math.uqam.ca/programmes/premier-cycle/). Le PDF d'accueil original n'a pas été rouvert ici; sa lecture antérieure est documentée dans [le registre du projet](../../../miscellaneous/bac_sciences_ouvertures_fr/sources/accueil_septembre_2026.md).

### Musique : une option, pas un obstacle au premier bon montage

Choisir une piste sans paroles, avec source, licence et preuve d'utilisation conservées. Prévoir des fondus de début/fin et une baisse de niveau pendant la voix; vérifier à l'écoute sur téléphone. Ne pas réutiliser automatiquement le piano du film long : il n'a pas été évalué comme musique entraînante pour cette capsule. Ne pas importer le renderer du film long pour profiter de son mixage; réutiliser une fonction isolée et testée seulement si utile. Livrer une variante voix seule et une variante mixée pour comparaison; ne pas changer la musique de l'autre film sans demande.

## 5. Nouveau montage proposé — maths

Cible éditoriale proposée : environ 70–80 secondes, à vérifier avec la voix réelle; conserver le garde-fou existant de 60–90 secondes tant que le format n'est pas redécidé.

**Ouverture.** Prononcer l'accroche demandée. Montrer un environnement réellement accueillant, puis une interaction étudiante plutôt que remplacer un portrait par un autre portrait. À l'écran, deux idées courtes suffisent : « Des maths de haut niveau » et « Une université à votre écoute ».

**Apprendre.** Garder « Échanger · Pratiquer · Progresser », les trois faits simplifiés et de l'espace libre. Les précisions administratives restent dans les sources, pas en petits caractères gris.

**Découvrir la recherche.** Un premier plan stable sur les possibilités de stages, sans grille d'acronymes. Puis un seul écran « Trois portes d'entrée vers la recherche » : CIRGET — géométrie et topologie; LaCIM — combinatoire et informatique mathématique; STATQAM — statistique et science des données. Laisser les trois domaines visibles pendant leur présentation; mettre en valeur l'élément prononcé sans changer de photo à chaque nom. L'ajout d'une photo STATQAM n'est pas une condition pour obtenir une bonne séquence.

**Être accompagné.** Employer la formulation demandée sur les étudiants plus avancés dans les deux canaux. Une photo d'accueil et un seul petit bloc sur la bibliothèque suffisent; P04 ne doit pas être légendé comme preuve d'un programme spécifique de mentorat.

**Vivre à Montréal et conclure.** Éviter de répéter trois messages d'accueil déjà traités. Conserver l'information de lieu utile, puis terminer sur M01/M02 avec un voile et un appel à l'action unique, stable. Ne pas présenter le panorama comme une vue du campus. Garder l'éventuel logo officiel soumis aux validations existantes.

## 6. Ordre de réalisation et fichiers concernés

| Lot | Action | Fichiers à modifier lors de l'implémentation |
|---|---|---|
| 1 — images | Choisir les fichiers exacts, vérifier les droits et recadrages, régénérer les inventaires | `assets/uqam_promo/`; `fetch_uqam_promo_assets.py`; inventaires générés |
| 2 — sciences | Mettre à jour le schéma, le récit, les durées, les transitions, le cadrage et le mixage optionnel | `project.json`, `project.py`, `bac_sciences_ouvertures_fr_scene.py`, `build.py`, `tests/test_uqam_ouvertures.py` |
| 3 — maths | Modifier la narration effective, remplacer le portrait, simplifier les textes, stabiliser recherche et conclusion | `promo_beats.py`, `bac_math_uqam_fr_scene.py`, préflight de `build_release.py`, `tests/test_uqam_promo.py` |
| 4 — cohérence | Mettre à jour la revue et les descriptions du format après la modification réelle | `scripts/uqam_revision/render_review.py`, README des projets, `miscellaneous/uqam_promotion.json`, références actives au format vingt secondes |
| 5 — réception | Tester, rendre un aperçu sans coûts vocaux, puis la version narrée autorisée et inspecter l'export | Scripts de revue existants, rapports datés, médias générés hors Git |

Ne pas utiliser les anciens scripts de migration pour réappliquer une ancienne version. Ne pas déplacer les projets ni fusionner leurs moteurs. Les binaires historiques et les anciens rapports restent conservés. Les nouveaux médias et caches ne sont pas des sources à committer.

## 7. Critères de réception — à cocher sur les nouveaux fichiers

- [ ] Tous les commentaires du tableau ont un résultat vérifiable dans la nouvelle vidéo et sa narration; une recherche dans le code ne tient pas lieu de preuve finale.
- [ ] Sciences : durée mesurée par `ffprobe` de 30 secondes maximum, voix non tronquée et fin lisible. Déclarer séparément la durée de l'aperçu sans voix et celle du rendu Azure.
- [ ] Photos : provenance réelle, crédit exact, dimensions décodées, recadrage utile et empreinte enregistrés; pas d'image de Laval présentée comme Montréal, de visiteurs du secondaire présentés comme étudiants du bac ou de Getty traité comme librement réutilisable.
- [ ] Sciences : aucune utilisation des deux photos rejetées dans le nouveau montage. Maths : plus de portrait/cartouche Lisa Berger; anciens fichiers conservés hors scénario actif.
- [ ] Recherche : trois centres sur un écran stable; description de STATQAM présente dans les unités réellement synthétisées et dans les sous-titres, pas seulement dans une constante écrasée.
- [ ] Anciennes mentions grisées et « mentorat par les pairs » absentes du texte affiché et de la voix effective; nouvelle ligne de mentorat sans débordement.
- [ ] Textes et sous-titres contrôlés dans l'export : deux lignes de sous-titres maximum, absence de collision, typographie lisible sur petit écran; ne pas résoudre un trop-plein uniquement en diminuant les polices.
- [ ] Transitions inspectées au début, au milieu et à la fin de chaque fondu, puis en lecture continue : pas de trou noir/blanc, de texte doublé, de visage coupé ou d'image incompréhensible. Garder les plans significatifs environ quatre secondes ou plus lorsque le récit le permet.
- [ ] Montréal : texte entièrement lisible sur le voile et crédit correct; dernier appel à l'action tenu au moins deux secondes après la dernière parole, sans dépasser les limites de durée.
- [ ] Musique éventuelle : aucun écrasement de la voix, pas de saturation, début/fin propres, source et licence consignées. Les résultats automatiques de niveau ne remplacent pas l'écoute complète.
- [ ] Aperçu sans narration clairement identifié au premier plan; aucune musique seule ni absence d'erreur ne doit le faire qualifier de rendu narré.
- [ ] Rapport séparant tests exécutés, rendu réel, inspection des images encodées, écoute complète et approbation de diffusion. Ne pas désactiver des contrôles pour obtenir un résultat vert.

## 8. État de ce travail

Réalisé : consultation des sources publiques du catalogue; contrôle de la base GitHub; audit du scénario, des dépendances de narration, des garde-fous et des tests; rédaction du plan de montage et de réception. La photographie M02 a été affichée et examinée; les autres fichiers candidats n'ont pas reçu d'inspection visuelle complète. La récupération réseau du dépôt dans le conteneur a échoué; la consultation et l'enregistrement passent par le connecteur GitHub.

Non réalisé : modification des scènes, intégration de nouveaux JPEG, choix d'une piste musicale, tests Manim, nouveaux rendus, nouvelle narration Azure, écoute complète et autorisation de diffusion. Ces étapes ne sont ni lancées en arrière-plan ni supposées terminées par la présence de ce document.
