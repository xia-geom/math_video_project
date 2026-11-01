# 53 — Amplitude et maximum

**Objectif :** lire l'amplitude comme distance à la médiane et distinguer
coefficient signé, maximum, minimum et écart total. Prérequis : sinus, cosinus,
translation verticale et lecture d'un graphe.

L'exemple \(f(x)=-4\cos(3x)+2\) a amplitude \(4\), médiane \(2\), maximum
\(6\) et minimum \(-2\). La courbe \(2+4\cos(3x)\) est réfléchie autour de
la médiane pour devenir celle de l'exemple; ses extrema et deux flèches de
longueur \(4\) rendent visibles les distances conservées. Le calcul des valeurs
en \(0\) et \(\pi/3\) vérifie les extrêmes. Le rappel final précise la forme
\(A\cos(B(x-C))+D\), avec \(B\ne0\), et affiche que les extrema sont pris
sur tous les réels. Un cycle complet suffit lorsque \(A\ne0\); sur un
intervalle plus court, les deux hauteurs peuvent ne pas être atteintes.
Le cas \(A=0\) est distingué : fonction constante, amplitude nulle et
maximum comme minimum égaux à \(D\). L'amplitude est donc une distance
non négative, pas nécessairement strictement positive.

**Autocontrôle :** \(3\sin(2x)-1\), avec pause de six secondes; amplitude
\(3\), médiane \(-1\), maximum \(2\) et minimum \(-4\).

**Sources :** manuel MAT0339, §16.2 « Amplitude, période, déphasage et ligne
médiane » et §16.7 « Construire une sinusoïde et retrouver un angle »;
cahier, exercice 16.6 B. Les références portent sur les sources actives du
dépôt, dans `books/mat0339/sources/`.

**Classe :** `AmplitudeMaximumFR`. La narration et les sous-titres utilisent
`TeachingScene`; le mode de prévisualisation explicitement silencieux est
`MANIM_DISABLE_VOICEOVER=1`. L'import du module ne synthétise aucune voix.

Sources Git contrôlées : [manuel, chapitre 16](../../../books/mat0339/sources/manual/chapters/ch16.tex) et [cahier, chapitre 16](../../../books/mat0339/sources/workbook/chapters/ch16.tex). Le [plan du lot](../../../reports/error_capsules/2026-10-30/PLAN.md) distingue l’édition du 10 octobre intégrée et la révision éditoriale du 17 octobre consultée.
