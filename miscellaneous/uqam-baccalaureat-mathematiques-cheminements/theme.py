"""Visual theme for the reconstructed course-map video."""

COLORS = {
    "background": "#F5F3EE",
    "paper": "#FFFFFF",
    "ink": "#17232C",
    "muted": "#4F5C65",
    "grid": "#D9DEE1",
    "mathstat": "#DDE8F4",
    "mathstat_edge": "#6684A1",
    "info": "#F1C4B9",
    "info_edge": "#B75E49",
    "option": "#D7E0E5",
    "option_edge": "#73838D",
    "complement": "#F6E9BB",
    "complement_edge": "#B7973F",
    "context": "#E9D49A",
    "context_edge": "#9D7E2F",
    "math": "#315F9E",
    "stat": "#1B8178",
    "computer": "#B7513B",
    "gold": "#8A6500",
    "dark": "#26343D",
}

PROGRAM_ACCENTS = {
    "math": COLORS["math"],
    "stat": COLORS["stat"],
    "info_math": COLORS["computer"],
    "info_stat": COLORS["computer"],
}

CATEGORY_STYLE = {
    "mathstat": (COLORS["mathstat"], COLORS["mathstat_edge"]),
    "info": (COLORS["info"], COLORS["info_edge"]),
    "option": (COLORS["option"], COLORS["option_edge"]),
    "complement": (COLORS["complement"], COLORS["complement_edge"]),
    "context": (COLORS["context"], COLORS["context_edge"]),
}
