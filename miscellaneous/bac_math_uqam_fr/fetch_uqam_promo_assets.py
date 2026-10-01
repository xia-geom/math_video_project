"""Fetch and inventory sourced UQAM review assets; rendering stays offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ASSET_DIR = REPO_ROOT / "assets" / "uqam_promo"
UQAM_DEFAULT_PHOTO_LIBRARY = "https://salledepresse.uqam.ca/banque-de-photos/"
UQAM_PAVILION_PHOTO_LIBRARY = "https://salledepresse.uqam.ca/banque-de-photos/photos-de-pavillons/"
AUTHORIZATION_BASIS = (
    "User directed inclusion of the selected UQAM-published images and stated "
    "that they believe this use is acceptable. Formal republication permission "
    "was not independently documented by this tool."
)
RIGHTS_STATUS = "User-directed inclusion; formal reuse permission not independently verified."

ASSETS: list[dict[str, str]] = [
    {
        "kind": "image",
        "filename": "math_workshop_2019.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2022/01/ateliers-scientifiques-4633-002.jpg",
        "source_page": "https://actualites.uqam.ca/2019/4-a-6-des-sciences-ateliers-gratuits-grand-public/",
        "credit": "Nathalie St-Pierre",
        "use": "Public mathematics workshop in 2019, not a regular undergraduate class. Limited to a 1000-pixel panel; never full-bleed at 1080p.",
        "authorization_basis": "User-requested editorial review of UQAM-published imagery.",
        "rights_status": "Review use; formal republication permission not independently verified.",
        "expected_sha256": "80761c168c7570d89dcc575af92e2a0e633b1817be74030313af7e087f826136",
    },
    {
        "kind": "image",
        "filename": "student_welcome_2025.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2025/09/accueil-etudiants-internationaux-5994.jpg",
        "source_page": "https://actualites.uqam.ca/2025/fete-accueil-pour-les-etudiantes-et-etudiants-internationaux-25/",
        "credit": "Nathalie St-Pierre",
        "use": "Student welcome event, September 2025: the Triplex language game. Warm campus atmosphere, not mathematics teaching or a literal mentoring session.",
        "authorization_basis": "User-requested editorial review of UQAM-published imagery.",
        "rights_status": "Review use; formal republication permission not independently verified.",
        "expected_sha256": "88b18808f7717dd8bbbb1ae7ce6af617ed9eec042b8f9e2e415f5e61967bfea3",
    },
    {
        "kind": "image",
        "filename": "montreal_skyline_2026.jpg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Montreal%2C_Quebec_skyline.jpg",
        "source_page": "https://commons.wikimedia.org/wiki/File:Montreal,_Quebec_skyline.jpg",
        "credit": "Quintin Soloviev · CC BY 4.0",
        "use": "Montréal closing background. Photograph taken 2026-06-01; version 2026-08-08. Cropped with a white veil; no endorsement implied.",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "rights_status": "CC BY 4.0 as displayed on the file page; attribution, source/license link and modifications recorded.",
        "expected_sha256": "ee9599ea4c08af07386ab95c23acb55c297209db90517e38e1c771fa7a4b23e1",
    },
    {
        "kind": "image", "filename": "campus_central_uqam.jpg",
        "url": "https://salledepresse.uqam.ca/wp-content/uploads/sites/16/2022/01/J_hr.jpg",
        "source_page": UQAM_PAVILION_PHOTO_LIBRARY, "credit": "Photo : UQAM",
        "use": "Legacy campus identity photo, decoded as 1302 by 930 pixels. Do not enlarge to full-screen 1080p; the revised promo uses the science building.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "classroom_math.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2025/05/finale-aqjm-w.jpg",
        "source_page": "https://actualites.uqam.ca/2025/competition-de-mathematiques-a-luqam/",
        "credit": "Mireille Soboya",
        "use": "Legacy shared asset retained for reproducibility of older UQAM builds; do not use as the opening image for new evergreen promotional films.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "francois_bergeron.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2022/01/francois-bergeron-8400-w.jpg",
        "source_page": "https://actualites.uqam.ca/2021/des-professeurs-en-direct-de-leur-studio/",
        "credit": "Nathalie St-Pierre",
        "use": "Legacy teaching portrait retained for historical builds; not used in the revised promo.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "lisa_berger.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2024/04/lisa-4143-w-1024x683.jpg",
        "source_page": "https://actualites.uqam.ca/2024/des-etudiantes-performantes-et-engagees/",
        "credit": "Nathalie St-Pierre",
        "use": "Legacy portrait explicitly removed from the revised promo; retained only for historical builds.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "research_math.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2023/03/pk-sb-pole-math-w.jpg",
        "source_page": "https://actualites.uqam.ca/2023/nouveau-pole-mathematiques-complexe-sciences-pierre-dansereau/",
        "credit": "Nathalie St-Pierre",
        "use": "Legacy posed group at the mathematics research hub; removed from both revised capsules.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "support_students.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2026/01/allo-kiosque-4577-w.jpg",
        "source_page": "https://actualites.uqam.ca/2026/programme-allo-elargit-programmation/",
        "credit": "Nathalie St-Pierre",
        "use": "General UQAM new-student welcome/support atmosphere. The Allô! programme expanded to all new UQAM students in 2026; the image is not presented as a literal photo of the Faculty peer-mentoring programme.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "bibliotheque_sciences_2026.jpg",
        "url": "https://services-medias.uqam.ca/media/uploads/sites/4/2026/04/01104213/Image-e1783021536544.jpg",
        "source_page": "https://bibliotheques.uqam.ca/nouvelles/top-6-des-meilleurs-endroits-pour-etudier-aux-bibliotheques/",
        "credit": "Service des bibliothèques · UQAM",
        "use": "Current Bibliothèque des sciences study environment, 1024 by 538 pixels, bounded landscape panel only; replacing the 2021 open-house photograph with masked visitors.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "bibliotheque_sciences.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2022/01/uqampoaut2021-0957.jpg",
        "source_page": "https://actualites.uqam.ca/2021/portes-ouvertes-uqam-reussite/",
        "credit": "David Ospina",
        "use": "Legacy 2021 open-house/library asset retained for reproducibility; the pictured masked visitors make it unsuitable for new evergreen promo.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "sciences_biologiques_uqam.jpg",
        "url": "https://salledepresse.uqam.ca/wp-content/uploads/sites/16/2022/01/SB_hr-scaled.jpg",
        "source_page": UQAM_PAVILION_PHOTO_LIBRARY, "credit": "Photo : UQAM",
        "use": "Science-complex location image: pavillon des Sciences biologiques, used instead of the street-dominated Président-Kennedy exterior.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "president_kennedy.jpg",
        "url": "https://salledepresse.uqam.ca/wp-content/uploads/sites/16/2022/01/PK_hr-scaled.jpg",
        "source_page": UQAM_PAVILION_PHOTO_LIBRARY, "credit": "Photo : UQAM",
        "use": "Legacy street-heavy Président-Kennedy exterior retained because older UQAM builds reference it; do not select it for new promo location shots.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "international_students.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2025/03/pause-internationale-w.jpg",
        "source_page": "https://actualites.uqam.ca/2025/un-espace-accueillant-pour-les-etudiantes-et-etudiants-internationaux/",
        "credit": "Faculté des sciences", "use": "International-student community and support.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "allo_pk.jpg",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2025/11/local-allo-pk.jpg",
        "source_page": "https://actualites.uqam.ca/2025/nouveau-local-allo-complexe-sciences-pierre-dansereau/",
        "credit": "Programme d'accueil de la communauté étudiante internationale – Allô!",
        "use": "Allô! student-support space inside the science complex.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "font", "filename": "fonts/Roboto-VariableFont_wdth,wght.ttf",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/Roboto%5Bwdth%2Cwght%5D.ttf",
        "source_page": "https://github.com/google/fonts/tree/main/ofl/roboto",
        "credit": "Roboto contributors", "use": "Deterministically registered UQAM typography.",
        "license": "SIL Open Font License 1.1",
    },
    {
        "kind": "license", "filename": "fonts/OFL.txt",
        "url": "https://raw.githubusercontent.com/google/fonts/main/ofl/roboto/OFL.txt",
        "source_page": "https://github.com/google/fonts/tree/main/ofl/roboto",
        "credit": "Roboto contributors", "use": "Roboto license text.",
        "license": "SIL Open Font License 1.1",
    },
]


def looks_like_image(data: bytes) -> bool:
    return (
        data.startswith(b"\xff\xd8\xff")
        or data.startswith(b"\x89PNG\r\n\x1a\n")
        or (data.startswith(b"RIFF") and b"WEBP" in data[:16])
    )


def validate_bytes(kind: str, data: bytes, content_type: str = "") -> None:
    if not data:
        raise RuntimeError("empty response")
    if kind == "image" and not looks_like_image(data):
        raise RuntimeError(f"response is not a supported image ({content_type!r})")
    if kind == "font" and not (data.startswith(b"\x00\x01\x00\x00") or data.startswith(b"OTTO")):
        raise RuntimeError("response is not a supported OpenType/TrueType font")
    if kind == "license" and b"SIL OPEN FONT LICENSE" not in data.upper():
        raise RuntimeError("response is not the expected font license")


def download_atomic(item: dict[str, str], destination: Path) -> int:
    request = urllib.request.Request(
        item["url"], headers={"User-Agent": "Mozilla/5.0 (Xia_video UQAM promo asset fetcher)"}
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    validate_bytes(item["kind"], data, content_type)
    if item.get("expected_sha256") and hashlib.sha256(data).hexdigest() != item["expected_sha256"]:
        raise RuntimeError("Downloaded asset differs from the pinned editorial version")
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=destination.name + ".", dir=str(destination.parent))
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
        Path(temporary_name).replace(destination)
    finally:
        temporary = Path(temporary_name)
        if temporary.exists():
            temporary.unlink()
    return len(data)


def inspect_asset(item: dict[str, str], asset_dir: Path) -> dict[str, object]:
    path = asset_dir / item["filename"]
    result: dict[str, object] = dict(item)
    if not path.is_file():
        result["status"] = "missing"
        return result
    data = path.read_bytes()
    validate_bytes(item["kind"], data)
    if item.get("expected_sha256") and hashlib.sha256(data).hexdigest() != item["expected_sha256"]:
        raise RuntimeError("Local asset differs from the pinned editorial version")
    result.update({"status": "present", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    if item["kind"] == "image":
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            result["dimensions"] = {"width": image.width, "height": image.height}
            result["format"] = image.format
    return result


def inventory(asset_dir: Path) -> list[dict[str, object]]:
    return [inspect_asset(item, asset_dir) for item in ASSETS]


def write_manifest(asset_dir: Path, records: list[dict[str, object]]) -> None:
    asset_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": 1,
        "purpose": "Inspected download inventory for the two UQAM introductory films; not a list of committed binaries",
        "assets": records,
    }
    (asset_dir / "sources.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# UQAM introductory-film asset inventory", "",
        "The user directed inclusion of these UQAM-published photographs for this project.",
        "This is the inspected local download inventory, not a claim that all binaries are tracked by Git.",
        "Run the asset fetcher before rendering. Formal republication permission for UQAM photos is not inferred.", "",
    ]
    for record in records:
        lines.extend([
            f"## {record['filename']}", f"- Type: {record['kind']}",
            f"- Source page: {record['source_page']}", f"- Direct source: {record['url']}",
            f"- Credit: {record['credit']}", f"- Intended use: {record['use']}",
        ])
        for field, label in (("authorization_basis", "Authorization basis"), ("rights_status", "Rights status"),
                             ("license", "License"), ("license_url", "License URL")):
            if field in record:
                lines.append(f"- {label}: {record[field]}")
        lines.append(f"- Status: {record['status']}")
        if record["status"] == "present":
            dimensions = record.get("dimensions")
            if dimensions:
                lines.append(f"- Dimensions: {dimensions['width']} × {dimensions['height']}")
            lines.extend([f"- Bytes: {record['bytes']}", f"- SHA-256: `{record['sha256']}`"])
        lines.append("")
    (asset_dir / "SOURCES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="redownload existing files")
    parser.add_argument("--list", action="store_true", help="list assets without downloading")
    parser.add_argument("--check", action="store_true", help="validate local assets without downloading")
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    args = parser.parse_args()
    if args.list:
        for item in ASSETS:
            print(f"{item['filename']}: {item['source_page']}")
        return 0
    asset_dir = args.asset_dir.resolve()
    failures: list[tuple[str, str]] = []
    if not args.check:
        for item in ASSETS:
            destination = asset_dir / item["filename"]
            if destination.exists() and destination.stat().st_size > 0 and not args.force:
                print(f"KEEP  {destination}")
                continue
            try:
                size = download_atomic(item, destination)
                print(f"GET   {destination} ({size:,} bytes)")
            except Exception as exc:
                failures.append((item["filename"], str(exc)))
                print(f"FAIL  {item['filename']}: {exc}")
    records: list[dict[str, object]] = []
    for item in ASSETS:
        try:
            record = inspect_asset(item, asset_dir)
            if record["status"] != "present":
                failures.append((item["filename"], "missing"))
            records.append(record)
        except Exception as exc:
            failures.append((item["filename"], str(exc)))
            records.append({**item, "status": "invalid", "error": str(exc)})
    if not args.check:
        write_manifest(asset_dir, records)
    if failures:
        for filename, reason in failures:
            print(f"INVALID {filename}: {reason}")
        return 1
    print(f"Validated {len(records)} assets in {asset_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
