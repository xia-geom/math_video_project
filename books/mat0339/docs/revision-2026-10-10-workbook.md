# MAT0339 — révision du cahier et des réponses brèves, 10 octobre 2026

Ce rapport décrit les modifications de `sources/workbook/` pour les éditions étudiant et avec réponses. Les cinq parties, les 17 chapitres, les 126 exercices de section et les 17 synthèses sont conservés. Les deux éditions partagent les mêmes chapitres; seule l'édition avec réponses ajoute [backmatter.tex](../sources/workbook/backmatter.tex). Les réponses restent des résultats et des pistes, et non des solutions entièrement développées.

Les sources actives sont révisées sans modifier les originaux, les documents historiques ou les anciennes releases. Les identifiants AUD renvoient au [rapport du 6 septembre](../audits/2026-09-06/RAPPORT_AUDIT.md), conservé dans son état historique. Le [rapport général](revision-2026-10-10.md) documente le manuel, les examens et la compilation commune.

## Corrections issues de l'audit

| Constat | Exercice ou synthèse | Modification et contrôle |
|---|---|---|
| AUD-01 | 7.2 | MATHEMATIQUE contient 12 lettres; M, A, T et E apparaissent chacun deux fois. Le quotient `12!/(2!)⁴` donne 29 937 600 anagrammes. Le test recompte les caractères et calcule le multinomial. |
| AUD-02 | 1.7 | L'encadrement demandé entre deux dizaines consécutives devient `150 < q < 160`, avec une minoration et une majoration explicites. La valeur exacte est `13299/85`, soit `156,46` au centième. Les bornes et l'arrondi sont calculés indépendamment avec des fractions. |
| AUD-03 | 15.2 | Les deux longueurs calculées par la loi des sinus sont arrondies à `13,11` et `13,47`. La seconde formule figure désormais dans la réponse. |
| AUD-04 | 15.5 | Le cas SSA donne `B ≈ 66,67°` ou `113,33°`, puis `C ≈ 73,33°` ou `26,67°`. Les deux triangles sont admissibles. Le sinus intermédiaire n'est pas arrondi avant le calcul des angles. |
| AUD-05 | Synthèse 15 | La longueur de triangulation est `120 sin(48°)/sin(65°) ≈ 98,40`. Le test recalcule la valeur à partir des angles. |
| AUD-16 | 15.3 | Quatre schémas étiquetés SSS, SAS, ASA et SSA sont fournis. Chaque inconnue est désignée, les côtés sont opposés aux sommets correspondants, et les dessins sont annoncés comme non à l'échelle. Le corrigé donne la première équation de chacun des quatre cas. |
| AUD-17 | 3.7 | La question B utilise explicitement le graphe construit en A. Les lectures approximatives sont permises; la réponse rappelle qu'elles dépendent du dessin choisi. |
| AUD-18 | 17.5 | La consigne renvoie à l'enseignement des ondes en 17.5 du manuel. Elle précise les unités de `x`, `y` et `t`, demande la période et le sens de propagation, et le corrigé explique la phase constante. Les résultats sont `A=3 m`, `λ=5 m`, `T=0,5 s`, `f=2 Hz`, propagation vers les `x` croissants à `10 m/s`. |
| AUD-19 | Synthèse 2 | Le dénominateur est conservé dans `(x−1)/(x+2)−2 = (−x−5)/(x+2) ≤ 0`, avec `x≠−2`. Le tableau de signes donne `]−∞,−5] ∪ ]−2,+∞[`. Les substitutions `x=−6` et `x=−3` montrent pourquoi on ne peut pas éliminer le dénominateur sans discuter son signe. |
| AUD-20 | 2.5 et 2.8 | Le domaine d'une racine et la condition nécessaire de signe sont séparés. Pour `√(2x+3)=x`, les expressions sont définies dès `x≥−3/2`, tandis qu'une solution impose `x≥0`. Pour `√(x+1)=x−1`, le domaine est `x≥−1` et une solution impose `x≥1`. Les candidats sont vérifiés dans l'équation initiale. |

## Corrections supplémentaires et synchronisation

Les chapitres et les réponses brèves ont été relus ensemble. Les ajouts de données, les restrictions de domaine et les valeurs suivantes se retrouvent dans les deux éditions lorsque cela concerne l'énoncé, et dans les réponses correspondantes lorsque cela concerne le calcul.

| Section | Révision |
|---|---|
| 1.6 | Les égalités avec radicaux sont examinées pour `a,b≥0`, avec justification. |
| 2.2 | La comparaison de deux expressions rationnelles demande leurs domaines naturels et si elles définissent la même fonction. Elle ne les suppose plus toutes deux définies sur les réels. |
| 4.2 | Le rectangle est non dégénéré; ses côtés `x` et `12−x` sont en mètres. Le domaine devient `]0,12[` et l'aire maximale porte l'unité `36 m²`. |
| 4.7 | La consigne demande directement de vérifier le modèle à partir des données, des unités et des contraintes. |
| 5.1 | L'étude porte sur la fonction rationnelle fournie en B. Le corrigé conserve le domaine initial, distingue le zéro `2`, le trou `(-2,4/5)` et l'asymptote verticale `3`. |
| 6.3 | L'infinitif est harmonisé dans la consigne. La réponse précise `b>0`, `b≠1` et la positivité des arguments dans les lois logarithmiques. |
| 6.5 | Le temps de doublement est corrigé à `ln(2)/ln(1,042) ≈ 16,85 ans`. |
| 6.7, 6.8 et synthèse 6 | La prise de logarithme du modèle suppose `A>0` et `b>0`; le cas `b=1` est constant. Le refroidissement suppose `k>0`. La construction d'une exponentielle utilise deux abscisses distinctes et deux ordonnées positives. L'expression « toutes les 5 unités de temps » remplace une formulation imprécise. |
| 7.1 et 7.3 | L'alphabet comporte explicitement 26 lettres et les chiffres vont de 0 à 9. Les choix de quatre lettres avec ou sans répétition sont formulés séparément. |
| 8.5 et 8.7 | Les 12 essais de Bernoulli sont indépendants, avec probabilité de succès `0,7`. La comparaison de fréquences porte sur de nombreuses séries de 100 ou 1 000 lancers indépendants d'une pièce équilibrée; aucune simulation non fournie n'est requise. |
| 9.6 et synthèse 9 | L'égalité de vecteurs prend en compte la longueur, la direction et le sens. La consigne demande de déterminer l'alignement. La distance erronée `BC=√41` est remplacée par `BC=5`. |
| 10.7 | L'intersection dispose de données complètes : `(x,y)=(1,2)+t(2,−1)` et `x+y=5`. La réponse obtient `t=2`, puis `(5,0)`, et vérifie ce point. |
| 11.5, 11.8 et synthèse 11 | Les rotations de 90° sont explicitement antihoraires; l'étirement horizontal est « de facteur 3 ». |
| 12.3 et 12.8 | Les opérations sur les lignes sont reliées aux transformations des équations. Le calcul comparatif utilise `3x+2y=13`, `5x−2y=11`; les deux éliminations donnent `(3,2)`, via `8x=24` ou `16y=32`. |
| 13.6, 13.7 et synthèse 13 | « Au moins le double » remplace une formulation ambiguë. Le tableau demandé provient du problème construit en A. Le corrigé ne garantit plus l'optimum entier par l'arrondi ou les seuls voisins de l'optimum continu : il faut examiner les points entiers réalisables ou employer une méthode adaptée. |
| 14.4 et 14.5 | La parité du sinus et du cosinus et la période de la tangente sont formulées correctement. Le rayon de l'exercice d'arc est donné en centimètres. |
| 15.3 | Les contrôles d'un triangle calculé sont demandés en termes de somme des angles, d'ordre des côtés et des angles, et d'inégalité triangulaire. La première question SSA dessinée et le second exemple numérique sont traités séparément dans la réponse. |
| 16.2 | L'amplitude vaut `|A|`; le signe de `A` détermine une réflexion. La période `2π/|B|` est donnée pour `A,B≠0`. |
| 16.6, 16.7 et synthèse 16 | Les maxima demandés sont les deux premières abscisses positives. La résolution temporelle se fait sur `[0,6]`. La réponse à `sin(x)+cos(x)=1` sur l'intervalle fermé `[0,2π]` inclut maintenant l'extrémité `2π`, en plus de `0` et `π/2`. |
| 17.1, 17.2, 17.6 et synthèse 17 | Le mouvement est uniforme, le sens de rotation et les unités sont précisés lorsque nécessaires. La vitesse linéaire est `r|ω|`. Le modèle général précise `r>0` et `ω≠0`. |
| 17.4 | La recherche des premiers instants se fait pour `t≥0`. Les familles utilisent `k∈ℤ`; les premiers passages à la médiane, maximum et minimum sont respectivement `3`, `5` et `1`. |
| Synthèse 17 | Le diagnostic de phase précise que les hauteurs maximale et minimale ainsi que la période sont déjà reproduites. Seuls les passages à la médiane sont trop tôt, ce qui rend le paramètre à examiner identifiable. |

Les couvertures décrivent le contenu (« Exercices classés selon les sections du manuel », « Exercices par section », « Problèmes de synthèse »). La date vient de [edition.tex](../sources/edition.tex). Le mode d'emploi annonce la correction des réponses et la stabilité de la numérotation; les conseils demandent de préciser la méthode, les hypothèses, les unités et de vérifier le résultat. La conclusion propose de refaire un exercice difficile sans regarder la réponse, puis de vérifier dans l'énoncé initial.

## Contrôles mathématiques et structurels

Les huit tests de [test_revision_workbook.py](../tests/test_revision_workbook.py) couvrent le multinomial, l'encadrement rationnel, l'inéquation avec dénominateur de signe variable, la distinction domaine/condition nécessaire, les arrondis trigonométriques et les deux branches SSA, les quatre configurations fournies, les calculs supplémentaires et l'utilisation commune de la date d'édition. Les calculs partent des données et sont reliés aux réponses présentes dans la source. Les calculs d'onde sont également couverts par les contrôles du manuel.

La commande commune est `make -C books/mat0339 verify`. Lors de la première compilation complète de cette révision, le responsable de l'intégration a signalé 60 tests réussis, la conservation de la structure et des archives, et aucune boîte débordante dans les journaux des livres. Ces résultats précèdent les dernières retouches de mise en page; les résultats de la compilation finale doivent être inscrits dans le manifeste général. La commande `make -C books/mat0339 student answers` reconstruit les deux variantes et exécute les vérifications du projet.

Ces tests ne constituent pas une preuve de toutes les formules du cahier. Les exemples ouverts conservent des réponses variables; leurs pistes indiquent les critères pertinents.

## Revue visuelle de toutes les pages — première compilation

Les numéros ci-dessous sont les numéros physiques des PDF de la première compilation examinée, avant les dernières retouches. Ils peuvent changer lors de la reconstruction. Les rendus à 65 ppp et leurs planches de contrôle sont dans `build/review-2026-10-10/student/` et `build/review-2026-10-10/answers/`.

| Ensemble | Méthode et couverture réellement effectuées |
|---|---|
| Cahier étudiant, 64 pages | Le responsable de l'intégration a inspecté les planches couvrant les 64 pages. |
| Édition avec réponses, pages 1–8 | Inspection visuelle des couvertures, textes liminaires et tables des matières, par les planches 01 et 02. |
| Édition avec réponses, pages 9–63 | Comparaison pixel par pixel des 55 images avec les mêmes pages du cahier étudiant : aucune différence. Comparaison du texte extrait : aucune différence. L'inspection de ces pages du cahier étudiant vaut donc aussi pour ce rendu commun. |
| Édition avec réponses, pages 64–83 | Inspection de la page 64 et des planches 17–21 couvrant les pages 65–83. Agrandissements complémentaires des pages 67, 72 et 80. |

Les agrandissements des réponses vérifient notamment l'inéquation et son dénominateur (page 67, numéro imprimé 59), le comptage de MATHEMATIQUE (page 72, numéro imprimé 64), et les arrondis/branches SSA du chapitre 15 (page 80, numéro imprimé 72). Aucun chevauchement, rognage ou débordement de formule n'a été constaté dans ces pages de réponses.

La revue a révélé trois défauts de pagination : le titre 12.7 isolé en bas de page du cahier étudiant (page physique 46), une entrée double « Réponses brèves et pistes » dans la table des matières de l'édition avec réponses (page 7), et un en-tête « Table des matières » sur la page blanche 8. Les sources ont ensuite reçu une réservation d'espace avant 12.7, la suppression de l'entrée manuelle de table des matières en double et le traitement des pages blanches par `emptypage`. Les couvertures et deux précisions mathématiques (phase et base logarithmique) ont également été retouchées après ce premier rendu.

**Revue finale terminée.** Les PDF reconstruits comptent toujours 64 et 83 pages. La comparaison des rendus complets à 65 ppp avec la première compilation limite les changements aux pages 1, 8, 46, 47 et 63 du cahier étudiant, et aux pages 1, 7, 8, 46, 47, 63 et 71 de l'édition avec réponses. Toutes ces modifications ont été inspectées à 100 ppp, directement ou par identité avec le rendu étudiant. La table des matières conserve une seule entrée vers la page imprimée 56; la page blanche 8 n'a plus d'en-tête; le titre 12.7 est suivi des questions A et B. La question C continue sur la page suivante, sans rognage. Les passages révisés sur la phase et les hypothèses logarithmiques restent lisibles.

Les pages physiques 55–56 ont été inspectées en détail : les données, sommets et inconnues des quatre triangles sont lisibles; un rendu en gris à 150 ppp confirme que leur interprétation ne dépend pas des couleurs. Les pages voisines et la fin du chapitre 17 ont également été examinées. Les 55 pages d'exercices partagées (9–63) ont été à nouveau comparées pixel par pixel dans les deux PDF finaux, sans différence. Les preuves locales sont dans `build/review-2026-10-10/workbook-final/`; `65/comparison.json` consigne les pages modifiées. Les empreintes des PDF livrés figurent dans le manifeste général.

La vérification finale exécute les 60 tests avec succès. Les trois builds du livre ne présentent aucun débordement ni référence non résolue. Une boîte de paragraphe insuffisamment remplie (`Underfull hbox`, badness 1509) subsiste dans les réponses : c'est un avertissement de justification, sans collision ou texte manquant observé à la revue des pages.

Aucune approbation institutionnelle, vérification exhaustive d'un syllabus externe ni certification PDF/UA n'est déclarée.
