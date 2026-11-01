# MAT0339 — Audit approfondi et deuxième lot de capsules

**Date du lot : 31 octobre 2026.** Les quatorze capsules **44–57** ont été
réexaminées et les huit capsules **58–65** sont implémentées. Le lot comporte
**22 prévisualisations silencieuses finales**, leurs textes français de narration
et un catalogue de correspondance avec les livres. Le [relevé vérifiable](verification.json)
conserve les empreintes, instants d’inspection, contrôles et limites par capsule.

## Sources et périmètre

La référence intégrée reste le manuel et le cahier de l’édition du **10 octobre
2026**, présents dans `main` au commit `4d451c37d483d763e33683a7fb683d1e0fdde62d`.
La révision du **17 octobre**, commit `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`,
a également été consultée dans la [PR #29](https://github.com/xia-geom/math_video_project/pull/29),
encore non fusionnée lors du contrôle. Les anciennes pièces jointes d’août ne
fondent pas ce travail. Les corrections éditoriales en attente sont distinguées
de la version intégrée; cette tâche ne modifie pas les chapitres des livres.

Le catalogue compte désormais **65 vidéos numérotées : 37 leçons principales et
28 compléments sur les erreurs fréquentes**. Il contient 66 sources de scènes
en comptant l’animation d’identité non numérotée. Les 57 entrées précédentes et
leurs 57 objets de référence aux livres ont été conservés. Les nouvelles
sources, classes, identifiants, prérequis, numéros et noms de livraison sont
cohérents dans le catalogue, la playlist et les correspondances des livres.

## Améliorations du premier lot

| Capsule | Constat et amélioration |
|---|---|
| 48 — Probabilité conditionnelle | L’hypothèse de sélection uniforme d’un membre est maintenant explicite à l’écran et dans le texte de narration. Elle justifie le passage des effectifs aux probabilités. |
| 49 — Indépendance et incompatibilité | Ajout de deux événements indépendants définis sur le même dé équilibré. Le produit des probabilités est vérifié et le critère exact d’indépendance figure dans le rappel. |
| 50 — Trajet et déplacement | L’égalité entre distance parcourue et somme des normes suppose maintenant explicitement un segment rectiligne pour chaque étape. Les détours sont expliqués. La flèche aller retirée ne réapparaît plus pendant le fondu de la page retour. |
| 52 — Arrondi d’un optimum | L’ancienne étiquette du sommet continu est détachée de son groupe après son retrait. Elle ne réapparaît plus à côté du point arrondi pendant la transition. |
| 53 — Amplitude et maximum | Domaine réel, coefficient de fréquence non nul et cas constant `A=0` explicités. L’amplitude est présentée comme non négative; une amplitude nulle est permise. |
| 55 — Fréquence et vitesse angulaire | L’ancien rectangle de mise en évidence est détaché de son groupe; seul le repère final subsiste pendant le fondu sortant. |
| 57 — Onde progressive | Ajout de la dérivation à phase constante qui détermine le sens de propagation, des unités des coefficients et de l’axe vertical. Le chronomètre retiré ne revient plus par-dessus la vitesse pendant le fondu. |

Les capsules **44, 45, 46, 47, 51, 54 et 56** sont conservées après vérification
des hypothèses, domaines, calculs, contre-exemples, exercices et images encodées.
L’impression initiale d’un retour de barre dans 46 a été écartée par inspection
en taille native, mesure des pixels et suivi de la géométrie. Aucun défaut de
barre n’a été retenu et aucune modification de cette source n’a été faite.

## Nouveau lot 58–65

Les références ci-dessous renvoient aux sections actives du manuel (M) et du
cahier (C); les notices locales distinguent les exemples repris des adaptations.

| No | Erreur ciblée et réalisation | Références principales |
|---|---|---|
| 58 | Une valeur de calculatrice ne fournit pas toutes les solutions. Deux familles pour `sin(2x)=√3/2`, filtrage sur `[0,2π]`, contrôle graphique et vérification des extrémités dans l’autocontrôle. | M 16.3, 16.4, 16.7; C 16.3–16.4 |
| 59 | Deux côtés et un angle peuvent déterminer zéro, un ou deux triangles. Construction du cas ambigu, tangence, candidat dégénéré et contrôle de la somme des angles. | M 15.4–15.5; C 15.5 |
| 60 | Un déterminant nul ne suffit pas à conclure à l’incompatibilité. Conservation du second membre, condition `0=k−2`, paramétrage et substitution dans les deux équations. | M 12.7–12.9; C 12.4A, synthèse S1 du chapitre 12; C 12.7A en prolongement |
| 61 | Un comité n’est pas un podium. Les six ordres d’un même groupe expliquent la correction du comptage; l’exercice distingue une personne responsable de deux membres sans rôles distincts. | M 7.8–7.9; C 7.8 |
| 62 | Une liste de valeurs possibles n’est pas une liste d’issues équiprobables. Pièce, regroupement des nombres de piles, grille des 36 couples de dés et modèle de pièce biaisée. | M 8.2, 8.9; C 8.2B–C, 8.4C |
| 63 | Sans remise, les probabilités conditionnelles changent. Retrait d’une boule, arbre actualisé, produit le long d’un chemin et somme de cas disjoints; distinction entre probabilité conditionnelle et marginale. | M 8.3, 8.9; C 8.3C |
| 64 | Les coefficients d’une équation cartésienne donnent une normale. Direction vérifiée par déplacement, substitution et produit scalaire; conditions de non-nullité, multiples et droite verticale. | M 10.2, 10.7; C 10.2 |
| 65 | Les formules d’arc et de secteur exigent des radians. Conversion des unités, fraction de cercle, exemple avec un rayon de 6 cm et diagnostic du mode DEG/RAD. | M 14.1, 14.6–14.7; C 14.6–14.7 |

Chaque nouvelle capsule possède un objectif, des prérequis, un exemple motivé,
une explication visuelle et un exercice différent avec **six secondes de
réflexion** avant une page de réponse. Les huit contenus mathématiques ont reçu
une relecture indépendante de leur auteur. Les solutions et hypothèses ont été
contrôlées par calcul exact, énumération ou calcul numérique selon le problème.

## Défauts trouvés pendant la production

La vérification a conduit à déplacer des étiquettes de cercle et de courbe dans
58, à séparer le paramétrage et sa substitution dans 60, à faire circuler les
cartes de 61 sur des trajectoires distinctes, à corriger l’ordre verbal du
coefficient binomial dans sa narration et à agrandir les cartes de 62 pour que
les fractions ne touchent plus leurs bordures. Des titres trop longs ont été
raccourcis sans réduire la taille de toute la page. Le constructeur de secteur
de 65 a aussi été adapté à l’API Manim installée avant le rendu final.

L’inspection des vidéos a révélé le même défaut de propriété des objets dans
**50, 52, 55, 57, 60 et 61** : un objet retiré individuellement restait membre du
groupe de la page et réapparaissait pendant le fondu de ce groupe. Chaque objet
retiré définitivement est maintenant détaché de son parent. Les scènes ont été
reconstruites et réencodées; les instants qui exposaient le défaut ont été
inspectés de nouveau. Les rendus remplacés sont conservés comme traces de
travail et exclus de la livraison. Le [standard d’enseignement](../../../docs/TEACHING_STANDARD.md)
documente ce cas et demande une inspection du début et du milieu de ces fondus.

## Résultats de vérification

- **22 rendus frais**, de **854 × 480 pixels à 15 images/s**, sans piste audio.
  Chaque source, fermeture des entrées de rendu et vidéo finale correspond à
  son empreinte vérifiée. Le décodage intégral de chaque vidéo avec FFmpeg,
  erreurs fatales activées, a réussi.
- **530 états de construction** : aucun candidat automatique de chevauchement
  entre textes ou de dépassement des marges. L’instrument mesure des états
  stables et ne certifie pas les images intermédiaires.
- **188 pages pédagogiques complètes** inspectées dans les vidéos finales,
  plus **113 images choisies de mouvement, fondu ou réflexion**, soit **301
  images encodées effectivement inspectées**. Il s’agit d’un contrôle d’images
  choisies, pas d’un visionnement continu de tous les films.
- **246 tests ciblés du cours et 24 sous-tests**, puis **64 tests du livre**,
  réussis. Analyse syntaxique et Ruff sur les **22 sources finales**, catalogue,
  prérequis, index générés et espaces Git vérifiés. Les 17 chapitres et 126
  sections des livres restent alignés.
- **Catalogue PDF de cinq pages** compilé et inspecté. Les dernières retouches
  de correspondance ne modifient pas la source du PDF déjà contrôlé.

La suite du cours a précédé les dernières corrections locales de disposition
et de retrait d’objets. Après ces corrections, les scènes concernées ont reçu
une nouvelle construction, un nouveau rendu et une nouvelle inspection des
images; l’analyse syntaxique, Ruff et les empreintes ont été vérifiés sur les
22 sources finales. Le contrôle complet du livre a aussi été répété après la
dernière correction de ses notes de correspondance.

Le passage de Ruff est **limité aux 22 scènes de ce lot**. Les diagnostics
historiques du contrôle Ruff sur l’ensemble du dépôt restent distincts; aucun
passage global de ce contrôle n’est annoncé par le présent rapport.

### Mesures par capsule

La durée ci-dessous est celle de l’aperçu silencieux. Elle ne mesure ni la
durée de parole ni la durée finale d’une leçon narrée.

| No | Capsule | États | Pages complètes | Images encodées inspectées | Aperçu silencieux (s) |
|---|---|---:|---:|---:|---:|
| 44 | Diviser par une inconnue : la solution disparue | 21 | 8 | 11 | 37.73 |
| 45 | Un dénominateur peut changer le sens de l’inégalité | 28 | 10 | 13 | 46.87 |
| 46 | Deux pourcentages opposés ne s’annulent pas | 23 | 8 | 11 | 41.40 |
| 47 | Le logarithme d’une somme : une fausse règle | 23 | 9 | 12 | 43.40 |
| 48 | Probabilité conditionnelle : le groupe de référence | 29 | 10 | 14 | 75.20 |
| 49 | Indépendants et incompatibles | 27 | 9 | 12 | 65.40 |
| 50 | Additionner des déplacements ou des longueurs | 20 | 7 | 10 | 52.60 |
| 51 | Le carré d’une matrice ne se calcule pas case par case | 19 | 7 | 12 | 47.93 |
| 52 | Arrondir une solution optimale peut la rendre impossible | 23 | 8 | 15 | 42.67 |
| 53 | L’amplitude et la hauteur maximale | 19 | 7 | 11 | 35.13 |
| 54 | Le déphasage se lit après factorisation | 18 | 7 | 11 | 33.53 |
| 55 | Tours par minute, radians par seconde et période | 23 | 8 | 14 | 41.20 |
| 56 | Un temps de doublement existe-t-il vraiment ? | 25 | 9 | 13 | 45.27 |
| 57 | Période, longueur d'onde et vitesse de propagation | 30 | 10 | 17 | 50.93 |
| 58 | La calculatrice ne donne pas toutes les solutions trigonométriques | 21 | 8 | 12 | 37.60 |
| 59 | Deux côtés et un angle : zéro, un ou deux triangles | 25 | 9 | 13 | 43.33 |
| 60 | Déterminant nul : aucune solution ou une infinité ? | 28 | 10 | 16 | 45.33 |
| 61 | Un comité n’est pas un podium | 26 | 8 | 15 | 38.60 |
| 62 | Des résultats possibles ne sont pas forcément équiprobables | 22 | 8 | 18 | 40.20 |
| 63 | Sans remise : actualiser les probabilités conditionnelles | 30 | 10 | 23 | 48.33 |
| 64 | Vecteur normal ou vecteur directeur ? | 25 | 9 | 14 | 46.00 |
| 65 | Degrés dans les formules en radians | 25 | 9 | 14 | 58.47 |
| **Total** | **22 capsules** | **530** | **188** | **301** | **1017.13** |

Les textes extraits des enregistrements de narration totalisent **11 050 mots**
selon la méthode enregistrée dans le JSON. Ce comptage représente un script,
sans synthèse vocale ni mesure de temps parlé.

## Reproduction

Depuis la racine du dépôt, avec l’environnement `.venv` du projet :

```bash
.venv/bin/python tools/course_catalog.py check
.venv/bin/python -m pytest -q \
  tests/test_course_catalog.py tests/test_render_curriculum.py \
  tests/test_course_timing.py tests/test_course_review.py \
  tests/test_public_workflow_policy.py tests/test_expanded_teaching.py \
  tests/test_teaching_revision.py tests/test_course_boundaries.py \
  tests/test_syllabus_expansion.py tests/test_course_workflow_syntax.py
PATH="$PWD/.venv/bin:$PATH" make -C books/mat0339 verify
git diff --check
```

Une construction ciblée utilise un index commençant à zéro : `--entry 57`
sélectionne la capsule 58. Choisir un nouveau dossier pour préserver les traces.

```bash
MANIM_DISABLE_VOICEOVER=1 .venv/bin/python scripts/teaching_revision/review.py \
  --entry 57 --all-states --output review_artifacts/recheck_58/construction
```

Le moteur `scripts.render_syllabus_expansion.render_one(entry, output, 'silent',
'ql')` produit les prévisualisations avec empreintes, mesures de flux et horloge
des explications. Les entrées se lisent avec `tools.course_catalog.load_catalog`.
Le décodage complet s’effectue ensuite avec
`ffmpeg -v error -xerror -i CHEMIN_DU_MP4 -f null -`. Regarder les images extraites
aux instants documentés reste une opération distincte.

## État de livraison

Les sources et le compte rendu sont proposés dans la
[PR #27](https://github.com/xia-geom/math_video_project/pull/27), conservée en
brouillon. Le paquet de revue contient seulement les 22 MP4 finaux, leurs
22 textes de narration, ce rapport, le relevé JSON et le catalogue PDF.

La synthèse vocale, l’écoute, l’évaluation de la durée narrée, le visionnement
intégral du mouvement et la revue à la résolution finale restent à effectuer.
Les identifiants du service Speech n’étaient pas disponibles pour ce travail.
Les aperçus gardent leur rythme accéléré de contrôle structurel. Le statut
`release_ready` reste `false`; cette livraison ne fusionne ni ne publie les vidéos.
