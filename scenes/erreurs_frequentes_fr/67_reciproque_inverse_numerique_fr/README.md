# 67 — Fonction réciproque ou inverse d’une valeur ?

Classe publique : `ReciproqueInverseNumeriqueFR`. Identifiant stable :
`reciproque_inverse_numerique`.

## Objectif et complémentarité

Distinguer \(f^{-1}\) de \(1/f\) en comparant les opérations, les domaines
et les contrôles qui les définissent. La vidéo 11 explique la construction
d’une réciproque et affiche déjà l’avertissement final. Cette capsule développe
ce diagnostic avec deux calculs différents sur la même entrée et avec un
point où les domaines diffèrent; elle ne refait pas la réflexion des graphes.

Prérequis : fonction, composition, équation affine et division par un nombre
non nul.

## Sources Git

Le manuel intégré du 10 octobre 2026, commit
`4d451c37d483d763e33683a7fb683d1e0fdde62d`, section 3.5, donne la définition
avec ensembles de départ et d’arrivée, l’exemple \(f(x)=3x-5\) et
l’avertissement \(f^{-1}\ne1/f\) au sens des opérations. Le cahier 3.5 A
demande la réciproque de \(3x-7\) et les deux compositions. La comparaison
à \(1/f\) et les diagrammes numériques sont des ajouts de la capsule.

La révision du 17 octobre, commit
`e418c5ed57338440e1f88dddbea0e0bebc2cfe55`, encore en attente dans la PR 29
lors de la consultation, ne modifie pas ces sections. Le cahier 3.5 C propose
un prolongement rationnel; il n’est pas résolu dans cette capsule.

## Exemples et contrôles

Pour \(f:\mathbb R\to\mathbb R\), \(f(x)=3x-5\), le trajet
\(3\mapsto4\) se défait par \(f^{-1}(4)=3\). En revanche,
\(1/f(4)=1/7\). La réciproque est \(f^{-1}(y)=(y+5)/3\), définie sur
\(\mathbb R\); la fonction \(h(x)=1/(3x-5)\) exclut \(x=5/3\).
La valeur \(f^{-1}(5/3)=20/9\) reste définie. On compare les contrôles
par composition et par multiplication, en conservant les conditions.

L’autocontrôle, après six secondes de réflexion, donne
\(f^{-1}(y)=(y+7)/3\) pour \(f(x)=3x-7\). Les deux compositions sont
vérifiées symboliquement. La fonction \(1/(3x-7)\) exige \(x\ne7/3\).

## Hypothèses et limites

- Pour une fonction \(f:A\to B\), une réciproque sur tout \(B\) exige la
  bijection annoncée. Une restriction des ensembles peut modifier cette question.
- La fonction \(1/f\) est définie là où \(f\) est définie et non nulle;
  elle ne requiert pas l’injectivité.
- Deux opérations différentes peuvent parfois donner la même valeur en un
  point. La capsule compare leur définition et ne prétend pas que leurs valeurs
  sont partout différentes.
- Les diagrammes gardent les entrées et les sorties explicites; les flèches
  du trajet réciproque sont inversées.

La narration française est écrite dans les appels `explain`. Le service partagé,
l’ouverture unique et le mode silencieux explicite sont conservés. Un aperçu
silencieux ne certifie ni la durée parlée, ni l’écoute, ni la diffusion finale.
