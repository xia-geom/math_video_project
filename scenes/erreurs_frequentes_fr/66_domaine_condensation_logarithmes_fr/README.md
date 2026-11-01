# 66 — Condenser des logarithmes ne change pas le domaine

Classe publique : `DomaineCondensationLogarithmesFR`. Identifiant stable :
`domaine_condensation_logarithmes`.

## Objectif et prérequis

Conserver le domaine original lors de l’application d’une identité logarithmique.
Prérequis : logarithme réel, loi du produit, résolution quadratique et filtrage
des solutions. La capsule 47 traite la fausse loi d’une somme; celle-ci traite
une loi correcte dont on oublierait les conditions.

## Sources Git

Le manuel intégré du 10 octobre 2026, commit
`4d451c37d483d763e33683a7fb683d1e0fdde62d`, fournit l’exemple de la section 6.4
et les contrôles de domaine de la section 6.8. L’exercice de vérification est
exactement le cahier 6.4 B. La révision du 17 octobre, commit
`e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, encore en attente dans la PR 29
lors de la consultation, ne modifie ni cet exemple ni cet exercice. Les
illustrations de domaines et le diagnostic du candidat négatif sont propres
à la capsule.

## Déroulement mathématique

L’exemple est \(\ln(x-1)+\ln(x+1)=\ln8\). Le domaine original est
\(x>1\). La condensation donne \(\ln(x^2-1)=\ln8\), en conservant cette
condition. Les candidats \(3\) et \(-3\) résultent de \(x^2=9\); seul
\(3\) convient. Le candidat \(-3\) donne deux arguments négatifs, même si
leur produit est positif. Deux droites graduées montrent que le domaine
naturel de la formule condensée serait plus large que celui de l’original.

L’exercice demande \(\ln(x-1)+\ln(x+2)=\ln12\). Après une pause de six
secondes, la réponse conserve \(x>1\), résout \(x^2+x-14=0\) et retient
seulement \((-1+\sqrt{57})/2\). La vérification utilise les deux arguments
positifs et leur produit égal à douze, sans approximation prématurée.

## Contrats pédagogiques

- Tous les logarithmes sont réels et leurs arguments sont strictement positifs.
- Une identité conserve ses hypothèses; elle n’autorise pas à élargir le domaine.
- Les domaines représentés se prolongent dans le sens des flèches; les cercles
  ouverts excluent les bornes.
- La question de l’autocontrôle précède sa réponse sur une page distincte.
- L’ouverture UQAM et le service de narration sont ceux des outils partagés.

Le texte français complet est dans les appels `explain` de la scène. Un aperçu
silencieux vérifie la structure et la disposition; il ne certifie ni l’écoute,
ni la durée parlée, ni une diffusion finale.
