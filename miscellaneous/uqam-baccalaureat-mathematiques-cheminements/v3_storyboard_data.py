"""Renderer-ready data for the 3:35 V3 UQAM program storyboard.

All times in ``SceneSpec`` are absolute program times in seconds.  Times in
``ConceptSegment`` and ``ActionWindow`` are relative to the start of their
scene.  Narration text lives exclusively in ``voiceover_v3_fr.txt``; the cue
IDs below identify its authored, sentence-level lines in order.
"""

from __future__ import annotations

from dataclasses import dataclass


FPS = 30
FRAME_SIZE_OPTIONS = ((1920, 1080), (1280, 720))
TARGET_DURATION_SECONDS = 215.0
LANGUAGE = "fr-CA"

BACKGROUND = "#F7F8FA"
SURFACE = "#FFFFFF"
INK = "#18212B"
MUTED = "#69737D"
GRID = "#E6E9ED"

MATH_ACCENT = "#3157D5"
STATISTICS_ACCENT = "#008A7A"
COMPUTING_ACCENT = "#E15B45"
COMPLEMENTARY_ACCENT = "#F2E6C9"

CARD_CORNER_RADIUS = (14, 18)
CARD_BORDER_WIDTH = 1
INACTIVE_CARD_OPACITY = (0.20, 0.30)
EASED_MOVEMENT_SECONDS = (0.35, 0.55)
MINIMUM_REVEAL_HOLD_SECONDS = 0.70


@dataclass(frozen=True, slots=True)
class ConceptSegment:
    """A named concept presented during a scene."""

    id: str
    start: float
    end: float
    on_screen: str
    highlighted_course_labels: tuple[str, ...] = ()
    visual: str = ""
    summary_line: str = ""


@dataclass(frozen=True, slots=True)
class ActionWindow:
    """An explicit animation or visual hold window from the storyboard."""

    start: float
    end: float
    action: str
    targets: tuple[str, ...] = ()
    detail: str = ""


@dataclass(frozen=True, slots=True)
class SceneSpec:
    """Complete timing and content specification for one V3 scene."""

    id: str
    start: float
    end: float
    title: str
    subtitle: str = ""
    on_screen_phrases: tuple[str, ...] = ()
    table_programs: tuple[str, ...] = ()
    segments: tuple[ConceptSegment, ...] = ()
    actions: tuple[ActionWindow, ...] = ()
    narration_cue_ids: tuple[str, ...] = ()
    visual_notes: tuple[str, ...] = ()

    @property
    def duration(self) -> float:
        return self.end - self.start


def cue_ids(scene_id: str, count: int) -> tuple[str, ...]:
    """Return stable IDs for the authored lines in a narration section."""

    return tuple(f"{scene_id}:{index:02d}" for index in range(1, count + 1))


SCENES: tuple[SceneSpec, ...] = (
    SceneSpec(
        id="v3_01_opening",
        start=0.0,
        end=7.0,
        title="Étudier les mathématiques à l’UQAM",
        subtitle="Une formation commune, plusieurs orientations",
        on_screen_phrases=(
            "Étudier les mathématiques à l’UQAM",
            "Une formation commune, plusieurs orientations",
        ),
        actions=(
            ActionWindow(
                0.0,
                1.2,
                "draw_connecting_line",
                ("line",),
                "Une ligne fine entre par la gauche et traverse l’écran.",
            ),
            ActionWindow(
                1.2,
                2.5,
                "reveal_opening_title",
                ("title", "subtitle"),
                "Le titre apparaît en fondu et monte doucement.",
            ),
            ActionWindow(
                2.5,
                5.5,
                "reveal_mathematical_symbols",
                ("curve", "point_group", "code_bracket"),
                "La courbe, le groupe de points et le crochet de code apparaissent.",
            ),
            ActionWindow(
                5.5,
                7.0,
                "hold",
                ("line", "title", "symbols"),
                "Aucun nouveau mouvement.",
            ),
        ),
        narration_cue_ids=cue_ids("v3_01_opening", 3),
        visual_notes=(
            "Aucune table n’est visible.",
            "La ligne s’arrête au centre.",
        ),
    ),
    SceneSpec(
        id="v3_02_reading_the_table",
        start=7.0,
        end=23.0,
        title="Comment lire le cheminement?",
        on_screen_phrases=(
            "AUTOMNE",
            "HIVER",
            "1 année = Automne + Hiver",
        ),
        actions=(
            ActionWindow(
                0.0,
                2.0,
                "show_empty_table_frame",
                ("two_row_table",),
                "Afficher uniquement le cadre vide de la table simplifiée.",
            ),
            ActionWindow(
                2.0,
                5.0,
                "unfold_autumn_row",
                ("AUTOMNE", "autumn_course_cards"),
                "Le libellé entre, puis cinq cartes sans nom se déploient de gauche à droite.",
            ),
            ActionWindow(
                5.0,
                8.0,
                "unfold_winter_row",
                ("HIVER", "winter_course_cards"),
                "Le libellé entre, puis cinq cartes sans nom se déploient.",
            ),
            ActionWindow(
                8.0,
                12.0,
                "group_academic_year",
                ("autumn_row", "winter_row", "soft_bracket"),
                "Une accolade légère regroupe les deux sessions.",
            ),
            ActionWindow(
                12.0,
                16.0,
                "reveal_year_equation",
                ("1 année = Automne + Hiver",),
                "La relation annuelle apparaît, puis reste lisible.",
            ),
        ),
        narration_cue_ids=cue_ids("v3_02_reading_the_table", 2),
        visual_notes=(
            "Ne montrer aucun nom de cours.",
            "Cette scène enseigne la structure de la grille.",
        ),
    ),
    SceneSpec(
        id="v3_03_course_load",
        start=23.0,
        end=39.0,
        title="Cinq cours ou quatre cours",
        on_screen_phrases=(
            "5 cours par session",
            "4 cours par session",
        ),
        actions=(
            ActionWindow(
                0.0,
                3.0,
                "enter_five_course_cards",
                ("five_equal_cards",),
                "Cinq cartes de même largeur apparaissent.",
            ),
            ActionWindow(
                3.0,
                7.0,
                "activate_five_course_option",
                ("5 cours par session",),
                "L’onglet cinq cours devient actif.",
            ),
            ActionWindow(
                7.0,
                11.0,
                "transform_five_cards_into_four",
                ("course_cards", "timeline"),
                "Transformation continue vers quatre cartes légèrement plus grandes; la ligne du temps s’allonge.",
            ),
            ActionWindow(
                11.0,
                14.0,
                "activate_four_course_option",
                ("4 cours par session",),
                "L’onglet quatre cours devient actif.",
            ),
            ActionWindow(
                14.0,
                16.0,
                "hold",
                ("four_course_cards", "expanded_timeline"),
                "Bref maintien sans nouvelle information.",
            ),
        ),
        narration_cue_ids=cue_ids("v3_03_course_load", 3),
        visual_notes=(
            "Ne jamais qualifier le cheminement à quatre cours de « temps partiel ».",
            "Le guide offre les deux charges et des départs en automne ou en hiver.",
        ),
    ),
    SceneSpec(
        id="v3_04_complementary_column",
        start=39.0,
        end=54.0,
        title="Une place pour personnaliser le parcours",
        on_screen_phrases=(
            "Une place pour personnaliser le parcours",
            "Cours complémentaire",
            "Cours d’option",
            "Éthique ou mathématiques dans la société",
        ),
        actions=(
            ActionWindow(
                0.0,
                3.0,
                "slide_five_columns_into_place",
                ("five_column_row",),
                "Quatre colonnes neutres et une colonne droite crème prennent place.",
            ),
            ActionWindow(
                3.0,
                6.0,
                "lift_complementary_column",
                ("rightmost_column",),
                "La colonne droite avance légèrement.",
            ),
            ActionWindow(
                6.0,
                9.0,
                "show_complementary_label",
                ("Cours complémentaire",),
            ),
            ActionWindow(
                9.0,
                12.0,
                "morph_to_option_label",
                ("Cours d’option",),
            ),
            ActionWindow(
                12.0,
                15.0,
                "morph_to_ethics_label",
                ("Éthique ou mathématiques dans la société",),
            ),
        ),
        narration_cue_ids=cue_ids("v3_04_complementary_column", 3),
        visual_notes=(
            "La colonne distincte utilise un crème neutre, jamais un jaune vif.",
            "N’utiliser qu’un petit repère d’accent.",
        ),
    ),
    SceneSpec(
        id="v3_05_common_foundation",
        start=54.0,
        end=70.0,
        title="Une base largement commune",
        on_screen_phrases=(
            "Calcul",
            "Probabilités",
            "Algèbre linéaire",
            "Statistique",
            "Analyse",
            "Informatique / programmation",
        ),
        table_programs=(
            "mathématiques fondamentales",
            "statistique",
            "concentration informatique",
        ),
        segments=(
            ConceptSegment(
                id="common_first_year",
                start=0.0,
                end=16.0,
                on_screen="Une base largement commune",
                highlighted_course_labels=(
                    "Calcul",
                    "Probabilités",
                    "Algèbre linéaire",
                    "Statistique",
                    "Analyse",
                    "Informatique / programmation",
                ),
                visual="Trois copies translucides du premier niveau se séparent progressivement en trois voies.",
            ),
        ),
        actions=(
            ActionWindow(
                0.0,
                4.0,
                "show_first_year_table",
                ("first_year_table",),
                "Une seule grille de première année apparaît.",
            ),
            ActionWindow(
                4.0,
                7.0,
                "duplicate_common_table",
                ("math_table", "statistics_table", "computing_table"),
                "La grille se duplique en trois copies translucides.",
            ),
            ActionWindow(
                7.0,
                12.0,
                "sequence_common_subject_highlights",
                (
                    "Calcul",
                    "Probabilités",
                    "Algèbre linéaire",
                    "Statistique",
                    "Analyse",
                    "Informatique / programmation",
                ),
                "Les domaines communs s’illuminent successivement sans codes de cours.",
            ),
            ActionWindow(
                12.0,
                16.0,
                "separate_three_pathways",
                ("math_path", "statistics_path", "computing_path"),
                "Les trois copies commencent à former trois voies.",
            ),
        ),
        narration_cue_ids=cue_ids("v3_05_common_foundation", 4),
        visual_notes=(
            "Ne montrer que la première année.",
            "Employer des domaines généraux plutôt que des codes.",
        ),
    ),
    SceneSpec(
        id="v3_06_fundamental_mathematics",
        start=70.0,
        end=101.0,
        title="Mathématiques fondamentales",
        subtitle="Approfondir les structures et les raisonnements",
        table_programs=("mathématiques fondamentales",),
        segments=(
            ConceptSegment(
                id="analysis",
                start=0.0,
                end=10.0,
                on_screen="Analyse",
                highlighted_course_labels=(
                    "Analyse I",
                    "Analyse II",
                    "Analyse III",
                    "Analyse complexe",
                    "Équations différentielles",
                ),
                visual="Une courbe évolue, puis approche une limite.",
            ),
            ConceptSegment(
                id="algebra",
                start=10.0,
                end=19.0,
                on_screen="Algèbre",
                highlighted_course_labels=(
                    "Algèbre linéaire",
                    "Théorie des groupes",
                    "Théorie des anneaux",
                ),
                visual="Une forme tourne; ses symétries répétées deviennent un réseau simple.",
            ),
            ConceptSegment(
                id="geometry_topology",
                start=19.0,
                end=28.0,
                on_screen="Géométrie et topologie",
                highlighted_course_labels=(
                    "Géométries",
                    "Formes différentielles",
                    "Topologie",
                    "Géométrie différentielle",
                ),
                visual="Une forme fermée se déforme continûment en une autre.",
            ),
            ConceptSegment(
                id="summary",
                start=28.0,
                end=31.0,
                on_screen="Analyse · Algèbre · Géométrie · Topologie",
                summary_line="Analyse · Algèbre · Géométrie · Topologie",
            ),
        ),
        actions=(
            ActionWindow(
                0.0,
                10.0,
                "activate_analysis_segment",
                ("analysis_courses", "limit_curve"),
            ),
            ActionWindow(
                10.0,
                19.0,
                "activate_algebra_segment",
                ("algebra_courses", "symmetry_network"),
            ),
            ActionWindow(
                19.0,
                28.0,
                "activate_geometry_topology_segment",
                ("geometry_topology_courses", "deforming_closed_form"),
            ),
            ActionWindow(
                28.0,
                31.0,
                "hold_branch_summary",
                ("Analyse · Algèbre · Géométrie · Topologie",),
            ),
        ),
        narration_cue_ids=cue_ids("v3_06_fundamental_mathematics", 6),
        visual_notes=(
            "La table occupe la gauche; un seul visuel conceptuel occupe la droite.",
            "Les cartes non actives restent à 20–30 % d’opacité.",
        ),
    ),
    SceneSpec(
        id="v3_07_statistics",
        start=101.0,
        end=132.0,
        title="Statistique",
        subtitle="Recueillir, modéliser et comprendre les données",
        table_programs=("statistique",),
        segments=(
            ConceptSegment(
                id="data_collection",
                start=0.0,
                end=10.0,
                on_screen="Recueillir des données",
                highlighted_course_labels=(
                    "Laboratoire de statistique",
                    "Échantillonnage",
                    "Plans d’expérience",
                ),
                visual="Une population de points apparaît; un échantillon est sélectionné.",
            ),
            ConceptSegment(
                id="modelling",
                start=10.0,
                end=20.0,
                on_screen="Construire des modèles",
                highlighted_course_labels=(
                    "Statistique II",
                    "Régression",
                    "Processus stochastiques",
                ),
                visual="Un nuage de points, une droite de régression et une bande légère d’incertitude apparaissent.",
            ),
            ConceptSegment(
                id="advanced_data_methods",
                start=20.0,
                end=28.0,
                on_screen="Analyser et apprendre",
                highlighted_course_labels=(
                    "Analyse multivariée",
                    "Biostatistique",
                    "Statistique informatique",
                    "Apprentissage statistique",
                ),
                visual="Plusieurs groupes de points sont classés.",
            ),
            ConceptSegment(
                id="summary",
                start=28.0,
                end=31.0,
                on_screen="Collecte · Modélisation · Analyse · Apprentissage",
                summary_line="Collecte · Modélisation · Analyse · Apprentissage",
            ),
        ),
        actions=(
            ActionWindow(
                0.0,
                10.0,
                "activate_data_collection_segment",
                ("collection_courses", "population_sample"),
            ),
            ActionWindow(
                10.0,
                20.0,
                "activate_modelling_segment",
                ("modelling_courses", "regression_visual"),
            ),
            ActionWindow(
                20.0,
                28.0,
                "activate_advanced_methods_segment",
                ("advanced_statistics_courses", "classification_visual"),
            ),
            ActionWindow(
                28.0,
                31.0,
                "hold_branch_summary",
                ("Collecte · Modélisation · Analyse · Apprentissage",),
            ),
        ),
        narration_cue_ids=cue_ids("v3_07_statistics", 7),
        visual_notes=(
            "La table occupe la gauche; un seul visuel conceptuel occupe la droite.",
            "La couleur apparaît seulement sur la famille de cours active.",
        ),
    ),
    SceneSpec(
        id="v3_08_mathematics_computing",
        start=132.0,
        end=164.0,
        title="Concentration informatique",
        subtitle="Relier mathématiques, algorithmes et programmation",
        table_programs=("concentration informatique",),
        segments=(
            ConceptSegment(
                id="programming",
                start=0.0,
                end=10.0,
                on_screen="Programmer",
                highlighted_course_labels=(
                    "Programmation I",
                    "Programmation II",
                ),
                visual="Une instruction mathématique devient du pseudocode, puis un résultat simple.",
            ),
            ConceptSegment(
                id="data_structures_algorithms",
                start=10.0,
                end=21.0,
                on_screen="Organiser et résoudre",
                highlighted_course_labels=(
                    "Structures de données",
                    "Algorithmique",
                    "Mathématiques algorithmiques",
                ),
                visual="Une liste devient un arbre, puis un chemin est trouvé dans l’arbre.",
            ),
            ConceptSegment(
                id="databases_advanced_computing",
                start=21.0,
                end=29.0,
                on_screen="Données et informatique avancée",
                highlighted_course_labels=(
                    "Bases de données",
                    "Systèmes",
                    "Informatique avancée",
                ),
                visual="Des enregistrements entrent dans une base; une requête extrait une sélection.",
            ),
            ConceptSegment(
                id="summary",
                start=29.0,
                end=32.0,
                on_screen="Programmation · Structures de données · Algorithmes · Bases de données",
                summary_line="Programmation · Structures de données · Algorithmes · Bases de données",
            ),
        ),
        actions=(
            ActionWindow(
                0.0,
                10.0,
                "activate_programming_segment",
                ("programming_courses", "instruction_to_code"),
            ),
            ActionWindow(
                10.0,
                21.0,
                "activate_data_structures_segment",
                ("data_structure_courses", "list_tree_path"),
            ),
            ActionWindow(
                21.0,
                29.0,
                "activate_database_segment",
                ("database_courses", "database_query"),
            ),
            ActionWindow(
                29.0,
                32.0,
                "hold_branch_summary",
                ("Programmation · Structures de données · Algorithmes · Bases de données",),
            ),
        ),
        narration_cue_ids=cue_ids("v3_08_mathematics_computing", 5),
        visual_notes=(
            "Utiliser le nom officiel « concentration informatique ».",
            "La table occupe la gauche; un seul visuel conceptuel occupe la droite.",
        ),
    ),
    SceneSpec(
        id="v3_09_computing_profiles",
        start=164.0,
        end=180.0,
        title="Deux profils dans la concentration informatique",
        on_screen_phrases=(
            "Profil mathématiques",
            "Structures et mathématiques avancées",
            "Profil statistique",
            "Statistique et science des données",
        ),
        table_programs=(
            "concentration informatique — profil mathématiques",
            "concentration informatique — profil statistique",
        ),
        segments=(
            ConceptSegment(
                id="mathematics_profile",
                start=7.0,
                end=12.0,
                on_screen="Profil mathématiques",
                highlighted_course_labels=(
                    "Théorie des groupes",
                    "Théorie des anneaux",
                ),
                visual="Une carte spacieuse présente l’approfondissement des structures mathématiques.",
            ),
            ConceptSegment(
                id="statistics_profile",
                start=12.0,
                end=16.0,
                on_screen="Profil statistique",
                highlighted_course_labels=(
                    "Statistique II",
                    "Régression",
                    "Statistique informatique",
                    "Apprentissage statistique",
                ),
                visual="Une carte spacieuse présente la statistique et la science des données.",
            ),
        ),
        actions=(
            ActionWindow(
                0.0,
                3.0,
                "show_common_computing_card",
                ("common_computing_card",),
            ),
            ActionWindow(
                3.0,
                7.0,
                "divide_into_two_profile_cards",
                ("mathematics_profile_card", "statistics_profile_card"),
            ),
            ActionWindow(
                7.0,
                12.0,
                "highlight_mathematics_profile",
                ("mathematics_profile_card",),
            ),
            ActionWindow(
                12.0,
                16.0,
                "highlight_statistics_profile",
                ("statistics_profile_card",),
            ),
        ),
        narration_cue_ids=cue_ids("v3_09_computing_profiles", 4),
        visual_notes=(
            "Présenter deux cartes ouvertes et directement comparables.",
            "Ne pas employer « math-info » comme nom officiel.",
        ),
    ),
    SceneSpec(
        id="v3_10_comparison",
        start=180.0,
        end=198.0,
        title="Comparaison finale",
        on_screen_phrases=(
            "Mathématiques fondamentales",
            "Analyse",
            "Algèbre",
            "Géométrie",
            "Topologie",
            "Statistique",
            "Données",
            "Modèles",
            "Incertitude",
            "Apprentissage",
            "Concentration informatique",
            "Programmation",
            "Structures de données",
            "Algorithmes",
            "Deux profils",
            "Une base largement commune. Trois orientations.",
        ),
        table_programs=(
            "mathématiques fondamentales",
            "statistique",
            "concentration informatique",
        ),
        actions=(
            ActionWindow(
                0.0,
                5.0,
                "enter_three_vertical_maps",
                ("math_map", "statistics_map", "computing_map"),
                "Les trois cartes verticales entrent l’une après l’autre.",
            ),
            ActionWindow(
                5.0,
                11.0,
                "pulse_branch_accents",
                ("math_accent", "statistics_accent", "computing_accent"),
                "Chaque accent de branche pulse une seule fois.",
            ),
            ActionWindow(
                11.0,
                15.0,
                "align_common_first_year",
                ("common_foundation_rows",),
                "La base commune de première année s’aligne entre les trois cartes.",
            ),
            ActionWindow(
                15.0,
                18.0,
                "hold_comparison",
                ("three_maps", "Une base largement commune. Trois orientations."),
            ),
        ),
        narration_cue_ids=cue_ids("v3_10_comparison", 3),
        visual_notes=(
            "Les trois cartes sont étroites, verticales et de même poids visuel.",
        ),
    ),
    SceneSpec(
        id="v3_11_guide",
        start=198.0,
        end=215.0,
        title="Pour tous les détails",
        on_screen_phrases=(
            "Pour tous les détails",
            "Guide de la personne étudiante 2025–2026",
            "mathématiques et statistique",
            "Cheminements à 4 ou 5 cours",
            "Début à l’automne ou à l’hiver",
            "Préalables, options et cours complémentaires",
            "math.uqam.ca",
        ),
        actions=(
            ActionWindow(
                0.0,
                3.0,
                "enter_guide_cover",
                ("guide_cover",),
                "Une représentation propre de la couverture entre à gauche.",
            ),
            ActionWindow(
                3.0,
                7.0,
                "reveal_exact_guide_title",
                ("Guide de la personne étudiante 2025–2026", "mathématiques et statistique"),
            ),
            ActionWindow(
                7.0,
                12.0,
                "reveal_practical_details",
                (
                    "Cheminements à 4 ou 5 cours",
                    "Début à l’automne ou à l’hiver",
                    "Préalables, options et cours complémentaires",
                ),
                "Faire apparaître les trois précisions une à une.",
            ),
            ActionWindow(
                12.0,
                17.0,
                "hold_url_and_closing",
                ("math.uqam.ca", "guide_cover", "guide_details"),
                "Afficher l’URL et maintenir l’image; les deux dernières secondes restent parfaitement fixes.",
            ),
        ),
        narration_cue_ids=cue_ids("v3_11_guide", 6),
        visual_notes=(
            "La couverture est à gauche et les informations à droite.",
            "Ne pas fondre au noir avant le maintien final de deux secondes.",
        ),
    ),
)


SCENE_BY_ID: dict[str, SceneSpec] = {scene.id: scene for scene in SCENES}
SCENE_IDS: tuple[str, ...] = tuple(scene.id for scene in SCENES)

EXPECTED_SCENE_IDS = (
    "v3_01_opening",
    "v3_02_reading_the_table",
    "v3_03_course_load",
    "v3_04_complementary_column",
    "v3_05_common_foundation",
    "v3_06_fundamental_mathematics",
    "v3_07_statistics",
    "v3_08_mathematics_computing",
    "v3_09_computing_profiles",
    "v3_10_comparison",
    "v3_11_guide",
)


def validate_storyboard() -> None:
    """Fail fast when edits break the exact V3 timing contract."""

    if SCENE_IDS != EXPECTED_SCENE_IDS:
        raise ValueError(f"Unexpected V3 scene order: {SCENE_IDS!r}")
    if len(SCENE_BY_ID) != len(SCENES):
        raise ValueError("V3 scene IDs must be unique.")

    cursor = 0.0
    for scene in SCENES:
        if scene.start != cursor:
            raise ValueError(
                f"{scene.id} starts at {scene.start}, expected contiguous start {cursor}."
            )
        if scene.end <= scene.start:
            raise ValueError(f"{scene.id} has a non-positive duration.")

        for segment in scene.segments:
            if not (0.0 <= segment.start < segment.end <= scene.duration):
                raise ValueError(f"Segment {segment.id} falls outside {scene.id}.")
        for action in scene.actions:
            if not (0.0 <= action.start < action.end <= scene.duration):
                raise ValueError(f"Action {action.action} falls outside {scene.id}.")

        cursor = scene.end

    if cursor != TARGET_DURATION_SECONDS:
        raise ValueError(
            f"V3 duration is {cursor}s, expected {TARGET_DURATION_SECONDS}s."
        )


validate_storyboard()
