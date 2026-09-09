# MAT0339 — Audit des PDF du 5 septembre 2026

Date du rapport : 6 septembre 2026.

## Périmètre et statut

21 anomalies documentées; corrections proposées, non appliquées aux anciens PDF. Texte intégral extrait; 49 pages candidates de figures du manuel examinées visuellement, plus des contrôles ciblés complémentaires. Pas de certification exhaustive de toutes les pages ni de toutes les sous-questions du cahier. Aucun merge GitHub effectué.

Codes : M = manuel (199 pages), E = cahier étudiant (63 pages), C = cahier avec réponses (82 pages). Les pages PDF sont physiques; les pages imprimées sont les numéros visibles.

P1 : correction nécessaire avant diffusion validée. P2 : qualité, précision, arrondi ou alignement. Tous les constats restent ouverts dans les PDF du 5 septembre.

## AUD-01 — Anagrammes de MATHEMATIQUE

**P1 — C, PDF 71, page imprimée 63; section 7.2.**

**Constat.** Le corrigé annonce onze lettres et trois paires de lettres répétées. Le mot imprimé compte douze lettres; M, A, T et E apparaissent chacun deux fois.

**Correction proposée.** Le nombre correct est \[\frac{12!}{2!\,2!\,2!\,2!}=29\,937\,600,\] et non \(4\,989\,600\). Recompter à partir de la chaîne de caractères, sans recopier une formule antérieure.

**Contrôle de fermeture.** Comptage des caractères, puis calcul entier du coefficient multinomial. Vérifier simultanément l’énoncé, le corrigé et tout export de la banque.

## AUD-02 — Encadrement et arrondi du quotient

**P2 — C, PDF 65, page imprimée 57; section 1.7 A.**

**Constat.** L’énoncé étudiant (PDF 11, p. 3) demande deux dizaines consécutives. Le corrigé donne 150 et 170 et une approximation 156,45.

**Correction proposée.** On doit obtenir \[150<\frac{19{,}8\times4{,}03}{0{,}51}<160,\qquad q\approx156{,}46.\] Un encadrement sans calcul exact est possible en minorant par \(19{,}5\times4/0{,}52=150\) et en majorant par \(20\times4{,}08/0{,}51=160\).

**Contrôle de fermeture.** Le quotient exact est \(13299/85\). Les bornes doivent différer de dix et l’arrondi doit être calculé à partir de la valeur non arrondie.

## AUD-03 — Deux longueurs mal arrondies

**P2 — C, PDF 79, page imprimée 71; section 15.2 B.**

**Constat.** Pour \(A=35^\circ\), \(B=70^\circ\) et \(a=8\), le corrigé donne \(b\approx13{,}10\) et \(c\approx13{,}48\).

**Correction proposée.** Comme \(C=75^\circ\), \[b=8\frac{\sin70^\circ}{\sin35^\circ}\approx13{,}11,\qquad c=8\frac{\sin75^\circ}{\sin35^\circ}\approx13{,}47.\]

**Contrôle de fermeture.** Recalculer avec les angles exacts en mode degré, conserver la précision interne, puis arrondir au centième.

## AUD-04 — Angles du cas ambigu SSA

**P2 — C, PDF 79, page imprimée 71; section 15.5 B.**

**Constat.** Le corrigé annonce \(66{,}69^\circ\) et \(113{,}31^\circ\) pour les données \(A=40^\circ,a=7,b=10\).

**Correction proposée.** \[B_1=\arcsin\!\left(\frac{10\sin40^\circ}{7}\right)\approx66{,}67^\circ,\quad B_2\approx113{,}33^\circ.\] Les deux troisièmes angles sont positifs, environ \(73{,}33^\circ\) et \(26{,}67^\circ\). La conclusion « deux triangles » reste correcte.

**Contrôle de fermeture.** Ne pas arrondir le sinus intermédiaire à quatre décimales avant l’arcsinus. Vérifier les deux branches et la somme des angles.

## AUD-05 — Longueur de triangulation

**P2 — C, PDF 79, page imprimée 71; section Synthèse 15, S1.**

**Constat.** Le corrigé donne \(a\approx98{,}39\) pour \(a=120\sin48^\circ/\sin65^\circ\).

**Correction proposée.** La valeur est environ \(98{,}3963509\), donc \(98{,}40\) au centième. Les autres valeurs annoncées \(b\approx121{,}88\) et la hauteur \(90{,}57\) sont compatibles avec le recalcul.

**Contrôle de fermeture.** Uniformiser la précision finale, sans propager une approximation à une nouvelle étape.

## AUD-06 — La région coloriée a le mauvais sommet

**P1 — M, PDF 151, page imprimée 141; section 13.6.**

**Constat.** Les frontières sont \(3x+y=18\) et \(x+y=8\). Leur intersection est \((5,3)\), alors que la région coloriée et son point de raccord sont placés en \((4,4)\). Le remplissage ne représente donc pas l’intersection des demi-plans.

**Correction proposée.** Reconstruire le polygone à partir des sommets \[(0,0),\ (6,0),\ (5,3),\ (0,8).\] Pour l’objectif annoncé \(P=70x+40y\), les valeurs sont \(0,420,470,320\); le maximum est \(470\) en \((5,3)\). La ligne d’objectif doit avoir la pente \(-7/4\).

**Contrôle de fermeture.** Calculer les intersections depuis les mêmes coefficients que le texte; tester tous les sommets dans toutes les contraintes; vérifier le remplissage sur le rendu.

## AUD-07 — La famille de niveaux n’est pas cohérente

**P1 — M, PDF 150, page imprimée 140; section 13.5.**

**Constat.** Le dessin est censé montrer le déplacement parallèle d’une droite. Dans la source d’août correspondant à cette figure conservée visuellement, les segments joignent \((-0{,}2,c/2)\) à \((c/3,0)\) pour plusieurs valeurs de \(c\): leurs pentes diffèrent. Le point rouge n’est pas justifié par un objectif numérique annoncé.

**Correction proposée.** Fixer d’abord un objectif explicite, puis calculer ses niveaux et son optimum. Par exemple pour \(3x+2y=c\), l’extrémité gauche doit être \((-0{,}2,(c+0{,}6)/2)\). Pour le polygone de ce dessin, l’optimum de cet objectif proposé est \((3{,}2,2{,}4)\), de valeur \(14{,}4\), et non le point rouge \((1{,}2,4{,}2)\), de valeur \(12\).

**Contrôle de fermeture.** Confirmer le code exact dans les sources de septembre avant modification. Les niveaux doivent avoir un normal commun; le point souligné doit maximiser l’objectif choisi sur tous les sommets.

## AUD-08 — Une simplification ne suffit pas à produire un trou

**P1 — M, PDF 62, page imprimée 52; section 5.2.**

**Constat.** Le texte oppose « un facteur simplifiable, qui produit un trou » à un facteur restant qui produit une asymptote. Une cancellation partielle ne suffit pas : \(x/x^2=1/x\) pour \(x\ne0\) garde une asymptote en zéro.

**Correction proposée.** Parler du quotient entièrement réduit. À une valeur interdite, il y a un trou si le dénominateur réduit est non nul; s’il s’annule encore, le quotient réduit présente une asymptote verticale. Conserver dans les deux cas le domaine initial.

**Contrôle de fermeture.** Contraster explicitement \(x^2/x\) et \(x/x^2\), tous deux initialement indéfinis en zéro. Relire aussi la formulation voisine de la section 5.3.

## AUD-09 — Un angle de trente degrés est placé au pied de la hauteur

**P1 — M, PDF 161, page imprimée 151; section 14.6.**

**Constat.** Dans le triangle équilatéral coupé en deux, l’étiquette \(30^\circ\) apparaît près du pied de la hauteur, où l’angle est droit. Elle ne désigne pas l’angle de trente degrés au sommet.

**Correction proposée.** Déplacer \(30^\circ\) au sommet entre la hauteur et un côté; marquer \(90^\circ\) au pied par un petit carré. Garder \(60^\circ\) à la base et les longueurs \(1,\sqrt3,2\).

**Contrôle de fermeture.** Les étiquettes d’angle doivent être associées à des arcs centrés au bon sommet; vérifier la perpendicularité, les longueurs et la somme des angles.

## AUD-10 — Ensembles emboîtés : étiquette intérieure superposée

**P2 — M, PDF 13, page imprimée 3; section 1.1.**

**Constat.** Le symbole \(\mathbb N\) et la liste \(0,1,2,\ldots\) se superposent dans le rectangle le plus petit.

**Correction proposée.** Réserver un emplacement fixe pour le nom de chaque ensemble et un autre pour ses exemples; agrandir le rectangle intérieur plutôt que réduire le texte.

**Contrôle de fermeture.** Contrôle au format d’impression et en niveaux de gris : aucune paire de boîtes de texte non intentionnellement superposées.

## AUD-11 — Droite réelle : flèche et étiquettes de points

**P2 — M, PDF 16, page imprimée 6; section 1.5.**

**Constat.** La flèche mesurant la distance se trouve sur le niveau des étiquettes \(a=-2\) et \(b=3\). Les traits traversent ou frôlent le texte.

**Correction proposée.** Séparer trois niveaux : points et graduations; noms des points; ligne de cote et sa valeur. Réserver une marge autour des extrémités de la flèche.

**Contrôle de fermeture.** Examiner les nœuds dans le rendu final, pas seulement la largeur extérieure de l’image.

## AUD-12 — Une annotation recouvre les deux boîtes

**P2 — M, PDF 28, page imprimée 18; section 2.7.**

**Constat.** « une solution ajoutée » est posé sur le haut des boîtes « ensemble initial » et « après multiplication ». La cause de la transformation devient difficile à lire.

**Correction proposée.** Placer le commentaire au-dessus de la flèche, avec sa propre largeur et un décalage vertical suffisant; garder les ensembles au centre de deux boîtes séparées.

**Contrôle de fermeture.** La flèche, son libellé et les deux contenus doivent avoir des zones distinctes.

## AUD-13 — Des légendes sont traversées par les courbes

**P2 — M, PDF 62, page imprimée 52; section 5.1--5.2.**

**Constat.** Les mentions « racine simple », « racine double », « traverse », « touche » et les libellés verticaux des asymptotes touchent les tracés. Deux dessins presque identiques sont répétés sur la même page.

**Correction proposée.** Déporter les légendes dans une zone libre et les relier par de courts traits de rappel. Donner un rôle distinct aux deux figures, ou remplacer la répétition par un exemple contrastant trou et pôle.

**Contrôle de fermeture.** Contrôler chaque étiquette à taille réelle. Une diminution globale de la figure n’est pas une correction de collision.

## AUD-14 — La représentation des effectifs masque son propre message

**P2 — M, PDF 99, page imprimée 89; section 8.8.**

**Constat.** Le mot « malades » est vertical sur une bordure, le commentaire est posé dans le rectangle, et « faux positifs » longe le bord inférieur. Les petites régions sont difficiles à distinguer.

**Correction proposée.** Préférer un tableau d’effectifs avec lignes malades/non malades et colonnes test positif/négatif : \((190,10)\) et \((392,9408)\). Mettre à côté le rapport \(190/(190+392)\), sans superposer les explications aux zones.

**Contrôle de fermeture.** Les sommes de lignes valent 200 et 9800; la colonne positive vaut 582. Le support doit rester lisible sans couleur.

## AUD-15 — La grille transformée ne montre qu’une famille de droites

**P2 — M, PDF 129, page imprimée 119; section 11.6.**

**Constat.** Pour la matrice affichée \(A=\begin{pmatrix}2&1\\0&1\end{pmatrix}\), la figure de droite montre essentiellement les droites obliques. La seconde famille de la grille initiale n’est pas représentée.

**Correction proposée.** Dessiner aussi les images des lignes horizontales. Pour \((u,v)\mapsto(2u+v,v)\), les lignes \(v=c\) restent horizontales; les lignes \(u=c\) deviennent \(x-y=2c\). Utiliser un même repère géométrique.

**Contrôle de fermeture.** Calculer les deux familles depuis la transformation et tester les images des deux vecteurs de base.

## AUD-16 — Quatre schémas demandés, mais non fournis

**P1 — E, PDF 55, page imprimée 47; section 15.3 A.**

**Constat.** L’exercice demande une première équation « pour quatre schémas correspondant à SSS, SAS, ASA et SSA ». Aucun de ces quatre schémas n’est fourni ou référencé précisément.

**Correction proposée.** Joindre quatre triangles étiquetés avec leurs données, ou réécrire l’énoncé pour demander explicitement à l’étudiant de construire lui-même ces quatre configurations.

**Contrôle de fermeture.** Faire résoudre l’exercice avec le seul sujet distribué; aucune image implicite ne doit être nécessaire.

## AUD-17 — Un graphe donné est introuvable

**P2 — E, PDF 19, page imprimée 11; section 3.7 B.**

**Constat.** L’exercice commence par « Sur un graphe donné » sans identifier de graphe sur la page ni un renvoi univoque.

**Correction proposée.** Fournir le graphe à analyser, nommer une figure précise du manuel, ou demander de créer un exemple. Préciser si les valeurs attendues sont exactes ou lues approximativement.

**Contrôle de fermeture.** Un lecteur doit identifier sans intervention orale le support de la question.

## AUD-18 — La progression ne prépare pas suffisamment l’onde spatiale

**P2 — E, PDF 61, page imprimée 53; section 17.5.**

**Constat.** L’exercice \(y(x,t)=3\sin(2\pi x/5-4\pi t)\) demande longueur d’onde et vitesse de propagation. Les sections temporelles du manuel ne dérivent pas ces notions spatiales ni \(v=\omega/k\). Le corrigé (PDF 81, p. 73) les utilise directement.

**Correction proposée.** Ajouter une courte préparation distinguant période temporelle et période spatiale, avec unités et déplacement d’une phase constante, ou marquer ce problème comme approfondissement accompagné. Les examens de travail ci-joints restent limités aux sinusoïdes temporelles.

**Contrôle de fermeture.** Associer chaque compétence évaluée à une définition et un exemple enseignés. Il s’agit d’un décalage entre documents, pas d’une conclusion sur un plan de cours officiel absent.

## AUD-19 — Le dénominateur disparaît dans une étape du corrigé

**P1 — C, PDF 66, page imprimée 58; section Synthèse 2, S3.**

**Constat.** Pour \((x-1)/(x+2)\le2\), le corrigé passe d’abord à \((x-1)-2(x+2)\le0\), puis remet le dénominateur. Cette étape n’est pas équivalente lorsque le dénominateur est négatif. L’ensemble final annoncé est correct.

**Correction proposée.** Pour \(x\ne-2\), conserver \[\frac{x-1}{x+2}-2=\frac{-x-5}{x+2}\le0.\] Le tableau de signes donne \(]-\infty,-5]\cup]-2,+\infty[\). Ne pas enseigner une étape fausse en dépit du bon résultat final.

**Contrôle de fermeture.** Tester \(x=-6\): le quotient initial vérifie l’inégalité mais le numérateur isolé ne la vérifie pas. Vérifier chaque équivalence, et non seulement les solutions.

## AUD-20 — Domaine et condition nécessaire sont confondus

**P2 — M, PDF 27, page imprimée 17; section 2.5; cahier 2.5 A.**

**Constat.** Pour \(\sqrt{x+1}=x-1\), « le domaine impose \(x\ge1\) » confond la définition des expressions avec la condition de signe imposée à une solution. Une formulation analogue figure dans les réponses du cahier pour \(\sqrt{2x+3}=x\).

**Correction proposée.** Le domaine commun du premier exemple est \([-1,+\infty[\); toute solution doit en outre avoir \(x\ge1\). Pour le second, le domaine est \([-3/2,+\infty[\) et la condition supplémentaire est \(x\ge0\). Les résultats de résolution restent inchangés.

**Contrôle de fermeture.** Utiliser deux lignes séparées avant l’élévation au carré : « expressions définies » et « condition nécessaire pour une solution ».

## AUD-21 — Hypothèses locales du modèle exponentiel

**P2 — M, PDF 75, page imprimée 65; section 6.6--6.7.**

**Constat.** Les expressions \(T=\log_b2\), \(Q(t+1)/Q(t)\) et \(\ln Q(t)\) nécessitent des hypothèses qui ne sont pas toutes rappelées à leur apparition.

**Correction proposée.** Pour le temps de doublement futur d’une quantité positive, imposer \(Q_0>0\) et \(b>1\). Le quotient exige \(Q_0\ne0\); la linéarisation logarithmique exige \(Q_0>0,b>0\). Traiter séparément le cas constant \(b=1\).

**Contrôle de fermeture.** Tester les cas \(Q_0=0\), \(b=1\) et \(0<b<1\) sans utiliser un logarithme ou un temps de doublement non défini.

## Vérifications et limites

Le script `sources/verify_calculations.py` recalcule les valeurs signalées et des résultats des examens. Les contrôles de barème font partie du total; ce nombre n’est pas un nombre de théorèmes certifiés. Le test ne garantit pas que toute formule imprimée dans le manuel a été analysée.

## Versions

M — `MAT0339_manuel_2026-09-05.pdf`; SHA-256 `dcba48fdcb4cb53ee93df1cd4f9304de20b7058441204954d1912735143210a7`.

E — `MAT0339_cahier_etudiant_2026-09-05.pdf`; SHA-256 `e4073fcaa9b68ea23a60e15bb4d4ff8fbdfc24ee600a5b197558c3a2a1e1775a`.

C — `MAT0339_cahier_reponses_2026-09-05.pdf`; SHA-256 `4190459ad6af0ba673c0745ee39c682d95677f2dc9d83b7c43f8837a0d31ef12`.
