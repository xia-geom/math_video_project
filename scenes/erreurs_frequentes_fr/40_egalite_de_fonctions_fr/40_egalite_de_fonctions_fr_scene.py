"""Equality of functions, retaining the course's declared-codomain convention."""
from manim import (BLACK, DOWN, RIGHT, WHITE, VGroup, config)

from tools import tts
from tools.teaching_chapters import (play_lesson_opening, play_chapter_outline, play_lesson_closing)
from tools.teaching_layout import TeachingScene, panel

CHAPTERS = ('Comparer les valeurs et l’image', 'Comparer domaine et arrivée', 'Appliquer le critère complet')

config.background_color = WHITE


class EgaliteDeFonctionsFR(TeachingScene):
    def chapter_narration(self, spoken):
        return self.voiceover(text=tts.ssml(spoken), subcaption=tts.strip_ssml(spoken))

    def construct(self):
        self.setup_narration()
        narration = None if self.silent else self.chapter_narration
        play_lesson_opening(self, 'Égalité de fonctions', 'Comparer le domaine, l’arrivée\net les valeurs à chaque entrée.', narration=narration)
        play_chapter_outline(self, CHAPTERS, 0, 'Commençons par les données et la question.', narration=narration)
        self._different_formulas_same_function()
        self._same_image_is_not_enough()
        play_chapter_outline(self, CHAPTERS, 1, 'Comparons maintenant les ensembles de départ et d’arrivée.', narration=narration)
        self._same_formula_different_domain()
        self._codomain_matters()
        play_chapter_outline(self, CHAPTERS, 2, 'Rassemblons les trois conditions de l’égalité.', narration=narration)
        self._formal_criterion()
        play_lesson_closing(
            self, 'Égalité de fonctions', ('Comparer les domaines.', 'Comparer les ensembles d’arrivée annoncés.', 'Comparer les valeurs pour chaque entrée.'),
            '\\begin{gathered}u,v:\\mathbb R\\to\\mathbb R\\\\u(x)=x^2,\\qquad v(x)=|x|\\end{gathered}', 'Même image : est-ce suffisant pour avoir u = v ?',
            recap_spoken='Comparer les domaines. Comparer les ensembles d’arrivée annoncés. Comparer les valeurs pour chaque entrée.', practice_spoken='Reprenez le carré et la valeur absolue sur les réels. Avoir la même image suffit-il ? Testez la même entrée.', narration=narration,
        )

    def _function_card(self, declaration, formula, color=BLACK):
        content = VGroup(self.formula(declaration, 34, color), self.formula(formula, 44))
        content.arrange(DOWN, buff=0.30)
        return panel(content, width=5.55, height=1.8, color=color)

    def _different_formulas_same_function(self):
        left = self._function_card(r'f:\mathbb R\to\mathbb R', r'f(x)=x^2')
        right = self._function_card(r'g:\mathbb R\to\mathbb R', r'g(x)=|x|^2')
        cards = VGroup(left, right).arrange(RIGHT, buff=0.55)
        question = self.words('Deux formules différentes. Deux fonctions différentes ?', 28)
        self.new_page('Même fonction, ou pas ?', cards, question, gap=0.65)
        self.explain('Voici x au carré, et le carré de la valeur absolue de x. Les deux fonctions vont des réels vers les réels.', cards)
        self.explain('Les formules ont l’air différentes. Est-ce suffisant pour dire que les fonctions sont différentes ?', question)
        identity = self.formula(r'\forall x\in\mathbb R,\qquad |x|^2=x^2', 46)
        verdict = self.formula(r'f=g', 62, BLACK)
        why = self.words('Mêmes entrées, même arrivée, mêmes valeurs.', 29)
        self.new_page('Ici, les fonctions sont égales', identity, verdict, why)
        self.explain('Non. Pour chaque réel, ces deux calculs donnent la même valeur. Cette identité le prouve pour toutes les entrées, pas seulement quelques exemples.', identity)
        self.explain('Le domaine et l’ensemble d’arrivée sont aussi les mêmes. Les fonctions sont donc égales.', verdict, why)

    def _same_image_is_not_enough(self):
        left = self._function_card(r'u:\mathbb R\to\mathbb R', r'u(x)=x^2')
        right = self._function_card(r'v:\mathbb R\to\mathbb R', r'v(x)=|x|')
        cards = VGroup(left, right).arrange(RIGHT, buff=0.55)
        image = self.formula(r'\operatorname{Im}(u)=\operatorname{Im}(v)=[0,+\infty[', 38)
        self.new_page('Même image : est-ce suffisant ?', cards, image)
        self.explain('Changeons maintenant la seconde règle : on prend simplement la valeur absolue.', cards)
        self.explain('Les deux fonctions atteignent tous les nombres positifs ou nuls. Elles ont la même image.', image)
        test = self.formula(r'u(2)=4\qquad\ne\qquad v(2)=2', 48)
        verdict = self.formula(r'u\ne v', 60, BLACK)
        why = self.words('Une seule entrée suffit à les distinguer.', 30)
        self.new_page('Essayons la même entrée : 2', test, verdict, why)
        self.explain('Pour deux, le carré donne quatre, tandis que la valeur absolue donne deux.', test)
        self.explain('Même ensemble de sorties possibles, mais pas la même sortie à chaque entrée. Les fonctions ne sont pas égales.', verdict, why)

    def _same_formula_different_domain(self):
        left = self._function_card(r'f:\mathbb R\to\mathbb R', r'f(x)=x^2')
        right = self._function_card(r'g:[0,+\infty[\to\mathbb R', r'g(x)=x^2')
        cards = VGroup(left, right).arrange(RIGHT, buff=0.55)
        domain = self.formula(r'\mathbb R\ne[0,+\infty[', 44, BLACK)
        self.new_page('Même formule, domaines différents', cards, domain)
        self.explain('Cette fois, les deux règles sont x au carré. Mais f accepte tous les réels; g accepte seulement les nombres positifs ou nuls.', cards)
        self.explain('Le domaine fait partie de la fonction. Ces deux domaines sont différents.', domain)
        left_test = self.formula(r'f(-2)=4', 48)
        right_test = self.formula(r'-2\notin\operatorname{Dom}(g)', 44, BLACK)
        restriction = self.formula(r'g=f\big|_{[0,+\infty[}', 44, BLACK)
        label = self.words('g est une restriction de f.', 30)
        self.new_page('L’entrée −2 révèle la différence', left_test, right_test, restriction, label, gap=0.35)
        self.explain('f de moins deux vaut quatre. Mais moins deux n’est pas une entrée autorisée pour g.', left_test, right_test)
        self.explain('On peut tout de même les relier : g est la restriction de f aux réels positifs ou nuls. Même calcul, sur un domaine plus petit.', restriction, label)

    def _codomain_matters(self):
        left = self._function_card(r'p:\mathbb R\to\mathbb R', r'p(x)=x^2')
        right = self._function_card(r'q:\mathbb R\to[0,+\infty[', r'q(x)=x^2')
        cards = VGroup(left, right).arrange(RIGHT, buff=0.55)
        convention = self.words('Convention du cours : l’arrivée fait partie de la fonction.', 27)
        self.new_page('Et l’ensemble d’arrivée ?', cards, convention)
        self.explain('Ici, les entrées et les valeurs calculées sont identiques. Mais les ensembles d’arrivée annoncés sont différents.', cards)
        self.explain('Dans la convention de ce cours, l’ensemble d’arrivée fait aussi partie de la fonction. On doit donc le comparer.', convention)
        p = VGroup(self.formula(r'\operatorname{Im}(p)=[0,+\infty[\subsetneq\mathbb R', 38),
                   self.words('p : pas surjective', 30, BLACK)).arrange(DOWN, buff=0.25)
        q = VGroup(self.formula(r'\operatorname{Im}(q)=[0,+\infty[', 38),
                   self.words('q : surjective', 30, BLACK)).arrange(DOWN, buff=0.25)
        self.new_page('L’arrivée change la surjectivité', p, q, gap=0.7)
        self.explain('p annonce tous les réels, mais n’atteint aucun nombre négatif. Elle n’est pas surjective.', p)
        self.explain('q annonce seulement les nombres positifs ou nuls, et les atteint tous. Elle est surjective.', q)

    def _formal_criterion(self):
        declaration = self.formula(r'f:A\to B,\qquad g:C\to D', 42)
        condition = self.formula(
            r'f=g\quad\Longleftrightarrow\quad\begin{cases}'
            r'A=C,\\B=D,\\\forall x\in A,\quad f(x)=g(x).\end{cases}', 40)
        box = panel(condition, width=9.8, height=2.5)
        self.new_page('Le critère complet', declaration, box, gap=0.55)
        self.explain('Rassemblons les trois vérifications pour les fonctions f et g.', declaration)
        self.explain('Même domaine. Même ensemble d’arrivée. Puis, pour chaque entrée du domaine, exactement la même valeur. Dans notre convention, c’est le critère complet.', box, hold=1.8)
