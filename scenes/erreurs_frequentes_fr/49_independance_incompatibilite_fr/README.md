# 49 — Indépendance et incompatibilité

Objectif : distinguer l’intersection vide du critère probabiliste d’indépendance.

Sources : manuel MAT0339, § 8.4 « Indépendance » ; cahier, exercice 8.4 B. Sur un dé équilibré, pair et impair sont incompatibles mais pas indépendants : l’intersection a probabilité zéro, le produit vaut \(1/4\). La conclusion générale précise que les deux probabilités doivent être positives ; le cas de l’événement impossible est expliqué.

Animation : sélection des issues d’un dé, puis colonnes et lignes d’une grille de 36 couples équiprobables pour deux dés équilibrés lancés indépendamment. Les neuf cases d’intersection montrent une indépendance compatible avec une intersection non vide.

Autocontrôle : sur un dé équilibré, pair et supérieur à trois ne sont ni incompatibles ni indépendants, puisque l’intersection est \(\{4,6\}\) et \(1/3\ne1/4\). La réponse suit une pause de six secondes.

Classe : `IndependanceIncompatibiliteFR`. Narration et sous-titres passent par `TeachingScene` ; une seule ouverture UQAM est appelée. `MANIM_DISABLE_VOICEOVER=1` sélectionne un aperçu silencieux. Les vérifications du lot sont documentées séparément du statut de diffusion.
