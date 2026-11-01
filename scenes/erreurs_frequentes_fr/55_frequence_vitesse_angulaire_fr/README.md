# 55 — Fréquence, vitesse angulaire et période

**Objectif :** convertir tours/minute en cycles/seconde et radians/seconde,
puis retrouver la période. Prérequis : radians, proportionnalité et
conversion minute/seconde. L’exemple et l’autocontrôle supposent explicitement
une rotation uniforme antihoraire ; la vitesse angulaire est positive dans
cette convention. Une page distingue le cas horaire, où elle est négative.

Une roue à 18 tours/minute a fréquence \(0{,}3\,\mathrm{Hz}\), vitesse angulaire
\(3\pi/5\,\mathrm{rad/s}\) et période \(10/3\,\mathrm{s}\).
Un point en rotation, un chronomètre, un compteur de tours
et un compteur de radians partagent le même temps. Les compteurs décimaux
sont annoncés comme arrondis; les égalités exactes sont affichées séparément.
Tous les objets dynamiques appartiennent à la page; leurs updaters sont
arrêtés avant le changement de page. Le premier cadre de mise en évidence
est retiré du groupe après son fondu, avant l'apparition du cadre final;
il ne réapparaît donc pas pendant la sortie de page.

**Autocontrôle :** 30 tours/minute dans le sens antihoraire, pause de six
secondes, puis \(0{,}5\,\mathrm{Hz}\), \(\pi\,\mathrm{rad/s}\) et
\(2\,\mathrm{s}\). Les contrôles \(fT=1\) et \(\omega T=2\pi\)
sont expliqués pour ce sens de rotation. Les formules générales
\(|\omega|=2\pi f\) et \(T=2\pi/|\omega|\), pour \(\omega\ne0\),
conservent une fréquence et une période positives dans les deux sens.

**Sources :** manuel MAT0339, §17.1 « Vitesse angulaire »; cahier,
exercice 17.1 A–B. Les sources actives sont
`books/mat0339/sources/manual/chapters/ch17.tex` et
`books/mat0339/sources/workbook/chapters/ch17.tex`, édition du 10 octobre 2026,
également vérifiées dans la révision du 17 octobre.

**Classe :** `FrequenceVitesseAngulaireFR`. `TeachingScene` assure narration
et sous-titres; `MANIM_DISABLE_VOICEOVER=1` choisit explicitement le mode
silencieux. Aucun appel de synthèse ou de publication n'a lieu à l'import.
