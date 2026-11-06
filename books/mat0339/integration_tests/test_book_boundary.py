"""The required book test suite must not depend on the teaching runtime."""

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class BookBoundaryTests(unittest.TestCase):
    def test_normal_tests_run_without_site_packages_or_course_catalogue(self):
        # This suite lives outside tests/, so discovering the required book tests
        # cannot recursively launch this integration test.
        code = """
import importlib.abc
import sys
import unittest

class RejectCourseDependencies(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "tools.course_catalog" or fullname.split(".")[0] in {
            "yaml", "manim", "manim_voiceover", "azure"
        }:
            raise ImportError("Book verification must not import " + fullname)

sys.meta_path.insert(0, RejectCourseDependencies())
suite = unittest.defaultTestLoader.discover(sys.argv[1])
result = unittest.TextTestRunner().run(suite)
raise SystemExit(not result.wasSuccessful())
"""
        result = subprocess.run(
            [sys.executable, "-S", "-B", "-c", code, str(ROOT / "tests")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
