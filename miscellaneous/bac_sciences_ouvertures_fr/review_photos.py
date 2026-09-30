"""Explicit network preparation for the openings photo review; never publishes.

Run separately from the renderer. Candidate downloads are review material, not
proof of permission or approval. The existing pinned campus asset is restored
on fresh checkouts without modifying the shared photo inventory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATES = [
    {
        "key": "science_library",
        "url": "https://services-medias.uqam.ca/media/uploads/sites/4/2026/04/01104213/Image-e1783021536544.jpg",
        "source_url": "https://bibliotheques.uqam.ca/nouvelles/top-6-des-meilleurs-endroits-pour-etudier-aux-bibliotheques/",
        "credit": "Service des bibliothèques · UQAM",
        "use": "Science-library study setting; photographer credit not separately identified.",
    },
    {
        "key": "finance_room",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2022/09/fondation-bourse-mtl-7740.jpg",
        "source_url": "https://actualites.uqam.ca/2022/reseautage-a-la-salle-des-marches-esg-uqam/",
        "credit": "Photo : Nathalie St-Pierre",
        "use": "ESG UQAM trading-room networking event, 2022; not a guaranteed mathematics-course facility.",
    },
    {
        "key": "digital_media",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2024/03/jeux-video-1278.jpg",
        "source_url": "https://actualites.uqam.ca/2024/visite-studio-jeux-video-indie-asylum/",
        "credit": "Photo : Nathalie St-Pierre",
        "use": "Indie Asylum studio visited by UQAM digital-media students in 2024; off-campus, not a UQAM laboratory.",
    },
]


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "UQAM-video-visual-review/1.0"})
    with urlopen(request, timeout=45) as response:
        data = response.read(16_000_001)
    if len(data) > 16_000_000:
        raise ValueError("Photograph exceeds the 16 MB review limit")
    with Image.open(BytesIO(data)) as image:
        image.verify()
    return data


def prepare(destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    spec = json.loads((HERE / "project.json").read_text(encoding="utf-8"))
    campus = spec["assets"]["campus"]
    campus_path = (HERE / campus["path"]).resolve()
    if not campus_path.exists():
        data = download("https://salledepresse.uqam.ca/wp-content/uploads/sites/16/2022/01/SB_hr-scaled.jpg")
        if hashlib.sha256(data).hexdigest() != campus["sha256"]:
            raise ValueError("Downloaded campus image differs from the pinned original")
        campus_path.parent.mkdir(parents=True, exist_ok=True)
        campus_path.write_bytes(data)

    records = []
    for candidate in CANDIDATES:
        record = dict(candidate)
        record["rights_status"] = "Review only; formal promotional reuse permission not independently verified."
        try:
            data = download(candidate["url"])
            path = destination / (candidate["key"] + ".jpg")
            path.write_bytes(data)
            with Image.open(BytesIO(data)) as image:
                width, height = image.size
            record.update(status="downloaded", sha256=hashlib.sha256(data).hexdigest(), width=width, height=height,
                          full_screen_eligible=width >= 1600 and height >= 900)
        except (OSError, ValueError) as error:
            record.update(status="unavailable", error=str(error))
        records.append(record)

    snapshot = destination / "source_snapshot"
    paths = [
        HERE / "project.json", HERE / "project.py", HERE / "build.py",
        HERE / "bac_sciences_ouvertures_fr_scene.py", HERE / "requirements.txt",
        HERE / "README.md", ROOT / "tests/test_uqam_ouvertures.py",
        ROOT / "ARCHITECTURE.md", ROOT / "miscellaneous/README.md",
    ]
    for path in paths:
        target = snapshot / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    originals = destination / "current_photos"
    originals.mkdir(exist_ok=True)
    for key, asset in spec["assets"].items():
        path = (HERE / asset["path"]).resolve()
        if path.is_file():
            shutil.copy2(path, originals / (key + ".jpg"))
    (destination / "candidates.json").write_text(
        json.dumps({"candidates": records, "release_ready": False}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.output)


if __name__ == "__main__":
    main()
