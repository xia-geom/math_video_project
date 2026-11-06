"""Check workflow YAML, selection shell syntax and the catalogue selector module."""
import ast
import subprocess

import yaml

from tools.course_catalog import ROOT


def test_workflow_yaml_and_catalogue_script_are_valid():
    for path in [*(ROOT / '.github/workflows').glob('*.yml'), *(ROOT / '.github/workflows').glob('*.yaml')]:
        yaml.safe_load(path.read_text())
    workflow = yaml.safe_load((ROOT / '.github/workflows/smoke.yml').read_text())
    script = next(s['run'] for s in workflow['jobs']['catalog']['steps'] if s.get('id') == 'catalog')
    subprocess.run(['bash', '-n'], input=script, text=True, check=True, capture_output=True)
    ast.parse((ROOT / 'scripts/select_affected_lessons.py').read_text())
