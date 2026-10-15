# Banque priorisée de conceptions erronées — révision après le cours

**État : proposition éditoriale, 15 octobre 2026.** Cette banque prépare des
améliorations ou de futures capsules; elle ne crée aucune leçon, aucun numéro
et aucune autorisation de production. Les identités vidéo proviennent du
[catalogue unique](programme_principal_fr.yaml). Une couverture constatée dans
une source ne certifie ni le rendu livré ni l'apprentissage des étudiants.

Les raisonnements incorrects et les exemples ci-dessous sont **construits pour
l'enseignement**. Aucun n'est présenté comme une réponse recueillie auprès des
étudiants de MAT0339. « Documenté » signifie que le mécanisme est rapporté dans
une étude primaire indiquée; « plausible » signifie qu'il s'agit ici d'une
hypothèse pédagogique à vérifier. Une erreur isolée ne suffit pas à diagnostiquer
une conception durable.

Les priorités sont **éditoriales**, selon la précision du besoin dans le livre
et la couverture déjà écrite. Elles ne classent pas la fréquence des erreurs.
Les références au manuel et au cahier ont été vérifiées séparément dans les
sources actives de l'édition du 10 octobre 2026. Les lettres A, B et C désignent
les exercices de chaque section, pas des numéros de vidéos.

## Ordre de travail proposé

| Rang éditorial | Objet | Suite proposée |
|---|---|---|
| 1 | Amplitude et maximum | Candidat à une capsule distincte; objectif absent des sources trigonométriques inspectées. |
| 2 | Période et déphasage | Candidat à une capsule distincte, centrée sur la lecture de l'argument. |
| 3 | Degrés et radians | Renforcer d'abord la leçon du cercle unité avec un diagnostic d'unité. |
| 4 | Valeur principale et toutes les solutions | Réutiliser et améliorer l'exemple déjà intégré à la leçon 34. |
| 5 | Trou et asymptote verticale | Renforcer la comparaison déjà présente dans la leçon 15. |
| 6 | Domaine après simplification | Réutiliser la capsule 43 et la leçon 15; éviter un doublon. |

## 1. Prendre le maximum pour l'amplitude

**Raisonnement incorrect construit.** Pour une sinusoïde de maximum 7 et de
minimum 1 : « L'amplitude est 7, puisque c'est sa hauteur maximale. »

**Correction et vérification.** La médiane est `(7 + 1)/2 = 4`; l'amplitude
est `(7 − 1)/2 = 3`. Par exemple, `f(x) = 3 cos(x) + 4` atteint 7 en `x = 0`
et 1 en `x = π`. La distance de la médiane à chacun de ces extrêmes vaut 3.
Pour `A sin(B(x − C)) + D`, avec `A ≠ 0` et `B ≠ 0`, l'amplitude est `|A|`
et le maximum est `D + |A|`. Un coefficient négatif ne donne pas une amplitude
négative.

**Statut de preuve.** Documenté : Youbi rapporte notamment l'addition de `A`
et `D` pour trouver l'amplitude, ainsi que des confusions entre coefficient,
extremum et amplitude (§6.1.2.2–6.1.2.4). L'exemple 7/1 est notre adaptation.
[Étude primaire et limites de population : R2](#r2--transformations-trigonométriques).

**Livre.** Manuel §16.2, « Amplitude, période, déphasage et ligne médiane »
(`manual:section:16.02`), puis §16.6, « Effet des paramètres d'une sinusoïde ».
Cahier §16.2 B (`workbook:section:16.02`) demande une équation de maximum 7,
minimum 1, période 6 et maximum en `x = 2`; le modèle complet est par exemple
`3 cos((π/3)(x − 2)) + 4`. Cahier §17.3 A demande de lire amplitude et médiane
à partir des hauteurs 2 m et 42 m : amplitude 20 m, médiane 22 m.

**Couverture et décision.** `du_cercle_unite_a_la_fonction_sinus` (31) explique
le sinus du cercle unité, mais pas l'effet conjoint d'une amplitude et d'une
translation verticale. Aucune des six capsules d'erreurs ne cible cette
distinction. **Candidat à une nouvelle capsule**, avec objectif propre : lire
amplitude, médiane et extrêmes sur une même figure. Aucun numéro n'est réservé.

**Auto-vérification proposée.** Pour `g(x) = −4 cos(3x) + 2`, donner amplitude,
minimum et maximum, puis vérifier en `0` et `π/3`. Réponse : 4, −2 et 6.

## 2. Lire directement la période et le déphasage dans les nombres écrits

**Raisonnements incorrects construits.** Pour `f(x) = sin(2x − π/2)` :
« La période reste 2π puisqu'il s'agit d'un sinus »; « le déplacement vers la
droite vaut π/2 puisque je lis −π/2 dans l'argument ».

**Correction et vérification.** Factoriser l'argument :
`2x − π/2 = 2(x − π/4)`. La période fondamentale vaut `2π/2 = π` et le
déphasage choisi est `π/4` vers la droite. On vérifie `f(x + π) = f(x)`;
`f(π/4) = 0`, puis `f(π/2) = 1`, un quart de période plus loin.
La propriété `f(x + 2π) = f(x)` est également vraie : elle ne prouve pas que
`2π` soit la **plus petite** période positive. Pour `A sin(Bx − c) + D`,
le décalage est `c/B`, tandis que dans `A sin(B(x − C)) + D`, il est `C`.
Ces formules de période fondamentale supposent `A ≠ 0` et `B ≠ 0`.

**Statut de preuve.** Documenté : Youbi décrit l'attribution systématique de
`2π` au sinus transformé (§6.1.2.6.3) et la confusion entre la constante
soustraite dans l'argument et le décalage horizontal (§8.1.4.1).
[Étude primaire : R2](#r2--transformations-trigonométriques).

**Livre.** Manuel §16.2 (`manual:section:16.02`), §16.6
(`manual:section:16.06`) et dérivation de `2π/|B|` dans §16.7,
« Construire une sinusoïde et retrouver un angle ».
Cahier §16.2 A porte précisément sur `3 sin(2(x − π/4)) − 1`;
§16.6 A compare `sin x`, `2 sin x`, `sin(2x)` et `sin(x − π/2)`;
§16.7 B fait construire `2 sin(πt/3) − 1` sur une période.

**Couverture et décision.** `du_cercle_unite_a_la_fonction_sinus` (31) et
`lire_les_proprietes_d_un_graphe` (07) montrent la périodicité du sinus de base.
Les sources inspectées ne développent pas les paramètres d'une sinusoïde
transformée. **Candidat à une nouvelle capsule**, distincte de la précédente :
raisonner sur une variation de l'argument et sur l'entrée qui l'annule.

**Auto-vérification proposée.** Pour `g(x) = sin(3x − π)`, obtenir période
`2π/3`, décalage `π/3`; vérifier le passage croissant par zéro en `π/3` et
le maximum en `π/2`. Préciser que le décalage d'une fonction périodique n'est
pas unique : les décalages qui diffèrent d'une période donnent la même courbe.

## 3. Employer une valeur numérique sans vérifier l'unité d'angle

**Raisonnement incorrect construit.** « Je tape `sin(π/6)`, donc le résultat
de ma calculatrice doit être le sinus de trente degrés, quel que soit le mode. »

**Correction et vérification.** `π/6` radian et `30°` représentent le même
angle. En mode radians, `sin(π/6) = 1/2`; en mode degrés, la saisie `π/6`
désigne environ `0,524°`, dont le sinus vaut environ `0,00914`.
Le réglage n'effectue pas automatiquement la conversion de la saisie.
Relier le radian à `s/r` : sur un cercle de rayon 3, un angle de 1 radian
intercepte un arc de longueur 3; un tour complet vaut `2π` radians.

**Statut de preuve.** Documenté : Youbi examine des confusions entre degrés
et radians et des erreurs d'utilisation de la calculatrice (§6.2.1–6.2.2).
L'exemple précis reprend le diagnostic du cahier, et non une copie d'étudiant.
[Étude primaire : R2](#r2--transformations-trigonométriques).

**Livre.** Manuel §14.1, « Degrés et radians » (`manual:section:14.01`),
§14.5, « Le radian mesure naturellement une rotation », et §14.7,
« Mesurer et lire une rotation », sous-partie sur la calculatrice.
Cahier §14.1 A–C traite les conversions; §14.5 A–C relie angle, rayon et
arc; **§14.7 C** (`workbook:section:14.07`) demande explicitement de
diagnostiquer `sin(π/6) ≈ 0,0091` en mode degrés.

**Couverture et décision.** `du_cercle_unite_a_la_fonction_sinus` (31)
utilise des radians et relie un tour à `2π`;
`fonctions_trigonometriques_inverses` (34) annonce aussi les radians.
Le diagnostic de mode calculatrice n'a pas été trouvé dans ces sources.
**Améliorer d'abord 31** avec une comparaison de deux saisies représentant
le même angle. Une capsule autonome ne serait justifiée que par un objectif
de diagnostic d'unité distinct, après retour des étudiants.

**Auto-vérification proposée.** Calculer le cosinus de `60°` avec chaque mode :
saisir `60` en degrés et `π/3` en radians; les deux résultats doivent valoir `1/2`.

## 4. Confondre la valeur principale avec toutes les solutions

**Raisonnement incorrect construit.** « `arcsin(√3/2) = π/3`, donc `π/3`
est la seule solution de `sin x = √3/2` dans les réels. »

**Correction et contre-exemple.** `sin(2π/3) = √3/2` fournit immédiatement
une seconde solution. Sur `[0,2π]`, les solutions sont `π/3` et `2π/3`.
Dans les réels, elles sont `π/3 + 2kπ` ou `2π/3 + 2kπ`, avec `k ∈ ℤ`.
La valeur principale de l'arcsinus appartient à `[-π/2,π/2]`; l'équation,
elle, doit être résolue sur l'ensemble demandé. Les deux familles se confondent
pour un sinus égal à 1 ou −1; il ne faut pas compter alors deux familles distinctes.

**Statut de preuve.** Documenté : l'étude exploratoire de Bolema décrit des
ensembles incomplets et l'écriture du seul angle principal (§4.4, tableau des
catégories d'erreurs). Elle porte sur 60 étudiants de première année d'ingénierie,
pas sur MAT0339. [Source primaire : R3](#r3--équations-trigonométriques).

**Livre.** Manuel §16.3, « Fonctions trigonométriques réciproques », puis
§16.4, « Équations trigonométriques élémentaires » (`manual:section:16.04`),
qui sépare un intervalle donné de l'ensemble des réels. Cahier **§16.4 A**
(`workbook:section:16.04`) est exactement `sin x = √3/2` sur `[0,2π]`
puis dans les réels; §16.3 B porte sur `arcsin(sin(5π/6))`.

**Couverture et décision.** `fonctions_trigonometriques_inverses` (34)
inclut déjà l'exemple développé « Valeur principale ou solutions ? » dans
[ses exemples intégrés](worked_examples/fonctions_trigonometriques_inverses.yaml).
Il donne les deux solutions de `sin θ = 1/2` sur un tour puis les deux familles
avec `2kπ`. **Réutiliser ou améliorer cette séquence**, notamment son lien
avec l'exercice du cahier; ne pas qualifier le sujet de couverture manquante.

**Auto-vérification proposée.** Résoudre `sin x = −1/2` sur `[0,2π[` puis
dans les réels. Réponse sur l'intervalle : `7π/6` et `11π/6`; ajouter `2kπ`
à chacune de ces valeurs pour les solutions réelles.

## 5. Transformer toute valeur interdite en asymptote verticale

**Raisonnement incorrect construit.** Pour
`R(x) = (x² − 4)/(x² − x − 6)` : « Le dénominateur est nul en −2 et en 3;
il y a donc deux asymptotes verticales. »

**Correction et vérification.** Le domaine exclut bien −2 et 3. La factorisation
donne `((x − 2)(x + 2))/((x − 3)(x + 2))`, donc
`R(x) = (x − 2)/(x − 3)` sur ce domaine. Près de −2, les valeurs tendent
vers `4/5` : le point `(-2,4/5)` est un trou. En 3, le dénominateur réduit
s'annule et le numérateur vaut 1 : il reste une asymptote verticale.
Une simplification partielle ne suffit pas : `x/x² = 1/x`, pour `x ≠ 0`,
conserve une asymptote en 0 malgré l'annulation d'un facteur.

**Statut de preuve.** **Hypothèse plausible pour ce diagnostic précis**,
explicitement anticipée par le manuel. R1 documente des erreurs voisines de
domaine et de manipulation rationnelle, mais ne vérifie pas à elle seule la
confusion exacte « trou = asymptote ». Aucun taux ni observation locale n'est
attribué à cet exemple. [Source contextuelle : R1](#r1--expressions-rationnelles).

**Livre.** Manuel §5.2, « Prévoir un graphe à partir de l'expression »
(`manual:section:05.02`), compare `x²/x` et `x/x²`; §5.4,
« Du facteur au graphe » (`manual:section:05.04`), développe les trous et
asymptotes avec **un autre quotient**. Cahier **§5.1 B–C**
(`workbook:section:05.01`) contient le quotient `R` utilisé ici et demande de
distinguer zéro, valeurs interdites, trou et asymptote. Ne pas lui attribuer
automatiquement le numéro de section du manuel.

**Couverture et décision.** `fonctions_rationnelles` (15) contient déjà
« Trou ou asymptote verticale ? » et l'exemple intégré « Un facteur disparaît,
pas le trou » dans [ses exemples développés](worked_examples/fonctions_rationnelles.yaml).
**Améliorer la comparaison existante** avec le quotient du cahier réunissant
un trou et un pôle. Une seconde capsule sur la même distinction serait redondante.

**Auto-vérification proposée.** Comparer `x²/x` et `x/x²` près de 0 : les
domaines excluent tous deux 0, mais seul le premier possède un trou en `(0,0)`.

## 6. Rétablir une valeur interdite après annulation d'un facteur

**Raisonnement incorrect construit.** « `(x² − 4)/(x − 2) = x + 2`,
donc la fraction vaut 4 lorsque `x = 2`. »

**Correction et vérification.** L'expression initiale est définie seulement
pour `x ≠ 2`. Pour ces valeurs, on peut diviser par le facteur non nul `x − 2`.
En 2, l'expression initiale reste `0/0`, qui n'est pas défini.
La fonction `g(x) = x + 2` sur tous les réels est une extension de la fonction
initiale; elle n'a pas le même domaine. Conserver la restriction à chaque ligne.

**Statut de preuve.** **Hypothèse plausible pour cette inférence précise**.
R1 documente des annulations invalides et des erreurs de domaine, mais la
persistance d'une restriction après une annulation correcte n'y est pas
directement établie par l'exemple consulté. L'objectif est directement présent
dans le manuel et les scènes. [Source contextuelle : R1](#r1--expressions-rationnelles).

**Livre.** Manuel §3.4, « Opérations et composition »
(`manual:section:03.04`), conserve `x ≠ 2` après simplification du quotient
de deux fonctions; §5.4 impose le domaine avant factorisation. Cahier §3.4 A
(`workbook:section:03.04`) demande les domaines de `f + g`, `fg` et `f/g`
pour `f(x) = √(x + 1)`, `g(x) = 1/(x − 2)`; les trois domaines valent
`[-1,+∞[ \ {2}`. Cahier §5.1 B fournit une autre simplification avec deux
valeurs interdites, qui restent toutes deux exclues.

**Couverture et décision.** `annulation_dans_les_fractions` (43) enseigne
explicitement la conservation des restrictions dans son acte algébrique et
son récapitulatif. `fonctions_rationnelles` (15) l'illustre et l'évalue;
`egalite_de_fonctions` (40) explique pourquoi le domaine fait partie de la
fonction. **Réutiliser 43 et 15**, puis améliorer leur renvoi au livre si le
diagnostic le justifie. Ne pas créer une nouvelle capsule pour répéter cet objectif.

**Auto-vérification proposée.** Réduire `(x² − 1)/(x − 1)` en conservant le
domaine : `x + 1` pour `x ≠ 1`. Demander séparément la valeur en 1 de
l'expression initiale : elle n'existe pas.

## Sources primaires et portée de la recherche

### R1 — Expressions rationnelles

Schnepper et McCoy (2013),
[« Analysis of Misconceptions in High School Mathematics »](https://files.eric.ed.gov/fulltext/EJ1152503.pdf),
*Networks*, 15(1), notamment « Error Type 2 » et « Error Type 5 ». Étude de classe auprès de 38 élèves
d'Algèbre II, avec entretiens de cinq volontaires. Les exemples observés
comprennent l'annulation d'un terme dans une somme et une confusion entre
zéro d'une fonction et valeur exclue de son domaine. Cette étude n'établit pas
la fréquence des six diagnostics de cette banque.

Complément bibliographique : Ruhl, Belward et Balatti (2011),
[« A Systematic Analysis of Errors in the Simplification of a Rational Expression »](https://researchonline.jcu.edu.au/21097/),
actes de Volcanic Delta, p. 314–321. Le résumé du dépôt décrit l'analyse de
95 productions universitaires **sélectionnées parce que leur simplification
était incorrecte**; cet effectif n'est pas une estimation de prévalence.
Seuls le résumé et les métadonnées ont été consultés pour ce complément.

### R2 — Transformations trigonométriques

Francis Youbi (2025),
[« Exploring the challenges of learning transformations of trigonometric functions by senior phase mathematics preservice teachers at a KwaZulu-Natal university »](https://researchspace.ukzn.ac.za/items/f71be535-a5f2-4af2-9685-25ef1f56ea9f),
thèse de doctorat, University of KwaZulu-Natal.
[Texte intégral consulté](https://researchspace.ukzn.ac.za/server/api/core/bitstreams/da972ec3-0422-446c-b2ab-b8f822aa29f1/content).
Le résumé annonce 125 enseignants en formation en première année et cinq
entretiens. Les observations locales à cette formation ne donnent pas un taux
applicable aux étudiants de MAT0339. Les exemples et corrections de cette banque
ont été vérifiés mathématiquement indépendamment du texte de recherche.

### R3 — Équations trigonométriques

[« Errores en la Resolución de Ecuaciones Trigonométricas: un Estudio Exploratorio con Estudiantes de Primer Año de Ingeniería »](https://www.scielo.br/j/bolema/a/YjNnLWWKfbN9ByDFHzCvwWH/?format=html&lang=es),
*Bolema*, 37(75), 2023, DOI 10.1590/1980-4415v37n75a16.
Étude primaire de 60 étudiants au moyen de trois tâches écrites; la catégorie
des ensembles de solutions incomplets est explicitée en §4.4 et dans le tableau
des erreurs. Cette preuve concerne les tâches et participants étudiés.

### Limites et usage

La recherche est ciblée, non systématique. Les mécanismes précis des fiches 5
et 6 restent signalés comme plausibles faute de preuve primaire directement
vérifiée dans cette recherche; cela n'affecte pas la vérification mathématique
des contre-exemples. Les fiches 1–4 distinguent aussi le mécanisme documenté
de notre mise en scène pédagogique.

Pour préparer une révision, faire résoudre un diagnostic, demander la raison
du choix, montrer le contre-exemple puis faire résoudre l'auto-vérification sans
la réponse visible. La décision de produire une nouvelle capsule dépendra de
son objectif distinct et du retour pédagogique; cette liste seule ne lance
aucune production. Les observations éventuelles des étudiants se conservent
hors du dépôt public; un bilan partagé doit rester anonyme et agrégé.
