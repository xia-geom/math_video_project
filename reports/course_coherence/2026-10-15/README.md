# Cohérence des 43 vidéos — révision silencieuse avant Azure

Le propriétaire a demandé d’étendre aux **43 vidéos existantes** le traitement
approuvé sur les pilotes 15 et 43, avant toute utilisation d’Azure. Les 43
sources disposent maintenant du même dispositif et d’un MP4 muet complet,
lié aux empreintes des sources actuelles. Aucun média n’a été publié ou
transféré vers Drive.

## Résultat

- Ouverture commune : titre, objectif, signature de la Faculté des sciences
  dessinée par code en bas à gauche. Le bumper centré est remplacé.
- **156 chapitres explicitement rédigés**, soit trois ou quatre par vidéo.
  Chaque rappel conserve la liste et son ordre; seul le chapitre entrant est
  en gras. Aucun compteur « Étape N sur … » n’est ajouté.
- Texte pédagogique, corrections et traits en noir; fonds blancs ou neutres.
  Les labels, cadres et styles de traits portent les distinctions. La
  signature institutionnelle conserve ses couleurs de référence.
- Conclusion commune : trois idées « À retenir », reprise d’un exemple déjà
  corrigé sous « À vous », puis « Fin de la capsule » avec le titre et la
  signature. Maintiens minimaux : **8 / 8 / 3 secondes**. La carte finale
  demeure visible dans la dernière image.
- Les classes publiques, identifiants stables, profils vocaux et modes de
  narration existants sont conservés. Les films promotionnels sont exclus.

Les helpers restent dans `tools/teaching_chapters.py`. Un chapitre qui poursuit
un diagramme peut le masquer temporairement avec `preserve_content=True`;
ses objets, son contexte et l’état antérieur de ses mises à jour sont restaurés.
Un test avec le vrai moteur Manim vérifie notamment qu’un objet déjà figé ne
reprend pas accidentellement ses mises à jour pendant le rappel.

## Rendus et accès local

Le dossier local courant est
`review_artifacts/course_coherence/2026-10-15/final/`.

- `index.html` rassemble les 43 prévisualisations avec les contrôles vidéo
  ordinaires. Il s’agit d’un outil de revue local, sans export de chapitres
  pour un lecteur de diffusion.
- Chaque sous-dossier numéroté contient le MP4, son `STATUS.json`, les
  empreintes d’entrée, les événements de cartes, les états inspectables et
  les références aux rapports de revue.
- `manifest.json` conserve les identités du catalogue et les empreintes
  complètes. La copie textuelle versionnée
  [silent_review_manifest.json](silent_review_manifest.json) donne les
  43 empreintes vidéo, durées et tentatives d’origine.

Les **43 rendus effectifs** sont en 854 × 480 à 15 i/s, soit **106,96 minutes**
de prévisualisation muette. FFprobe confirme l’absence de piste audio dans
chacun. Les 43 fichiers finaux ont été relus et hachés; leurs empreintes
d’entrée correspondent aux sources actuelles. Les 328 cartes structurelles
ont les événements attendus et les maintiens minimaux contrôlés. Le relevé
des états ne signale aucun texte hors cadre ni encre chromatique. Ces mesures
ne remplacent pas l’inspection visuelle et ne prouvent pas l’absence de tout
chevauchement.

`scripts/render_course_coherence.py` sélectionne les leçons depuis le catalogue
unifié, impose le mode muet et remplace le constructeur Azure par une erreur
avant tout appel. Il refuse de remplacer une tentative existante.
`scripts/inspect_course_coherence.py` extrait des images du MP4 encodé;
les nouvelles extractions sont conservées dans des ensembles nommés immuables,
pour ne pas remplacer les images ou conclusions déjà citées par un réviseur.
Les anciens ensembles et les tentatives ayant échoué restent conservés.

Exemples pour une future révision locale :

```bash
python scripts/render_course_coherence.py --output review_artifacts/course_coherence/nouvelle_tentative --jobs 2
python scripts/inspect_course_coherence.py --root review_artifacts/course_coherence/nouvelle_tentative --sample-set revue_v1
```

## Défauts corrigés pendant la revue

| Leçon | Correction corroborée |
|---|---|
| 01 | Encadrer séparément les constantes et coefficients, sans inclure les variables dans un cadre étiqueté « constantes ». |
| 05 | Dégager la conclusion du cercle et du test vertical. |
| 07 | Éclaircir l’intersection, préciser `k > 0` pour la dilatation horizontale et retirer une ancienne courbe d’un nouvel exemple quadratique. |
| 11 | Conserver l’avertissement distinct : `f⁻¹` ne signifie pas `1/f`, avant la nouvelle conclusion. |
| 14 | Séparer la formule et la question initiales des axes et de la courbe. |
| 21 | Garder l’étiquette AB opaque lors de la comparaison avec BA. |
| 32 | Nommer le triangle 3–4–5 et l’angle opposé au côté 4 dans la consigne. |
| 34 | Distinguer la branche principale par un trait épais continu, la courbe complète étant en pointillés. |

Chaque correction visuelle a un nouveau rendu et une vérification d’images
encodées. Les erreurs de l’outil de contrôle, notamment la récursion du getter
de couleur des rectangles Manim, ont été corrigées sans modifier les calculs
des scènes. Elles ne sont pas comptées comme défauts mathématiques des vidéos.

## Vérifications séparées

| Niveau | Résultat et limite |
|---|---|
| Sources | 43 scènes et cinq helpers/scripts compilés; identités, voix et appels de profil comparés au checkpoint `2b3977d`. Catalogue et livre inchangés. |
| Tests de catalogue et contrats | 96 réussis. |
| Helpers et signature | 19 réussis, dont restauration des mises à jour et maintiens des cartes. |
| Régressions étendues | Première exécution : 230 réussies, 12 échecs, 848 sous-tests réussis. Les 12 échecs ont été résolus puis les 12 tests concernés ont réussi : avertissement de la leçon 11 restauré; assertions de couleur et d’ouverture alignées sur le format demandé. Aucun test désactivé. |
| Sous-ensemble des dix ajouts au programme | Fichier de tests complet réexécuté après correction : 34 réussis. Ce sous-ensemble recoupe la ligne précédente. |
| Conservation des preuves | Un test de régression réussi : une extraction ne peut écraser un ensemble déjà revu. |
| Rendus réels | 43 MP4 complets, muets, avec empreintes actuelles; aucune synthèse Azure. |
| Images encodées | Toutes les leçons échantillonnées; cartes et états intermédiaires, plus contrôles natifs ciblés et dernières images. Aucun défaut corroboré encore ouvert dans ce périmètre. |
| Lecture continue | Non effectuée pour les 43 vidéos; les échantillons ne valident pas tous les mouvements et fondus. |
| Écoute et synchronisation audiovisuelle | Non effectuées. Les durées et contextes de narration sont contrôlés dans le code; la voix réelle est délibérément différée selon la demande du propriétaire. |
| Haute résolution et approbation institutionnelle | Non validées par cette livraison de prévisualisations. La signature reste une reconstruction approximative. |

Les journaux de tests et rendus se trouvent sous le dossier local daté, hors
Git. La seule alerte de la suite est la dépréciation existante de
`pkg_resources` dans la dépendance de narration. Les résultats ne certifient
pas une diffusion finale.

## Contraste, signature et catalogue

La méthode de contraste suit la référence
[AudioEye](https://www.audioeye.com/fr/color-contrast-checker/) déjà contrôlée
pendant le pilote. Noir sur blanc : **21:1**; noir sur un panneau neutre
`#F5F5F5` : **19,26:1**. Des fonds gris plus soutenus utilisés dans les schémas
restent au-dessus de 4,5:1 : `#BFBFBF` donne 11,42:1, `#A6A6A6` 8,63:1;
l’intersection éclaircie de la leçon 07 donne environ 7,93:1. Le libellé
atténué de la leçon 21 a été remis en noir opaque. Ces vérifications portent
sur les états de lecture, pas sur chaque pixel d’un fondu.

La référence de signature est l’[image officielle de la Faculté](https://coeurdessciences.uqam.ca/wp-content/uploads/lg_Faculte-sciences-interne-COUL-1.jpg).
La provenance et la comparaison visuelle du pilote sont conservées dans
`assets/branding/` et `reports/chapter_pilot/2026-10-15/`. L’intégration aux
43 ouvertures et fins a été inspectée; elle n’apporte aucune approbation
institutionnelle supplémentaire et ne transforme pas la reconstruction en
géométrie officielle exacte.

Le catalogue français reste celui du pilote :
`books/mat0339/curriculum/catalogue-videos.tex`, 43 entrées, références du
manuel et du cahier dans deux colonnes distinctes. Le PDF existant de trois
pages a été compilé et inspecté pendant le pilote; son empreinte inchangée
figure dans le manifeste. Cette révision n’a pas modifié le texte pédagogique
du livre, ses associations ou la banque de méprises. Aucun nouveau sujet de
vidéo n’est commandé.

## Relectures et portée

- [Erreurs de règles mécaniques](review_mechanical.md) : 01–14, avec les six
  constats initiaux puis leur fermeture sur les nouveaux MP4; avertissement
  de 11 revérifié.
- [Bases algébriques fragiles](review_weak_algebra.md) : 30–43; toutes les
  cartes, échantillons de contenu et compléments de géométrie.
- [Révision rapide](review_quick_revision.md) : 15, comparaisons 30/43,
  contrats des 43 sources et catalogue inchangé.
- [Agent principal](review_root.md) : inspection indépendante des sources
  rédigées par l’autre agent pour 16–29; correction et nouveau contrôle de 21.

Les rôles ChatGPT ont reçu du matériel rendu et consignent les fichiers,
empreintes, horodatages, références de catalogue et limites réellement
inspectés. Leur accord ne constitue pas une preuve d’apprentissage réel.
Les rapports historiques sont conservés; les nouveaux contrôles n’écrasent
pas les constats de leurs versions antérieures.

Le prochain contrôle porte sur la lecture des prévisualisations silencieuses.
Azure, l’écoute, la synchronisation audiovisuelle, la haute résolution et la
diffusion restent des étapes ultérieures distinctes. `release_ready` demeure
faux; aucun push, aucune livraison Drive et aucune publication.
