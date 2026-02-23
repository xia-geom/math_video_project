from manim import *
import numpy as np

UQAM_BLUE = "#0A55A0"  # couleur donnée pour l'UQAM dans les normes du réseau UQ
# :contentReference[oaicite:2]{index=2}

class UQAMLogoBumper(Scene):
    def pick_accent(self, logo: VGroup) -> VMobject | None:
        """
        Heuristique robuste: l'accent est typiquement un petit élément
        assez haut en y, peu large, au-dessus du A.
        On choisit l'élément avec (y_top élevé) et (aire petite).
        """
        parts = list(logo.family_members_with_points())
        if not parts:
            return None

        scored = []
        for m in parts:
            bb = m.get_bounding_box()
            y_top = bb[2][1]
            w = m.width
            h = m.height
            area = max(w * h, 1e-6)
            # score: haut + pénalise les gros blocs
            score = y_top - 0.35 * np.log(area)
            scored.append((score, m, area, y_top))

        scored.sort(key=lambda t: t[0], reverse=True)
        # On filtre un peu pour éviter de prendre tout le logo si le SVG est "monobloc".
        for _, m, area, _ in scored[:12]:
            if area < 0.15 * (logo.width * logo.height):
                return m
        return None

    def construct(self):
        self.camera.background_color = WHITE  # mets à BLACK si tu préfères

        # 1) Charger le logo (SVG recommandé)
        logo = SVGMobject("pythagore_whiteboard_fr/LOGO_UQAM.png")
        logo.set_color(UQAM_BLUE)
        logo.scale_to_fit_width(9.0)
        logo.move_to(ORIGIN)

        # Optionnel: si tu veux un rendu plus "vector clean"
        for m in logo.family_members_with_points():
            m.set_stroke(width=6)  # contour visible pendant le draw

        accent = self.pick_accent(logo)

        # 2) Tracé -> remplissage (sobre, institutionnel)
        self.play(DrawBorderThenFill(logo), run_time=1.4)

        # 3) Petit accent de vie sur l'accent grave (si détecté)
        if accent is not None:
            # Copie pour un "tap" discret
            tap = accent.copy().set_opacity(0.0)
            tap.set_stroke(width=0)
            tap.set_fill(color=UQAM_BLUE, opacity=1)

            # Drop très léger depuis au-dessus
            tap.shift(0.25 * UP)
            tap.set_opacity(1.0)

            self.add(tap)
            self.play(
                tap.animate.shift(0.25 * DOWN),
                rate_func=rate_functions.ease_out_back,
                run_time=0.35,
            )
            self.play(FadeOut(tap), run_time=0.15)

        # 4) Micro "breath" (quasi imperceptible)
        self.play(logo.animate.scale(1.02), run_time=0.25)
        self.play(logo.animate.scale(1/1.02), run_time=0.25)

        self.wait(0.3)


class UQAMCornerBug(Scene):
    """
    Variante utile: au début de la vidéo, le logo apparaît puis se range
    dans un coin comme watermark (sans voler l’attention).
    """
    def construct(self):
        self.camera.background_color = WHITE

        logo = SVGMobject("pythagore_whiteboard_fr/LOGO_UQAM.png").set_color(UQAM_BLUE)
        logo.scale_to_fit_width(4.0)
        logo.move_to(ORIGIN)

        self.play(FadeIn(logo, shift=0.15*UP), run_time=0.5)

        corner = logo.copy().scale(0.38)
        corner.to_corner(DR, buff=0.35)

        self.play(Transform(logo, corner), run_time=0.6)
        self.play(logo.animate.set_opacity(0.55), run_time=0.2)
        self.wait(0.5)
