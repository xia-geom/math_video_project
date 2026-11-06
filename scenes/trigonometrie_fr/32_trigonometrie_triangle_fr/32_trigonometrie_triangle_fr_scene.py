"""S08 — right-triangle ratios, with the angle and side roles explicit."""
from manim import (
    BLACK,
    DOWN,
    LEFT,
    RIGHT,
    UP,
    WHITE,
    Angle,
    Line,
    MathTex,
    RightAngle,
    Tex,
    Text,
    VGroup,
    config,
)

from tools import tts
from tools.expanded_teaching import ExpandedTeachingScene as TeachingScene
from tools.teaching_chapters import play_chapter_outline, play_lesson_closing, play_lesson_opening
from tools.teaching_layout import panel

CHAPTERS = ('Choisir l’angle et nommer les côtés', 'Construire et utiliser les rapports', 'Vérifier et s’entraîner')

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class TrigonometrieTriangleFR(TeachingScene):
    def chapter_narration(self, spoken):
        return self.voiceover(text=tts.ssml(spoken), subcaption=tts.strip_ssml(spoken))

    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(self, 'Trigonométrie du triangle', 'Choisir un rapport trigonométrique\nen repérant l’angle et les côtés.', narration=narration)
        play_chapter_outline(self, CHAPTERS, 0, 'Commençons par les données et la question.', narration=narration)
        a, b, c = [-1.8, -1, 0], [1.2, -1, 0], [1.2, 1.25, 0]
        base = Line(a, b, color=BLACK)
        opposite = Line(b, c, color=BLACK)
        hypotenuse = Line(a, c, color=BLACK)
        angle = Angle(base, hypotenuse, radius=0.45, color=BLACK)
        right = RightAngle(Line(b, a), Line(b, c), length=0.2, color=BLACK)
        diagram = VGroup(base, opposite, hypotenuse, angle, right,
                         self.formula('4', 32).next_to(base, DOWN, buff=0.18),
                         self.formula('3', 32).next_to(opposite, RIGHT, buff=0.18),
                         self.formula('5', 32).next_to(hypotenuse.get_center(), UP + LEFT, buff=0.18),
                         self.formula(r'\theta', 30).move_to([-1.12, -0.8, 0]))
        self.new_page('Un triangle rectangle, un angle choisi', diagram)
        self.explain('Voici un triangle rectangle dont les côtés mesurent trois, quatre et cinq. L’angle theta est celui situé à gauche, pas l’angle droit.', diagram, hold=5)

        a = self.words('Hypoténuse : côté opposé à l’angle droit.')
        b = self.words('Opposé et adjacent : par rapport à l’angle choisi.')
        self.new_page('Nommer les côtés sans ambiguïté', a, b)
        self.explain('L’hypoténuse est le côté de longueur cinq. C’est toujours le côté opposé à l’angle droit.', a, hold=4)
        self.explain('Pour notre angle theta, le côté opposé mesure trois. Le côté adjacent, autre que l’hypoténuse, mesure quatre. Si l’on change d’angle aigu, les rôles opposé et adjacent s’échangent.', b, hold=5)

        play_chapter_outline(self, CHAPTERS, 1, 'Construisons les trois rapports trigonométriques.', narration=narration)
        a = self.formula(r'\sin\theta=\frac{\text{opposé}}{\text{hypoténuse}}=\frac35', 40)
        b = self.formula(r'\cos\theta=\frac{\text{adjacent}}{\text{hypoténuse}}=\frac45', 40)
        c = self.formula(r'\tan\theta=\frac{\text{opposé}}{\text{adjacent}}=\frac34', 40)
        self.new_page('Sinus et cosinus', a, b, gap=0.4)
        self.explain('Le sinus est le rapport du côté opposé à l’hypoténuse. Il vaut ici trois cinquièmes.', a, hold=4)
        self.explain('Le cosinus compare le côté adjacent à l’hypoténuse. Il vaut quatre cinquièmes.', b, hold=4)
        self.new_page('La tangente', c)
        self.explain('La tangente compare le côté opposé au côté adjacent. Elle vaut trois quarts. Ces définitions concernent ici un angle aigu d’un triangle rectangle.', c, hold=4)

        a = panel(self.formula(r'\frac{3}{5}=\frac{6}{10},\qquad\frac45=\frac8{10}', 40))
        b = self.words('Agrandir le triangle conserve les rapports.')
        self.new_page('Même angle, mêmes rapports', a, b)
        self.explain('Si l’on multiplie toutes les longueurs par deux, les rapports ne changent pas.', a, hold=4)
        self.explain('Des triangles rectangles ayant le même angle aigu sont semblables. Les longueurs changent avec l’échelle, mais pas ces rapports.', b, hold=4)

        a = panel(self.formula(r'\sin30^\circ=\frac12,\qquad\frac{\text{opposé}}{10}=\frac12', 38))
        b = self.formula(r'\text{opposé}=10\times\frac12=5', 40)
        self.new_page('Retrouver une longueur', a, b)
        self.explain('Dans un autre triangle rectangle, l’angle choisi vaut trente degrés et l’hypoténuse mesure dix. Cherchons le côté opposé.', a, hold=4)
        self.explain('Le sinus de trente degrés vaut une moitié. Le côté opposé mesure donc cinq. Sur une calculatrice, le mode degrés doit correspondre à l’unité de l’angle.', b, hold=4)

        play_chapter_outline(self, CHAPTERS, 2, 'Relions les rapports à Pythagore, puis changeons d’angle.', narration=narration)
        a = panel(self.formula(r'\sin^2\theta+\cos^2\theta=\frac9{25}+\frac{16}{25}=1', 36))
        b = self.words('Une vérification issue du théorème de Pythagore.')
        self.new_page('Relier les rapports à la géométrie', a, b)
        self.explain('Dans le triangle trois, quatre, cinq, la somme du carré du sinus et du carré du cosinus vaut un.', a, hold=4)
        self.explain('C’est le théorème de Pythagore divisé par le carré de l’hypoténuse. Les formules sont liées à la géométrie.', b, hold=4)

        a = self.words('Triangle rectangle 3–4–5 :\nangle opposé au côté de longueur 4.')
        b = self.formula(r'\sin\varphi=\frac45,\quad\cos\varphi=\frac35,\quad\tan\varphi=\frac43', 38)
        self.guided_examples('trigonometrie_triangle')
        self.new_page('À vous : changer l’angle de référence', a, b)
        self.explain('Dans le triangle rectangle de côtés trois, quatre, cinq, quels sont les trois rapports pour l’angle opposé au côté de longueur quatre ?', a, hold=6, pause_after=6)
        self.explain('Le côté opposé devient quatre et l’adjacent devient trois. L’hypoténuse reste cinq. On obtient quatre cinquièmes, trois cinquièmes et quatre tiers.', b, hold=4)
        play_lesson_closing(
            self, 'Trigonométrie du triangle', ('Repérer d’abord l’angle de référence.', 'Nommer opposé, adjacent et hypoténuse.', 'Choisir le rapport qui relie les données.'),
            '\\text{Triangle rectangle : côtés }3,4,5', 'Pour l’angle opposé au côté 4, donnez\nle sinus, le cosinus et la tangente.',
            recap_spoken='Repérer d’abord l’angle de référence. Nommer opposé, adjacent et hypoténuse. Choisir le rapport qui relie les données.', practice_spoken='Reprenez le triangle trois, quatre, cinq. Pour l’angle opposé au côté de longueur quatre, donnez les trois rapports.', narration=narration,
        )
