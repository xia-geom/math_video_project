# MAT0339 — second audit des erreurs et lot 66–73

**Date : 1 novembre 2026.** Cet audit reprend les 22 capsules 44–65, corrige un défaut de transition restant dans 48 et ajoute huit capsules, 66–73. Les 30 prévisualisations silencieuses livrées ont été produites à nouveau avec le catalogue étendu. Le cours contient maintenant **73 entrées : 37 leçons principales et 36 compléments d’erreurs**. L’animation d’identité séparée porte le nombre de sources de scènes à 74.

Le [registre de vérification](verification.json) conserve les empreintes des sources, entrées de rendu, vidéos et images effectivement inspectées. L’[analyse de complémentarité](gap-analysis.json) documente les 65 entrées examinées pour choisir ce lot, 14 sujets proposés, leurs références et les six sujets laissés pour une prochaine sélection. La priorité est éditoriale; elle ne prétend pas mesurer la fréquence réelle des erreurs chez les étudiants.

## Sources du livre et portée

| Source | Version consultée | Statut au début de l’audit |
|---|---|---|
| Manuel et cahier intégrés à `main` | Édition du 10 octobre 2026, commit `4d451c37d483d763e33683a7fb683d1e0fdde62d` | Autorité intégrée |
| Révision éditoriale du livre | Édition du 17 octobre 2026, commit `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, PR #29 | Consultée séparément, non fusionnée |
| Base des capsules de cet audit | Commit `70be76cb3a222005ba2589c6bc3becd482b7f39c` | Sources 44–65 de départ |

Les anciennes pièces jointes ne sont pas utilisées comme édition courante. Le travail ne modifie pas le texte des chapitres du manuel ou du cahier. La carte des vidéos et son répertoire généré sont actualisés pour les nouvelles identités.

L’analyse de lacunes porte sur toutes les entrées du catalogue et sur les passages et scènes voisins des sujets envisagés. La nouvelle relecture détaillée des mathématiques et des scripts porte sur **44–65**, puis sur les huit nouvelles capsules. Elle ne constitue pas une nouvelle lecture exhaustive de toutes les pages du livre ni de toutes les 37 leçons principales.

Un point de provenance est traité explicitement dans 72 : la version intégrée du cahier ne précise pas partout que les extrema sont consécutifs. La révision en attente ajoute notamment « minimum suivant » et « maxima consécutifs ». La capsule énonce cette hypothèse comme une donnée nécessaire; sa notice distingue la clarification consultée de l’énoncé déjà intégré.

## Correction issue du second audit

### 48 — conserver le groupe de référence pendant le fondu

Le raisonnement utilise neuf personnes suivant les mathématiques : six femmes et trois hommes. Dans la vidéo précédente, les **21 points exclus** et les anciennes légendes « 18 femmes » et « 12 hommes » réapparaissaient au début du fondu sortant. Le défaut est visible aux images **408 et 410**, soit **27,200 s et 27,333333 s**. L’image contredisait donc momentanément la phrase « Les 9 personnes en maths forment le nouveau groupe ».

Le fondu avait été appliqué à un groupe temporaire, tandis que les objets supprimés restaient membres de leurs véritables groupes propriétaires. La correction retire les points des groupes femmes/hommes et les deux légendes de leurs groupes de population. Le nouveau fondu conserve uniquement les neuf personnes retenues. Deux relectures indépendantes des mêmes instants dans le nouveau fichier confirment la correction. Les calculs et le texte parlé restent identiques.

Les autres capsules 44–65 n’ont pas reçu de modification de source sans défaut concret. Le second examen a repris domaines, hypothèses, cas limites, unités, arguments parlés et cohérence avec les exercices. Il a également inspecté **107 images supplémentaires des vidéos antérieures**, distinctes des sélections du premier audit : 28 pour 44–57 et 79 pour 58–65. Cette exploration ne constitue pas un visionnage continu.

Les vérifications indépendantes incluent des calculs en fractions exactes, des énumérations finies, des preuves analytiques et, pour le cas ambigu des triangles, 976 configurations de paramètres. Aucun nouveau défaut mathématique n’a été trouvé dans ces 22 sources. Les corrections de transitions du lot précédent sont conservées.

## Huit capsules implémentées

*M = manuel; C = cahier. Les exemples de transfert sont identifiés comme adaptations, même lorsqu’ils s’appuient directement sur une méthode du livre.*

| Nº | Capsule et contrôle ajouté | Exemple principal et autocontrôle | Repères |
|---|---|---|---|
| **66** | **Condenser des logarithmes ne change pas le domaine.** Garder les conditions sur chaque argument, puis filtrer les candidats. | `ln(x−1)+ln(x+1)=ln8` impose `x>1`; parmi ±3, seule 3 convient. L’exercice distinct `ln(x−1)+ln(x+2)=ln12` garde `(−1+√57)/2`. | M 6.4, 6.8; C 6.4B |
| **67** | **Fonction réciproque ou inverse d’une valeur ?** Comparer opérations, domaines et contrôles. | Pour `f(x)=3x−5`, `f⁻¹(4)=3` tandis que `1/f(4)=1/7`. La réciproque est définie sur R, le quotient exclut 5/3. Autocontrôle `3x−7`, avec les deux compositions. | M 3.5; C 3.5A, prolongement C |
| **68** | **Une projection signée n’est pas une longueur.** Séparer nombre signé, vecteur projeté et norme. | Transfert : `u=(−3,2)`, `v=(2,0)` donne composante −3, projection `(−3,0)` et longueur 3. Autocontrôle du cahier : `u=(3,4)`, `v=(1,2)`; projection `(11/5,22/5)` et résidu perpendiculaire. | M 9.4, 9.7; C 9.7A–B |
| **69** | **Au moins un ne signifie pas exactement un.** Diagnostiquer le comptage par position marquée. | Transfert : codes de trois chiffres, répétition et zéro initial permis. Au moins un zéro : `10³−9³=271`; exactement un : `3×9²=243`. Autocontrôle binaire de longueur 8 : 255 contre 8. | M 7.6, 7.9; C 7.6A |
| **70** | **Espérance : gain net et résultat incertain.** Définir la variable et inclure les coûts dans toutes les issues. | Le jeu du cahier coûte 4 $ et verse 20 $ avec probabilité 0,1 : gains nets 16 $ ou −4 $, espérance −2 $. Autocontrôle original : dé équilibré, coût 1 $, versement 6 $ sur un six; espérance 0 sans gain nul garanti. | M 8.6, 8.9; C 8.6A–C, exemple B |
| **71** | **Région non bornée : l’optimum peut exister.** Étudier la direction de l’objectif et prouver son résultat. | Sur `x,y≥0`, `x+y≥2`, le minimum de `x+y` est 2 sur toute une arête; le maximum de `−x−y` est −2, tandis que `x+y` n’a pas de maximum. Transfert : minimiser `3x+2y` sous `x,y≥0` et `2x+y≥6` donne 9, uniquement en `(3,0)`. | M 13.4, 13.7; C 13.4B et synthèse S2, transferts |
| **72** | **Du maximum au minimum suivant : une demi-période.** Contrôler le caractère consécutif des extrema. | Marée : maximum 4,8 m à 3 h, minimum suivant 0,8 m à 9,2 h : `T=12,4 h`, amplitude 2 m et médiane 2,8 m. Autocontrôle : maxima consécutifs à 2, 10, 18 h, maximum 15 m et minimum 3 m : `T=8`, amplitude 6, médiane 9. | M 17.7–17.8; C 17.7A et synthèse S1, hypothèse explicitée |
| **73** | **Ce qui décroît, c’est l’écart à l’équilibre.** Retirer la température ambiante avant d’appliquer la demi-vie. | Adaptation `T(t)=20+60·2^(−t/10)` : après 10 min, T vaut 50 °C. Atteindre 40 °C prend `10 ln3/ln2≈15,85 min`. Autocontrôle `10+60·2^(−t/4)` : T(4)=40 et T=25 à 8 min. | M 6.8; C 6.8C, adaptations |

Chaque capsule possède une seule ouverture commune, un script français, une question de transfert, une pause de réflexion de six secondes et une correction distincte. Le statut du catalogue reste `authored` et `release_ready: false`.

### Complémentarité vérifiée

La capsule 47 explique déjà pourquoi le logarithme d’une somme ne se distribue pas; 66 traite une loi correcte utilisée après perte du domaine. La leçon 11 mentionne déjà que `f⁻¹` ne signifie pas `1/f`; 67 développe ce diagnostic par des opérations numériques, des domaines distincts et des contrôles différents. La leçon 20 traite l’union de deux événements; 69 ajoute la multiplicité variable créée par le marquage d’une position. La non-commutativité des matrices, déjà développée en 26, n’a pas été retenue comme nouveau sujet.

### Améliorations faites pendant la réalisation

- **66 :** graduations de droites numériques rendues explicitement noires après détection de leur invisibilité dans la première construction.
- **67 :** bijection et non-nullité présentées comme deux conditions distinctes; une réciproque peut parfaitement recevoir ou produire zéro.
- **68 :** calcul de la projection et contrôle du résidu répartis sur deux pages pour conserver la taille des caractères. La projection se fait sur la droite entière; `v≠0` est explicite, `u=0` reste permis.
- **69 :** correction divisée en deux pages lisibles; le point d’interrogation porte sur le comptage proposé `N`, et non sur l’égalité arithmétique vraie `3×10²=300`.
- **70 :** titre d’autocontrôle reformulé pour ne pas révéler l’espérance nulle; questions séparées sur l’espérance et sur un gain nul garanti.
- **71 :** prolongements visibles de la région non bornée et démonstration de l’arête optimale entière; la fenêtre du dessin ne devient pas une contrainte supplémentaire.
- **72 :** « suivant » et « consécutifs » explicites, cas d’extrema manqués traité, coefficient positif `A` nommé précisément.
- **73 :** isolation de l’exponentielle et résolution logarithmique séparées; intervalle `20<T(t)≤80` et domaine `t≥0` contrôlés avant d’accepter un seuil.

## Vérifications et limites exactes

| Vérification | Résultat |
|---|---|
| Sources et identité du cours | 73 entrées, 37 principales + 36 erreurs; 74 scènes avec l’identité séparée |
| Relecture mathématique et des scripts | 22 capsules existantes et huit nouvelles; chaque nouvelle capsule a une relecture indépendante |
| Constructions nouvelles | 9 scènes, 243 états distincts; zéro candidat de chevauchement ou de sortie du cadre |
| Constructions antérieures réutilisées | 21 scènes inchangées, 501 états; correspondance exacte des empreintes de source vérifiée |
| Rendus actuels | 30 aperçus silencieux, 854 × 480, 15 images/s; toutes les entrées de rendu correspondent aux fichiers courants |
| Inspection des fichiers encodés actuels | 267 pages complètes et 147 échantillons supplémentaires de mouvements, fondus ou réflexion : **414 images inspectées** |
| Décodage technique intégral | 30 fichiers décodés jusqu’au bout par FFmpeg, sans erreur |
| Tests du cours | 254 cas et 24 sous-tests; catalogue, routage, durées, provenance, disposition et politiques de workflows |
| Vérification du livre | 64 tests; renvois de sections et répertoires générés actualisés |
| Gardes publics et workflows | 14 tests et 5 sous-tests; six tests de politique et les cinq sous-tests sont déjà inclus dans les nombres du cours |
| Syntaxe et Ruff des scènes | Les 30 sources auditées passent; les quatre fichiers de tests modifiés conservent 13 diagnostics Ruff antérieurs, sans en introduire |
| Audit public | Historique des références récupérées et fichiers suivis, y compris les nouveaux fichiers indexés : zéro détection de secret; règles inchangées dans cette révision |

La première concaténation de 57 a échoué dans PyAV. L’essai est conservé et exclu de la sélection; un nouveau rendu sans modification de source a réussi, puis passé le décodage intégral. Les premières versions de 69 et 70 ont également été remplacées après les améliorations de leurs questions. Le manifeste sélectionne explicitement les fichiers courants; la présence d’un ancien MP4 ne vaut pas validation.

Les vidéos ont été rendues depuis la base Git accompagnée des modifications en cours. Le registre conserve donc **les empreintes de toutes les entrées**, et pas seulement le nom du commit de base. Les couples chemin/empreinte sont stockés sous forme d’enregistrements explicites `input_files`. Ils permettent de reconstruire et vérifier la signature du rendu sans transformer un nom de fichier contenant « tokenizer » en pseudo-variable de secret.

Le contrôle des images encodées est un examen de toutes les pages complètes et des instants déclarés. Il ne signifie pas que chaque image intermédiaire a été vue. Le décodage complet prouve la lisibilité technique du flux; il ne remplace pas un visionnage humain continu. Les 744 états de construction correspondent à des fins stables d’animations, et non à tous leurs états intermédiaires.

**La livraison reste une livraison de revue silencieuse.** Les scripts sont rédigés, mais aucune nouvelle synthèse vocale n’a été produite, écoutée ou mesurée. La durée cumulée des aperçus est de 1 419,733332 secondes; elle ne prédit pas la durée des vidéos narrées. Résolution finale, visionnage continu, écoute et approbation de diffusion restent des étapes distinctes. La dette Ruff générale du dépôt n’est pas corrigée par cet audit et aucun contrôle n’a été désactivé.

## Six propositions complémentaires à conserver

Ces sujets ne reçoivent pas encore de numéro réservé. Leurs exemples, autocontrôles et raisons de non-redondance figurent dans l’analyse jointe.

| Sujet | Erreur ciblée | Repères |
|---|---|---|
| Comparer des écarts exige de regarder les pas | Diagnostiquer un modèle à partir de différences de sorties malgré des intervalles d’entrée inégaux | M 4.5–4.6; C 4.5A–C, 6.7C en transfert |
| Valeur absolue : faut-il écrire « et » ou « ou » ? | Confondre intérieur d’un intervalle et réunion des deux régions extérieures | M 1.7, 2.5; C 1.5A–B, 2.5C |
| Exactement k succès : un chemin ne suffit pas | Oublier les placements possibles des succès dans un modèle binomial | M 8.5, 8.9; C 8.5A–B |
| Un produit de matrices nul n’annule pas forcément un facteur | Étendre sans condition la propriété du produit nul des réels aux matrices | M 11.3, 11.7, 12.5; C 11.3B, 11.7A–B en transfert |
| Une formule définie ne valide pas son extrapolation | Confondre domaine algébrique et validité d’un modèle dans son contexte | M 4.5, 4.7; C 4.7B–C et synthèse S2 |
| Une mesure approchée ne donne pas une aire exacte | Traiter des mesures centrales comme exactes ou mal propager leurs intervalles | M 1.7; C chapitre 1, synthèse S3 |

La livraison accompagne les 30 aperçus de leurs scripts complets, d’un catalogue PDF, d’un manifeste de fichiers et d’une vérification de livraison. Les médias générés restent hors Git; le code, les notices, le catalogue et les rapports sont conservés dans la même proposition de modification que les lots précédents.
