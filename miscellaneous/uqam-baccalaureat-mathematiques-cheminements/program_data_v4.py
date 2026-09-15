"""V4-only transcription of the 2026–2027 guide, pp. 9, 13, 18, 22.

Scope: recommended autumn entry, five courses/session. Short labels are for
screen use; official_titles and codes identify the actual courses. Blocks and
alternatives are not guaranteed course offerings. V2/V3 data are unchanged.
"""
from copy import deepcopy
from dataclasses import dataclass

from program_data import PROGRAMS as HISTORICAL_PROGRAMS

SOURCE_URL = "https://math.uqam.ca/wp-content/uploads/sites/23/guide-etudiant_2026-2027.pdf"
SOURCE_YEAR = "2026–2027"
SOURCE_VERSION = "2026-07-24"
VERIFIED_DATE = "2026-09-14"

@dataclass(frozen=True)
class Course:
    title: str
    category: str
    codes: tuple[str, ...]
    official_titles: tuple[str, ...]
    kind: str
    source_page: int
    note: str = ""
    source_url: str = SOURCE_URL
    source_version: str = SOURCE_VERSION

# Identities transcribed from the four grids. No prerequisite arrows are inferred.
IDENTITIES = {
    "Calcul I": ("MAT1115", "Calcul I"),
    "Probabilités I": ("MAT1700", "Probabilités I"),
    "Algèbre linéaire I": ("MAT1250", "Algèbre linéaire I"),
    "Arithmétique et géométrie": ("MAT1150", "Arithmétique et géométrie classique"),
    "Mathématiques algorithmiques": ("MAT1060", "Mathématiques algorithmiques"),
    "Statistique I": ("STT1000", "Statistique I"),
    "Algèbre linéaire II": ("MAT1260", "Algèbre linéaire II"),
    "Analyse I": ("MAT1130", "Analyse I"),
    "Géométries": ("MAT2400", "Géométries"),
    "Théorie des groupes": ("MAT2250", "Théorie des groupes"),
    "Analyse II": ("MAT2150", "Analyse II"),
    "Théorie des anneaux": ("MAT2260", "Théorie des anneaux"),
    "Équations différentielles": ("MAT2191", "Calcul des équations différentielles ordinaires"),
    "Analyse complexe I": ("MAT2160", "Analyse complexe I"),
    "Équations aux dérivées partielles": ("MAT2411", "Équations aux dérivées partielles et physique mathématique"),
    "Algèbre linéaire III": ("MAT3250", "Algèbre linéaire III"),
    "Analyse III": ("MAT3150", "Analyse III"),
    "Introduction à la topologie": ("MAT3400", "Introduction à la topologie"),
    "Géométrie différentielle": ("MAT3560", "Géométrie différentielle"),
    "Laboratoire de statistique": ("STT2100", "Laboratoire de statistique"),
    "Échantillonnage": ("STT2010", "Échantillonnage"),
    "Statistique II": ("STT2000", "Statistique II"),
    "Communication scientifique": ("COM5500", "Introduction à la communication scientifique"),
    "Processus stochastiques": ("MAT2720", "Processus stochastiques"),
    "Plans d'expérience et ANOVA": ("STT2110", "Plans d'expérience et ANOVA"),
    "Régression": ("STT2120", "Régression"),
    "Analyse multivariée": ("STT3100", "Analyse multivariée appliquée"),
    "Biostatistique": ("STT3120", "Biostatistique"),
    "Statistique informatique": ("STT3010", "Statistique informatique"),
    "Apprentissage statistique": ("STT3030", "Apprentissage statistique"),
    "Synthèse": ("STT3200", "Synthèse"),
    "Programmation I": ("INF1120", "Programmation I"),
    "Programmation II": ("INF2120", "Programmation II"),
    "Structures de données et algorithmes": ("INF3105", "Structures de données et algorithmes"),
    "Analyse numérique I": ("MAT2170", "Analyse numérique I"),
    "Algorithmique": ("INF5130", "Algorithmique"),
}
ALTERNATIVES = {
    "INF1120 Programmation I ou INF1035 Informatique pour les sciences": (("INF1120", "INF1035"), ("Programmation I", "Informatique pour les sciences")),
    "Analyse numérique ou processus stochastiques": (("MAT2170", "MAT2720"), ("Analyse numérique I", "Processus stochastiques")),
    "Analyse numérique ou probabilités II": (("MAT2170", "MAT2710"), ("Analyse numérique I", "Probabilités II")),
    "Statistique III ou sujets spéciaux": (("STT3000", "STT3020"), ("Statistique III", "Sujets spéciaux de statistique")),
    "Bases de données ou systèmes": (("INF3080", "INF1070"), ("Bases de données", "Utilisation et administration des systèmes informatiques")),
    "Séminaire de mathématiques": (("MAT3500", "MAT3505", "MAT3510"), ("Séminaire de mathématiques",)),
    "Éthique ou mathématiques dans la société": (("COM5500", "FSM4000", "MAT6221", "PHI1003", "PHI1009"), ("Bloc éthique ou mathématiques dans la société",)),
}
BLOCKS = {"Cours complémentaire", "Cours d'option", "Option mathématiques-statistique", "Spécialisation en mathématiques", "Informatique avancée"}

PROGRAMS = deepcopy(HISTORICAL_PROGRAMS)
for key, program in PROGRAMS.items():
    program.update(source_year=SOURCE_YEAR, source_url=SOURCE_URL,
                   source_version=SOURCE_VERSION, verified_date=VERIFIED_DATE,
                   pathway="Début à l'automne, 5 cours par session")
    for row, semester in enumerate(program["semesters"]):
        for column, old in enumerate(semester):
            title, category, note = old.title, old.category, ""
            if key == "math" and (row, column) == (3, 3):
                title = "Équations aux dérivées partielles"
            if key == "stat" and (row, column) == (1, 2):
                title, category = "Cours d'option", "option"
                note = "Page 13, note 3 : ACT2100 recommandé; ce n'est pas un cours imposé dans cette case."
            if key == "stat" and (row, column) == (3, 3):
                title, category = "Algèbre linéaire II", "mathstat"
            if title in IDENTITIES:
                code, official = IDENTITIES[title]
                codes, titles, kind = (code,), (official,), "course"
            elif title in ALTERNATIVES:
                codes, titles = ALTERNATIVES[title]
                kind = "block" if title == "Éthique ou mathématiques dans la société" else "alternative"
            elif title in BLOCKS:
                codes, titles, kind = (), (title,), "block"
            else:
                raise ValueError(f"Unattributed V4 course: {key}/{row}/{column}: {title}")
            if key.startswith("info_") and (row, column) == (0, 4):
                codes = ("INF1035", "INF1120")
                titles = ("Cours complémentaire", "Informatique pour les sciences", "Programmation I")
                kind = "alternative"
                note = "La grille autorise aussi INF1035 ou INF1120 dans cette case; voir le guide pour le cheminement individuel."
            if key == "info_stat" and (row, column) in {(5, 0), (5, 1)}:
                kind = "block_selection"
                note = "Choix du bloc de spécialisation, page 22, note 4; ne pas présenter comme universellement obligatoire."
            semester[column] = Course(title, category, codes, titles, kind, program["source_page"], note)

for theme in PROGRAMS["math"]["themes"]:
    if theme["id"] == "geometry":
        theme["highlight"] = [position for position in theme["highlight"] if position != (3, 3)]
    if theme["id"] == "analysis":
        theme["highlight"].append((3, 3))
