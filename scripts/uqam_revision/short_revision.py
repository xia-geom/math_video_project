"""Companion to the guarded UQAM migration; edits only the short film."""
from __future__ import annotations
import ast
from pathlib import Path

BEATS = '''"""Speech units synthesized separately; no guessed word-count timing."""
NARRATION_BEATS = {
    "research": (
        "Ce milieu à taille humaine s'appuie aussi sur un pôle mathématique.",
        "Dès le bac, des stages d'été peuvent ouvrir la porte à la recherche.",
        "Au CIRGET et au LaCIM, on découvre des questions et une communauté scientifique.",
    ),
    "montreal": (
        "Le pavillon Président-Kennedy se trouve au Quartier des spectacles, avec un accès intérieur direct au métro Place-des-Arts.",
        "Des espaces d'accueil aident à prendre ses repères.",
        "La Faculté accompagne aussi l'arrivée et l'intégration des étudiants internationaux.",
    ),
    "close": (
        "Des mathématiques exigeantes.",
        "Un milieu à taille humaine.",
        "Un réseau de recherche.",
        "Montréal à votre porte.",
        "Découvrez le bac en mathématiques à l'UQAM.",
    ),
}
'''

CONSTRUCT = '''
def construct(self):
    configure_azure_speech_environment(PROMO_VOICE)
    self.set_speech_service(AzureService(**azure_service_kwargs(PROMO_VOICE)))
    self.semantic_shots = []
    self.semantic_acts = []
    for key in NARRATION_SEGMENTS:
        self._act_start = float(self.renderer.time)
        getattr(self, "act_" + key)()
        self.semantic_acts.append({"act": key, "start": self._act_start, "end": float(self.renderer.time)})
    self.wait(1.0)
    timeline = Path(os.getenv("UQAM_TIMELINE_PATH", str(REPO_ROOT / "dist/bac_math_uqam_fr/semantic_timeline.json")))
    timeline.parent.mkdir(parents=True, exist_ok=True)
    timeline.write_text(json.dumps({"timing_source": "rendered scene clock and separately synthesized speech units", "acts": self.semantic_acts, "shots": self.semantic_shots, "duration": float(self.renderer.time), "listening_review": "pending"}, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
'''
RESEARCH = '''
def act_research(self):
    heading = title_text("La recherche, dès le bac", 44)
    heading.to_edge(UP, buff=0.52).to_edge(LEFT, buff=0.70)
    hub = photo_card("research_math.jpg", research_network_fallback(), width=6.15, height=3.65)
    hub.to_edge(LEFT, buff=0.65).shift(0.05 * DOWN)
    facts = Group(
        clean_fact("stages d'été en recherche", "des possibilités à explorer"),
        clean_fact("CIRGET", "centre interuniversitaire"),
        clean_fact("LaCIM", "centre de recherche de l'UQAM"),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
    facts.to_edge(RIGHT, buff=0.72)
    start = float(self.renderer.time)
    with self.narrate_unit("research", 0):
        self.play(FadeIn(heading), FadeIn(hub), FadeIn(facts), run_time=0.75)
    # Hold the fully readable photo and facts through a complete second unit.
    with self.narrate_unit("research", 1):
        pass
    self.play(FadeOut(hub), FadeOut(facts), run_time=0.4)
    self.record_photo("research_math.jpg", start, float(self.renderer.time))
    pathway = research_network_fallback().shift(0.10 * DOWN)
    with self.narrate_unit("research", 2):
        self.play(FadeIn(pathway), run_time=0.7)
    self.play(FadeOut(Group(heading, pathway)), run_time=0.38)
'''
MONTREAL = '''
def act_montreal(self):
    # Each full-bleed plan remains until its separately synthesized unit ends.
    plans = (
        ("president_kennedy.jpg", "Pavillon Président-Kennedy", "Quartier des spectacles · métro Place-des-Arts", "Photo UQAM", metro_fallback),
        ("allo_pk.jpg", "Des repères dès l'arrivée", "Espace d'accueil Allô!", "Photo : programme Allô! · UQAM", international_fallback),
        ("international_students.jpg", "Une communauté ouverte sur le monde", "Ressources de la Faculté des sciences", "Photo : Faculté des sciences · UQAM", international_fallback),
    )
    for index, (filename, title, detail, credit_text, fallback) in enumerate(plans):
        photo = full_bleed_photo(filename, fallback())
        copy = editorial_overlay(title, [detail], width=11.5, title_size=36)
        copy.to_edge(LEFT, buff=0.65).shift(0.65 * UP)
        credit = photo_credit(credit_text)
        start = float(self.renderer.time)
        with self.narrate_unit("montreal", index):
            self.play(FadeIn(photo), FadeIn(copy), FadeIn(credit), run_time=0.65)
        self.play(FadeOut(photo), FadeOut(copy), FadeOut(credit), run_time=0.35)
        self.record_photo(filename, start, float(self.renderer.time), credit_text)
'''
CLOSE = '''
def act_close(self):
    lines = Group(*[kerning_text(text, size=41, weight="BOLD", color=UQAM_BLUE if index == 1 else INK) for index, text in enumerate(NARRATION_BEATS["close"][:4])]).arrange(DOWN, buff=0.27).move_to(0.20 * UP)
    for index, line in enumerate(lines):
        with self.narrate_unit("close", index):
            self.play(FadeIn(line, shift=0.07 * UP), run_time=0.4)
    # Do not remove the summary while its corresponding words are still spoken.
    self.play(FadeOut(lines), run_time=0.4)
    slogan = title_text("Aller loin, sans avancer seul.", 43).move_to(1.02 * UP)
    programme = body_text("Baccalauréat en mathématiques", 28, UQAM_BLUE).next_to(slogan, DOWN, buff=0.42)
    cta = Group(body_text("Découvrir le programme", 23, INK), body_text(CTA_DISPLAY, 23, UQAM_BLUE)).arrange(DOWN, buff=0.14).next_to(programme, DOWN, buff=0.37)
    with self.narrate_unit("close", 4):
        self.play(FadeIn(slogan), FadeIn(programme), FadeIn(cta), run_time=0.65)
    self.wait(FINAL_CARD_HOLD)
    if USE_OFFICIAL_LOGO and LOGO_APPROVED and LOGO_PATH.exists():
        self.play(FadeOut(slogan), FadeOut(programme), FadeOut(cta), run_time=0.35)
        logo = ImageMobject(str(LOGO_PATH)).scale_to_fit_width(2.9).move_to(ORIGIN)
        self.play(FadeIn(logo), run_time=0.5)
        self.wait(1.2)
'''


def apply_short(root: Path, replace_method, edit):
    folder = root / 'miscellaneous/bac_math_uqam_fr'
    scene = folder / 'bac_math_uqam_fr_scene.py'
    build = folder / 'build_release.py'
    (folder / 'promo_beats.py').write_text(BEATS)
    edit(scene, 'from PIL import Image, ImageDraw, ImageFont', 'from PIL import Image, ImageDraw, ImageFont\nfrom tools.uqam_video_review import cover_image\nfrom promo_beats import NARRATION_BEATS')
    edit(scene, 'MID_GREY = "#8A8F94"', 'MID_GREY = "#59616B"')
    edit(scene, 'Text.set_default(font=FONT, color=INK)', 'for _segment, _beats in NARRATION_BEATS.items():\n    NARRATION_SEGMENTS[_segment] = " ".join(_beats)\n\nText.set_default(font=FONT, color=INK)')
    edit(scene, '"2 h de TP par semaine"', '"travaux pratiques"')
    edit(scene, '"dans les cours du premier niveau"', '"accompagner les apprentissages"')
    edit(scene, '"Les groupes sont à taille humaine, les enseignants accessibles, "', '"La Faculté met en avant des groupes à taille humaine et des enseignants accessibles, "')
    edit(scene, 'max_subcaption_len=52', 'max_subcaption_len=42')
    replace_method(scene, 'construct', CONSTRUCT, 'BacMathUQAMFR')
    replace_method(scene, 'act_research', RESEARCH, 'BacMathUQAMFR')
    replace_method(scene, 'act_montreal', MONTREAL, 'BacMathUQAMFR')
    replace_method(scene, 'act_close', CLOSE, 'BacMathUQAMFR')
    # Add class helpers immediately before narrate, retaining its public API.
    edit(scene, '    def narrate(self, text: str, *, rate: str | None = None):', '''    def record_photo(self, filename, start, end, displayed_credit=None):
        self.semantic_shots.append({"filename": filename, "start": start, "end": end,
                                    "displayed_credit": displayed_credit,
                                    "placement": "upper-right protected panel" if displayed_credit else "distribution description"})

    def narrate_unit(self, segment, index):
        return self.narrate(NARRATION_BEATS[segment][index], rate=NARRATION_RATES[segment])

    def narrate(self, text: str, *, rate: str | None = None):''')
    replace_method(scene, 'photo_credit', '''
def photo_credit(text: str) -> Group:
    credit = kerning_text(text, size=18, weight="NORMAL", color=WHITE)
    panel = Rectangle(width=credit.width + 0.30, height=credit.height + 0.20,
                      stroke_width=0, fill_color=INK, fill_opacity=1)
    credit.move_to(panel)
    return Group(panel, credit).to_corner(UR, buff=0.35)
''')
    # A cover crop is chosen explicitly and recorded, never stretched.
    edit(scene, '        image = ImageMobject(str(path))\n        factor = max(config.frame_width / image.width, config.frame_height / image.height)', '        focal = (0.5, 0.5) if filename == "president_kennedy.jpg" else (0.5, 0.48)\n        pixels = np.asarray(cover_image(path, (config.pixel_width, config.pixel_height), focal))\n        image = ImageMobject(pixels)\n        factor = max(config.frame_width / image.width, config.frame_height / image.height)')
    # Log actual clock positions for unchanged photo treatments as well.
    text = scene.read_text()
    tree = ast.parse(text)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'BacMathUQAMFR')
    for name in ('act_hook', 'act_human_scale', 'act_support'):
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
        source = ast.get_source_segment(text, method)
        if name == 'act_hook':
            source = source.replace('        self.play(FadeIn(visual), run_time=0.65)', '        context_credit = photo_credit("Activité mathématique · Photo : Mireille Soboya")\n        self.play(FadeIn(visual), FadeIn(context_credit), run_time=0.65)')
            source = source.replace('            FadeOut(sub),', '            FadeOut(sub),\n            FadeOut(context_credit),')
            source += '\n        self.record_photo("classroom_math.jpg", self._act_start, float(self.renderer.time), "Activité mathématique · Photo : Mireille Soboya")\n'
        elif name == 'act_human_scale':
            source = source.replace('            self.wait(TEACHING_PORTRAIT_HOLD)', '            self.wait(TEACHING_PORTRAIT_HOLD)\n            portrait_end = float(self.renderer.time) + 0.45\n            self.record_photo("lisa_berger.jpg", self._act_start, portrait_end)\n            self.record_photo("francois_bergeron.jpg", self._act_start, portrait_end)')
        else:
            source = source.replace('            self.play(\n                FadeIn(support_photo', '            support_start = float(self.renderer.time)\n            self.play(\n                FadeIn(support_photo')
            source = source.replace('            self.play(\n                FadeIn(library_photo', '            library_start = float(self.renderer.time)\n            self.play(\n                FadeIn(library_photo')
            source += '\n        self.record_photo("support_students.jpg", support_start, float(self.renderer.time))\n        self.record_photo("bibliotheque_sciences.jpg", library_start, float(self.renderer.time))\n'
        # ast.get_source_segment omits the indentation on the first line only.
        source = '    ' + source
        replace_method(scene, name, source, 'BacMathUQAMFR')

    edit(build, 'from tools.tts import (', 'from promo_beats import NARRATION_BEATS\nfrom tools.uqam_video_review import validate_subtitles, photo_credit_inventory, review_times\n\nfrom tools.tts import (')
    # Resolve once in the parent; send those same values to the child renderer.
    edit(build, '"UQAM_PROMO_RATE": "+2%",', '"UQAM_PROMO_RATE": PROMO_RATE,')
    edit(build, '"UQAM_PROMO_CTA_URL": (\n                "https://etudier.uqam.ca/programme/baccalaureat-mathematiques"\n            ),', '"UQAM_PROMO_CTA_URL": CTA_URL,')
    edit(build, '"UQAM_PROMO_CTA_DISPLAY": "etudier.uqam.ca",', '"UQAM_PROMO_CTA_DISPLAY": CTA_DISPLAY,')
    edit(build, '"UQAM_HOOK_RATE": os.getenv("UQAM_HOOK_RATE", "0%"),', '"UQAM_HOOK_RATE": NARRATION_RATES["hook"],')
    edit(build, '"RENDER_SKIP_DRIVE_COPY": "1",', '"RENDER_SKIP_DRIVE_COPY": "1",\n            "UQAM_TIMELINE_PATH": str(RAW_DIR / "semantic_timeline.json"),')
    edit(build, '        "asset_manifest": ASSET_DIR / "sources.json",', '        "asset_manifest": ASSET_DIR / "sources.json",\n        "speech_units": Path(__file__).with_name("promo_beats.py"),\n        "review_helpers": REPO_ROOT / "tools/uqam_video_review.py",\n        "semantic_timeline": RAW_DIR / "semantic_timeline.json",')
    replace_method(build, 'validate_srt', '''
def validate_srt(path: Path, duration: float) -> dict[str, Any]:
    return validate_subtitles(path, duration)
''')
    edit(build, '    for name, narration in NARRATION_SEGMENTS.items():', '''    units = []
    for group, narration in NARRATION_SEGMENTS.items():
        for index, text in enumerate(NARRATION_BEATS.get(group, (narration,))):
            units.append((f"{group}.{index + 1:02d}", group, text))
    for name, group, narration in units:''')
    edit(build, 'rate=NARRATION_RATES.get(name, PROMO_RATE),', 'rate=NARRATION_RATES.get(group, PROMO_RATE),')
    edit(build, '    if samples.size < sample_rate:', '    if samples.size < int(0.15 * sample_rate):')
    # Sample measured shot transitions, not only fractions of the total film.
    edit(build, '    for index, fraction in enumerate(fractions, start=1):\n        timestamp = duration * fraction', '''    times = [duration * fraction for fraction in fractions]
    timeline_path = RAW_DIR / "semantic_timeline.json"
    if timeline_path.is_file():
        timeline = json.loads(timeline_path.read_text())
        times += review_times(timeline.get("shots", []), duration)
    for index, timestamp in enumerate(sorted(set(times)), start=1):''')
    edit(build, '"visible_photo_credits": False,', '"visible_photo_credits": True,  # See per-asset records for precise visibility.')
    edit(build, '        "normalization_applied": normalized,', '''        "photo_credits": photo_credit_inventory(assets, json.loads((RAW_DIR / "semantic_timeline.json").read_text())["shots"]),
        "review_status": {"raw_frame_inspection": "explicitly asserted by operator", "encoded_frame_inspection": "pending", "full_listening": "pending", "institutional_approval": "not inferred"},
        "normalization_applied": normalized,''')
    edit(build, '            "representative_frames": qa_frames,', '            "representative_frames": qa_frames,\n            "encoded_representative_frames": extract_representative_frames(video, release_dir / "encoded_qa"),')
    edit(build, 'synchronized French cues', 'French cues; listening alignment remains a separate review')
    edit(build, 'all six individual MAI clips passed', 'all individually synthesized MAI clips passed')
    edit(build, '- Visual QA: explicitly approved after inspection of representative frames.', '- Raw-frame QA: asserted by operator; encoded-frame review and full listening remain separate pending gates.')
    (folder / 'README.md').write_text('''# Film court du baccalauréat en mathématiques

La narration de Montréal, de la recherche et de la conclusion est découpée en prises indépendantes dans `promo_beats.py`. Chaque changement de plan attend la fin de sa prise, sans estimation au nombre de mots. `semantic_timeline.json` consigne les plans sur l’horloge réelle du rendu.

Les photographies gardent leur contexte : activité mathématique, accueil Allô!, visite de bibliothèque et pôle de recherche. Les portraits ne sont pas des témoignages enregistrés. Les crédits non affichés doivent accompagner la description de diffusion; l’inventaire par actif distingue explicitement les deux modes. Autorisations de diffusion et d’identité visuelle ne sont jamais déduites des tests.

`build_release.py` conserve le contrôle séparé d’inspection brute et refuse les rendus périmés. Il produit aussi les images de contrôle de l’export encodé et des statistiques SRT. Un passage automatisé ne certifie ni l’écoute, ni la lecture, ni la diffusion institutionnelle. La voix MAI existante et l’absence de musique restent les valeurs de référence.

La valeur effective du débit et de l’appel à l’action est celle résolue par le parent; la même valeur est transmise au processus de rendu et au manifeste. Les anciennes constantes de maintien sont conservées pour compatibilité, mais ne pilotent plus la sortie des plans Montréal/recherche/conclusion.
''')
