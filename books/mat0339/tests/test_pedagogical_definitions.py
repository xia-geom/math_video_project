"""Prérequis explicites et exemples de la révision pédagogique du 6 novembre."""

import itertools
import math
import unittest
from collections import Counter
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def manual(number):
    return (ROOT / f"sources/manual/chapters/ch{number:02}.tex").read_text()


class PedagogicalDefinitions(unittest.TestCase):
    def test_real_coefficients_are_explicit_before_use(self):
        polynomial = manual(2)
        self.assertLess(polynomial.index(r"\emph{monôme en $x$}"),
                        polynomial.index(r"\begin{definition}{Polynôme}"))
        self.assertIn(r"a_0,\ldots,a_n\in\R", polynomial)
        quadratic = manual(4).split(r"\begin{definition}{Fonction quadratique}", 1)[1]
        quadratic = quadratic.split(r"\end{definition}", 1)[0]
        self.assertIn(r"a,b,c\in\R", quadratic)
        self.assertIn(r"a\neq0", quadratic)

    def test_rational_power_examples_use_the_positive_root(self):
        # Both descriptions must satisfy y^q=b^p, including a negative exponent.
        for numerator, denominator, value in ((2, 3, Fraction(4)),
                                               (4, 6, Fraction(4)),
                                               (-2, 3, Fraction(1, 4))):
            self.assertGreater(value, 0)
            self.assertEqual(value**denominator, Fraction(8)**numerator)
        self.assertAlmostEqual(math.sqrt(0.88)**2, 0.88)
        text = manual(6)
        self.assertLess(text.index(r"b^{p/q}=\sqrt[q]{b^p}"),
                        text.index(r"\begin{definition}{Fonction exponentielle}"))
        self.assertIn("existence et d'unicité", text)

    def test_irrational_power_approximations_respect_both_monotonicities(self):
        exponent = math.sqrt(2)
        self.assertLess(1.4142, exponent)
        self.assertLess(exponent, 1.4143)
        for base in (2, 0.88):
            errors = []
            for digits in range(1, 6):
                lower = math.floor(exponent * 10**digits) / 10**digits
                upper = lower + 10**(-digits)
                bounds = sorted((base**lower, base**upper))
                self.assertLessEqual(bounds[0], base**exponent)
                self.assertLessEqual(base**exponent, bounds[1])
                errors.append(bounds[1] - bounds[0])
            self.assertTrue(all(after < before for before, after in zip(errors, errors[1:])))

    def test_multinomial_quotient_counts_equal_sized_groups(self):
        for counts in ((2, 2, 1), (3, 1), (0, 0), (0, 2, 1)):
            letters = tuple(letter for letter, count in enumerate(counts)
                            for _ in range(count))
            groups = Counter(itertools.permutations(letters))
            group_size = math.prod(math.factorial(count) for count in counts)
            self.assertEqual(set(groups.values()), {group_size})
            quotient = Fraction(math.factorial(len(letters)), group_size)
            self.assertEqual(quotient.denominator, 1)
            self.assertEqual(quotient, len(groups))

    def test_arrangement_and_combination_integrality_including_empty_selection(self):
        for n in range(8):
            for k in range(n + 1):
                arrangements = list(itertools.permutations(range(n), k))
                groups = Counter(frozenset(selection) for selection in arrangements)
                self.assertEqual(set(groups.values()), {math.factorial(k)})
                self.assertEqual(Fraction(math.factorial(n), math.factorial(n - k)),
                                 len(arrangements))
                self.assertEqual(Fraction(len(arrangements), math.factorial(k)),
                                 math.comb(n, k))
                self.assertEqual(len(groups), math.comb(n, k))

    def test_unit_circle_precedes_dot_product_and_explains_the_workbook_angle(self):
        text = manual(9)
        self.assertLess(text.index(r"\emph{cercle unité}"),
                        text.index(r"\begin{definition}{Produit scalaire}"))
        for angle, abscissa in ((0, 1), (60, 0.5), (90, 0), (120, -0.5), (180, -1)):
            self.assertAlmostEqual(math.cos(math.radians(angle)), abscissa)
        u, v = (2, 1), (-1, 3)
        cosine = sum(a * b for a, b in zip(u, v)) / (math.hypot(*u) * math.hypot(*v))
        angle = math.degrees(math.acos(cosine))
        self.assertGreater(cosine, 0)
        self.assertLess(angle, 90)
        self.assertAlmostEqual(round(angle, 2), 81.87)


if __name__ == "__main__":
    unittest.main()
