# 61 — Un comité n'est pas un podium

**Objectif :** décider quels échanges changent réellement le résultat d'un
choix, puis corriger un éventuel comptage multiple. Prérequis : principe
du produit, factorielle, arrangements et combinaisons.

L'exemple du manuel et du cahier compare trois personnes parmi dix :
\(10\times9\times8=720\) podiums, mais
\(\binom{10}{3}=720/3!=120\) comités sans rôles distincts.
Une animation échange deux personnes en conservant les places du podium.
Les rangs changent; l'ensemble des membres reste identique.

Les six ordres de \(A,B,C\) sont présentés explicitement et regroupés
visuellement vers le même ensemble \(\{A,B,C\}\). Chaque groupe de trois
personnes **distinctes** possède exactement six descriptions ordonnées :
c'est cette multiplicité constante qui autorise la division par \(3!\).
Les choix se font sans répétition; la capsule n'applique pas cette division
à des tirages avec répétition ou à des rôles différents.

**Autocontrôle original :** parmi huit personnes distinctes, choisir une
personne responsable et deux autres membres sans rôle distinct. Après six
secondes de réflexion, une page séparée donne
\(8\binom72=8\times7\times6/2!=168\). Seul l'échange des deux membres
est sans effet. Le second comptage \(\binom83\times3=168\) vérifie la
réponse et explique pourquoi diviser par \(3!\) serait incorrect.

**Sources actives dans Git :**

- `books/mat0339/sources/manual/chapters/ch07.tex`, sections 7.8 et 7.9
  (`manual:section:07.08`, `manual:section:07.09`).
- `books/mat0339/sources/workbook/chapters/ch07.tex`, exercices 7.8 A–B.
  L'autocontrôle est un transfert original avec un seul rôle distingué.
- Édition intégrée à `main` au commit
  `4d451c37d483d763e33683a7fb683d1e0fdde62d`, consultée avec la révision
  éditoriale `e418c5ed57338440e1f88dddbea0e0bebc2cfe55`.

**Classe :** `ComiteOuPodiumFR`. Une ouverture UQAM; narration française
et sous-titres par `TeachingScene` et le service partagé.
`MANIM_DISABLE_VOICEOVER=1` sélectionne explicitement une prévisualisation
silencieuse. Médias générés hors Git; narration, écoute et publication
ne sont pas déduites d'une validation de source.
