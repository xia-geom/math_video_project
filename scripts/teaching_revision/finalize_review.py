"""Finish the observed reflection-label collision and retire CI write access."""
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
    workflow = ROOT / '.github/workflows/teaching-revision.yml'
    source = workflow.read_text()
    start = source.index('      - name: Save final scoped corrections to the working branch')
    end = source.index('      - name: Snapshot exact teaching source', start)
    source = source[:start] + '''      - name: Record the exact tested source commit
        run: |
          mkdir -p review_artifacts/teaching
          git rev-parse HEAD > review_artifacts/teaching/tested_commit.txt
''' + source[end:]
    source = source.replace("    if: github.event.pull_request.head.repo.full_name == github.repository && github.head_ref == 'fix/teaching-layout-voice-intro'\n", '')
    source = source.replace('    permissions:\n      contents: write\n', '')
    source = source.replace('          ref: ${{ github.event.pull_request.head.sha }}\n          fetch-depth: 0',
                            '          ref: ${{ github.event.pull_request.head.sha || github.sha }}\n          persist-credentials: false')
    workflow.write_text(source)


if __name__ == '__main__':
    main()
