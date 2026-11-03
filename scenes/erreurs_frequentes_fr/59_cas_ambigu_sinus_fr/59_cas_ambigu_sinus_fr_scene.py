"""The SSA sine-law candidates still need nondegenerate-triangle checks."""

import math

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Arc,
    Circle,
    Create,
    DashedLine,
    Dot,
    Line,
    MathTex,
    Tex,
    Text,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class CasAmbiguSinusFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._two_intersections()
        self._two_triangles()
        self._none_or_tangent()
        self._degenerate_candidate()
        self._general_check()
        self._self_check()
        self._self_check_answer()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        data = self.formula(r"A=30^\circ,\qquad a=7,\qquad b=10", 46)
        relation = self.formula(r"\sin B=\frac{b\sin A}{a}=\frac57", 46)
        answer = self.formula(r"B=\arcsin\frac57\approx45{,}6^\circ\quad\text{seulement ?}", 40)
        self.new_page("Le premier angle ne suffit pas", data, relation, answer, gap=0.6)
        self.explain(
            "Nous connaissons deux côtés et un angle qui n'est pas compris entre eux. "
            "Les petites lettres désignent les côtés opposés aux angles de même lettre. "
            "La loi des sinus donne ici sinus de B égal à cinq sur sept.",
            data, relation,
        )
        self.explain(
            "La calculatrice propose environ quarante-cinq virgule six degrés. "
            "Mais le sinus d'un angle et celui de son supplémentaire sont égaux. "
            "Il faut chercher une seconde possibilité, puis vérifier si elle forme un triangle.",
            answer,
        )

    def _two_intersections(self):
        unit = 0.26
        def point(x, y):
            return unit * (x * RIGHT + y * UP)
        abscissa = 10 * math.cos(math.pi / 6)
        half_chord = math.sqrt(7**2 - 5**2)
        a = point(0, 0)
        c = point(abscissa, 5)
        b1 = point(abscissa + half_chord, 0)
        b2 = point(abscissa - half_chord, 0)
        base = Line(point(-0.7, 0), point(16, 0), color=BLACK, stroke_width=2)
        known_side = Line(a, c, color=BLACK, stroke_width=3)
        angle = Arc(radius=0.5, start_angle=0, angle=math.pi / 6, arc_center=a, color=BLACK)
        circle = Circle(radius=7 * unit, color=BLUE_D, stroke_width=2).move_to(c)
        altitude = DashedLine(c, point(abscissa, 0), color=BLACK, stroke_width=2)
        centers = VGroup(Dot(a, color=BLACK, radius=0.055), Dot(c, color=BLACK, radius=0.055))
        labels = VGroup(
            self.formula("A", 29).next_to(centers[0], DOWN + LEFT, buff=0.13),
            self.formula("C", 29).next_to(centers[1], UP, buff=0.14),
        )
        dots = VGroup(Dot(b1, color=BLUE_D, radius=0.07), Dot(b2, color=BLUE_D, radius=0.07))
        candidates = VGroup(
            self.formula("B_1", 29).next_to(dots[0], DOWN, buff=0.15),
            self.formula("B_2", 29).next_to(dots[1], DOWN, buff=0.15),
        )
        first_side = Line(c, b1, color=BLUE_D, stroke_width=3)
        second_side = Line(c, b2, color=BLUE_D, stroke_width=3)
        diagram = VGroup(base, known_side, angle, circle, altitude, centers, labels,
                         dots, candidates, first_side, second_side)
        caption = self.formula(r"AC=b=10,\qquad CB=a=7,\qquad h=5", 36)
        self.new_page("Deux positions pour le même côté", diagram, caption, gap=0.3)
        self.explain(
            "Fixons A, le côté A C de longueur dix et la demi-droite sur laquelle "
            "B doit se trouver. Le point B doit aussi être à distance sept de C. "
            "Il appartient donc à ce cercle. La hauteur jusqu'à la droite vaut cinq.",
            base, known_side, angle, centers, labels, altitude, caption,
        )
        self.play(Create(circle), run_time=1.3)
        self.explain(
            "Le cercle rencontre la demi-droite en deux points distincts, tous deux "
            "différents de A. Relions chacun à C : nous obtenons deux triangles. "
            "Le côté opposé à A garde la même longueur, mais la base change.",
            dots, candidates,
        )
        self.play(Create(first_side), Create(second_side), run_time=1.3)

    def _two_triangles(self):
        first = self.formula(r"B_1=\arcsin(5/7)\approx45{,}6^\circ", 43)
        second = self.formula(r"B_2=180^\circ-B_1\approx134{,}4^\circ", 43)
        remaining = self.formula(r"C_1\approx104{,}4^\circ,\qquad C_2\approx15{,}6^\circ", 42)
        check = self.words("Deux angles restants positifs : deux triangles.", 28, BLUE_D)
        self.new_page("Tester les deux angles restants", first, second, remaining, check, gap=0.45)
        self.explain(
            "Le second angle B est le supplémentaire du premier, environ "
            "cent trente-quatre virgule quatre degrés. Nous calculons ensuite "
            "C en retirant A et B de cent quatre-vingts degrés, pour chacun des candidats.",
            first, second,
        )
        self.explain(
            "Les angles restants valent environ cent quatre virgule quatre "
            "et quinze virgule six degrés. Les deux sont strictement positifs. "
            "Ces deux solutions sont donc des triangles non aplatis. "
            "Les décimales affichées sont arrondies après les calculs.",
            remaining, check,
        )

    def _none_or_tangent(self):
        fixed = self.formula(r"A=30^\circ,\qquad b=10,\qquad h=b\sin A=5", 39)
        none = self.formula(r"a=4:\qquad\sin B=\frac54>1\quad\Rightarrow\quad0\text{ triangle}", 37)
        tangent = self.formula(r"a=5:\qquad B=90^\circ,\ C=60^\circ\quad\Rightarrow\quad1\text{ triangle}", 37)
        note = self.words("Sous la hauteur : aucun contact. À la hauteur : tangence.", 28)
        self.new_page("La longueur peut tout changer", fixed, none, tangent, note, gap=0.48)
        self.explain(
            "Gardons le même angle A et le même côté b. Si a vaut quatre, "
            "le cercle n'atteint pas la droite, située à distance cinq de son centre. "
            "La formule demanderait un sinus supérieur à un : aucun triangle n'existe.",
            fixed, none,
        )
        self.explain(
            "Si a vaut exactement cinq, le cercle est tangent à la demi-droite. "
            "L'angle B vaut quatre-vingt-dix degrés et C vaut soixante degrés. "
            "Cette fois, nous obtenons un seul triangle.",
            tangent, note,
        )

    def _degenerate_candidate(self):
        data = self.formula(r"A=30^\circ,\qquad a=b=10\quad\Rightarrow\quad\sin B=\frac12", 40)
        first = self.formula(r"B_1=30^\circ\quad\Rightarrow\quad C_1=120^\circ", 43)
        second = self.formula(r"B_2=150^\circ\quad\Rightarrow\quad C_2=0^\circ", 43)
        note = self.words("Un angle nul donne une figure aplatie : on la rejette.", 28, BLUE_D)
        self.new_page("Deux candidats, un seul triangle", data, first, second, note, gap=0.5)
        self.explain(
            "Un sinus situé entre zéro et un ne garantit pas deux triangles. "
            "Avec a et b tous deux égaux à dix, les deux angles proposés "
            "sont trente et cent cinquante degrés.",
            data, first,
        )
        self.explain(
            "Le premier laisse un angle C de cent vingt degrés. Le second "
            "ne laisse aucun angle : C vaut zéro. Dans la construction, "
            "ce candidat ferait coïncider B avec A. Il faut le rejeter. "
            "Il reste exactement un triangle.",
            second, note,
        )

    def _general_check(self):
        assumptions = self.formula(r"0^\circ<A<180^\circ,\qquad a>0,\quad b>0", 38)
        ratio = self.formula(r"k=\frac{b\sin A}{a}>0", 44)
        candidates = self.words("Si k ≤ 1 : former les angles candidats, sans doublon.", 28)
        strict = self.formula(r"A+B<180^\circ\quad\Longleftrightarrow\quad C>0^\circ", 43, BLUE_D)
        tangent = self.formula(r"k=1:\quad B=90^\circ\text{ exige }A<90^\circ", 36)
        self.new_page("Un sinus possible ne suffit pas", assumptions, ratio, candidates, strict, tangent, gap=0.32)
        self.explain(
            "La méthode générale commence avec un angle strictement compris "
            "entre zéro et cent quatre-vingts degrés et deux côtés positifs. "
            "Si k dépasse un, il n'y a pas de solution. Sinon, formons les "
            "angles candidats, en ne comptant qu'une fois un angle répété.",
            assumptions, ratio, candidates,
        )
        self.explain(
            "Chaque candidat doit ensuite laisser un troisième angle strictement "
            "positif. Même lorsque k vaut un, l'angle droit obtenu ne forme "
            "un triangle que si A est aigu. Si A est droit ou obtus, "
            "la somme des angles est déjà trop grande.",
            strict, tangent,
        )

    def _self_check(self):
        data = self.formula(r"A=120^\circ,\qquad a=b=6", 51)
        question = self.words("Combien de triangles non aplatis ?", 31)
        hint = self.words("Examiner les angles proposés, puis l'angle restant.", 28)
        self.new_page("À vous : un angle obtus", data, question, hint, gap=0.65)
        self.explain(
            "À vous. L'angle A vaut cent vingt degrés et les deux côtés "
            "a et b valent six. Combien de triangles non aplatis existe-t-il ? "
            "Calculez les angles B possibles, puis contrôlez l'angle restant.",
            data, question, hint, pause_after=6,
        )

    def _self_check_answer(self):
        sine = self.formula(r"\sin B=\sin120^\circ=\frac{\sqrt3}{2}", 45)
        first = self.formula(r"B_1=60^\circ\quad\Rightarrow\quad C_1=0^\circ", 43)
        second = self.formula(r"B_2=120^\circ\quad\Rightarrow\quad C_2=-60^\circ", 43)
        answer = self.words("Aucun triangle non aplati.", 33, BLUE_D)
        self.new_page("Les deux candidats échouent", sine, first, second, answer, gap=0.5)
        self.explain(
            "Les côtés a et b étant égaux, le sinus de B vaut le sinus "
            "de cent vingt degrés, soit racine de trois sur deux. "
            "Les candidats sont soixante et cent vingt degrés.",
            sine, first,
        )
        self.explain(
            "Le premier donne un troisième angle nul, le second un troisième "
            "angle négatif. Aucun ne convient. Le fait que la valeur du sinus "
            "soit autorisée ne garantit donc même pas l'existence d'un triangle.",
            second, answer,
        )

    def _takeaway(self):
        rule = self.words("Chercher les deux angles ; vérifier le triangle entier.", 29, BLUE_D)
        source = self.words("Manuel 15.4–15.5 · Cahier 15.5 B, synthèse S3", 28)
        self.new_page("Deux vérifications différentes", rule, source, gap=0.85)
        self.explain(
            "La loi des sinus propose des angles. La somme des angles, "
            "la positivité des côtés et l'exclusion des figures aplaties "
            "décident lesquels représentent vraiment des triangles. "
            "C'est cette seconde vérification qui résout le cas ambigu.",
            rule, source,
        )
