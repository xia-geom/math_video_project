# 58 — La calculatrice ne donne pas toutes les solutions

**Objectif :** passer d'une valeur principale à l'ensemble complet des
solutions, puis le restreindre à l'intervalle demandé. Prérequis : cercle
unité, sinus, cosinus et fonctions trigonométriques réciproques.

La capsule résout l'exemple original \(\sin(2x)=\sqrt3/2\) sur
\([0,2\pi]\). Le cercle explique les deux angles de même ordonnée;
la substitution \(u=2x\) et les tours complets donnent deux familles.
La division porte sur toute l'expression, y compris le terme de période.
Le filtrage des entiers donne exactement
\(\{\pi/6,\pi/3,7\pi/6,4\pi/3\}\). Le graphe fournit un contrôle
visuel des quatre intersections, sans remplacer la preuve de complétude.
Les extrémités, bien qu'incluses dans l'intervalle, ne sont pas solutions
de cet exemple.

**Autocontrôle original :** \(\cos(2x)=1\) sur \([0,2\pi]\).
Après six secondes de réflexion, une page séparée explique pourquoi
\(\{0,\pi,2\pi\}\) contient trois solutions distinctes. Les deux
extrémités représentent le même point du cercle mais des valeurs
différentes de la variable.

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch16.tex`, sections 16.3, 16.4
  et 16.7, labels `manual:section:16.03`, `16.04`, `16.07`.
- `books/mat0339/sources/workbook/chapters/ch16.tex`, exercices 16.3 B
  et 16.4 A–B; les exemples animés sont des transferts originaux.
- Référence principale : édition intégrée à `main` au commit
  `4d451c37d483d763e33683a7fb683d1e0fdde62d`. La révision éditoriale
  `e418c5ed57338440e1f88dddbea0e0bebc2cfe55` a également été consultée.

**Classe :** `SolutionsTrigonometriquesCompletesFR`. Une ouverture UQAM;
narration française par `TeachingScene` et le service partagé.
`MANIM_DISABLE_VOICEOVER=1` choisit explicitement une prévisualisation
silencieuse. Une source ou une prévisualisation ne constitue pas une
validation de narration ni une publication. Médias générés hors Git.
