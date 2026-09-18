"""Equality of functions, retaining the course's declared-codomain convention."""
from manim import BLUE_D, DOWN, GREEN_D, RED_D, RIGHT, WHITE, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE


class EgaliteDeFonctionsFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._different_formulas_same_function()
        self._same_image_is_not_enough()
        self._same_formula_different_domain()
        self._codomain_matters()
        self._formal_criterion()
        self._summary()
        self.wait(1.2)

    def _function_card(self, declaration, formula, color=BLUE_D):
        content = VGroup(self.formula(declaration, 34, color), self.formula(formula, 44))
        content.arrange(DOWN, buff=0.30)
        return panel(content, width=5.55, height=1.8, color=color)

    def _different_formulas_same_function(self):
        left = self._function_card(r'f:\mathbb R\to\mathbb R', r'f(x)=x^2')
        right = self._function_card(r'g:\mathbb R\to\mathbb R', r'g(x)=|x|^2')
        cards = VGroup(left, right).arrange(RIGHT, buff=0.55)
        question = self.words('Deux formules différentes. Deux fonctions différentes ?', 28)
        self.new_page('Même fonction, ou pas ?', cards, question, gap=0.65)
        self.explain('Voici x au carré, et la valeur absolue de x au carré. Les deux fonctions vont des réels vers les réels.', cards)
        self.explain('Les formules ont l’air différentes. Est-ce suffisant pour dire que les fonctions sont différentes ?', question)
        identity = self.formula(r'\forall x\in\mathbb R,\qquad |x|^2=x^2', 46)
        verdict = self.formula(r'f=g', 62, GREEN_D)
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
        verdict = self.formula(r'u\ne v', 60, RED_D)
        why = self.words('Une seule entrée suffit à les distinguer.', 30)
        self.new_page('Essayons la même entrée : 2', test, verdict, why)
        self.explain('Pour deux, le carré donne quatre, tandis que la valeur absolue donne deux.', test)
        self.explain('Même ensemble de sorties possibles, mais pas la même sortie à chaque entrée. Les fonctions ne sont pas égales.', verdict, why)

    def _same_formula_different_domain(self):
        left = self._function_card(r'f:\mathbb R\to\mathbb R', r'f(x)=x^2')
        right = self._function_card(r'g:[0,+\infty[\to\mathbb R', r'g(x)=x^2')
        cards = VGroup(left, right).arrange(RIGHT, buff=0.55)
        domain = self.formula(r'\mathbb R\ne[0,+\infty[', 44, BLUE_D)
        self.new_page('Même formule, domaines différents', cards, domain)
        self.explain('Cette fois, les deux règles sont x au carré. Mais f accepte tous les réels; g accepte seulement les nombres positifs ou nuls.', cards)
        self.explain('Le domaine fait partie de la fonction. Ces deux domaines sont différents.', domain)
        left_test = self.formula(r'f(-2)=4', 48)
        right_test = self.formula(r'-2\notin\operatorname{Dom}(g)', 44, RED_D)
        restriction = self.formula(r'g=f\big|_{[0,+\infty[}', 44, BLUE_D)
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
                   self.words('p : pas surjective', 30, RED_D)).arrange(DOWN, buff=0.25)
        q = VGroup(self.formula(r'\operatorname{Im}(q)=[0,+\infty[', 38),
                   self.words('q : surjective', 30, GREEN_D)).arrange(DOWN, buff=0.25)
        self.new_page('L’arrivée change la surjectivité', p, q, gap=0.7)
        self.explain('p annonce tous les réels, mais n’atteint aucun nombre négatif. Elle n’est pas surjective.', p)
        self.explain('q annonce seulement les nombres positifs ou nuls, et les atteint tous. Elle est surjective.', q)

    def _formal_criterion(self):
        declaration = self.formula(r'f:A\to B,\qquad g:C\to D', 42)
        condition = self.formula(
            r'f=g\quad\Longleftrightarrow\quad\begin{cases}'
            r'A=C,\\B=D,\\\forall x\in A,\quad f(x)=g(x).\end{cases}', 40)
        box = panel(condition, width=9.8, height=2.5)
        self.new_page('Le critère complet — convention du cours', declaration, box, gap=0.55)
        self.explain('Rassemblons les trois vérifications pour les fonctions f et g.', declaration)
        self.explain('Même domaine. Même ensemble d’arrivée. Puis, pour chaque entrée du domaine, exactement la même valeur. Dans notre convention, c’est le critère complet.', box, hold=1.8)

    def _summary(self):
        message = self.words('Une fonction n’est pas seulement une formule.', 32, BLUE_D)
        checks = VGroup(self.words('Le domaine', 32), self.words('L’ensemble d’arrivée', 32),
                        self.words('La valeur à chaque entrée', 32)).arrange(DOWN, buff=0.38)
        self.new_page('À retenir', message, checks, gap=0.7)
        self.explain('Ne vous fiez donc ni à l’apparence de la formule, ni à la seule image.', message)
        self.explain('Comparez le domaine, l’arrivée et les valeurs à chaque entrée. C’est cela, comparer deux fonctions.', checks)
