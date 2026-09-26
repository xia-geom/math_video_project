"""Check both YAML parsing and the embedded Python used for the dynamic matrix."""
import ast

import yaml

from tools.course_catalog import ROOT


def test_workflow_yaml_and_catalogue_script_are_valid():
    for path in (ROOT / '.github/workflows').glob('*.yml'):
        yaml.safe_load(path.read_text())
    workflow = yaml.safe_load((ROOT / '.github/workflows/smoke.yml').read_text())
    script = next(s['run'] for s in workflow['jobs']['catalog']['steps'] if s.get('id') == 'catalog')
    ast.parse(script.split("<<'PYTHON'\n", 1)[1].rsplit('\nPYTHON', 1)[0])
