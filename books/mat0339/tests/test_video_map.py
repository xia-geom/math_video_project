"""Le rendu de la carte dépend des identités, pas de copies des numéros vidéo."""
import importlib.util
from pathlib import Path
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


if __name__=='__main__':unittest.main()
