# MAT0339 — Capsules sur les erreurs fréquentes

## Sources et périmètre

Ce lot aide à reconnaître des erreurs de raisonnement commises pendant les
exercices. Il ne constitue pas une liste de fautes restant dans le manuel.

Le texte de référence est l’édition du **10 octobre 2026**, présente dans
[`main` au commit `4d451c3`](https://github.com/xia-geom/math_video_project/tree/4d451c37d483d763e33683a7fb683d1e0fdde62d/books/mat0339/sources).
Les sources actives sont `books/mat0339/sources/manual/chapters/` et
`books/mat0339/sources/workbook/chapters/`. Les anciens fichiers d’août et les
PDF archivés ne servent pas de base à ce relevé.

La [révision du 17 octobre, au commit `e418c5e`](https://github.com/xia-geom/math_video_project/tree/e418c5ed57338440e1f88dddbea0e0bebc2cfe55/books/mat0339/sources),
proposée dans la PR #29, a également été consultée. Elle n’est pas fusionnée
dans `main` au moment du relevé. Ses clarifications ne changent pas les
identifiants des sections citées; la présente modification n’intègre pas son
texte dans le livre.

Le catalogue possède déjà 37 leçons principales et six capsules d’erreurs,
numérotées de 38 à 43. Celles-ci traitent l’implication et l’équivalence, la
racine d’un produit, l’égalité de fonctions, les solutions parasites, l’ordre
de composition et la simplification des fractions. Le lot conserve les douze
identités 44–55 déjà proposées dans la PR #27 et ajoute 56–57. La numérotation
reste définie uniquement dans `curriculum/programme_principal_fr.yaml`.

## Premier lot : quatorze sources de capsules

Le choix privilégie des erreurs qui demandent un contrôle supplémentaire après
une méthode déjà étudiée : vérifier un domaine, identifier une population,
retrouver une unité ou interpréter une solution dans son contexte. Les chapitres
sur les modèles exponentiels et les ondes justifient les deux ajouts. Il s’agit
d’une priorité éditoriale fondée sur le livre et le catalogue, sans mesure de la
fréquence des erreurs chez les étudiants.

Dans les tableaux, **M** désigne le manuel et **C** le cahier. Une adaptation
reprend une idée du livre avec un exemple original; elle n’est pas présentée
comme la reproduction exacte de l’exercice cité.

| No | Capsule | Erreur à reconnaître et contrôle proposé | Références actuelles |
|---|---|---|---|
| 44 | Diviser par une inconnue : la solution disparue | Diviser par un facteur nul peut perdre une solution. Factoriser ou séparer les cas. | M2.6–2.8; C2.6A, adaptation. |
| 45 | Un dénominateur peut changer le sens de l’inégalité | Vérifier le domaine et le signe; ramener à zéro une inégalité dont le second membre ne l’est pas. | M2.4, M2.8; C2.4C et synthèse S3 du chapitre 2. |
| 46 | Deux pourcentages opposés ne s’annulent pas | La seconde variation porte sur une nouvelle base. Suivre les facteurs successifs. | M1.7; C1, synthèse S2. |
| 47 | Le logarithme d’une somme : une fausse règle | Tester l’identité proposée et distinguer somme et produit, avec leurs domaines. | M6.3, M6.8; C6.3C. |
| 48 | Probabilité conditionnelle : le groupe de référence | Inverser la condition change le groupe au dénominateur. Comparer les effectifs. | M8.3, M8.8; C8.3B. |
| 49 | Indépendants et incompatibles | Une intersection vide n’est pas le critère d’indépendance. Vérifier les probabilités. | M8.4, M8.9; C8.4B. |
| 50 | Additionner des déplacements ou des longueurs | Le trajet parcouru et le déplacement total répondent à deux questions différentes. | M9.2–9.3; C9.2C. |
| 51 | Le carré d’une matrice ne se calcule pas case par case | Répéter la transformation et utiliser le produit ligne-colonne. | M11.3–11.4; C11.4B–C. |
| 52 | Arrondir une solution optimale peut la rendre impossible | Après l’arrondi, vérifier toutes les contraintes, puis prouver l’optimalité entière. | M13.3, M13.7; C13, synthèse S3, exemple original. |
| 53 | L’amplitude et la hauteur maximale | Mesurer l’écart à la médiane et distinguer coefficient signé, amplitude et extrêmes. | M16.2, M16.6–16.7; C16.6B. |
| 54 | Le déphasage se lit après factorisation | Factoriser l’argument et vérifier un point caractéristique du graphe. | M16.6–16.7; C16.2A, adaptation. |
| 55 | Tours par minute, radians par seconde et période | Convertir chaque unité et préciser le sens de rotation. | M17.1, M17.8; C17.1A–B. |
| 56 | Un temps de doublement existe-t-il toujours ? | Vérifier croissance, temps futur et valeur initiale avant d’appliquer une formule. | M6.6, M6.8; C6.5A–B et C6.6C, prolongement. |
| 57 | Période, longueur d’onde et propagation | Fixer une position pour mesurer une durée; fixer un instant pour mesurer une distance. | M17.5; C17.5A–C. |

Chaque capsule comprend une question, une explication visuelle, un exemple et
un exercice avec une pause de réflexion de six secondes avant la réponse.
Les exemples encore présents dans le cahier sont conservés. Les compléments
visent les contrôles qui manquent au raisonnement tenté, sans répéter toute la
leçon principale.

## Points vérifiés dans le livre actuel

- **Inéquations.** L’exercice C2.4C reste
  \(\frac{x+2}{x-3}>0\). La synthèse S3 ajoute
  \(\frac{x-1}{x+2}\le2\), dont la solution est
  \(]-\infty,-5]\cup]-2,+\infty[\). Le passage à un quotient comparé à zéro
  constitue une étape distincte.
- **Conditionnement.** L’exemple fictif de M8.8 donne
  \(P(+\mid M)=190/200=95\%\), tandis que
  \(P(M\mid+)=190/582\approx32{,}65\%\). Le numérateur est commun, les
  populations de référence diffèrent. L’exercice C8.3B reste un complément
  utile avec les effectifs d’une classe.
- **Optimisation entière.** Le petit modèle de la capsule 52 est un exemple
  original pour la synthèse C13 S3. Ses contraintes impliquent
  \(0\le x,y\le4\), ce qui permet d’examiner tous les points entiers. Un
  contrôle de quelques voisins de l’optimum continu ne suffirait pas à justifier
  la réponse.
- **Rotation.** Dans M17.1, la vitesse angulaire est signée. La relation générale
  est \(T=2\pi/|\omega|\) pour \(\omega\ne0\); la formule
  \(\omega=2\pi f\) suppose le sens positif annoncé.
- **Doublement.** Pour \(Q(t)=Q_0b^t\), avec un temps réel \(t\ge0\),
  \(Q_0>0\) et \(b>1\), le temps futur de doublement vaut
  \(\ln2/\ln b\). Pour \(0<b<1\), ce doublement futur n’existe pas.
  Les cas constants \(b=1\) et \(Q_0=0\) nécessitent une explication séparée.
- **Onde.** L’exercice C17.5A porte sur
  \(y(x,t)=3\sin(2\pi x/5-4\pi t)\), avec les positions en mètres et le temps
  en secondes. Il donne une amplitude de \(3\,\mathrm m\), une longueur d’onde
  de \(5\,\mathrm m\), une période de \(0{,}5\,\mathrm s\), une fréquence de
  \(2\,\mathrm{Hz}\) et une propagation vers les positions croissantes à
  \(10\,\mathrm{m/s}\). La vitesse du profil ne décrit pas le mouvement vertical
  d’un point à position fixée.

## Huit sujets pour le lot suivant

Ces sujets restent proposés; aucun numéro ni statut de production ne leur est
attribué. Ils peuvent reprendre une notion enseignée dans une leçon principale,
avec un raisonnement erroné précis à diagnostiquer.

| Sujet proposé | Apport de la capsule | Références |
|---|---|---|
| La calculatrice ne donne pas toutes les solutions trigonométriques | Passer d’une valeur principale à toutes les solutions sur l’intervalle demandé. | M16.3–16.4, M16.7; C16.3B, C16.4A. |
| Deux côtés et un angle : zéro, un ou deux triangles | Examiner le second angle possible et éliminer les triangles aplatis. | M15.4–15.5; C15.5B, C15 synthèse S3. |
| Déterminant nul : aucune solution ou une infinité ? | Séparer singularité et compatibilité du système. | M12.7–12.9; C12.3C, C12.7A. |
| Un comité n’est pas un podium | Reconnaître plusieurs ordres qui décrivent le même groupe. | M7.8–7.9; C7.8A–B. |
| Des résultats possibles ne sont pas forcément équiprobables | Construire des issues élémentaires avant de compter les cas favorables. | M8.9; C8.2C. |
| Sans remise : les probabilités changent | Mettre à jour les effectifs après un tirage et considérer les deux ordres possibles. | M8.3, M8.9. |
| Vecteur normal ou vecteur directeur ? | Lire les coefficients d’une équation cartésienne et vérifier une orthogonalité. | M10.2, M10.7; C10.2A–C. |
| Degrés dans une formule en radians | Diagnostiquer le mode de la calculatrice et les unités de l’angle. | M14.7; C14.6A, C14.7C. |

## Quatre prolongements

| Sujet proposé | Apport de la capsule | Références |
|---|---|---|
| Additionner des cas qui se recoupent | Repérer et retirer le double comptage de l’intersection. | M7.6, M7.9, M8.9; C7.6B–C. |
| Une région non bornée peut avoir un optimum | Relier la direction des lignes de niveau à la géométrie de la région. | M13.4, M13.7. |
| Un maximum et le minimum suivant : une demi-période | Vérifier que les extrema considérés sont consécutifs. | M17.7–17.8; C16 synthèse S2, C17 synthèse S1. |
| Une espérance n’est pas un résultat garanti | Distinguer gain brut, gain net et moyenne sur des répétitions. | M8.6, M8.9; C8.6B–C. |

## État de production

Ce document fixe les sujets et leurs références. La présence d’une source, une
prévisualisation silencieuse, une version narrée et une validation de diffusion
sont des états distincts. Les résultats techniques réellement obtenus sont
consignés dans le [compte rendu de réalisation du lot](VERIFICATION.md). Les fichiers générés ne
sont pas ajoutés au code source Git.
