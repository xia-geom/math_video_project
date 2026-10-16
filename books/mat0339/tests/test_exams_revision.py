"""Recalculs indépendants de la banque du 10 octobre; aucune certification pédagogique."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import re
import unittest
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITION = ROOT / "exams/2026-10-10"


def product(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)) for i in range(2))


class ExamEditionContracts(unittest.TestCase):
    def test_september_archive_unchanged(self):
        provenance = json.loads((EDITION / "provenance.json").read_text())
        for relative, expected in provenance["source_files_sha256"].items():
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((ROOT / "exams/2026-09-06" / relative).read_bytes()).hexdigest(), expected)

    def test_questions_points_and_pairing_preserved(self):
        manifest = json.loads((EDITION / "examens_manifest.json").read_text())
        self.assertEqual(len(manifest), 18)
        total_items = 0
        for series, exam in itertools.product("ABC", range(1, 4)):
            base = EDITION / f"sources/serie_{series}/examen_{exam}"
            subject = base.with_name(base.name + "_sujet.tex").read_text()
            answers = base.with_name(base.name + "_corrige.tex").read_text()
            questions = re.findall(r"\\hfill\\textbf\{(\d+) points\}", answers)
            expected = [int(x) for x in re.findall(r"\\item \\textbf\{\((\d+) points\)\}", subject)]
            actual = [int(x) for x in re.findall(r"\\item \\textbf\{(\d+) points\.", answers)]
            with self.subTest(series=series, exam=exam):
                self.assertEqual(len(questions), 6)
                self.assertEqual(sum(map(int, questions)), 100)
                self.assertEqual(expected, actual)
                self.assertEqual(sum(actual), 100)
                chunks = re.split(r"\{\\large\\bfseries Question \d+ -- ", answers)[1:]
                for declared, chunk in zip(questions, chunks):
                    allocations = re.findall(r"\\item \\textbf\{(\d+) points\.", chunk)
                    self.assertEqual(sum(map(int, allocations)), int(declared))
                for text in (subject, answers):
                    self.assertIn("10 octobre 2026", text)
                    self.assertNotIn("write18", text)
                    self.assertIn(r"\pageref*{LastPage}", text)
            total_items += len(actual)
        self.assertEqual(total_items, 165)

    def test_review_matches_final_source(self):
        review = json.loads((EDITION / "review.json").read_text())
        self.assertEqual(len(review["questions"]), 54)
        self.assertEqual(sum(q["subquestions"] for q in review["questions"]), 165)
        self.assertEqual(len(review["reviewed_source_sha256"]), 18)
        for relative, expected in review["reviewed_source_sha256"].items():
            self.assertEqual(hashlib.sha256((EDITION / relative).read_bytes()).hexdigest(), expected,
                             f"Source changed after mathematical review: {relative}")


class ExamCalculations(unittest.TestCase):
    def test_exact_arithmetic_radicals_and_percentage_composition(self):
        self.assertEqual((F(3, 4) - F(1, 6)) / F(7, 12), 1)
        self.assertEqual((F(5, 6) - F(1, 4)) / F(7, 8), F(2, 3))
        self.assertEqual((F(7, 10) + F(1, 5)) / F(3, 2), F(3, 5))
        for high, low, factor, radicand in [(72, 8, 4, 2), (75, 12, 3, 3), (98, 32, 3, 2)]:
            self.assertAlmostEqual(math.sqrt(high) - math.sqrt(low), factor * math.sqrt(radicand))
        for price, up, down, final, rate in [(80,F(5,4),F(4,5),F(80),F(0)),
                (120,F(9,10),F(6,5),F(648,5),F(2,25)),
                (200,F(23,20),F(17,20),F(391,2),F(-9,400))]:
            self.assertEqual(price * up * down, final)
            self.assertEqual(up * down - 1, rate)
        for x in range(-5, 6):
            for value in (x-3, 2*x+1, x+2):
                self.assertEqual(math.sqrt(value * value), abs(value))

    def test_radical_equations_original_domain_and_extraneous_roots(self):
        for a, b, candidates, expected in [(2,3,(3,-1),3), (3,4,(4,-1),4), (1,6,(3,-2),3)]:
            valid = [x for x in candidates if a*x+b >= 0 and math.sqrt(a*x+b) == x]
            self.assertEqual(valid, [expected])
            self.assertEqual(F(a) * F(-b,a) + b, 0)
            for x in candidates:
                self.assertEqual(x*x, a*x+b)
        self.assertEqual([x for x in (-1,4) if x >= 1 and math.sqrt(x+5) == x-1], [4])

    def test_rational_inequalities_all_regions_and_boundaries(self):
        cases = [(1,-2,lambda y:y>=0,lambda x:x < -2 or x >= 1),
                 (-1,3,lambda y:y<=0,lambda x:-1 <= x < 3),
                 (2,-4,lambda y:y<0,lambda x:-4 < x < 2),
                 (2,-1,lambda y:y>0,lambda x:x < -1 or x > 2)]
        for zero, pole, predicate, membership in cases:
            for x in map(F, range(-8, 9)):
                if x != pole:
                    self.assertEqual(predicate((x-zero)/(x-pole)), membership(x))
                else:
                    self.assertFalse(membership(x))

    def test_composition_domains_and_inverse_both_directions(self):
        for a,b,c,d,bound,le in [(1,1,2,-3,1,False),(-1,4,3,1,1,True),(1,-2,-2,5,F(3,2),True)]:
            for x in (F(-10),F(0),F(1),F(3,2),F(2),F(7)):
                g = c*x+d
                self.assertEqual(a*g+b >= 0, x <= bound if le else x >= bound)
                self.assertEqual((g-d)/c, x)
                self.assertEqual(c*((x-d)/c)+d, x)
        # Distinct valid inputs exercise both orders without silently sharing their domains.
        self.assertEqual(2*math.sqrt(3+1)-3,1)
        self.assertEqual(math.sqrt((2*3-3)+1),2)
        self.assertEqual(3*math.sqrt(4-0)+1,7)
        self.assertEqual(math.sqrt(4-(3*1+1)),0)
        self.assertEqual(5-2*math.sqrt(6-2),1)
        self.assertEqual(math.sqrt((5-2*F(3,2))-2),0)
        for x in map(F, range(-3,4)):
            self.assertEqual(5-(5-x), x)
            self.assertNotEqual(3*x+2, 3*x+10)

    def test_quadratic_models_domains_and_level_sets(self):
        for x in map(F, range(0,16)):
            self.assertEqual(x*(15-x), -(x-F(15,2))**2+F(225,4))
            self.assertEqual(x*(15-x)>=50, 5<=x<=10)
        for t in map(F, range(0,8)):
            self.assertEqual(-2*t*t+12*t+14, -2*(t-3)**2+32)
            self.assertEqual(-2*t*t+12*t+14 >= 24, 1<=t<=5)
        for q in map(F, range(0,21)):
            self.assertEqual(-q*q+20*q-64, -(q-10)**2+36)
            self.assertEqual(-q*q+20*q-64>0, 4<q<16)

    def test_rational_holes_poles_and_admissible_zeros(self):
        for hole, zero, pole, value in [(1,-1,2,F(-2)),(2,-2,-3,F(4,5)),(1,-3,-1,F(2))]:
            self.assertNotEqual(hole,pole)
            self.assertEqual(F(hole-zero,hole-pole),value)
            for x in range(-6,7):
                if x not in (hole,pole):
                    self.assertEqual(F((x-hole)*(x-zero),(x-hole)*(x-pole)),F(x-zero,x-pole))
            self.assertNotIn(zero,(hole,pole))
            self.assertNotEqual(pole-zero,0)
        self.assertEqual(F(5*5-9,5-3),8)

    def test_growth_decay_real_thresholds_and_integer_boundaries(self):
        self.assertEqual(F(500)*F(108,100)**3,F(78732,125))
        self.assertEqual(round(500*1.08**3,2),629.86)
        self.assertEqual(round(240*2**(-1.5),2),84.85)
        self.assertEqual(F(1000)*F(9,10)**4,F(6561,10))
        t = math.log(2)/math.log(1.08)
        self.assertEqual(round(t,2),9.01)
        self.assertEqual(math.ceil(t),10)
        self.assertLess(F(500)*F(27,25)**9,1000)
        self.assertGreater(F(500)*F(27,25)**10,1000)
        self.assertEqual(round(500*1.08**9,2),999.50)
        self.assertEqual(round(500*1.08**10,2),1079.46)
        self.assertEqual(240*2**(-18/6),30)
        self.assertLess(240*2**(-19/6),30)
        t=math.log(.5)/math.log(.9)
        self.assertEqual(round(t,2),6.58)
        self.assertEqual(math.ceil(t),7)
        self.assertGreater(F(1000)*F(9,10)**6,500)
        self.assertLess(F(1000)*F(9,10)**7,500)

    def test_log_equations_domain_selection_and_substitution(self):
        for p,q,rhs,roots,expected in [(-1,1,8,(-3,3),3),(-2,0,8,(-2,4),4),(1,-2,4,(-2,3),3)]:
            valid=[]
            for x in roots:
                self.assertEqual((x+p)*(x+q),rhs)
                if x+p>0 and x+q>0:
                    self.assertAlmostEqual(math.log(x+p)+math.log(x+q),math.log(rhs))
                    valid.append(x)
            self.assertEqual(valid,[expected])

    def test_codes_committees_roles_and_anagrams(self):
        self.assertEqual(26*25*10**2,65000)
        self.assertEqual(26*10*9*8,18720)
        self.assertEqual(10**2*26*25,65000)
        self.assertEqual(math.comb(8,3),56)
        self.assertEqual(math.comb(9,4),126)
        self.assertEqual(8*7,56)
        for word,expected in [("ANANAS",60),("LEVEL",30),("LETTRE",180)]:
            counts=Counter(word)
            self.assertEqual(math.factorial(len(word))//math.prod(math.factorial(n) for n in counts.values()),expected)
            self.assertEqual(len(set(itertools.permutations(word))),expected)

    def test_urn_probabilities_by_ordered_individual_draws(self):
        for red,blue,expected_paths,expected_event,expected_cond,different in [
                (4,3,[F(2,7)]*3+[F(1,7)],F(3,7),F(2,3),False),
                (5,3,[F(5,14),F(15,56),F(15,56),F(3,28)],F(15,28),F(3,7),True),
                (3,2,[F(3,10)]*3+[F(1,10)],F(2,5),F(3,4),False)]:
            balls=list(enumerate("R"*red+"B"*blue))
            outcomes=list(itertools.permutations(balls,2))
            counts=Counter(a[1]+b[1] for a,b in outcomes)
            paths=[F(counts[p],len(outcomes)) for p in ("RR","RB","BR","BB")]
            self.assertEqual(paths,expected_paths)
            self.assertEqual(sum(paths),1)
            self.assertEqual(paths[1]+paths[2] if different else paths[0]+paths[3],expected_event)
            cond=paths[2]/(paths[0]+paths[2]) if different else paths[1]/(paths[1]+paths[3])
            self.assertEqual(cond,expected_cond)
            self.assertNotEqual(F(red-1,red+blue-1),F(red,red+blue))
        self.assertEqual(F(2,5)*F(1,4),F(1,10))

    def test_binomial_and_expectation_by_outcome_enumeration(self):
        for n,p,k,win,loss,prob,atleast,expectation in [
            (5,F(4,5),4,6,4,F(256,625),F(3124,3125),4),
            (4,F(3,4),3,5,3,F(27,64),F(255,256),3),
            (6,F(1,2),3,8,2,F(5,16),F(63,64),3)]:
            distribution=Counter()
            for sequence in itertools.product((0,1),repeat=n):
                successes=sum(sequence)
                distribution[successes]+=p**successes*(1-p)**(n-successes)
            self.assertEqual(sum(distribution.values()),1)
            self.assertEqual(distribution[k],prob)
            self.assertEqual(1-distribution[0],atleast)
            self.assertEqual(win*p-loss*(1-p),expectation)
        self.assertEqual(1-F(4,5)**3,F(61,125))
        self.assertEqual(F(math.comb(3,2),8),F(3,8))

    def test_vector_projection_angle_and_orthogonal_residual(self):
        for u,v,projection,angle in [((3,4),(4,0),(3,0),53.13),((1,3),(2,2),(2,2),26.57),((4,2),(0,3),(0,2),63.43)]:
            uv=sum(a*b for a,b in zip(u,v))
            vv=sum(b*b for b in v)
            p=tuple(F(uv,vv)*b for b in v)
            self.assertEqual(p,projection)
            self.assertEqual(sum((a-c)*b for a,b,c in zip(u,v,p)),0)
            actual=math.degrees(math.acos(uv/math.sqrt(sum(a*a for a in u)*vv)))
            self.assertEqual(round(actual,2),angle)

    def test_matrix_products_inverse_and_solutions(self):
        cases=[(((2,1),(1,1)),((1,2),(0,1)),((2,5),(1,3)),((4,3),(1,1)),(7,4),(3,1)),
               (((1,2),(2,3)),((2,0),(0,1)),((2,2),(4,3)),((2,4),(2,3)),(8,13),(2,3)),
               (((3,1),(2,1)),((1,0),(1,1)),((4,1),(3,1)),((3,1),(5,2)),(11,8),(3,2))]
        for a,b,ab,ba,rhs,solution in cases:
            self.assertEqual(product(a,b),ab)
            self.assertEqual(product(b,a),ba)
            self.assertNotEqual(ab,ba)
            det=a[0][0]*a[1][1]-a[0][1]*a[1][0]
            inverse=((F(a[1][1],det),F(-a[0][1],det)),(F(-a[1][0],det),F(a[0][0],det)))
            self.assertEqual(product(a,inverse),((1,0),(0,1)))
            self.assertEqual(product(inverse,a),((1,0),(0,1)))
            self.assertEqual(tuple(sum(a[i][j]*solution[j] for j in range(2)) for i in range(2)),rhs)

    def test_line_plane_intersections_and_parameter_families(self):
        for point,direction,normal,rhs,t,expected in [((1,0,2),(2,1,-1),(1,1,1),5,1,(3,1,1)),
            ((0,1,1),(1,2,-1),(2,-1,1),3,-3,(-3,-5,4)),
            ((2,-1,0),(1,1,2),(1,-1,1),7,2,(4,1,4))]:
            dot=sum(a*b for a,b in zip(normal,direction))
            self.assertNotEqual(dot,0)
            self.assertEqual(F(rhs-sum(a*b for a,b in zip(normal,point)),dot),t)
            intersection=tuple(a+t*b for a,b in zip(point,direction))
            self.assertEqual(intersection,expected)
            self.assertEqual(sum(a*b for a,b in zip(normal,intersection)),rhs)
        for rhs1,rhs2 in [(3,1),(4,2),(5,1)]:
            for s in map(F,(-7,0,2,11)):
                x,y,z=F(rhs1+rhs2,2)-s,F(rhs1-rhs2,2),s
                self.assertEqual(x+y+z,rhs1)
                self.assertEqual(x-y+z,rhs2)
                self.assertEqual(2*x+2*z,rhs1+rhs2)

    def test_linear_programming_all_vertices_from_constraints(self):
        for rows,objective,expected_point,expected_value in [
            (((1,2,12),(2,1,12)),(30,40),(F(4),F(4)),280),
            (((3,1,18),(1,1,8)),(70,40),(F(5),F(3)),470),
            (((2,1,14),(1,3,18)),(40,50),(F(24,5),F(22,5)),412)]:
            boundaries=[*rows,(1,0,0),(0,1,0)]
            vertices=set()
            for (a,b,c),(d,e,f) in itertools.combinations(boundaries,2):
                det=a*e-b*d
                if not det:
                    continue
                x,y=F(c*e-b*f,det),F(a*f-c*d,det)
                if x>=0 and y>=0 and all(i*x+j*y<=k for i,j,k in rows):
                    vertices.add((x,y))
            self.assertEqual(len(vertices),4)
            optimum=max(vertices,key=lambda p:sum(a*b for a,b in zip(objective,p)))
            self.assertEqual(optimum,expected_point)
            self.assertEqual(sum(a*b for a,b in zip(objective,optimum)),expected_value)
            self.assertTrue(all(a*optimum[0]+b*optimum[1]==c for a,b,c in rows))

    def test_radians_sectors_triangles_and_rounding(self):
        for degrees,ratio,sine,cosine in [(225,F(5,4),-math.sqrt(2)/2,-math.sqrt(2)/2),
            (-120,F(-2,3),-math.sqrt(3)/2,-.5),(330,F(11,6),-.5,math.sqrt(3)/2)]:
            self.assertEqual(F(degrees,180),ratio)
            self.assertAlmostEqual(math.sin(float(ratio)*math.pi),sine)
            self.assertAlmostEqual(math.cos(float(ratio)*math.pi),cosine)
        for radius,alpha,arc,area in [(6,F(2,3),4,12),(4,F(3,4),3,6),(5,F(4,5),4,10)]:
            self.assertEqual(radius*alpha,arc)
            self.assertEqual(F(radius**2,2)*alpha,area)
        for a,b,c2,angle,area_coefficient in [(7,9,67,47.78,F(63,4)),(6,8,52,46.10,F(12)),(5,8,49,38.21,F(10))]:
            self.assertEqual(a*a+b*b-a*b,c2)
            c=math.sqrt(c2)
            self.assertTrue(abs(b-a)<c<a+b)
            self.assertEqual(round(math.degrees(math.acos((b*b+c2-a*a)/(2*b*c))),2),angle)
            self.assertEqual(F(a*b,4),area_coefficient)

    def test_trigonometric_roots_all_branches_on_half_open_interval(self):
        cases=[(lambda x:math.sin(x)+.5,[F(7,6),F(11,6)]),
               (lambda x:math.cos(2*x)-.5,[F(1,6),F(5,6),F(7,6),F(11,6)]),
               (lambda x:math.cos(x)+math.sqrt(3)/2,[F(5,6),F(7,6)]),
               (lambda x:math.sin(2*x),[F(0),F(1,2),F(1),F(3,2)]),
               (lambda x:math.tan(x)-1,[F(1,4),F(5,4)]),
               (lambda x:2*math.sin(x)**2-1,[F(1,4),F(3,4),F(5,4),F(7,4)])]
        for function,roots in cases:
            # The pi/12 grid contains every root of these particular exact equations.
            actual=[F(k,12) for k in range(24) if abs(function(k*math.pi/12))<1e-9]
            self.assertEqual(actual,roots)
            self.assertTrue(all(0<=r<2 for r in roots))

    def test_sinusoid_characteristics_and_all_level_times(self):
        models=[(lambda t:14-12*math.cos(math.pi*t/20),40,2,26,20,[40/3,80/3]),
                (lambda t:16+6*math.cos(math.pi*(t-14)/12),24,10,22,19,[10,18]),
                (lambda t:4+3*math.sin(math.pi*(t-2)/6),12,1,7,5.5,[3,7])]
        for function,period,low,high,target,roots in models:
            values=[function(period*k/240) for k in range(240)]
            self.assertAlmostEqual(min(values),low)
            self.assertAlmostEqual(max(values),high)
            for t in (0,1,3,9):
                self.assertAlmostEqual(function(t+period),function(t))
            for t in roots:
                self.assertAlmostEqual(function(t),target)
            self.assertEqual(len(roots),2)
        self.assertEqual(models[0][0](0),2)
        self.assertEqual(models[1][0](14),22)
        self.assertEqual(models[2][0](2),4)
        self.assertGreater(models[2][0](2.01),4)


if __name__ == "__main__":
    unittest.main()
