from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(rel: str, old: str, new: str) -> bool:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if new in text:
        return False
    if old not in text:
        raise RuntimeError(f"Expected source block not found in {rel}:\n{old[:240]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"patched {rel}")
    return True


def insert_once(rel: str, anchor: str, insertion: str, marker: str) -> bool:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return False
    if anchor not in text:
        raise RuntimeError(f"Insertion anchor not found in {rel}: {anchor!r}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")
    print(f"patched {rel}")
    return True


# ---------------------------------------------------------------------------
# P01 — remove the cross-through between unrelated formula annotations/text.
# ---------------------------------------------------------------------------
replace_once(
    "scenes/algebre_et_polynomes_fr/01_variables_et_polynomes_fr/01_variables_et_polynomes_fr_scene.py",
    '''            self.play(\n                FadeTransform(\n                    VGroup(rel_expr, rel_const_box, rel_const_lbl, rel_var_box, rel_var_lbl),\n                    key_line,\n                ),\n                run_time=1.0,\n            )''',
    '''            self.play(\n                FadeOut(VGroup(rel_expr, rel_const_box, rel_const_lbl, rel_var_box, rel_var_lbl)),\n                run_time=0.45,\n            )\n            self.play(FadeIn(key_line, shift=UP * 0.08), run_time=0.55)''',
)

# ---------------------------------------------------------------------------
# P03 — make the scene genuinely silent-renderable.
# ---------------------------------------------------------------------------
p03 = "scenes/algebre_et_polynomes_fr/03_racine_carree_et_valeur_absolue_fr/03_racine_carree_et_valeur_absolue_fr_scene.py"
insert_once(
    p03,
    "from __future__ import annotations\n",
    "\nimport os\nfrom contextlib import contextmanager\nfrom dataclasses import dataclass\n",
    "from dataclasses import dataclass",
)
insert_once(
    p03,
    "SAFE_WIDTH = 12.4\n",
    '''\n\n@dataclass\nclass _NoVoiceTracker:\n    duration: float = 0.0\n''',
    "class _NoVoiceTracker:",
)
replace_once(
    p03,
    '''    def narration(self, spoken: str):\n        \"\"\"Create a voiceover context with SSML-free captions.\"\"\"\n        return self.voiceover(\n            text=ssml(spoken),\n            subcaption=strip_ssml(spoken),\n        )''',
    '''    def _setup_voiceover(self) -> None:\n        self._voiceover_enabled = False\n        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {"1", "true", "yes"}:\n            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")\n            return\n\n        key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")\n        region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")\n        if not key or not region:\n            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")\n            return\n\n        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", key)\n        os.environ.setdefault("AZURE_SERVICE_REGION", region)\n        os.environ.setdefault("SPEECH_KEY", key)\n        os.environ.setdefault("SPEECH_REGION", region)\n        try:\n            self.set_speech_service(AzureService(voice=VOICE_ID))\n        except Exception as exc:\n            print(f"[voiceover] Azure setup failed: {exc}. Rendering without narration.")\n            return\n        self._voiceover_enabled = True\n\n    @contextmanager\n    def narration(self, spoken: str):\n        \"\"\"Create a voiceover context with an explicit silent fallback.\"\"\"\n        if self._voiceover_enabled:\n            with self.voiceover(\n                text=ssml(spoken),\n                subcaption=strip_ssml(spoken),\n            ) as tracker:\n                yield tracker\n        else:\n            yield _NoVoiceTracker()''',
)
replace_once(
    p03,
    "        self.set_speech_service(AzureService(voice=VOICE_ID))",
    "        self._setup_voiceover()",
)

# ---------------------------------------------------------------------------
# P04 — replace unrelated text morphs with clean sequential fades.
# ---------------------------------------------------------------------------
p04 = "scenes/fonctions_et_graphiques_fr/04_domaine_et_image_fr/04_domaine_et_image_fr_scene.py"
replace_once(
    p04,
    '''        self.play(\n            FadeOut(image_projection),\n            FadeOut(image_guides),\n            FadeOut(image_text),\n            FadeOut(graph_label),\n            ReplacementTransform(heading, relation_heading),\n            run_time=0.65,\n        )\n        heading = relation_heading''',
    '''        self.play(\n            FadeOut(image_projection),\n            FadeOut(image_guides),\n            FadeOut(image_text),\n            FadeOut(graph_label),\n            FadeOut(heading),\n            run_time=0.35,\n        )\n        self.play(FadeIn(relation_heading), run_time=0.35)\n        heading = relation_heading''',
)
replace_once(
    p04,
    '''            self.play(\n                domain_part.animate.set_color(BLACK),\n                map_arrow.animate.set_color(ACCENT),\n                image_part.animate.set_color(ACCENT),\n                ReplacementTransform(explanation_one, explanation_two),\n                run_time=0.65,\n            )''',
    '''            self.play(\n                domain_part.animate.set_color(BLACK),\n                map_arrow.animate.set_color(ACCENT),\n                image_part.animate.set_color(ACCENT),\n                FadeOut(explanation_one),\n                run_time=0.35,\n            )\n            self.play(FadeIn(explanation_two), run_time=0.35)''',
)
replace_once(
    p04,
    '''            self.play(\n                map_arrow.animate.set_color(BLACK),\n                image_part.animate.set_color(BLACK),\n                subset.animate.set_color(ACCENT),\n                codomain_part.animate.set_color(ACCENT),\n                ReplacementTransform(explanation_two, explanation_three),\n                run_time=0.65,\n            )''',
    '''            self.play(\n                map_arrow.animate.set_color(BLACK),\n                image_part.animate.set_color(BLACK),\n                subset.animate.set_color(ACCENT),\n                codomain_part.animate.set_color(ACCENT),\n                FadeOut(explanation_two),\n                run_time=0.35,\n            )\n            self.play(FadeIn(explanation_three), run_time=0.35)''',
)

# ---------------------------------------------------------------------------
# P21 — replace unrelated section-header morph.
# ---------------------------------------------------------------------------
p21 = "scenes/matrices_fr/21_lire_et_appliquer_une_matrice_fr/21_lire_et_appliquer_une_matrice_fr_scene.py"
replace_once(
    p21,
    '''        with self.narrated(spoken, caption) as tracker:\n            self.play(\n                FadeOut(\n                    entry_box,\n                    entry_meaning,\n                    size_formula,\n                    size_words,\n                    col_a,\n                    col_b,\n                    row_apples,\n                    row_bananas,\n                ),\n                Transform(header, calculation_header),\n                Transform(recipe_matrix, matrix_target),\n                run_time=0.7,\n            )''',
    '''        with self.narrated(spoken, caption) as tracker:\n            self.play(FadeOut(header), run_time=0.30)\n            self.play(\n                FadeOut(\n                    entry_box,\n                    entry_meaning,\n                    size_formula,\n                    size_words,\n                    col_a,\n                    col_b,\n                    row_apples,\n                    row_bananas,\n                ),\n                FadeIn(calculation_header),\n                Transform(recipe_matrix, matrix_target),\n                run_time=0.7,\n            )\n            header = calculation_header''',
)

# ---------------------------------------------------------------------------
# P22 — separate opening title and question vertically.
# ---------------------------------------------------------------------------
p22 = "scenes/matrices_fr/22_operations_sur_les_matrices_fr/22_operations_sur_les_matrices_fr_scene.py"
replace_once(
    p22,
    '''        question = Text(\n            "Pourquoi deux règles de calcul différentes ?",\n            font_size=34,\n        )\n        addition_icon = MathTex(''',
    '''        question = Text(\n            "Pourquoi deux règles de calcul différentes ?",\n            font_size=34,\n        )\n        title.shift(UP * 0.95)\n        question.next_to(title, DOWN, buff=0.48)\n        addition_icon = MathTex(''',
)

# ---------------------------------------------------------------------------
# P23 — safe opening-title width and non-scrambling formula replacement.
# ---------------------------------------------------------------------------
p23 = "scenes/matrices_fr/23_determinant_et_matrice_inverse_fr/23_determinant_et_matrice_inverse_fr_scene.py"
replace_once(
    p23,
    '''        title = Text(\n            "Matrices 3 — déterminant et matrice inverse",\n            font_size=44,\n            weight=SEMIBOLD,\n        )\n        question = Text(''',
    '''        title = Text(\n            "Matrices 3 — déterminant et matrice inverse",\n            font_size=44,\n            weight=SEMIBOLD,\n        )\n        if title.width > config.frame_width - 1.0:\n            title.scale_to_fit_width(config.frame_width - 1.0)\n        question = Text(''',
)
replace_once(
    p23,
    "            self.play(ReplacementTransform(product_formula, product_simplified), run_time=0.7)",
    "            self.play(FadeOut(product_formula), run_time=0.30)\n            self.play(FadeIn(product_simplified), run_time=0.40)",
)

# ---------------------------------------------------------------------------
# P24 — all unrelated phase headings use sequential fade replacement.
# ---------------------------------------------------------------------------
p24 = "scenes/trigonometrie_fr/24_du_cercle_au_sinus_fr/24_du_cercle_au_sinus_fr_scene.py"
insert_once(
    p24,
    '''    def _phase_caption(self, text: str) -> Text:\n        caption = Text(text, font_size=30, weight="MEDIUM")\n        caption.to_edge(UP, buff=0.35)\n        return caption\n''',
    '''\n    def _replace_phase_caption(self, current: Text, new: Text) -> Text:\n        self.play(FadeOut(current), run_time=0.25)\n        self.play(FadeIn(new), run_time=0.35)\n        return new\n''',
    "def _replace_phase_caption",
)
replace_once(
    p24,
    "            self.play(Transform(caption, next_caption), run_time=0.7)",
    "            caption = self._replace_phase_caption(caption, next_caption)",
)
replace_once(
    p24,
    '''            self.play(\n                Transform(caption, next_caption),\n                FadeOut(sine_definition),''',
    '''            caption = self._replace_phase_caption(caption, next_caption)\n            self.play(\n                FadeOut(sine_definition),''',
)
replace_once(
    p24,
    '''            self.play(\n                Transform(caption, next_caption),\n                FadeOut(unit_arc_formula),''',
    '''            caption = self._replace_phase_caption(caption, next_caption)\n            self.play(\n                FadeOut(unit_arc_formula),''',
)
replace_once(
    p24,
    '''            self.play(\n                Transform(caption, next_caption),\n                FadeOut(graph_point_formula),''',
    '''            caption = self._replace_phase_caption(caption, next_caption)\n            self.play(\n                FadeOut(graph_point_formula),''',
)

# ---------------------------------------------------------------------------
# P26 — fully clear the old area rows before writing the comparison line.
# ---------------------------------------------------------------------------
p26 = "scenes/geometrie_fr/16_pythagore_par_les_aires_fr/16_pythagore_par_les_aires_fr_scene.py"
replace_once(
    p26,
    '''        with self.narrated(script[6]):\n            self.play(\n                FadeOut(VGroup(area_rows, side_label_bottom, side_label_right)),\n                Transform(geom_identity, geom_line_target),\n                Write(algebra_line),\n                run_time=1.8,\n            )''',
    '''        with self.narrated(script[6]):\n            self.play(\n                FadeOut(VGroup(area_rows, side_label_bottom, side_label_right)),\n                run_time=0.55,\n            )\n            self.play(\n                Transform(geom_identity, geom_line_target),\n                Write(algebra_line),\n                run_time=1.25,\n            )''',
)

# ---------------------------------------------------------------------------
# P27 — remove morphs between unrelated prose/cell layouts.
# ---------------------------------------------------------------------------
p27 = "scenes/notations_fr/18_notation_sigma_fr/18_notation_sigma_fr_scene.py"
insert_once(
    p27,
    '''    @staticmethod\n    def _fit_width(mobject: Mobject, margin: float = 1.0) -> Mobject:\n        max_width = config.frame_width - margin\n        if mobject.width > max_width:\n            mobject.scale_to_fit_width(max_width)\n        return mobject\n''',
    '''\n    def _replace_without_morph(self, current: Mobject, new: Mobject, run_time: float = 0.8) -> Mobject:\n        self.play(FadeOut(current), run_time=run_time / 2)\n        self.play(FadeIn(new), run_time=run_time / 2)\n        return new\n''',
    "def _replace_without_morph",
)
replace_once(
    p27,
    "            self.play(Transform(hundred_terms, compact_prompt), run_time=0.9)",
    "            hundred_terms = self._replace_without_morph(hundred_terms, compact_prompt, run_time=0.9)",
)
replace_once(
    p27,
    '''                self.play(\n                    Transform(focus, next_focus),\n                    Transform(description, next_description),\n                    run_time=0.85,\n                )''',
    '''                self.play(Transform(focus, next_focus), run_time=0.35)\n                description = self._replace_without_morph(\n                    description, next_description, run_time=0.50\n                )''',
)
replace_once(
    p27,
    "            self.play(FadeOut(focus), Transform(description, instruction), run_time=0.8)",
    "            self.play(FadeOut(focus), run_time=0.25)\n            description = self._replace_without_morph(description, instruction, run_time=0.55)",
)
replace_once(
    p27,
    '''            self.play(\n                FadeOut(VGroup(loop_title, index_label, value_label, index_cells, active, rule)),\n                ReplacementTransform(value_cells, produced_values),\n                sigma.animate.move_to(UP * 1.65),\n                run_time=1.1,\n            )''',
    '''            self.play(\n                FadeOut(VGroup(loop_title, index_label, value_label, index_cells, active, rule, value_cells)),\n                sigma.animate.move_to(UP * 1.65),\n                run_time=0.55,\n            )\n            self.play(FadeIn(produced_values), run_time=0.55)''',
)

# ---------------------------------------------------------------------------
# E01/E03/E04 — direct self.voiceover users get a silent-safe wrapper.
# ---------------------------------------------------------------------------
def patch_direct_voiceover_scene(rel: str, service_expr: str) -> None:
    insert_once(
        rel,
        "from __future__ import annotations\n",
        "\nimport os\nfrom contextlib import contextmanager\nfrom dataclasses import dataclass\n",
        "from dataclasses import dataclass",
    )
    insert_once(
        rel,
        "ERROR = RED_D\n",
        '''\n\n@dataclass\nclass _NoVoiceTracker:\n    duration: float = 0.0\n''',
        "class _NoVoiceTracker:",
    )
    class_name = {
        "scenes/erreurs_frequentes_fr/01_implication_et_equivalence_fr/01_implication_et_equivalence_fr_scene.py": "ImplicationEtEquivalenceFR",
        "scenes/erreurs_frequentes_fr/03_egalite_de_fonctions_fr/03_egalite_de_fonctions_fr_scene.py": "EgaliteDeFonctionsFR",
        "scenes/erreurs_frequentes_fr/04_solutions_parasites_fr/04_solutions_parasites_fr_scene.py": "CarreEtSolutionsParasitesFR",
    }[rel]
    class_anchor = f"class {class_name}(VoiceoverScene):\n"
    helper = f'''\n    def _setup_voiceover(self) -> None:\n        self._voiceover_enabled = False\n        if os.getenv("MANIM_DISABLE_VOICEOVER", "").lower() in {{"1", "true", "yes"}}:\n            print("[voiceover] MANIM_DISABLE_VOICEOVER set. Rendering without narration.")\n            return\n\n        key = os.getenv("AZURE_SUBSCRIPTION_KEY") or os.getenv("SPEECH_KEY")\n        region = os.getenv("AZURE_SERVICE_REGION") or os.getenv("SPEECH_REGION")\n        if not key or not region:\n            print("[voiceover] Missing Azure Speech credentials. Rendering without narration.")\n            return\n\n        os.environ.setdefault("AZURE_SUBSCRIPTION_KEY", key)\n        os.environ.setdefault("AZURE_SERVICE_REGION", region)\n        os.environ.setdefault("SPEECH_KEY", key)\n        os.environ.setdefault("SPEECH_REGION", region)\n        try:\n            self.set_speech_service({service_expr})\n        except Exception as exc:\n            print(f"[voiceover] Azure setup failed: {{exc}}. Rendering without narration.")\n            return\n        self._voiceover_enabled = True\n\n    @contextmanager\n    def voiceover(self, text: str, subcaption: str | None = None, **kwargs):\n        if self._voiceover_enabled:\n            with super().voiceover(text=text, subcaption=subcaption, **kwargs) as tracker:\n                yield tracker\n        else:\n            yield _NoVoiceTracker()\n'''
    insert_once(rel, class_anchor, helper, "def _setup_voiceover(self) -> None:")
    replace_once(rel, f"        self.set_speech_service({service_expr})", "        self._setup_voiceover()")


patch_direct_voiceover_scene(
    "scenes/erreurs_frequentes_fr/01_implication_et_equivalence_fr/01_implication_et_equivalence_fr_scene.py",
    "AzureService(voice=VOICE_ID)",
)
patch_direct_voiceover_scene(
    "scenes/erreurs_frequentes_fr/03_egalite_de_fonctions_fr/03_egalite_de_fonctions_fr_scene.py",
    "AzureService(voice=VOICE_ID)",
)
patch_direct_voiceover_scene(
    "scenes/erreurs_frequentes_fr/04_solutions_parasites_fr/04_solutions_parasites_fr_scene.py",
    "AzureService(**azure_service_kwargs())",
)

print("visual-audit fixes applied (or already present)")
