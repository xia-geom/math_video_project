"""Régressions ciblées : calculs indépendants, hypothèses et texte corrigé.

Ces contrôles ne prétendent pas analyser automatiquement toute la mathématique du livre.
"""
from __future__ import annotations

import itertools
import math
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def chapter(n: int) -> str:
    return (ROOT / f'sources/manual/chapters/ch{n:02}.tex').read_text()


class MathematicalRegressions(unittest.TestCase):
    def test_banane_by_enumeration(self):
        self.assertEqual(len(set(itertools.permutations('BANANE'))), 180)
        self.assertNotIn(r'\frac{6!}{3!2!}=60', chapter(7))
        self.assertEqual(chapter(7).count(r'\frac{6!}{2!2!}=180'), 2)

    def test_logarithm_bounds(self):
        self.assertLess(2**2, 7)
        self.assertLess(7, 2**3)
        self.assertLess(2, math.log2(7))
        self.assertLess(math.log2(7), 3)
        self.assertNotIn('$2^3<7<2^4$', chapter(6))

    def test_compound_growth_exact_rational(self):
        amount = F(5000) * F(1042, 1000)**8
        self.assertEqual(round(float(amount), 2), 6948.83)
        self.assertIn('6948{,}83', chapter(6))
        self.assertNotIn('6948{,}57', chapter(6))

    def test_trigonometric_rounding(self):
        radians = math.radians
        side = math.sqrt(7**2 + 11**2 - 2 * 7 * 11 * math.cos(radians(54)))
        ac = 120 * math.sin(radians(63)) / math.sin(radians(69))
        self.assertEqual(round(side, 2), 8.92)
        self.assertEqual(round(ac, 2), 114.53)
        self.assertEqual(round(ac * math.sin(radians(48)), 2), 85.11)
        self.assertIn('8{,}92', chapter(15))
        self.assertIn('114{,}53', chapter(15))

    def test_probability_tree_paths(self):
        paths = [F(3, 5)*F(2, 4), F(3, 5)*F(2, 4), F(2, 5)*F(3, 4), F(2, 5)*F(1, 4)]
        self.assertEqual(paths, [F(3, 10)]*3 + [F(1, 10)])
        self.assertEqual(sum(paths), 1)
        self.assertIn('RR:3/10', chapter(8))
        self.assertIn('BB:1/10', chapter(8))

    def test_negative_frequency_period(self):
        for b in [-4.0, -0.5, 0.5, 3.0]:
            period = 2*math.pi/abs(b)
            self.assertGreater(period, 0)
            for x in [-1.7, 0.0, 2.1]:
                self.assertAlmostEqual(math.sin(b*(x+period)), math.sin(b*x))
        self.assertNotIn('BT=2\\pi,', chapter(16))
        self.assertIn('|B|T=2\\pi', chapter(16))

    def test_dot_product_and_projection(self):
        u, v = (F(4), F(3)), (F(1), F(1))
        uv = sum(x*y for x, y in zip(u, v))
        vv = sum(x*x for x in v)
        projection = tuple(uv/vv*x for x in v)
        self.assertEqual(projection, (F(7, 2), F(7, 2)))
        self.assertEqual(sum((x-p)*y for x, p, y in zip(u, projection, v)), 0)
        self.assertNotIn('\norm{', chapter(9))  # newline + damaged "orm{"

    def test_rational_inverse_both_directions(self):
        def f(x):
            return (2*x+1)/(x-3)

        def inv(y):
            return (3*y+1)/(y-2)
        for x in map(F, [-7, -1, 0, 1, 2, 4, 9]):
            self.assertEqual(inv(f(x)), x)
        for y in map(F, [-7, -1, 0, 1, 3, 4, 9]):
            self.assertEqual(f(inv(y)), y)
        self.assertIn('chaque élément du codomaine', chapter(3))

    def test_piecewise_graph(self):
        def h(x):
            return -x-1 if x < 0 else x*x-1 if x <= 2 else F(3)
        cases = {-4:3, -2:1, -1:0, 0:-1, 1:0, 2:3, 3:3}
        for x, y in cases.items():
            self.assertEqual(h(F(x)), y)
        self.assertIn('coordinates {(0,-1) (2,3)}', chapter(3))
        self.assertIn('\\{-4\\}\\cup[2,+\\infty[', chapter(3))

    def test_piecewise_linear_level(self):
        self.assertEqual(F(3, 2)*(F(-5, 3)+3), 2)
        self.assertEqual(1-2*F(-1, 2), 2)
        self.assertEqual(F(4)-2, 2)

    def test_transformations_not_accidentally_identical(self):
        def f(x):
            return abs(x-1)
        self.assertNotEqual(f(2*1), 2*f(1))
        self.assertEqual(f(2*F(1, 2)), 0)
        answers = (ROOT / 'sources/workbook/backmatter.tex').read_text()
        self.assertIn('zéro en \\(1/2\\)', answers)

    def test_mean_is_arithmetic(self):
        self.assertNotIn('moyenne géométrique du modèle', chapter(17))
        self.assertIn('moyenne arithmétique', chapter(17))
        self.assertEqual(F(28+4, 2), 16)

    def test_gauss_family(self):
        for t in map(F, [-2, 0, 1, 7]):
            x, y, z = 4-t, t-1, t
            self.assertEqual(x+2*y-z, 2)
            self.assertEqual(2*x-y+3*z, 9)
            self.assertEqual(3*x+y+2*z, 11)
        self.assertIn('En l’absence de contradiction', chapter(12))

    def test_integer_optimization_not_naive_rounding(self):
        pts = [(x,y) for x in range(5) for y in range(5) if 2*x+y<=8 and x+2*y<=8]
        self.assertEqual(max(30*x+40*y for x,y in pts), 180)
        self.assertIn('arrondir le sommet continu ne suffit pas', chapter(13))


if __name__ == '__main__':
    unittest.main()
