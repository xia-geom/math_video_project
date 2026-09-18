"""Final scoped source corrections; workflow edits use the authorized connector."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace(path, before, after):
    path = ROOT / path
    text = path.read_text()
    if after in text:
        return
    if text.count(before) != 1:
        raise ValueError(f'{path}: unexpected source state')
    path.write_text(text.replace(before, after))


def main():
    path = 'scenes/fonctions_et_graphiques_fr/08_operations_sur_les_fonctions_fr/08_operations_sur_les_fonctions_fr_scene.py'
    replace(path, 'pair_labels[0].move_to([-5.2, -1.4, 0])',
            'pair_labels[0].move_to([-5.25, -0.45, 0])')
    replace(path, 'pair_labels[1].move_to([5.2, -1.4, 0])',
            'pair_labels[1].move_to([5.55, -0.45, 0])')
    replace('scripts/teaching_revision/review.py',
            "frame_limit = 100 if entry['track'] == 'errors' and entry['order'] in (2, 3) else 8",
            "frame_limit = 100 if ((entry['track'] == 'errors' and entry['order'] in (2, 3)) or (entry['track'] == 'programme' and entry['order'] in (1, 8, 12))) else 8")
    replace('tests/test_teaching_revision.py',
            '    from tools.teaching_layout import TeachingScene\n    for key in',
            "    from tools.teaching_layout import TeachingScene\n    monkeypatch.setattr('dotenv.load_dotenv', lambda *args, **kwargs: False)\n    for key in")


if __name__ == '__main__':
    main()
