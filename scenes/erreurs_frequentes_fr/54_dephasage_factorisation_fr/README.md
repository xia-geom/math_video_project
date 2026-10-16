# 54 — Déphasage et factorisation

**Objectif :** lire le déplacement horizontal après factorisation de
l'argument et le vérifier avec un point caractéristique. Prérequis : sinus,
période et translations de graphes.

`sin(2x-pi)=sin(2(x-pi/2))` se lit comme une translation de `sin(2x)` de pi/2
vers la droite. Cinq points caractéristiques et la courbe se déplacent
ensemble. Un contrôle en pi/4 distingue la fonction demandée de celle obtenue
avec le décalage erroné pi.

**Autocontrôle :** factoriser `4x-pi=4(x-C)`; pause de six secondes avant
`C=pi/4`. Ce choix évite le cas `sin(3x-pi)`, où le décalage pi, malgré une
mauvaise factorisation exacte, donnerait accidentellement la même courbe que
pi/3 à une période près. La conclusion signale que les décalages d'une
sinusoïde sont équivalents modulo sa période.

**Sources :** manuel MAT0339, §16.7 « Construire une sinusoïde et retrouver un
angle », rubrique « Erreurs fréquentes »; cahier, exercice 16.2 A, adapté.
Fichiers : `MAT0339_manuel_audite_20260801_0101.tex` et
`MAT0339_cahier_exercices_par_section_20260802_2105.tex`.

**Classe :** `DephasageFactorisationFR`. Narration et sous-titres sont fournis
par `TeachingScene`; `MANIM_DISABLE_VOICEOVER=1` désigne le mode explicitement
silencieux. L'import ne déclenche pas de synthèse vocale.
