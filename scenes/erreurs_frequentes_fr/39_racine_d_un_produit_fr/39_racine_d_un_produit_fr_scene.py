"""Root of a product: real-domain conditions, counterexamples, proof, sign table."""
from manim import BLACK, BLUE_D, DOWN, GREEN_D, RED_D, RIGHT, WHITE, VGroup, config

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE


class RacineProduitHypothesesFR(TeachingScene):
    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._opening_question()
        self._working_example()
        self._reveal_hypotheses()
        self._illegal_substitution()
        self._complex_extension()
        self._why_theorem_works()
        self._sign_table()
        self._summary()
        self.wait(1.2)

    def _opening_question(self):
        rule = self.formula(r'\sqrt{ab}\overset{?}{=}\sqrt a\,\sqrt b', 64)
        question = self.words('Toujours ? Même avec des nombres négatifs ?', 30)
        self.new_page('La racine d’un produit', rule, question, gap=0.7)
        self.explain('Cette règle paraît familière. La racine d’un produit, ce serait le produit des racines.', rule)
        self.explain('Mais est-ce toujours vrai ? Essayons de voir où elle fonctionne, et où elle s’arrête.', question)

    def _working_example(self):
        left = self.formula(r'\sqrt{4\cdot9}=\sqrt{36}=6', 48)
        right = self.formula(r'\sqrt4\,\sqrt9=2\cdot3=6', 48, BLUE_D)
        conclusion = self.words('Ici, les deux calculs donnent 6.', 30)
        self.new_page('Commençons avec 4 et 9', left, right, conclusion)
        self.explain('D’un côté, quatre fois neuf donne trente-six. Sa racine vaut six.', left)
        self.explain('De l’autre, on multiplie deux par trois. On retrouve six.', right)
        self.explain('Cela marche ici. Un exemple ne suffit pourtant pas à prouver une règle générale.', conclusion)

    def _reveal_hypotheses(self):
        condition = self.formula(r'a\ge0,\qquad b\ge0', 48, BLUE_D)
        rule = panel(self.formula(r'\sqrt{ab}=\sqrt a\,\sqrt b', 54), width=9, height=1.6)
        note = self.words('Dans les réels, les conditions font partie de la règle.', 28)
        self.new_page('Les conditions à garder', condition, rule, note)
        self.explain('Dans les nombres réels, on demande que les deux facteurs soient positifs ou nuls.', condition)
        self.explain('Sous ces conditions, l’égalité est vraie. Nous allons expliquer pourquoi.', rule)
        self.explain('Les conditions ne sont pas un détail. On doit les vérifier avant d’utiliser la formule.', note)

    def _illegal_substitution(self):
        setting = self.formula(r'a=b=-1', 44, BLUE_D)
        lhs = self.formula(r'\sqrt{(-1)(-1)}=\sqrt1=1', 46)
        rhs = self.formula(r'\sqrt{-1}\,\sqrt{-1}', 46, RED_D)
        undefined = self.words('Non définie dans les réels', 30, RED_D)
        right = VGroup(rhs, undefined).arrange(DOWN, buff=0.25)
        self.new_page('Et si les deux facteurs valent −1 ?', setting, lhs, right)
        self.explain('Prenons deux facteurs égaux à moins un. Leur produit vaut un.', setting, lhs)
        self.explain('Mais, dans les réels, la racine de moins un n’existe pas. On ne peut donc pas séparer les racines.', right)

    def _complex_extension(self):
        principal = self.formula(r'\sqrt{-1}=i', 46, BLUE_D)
        lhs = self.formula(r'\sqrt{(-1)(-1)}=1', 44)
        rhs = self.formula(r'\sqrt{-1}\,\sqrt{-1}=i^2=-1', 44)
        verdict = self.formula(r'1\ne-1', 52, RED_D)
        self.new_page('Parenthèse : les racines complexes', principal, lhs, rhs, verdict, gap=0.35)
        self.explain('Avec les nombres complexes, la racine principale de moins un vaut i.', principal)
        self.explain('Le premier calcul donne un. Le second donne i au carré, donc moins un.', lhs, rhs)
        self.explain('Ce n’est pas une contradiction entre les nombres : la règle du produit ne s’applique pas en général aux racines complexes principales.', verdict)

    def _why_theorem_works(self):
        condition = self.formula(r'a,b\ge0', 40, BLUE_D)
        u = self.formula(r'u=\sqrt{ab}\ge0', 44)
        v = self.formula(r'v=\sqrt a\,\sqrt b\ge0', 44)
        same = self.formula(r'u^2=v^2=ab\quad\Longrightarrow\quad u=v', 44, BLUE_D)
        self.new_page('Pourquoi cela fonctionne', condition, u, v, same, gap=0.36)
        self.explain('Revenons à deux facteurs positifs ou nuls. Appelons u la racine du produit, et v le produit des racines.', condition, u, v)
        self.explain('Ces deux nombres sont non négatifs, et leurs carrés valent tous les deux a fois b. Ils sont donc égaux. C’est exactement le rôle des conditions.', same, hold=1.6)

    def _sign_table(self):
        """One symbolic table; the last three rows also cover exchanged factors."""
        centers = [-4.55, -2.30, 0.65, 4.10]
        widths = [2.0, 2.0, 3.5, 3.0]
        headers = [r'a', r'b', r'\sqrt{ab}', r'\sqrt a\,\sqrt b']
        cases = [
            (r'\ge0', r'\ge0', r'\checkmark', r'\checkmark'),
            (r'<0', r'>0', r'\times', r'\times'),
            (r'=0', r'<0', r'0', r'\times'),
            (r'<0', r'<0', r'\checkmark', r'\times'),
        ]
        header = VGroup(*[panel(self.formula(value, 36, BLUE_D), width=width,
                                 height=0.66, padding=0.12).move_to([x, 0, 0])
                          for value, x, width in zip(headers, centers, widths, strict=True)])
        rows = []
        for row in cases:
            cells = []
            for value, x, width in zip(row, centers, widths, strict=True):
                color = GREEN_D if value == r'\checkmark' else RED_D if value == r'\times' else BLACK
                cell = panel(self.formula(value, 34, color), width=width, height=0.66, padding=0.12)
                cell.move_to([x, 0, 0])
                cells.append(cell)
            rows.append(VGroup(*cells))
        table = VGroup(header, *rows).arrange(DOWN, buff=0.11)
        yes = VGroup(self.formula(r'\checkmark', 30, GREEN_D), self.words('définie dans ℝ', 26)).arrange(RIGHT, buff=0.2)
        no = VGroup(self.formula(r'\times', 30, RED_D), self.words('non définie dans ℝ', 26)).arrange(RIGHT, buff=0.2)
        legend = VGroup(yes, no).arrange(RIGHT, buff=0.7)
        self.new_page('Les signes, en un coup d’œil', table, legend, gap=0.30)
        self.explain('La coche signifie que l’expression existe dans les réels. La croix signifie qu’elle n’y est pas définie.', header, legend)
        self.explain('Avec deux facteurs positifs ou nuls, les deux expressions existent.', rows[0])
        self.explain('Avec des signes strictement opposés, aucune des deux expressions complètes n’est définie.', rows[1])
        self.explain('Avec zéro et un facteur négatif, la racine du produit vaut zéro. Les racines séparées ne sont toujours pas définies.', rows[2])
        self.explain('Avec deux facteurs négatifs, le produit est positif : sa racine existe, mais pas les deux racines séparées. Échanger les facteurs ne change pas ces conclusions.', rows[3], hold=1.8)

    def _summary(self):
        condition = self.formula(r'a\ge0\quad\text{et}\quad b\ge0', 46, BLUE_D)
        rule = self.formula(r'\sqrt{ab}=\sqrt a\,\sqrt b', 56)
        lesson = self.words('Vérifier les conditions, puis appliquer la règle.', 29)
        self.new_page('À retenir', condition, rule, lesson, gap=0.7)
        self.explain('Pour séparer la racine d’un produit réel, vérifiez d’abord chacun des deux facteurs.', condition)
        self.explain('Quand ils sont tous les deux positifs ou nuls, vous pouvez appliquer l’égalité.', rule)
        self.explain('Retenez ce réflexe : les conditions d’abord, la formule ensuite.', lesson)
