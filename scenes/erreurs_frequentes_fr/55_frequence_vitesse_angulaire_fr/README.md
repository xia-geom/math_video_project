# 55 — Fréquence, vitesse angulaire et période

**Objectif :** convertir tours/minute en cycles/seconde et radians/seconde,
puis retrouver la période. Prérequis : radians, proportionnalité et
conversion minute/seconde. On suppose une rotation uniforme antihoraire;
la vitesse angulaire est positive dans cette convention.

Une roue à 18 tours/minute a fréquence 0.3 Hz, vitesse angulaire 3pi/5 rad/s
et période 10/3 s. Un point en rotation, un chronomètre, un compteur de tours
et un compteur de radians partagent le même temps. Les compteurs décimaux
sont annoncés comme arrondis; les égalités exactes sont affichées séparément.
Tous les objets dynamiques appartiennent à la page; leurs updaters sont
arrêtés avant le changement de page.

**Autocontrôle :** 30 tours/minute, pause de six secondes, puis 0.5 Hz,
pi rad/s et 2 s. Les contrôles `f*T=1` et `omega*T=2pi` sont expliqués.

**Sources :** manuel MAT0339, §17.1 « Vitesse angulaire »; cahier,
exercice 17.1 A–B. Fichiers de référence :
`MAT0339_manuel_audite_20260801_0101.tex` et
`MAT0339_cahier_exercices_par_section_20260802_2105.tex`.

**Classe :** `FrequenceVitesseAngulaireFR`. `TeachingScene` assure narration
et sous-titres; `MANIM_DISABLE_VOICEOVER=1` choisit explicitement le mode
silencieux. Aucun appel de synthèse ou de publication n'a lieu à l'import.
