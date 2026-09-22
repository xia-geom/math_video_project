"""S03 — elementary probability models, not just counting outcomes."""
from fractions import Fraction

from manim import BLACK, BLUE_D, RIGHT, WHITE, MathTex, Square, Tex, Text, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)

FAIR_WEIGHTS = (Fraction(1, 6),) * 6
BIASED_WEIGHTS = (Fraction(1, 10),) * 5 + (Fraction(1, 2),)
EVEN = {2, 4, 6}
LARGE = {4, 5, 6}


def event_probability(event, weights):
    if len(weights) != 6 or any(w < 0 for w in weights) or sum(weights) != 1:
        raise ValueError('Six nonnegative probabilities summing to one are required.')
    if not set(event) <= set(range(1, 7)):
        raise ValueError('Event outside the sample space.')
    return sum((weights[i - 1] for i in set(event)), Fraction(0))


class ModelesProbabilistesFR(TeachingScene):
    def outcomes(self, selected=()):
        cells = []
        for i in range(1, 7):
            box = Square(side_length=0.8, stroke_color=BLACK, stroke_width=2,
                         fill_color=BLUE_D, fill_opacity=0.25 if i in selected else 0)
            cells.append(VGroup(box, self.formula(str(i), 36).move_to(box)))
        return VGroup(*cells).arrange(RIGHT, buff=0.18)

    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        a = self.outcomes()
        b = panel(self.formula(r'\Omega=\{1,2,3,4,5,6\}', 40))
        self.new_page('Une expérience, des issues possibles', a, b)
        self.explain('On lance un dé et on observe le numéro obtenu. Les six résultats possibles sont les issues de l’expérience.', a, hold=3)
        self.explain('Leur ensemble s’appelle l’univers. Une probabilité décrit un modèle de cette expérience, pas une certitude sur le prochain lancer.', b, hold=4)

        a = self.outcomes(EVEN)
        b = panel(self.formula(r'A=\{2,4,6\},\qquad P(A)=\frac36=\frac12', 38))
        self.new_page('Un événement est un ensemble d’issues', a, b)
        self.explain('L’événement A signifie obtenir un nombre pair. Il regroupe les issues deux, quatre et six.', a, hold=3)
        self.explain('Si le dé est équilibré, les six issues ont la même probabilité. On peut alors diviser le nombre d’issues favorables par le nombre total.', b, hold=4)

        a = panel(self.formula(r'P(1)=\cdots=P(5)=\frac1{10},\quad P(6)=\frac12', 36))
        b = self.formula(r'5\times\frac1{10}+\frac12=1', 38)
        c = panel(self.formula(r'P(A)=\frac1{10}+\frac1{10}+\frac12=\frac7{10}', 38))
        self.new_page('Autre modèle : un dé non équilibré', a, b, c, gap=0.3)
        self.explain('Imaginons maintenant ce modèle non uniforme. Chaque issue de un à cinq a une probabilité d’un dixième, et six a une probabilité d’une moitié.', a, hold=4)
        self.explain('Les probabilités sont positives et leur somme vaut un.', b, hold=3)
        self.explain('Pour obtenir un nombre pair, on additionne les poids de deux, quatre et six. Le résultat vaut sept dixièmes, et non une moitié. Compter les issues ne suffit donc pas sans équiprobabilité.', c, hold=5)

        a = panel(self.formula(r'P(A^{\mathrm c})=1-P(A)', 40))
        b = self.formula(r'1-\frac7{10}=\frac3{10}', 40)
        self.new_page('L’événement contraire', a, b)
        self.explain('Ne pas obtenir un nombre pair est l’événement contraire. Dans cet univers, cela signifie obtenir un nombre impair.', a, hold=3)
        self.explain('Dans notre modèle non uniforme, sa probabilité vaut un moins sept dixièmes, donc trois dixièmes.', b, hold=4)

        a = panel(self.formula(r'A=\{2,4,6\},\quad B=\{4,5,6\}', 38))
        b = self.formula(r'A\cap B=\{4,6\},\quad A\cup B=\{2,4,5,6\}', 36)
        self.new_page('Retour au dé équilibré : « A ou B »', a, b)
        self.explain('Revenons explicitement au dé équilibré. B signifie obtenir un nombre strictement supérieur à trois.', a, hold=3)
        self.explain('Quatre et six appartiennent aux deux événements. Pour A ou B, on les compte une seule fois.', b, hold=4)

        a = panel(self.formula(r'P(A\cup B)=P(A)+P(B)-P(A\cap B)', 36))
        b = self.formula(r'\frac36+\frac36-\frac26=\frac46=\frac23', 40)
        self.new_page('Éviter le double comptage', a, b)
        self.explain('On additionne les probabilités, puis on retire celle de l’intersection. Sans cette correction, on compterait deux fois les issues communes.', a, hold=4)
        self.explain('Ici, la probabilité d’obtenir un nombre pair ou supérieur à trois vaut deux tiers. La simple addition n’est valable que pour des événements disjoints.', b, hold=4)

        a = self.words('Trois issues favorables sur six : forcément une moitié ?')
        b = panel(self.formula(r'\text{Le comptage seul ne suffit pas.}', 32))
        self.new_page('À vous : quelle hypothèse manque ?', a, b)
        self.explain('Une personne compte trois issues favorables parmi six. Sa réponse d’une moitié est-elle toujours justifiée ?', a, hold=6, pause_after=6)
        self.explain('Non. Il faut connaître les probabilités des issues. Le quotient des effectifs est justifié dans le modèle équiprobable ; pour un autre modèle, on additionne les poids des issues favorables.', b, hold=4)
        self.wait(1)
