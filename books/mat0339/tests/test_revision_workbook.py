"""Contrôles indépendants des calculs et des consignes révisés en octobre."""
import importlib.util
import itertools
import math
import unittest
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = (ROOT/'sources/workbook/backmatter.tex').read_text()


class WorkbookRevision(unittest.TestCase):
    def test_mathematique_multinomial(self):
        counts = Counter('MATHEMATIQUE')
        self.assertEqual(len('MATHEMATIQUE'), 12)
        self.assertEqual({c for c,n in counts.items() if n == 2}, set('MATE'))
        total = math.factorial(sum(counts.values())) // math.prod(math.factorial(n) for n in counts.values())
        self.assertEqual(total, 29937600)
        self.assertIn(r'29\,937\,600', ANSWERS)
        identifiers = list(itertools.product(range(8), repeat=4))
        distinct = sum(len(set(code)) == 4 for code in identifiers)
        self.assertEqual((distinct, len(identifiers)), (1680, 4096))
        self.assertIn(r'Sans répétition $8\cdot7\cdot6\cdot5=1680$', ANSWERS)
        self.assertIn(r'avec répétition $8^4=4096$', ANSWERS)
        question = (ROOT/'sources/workbook/chapters/ch07.tex').read_text()
        self.assertIn('si les répétitions sont interdites? Si elles sont permises?', question)

    def test_estimation_bounds_and_rounding(self):
        q=F('19.8')*F('4.03')/F('.51')
        self.assertEqual(q, F(13299,85))
        self.assertEqual(F('19.5')*4/F('.52'),150)
        self.assertEqual(20*F('4.08')/F('.51'),160)
        self.assertLess(150,q)
        self.assertLess(q,160)
        self.assertEqual(round(float(q),2),156.46)
        self.assertIn('150<q<160', ANSWERS)
        self.assertIn('156{,}46', ANSWERS)

    def test_inequality_equivalence_including_negative_denominator(self):
        for x in map(F,[-10,-6,-5,-4,-3,F(-3,2),0,7]):
            original=(x-1)/(x+2)<=2
            reduced=(-x-5)/(x+2)<=0
            self.assertEqual(original,reduced)
            self.assertEqual(original,x<=-5 or x>-2)
        self.assertLessEqual((F(-6)-1)/(F(-6)+2),2)
        self.assertGreater(-F(-6)-5,0)
        self.assertNotIn(r'$(x-1)-2(x+2)\le0$',ANSWERS)
        self.assertIn(r'\dfrac{-x-5}{x+2}\le0',ANSWERS)

    def test_domain_and_solution_sign_are_separate(self):
        # -1 is in the radical's domain but cannot equal a nonnegative root.
        self.assertGreaterEqual(2*(-1)+3,0)
        self.assertNotEqual(math.sqrt(2*(-1)+3),-1)
        self.assertEqual(math.sqrt(2*3+3),3)
        self.assertIn('Expressions définies : $x\\ge-3/2$',ANSWERS)
        self.assertIn('Condition nécessaire pour une solution : $x\\ge0$',ANSWERS)

    def test_trigonometry_round_after_final_calculation(self):
        def sin(d):
            return math.sin(math.radians(d))
        for value,expected,printed in [
            (8*sin(70)/sin(35),13.11,'13{,}11'),
            (8*sin(75)/sin(35),13.47,'13{,}47'),
            (120*sin(48)/sin(65),98.40,'98{,}40')]:
            self.assertEqual(round(value,2),expected)
            self.assertIn(printed,ANSWERS)
        b=math.degrees(math.asin(10*sin(40)/7))
        self.assertEqual(round(b,2),66.67)
        self.assertEqual(round(180-b,2),113.33)
        for angle in [b,180-b]:
            self.assertGreater(180-40-angle,0)
            self.assertAlmostEqual(sin(angle)/10,sin(40)/7)
        self.assertIn('66{,}67',ANSWERS)
        self.assertIn('113{,}33',ANSWERS)

    def test_four_supplied_triangle_configurations(self):
        chapter=(ROOT/'sources/workbook/chapters/ch15.tex').read_text()
        self.assertEqual(chapter.count(r'\begin{tikzpicture}'),4)
        self.assertTrue(5+7>8)
        self.assertEqual(F(5**2+7**2-8**2,2*5*7),F(1,7))
        self.assertEqual(7**2+9**2-2*7*9*F(1,2),67)
        self.assertEqual(180-35-70,75)
        self.assertIn('sin40^\\circ/7',ANSWERS)
        self.assertNotIn('Équations selon la classification',ANSWERS)

    def test_additional_answer_corrections(self):
        self.assertEqual(math.dist((5,2),(2,6)),5)
        self.assertIn(r'$BC=5$',ANSWERS)
        for x in [0,math.pi/2,2*math.pi]:
            self.assertAlmostEqual(math.sin(x)+math.cos(x),1)
        self.assertIn(r'solutions $x=0,\pi/2,2\pi$',ANSWERS)
        self.assertEqual(round(math.log(2)/math.log(1.042),2),16.85)
        self.assertIn('16{,}85',ANSWERS)
        # (1,2)+t(2,-1) intersects x+y=5 at t=2.
        parameter = F(5-1-2, 2-1)
        intersection = (1+2*parameter, 2-parameter)
        self.assertEqual(intersection, (5, 0))
        self.assertEqual(sum(intersection), 5)
        self.assertIn('$(5,0)$', ANSWERS)
        def h(t):
            return 12+7*math.sin(math.pi*(t-3)/4)
        self.assertAlmostEqual(h(1),5)
        self.assertAlmostEqual(h(3),12)
        self.assertAlmostEqual(h(5),19)

    def test_edition_drives_filenames_and_epoch(self):
        spec=importlib.util.spec_from_file_location('book_build',ROOT/'scripts/build.py')
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertEqual(mod.EDITION,'2026-10-17')
        for target in mod.TARGETS.values():
            self.assertTrue(target[2].endswith(mod.EDITION))
        for area in ['manual','workbook']:
            self.assertIn(r'\input{../edition.tex}',(ROOT/f'sources/{area}/preamble.tex').read_text())
            self.assertIn(r'\EditionDate{}',(ROOT/f'sources/{area}/frontmatter.tex').read_text())


if __name__ == '__main__':
    unittest.main()
