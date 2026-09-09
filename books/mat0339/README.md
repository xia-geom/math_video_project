# MAT0339 — manuel, cahier, audit et banque d’examens

**Dernière révision du manuel : 5 septembre 2026. Audit approfondi : 6 septembre 2026. Statut : édition de travail soumise à relecture, non encore approuvée pour publication.**

Le manuel conserve les cinq parties, dix-sept chapitres et 126 sections de l’édition d’août. La révision du 5 septembre corrige des erreurs ciblées et reconstruit la progression du chapitre 3, sans renuméroter les sections du cahier. L’audit du 6 septembre documente encore 21 anomalies ouvertes, notamment des collisions visuelles et plusieurs corrections mathématiques ou pédagogiques à appliquer. Cette branche ne constitue donc pas une certification exhaustive du cours.

## Lire les documents

- [Manuel révisé](releases/2026-09-05/MAT0339_manuel_2026-09-05.pdf).
- [Cahier étudiant, sans réponses](releases/2026-09-05/MAT0339_cahier_etudiant_2026-09-05.pdf).
- [Cahier avec réponses brèves](releases/2026-09-05/MAT0339_cahier_reponses_2026-09-05.pdf).
- [Audit approfondi du 6 septembre](audits/2026-09-06/RAPPORT_AUDIT.md).
- [Banque de trois séries semestrielles](exams/2026-09-06/README.md) — trois examens par série, avec sujets et corrigés enseignants.
- [Modifications et limites de la révision](docs/revision-2026-09-05.md).
- [Correspondance avec les capsules vidéo](curriculum/video-map.md).

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
  audits/2026-09-06/        # audit approfondi et anomalies restant à corriger
  exams/2026-09-06/         # 3 séries × 3 examens, sujets, corrigés et PDF compilés
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

La compilation du manuel utilise `-no-shell-escape`, des sorties isolées et une date de contenu fixe. Les deux versions du cahier proviennent des mêmes chapitres. Les dates de contenu fixes ne garantissent pas un PDF identique entre versions différentes de TeX; le manifeste enregistre le moteur et les empreintes réelles.

`make -C books/mat0339 release` crée un nouvel instantané pour la date configurée et refuse d’écraser des PDF déjà archivés. Pour une révision ultérieure, choisir une nouvelle date d’édition, actualiser les métadonnées, les noms de sortie et les liens; ne pas supprimer l’ancien instantané pour contourner cette protection.

## Vérification et droits

La compilation réussie ne prouve pas la justesse de toutes les mathématiques. Les tests contrôlent des exemples identifiés, pas chaque exercice du cours. La numérotation des sections est conservée afin de maintenir les renvois du cahier. L’audit du 6 septembre doit être traité comme le registre actif des défauts connus jusqu’à leur correction et revalidation. Les cartes vidéo attestent la présence de sources de capsules, pas une vérification de leurs rendus finaux.

Voir [la notice conservée du manuel](NOTICE.md) : le texte original interdit la vente et l’utilisation commerciale. La licence Apache du code vidéo ne remplace pas cette notice propre aux documents pédagogiques.
