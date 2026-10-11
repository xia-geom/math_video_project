"""Régressions des figures et modèles révisés le 10 octobre 2026.

Les coordonnées et segments sont lus dans le TEX actif, puis contrôlés par
des calculs indépendants. Ces tests ne remplacent pas l'inspection du rendu.
"""
from __future__ import annotations

import ast
import itertools
import math
from pathlib import Path
import re
import unittest
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[1]


def section(chapter: int, number: int) -> str:
    text = (ROOT / f"sources/manual/chapters/ch{chapter:02}.tex").read_text()
    return text.split(f"\\label{{manual:section:{chapter:02}.{number:02}}}", 1)[1].split(
        "\\section{", 1
    )[0]


def arithmetic(expression: str, **variables):
    """Read the small arithmetic expressions used by these TikZ coordinates."""
    expression = expression.strip("{}").replace("\\", "")

    def visit(node):
        if isinstance(node, ast.Constant):
            return F(str(node.value))
        if isinstance(node, ast.Name):
            return variables[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -visit(node.operand)
        if isinstance(node, ast.BinOp):
            left, right = visit(node.left), visit(node.right)
            operations = {ast.Add: lambda: left + right, ast.Sub: lambda: left - right,
                          ast.Mult: lambda: left * right, ast.Div: lambda: left / right}
            return operations[type(node.op)]()
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == "sqrt" and len(node.args) == 1:
                return math.sqrt(visit(node.args[0]))
        raise ValueError(f"Unsupported coordinate expression: {expression}")

    return visit(ast.parse(expression, mode="eval").body)


POINT = r"\((\{[^{}]*\}|[^(),{}]+),(\{[^{}]*\}|[^(),{}]+)\)"


def points(text: str, **variables):
    return [tuple(arithmetic(value, **variables) for value in pair)
            for pair in re.findall(POINT, text)]


def vertices(constraints):
    """Intersections satisfying every half-plane a*x+b*y <= c."""
    result = set()
    for (a, b, c), (d, e, f) in itertools.combinations(constraints, 2):
        determinant = a * e - b * d
        if not determinant:
            continue
        x, y = (c * e - b * f) / determinant, (a * f - c * d) / determinant
        if all(p * x + q * y <= r for p, q, r in constraints):
            result.add((x, y))
    return result


class RevisedManualGeometry(unittest.TestCase):
    def test_aud06_workshop_region_and_objective(self):
        text = section(13, 6)
        constraints = [tuple(map(F, row)) for row in
                       [(3, 1, 18), (1, 1, 8), (-1, 0, 0), (0, -1, 0)]]
        feasible = vertices(constraints)
        fill = re.search(r"fill=mistteal[^\n]+coordinates \{([^\n]+)\} -- cycle", text)
        self.assertIsNotNone(fill)
        self.assertEqual(set(points(fill.group(1))), feasible)
        values = {point: 70 * point[0] + 40 * point[1] for point in feasible}
        self.assertEqual(values, {(F(0), F(0)): 0, (F(6), F(0)): 420,
                                  (F(5), F(3)): 470, (F(0), F(8)): 320})
        level = re.search(r"dash dot,domain=0:7\] \{([^}]+)\}", text).group(1)
        for x in map(F, [0, 5, 6]):
            y = arithmetic(level, x=x)
            self.assertEqual(70 * x + 40 * y, max(values.values()))
        self.assertIn("$470$ dollars, pour $5$ tables et $3$ étagères", text)

    def test_aud07_polygon_and_optimum(self):
        text = section(13, 5)
        constraints = [(F(-1), F(0), F(0)), (F(0), F(-1), F(0)),
                       (F(3), F(1), F(12)), (F(9), F(10), F(264, 5)),
                       (F(-1), F(2), F(36, 5))]
        fill = re.search(r"\\fill\[mistteal\] ([^\n]+)--cycle", text).group(1)
        drawn = set(points(fill))
        self.assertEqual(drawn, vertices(constraints))
        values = {point: 3 * point[0] + 2 * point[1] for point in drawn}
        self.assertEqual(max(values, key=values.get), (F(16, 5), F(12, 5)))
        self.assertEqual(max(values.values()), F(72, 5))
        marked = re.search(r"\\fill\[ink\] ([^\n]+) circle", text).group(1)
        self.assertEqual(points(marked), [(F(16, 5), F(12, 5))])
        self.assertIn(r"9x+10y\le\frac{264}{5}", text)
        self.assertIn(r"-x+2y\le\frac{36}{5}", text)

    def test_aud07_level_segments_share_the_objective_normal(self):
        text = section(13, 5)
        segment = re.search(r"\\draw\[slate!70,thick,dashed\] ([^\n]+);", text).group(1)
        levels = re.search(r"\\foreach \\c in \{([^}]+)\}", text).group(1)
        for level in map(F, levels.split(",")):
            first, last = points(segment, c=level)
            for x, y in (first, last):
                self.assertEqual(3 * x + 2 * y, level)
            self.assertEqual((last[1] - first[1]) / (last[0] - first[0]), F(-3, 2))
        optimum = re.search(r"\\draw\[terracotta,very thick,dash dot\] ([^\n]+);", text).group(1)
        for x, y in points(optimum):
            self.assertEqual(3 * x + 2 * y, F(72, 5))

    def test_aud15_both_grid_families_are_transformed(self):
        text = section(11, 6)
        pictures = text.split(r"\begin{tikzpicture}[scale=0.48]")[1:3]

        def segment(picture, variable, value):
            line = next(line for line in picture.splitlines()
                        if line.strip().startswith("\\foreach \\" + variable + " "))
            return points(line, **{variable: value})

        for variable in ("u", "v"):
            for value in map(F, range(-2, 3)):
                original = segment(pictures[0], variable, value)
                transformed = segment(pictures[1], variable, value)
                self.assertEqual(transformed, [(2 * u + v, v) for u, v in original])
                for x, y in transformed:
                    self.assertEqual(x - y if variable == "u" else y,
                                     2 * value if variable == "u" else value)
        self.assertIn(r"(0,0)--(2,0)", pictures[1])
        self.assertIn(r"(0,0)--(1,1)", pictures[1])

    def test_aud09_right_triangle_geometry_and_angle_centres(self):
        text = section(14, 6)
        figure = text.split(r"\begin{tikzpicture}[scale=1.9]", 1)[1].split(r"\end{tikzpicture}", 1)[0]
        c = points(re.search(r"\\coordinate \(C\) at ([^;]+);", figure).group(1))[0]
        h = points(re.search(r"\\coordinate \(H\) at ([^;]+);", figure).group(1))[0]
        self.assertEqual(h, (1, 0))
        self.assertAlmostEqual(math.dist((0, 0), c), 2)
        self.assertAlmostEqual(math.dist(h, c), math.sqrt(3))
        self.assertAlmostEqual(math.degrees(math.atan2(c[1], c[0])), 60)
        self.assertAlmostEqual(math.degrees(math.atan2(c[0], c[1])), 30)
        self.assertIn("arc[start angle=240,end angle=270,radius=0.4]", figure)
        self.assertIn(r"{sqrt(3)+0.4*sin(240)}", figure)
        self.assertIn("(0.87,0)--(0.87,0.13)--(1,0.13)", figure)

    def test_ssa_marked_intersections_lie_on_circle_and_ray(self):
        text = section(15, 4)
        candidates = []
        for name in ("C1", "C2"):
            expression = re.search(rf"\\coordinate \({name}\) at ([^;]+);", text).group(1)
            x, y = points(expression)[0]
            candidates.append((x, y))
            self.assertGreater(x, 0)
            self.assertGreater(y, 0)
            self.assertAlmostEqual(y / x, math.tan(math.pi / 6))
            self.assertAlmostEqual((x - 5) ** 2 + y ** 2, 3 ** 2)
        self.assertNotEqual(*candidates)
        self.assertIn(r"(B) circle (3)", text)


class RevisedWaveModels(unittest.TestCase):
    def test_aud18_temporal_spatial_periods_and_constant_phase(self):
        text = section(17, 5)
        for amplitude, k, omega in [(2, math.pi, 2 * math.pi),
                                    (3, 2 * math.pi / 5, 4 * math.pi)]:
            wavelength, period, speed = 2 * math.pi / k, 2 * math.pi / omega, omega / k
            self.assertAlmostEqual(speed, wavelength / period)
            for x, t in [(-2.3, 0), (0.3, 0.7), (5.1, 2)]:
                wave = lambda x, t: amplitude * math.sin(k * x - omega * t)
                self.assertAlmostEqual(wave(x + wavelength, t), wave(x, t))
                self.assertAlmostEqual(wave(x, t + period), wave(x, t))
                self.assertAlmostEqual(wave(x + speed * 0.13, t + 0.13), wave(x, t))
        self.assertAlmostEqual(wavelength, 5)
        self.assertAlmostEqual(period, 0.5)
        self.assertAlmostEqual(speed, 10)
        self.assertIn(r"\lambda=\frac{2\pi}{k}", text)
        self.assertIn(r"T=\frac{2\pi}{\omega}", text)
        self.assertIn(r"k\Delta x-\omega\Delta t=0", text)
        self.assertIn(r"\frac{\omega}{k}=\frac{\lambda}{T}", text)
        self.assertIn("radians par mètre", text)
        self.assertIn("radians par seconde", text)
        self.assertIn(r"y(x,t)=2\sin(\pi x-2\pi t)", text)

    def test_angular_velocity_assumes_uniform_anticlockwise_rotation(self):
        text = section(17, 1)
        self.assertLess(text.index("mouvement circulaire uniforme"), text.index(r"|\omega|="))
        self.assertIn("à vitesse constante dans le sens antihoraire", text)
        self.assertAlmostEqual((2 * math.pi / 8) * 3, 3 * math.pi / 4)
        self.assertIn(r"\theta_0+3\pi/4", text)


if __name__ == "__main__":
    unittest.main()
