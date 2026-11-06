# 56 — Un temps de doublement n'existe pas toujours

**Objectif :** vérifier qu'un doublement futur existe avant d'utiliser une
formule logarithmique. Prérequis : modèle exponentiel, logarithmes, domaine
d'une fonction et signe d'un quotient.

L'exemple original \(Q(t)=100(0{,}8)^t\), pour un temps **réel**
\(t\ge0\) mesuré en heures, confronte la cible \(200\) à une courbe
décroissante. Le point animé reste sous \(100\); l'inégalité
\(0<Q(t)\le100\) justifie l'impossibilité pour tout temps futur.
Le calcul formel donne \(\ln2/\ln(0{,}8)\approx-3{,}11\) heures,
hors du domaine demandé. Il ne faut pas prendre la valeur absolue de ce
résultat pour annoncer un doublement. Une cible différente, la moitié
de la quantité initiale, donne une demi-vie positive.

Les hypothèses \(Q_0>0\) et \(b>1\) sont affichées avec la formule du
temps de doublement. Pour \(b=1\) et \(Q_0>0\), le double n'est jamais
atteint. Pour \(Q_0=0\), l'égalité avec le double est vraie à tous les
instants et ne définit pas un temps unique. Le modèle est continu : on ne
confond pas un temps réel exact avec le premier indice entier dépassant
un seuil dans une suite.

**Autocontrôle original :** \(R(t)=80(1{,}25)^t\), avec \(t\ge0\)
réel en heures. Après six secondes de réflexion, la réponse explique
les hypothèses, donne \(T_d=\ln2/\ln(1{,}25)\approx3{,}11\) heures
et vérifie \(R(T_d)=160\) avec le temps exact.

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch06.tex`, sections 6.6
  (`manual:section:06.06`, « Temps caractéristiques ») et 6.8
  (`manual:section:06.08`, « Temps de doublement et demi-vie »).
- `books/mat0339/sources/workbook/chapters/ch06.tex`, exercices 6.5 A–B
  et 6.6 C; les exemples animés sont des exercices de transfert originaux.
- Édition du 10 octobre intégrée à `main` au commit
  `4d451c37d483d763e33683a7fb683d1e0fdde62d`, comparée à la révision
  éditoriale du 17 octobre, commit
  `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`. Les passages utilisés sont
  cohérents dans ces deux états; la seconde révision est encore distincte
  de `main` au moment de cette mise à jour.

**Classe :** `TempsDoublementExistenceFR`. Narration française et
sous-titres par `TeachingScene`, avec le service d'enseignement partagé.
`MANIM_DISABLE_VOICEOVER=1` sélectionne une prévisualisation silencieuse;
sa durée ne représente pas celle de la narration. Aucun rendu ni appel
de synthèse ne se produit à l'import. Les médias générés restent hors Git.
