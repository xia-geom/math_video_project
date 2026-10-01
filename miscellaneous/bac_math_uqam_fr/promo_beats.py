"""Single source of spoken copy. Review clocks are explicit fixtures, never speech estimates."""

NARRATION_BEATS = {
    "hook": (
        "À l'UQAM, faites des maths de haut niveau dans une université chaleureuse et à votre écoute !",
    ),
    "human_scale": (
        "Des enseignants accessibles, des petits groupes et une vraie place pour vos questions.",
        "Travaux pratiques et travail supervisé vous aident à progresser.",
    ),
    "research": (
        "Dès le bac, des stages d'été peuvent vous ouvrir les portes de la recherche.",
        "Au CIRGET, explorez la géométrie et la topologie.",
        "Au LaCIM, la combinatoire et l'informatique mathématique.",
        "STATQAM développe la recherche en statistique et en science des données.",
    ),
    "support": (
        "Le mentorat par les étudiants plus avancés vous aide à prendre vos repères.",
        "La Bibliothèque des sciences offre des espaces pour travailler, seul ou en équipe.",
    ),
    "montreal": (
        "Le Complexe des sciences Pierre-Dansereau se trouve au Quartier des spectacles, avec un accès intérieur direct au métro Place-des-Arts.",
        "Une communauté accueillante, ouverte sur le monde.",
    ),
    "close": (
        "Des maths de haut niveau.",
        "Un milieu à votre écoute.",
        "Trois portes d'entrée vers la recherche.",
        "Montréal à votre porte.",
        "Découvrez le bac en mathématiques à l'UQAM.",
    ),
}

# Editing fixtures used ONLY by the visibly labelled silent preview in review.py.
REVIEW_SECONDS = {
    "hook": (8.0,),
    "human_scale": (5.5, 4.0),
    "research": (5.5, 4.0, 4.0, 5.5),
    "support": (5.5, 5.5),
    "montreal": (9.0, 3.5),
    "close": (1.8, 1.8, 2.5, 1.8, 3.5),
}
