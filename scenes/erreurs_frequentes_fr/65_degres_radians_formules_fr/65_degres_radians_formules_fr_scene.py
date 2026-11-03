"""MAT0339 14.1, 14.6–14.7 : respecter l'unité d'un angle dans une formule."""

import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GRAY_B,
    GREEN_D,
    RED_D,
    RIGHT,
    WHITE,
    Arc,
    Circle,
    Create,
    Dot,
    Line,
    MathTex,
    MoveAlongPath,
    Rotate,
    Sector,
    Tex,
    Text,
    VGroup,
    config,
    linear,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class DegresRadiansFormulesFR(TeachingScene):
    """Convertir avant de substituer, puis vérifier le mode de calcul."""

    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._one_sixth_turn()
        self._convert()
        self._arc_and_sector()
        self._formula_contract()
        self._calculator_mode()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        data = self.formula(r'r=6\ \mathrm{cm},\qquad\theta=60^\circ', 45)
        attempted = self.formula(r's=r\theta=6\times60=360\ \mathrm{cm}\quad?', 43, RED_D)
        perimeter = self.formula(r'\text{Un tour : }2\pi r=12\pi\approx37{,}7\ \mathrm{cm}', 38)
        prompt = self.words('Un sixième de tour peut-il dépasser le tour complet ?', 29)
        self.new_page('Une formule juste, une mauvaise unité', data, attempted,
                      perimeter, prompt, gap=0.50)
        self.explain(
            'Sur un cercle de rayon six centimètres, un point tourne de '
            'soixante degrés. Un élève utilise la formule longueur égale rayon '
            'fois angle et trouve trois cent soixante centimètres. Le calcul '
            'arithmétique est correct. Mais peut-on y remplacer l’angle par '
            'le nombre soixante ?', data, attempted, hold=2,
        )
        self.explain(
            'Le tour complet mesure seulement douze pi centimètres, soit '
            'environ trente-sept virgule sept. Un sixième de ce tour ne peut '
            'pas mesurer trois cent soixante centimètres. L’ordre de grandeur '
            'révèle une confusion entre degrés et radians.',
            perimeter, prompt, hold=2,
        )

    def _one_sixth_turn(self):
        radius = 1.55
        circle = Circle(radius=radius, color=GRAY_B, stroke_width=2)
        base = Line(circle.get_center(), circle.get_right(), color=BLACK)
        ray = base.copy().set_color(BLUE_D)
        arc = Arc(radius=radius, start_angle=0, angle=math.pi / 3,
                  color=BLUE_D, stroke_width=6)
        point = Dot(circle.get_right(), radius=0.075, color=BLUE_D)
        diagram = VGroup(circle, base, ray, arc, point)
        data = VGroup(
            self.formula(r'r=6\ \mathrm{cm}', 36),
            self.formula(r'\theta=60^\circ', 40),
            self.formula(r'\frac{60}{360}=\frac16\ \text{de tour}', 40),
        ).arrange(DOWN, buff=0.48)
        row = VGroup(diagram, data).arrange(RIGHT, buff=1.25)
        note = self.words('Le point suit l’arc ; le rayon tourne de 60°.', 29)
        self.new_page('Le même angle, une fraction de tour', row, note, gap=0.55)
        self.explain(
            'Regardons le mouvement. Le point bleu reste sur le cercle et le '
            'rayon tourne autour du centre. Soixante degrés représentent un '
            'sixième des trois cent soixante degrés d’un tour complet.',
            circle, base, ray, point, data, hold=2,
        )
        self.play(
            Create(arc),
            MoveAlongPath(point, arc.copy()),
            Rotate(ray, angle=math.pi / 3, about_point=circle.get_center()),
            run_time=2.8, rate_func=linear,
        )
        self.explain(
            'La longueur cherchée est celle de l’arc bleu. Elle représente '
            'elle aussi un sixième de la circonférence. Nous ne mesurons pas '
            'la corde qui relierait directement les deux positions.',
            note, hold=2,
        )

    def _convert(self):
        definition = self.formula(r'\theta_{\mathrm{rad}}=\frac{s}{r}\qquad(r>0)', 42)
        formula = self.formula(r's=r\theta_{\mathrm{rad}}', 48, BLUE_D)
        conversion = self.formula(
            r'\theta_{\mathrm{rad}}=\theta_{\mathrm{deg}}\frac\pi{180}'
            r'\quad\Longrightarrow\quad60\frac\pi{180}=\frac\pi3', 39,
        )
        meaning = self.words('60° et π/3 rad désignent la même rotation.', 30)
        self.new_page('Le radian est un rapport de longueurs', definition,
                      formula, conversion, meaning, gap=0.43)
        self.explain(
            'La mesure en radians est définie par la longueur de l’arc '
            'divisée par le rayon, avec un rayon strictement positif. En '
            'multipliant cette définition par le rayon, nous obtenons la '
            'formule de longueur d’arc. Voilà pourquoi son angle doit être '
            'exprimé en radians.', definition, formula, hold=2,
        )
        self.explain(
            'Pour convertir une mesure en degrés, multiplions par pi sur '
            'cent quatre-vingts. Soixante degrés donnent pi sur trois '
            'radians. L’angle géométrique n’a pas changé : seul le nombre '
            'qui le mesure a changé.', conversion, meaning, hold=2,
        )

    def _arc_and_sector(self):
        circle = Circle(radius=1.45, color=GRAY_B, stroke_width=2)
        sector = Sector(radius=1.45, start_angle=0, angle=math.pi / 3,
                        fill_color=BLUE_D, fill_opacity=0.20, stroke_width=0)
        arc = Arc(radius=1.45, start_angle=0, angle=math.pi / 3,
                  color=BLUE_D, stroke_width=6)
        radii = VGroup(
            Line([0, 0, 0], [1.45, 0, 0], color=BLACK),
            Line([0, 0, 0], [1.45 / 2, 1.45 * math.sqrt(3) / 2, 0], color=BLACK),
        )
        diagram = VGroup(circle, sector, radii, arc)
        results = VGroup(
            self.formula(r's=6\frac\pi3=2\pi\ \mathrm{cm}', 40, GREEN_D),
            self.formula(r'\mathcal A=\frac16\pi(6)^2=6\pi\ \mathrm{cm}^2', 37),
        ).arrange(DOWN, buff=0.75)
        row = VGroup(diagram, results).arrange(RIGHT, buff=0.85)
        note = self.words('Même fraction du tour, du disque et du bord.', 29)
        self.new_page('Retrouver le sixième de cercle', row, note, gap=0.6)
        self.explain(
            'Substituons la mesure correcte : six fois pi sur trois donne '
            'deux pi centimètres. C’est bien un sixième de douze pi, la '
            'circonférence complète.', circle, radii, arc, results[0], hold=2,
        )
        self.explain(
            'Le secteur coloré occupe aussi un sixième du disque. Son aire '
            'vaut donc un sixième de pi fois six au carré, soit six pi '
            'centimètres carrés. La longueur porte des centimètres ; '
            'l’aire porte des centimètres carrés.',
            sector, results[1], note, hold=2,
        )

    def _formula_contract(self):
        domain = self.formula(r'r>0,\qquad0\le\theta_{\mathrm{rad}}\le2\pi', 38)
        radians = self.formula(
            r'\text{Radians : }s=r\theta_{\mathrm{rad}},\qquad'
            r'\mathcal A=\frac12r^2\theta_{\mathrm{rad}}', 39,
        )
        degrees = self.formula(
            r'\text{Degrés : }s=\frac{\theta_{\mathrm{deg}}}{360}\,2\pi r,'
            r'\qquad\mathcal A=\frac{\theta_{\mathrm{deg}}}{360}\,\pi r^2', 37,
        )
        note = self.words('Un secteur ordinaire, sans tour supplémentaire.', 29)
        self.new_page('Lire l’unité demandée par la formule', domain, radians,
                      degrees, note, gap=0.45)
        self.explain(
            'Pour un secteur ordinaire, nous choisissons un angle entre '
            'zéro et deux pi radians, soit entre zéro et trois cent '
            'soixante degrés. En radians, la fraction du tour est l’angle '
            'divisé par deux pi. En multipliant cette fraction par l’aire '
            'du disque, nous obtenons un demi fois le rayon au carré fois '
            'l’angle.', domain, radians, note, hold=2,
        )
        self.explain(
            'Nous pouvons aussi travailler en degrés, à condition de '
            'conserver la fraction angle sur trois cent soixante. Les '
            'deux méthodes donnent la même longueur et la même aire. '
            'Une formule n’efface pas l’unité de sa donnée.', degrees, hold=2,
        )

    def _calculator_mode(self):
        wrong = VGroup(
            self.words('Mode DEG', 30, RED_D),
            self.formula(r'\sin\!\left((\pi/6)^\circ\right)\approx0{,}0091', 39, RED_D),
        ).arrange(RIGHT, buff=0.65)
        rad = VGroup(
            self.words('Mode RAD', 30, BLUE_D),
            self.formula(r'\sin(\pi/6)=\frac12', 42),
        ).arrange(RIGHT, buff=0.65)
        deg = VGroup(
            self.words('Mode DEG', 30, BLUE_D),
            self.formula(r'\sin(30^\circ)=\frac12', 42),
        ).arrange(RIGHT, buff=0.65)
        rows = VGroup(wrong, rad, deg).arrange(DOWN, buff=0.65)
        note = self.words('Le mode interprète le nombre entré comme un angle.', 28)
        self.new_page('La calculatrice doit lire la même unité', rows, note, gap=0.55)
        self.explain(
            'Le cahier présente une calculatrice en mode degrés qui reçoit '
            'pi sur six et donne environ zéro virgule zéro zéro neuf un. '
            'Ce mode lit le nombre pi sur six comme une mesure en degrés, '
            'soit environ zéro virgule cinq deux trois six degré. Ce n’est '
            'pas l’angle pi sur six radians.', wrong, hold=2,
        )
        self.explain(
            'Pour calculer le sinus de pi sur six radians, passons en mode '
            'radians et gardons cette entrée. Ou restons en mode degrés '
            'et entrons trente. Les deux donnent une moitié. La présence '
            'du symbole pi dans une saisie ne choisit pas le mode à '
            'notre place.', rad, deg, note, hold=2,
        )

    def _self_check(self):
        data = self.formula(r'r=4,\qquad\theta=\frac{5\pi}{6}\ \mathrm{rad}', 47)
        questions = VGroup(
            self.words('Quelle longueur d’arc ? Quelle aire de secteur ?', 30),
            self.words('Quelle fraction du cercle permet de vérifier ?', 29),
        ).arrange(DOWN, buff=0.45)
        self.new_page('À vous : l’exercice 14.7 B du cahier', data, questions, gap=0.7)
        self.explain(
            'Reprenons les données du cahier : un rayon de quatre et un '
            'angle de cinq pi sur six radians. Calculez la longueur de '
            'l’arc et l’aire du secteur. L’angle est déjà en radians : '
            'faut-il encore le convertir ? Vérifiez aussi quelle fraction '
            'du cercle il représente.', data, questions, hold=2, pause_after=6,
        )

    def _self_check_answer(self):
        fraction = self.formula(r'\frac{5\pi/6}{2\pi}=\frac5{12}', 43)
        length = self.formula(r's=4\frac{5\pi}{6}=\frac{10\pi}{3}', 45, GREEN_D)
        area = self.formula(r'\mathcal A=\frac12(4)^2\frac{5\pi}{6}=\frac{20\pi}{3}', 42)
        verification = self.formula(
            r'\frac5{12}(8\pi)=\frac{10\pi}{3},\qquad'
            r'\frac5{12}(16\pi)=\frac{20\pi}{3}', 37,
        )
        self.new_page('Réponse : cinq douzièmes du cercle', fraction, length,
                      area, verification, gap=0.42)
        self.explain(
            'Cinq pi sur six, divisé par deux pi, donne cinq douzièmes '
            'de tour. La formule d’arc donne dix pi sur trois, en unités '
            'de longueur. La formule d’aire donne vingt pi sur trois, '
            'dans les unités d’aire correspondantes. Aucune conversion '
            'supplémentaire n’était nécessaire.', fraction, length, area, hold=2,
        )
        self.explain(
            'Pour contrôler, prenons cinq douzièmes de la circonférence '
            'huit pi, puis cinq douzièmes de l’aire du disque seize pi. '
            'Nous retrouvons les deux résultats. Cette vérification '
            'relie les calculs à la même fraction de cercle.',
            verification, hold=2,
        )

    def _takeaway(self):
        method = VGroup(
            self.words('Identifier l’unité de l’angle.', 32),
            self.words('Convertir selon la formule ou le mode.', 31),
            self.words('Contrôler la fraction du cercle et les unités.', 30),
        ).arrange(DOWN, buff=0.50)
        sources = self.words('Manuel 14.1, 14.6–14.7 · Cahier 14.6 A, 14.7 B–C', 28)
        self.new_page('Un angle, deux façons de le mesurer', method, sources, gap=0.75)
        self.explain(
            'Avant de remplacer une lettre par un nombre, identifiez '
            'l’unité de l’angle. Convertissez si la formule ou le mode '
            'l’exige. Enfin, contrôlez la fraction du cercle et les '
            'unités du résultat. Le chapitre quatorze du manuel et les '
            'exercices du cahier permettent de pratiquer ces trois gestes.',
            method, sources, hold=2,
        )
