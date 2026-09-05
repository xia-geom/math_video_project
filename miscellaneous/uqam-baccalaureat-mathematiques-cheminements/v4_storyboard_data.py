"""Renderer-ready visual specification for the UQAM programme video V4.

V4 replaces the anonymous course matrix with an explicit semester progression.
Only representative courses are shown, always on the row of their recommended
session.  The official guide remains the source of record; this storyboard
reconstructs only the recommended pathway beginning in the fall with five
courses per session.  Its visible label is intentionally undated so that the
overview remains reusable; source vintages stay recorded in the manifest.

The authored duration is intentionally not a round target.  It reflects the
amount of narration and the reading time required by each scene.  A renderer
may extend a scene when speech plus the required tail silence does not fit, but
it must never accelerate the narration to preserve these timings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from program_data import PROGRAMS


FPS = 30
WIDTH = 1280
HEIGHT = 720
FRAME_SIZE_OPTIONS = ((1920, 1080), (1280, 720))
LANGUAGE = "fr-CA"
SOURCE_YEAR = "2025–2026"

NARRATION_CUE_COUNTS = {
    "v4_01_opening": 3,
    "v4_03_course_load": 4,
    "v4_04_complementary_column": 4,
    "v4_05_common_to_specialization": 3,
    "v4_06_fundamental_mathematics": 7,
    "v4_07_statistics": 8,
    "v4_08_mathematics_computing": 5,
    "v4_09_computing_profiles": 6,
    "v4_10_comparison": 7,
    "v4_11_guide": 4,
    "v4_12_conclusion": 4,
}

PATHWAY_LABEL = (
    "Cheminement recommandé — début à l’automne — "
    "5 cours/session"
)

SEMESTER_LABELS = (
    "1re année · Automne",
    "1re année · Hiver",
    "2e année · Automne",
    "2e année · Hiver",
    "3e année · Automne",
    "3e année · Hiver",
)

@dataclass(frozen=True, slots=True)
class ActionWindow:
    """One named animation interval in seconds relative to its scene."""

    action: str
    start: float
    end: float

    def __post_init__(self) -> None:
        if not self.action:
            raise ValueError("An action name cannot be empty.")
        if self.start < 0 or self.end <= self.start:
            raise ValueError(
                f"Invalid action window {self.action!r}: "
                f"{self.start:.2f}–{self.end:.2f}"
            )


@dataclass(frozen=True, slots=True)
class CoursePlacement:
    """A representative course at its audited semester position."""

    row: int
    column: int
    title: str

    @property
    def semester_label(self) -> str:
        return SEMESTER_LABELS[self.row]


@dataclass(frozen=True, slots=True)
class BranchSegment:
    """One formal explanatory segment in a concentration scene."""

    id: str
    action: str
    program_key: str
    heading: str
    description: str
    courses: tuple[CoursePlacement, ...]


@dataclass(frozen=True, slots=True)
class SceneSpec:
    """Complete visual timing and text specification for one scene."""

    id: str
    start: float
    end: float
    title: str
    subtitle: str = ""
    actions: tuple[ActionWindow, ...] = ()
    final_still_hold: float = 0.0

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def narration_cue_ids(self) -> tuple[str, ...]:
        count = NARRATION_CUE_COUNTS[self.id]
        return tuple(f"{self.id}:{index:02d}" for index in range(1, count + 1))


def _course(program_key: str, row: int, column: int) -> CoursePlacement:
    """Resolve and validate a representative course from the audited tables."""

    if program_key not in PROGRAMS:
        raise KeyError(f"Unknown programme key: {program_key!r}")
    if not 0 <= row < len(SEMESTER_LABELS):
        raise ValueError(f"Course row out of range: {row}")
    semesters = PROGRAMS[program_key]["semesters"]
    if not 0 <= column < len(semesters[row]):
        raise ValueError(
            f"Course column out of range for {program_key}, row {row}: {column}"
        )
    return CoursePlacement(row, column, semesters[row][column].title)


BRANCH_SEGMENTS: dict[str, tuple[BranchSegment, ...]] = {
    "v4_06_fundamental_mathematics": (
        BranchSegment(
            id="analysis",
            action="show_analysis",
            program_key="math",
            heading="Analyse et équations",
            description=(
                "Étude des fonctions, des limites et des phénomènes continus."
            ),
            courses=tuple(
                _course("math", row, column)
                for row, column in (
                    (1, 3),
                    (2, 3),
                    (3, 1),
                    (3, 2),
                    (4, 1),
                )
            ),
        ),
        BranchSegment(
            id="algebra",
            action="show_algebra",
            program_key="math",
            heading="Algèbre et structures",
            description=(
                "Étude des structures et des propriétés qui organisent "
                "les objets mathématiques."
            ),
            courses=tuple(
                _course("math", row, column)
                for row, column in (
                    (0, 2),
                    (1, 2),
                    (2, 2),
                    (3, 0),
                    (4, 0),
                )
            ),
        ),
        BranchSegment(
            id="geometry",
            action="show_geometry",
            program_key="math",
            heading="Géométrie et topologie",
            description=(
                "Étude des formes, des espaces et de leurs transformations."
            ),
            courses=tuple(
                _course("math", row, column)
                for row, column in (
                    (0, 3),
                    (2, 1),
                    (3, 3),
                    (5, 0),
                    (5, 1),
                )
            ),
        ),
    ),
    "v4_07_statistics": (
        BranchSegment(
            id="collection",
            action="show_collection",
            program_key="stat",
            heading="Production des données",
            description=(
                "L’échantillonnage et les plans d’expérience encadrent "
                "la collecte."
            ),
            courses=tuple(
                _course("stat", row, column)
                for row, column in ((2, 0), (2, 1), (3, 1))
            ),
        ),
        BranchSegment(
            id="models",
            action="show_models",
            program_key="stat",
            heading="Modélisation et incertitude",
            description=(
                "La régression et les processus stochastiques représentent "
                "les relations et l’incertitude."
            ),
            courses=tuple(
                _course("stat", row, column)
                for row, column in ((2, 2), (3, 0), (3, 2), (4, 0))
            ),
        ),
        BranchSegment(
            id="advanced",
            action="show_advanced",
            program_key="stat",
            heading="Analyses avancées",
            description=(
                "La formation mène à la biostatistique, au calcul statistique "
                "et à l’apprentissage."
            ),
            courses=tuple(
                _course("stat", row, column)
                for row, column in (
                    (4, 1),
                    (4, 2),
                    (5, 0),
                    (5, 1),
                )
            ),
        ),
    ),
    "v4_08_mathematics_computing": (
        BranchSegment(
            id="programming",
            action="show_programming",
            program_key="info_math",
            heading="Programmation",
            description=(
                "Traduction d’une méthode en instructions exécutables."
            ),
            courses=tuple(
                _course("info_math", row, column)
                for row, column in ((1, 4), (2, 3))
            ),
        ),
        BranchSegment(
            id="algorithms",
            action="show_algorithms",
            program_key="info_math",
            heading="Structures de données et algorithmique",
            description=(
                "Organisation de l’information et formalisation des méthodes "
                "de résolution."
            ),
            courses=tuple(
                _course("info_math", row, column)
                for row, column in ((3, 3), (4, 2))
            ),
        ),
        BranchSegment(
            id="systems",
            action="show_systems",
            program_key="info_math",
            heading="Données, systèmes et informatique avancée",
            description=(
                "Passage des fondements aux systèmes et aux domaines "
                "informatiques spécialisés."
            ),
            courses=tuple(
                _course("info_math", row, column)
                for row, column in ((3, 2), (4, 3), (5, 2))
            ),
        ),
    ),
}


# Durations were authored from narration density, visual reading time, and a
# measured Azure Sylvie pass at the uniform -10% rate.  The map-reading scene
# was removed once the semester-labelled maps became self-explanatory.
_AUTHORED_SCENES = (
    (
        "v4_01_opening",
        15.0,
        "Baccalauréat en mathématiques",
        "Comprendre les cheminements et les concentrations",
        (
            ActionWindow("show_kicker", 0.30, 0.80),
            ActionWindow("show_title", 0.80, 1.50),
            ActionWindow("show_math_card", 3.10, 3.65),
            ActionWindow("show_statistics_card", 4.45, 5.00),
            ActionWindow("show_computing_card", 5.80, 6.35),
        ),
        0.0,
    ),
    (
        "v4_03_course_load",
        20.0,
        "Deux rythmes de progression",
        "Le guide présente une grille distincte pour chaque rythme.",
        (
            ActionWindow("show_five", 0.60, 1.15),
            ActionWindow("show_three_years", 3.00, 3.55),
            ActionWindow("show_four", 6.40, 6.95),
            ActionWindow("show_extended_path", 9.00, 9.55),
            ActionWindow("show_load_note", 12.00, 12.55),
        ),
        0.0,
    ),
    (
        "v4_04_complementary_column",
        21.0,
        "Des choix intégrés au cheminement",
        "Certaines sessions réservent une place à la diversification.",
        (
            ActionWindow("show_session", 0.50, 1.05),
            ActionWindow("show_complementary", 3.20, 3.75),
            ActionWindow("show_option", 6.20, 6.75),
            ActionWindow("show_society", 9.20, 9.75),
            ActionWindow("show_choice_note", 11.70, 12.25),
        ),
        0.0,
    ),
    (
        "v4_05_common_to_specialization",
        17.5,
        "Des enseignements communs à la spécialisation",
        "Le cheminement se précise progressivement.",
        (
            ActionWindow("show_common", 0.60, 1.15),
            ActionWindow("show_subjects", 2.40, 4.80),
            ActionWindow("show_transition", 6.10, 6.65),
            ActionWindow("show_concentrations", 7.50, 9.40),
            ActionWindow("show_specialization_note", 11.10, 11.65),
        ),
        0.0,
    ),
    (
        "v4_06_fundamental_mathematics",
        35.5,
        PROGRAMS["math"]["short_title"],
        "Théorie, structures et démonstrations",
        (
            ActionWindow("show_analysis", 0.60, 1.15),
            ActionWindow("show_algebra", 10.40, 10.95),
            ActionWindow("show_geometry", 20.40, 20.95),
        ),
        0.0,
    ),
    (
        "v4_07_statistics",
        38.0,
        PROGRAMS["stat"]["short_title"],
        "Données, modèles et incertitude",
        (
            ActionWindow("show_collection", 0.60, 1.15),
            ActionWindow("show_models", 10.40, 10.95),
            ActionWindow("show_advanced", 21.30, 21.85),
        ),
        0.0,
    ),
    (
        "v4_08_mathematics_computing",
        24.0,
        PROGRAMS["info_math"]["short_title"],
        "Un noyau informatique commun aux deux profils",
        (
            ActionWindow("show_programming", 0.60, 1.15),
            ActionWindow("show_algorithms", 6.20, 6.75),
            ActionWindow("show_systems", 12.80, 13.35),
            ActionWindow("show_profiles_transition", 17.40, 17.95),
        ),
        0.0,
    ),
    (
        "v4_09_computing_profiles",
        32.0,
        "Deux profils dans la concentration informatique",
        "Un même noyau, deux approfondissements disciplinaires",
        (
            ActionWindow("show_math_profile", 0.70, 1.25),
            ActionWindow("show_math_details", 2.00, 3.60),
            ActionWindow("show_statistics_profile", 11.00, 11.55),
            ActionWindow("show_statistics_details", 12.30, 13.90),
            ActionWindow("show_orientation_note", 22.00, 22.55),
            ActionWindow("show_common_note", 26.00, 26.55),
        ),
        0.0,
    ),
    (
        "v4_10_comparison",
        36.0,
        "Comparons les trois concentrations",
        "Objets d’étude et outils privilégiés",
        (
            ActionWindow("show_math", 0.70, 1.25),
            ActionWindow("show_statistics", 3.80, 4.35),
            ActionWindow("show_computing", 6.90, 7.45),
            ActionWindow("show_objects", 10.00, 10.55),
            ActionWindow("show_tools", 14.00, 14.55),
            ActionWindow("show_comparison_note", 18.00, 18.55),
        ),
        0.0,
    ),
    (
        "v4_11_guide",
        22.0,
        "Consulter le guide officiel",
        "Le guide présente l’ensemble des variantes du cheminement.",
        (
            ActionWindow("show_guide", 0.50, 1.05),
            ActionWindow("show_guide_title", 2.10, 2.65),
            ActionWindow("show_loads", 5.20, 5.75),
            ActionWindow("show_starts", 7.50, 8.05),
            ActionWindow("show_prerequisites", 9.80, 10.35),
            ActionWindow("show_url", 12.60, 13.15),
        ),
        0.0,
    ),
    (
        "v4_12_conclusion",
        22.0,
        "Les mathématiques pour comprendre le monde",
        "Une formation pour construire votre avenir",
        (
            ActionWindow("show_logo", 0.40, 1.15),
            ActionWindow("show_world", 1.20, 2.00),
            ActionWindow("show_future", 11.20, 12.00),
            ActionWindow("show_url", 15.20, 15.75),
        ),
        3.0,
    ),
)


def _build_scenes(
    authored: Iterable[
        tuple[
            str,
            float,
            str,
            str,
            tuple[ActionWindow, ...],
            float,
        ]
    ],
) -> tuple[SceneSpec, ...]:
    scenes: list[SceneSpec] = []
    cursor = 0.0
    for scene_id, duration, title, subtitle, actions, final_hold in authored:
        scene = SceneSpec(
            id=scene_id,
            start=cursor,
            end=cursor + duration,
            title=title,
            subtitle=subtitle,
            actions=actions,
            final_still_hold=final_hold,
        )
        if actions and actions[-1].end > duration - final_hold:
            raise ValueError(
                f"Actions in {scene_id} overlap its final still hold."
            )
        scenes.append(scene)
        cursor += duration
    return tuple(scenes)


SCENES = _build_scenes(_AUTHORED_SCENES)
SCENE_BY_ID = {scene.id: scene for scene in SCENES}
SCENE_DURATIONS = {scene.id: scene.duration for scene in SCENES}
TOTAL_DURATION_SECONDS = sum(scene.duration for scene in SCENES)

if TOTAL_DURATION_SECONDS != 283.0:
    raise AssertionError(
        f"Unexpected V4 authored duration: {TOTAL_DURATION_SECONDS:.3f}s"
    )


def validate_storyboard() -> None:
    """Raise a clear error when V4 scene timing or course mapping drifts."""

    expected_ids = tuple(NARRATION_CUE_COUNTS)
    actual_ids = tuple(scene.id for scene in SCENES)
    if actual_ids != expected_ids:
        raise ValueError(
            "V4 scene order does not match the narration contract: "
            f"{actual_ids!r}"
        )
    cursor = 0.0
    for scene in SCENES:
        if abs(scene.start - cursor) > 1e-9:
            raise ValueError(f"Non-contiguous scene start for {scene.id}")
        if scene.duration <= 0:
            raise ValueError(f"Non-positive duration for {scene.id}")
        for action in scene.actions:
            if action.end > scene.duration - scene.final_still_hold:
                raise ValueError(
                    f"Action {action.action!r} exceeds the active interval "
                    f"of {scene.id}"
                )
        cursor = scene.end
    for scene_id, segments in BRANCH_SEGMENTS.items():
        if scene_id not in SCENE_BY_ID:
            raise ValueError(f"Unknown branch scene: {scene_id}")
        for segment in segments:
            for course in segment.courses:
                actual = PROGRAMS[segment.program_key]["semesters"][
                    course.row
                ][course.column].title
                if course.title != actual:
                    raise ValueError(
                        "Stale representative-course title for "
                        f"{segment.program_key}[{course.row}][{course.column}]"
                    )
                if course.semester_label != SEMESTER_LABELS[course.row]:
                    raise ValueError("Course semester label does not match row")


validate_storyboard()


__all__ = [
    "ActionWindow",
    "BRANCH_SEGMENTS",
    "CoursePlacement",
    "FPS",
    "FRAME_SIZE_OPTIONS",
    "HEIGHT",
    "LANGUAGE",
    "NARRATION_CUE_COUNTS",
    "PATHWAY_LABEL",
    "SCENES",
    "SCENE_BY_ID",
    "SCENE_DURATIONS",
    "SEMESTER_LABELS",
    "SOURCE_YEAR",
    "SceneSpec",
    "TOTAL_DURATION_SECONDS",
    "WIDTH",
    "validate_storyboard",
]
