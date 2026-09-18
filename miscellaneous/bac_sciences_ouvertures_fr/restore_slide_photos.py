#!/usr/bin/env python3
"""Recover native photograph crops from the supplied PDF; never upscale them.

PyMuPDF is an extraction-only dependency, not part of the Manim runtime.
Run from any directory with --pdf "/path/to/Accueil Nouveaux-2026-Septembre.pdf".
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image

PDF_SHA256 = "9898b52281f5c6c1d2e1f5c18e7b6ad5e12dcb0cc84f4e992e6812a98de8d30a"
HERE = Path(__file__).resolve().parent
# These are the same photographed subjects and landscape framing as the previous
# review. Coordinates refer to embedded source pixels, not a page screenshot.
CROPS = {
    "students": {"xref": 7, "source_size": [1387, 640], "box": [220, 0, 1123, 508]},
    "building": {"xref": 9, "source_size": [2012, 1128], "box": [900, 130, 2012, 755]},
}


def pixel_digest(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


def restore(pdf: Path, output: Path) -> dict:
    import fitz  # Optional: python -m pip install PyMuPDF==1.26.7

    if hashlib.sha256(pdf.read_bytes()).hexdigest() != PDF_SHA256:
        raise ValueError("This is not the audited PDF. Recheck provenance before extracting.")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite a nonempty directory: {output}")
    result = {"source_pdf_sha256": PDF_SHA256, "source_page": 1, "assets": {}}
    images = {}
    with fitz.open(pdf) as doc:
        page_xrefs = {row[0] for row in doc[0].get_images(full=True)}
        for key, crop in CROPS.items():
            if crop["xref"] not in page_xrefs:
                raise ValueError("Expected image is not on physical page 1")
            raw = doc.extract_image(crop["xref"])
            with Image.open(io.BytesIO(raw["image"])) as image:
                if list(image.size) != crop["source_size"]:
                    raise ValueError("Unexpected embedded image dimensions")
                selected = image.convert("RGB").crop(crop["box"])
                selected.load()
            name = f"slide_01_{key}.png"
            images[name] = selected
            result["assets"][key] = {
                **crop, "path": name, "width": selected.width, "height": selected.height,
                "pixel_sha256": pixel_digest(selected),
                "processing": "native RGB crop; no resizing, sharpening, or generated pixels",
            }
    output.mkdir(parents=True, exist_ok=True)
    for name, image in images.items():
        image.save(output / name, format="PNG")
    for asset in result["assets"].values():
        asset["sha256"] = hashlib.sha256((output / asset["path"]).read_bytes()).hexdigest()
    (output / "manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=HERE / "assets" / "native")
    args = parser.parse_args()
    print(json.dumps(restore(args.pdf, args.output), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
