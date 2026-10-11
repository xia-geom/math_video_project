# MAT0339 — manuel, cahier, audit et banque d’examens

**Révision de travail : 10 octobre 2026.** Le manuel et les deux cahiers conservent les cinq parties, dix-sept chapitres et 126 sections. Cette révision corrige les 21 constats de septembre, précise plusieurs autres exemples et reprend la langue du manuel et du cahier pour des explications plus directes.

Les contrôles et leurs limites sont consignés dans [le rapport de révision](docs/revision-2026-10-10.md). Les sources, une compilation réussie et une relecture pédagogique ne constituent pas la même preuve. Les PDF restent des documents de travail.

## Lire les documents

Les trois PDF locaux sont produits par `make all` dans `dist/` (répertoire ignoré par Git) :

- [Manuel](dist/MAT0339_manuel_2026-10-10.pdf).
- [Cahier étudiant](dist/MAT0339_cahier_etudiant_2026-10-10.pdf).
- [Cahier avec réponses](dist/MAT0339_cahier_reponses_2026-10-10.pdf).
- [Examens révisés et compte rendu de relecture](exams/2026-10-10/README.md).
- [Correspondance avec les capsules vidéo](curriculum/video-map.md).

Les [PDF du 5 septembre](releases/2026-09-05/), l'[audit du 6 septembre](audits/2026-09-06/RAPPORT_AUDIT.md) et la [banque d'examens initiale](exams/2026-09-06/README.md) restent conservés sans modification. Ils ne contiennent pas les corrections d'octobre.

Les réponses brèves du cahier ne sont pas un corrigé détaillé de chaque exercice. La banque d’examens est une proposition de travail : les durées, le découpage et l’équivalence de difficulté entre séries restent à valider pédagogiquement.

## Organisation

```text
books/mat0339/
  sources/
    manual/                 # préambule, ouverture, conclusion et 17 chapitres
    workbook/               # mêmes chapitres; main.tex étudiant, answers.tex avec réponses
  originals/2026-08/        # deux sources originales intégrales, conservées à l’identique
  curriculum/               # correspondances livre–cahier–capsules
  docs/                     # provenance, registre des modifications, relecture
  audits/2026-09-06/        # audit historique des PDF de septembre
  exams/2026-09-06/         # banque initiale archivée
  exams/2026-10-10/         # sujets et corrigés révisés, provenance et relecture
  scripts/                  # compilation et contrôles limités au livre
  tests/                    # régressions mathématiques ciblées
  releases/2026-09-05/      # trois PDF datés du manuel et du cahier
  build/                    # intermédiaires locaux, ignorés par Git
  dist/                     # dernières compilations locales, ignorées par Git
```

Les scènes, narrations, ressources vidéo et leurs scripts restent dans leurs répertoires existants. Les répertoires `releases/` contiennent uniquement des instantanés explicitement construits; ils ne signifient pas qu’une publication pédagogique a été approuvée.

## Modifier et compiler

Modifier uniquement les sources actives dans `sources/`. Les fichiers `originals/2026-08/` sont des archives, pas des copies de travail. Les environnements et couleurs sont définis dans le préambule de chaque document. Les dessins TikZ restent dans les chapitres; aucun fichier de police n’est distribué.

Prérequis : Python 3.11 ou ultérieur, `make`, `latexmk`, pdfLaTeX, `pdfinfo`, et une distribution TeX incluant le français, TikZ/PGFPlots, tcolorbox, newpx et Source Sans Pro. Aucune dépendance Manim, Azure ou réseau n’est nécessaire à la compilation du livre.

Depuis la racine du dépôt :

```sh
make -C books/mat0339 verify   # archives, alignement, renvois et tests ciblés
make -C books/mat0339 all      # manuel + cahier étudiant + cahier avec réponses
make -C books/mat0339 manual   # manuel seulement
make -C books/mat0339 student  # cahier sans réponses
make -C books/mat0339 answers  # cahier avec réponses brèves
```

La date commune figure dans `sources/edition.tex`; elle détermine les couvertures, les noms des sorties et la date fixe de compilation.

La compilation du manuel utilise `-no-shell-escape`, des sorties isolées et une date de contenu fixe. Les deux versions du cahier proviennent des mêmes chapitres. Les dates de contenu fixes ne garantissent pas un PDF identique entre versions différentes de TeX; le manifeste enregistre le moteur et les empreintes réelles.

`make -C books/mat0339 release` crée un nouvel instantané pour la date configurée et refuse d’écraser des PDF déjà archivés. Pour une révision ultérieure, choisir une nouvelle date d’édition, actualiser les métadonnées, les noms de sortie et les liens; ne pas supprimer l’ancien instantané pour contourner cette protection.

## Vérification et droits

La compilation réussie ne prouve pas la justesse de toutes les mathématiques. Les tests contrôlent des exemples identifiés, pas chaque exercice du cours. La numérotation des sections est conservée afin de maintenir les renvois du cahier. Le registre `docs/issues.json` relie les constats de septembre aux corrections et aux preuves de la révision d'octobre; le rapport historique reste inchangé. Les cartes vidéo attestent la présence de sources de capsules, pas une vérification de leurs rendus finaux.

Voir [la notice conservée du manuel](NOTICE.md) : le texte original interdit la vente et l’utilisation commerciale. La licence Apache du code vidéo ne remplace pas cette notice propre aux documents pédagogiques.

## Examens et correspondance vidéo

```sh
python3 books/mat0339/scripts/build_exams.py
python3 books/mat0339/scripts/video_map.py         # vérifier la carte
python3 books/mat0339/scripts/video_map.py --write # régénérer ses liens
```

Les associations livre-vidéos utilisent les `lesson_id` stables du catalogue unifié. Les titres, numéros et chemins sont générés depuis ce catalogue. La carte n'est pas une dépendance de compilation des PDF.

L'assemblage des recueils d'examens nécessite `pypdf`. Si ce module se trouve dans un autre environnement Python, ajouter `--pdf-python /chemin/vers/python-avec-pypdf` à la commande de compilation des examens.

Les nouvelles compilations restent dans `dist/`; cette révision ne crée aucune publication ni livraison Drive.
