"""Audited course-map data for the UQAM mathematics program introduction.

The four grids below reconstruct the recommended pathways beginning in the
fall with five courses per semester from pages 9, 13, 18 and 22 of the
Guide de la personne étudiante 2025-2026.

The video does not display every title simultaneously.  It uses these exact
positions to build a muted pathway table and highlights a few representative
courses for each theme.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Course:
    title: str
    category: str = "mathstat"


# Categories follow the visual role used by the source tables, not an official
# semantic classification of every course.
M = "mathstat"
I = "info"
O = "option"
C = "complement"
CONTEXT = "context"


def c(title: str, category: str = M) -> Course:
    return Course(title, category)


PROGRAMS: dict[str, dict] = {
    "math": {
        "title": "Concentration mathématiques fondamentales",
        "short_title": "Concentration mathématiques fondamentales",
        "source_page": 9,
        "semesters": [
            [c("Calcul I"), c("Probabilités I"), c("Algèbre linéaire I"), c("Arithmétique et géométrie"), c("INF1120 Programmation I ou INF1035 Informatique pour les sciences", I)],
            [c("Mathématiques algorithmiques"), c("Statistique I"), c("Algèbre linéaire II"), c("Analyse I"), c("Cours complémentaire", C)],
            [c("Analyse numérique ou processus stochastiques", O), c("Géométries"), c("Théorie des groupes"), c("Analyse II"), c("Cours complémentaire", C)],
            [c("Théorie des anneaux"), c("Équations différentielles"), c("Analyse complexe I"), c("Formes différentielles"), c("Éthique ou mathématiques dans la société", CONTEXT)],
            [c("Algèbre linéaire III"), c("Analyse III"), c("Séminaire de mathématiques"), c("Cours d'option", O), c("Cours complémentaire", C)],
            [c("Introduction à la topologie"), c("Géométrie différentielle"), c("Séminaire de mathématiques"), c("Cours d'option", O), c("Cours complémentaire", C)],
        ],
        "themes": [
            {
                "id": "analysis",
                "title": "Analyse et équations",
                "phrase": "Fonctions, limites et phénomènes continus",
                "highlight": [(1, 3), (2, 3), (3, 1), (3, 2), (4, 1)],
                "labels": [(2, 3), (3, 1), (3, 2)],
            },
            {
                "id": "algebra",
                "title": "Algèbre et structures",
                "phrase": "Comprendre les règles derrière les objets",
                "highlight": [(0, 2), (1, 2), (2, 2), (3, 0), (4, 0)],
                "labels": [(2, 2), (3, 0), (4, 0)],
            },
            {
                "id": "geometry",
                "title": "Géométrie et espaces",
                "phrase": "Étudier les formes et leurs transformations",
                "highlight": [(0, 3), (2, 1), (3, 3), (5, 0), (5, 1)],
                "labels": [(2, 1), (5, 0), (5, 1)],
            },
            {
                "id": "seminar",
                "title": "Séminaire et options",
                "phrase": "Approfondir un sujet et le présenter",
                "highlight": [(4, 2), (4, 3), (5, 2), (5, 3)],
                "labels": [(4, 2), (5, 3)],
            },
        ],
    },
    "stat": {
        "title": "Concentration statistique",
        "short_title": "Concentration statistique",
        "source_page": 13,
        "semesters": [
            [c("Calcul I"), c("Probabilités I"), c("Algèbre linéaire I"), c("Arithmétique et géométrie"), c("INF1120 Programmation I ou INF1035 Informatique pour les sciences", I)],
            [c("Mathématiques algorithmiques"), c("Statistique I"), c("Algèbre linéaire II"), c("Analyse I"), c("Cours complémentaire", C)],
            [c("Laboratoire de statistique"), c("Échantillonnage"), c("Statistique II"), c("Analyse II"), c("Communication scientifique", CONTEXT)],
            [c("Processus stochastiques"), c("Plans d'expérience et ANOVA"), c("Régression"), c("Cours d'option", O), c("Cours complémentaire", C)],
            [c("Analyse numérique ou probabilités II", O), c("Analyse multivariée"), c("Biostatistique"), c("Statistique III ou sujets spéciaux"), c("Cours complémentaire", C)],
            [c("Statistique informatique"), c("Apprentissage statistique"), c("Synthèse"), c("Cours d'option", O), c("Cours complémentaire", C)],
        ],
        "themes": [
            {
                "id": "collection",
                "title": "Recueillir de bonnes données",
                "phrase": "Échantillonnage, laboratoire et expériences",
                "highlight": [(2, 0), (2, 1), (3, 1)],
                "labels": [(2, 0), (2, 1), (3, 1)],
            },
            {
                "id": "models",
                "title": "Modèles et incertitude",
                "phrase": "Décrire des relations sans tout connaître",
                "highlight": [(2, 2), (3, 0), (3, 2), (4, 0)],
                "labels": [(3, 0), (3, 2), (4, 0)],
            },
            {
                "id": "advanced",
                "title": "Analyses avancées",
                "phrase": "Plusieurs variables et domaines d'application",
                "highlight": [(4, 1), (4, 2), (4, 3)],
                "labels": [(4, 1), (4, 2), (4, 3)],
            },
            {
                "id": "learning",
                "title": "Calcul et apprentissage",
                "phrase": "Mettre les méthodes en œuvre par ordinateur",
                "highlight": [(5, 0), (5, 1), (5, 2)],
                "labels": [(5, 0), (5, 1), (5, 2)],
            },
        ],
    },
    "info_math": {
        "title": "Concentration informatique — profil mathématiques",
        "short_title": "Concentration informatique",
        "source_page": 18,
        "semesters": [
            [c("Calcul I"), c("Probabilités I"), c("Algèbre linéaire I"), c("Arithmétique et géométrie"), c("Cours complémentaire", C)],
            [c("Mathématiques algorithmiques"), c("Statistique I"), c("Algèbre linéaire II"), c("Analyse I"), c("Programmation I", I)],
            [c("Laboratoire de statistique"), c("Théorie des groupes"), c("Option mathématiques-statistique", O), c("Programmation II", I), c("Éthique ou mathématiques dans la société", CONTEXT)],
            [c("Processus stochastiques"), c("Théorie des anneaux"), c("Bases de données ou systèmes", I), c("Structures de données et algorithmes", I), c("Cours complémentaire", C)],
            [c("Analyse numérique I"), c("Spécialisation en mathématiques", O), c("Algorithmique", I), c("Informatique avancée", I), c("Cours complémentaire", C)],
            [c("Option mathématiques-statistique", O), c("Spécialisation en mathématiques", O), c("Informatique avancée", I), c("Informatique avancée", I), c("Cours complémentaire", C)],
        ],
    },
    "info_stat": {
        "title": "Concentration informatique — profil statistique",
        "short_title": "Concentration informatique",
        "source_page": 22,
        "semesters": [
            [c("Calcul I"), c("Probabilités I"), c("Algèbre linéaire I"), c("Arithmétique et géométrie"), c("Cours complémentaire", C)],
            [c("Mathématiques algorithmiques"), c("Statistique I"), c("Algèbre linéaire II"), c("Analyse I"), c("Programmation I", I)],
            [c("Laboratoire de statistique"), c("Statistique II"), c("Option mathématiques-statistique", O), c("Programmation II", I), c("Éthique ou mathématiques dans la société", CONTEXT)],
            [c("Processus stochastiques"), c("Régression"), c("Bases de données ou systèmes", I), c("Structures de données et algorithmes", I), c("Cours complémentaire", C)],
            [c("Analyse numérique I"), c("Option mathématiques-statistique", O), c("Algorithmique", I), c("Informatique avancée", I), c("Cours complémentaire", C)],
            [c("Statistique informatique"), c("Apprentissage statistique"), c("Informatique avancée", I), c("Informatique avancée", I), c("Cours complémentaire", C)],
        ],
    },
}

INFO_THEMES = [
    {
        "id": "programming",
        "title": "Programmer",
        "phrase": "Traduire une méthode en instructions",
        "program": "info_math",
        "highlight": [(1, 4), (2, 3)],
        "labels": [(1, 4), (2, 3)],
    },
    {
        "id": "algorithms",
        "title": "Données et algorithmes",
        "phrase": "Organiser l'information et résoudre efficacement",
        "program": "info_math",
        "highlight": [(3, 3), (4, 2)],
        "labels": [(3, 3), (4, 2)],
    },
    {
        "id": "systems",
        "title": "Bases de données et informatique avancée",
        "phrase": "Passer des fondements aux applications",
        "program": "info_math",
        "highlight": [(3, 2), (4, 3), (5, 2), (5, 3)],
        "labels": [(3, 2), (4, 3)],
    },
    {
        "id": "profiles",
        "title": "Deux profils",
        "phrase": "Mathématiques ou Statistique (science des données)",
        "program": "info_math",
        "highlight": [],
        "labels": [],
    },
]

COMMON_FOUNDATION = [
    "Calcul",
    "Algèbre linéaire",
    "Probabilités",
    "Statistique",
    "Analyse",
    "Mathématiques algorithmiques",
    "Informatique / programmation",
]
