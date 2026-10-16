"""Le rendu de la carte dépend des identités, pas de copies des numéros vidéo."""
import importlib.util
import copy
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('video_map',ROOT/'scripts/video_map.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


class VideoMapTests(unittest.TestCase):
    def test_number_and_link_follow_catalogue(self):
        mapping={'chapters':[{'chapter':i,'title':str(i),'note':'Couverture partielle.',
                              'lesson_ids':['stable'] if i==1 else []} for i in range(1,18)]}
        entries=[{'lesson_id':'stable','order':4,'title':'Calcul','scene_file':'scenes/04.py'}]
        self.assertIn('[04 - Calcul](../../../scenes/04.py)',module.render(mapping,entries))
        entries[0].update(order=9,scene_file='scenes/09.py')
        result=module.render(mapping,entries)
        self.assertIn('[09 - Calcul](../../../scenes/09.py)',result)
        self.assertNotIn('scenes/04.py',result)
        with self.assertRaises(KeyError):module.render(mapping,[])


class StudentCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT.parents[1]))
        from tools.course_catalog import load_catalog
        cls.entries = load_catalog()[1]
        cls.mapping = json.loads((ROOT/'curriculum/video-map.json').read_text())
        cls.indexes = module.section_indexes()

    def test_complete_catalogue_follows_stable_identity(self):
        content = module.render_catalogue(self.mapping, self.entries, self.indexes)
        self.assertEqual(content, (ROOT/'curriculum/catalogue-videos.tex').read_text())
        self.assertEqual(content.count(r'\addlinespace[7pt]'), len(self.entries))
        changed = copy.deepcopy(self.entries)
        changed[0].update(order=88, title='Titre corrigé & vérifié')
        content = module.render_catalogue(self.mapping, changed, self.indexes)
        self.assertIn(r'88 & \textbf{Titre corrigé \& vérifié}', content)
        self.assertNotIn('01 & ', content)

    def test_manual_and_workbook_targets_are_independent(self):
        ref = self.mapping['catalogue_references']['fonctions_rationnelles']
        self.assertEqual(ref['manual']['sections'], ['5.2', '5.3', '5.4'])
        self.assertEqual(ref['workbook']['sections'], ['5.1', '5.2', '5.3'])
        copy_map = copy.deepcopy(self.mapping)
        copy_map['catalogue_references']['fonctions_rationnelles']['workbook']['sections'] = ['2.2']
        content = module.render_catalogue(copy_map, self.entries, self.indexes)
        row = next(line for line in content.splitlines() if line.startswith('15 & '))
        self.assertIn(r'\S\S\ 5.2, 5.3, 5.4 & \S\ 2.2', row)
        root_rule = self.mapping['catalogue_references']['racine_d_un_produit']
        self.assertEqual(root_rule['manual']['sections'], ['1.4'])
        self.assertEqual(root_rule['workbook']['sections'], ['1.6'])
        equality = self.mapping['catalogue_references']['egalite_de_fonctions']
        self.assertEqual(equality['manual']['sections'], ['3.1'])
        self.assertEqual(equality['workbook']['sections'], ['2.2'])

    def test_missing_unknown_and_invalid_targets_fail(self):
        for mode in ('missing', 'extra', 'section', 'chapter', 'duplicate', 'ambiguous'):
            mapping = copy.deepcopy(self.mapping)
            refs = mapping['catalogue_references']
            target = refs['variables_et_polynomes']['manual']
            if mode == 'missing': del refs['variables_et_polynomes']
            elif mode == 'extra': refs['unknown_lesson'] = refs['variables_et_polynomes']
            elif mode == 'section': target['sections'] = ['99.1']
            elif mode == 'chapter': target['chapters'] = [18]
            elif mode == 'duplicate': target['sections'] = ['2.1', '2.1']
            else: target['chapters'] = [2]
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                module.validate_references(mapping, self.entries, self.indexes)

    def test_honest_fallbacks_and_no_technical_links(self):
        refs = self.mapping['catalogue_references']
        self.assertEqual(module.reference_text(refs['aire_du_cercle']['manual']), 'Ch. 14')
        self.assertEqual(module.reference_text(refs['notation_sigma']['manual']), 'Complément transversal')
        content = module.render_catalogue(self.mapping, self.entries, self.indexes)
        for forbidden in ('http:', 'https:', r'\href', r'\url', 'scenes/', '.py', 'QR'):
            self.assertNotIn(forbidden, content)


if __name__=='__main__':unittest.main()
