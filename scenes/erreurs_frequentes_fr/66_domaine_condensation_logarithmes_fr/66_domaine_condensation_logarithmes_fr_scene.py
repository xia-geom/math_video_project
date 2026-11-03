"""MAT0339 6.4 et 6.8 : conserver le domaine en condensant des logarithmes."""

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    RED_D,
    WHITE,
    Arrow,
    Dot,
    MathTex,
    NumberLine,
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


class DomaineCondensationLogarithmesFR(TeachingScene):
    """Une identité valable sur un domaine ne donne pas le droit de l'élargir."""

    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._original_domain()
        self._law_with_conditions()
        self._compare_domains()
        self._negative_candidate()
        self._solve_and_verify()
        self._self_check()
        self._self_check_calculation()
        self._self_check_filter()
        self._takeaway()
        self.wait(1.2)

    def _question(self):
        equation = self.formula(r'\ln(x-1)+\ln(x+1)=\ln8', 46)
        condensed = self.formula(r'\ln(x^2-1)=\ln8', 43)
        candidates = self.formula(r'x^2=9\quad\Longrightarrow\quad x=3\ \text{ou}\ x=-3', 41)
        question = self.words('Les deux candidats répondent-ils à la question ?', 29)
        self.new_page('Deux candidats, combien de solutions ?', equation,
                      condensed, candidates, question, gap=0.52)
        self.explain(
            'Le manuel propose cette équation logarithmique. En condensant '
            'les deux logarithmes, on obtient le logarithme de x au carré '
            'moins un. Le calcul conduit ensuite à trois et à moins trois. '
            'La loi utilisée ressemble à une règle correcte. Peut-on '
            'pour autant conserver les deux candidats ?',
            equation, condensed, candidates, question, hold=2,
        )

    def _original_domain(self):
        first = self.formula(r'x-1>0\quad\Longleftrightarrow\quad x>1', 43)
        second = self.formula(r'x+1>0\quad\Longleftrightarrow\quad x>-1', 43)
        both = self.formula(r'D=]1,+\infty[', 48, BLUE_D)
        note = self.words('Les deux arguments doivent être positifs.', 30)
        self.new_page('Le domaine vient en premier', first, second, both,
                      note, gap=0.48)
        self.explain(
            'Nous travaillons dans les nombres réels. Chaque argument '
            'd’un logarithme doit être strictement positif. Pour le '
            'premier logarithme, x moins un doit être positif : il faut '
            'x strictement supérieur à un. Pour le second, x doit être '
            'strictement supérieur à moins un.', first, second, hold=2,
        )
        self.explain(
            'Les deux conditions doivent être vraies en même temps. '
            'Le domaine de l’expression initiale est donc l’intervalle '
            'ouvert allant de un à plus l’infini. Ce domaine accompagne '
            'toutes les étapes qui suivent.', both, note, hold=2,
        )

    def _law_with_conditions(self):
        hypotheses = self.formula(r'a>0\quad\text{et}\quad b>0', 43, BLUE_D)
        law = self.formula(r'\ln a+\ln b=\ln(ab)', 48)
        application = self.formula(
            r'\ln(x-1)+\ln(x+1)=\ln(x^2-1)\qquad(x>1)', 39,
        )
        self.new_page('Une loi correcte, avec ses conditions', hypotheses,
                      law, application, gap=0.68)
        self.explain(
            'La loi du produit est bien correcte quand les deux facteurs '
            'sont strictement positifs. Elle transforme une somme de '
            'logarithmes en logarithme d’un produit. Ici, nous pouvons '
            'l’appliquer pour tout x supérieur à un, puisque les deux '
            'arguments sont alors positifs.', hypotheses, law, hold=2,
        )
        self.explain(
            'Mais l’égalité reste attachée à cette condition. Une '
            'expression nouvelle peut être définie en des points où '
            'l’expression de départ n’existait pas. Il faut distinguer '
            'une simplification autorisée d’un changement de domaine.',
            application, hold=2,
        )

    def _domain_strip(self, label, *, negative_branch=False):
        line = NumberLine(
            x_range=[-4, 4, 1], length=9.2, color=BLACK,
            include_numbers=True, numbers_to_include=[-3, -1, 0, 1, 3],
            font_size=25, decimal_number_config={'color': BLACK},
        )
        admitted = VGroup(
            Arrow(line.n2p(1), line.n2p(4), buff=0, color=BLUE_D,
                  stroke_width=6, max_tip_length_to_length_ratio=0.07),
            Dot(line.n2p(1), radius=0.085, color=BLUE_D,
                fill_color=WHITE, fill_opacity=1, stroke_width=3),
        )
        if negative_branch:
            admitted.add(
                Arrow(line.n2p(-1), line.n2p(-4), buff=0, color=BLUE_D,
                      stroke_width=6, max_tip_length_to_length_ratio=0.07),
                Dot(line.n2p(-1), radius=0.085, color=BLUE_D,
                    fill_color=WHITE, fill_opacity=1, stroke_width=3),
            )
        caption = self.words(label, 29)
        diagram = VGroup(line, admitted)
        return VGroup(caption, diagram).arrange(DOWN, buff=0.35)

    def _compare_domains(self):
        original = self._domain_strip('Expression initiale : x > 1')
        condensed = self._domain_strip('Logarithme du produit : x < −1 ou x > 1',
                                       negative_branch=True)
        note = self.words('La partie gauche n’appartient pas au domaine initial.', 28)
        self.new_page('Le produit accepte aussi deux négatifs', original,
                      condensed, note, gap=0.55)
        self.explain(
            'La première droite montre le domaine initial. Les cercles '
            'ouverts excluent les bornes et les flèches prolongent les '
            'intervalles. Pour le seul logarithme du produit, il suffit '
            'que x au carré moins un soit positif. Cela arrive aussi '
            'quand x est inférieur à moins un.', original, condensed, hold=2,
        )
        self.explain(
            'Dans cette partie gauche, les deux facteurs sont négatifs '
            'et leur produit est positif. Le logarithme du produit existe, '
            'mais les deux logarithmes séparés n’existent pas dans les '
            'réels. Cette zone supplémentaire ne peut pas fournir une '
            'solution de l’équation de départ.', note, hold=2,
        )

    def _negative_candidate(self):
        candidate = self.formula(r'x=-3', 46, RED_D)
        factors = self.formula(r'x-1=-4,\qquad x+1=-2', 42)
        original = self.words('ln(−4) et ln(−2) ne sont pas définis dans ℝ.', 29, RED_D)
        product = self.formula(r'(-4)(-2)=8>0\quad\Longrightarrow\quad\ln8\ \text{existe}', 40)
        self.new_page('Tester le candidat dans l’original', candidate,
                      factors, original, product, gap=0.48)
        self.explain(
            'Testons moins trois directement dans les arguments '
            'originaux. Nous obtenons moins quatre et moins deux. '
            'Leurs logarithmes ne sont pas définis dans les réels. '
            'Moins trois est donc rejeté avant toute addition.',
            candidate, factors, original, hold=2,
        )
        self.explain(
            'Le produit de moins quatre par moins deux vaut pourtant '
            'huit. Le logarithme de huit existe. Voilà exactement '
            'l’information perdue si l’on oublie les deux conditions '
            'avant de condenser.', product, hold=2,
        )

    def _solve_and_verify(self):
        domain = self.formula(r'\text{Sur }D=]1,+\infty[\ :', 37, BLUE_D)
        algebra = self.formula(
            r'\ln(x^2-1)=\ln8\ \Longleftrightarrow\ x^2-1=8', 39,
        )
        selected = self.formula(r'x=3\ \text{ou}\ x=-3\quad\longrightarrow\quad S=\{3\}', 40)
        check = self.formula(r'\ln(3-1)+\ln(3+1)=\ln2+\ln4=\ln8', 39, GREEN_D)
        self.new_page('Résoudre, filtrer, vérifier', domain, algebra,
                      selected, check, gap=0.49)
        self.explain(
            'Sur le domaine conservé, l’injectivité du logarithme '
            'permet d’égaler les arguments. On obtient x au carré '
            'égal à neuf, donc deux candidats algébriques. Seul '
            'trois appartient au domaine initial.',
            domain, algebra, selected, hold=2,
        )
        self.explain(
            'Enfin, dans l’équation de départ, trois donne logarithme '
            'de deux plus logarithme de quatre. Les arguments sont '
            'positifs et la somme vaut bien logarithme de huit. '
            'Cette vérification confirme la solution admise.', check, hold=2,
        )

    def _self_check(self):
        equation = self.formula(r'\ln(x-1)+\ln(x+2)=\ln12', 46)
        first = self.words('Écrivez d’abord le domaine.', 31)
        second = self.words('Puis trouvez les candidats et la solution admise.', 29)
        self.new_page('À vous : l’exercice 6.4 B du cahier', equation,
                      first, second, gap=0.75)
        self.explain(
            'Voici maintenant l’exercice du cahier, avec x plus deux '
            'dans le second logarithme et douze au second membre. '
            'Écrivez les conditions avant de condenser. Résolvez '
            'ensuite l’équation et décidez quel candidat est admissible. '
            'Vous pouvez garder une expression exacte avec une racine.',
            equation, first, second, hold=2, pause_after=6,
        )

    def _self_check_calculation(self):
        domain = self.formula(r'x>1\quad\text{et}\quad x>-2\quad\Longrightarrow\quad x>1', 39)
        product = self.formula(r'(x-1)(x+2)=12', 46)
        polynomial = self.formula(r'x^2+x-14=0', 47)
        roots = self.formula(r'x_- =\frac{-1-\sqrt{57}}2,\qquad x_+=\frac{-1+\sqrt{57}}2', 41)
        self.new_page('Réponse : le domaine et les candidats', domain,
                      product, polynomial, roots, gap=0.48)
        self.explain(
            'Les deux conditions donnent encore x strictement '
            'supérieur à un. Sur ce domaine, la condensation et '
            'l’injectivité du logarithme donnent x moins un fois '
            'x plus deux égal à douze. En développant et en ramenant '
            'tout à zéro, on obtient x au carré plus x moins quatorze.',
            domain, product, polynomial, hold=2,
        )
        self.explain(
            'Le discriminant vaut un plus cinquante-six, soit '
            'cinquante-sept. La formule quadratique donne les deux '
            'candidats affichés. Le calcul n’a pas encore remplacé '
            'le contrôle du domaine.', roots, hold=2,
        )

    def _self_check_filter(self):
        rejected = self.formula(r'x_-<1\quad\Longrightarrow\quad\text{rejeté}', 42, RED_D)
        accepted = self.formula(r'\alpha=\frac{-1+\sqrt{57}}2>1', 46, GREEN_D)
        product = self.formula(r'(\alpha-1)(\alpha+2)=12', 43)
        original = self.formula(r'\ln(\alpha-1)+\ln(\alpha+2)=\ln12', 40)
        self.new_page('La condition fait partie de la réponse', rejected,
                      accepted, product, original, gap=0.5)
        self.explain(
            'Le candidat avec le signe moins est inférieur à un et '
            'doit être rejeté. Celui avec le signe plus est supérieur '
            'à un : la racine de cinquante-sept est supérieure à '
            'trois. Ses deux arguments sont donc positifs.',
            rejected, accepted, hold=2,
        )
        self.explain(
            'Notons cette valeur alpha. Comme elle résout l’équation '
            'quadratique, le produit des deux arguments vaut douze. '
            'Ils sont tous deux positifs : la loi des logarithmes '
            'permet maintenant de vérifier l’équation originale. '
            'Il n’est pas nécessaire d’arrondir alpha.', product, original, hold=2,
        )

    def _takeaway(self):
        steps = VGroup(
            self.words('Écrire le domaine de l’expression initiale.', 31),
            self.words('Conserver ce domaine pendant la condensation.', 30),
            self.words('Filtrer les candidats et vérifier dans l’original.', 30),
        ).arrange(DOWN, buff=0.65)
        law = self.formula(r'\ln a+\ln b=\ln(ab)\quad\text{pour }a>0,\ b>0', 40, BLUE_D)
        self.new_page('À retenir : la loi garde ses conditions', steps, law, gap=0.75)
        self.explain(
            'La condensation ne crée pas une nouvelle permission '
            'd’utiliser des arguments négatifs. On écrit d’abord '
            'le domaine, on le conserve pendant le calcul, puis '
            'on filtre les candidats et on vérifie dans l’équation '
            'originale. Une formule plus courte doit conserver '
            'les conditions de la formule de départ.', steps, law, hold=2,
        )
