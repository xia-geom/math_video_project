"""Importing historical migrations must never read or rewrite lesson sources."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class HistoricalUtilityImportTests(unittest.TestCase):
    def test_imports_do_not_touch_source_files(self):
        tools = Path(__file__).resolve().parents[1] / 'tools'
        scripts = sorted(p for p in tools.glob('*.py')
                         if p.name.startswith(('patch_', 'fix_', 'apply_', 'correct_')))
        self.assertTrue(scripts)
        with tempfile.TemporaryDirectory() as folder:
            sentinel = Path(folder) / 'scene.py'
            sentinel.write_text('original lesson\n')
            before = sentinel.read_bytes()
            for path in scripts:
                with self.subTest(path=path.name):
                    spec = importlib.util.spec_from_file_location('historical_' + path.stem, path)
                    module = importlib.util.module_from_spec(spec)
                    with patch.object(Path, 'read_text', side_effect=AssertionError('Source read during import')), \
                         patch.object(Path, 'write_text', side_effect=AssertionError('Source write during import')):
                        spec.loader.exec_module(module)
                    self.assertTrue(callable(module.main))
            self.assertEqual(sentinel.read_bytes(), before)
