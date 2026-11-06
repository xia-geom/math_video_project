"""MAT0339 3.5 : distinguer la réciproque de f et l'inverse de ses valeurs."""

from manim import (
    BLACK,
    BLUE_D,
    DOWN,
    GREEN_D,
    LEFT,
    RED_D,
    RIGHT,
    WHITE,
    Arrow,
    MathTex,
    Tex,
    Text,
    VGroup,
    config,
)

from tools.branding import play_uqam_intro
from tools.teaching_layout import TeachingScene, panel

config.background_color = WHITE
Text.set_default(color=BLACK)
Tex.set_default(color=BLACK)
MathTex.set_default(color=BLACK)


class ReciproqueInverseNumeriqueFR(TeachingScene):
    """Comparer les opérations, les domaines et les contrôles qui les définissent."""

    def construct(self):
        self.setup_narration()
        play_uqam_intro(self)
        self._question()
        self._undo_the_function()
        self._invert_a_value()
        self._derive_inverse()
        self._compare_domains()
        self._different_checks()
        self._existence_conditions()
        self._self_check()
        self._self_check_answer()
        self._self_check_compositions()
        self._takeaway()
        self.wait(1.2)

    def _flow(self, left_value, rule, right_value, *, reverse=False):
        left = panel(self.formula(left_value, 44), width=1.55, height=1.20)
        machine = panel(self.formula(rule, 39), width=3.25, height=1.20)
        right = panel(self.formula(right_value, 44), width=1.55, height=1.20)
        start, end = (RIGHT * 0.40, LEFT * 0.40) if reverse else (LEFT * 0.40, RIGHT * 0.40)
        arrows = [Arrow(start, end, buff=0, color=BLUE_D, stroke_width=3)
                  for _ in range(2)]
        return VGroup(left, arrows[0], machine, arrows[1], right).arrange(RIGHT, buff=0.22)

    def _question(self):
        data = self.formula(r'f:\mathbb R\to\mathbb R,\qquad f(x)=3x-5', 43)
        notation = self.formula(r'f^{-1}(4)\quad\stackrel{?}{=}\quad\frac1{f(4)}', 53)
        question = self.words('Que demande chaque écriture ?', 32)
        self.new_page('Un exposant, deux opérations', data, notation, question, gap=0.8)
        self.explain(
            'Pour la fonction qui multiplie par trois puis soustrait '
            'cinq, comparons deux écritures. F exposant moins un de '
            'quatre désigne une valeur de la fonction réciproque. '
            'Un sur f de quatre désigne l’inverse numérique d’une '
            'valeur. Le même petit signe ne commande pas la même '
            'opération. Vérifions-le avec des nombres.',
            data, notation, question, hold=2,
        )

    def _undo_the_function(self):
        forward = self._flow('3', 'f', '4')
        backward = self._flow('3', r'f^{-1}', '4', reverse=True)
        statement = self.formula(r'f(3)=4\quad\Longrightarrow\quad f^{-1}(4)=3', 43, GREEN_D)
        self.new_page('La réciproque retrouve l’entrée', forward,
                      backward, statement, gap=0.7)
        self.explain(
            'La fonction envoie trois sur quatre, puisque trois '
            'fois trois moins cinq vaut quatre. Sa réciproque '
            'doit retrouver l’entrée trois à partir de la sortie '
            'quatre. Les flèches du deuxième trajet sont donc '
            'orientées en sens inverse.', forward, backward, hold=2,
        )
        self.explain(
            'La question f réciproque de quatre signifie : quelle '
            'entrée a produit quatre ? La réponse est trois. '
            'Nous avons défait une transformation de l’entrée '
            'vers la sortie.', statement, hold=2,
        )

    def _invert_a_value(self):
        evaluation = self._flow('4', 'f', '7')
        reciprocal = self._flow('7', r'z\mapsto1/z', r'1/7')
        result = self.formula(r'\frac1{f(4)}=\frac17\ne3=f^{-1}(4)', 44)
        self.new_page('L’inverse numérique transforme la valeur', evaluation,
                      reciprocal, result, gap=0.7)
        self.explain(
            'Pour un sur f de quatre, on commence au contraire '
            'par calculer f de quatre. Trois fois quatre moins '
            'cinq vaut sept. On prend ensuite l’inverse numérique '
            'de sept, donc un septième. La nouvelle opération '
            'agit sur le nombre obtenu.', evaluation, reciprocal, hold=2,
        )
        self.explain(
            'Avec la même entrée quatre dans les deux écritures, '
            'nous obtenons donc trois pour la réciproque et un '
            'septième pour l’inverse numérique de la valeur. '
            'Cette comparaison détecte immédiatement la confusion.',
            result, hold=2,
        )

    def _derive_inverse(self):
        steps = VGroup(
            self.formula(r'y=3x-5', 45),
            self.formula(r'y+5=3x', 45),
            self.formula(r'x=\frac{y+5}{3}', 47),
        ).arrange(DOWN, buff=0.45)
        inverse = self.formula(r'f^{-1}(y)=\frac{y+5}{3}', 48, BLUE_D)
        self.new_page('Défaire les opérations dans l’ordre inverse', steps,
                      inverse, gap=0.65)
        self.explain(
            'Pour retrouver l’entrée, partons de y égal à trois '
            'x moins cinq. Ajoutons cinq, puis divisons par trois. '
            'Cela défait les deux opérations dans l’ordre inverse. '
            'La réciproque envoie donc y sur y plus cinq, divisé '
            'par trois.', steps, inverse, hold=2,
        )

    def _compare_domains(self):
        inverse = self.formula(r'f^{-1}(y)=\frac{y+5}{3},\qquad y\in\mathbb R', 42)
        reciprocal = self.formula(r'h(x)=\frac1{f(x)}=\frac1{3x-5},\qquad x\ne\frac53', 41)
        zero = self.formula(r'f(5/3)=0\quad\Longrightarrow\quad h(5/3)\ \text{non défini}', 37, RED_D)
        allowed = self.formula(r'f^{-1}(5/3)=\frac{20}{9}\quad\text{existe}', 42, GREEN_D)
        self.new_page('Les domaines sont aussi différents', inverse,
                      reciprocal, zero, allowed, gap=0.52)
        self.explain(
            'La réciproque est définie pour toute sortie réelle '
            'de cette fonction affine. Son dénominateur est '
            'toujours trois. Pour la fonction h égale à un sur '
            'f, il faut en revanche éviter une valeur nulle '
            'de f. L’entrée cinq tiers doit être exclue.',
            inverse, reciprocal, hold=2,
        )
        self.explain(
            'En cinq tiers, h demanderait une division par zéro. '
            'Mais la réciproque peut parfaitement recevoir cinq '
            'tiers comme entrée : elle renvoie vingt neuvièmes. '
            'L’existence d’une valeur dans l’un des domaines '
            'ne décide pas de son existence dans l’autre.',
            zero, allowed, hold=2,
        )

    def _different_checks(self):
        inverse_label = self.words('Réciproque : composer redonne l’entrée.', 30)
        inverse_check = self.formula(r'f^{-1}(f(x))=x,\qquad f(f^{-1}(y))=y', 39)
        reciprocal_label = self.words('Inverse numérique : multiplier donne un.', 30)
        reciprocal_check = self.formula(r'f(x)\,h(x)=1\qquad\left(x\ne\frac53\right)', 43)
        self.new_page('Deux contrôles différents', inverse_label,
                      inverse_check, reciprocal_label, reciprocal_check, gap=0.55)
        self.explain(
            'Le contrôle de la réciproque est une composition. '
            'Appliquer f puis sa réciproque redonne x; appliquer '
            'la réciproque puis f redonne y. Ici les deux '
            'identités sont valables pour tous les réels.',
            inverse_label, inverse_check, hold=2,
        )
        self.explain(
            'Le contrôle de l’inverse numérique est un produit. '
            'Pour une entrée où f n’est pas nul, la valeur f de '
            'x multipliée par h de x vaut un. Retrouver l’entrée '
            'par composition et obtenir un par multiplication '
            'sont deux propriétés distinctes.',
            reciprocal_label, reciprocal_check, hold=2,
        )

    def _existence_conditions(self):
        bijection = self.formula(r'f:A\to B\ \text{bijective}\quad\Longrightarrow\quad f^{-1}:B\to A', 37)
        meaning = self.words('Chaque sortie de B provient d’une seule entrée de A.', 28)
        reciprocal = self.formula(r'h(x)=\frac1{f(x)}\quad\text{là où }f(x)\ne0', 43)
        note = self.words('Bijection et non-nullité : deux conditions différentes.', 28)
        self.new_page('Vérifier que l’objet demandé existe', bijection,
                      meaning, reciprocal, note, gap=0.56)
        self.explain(
            'Pour une fonction générale de A vers B, une '
            'réciproque définie sur tout B exige que chaque '
            'sortie annoncée soit atteinte par une unique '
            'entrée. C’est la condition de bijection. Choisir '
            'les ensembles fait donc partie de la définition.',
            bijection, meaning, hold=2,
        )
        self.explain(
            'La fonction un sur f exige seulement, à chaque '
            'entrée retenue, que f soit définie et non nulle. '
            'Elle ne demande pas de pouvoir retrouver une '
            'entrée unique à partir d’une sortie. Les deux '
            'conditions ne sont pas interchangeables.',
            reciprocal, note, hold=2,
        )

    def _self_check(self):
        function = self.formula(r'f:\mathbb R\to\mathbb R,\qquad f(x)=3x-7', 43)
        questions = VGroup(
            self.words('Trouver f⁻¹ et vérifier les deux compositions.', 30),
            self.words('Écrire aussi 1/f et préciser son domaine.', 30),
        ).arrange(DOWN, buff=0.65)
        self.new_page('À vous : l’exercice 3.5 A du cahier', function,
                      questions, gap=0.8)
        self.explain(
            'Le cahier demande la réciproque de trois x moins '
            'sept et la vérification des deux compositions. '
            'Faites ce calcul, puis ajoutez notre comparaison : '
            'quelle serait la fonction un sur f, et quelle '
            'entrée faudrait-il exclure de son domaine ?',
            function, questions, hold=2, pause_after=6,
        )

    def _self_check_answer(self):
        inverse = self.formula(r'f^{-1}(y)=\frac{y+7}{3},\qquad y\in\mathbb R', 44, GREEN_D)
        reciprocal = self.formula(r'\frac1{f(x)}=\frac1{3x-7},\qquad x\ne\frac73', 44)
        check = self.formula(r'f(5)=8,\qquad f^{-1}(8)=5,\qquad\frac1{f(5)}=\frac18', 40)
        self.new_page('Réponse : deux règles, deux domaines', inverse,
                      reciprocal, check, gap=0.85)
        self.explain(
            'Pour la réciproque, on ajoute sept à la sortie '
            'puis on divise par trois. Toutes les sorties '
            'réelles sont admissibles. Pour un sur f, on '
            'garde trois x moins sept au dénominateur; il '
            'faut donc exclure sept tiers.', inverse, reciprocal, hold=2,
        )
        self.explain(
            'Un contrôle concret donne f de cinq égal à huit. '
            'La réciproque de huit doit donc être cinq. '
            'L’inverse numérique de f de cinq est, lui, '
            'un huitième. Les flèches et le calcul racontent '
            'la même distinction.', check, hold=2,
        )

    def _self_check_compositions(self):
        first = self.formula(r'f^{-1}(f(x))=\frac{(3x-7)+7}{3}=x', 43)
        second = self.formula(r'f(f^{-1}(y))=3\frac{y+7}{3}-7=y', 43)
        domain = self.formula(r'x\in\mathbb R,\qquad y\in\mathbb R', 40, BLUE_D)
        self.new_page('Vérifier dans les deux sens', first, second, domain, gap=0.8)
        self.explain(
            'Vérifions maintenant les deux compositions '
            'symboliques demandées. Dans la première, les '
            'deux sept se compensent et la division par '
            'trois redonne x. Dans la seconde, multiplier '
            'par trois puis retirer sept redonne y. '
            'Aucun dénominateur variable ne crée ici '
            'de restriction supplémentaire.', first, second, domain, hold=2,
        )

    def _takeaway(self):
        inverse = self.formula(r'f^{-1}:\ \text{retrouver une entrée}', 43, BLUE_D)
        reciprocal = self.formula(r'\frac1f:\ \text{inverser numériquement une valeur}', 39)
        checks = self.words('Composition et domaine ; produit et non-nullité.', 30)
        self.new_page('À retenir : identifier l’opération', inverse,
                      reciprocal, checks, gap=0.85)
        self.explain(
            'Avant de calculer, identifiez l’opération. La '
            'réciproque retrouve une entrée et se vérifie '
            'par composition, entre les domaines annoncés. '
            'L’inverse numérique transforme une valeur '
            'non nulle en son inverse et se vérifie par '
            'multiplication. Le symbole moins un ne suffit '
            'pas à confondre ces deux objets.', inverse, reciprocal, checks, hold=2,
        )
