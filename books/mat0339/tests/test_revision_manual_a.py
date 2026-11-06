"""Contrôles mathématiques ciblés de la révision des chapitres 1 à 9.

Ces tests ne contrôlent ni les collisions graphiques ni toutes les affirmations.
"""
import math
import re
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def chapter(number):
    return (ROOT / f'sources/manual/chapters/ch{number:02}.tex').read_text()


class ManualRevisionA(unittest.TestCase):
    def test_radical_domain_is_distinct_from_solution_sign(self):
        # 0 is in the domain of sqrt(x+1)=x-1, but is not a solution.
        self.assertGreaterEqual(0 + 1, 0)
        self.assertNotEqual(math.sqrt(0 + 1), 0 - 1)
        self.assertEqual(math.sqrt(3 + 1), 3 - 1)
        # The second example has the same distinction at candidate -1.
        self.assertGreaterEqual(2 * (-1) + 3, 0)
        self.assertNotEqual(math.sqrt(2 * (-1) + 3), -1)
        self.assertEqual(math.sqrt(2 * 3 + 3), 3)
        text = chapter(2)
        self.assertIn('expressions sont définies pour $x\\ge-1$', text)
        self.assertIn('expressions sont définies pour $x\\ge-3/2$', text)
        self.assertNotIn('Le domaine impose $x\\ge1$', text)

    def test_cancelled_factor_can_leave_a_pole(self):
        # Both original expressions exclude zero; their reduced limits differ.
        for denominator in (10, 100, 1000):
            for sign in (-1, 1):
                x = F(sign, denominator)
                self.assertEqual(x**2 / x, x)
                self.assertEqual(x / x**2, 1 / x)
                self.assertLessEqual(abs(x**2 / x), F(1, 10))
                self.assertGreaterEqual(abs(x / x**2), 10)
        text = chapter(5)
        self.assertIn('$x^2/x=x$, $x\\ne0$', text)
        self.assertIn('$x/x^2=1/x$, $x\\ne0$', text)
        self.assertIn('entièrement réduit', text)
        self.assertNotIn('un facteur simplifiable, qui produit un trou', text)

    def test_hole_height_and_remaining_pole(self):
        def reduced(x):
            return (x + 2) / (x + 1)
        self.assertEqual(reduced(F(2)), F(4, 3))
        for x in map(F, (-3, 0, 1, 3)):
            self.assertEqual((x*x - 4)/(x*x - x - 2), reduced(x))
        self.assertNotEqual(F(-1) + 2, 0)
        self.assertEqual(F(-1) + 1, 0)

    def test_probability_table_matches_model_and_all_margins(self):
        text = chapter(8)
        rows = {}
        for name in ('Malades', 'Non malades', 'Total'):
            match = re.search(rf'^{name} & (.+)\\\\$', text, re.M)
            self.assertIsNotNone(match, name)
            values = re.findall(r'\$([\d\\,]+)\$', match.group(1))
            rows[name] = tuple(int(value.replace(r'\,', '')) for value in values)
        self.assertEqual(rows['Malades'], (190, 10, 200))
        self.assertEqual(rows['Non malades'], (392, 9408, 9800))
        self.assertEqual(rows['Total'], (582, 9418, 10000))
        for row in rows.values():
            self.assertEqual(row[0] + row[1], row[2])
        for column in range(3):
            self.assertEqual(rows['Malades'][column] + rows['Non malades'][column],
                             rows['Total'][column])
        prior, sensitivity, false_positive = F(2, 100), F(95, 100), F(4, 100)
        posterior = prior*sensitivity / (prior*sensitivity + (1-prior)*false_positive)
        self.assertEqual(posterior, F(rows['Malades'][0], rows['Total'][0]))
        self.assertNotEqual(posterior, sensitivity)

    def test_future_doubling_and_half_life_conditions(self):
        for base in (1.03, 1.5, 2.0):
            time = math.log(2)/math.log(base)
            self.assertGreater(time, 0)
            self.assertAlmostEqual(7 * base**time, 14)
        for base in (0.5, 0.85, 0.99):
            doubling = math.log(2)/math.log(base)
            half_life = math.log(0.5)/math.log(base)
            self.assertLess(doubling, 0)
            self.assertGreater(half_life, 0)
            self.assertAlmostEqual(7 * base**half_life, 3.5)
        self.assertEqual(math.log(1), 0)
        self.assertEqual(0 * 2**5, 0)
        text = chapter(6)
        self.assertIn('avec $Q_0>0$ et $b>1$', text)
        self.assertIn('avec $b>0$ et $Q_0\\ne0$', text)
        self.assertIn('Si $Q_0\\le0$', text)

    def test_logarithmic_figure_uses_the_same_model(self):
        for time in (0, 1, 2.5, 4.5):
            quantity = 0.55 * 1.65**time
            self.assertAlmostEqual(math.log(quantity), math.log(0.55)+time*math.log(1.65))
        self.assertLess(math.log(0.55), 0)
        text = chapter(6)
        self.assertIn(r'plot(\x,{0.55*pow(1.65,\x)})', text)
        self.assertIn(r'plot(\x,{ln(0.55)+\x*ln(1.65)})', text)

    def test_translated_parabola_matches_its_printed_formula(self):
        for x in map(F, (-5, -3, -1, 0, 2)):
            self.assertEqual(x*x + 6*x + 5, (x+3)**2 - 4)
        self.assertEqual((F(-3)+3)**2 - 4, -4)
        text = chapter(4)
        self.assertIn(r'plot(\x,{\x*\x})', text)
        self.assertIn(r'plot(\x,{(\x+3)*(\x+3)-4})', text)
        self.assertNotIn(r'0.65*(\x+3)*(\x+3)-4', text)

    def test_signed_projection_is_not_a_length(self):
        u, v = (-3, 4), (2, 0)
        dot = sum(a*b for a, b in zip(u, v))
        component = F(dot, 2)
        projection = (component, F(0))
        self.assertEqual(component, -3)
        self.assertEqual(sum(x*x for x in projection), 9)
        self.assertLess(component, 0)
        self.assertIn(r'longueur $|\mathbf u\cdot\mathbf e|$', chapter(9))


if __name__ == '__main__':
    unittest.main()
