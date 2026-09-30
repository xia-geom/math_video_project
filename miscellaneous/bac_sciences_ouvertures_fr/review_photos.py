"""Prepare checksum-pinned UQAM photos before the offline renderer runs.

Downloaded photographs are review material, not proof of promotional reuse
permission. New photos live in ignored media/, not in the Git source history.
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

from miscellaneous.bac_sciences_ouvertures_fr.project import (
    HERE,
    ROOT,
    load_project,
    validate_assets,
)


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
    spec = load_project()
    for key, asset in spec["assets"].items():
        path = (HERE / asset["path"]).resolve()
        if not path.is_relative_to(ROOT):
            raise ValueError("Photo cache must stay inside the repository")
        if not path.is_file():
            url = asset.get("download_url")
            if not url:
                raise FileNotFoundError(f"Missing original repository photo: {key}")
            data = download(url)
            if hashlib.sha256(data).hexdigest() != asset["sha256"]:
                raise ValueError(f"Downloaded photo differs from the reviewed source: {key}")
            with Image.open(BytesIO(data)) as image:
                if image.size != (asset["width"], asset["height"]):
                    raise ValueError(f"Source dimensions changed: {key}")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    resolved = validate_assets(spec)
    originals = destination / "current_photos"
    originals.mkdir(exist_ok=True)
    for key, path in resolved.items():
        shutil.copy2(path, originals / (key + ".jpg"))
    snapshot = destination / "source_snapshot"
    paths = [*HERE.glob("*.py"), HERE / "project.json", HERE / "requirements.txt",
             HERE / "README.md", ROOT / "tests/test_uqam_ouvertures.py"]
    for path in paths:
        target = snapshot / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    (destination / "sources.json").write_text(json.dumps({
        "assets": spec["assets"], "release_ready": False,
        "excluded_candidate": {
            "subject": "Current science-library study space",
            "source_url": "https://bibliotheques.uqam.ca/nouvelles/top-6-des-meilleurs-endroits-pour-etudier-aux-bibliotheques/",
            "download_url": "https://services-medias.uqam.ca/media/uploads/sites/4/2026/04/01104213/Image-e1783021536544.jpg",
            "decoded_dimensions": [1024, 538],
            "reason": "Below the 1600 x 900 native source threshold; not enlarged into the film.",
        },
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.output)


if __name__ == "__main__":
    main()
