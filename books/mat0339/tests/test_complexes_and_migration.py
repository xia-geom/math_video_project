"""Calculs indépendants et conservation des identités lors du passage à l'annexe."""
from __future__ import annotations

import cmath
import copy
import hashlib
import importlib.util
import json
import math
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUAL = (ROOT / 'sources/manual/chapters/ch17.tex').read_text()
QUESTIONS = (ROOT / 'sources/workbook/chapters/ch17.tex').read_text()
ANSWERS = (ROOT / 'sources/workbook/backmatter.tex').read_text().split(
    r'\chapter*{Chapitre 17 -- Nombres complexes}', 1)[1].split(r'\chapter*{Annexe A --', 1)[0]
spec = importlib.util.spec_from_file_location('video_map_migration', ROOT / 'scripts/video_map.py')
video_map = importlib.util.module_from_spec(spec)
spec.loader.exec_module(video_map)


class ComplexCalculations(unittest.TestCase):
    def assertComplexAlmostEqual(self, actual, expected):
        self.assertAlmostEqual(actual.real, expected.real, places=10)
        self.assertAlmostEqual(actual.imag, expected.imag, places=10)

    def test_components_arithmetic_conjugation_and_cycle(self):
        z, w = 2 + 3j, 1 - 2j
        self.assertEqual((z+w, z*w, z.conjugate()), (3+1j, 8-1j, 2-3j))
        self.assertEqual((2*3-1)+(-5+3)*1j, 5-2j)
        self.assertEqual((3j)**2, -9)
        self.assertEqual((-3j)**2, -9)
        self.assertEqual(math.prod([1j]*2026), -1)
        for a, b in [(3,-2), (-4,0), (0,5)]:
            z = complex(a,b)
            self.assertEqual(z+z.conjugate(), 2*a)
            self.assertEqual(z-z.conjugate(), 2j*b)
        self.assertIn('zw=2-4i+3i-6i^2=8-i', MANUAL)
        self.assertIn('i^{4\\cdot506+2}=-1', ANSWERS)

    def test_quotient_and_inverse_exact_rational_components(self):
        # Solve (x+yi)(1-2i)=2+3i by a real 2x2 system.
        x, y = F(-4,5), F(7,5)
        self.assertEqual((x+2*y, y-2*x), (2,3))
        x, y = F(-3,25), F(-4,25)
        self.assertEqual((-3*x-4*y, 4*x-3*y), (1,0))
        self.assertEqual(abs(-3+4j), 5)
        self.assertEqual((1+1j)/(1-1j), 1j)
        self.assertIn(r'\frac{-4+7i}{5}', MANUAL)
        self.assertIn('$(-3-4i)/25$', ANSWERS)
        self.assertIn(r'La condition $z\ne0$ est indispensable', MANUAL)

    def test_polar_forms_and_quadrants(self):
        cases = [(1+1j, math.sqrt(2), math.pi/4),
                 (-math.sqrt(3)+1j, 2, 5*math.pi/6),
                 (-2j, 2, -math.pi/2),
                 (-1+1j, math.sqrt(2), 3*math.pi/4),
                 (-math.sqrt(3)-1j, 2, -5*math.pi/6)]
        for z, radius, theta in cases:
            with self.subTest(z=z):
                self.assertAlmostEqual(abs(z), radius)
                self.assertComplexAlmostEqual(cmath.rect(radius, theta), z)
                self.assertComplexAlmostEqual(cmath.rect(radius, theta+2*math.pi), z)
        self.assertAlmostEqual(cmath.phase(-1+1j)-cmath.phase(1-1j), math.pi)
        self.assertComplexAlmostEqual(cmath.rect(3,-math.pi/6), 3*math.sqrt(3)/2-1.5j)
        self.assertIn("Le nombre $0$ n'a pas d'argument", MANUAL)
        self.assertIn(r'2\e^{-5i\pi/6}', ANSWERS)

    def test_rotation_product_and_quotient(self):
        self.assertEqual(1j*(1+1j), -1+1j)
        self.assertEqual(abs(1+1j), abs(-1+1j))
        z, w = cmath.rect(2,math.pi/3), cmath.rect(3,-math.pi/6)
        self.assertComplexAlmostEqual(z*w, 3*math.sqrt(3)+3j)
        self.assertComplexAlmostEqual(z/w, 2j/3)
        self.assertEqual(2*(-1j), -2j)
        self.assertIn('3\\sqrt3+3i', ANSWERS)
        self.assertIn('2i/3', ANSWERS)

    def test_powers_and_all_distinct_roots(self):
        self.assertEqual((1+1j)**8, 16)
        cases = [(8, 3, [2, -1+1j*math.sqrt(3), -1-1j*math.sqrt(3)]),
                 (-16, 4, [complex(a,b)*math.sqrt(2) for a,b in [(1,1),(-1,1),(-1,-1),(1,-1)]]),
                 (16, 4, [2,2j,-2,-2j])]
        for w, n, roots in cases:
            with self.subTest(w=w, n=n):
                self.assertEqual(len(set(roots)), n)
                for z in roots:
                    self.assertComplexAlmostEqual(z**n, w)
                # Verify completeness by reconstructing the monic polynomial.
                coefficients = [1]
                for z in roots:
                    expanded = [0]*(len(coefficients)+1)
                    for k, coefficient in enumerate(coefficients):
                        expanded[k] += coefficient
                        expanded[k+1] -= coefficient*z
                    coefficients = expanded
                for actual, expected in zip(coefficients, [1]+[0]*(n-1)+[-w]):
                    self.assertComplexAlmostEqual(actual, expected)
        self.assertIn(r'k=0,1,\ldots,n-1', MANUAL)
        self.assertIn("Pour $w=0$, l'unique solution est $z=0$", MANUAL)
        self.assertIn(r'$z^4=-16$', QUESTIONS)
        self.assertIn(r'2\e^{i(\pi/4+k\pi/2)}', ANSWERS)

    def test_quadratics_by_substitution_and_vieta(self):
        cases = [(1,-2,5, [1+2j,1-2j]), (1,4,13, [-2+3j,-2-3j]),
                 (2,-4,1, [1+math.sqrt(2)/2,1-math.sqrt(2)/2]),
                 (1,-6,13, [3-2j,3+2j]), (1,-2,2, [1+1j,1-1j])]
        for a,b,c,roots in cases:
            with self.subTest(a=a,b=b,c=c):
                for z in roots:
                    self.assertComplexAlmostEqual(a*z*z+b*z+c, 0)
                self.assertComplexAlmostEqual(sum(roots), -b/a)
                self.assertComplexAlmostEqual(math.prod(roots), c/a)
        self.assertIn(r'z^2-6z+13', ANSWERS)
        self.assertIn(r'z^2-2z+2', ANSWERS)
        self.assertIn(r'a,b,c\in\R', MANUAL)
        self.assertIn(r'a\ne0', MANUAL)

    def test_synthesis_quotient_and_square(self):
        z = (2+2j)/(math.sqrt(3)-1j)
        self.assertComplexAlmostEqual(z, (math.sqrt(3)-1)/2+1j*(math.sqrt(3)+1)/2)
        self.assertAlmostEqual(abs(z), math.sqrt(2))
        self.assertAlmostEqual(cmath.phase(z), 5*math.pi/12)
        self.assertComplexAlmostEqual(z**12, -64)
        roots = [2,2j,-2,-2j]
        sides = [roots[(k+1)%4]-roots[k] for k in range(4)]
        for k, side in enumerate(sides):
            self.assertAlmostEqual(abs(side), 2*math.sqrt(2))
            self.assertAlmostEqual((side.conjugate()*sides[(k+1)%4]).real, 0)
        area = abs(sum((roots[k].conjugate()*roots[(k+1)%4]).imag for k in range(4)))/2
        self.assertEqual(area,8)
        self.assertIn(r'z^{12}=64\e^{5i\pi}=-64', ANSWERS)
        self.assertIn('aire $8$', ANSWERS)


class StableBookMigration(unittest.TestCase):
    def test_legacy_identities_are_preserved_and_new_ones_are_distinct(self):
        indexes = video_map.section_indexes()
        migration = json.loads((ROOT/'docs/section-migration-2026-11-06.json').read_text())
        for area, index in indexes.items():
            self.assertEqual(len(index),134)
            legacy = [key for key in index if not key.startswith('complexes.')]
            self.assertEqual(len(legacy),126)
            self.assertEqual(legacy,migration['legacy_section_ids'])
            for number in range(1,9):
                old, new = index[f'17.{number}'], index[f'complexes.{number}']
                self.assertEqual(old['chapter'],'A')
                self.assertEqual(old['display'],f'A.{number}')
                self.assertEqual(old['label'],f'{area}:section:17.{number:02}')
                self.assertEqual(new['chapter'],17)
                self.assertEqual(new['display'],f'17.{number}')
                self.assertNotEqual(old['label'],new['label'])
            self.assertIn('Vitesse angulaire',index['17.1']['heading_source'])
            self.assertIn('Construire les nombres complexes',index['complexes.1']['heading_source'])
        self.assertEqual(list(indexes['manual']),list(indexes['workbook']))

    def test_circular_sources_and_answers_survive_except_display_references(self):
        migration = json.loads((ROOT/'docs/section-migration-2026-11-06.json').read_text())
        for item in migration['moved_sources']:
            restored = (ROOT/item['to']).read_text()
            for old,new in item['allowed_text_replacements'].items():
                restored = restored.replace(new,old)
            self.assertEqual(hashlib.sha256(restored.encode()).hexdigest(),item['before_sha256'])
        answers = (ROOT/'sources/workbook/backmatter.tex').read_text()
        preserved = answers[answers.index(r'\chapter*{Annexe A --'):answers.index('\\fi\n\\backmatter')]
        for old,new in migration['preserved_answers']['allowed_text_replacements'].items():
            preserved = preserved.replace(new,old)
        self.assertEqual(hashlib.sha256(preserved.encode()).hexdigest(),migration['preserved_answers']['before_sha256'])

    def test_legacy_video_references_show_appendix_not_complexes(self):
        index = video_map.section_indexes()['manual']
        ref = {'sections':['17.1','17.5'],'chapters':[]}
        self.assertEqual(video_map.reference_text(ref,index),r'\S\S\ A.1, A.5')
        ref['sections']=['complexes.1']
        self.assertEqual(video_map.reference_text(ref,index),r'\S\ 17.1')
        # Historical callers and indices without display remain valid.
        self.assertEqual(video_map.reference_text({'sections':['1.1'],'chapters':[]},index),r'\S\ 1.1')
        self.assertEqual(video_map.reference_text({'sections':['1.1'],'chapters':[]}),r'\S\ 1.1')

    def test_invalid_index_identity_display_heading_or_label_fails(self):
        originals = {area:json.loads((ROOT/f'docs/{area}_section_index.json').read_text())
                     for area in ('manual','workbook')}
        for mode in ('duplicate','display','heading','label','chapter'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root/'docs').mkdir()
                (root/'sources').symlink_to(ROOT/'sources',target_is_directory=True)
                rows = copy.deepcopy(originals)
                target = rows['manual'][-1]
                if mode=='duplicate':
                    target['id']=rows['manual'][0]['id']
                elif mode=='display':
                    target['display']='17.8'
                elif mode=='heading':
                    target['heading_source']=r'\section{Wrong}'
                elif mode=='label':
                    target['label']='manual:section:missing'
                else:
                    target['chapter']='B'
                for area in rows:
                    (root/f'docs/{area}_section_index.json').write_text(json.dumps(rows[area]))
                with self.assertRaises(ValueError):
                    video_map.section_indexes(root)


if __name__ == '__main__':
    unittest.main()
