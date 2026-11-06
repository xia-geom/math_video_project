"""Exercise real import closures and fail-open-to-full render selection."""
import tempfile
import unittest
from pathlib import Path

from scripts.select_affected_lessons import changed_paths, select


class AffectedLessonsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.entries = [{'lesson_id': name, 'scene_file': f'scenes/{name}/{name}_scene.py',
                         'scene_class': name.title()} for name in ('one', 'two')]
        sources = {'scenes/one/one_scene.py': 'from tools.shared import helper\n',
                   'scenes/two/two_scene.py': 'from tools.shared import helper\n',
                   'tools/shared.py': 'helper = 1\n',
                   'curriculum/programme_principal_fr.yaml': 'fixture: true\n'}
        for name, text in sources.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)

    def selected(self, *paths):
        return select(self.entries, list(paths), self.root)

    def test_documentation_only_and_single_scene_changes(self):
        self.assertEqual(self.selected('docs/DEVELOPMENT.md')['selected_count'], 0)
        self.assertEqual(self.selected()['selected_count'], 0)
        self.assertEqual(self.selected(self.entries[0]['scene_file'])['lesson_ids'], ['one'])

    def test_catalogue_and_shared_helpers_select_all_dependents(self):
        for path in ('curriculum/programme_principal_fr.yaml', 'tools/shared.py'):
            with self.subTest(path=path):
                self.assertEqual(self.selected(path)['selected_count'], 2)

    def test_unknown_deleted_and_unparseable_dependencies_select_full_scope(self):
        for path in ('tools/new_dynamic_loader.py', 'assets/unknown.png', '../outside'):
            with self.subTest(path=path):
                self.assertEqual(self.selected(path)['selected_count'], 2)
        (self.root / 'tools/shared.py').unlink()
        self.assertEqual(self.selected('tools/shared.py')['selected_count'], 2)
        (self.root / self.entries[1]['scene_file']).write_text('def broken(:')
        self.assertEqual(self.selected(self.entries[0]['scene_file'])['selected_count'], 2)

    def test_missing_or_untrusted_git_comparison_keeps_full_scope(self):
        self.assertIsNone(changed_paths({'before': '--output=/tmp/unsafe', 'after': 'a' * 40}, self.root))
        self.assertIsNone(changed_paths({'before': 'a' * 40, 'after': 'b' * 40}, self.root))
        self.assertEqual(select(self.entries, None, self.root)['selected_count'], 2)
