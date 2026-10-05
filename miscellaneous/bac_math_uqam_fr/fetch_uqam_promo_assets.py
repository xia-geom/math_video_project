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
REVIEW_CANDIDATE_AUTHORIZATION = (
    "User editorial selection confirmed 2026-10-03; authorized for the requested "
    "review renders. Institutional publication clearance is separate and not inferred."
)
REVIEW_CANDIDATE_RIGHTS = (
    "Official UQAM source and stated credit documented; formal promotional "
    "republication permission not independently verified."
)
OCTOBER_4_AUTHORIZATION = (
    "User selected these images and requested localized retouching on 2026-10-04 "
    "for the maths capsule's editorial review. Institutional publication "
    "clearance is separate and not inferred."
)
DERIVATIVE_METHOD = (
    "imagegen localized generated-patch composition preserving untouched regions"
)

ASSETS: list[dict[str, str]] = [
    {
        "kind": "image", "filename": "ludopolis_2026.jpg", "candidate_id": "M1",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2026/01/grande-rentree-h26-5696.jpg",
        "source_page": "https://actualites.uqam.ca/2026/rentree-hivernale-festive/",
        "credit": "Nathalie St-Pierre",
        "display_credit": "Photo : Nathalie St-Pierre · Ludopolis, 2026",
        "use": "Selected for the maths film's welcoming-community opening. Ludopolis game break in the Sciences biologiques pavilion hall, January 2026. Participants and facilitators are not identified as mathematics students; not a class or mentoring session.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-03",
        "authorization_basis": REVIEW_CANDIDATE_AUTHORIZATION,
        "rights_status": REVIEW_CANDIDATE_RIGHTS,
        "expected_sha256": "86c65f740bc359be7beaf4375d63b45bf7dd11ae477a221414c36b12d66ddd27",
    },
    {
        "kind": "image", "filename": "accueil_hiver_2026.jpg", "candidate_id": "M3",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2026/01/grande-rentree-5527.jpg",
        "source_page": "https://actualites.uqam.ca/2026/rentree-hivernale-festive/",
        "credit": "Nathalie St-Pierre",
        "display_credit": "Photo : Nathalie St-Pierre · rentrée, 2026",
        "use": "Selected for the maths film's campus-community scene. Soup and hot-drink exchange during the January 2026 winter welcome at the campus central. Not a teacher exchange, mathematics class or peer-mentoring activity.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-03",
        "authorization_basis": REVIEW_CANDIDATE_AUTHORIZATION,
        "rights_status": REVIEW_CANDIDATE_RIGHTS,
        "expected_sha256": "b91e4ae71f0e774e13114a92a89b87569d532d0a52b1e09bb5abbfbf5022485d",
    },
    {
        "kind": "image", "filename": "northsec_2026.jpg", "candidate_id": "S1",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2026/05/northsec-2026-w-v2.jpg",
        "source_page": "https://actualites.uqam.ca/2026/northsec-2026-uqam-hubert-hackin/",
        "credit": "Jean Privat",
        "display_credit": "Photo : Jean Privat · NorthSec, 2026",
        "use": "Selected for the interdisciplinary film's computer-team image. Hubert Hackin’ at the NorthSec 2026 cybersecurity competition in Montréal. Mixed students, graduates, professors and colleagues, including an ÉTS member; not a UQAM undergraduate class or a group wholly enrolled in a single programme.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-03",
        "authorization_basis": REVIEW_CANDIDATE_AUTHORIZATION,
        "rights_status": REVIEW_CANDIDATE_RIGHTS,
        "expected_sha256": "f58fe5ad9f8f8dcd8fbc8b02d0f605c75f8a58f882f62f754f87c12d55453cfd",
    },
    {
        "kind": "image", "filename": "metamorphose_2024.jpg", "candidate_id": "S2",
        "url": "https://services-medias.uqam.ca/media/uploads/sites/4/2025/01/15094747/metamorphose-4.jpg",
        "source_page": "https://bibliotheques.uqam.ca/nouvelles/propositions-etudiantes-pour-metamorphose/",
        "credit": "Jérôme Bélanger, Rosalie Chrétien et Noémie Poirier Monfette",
        "credit_scope": "Collective gallery credit; the photographer of this individual image is not identified on the inspected source page.",
        "display_credit": "Photos : équipe Métamorphose",
        "use": "Selected for the interdisciplinary film's student-project image. Two smiling presenters beside design boards from the autumn 2024 Métamorphose library-space projects, reported in January 2025. Posed presentation, not active discussion; not evidence of a mathematics project or a BSc-by-accumulation pathway. Full gallery credit must accompany the abbreviated on-screen credit.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-03",
        "authorization_basis": REVIEW_CANDIDATE_AUTHORIZATION,
        "rights_status": REVIEW_CANDIDATE_RIGHTS + " The library website's CC BY terms for identified text do not establish a license for this photograph.",
        "expected_sha256": "39c86c91da5145ef255d58b1405346432c8cdf847230d76a0098882ec2b852ee",
    },
    {
        "kind": "image", "filename": "bouturage_2026.jpg", "candidate_id": "S3",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2026/01/grande-rentree-h26-5480.jpg",
        "source_page": "https://actualites.uqam.ca/2026/rentree-hivernale-festive/",
        "credit": "Nathalie St-Pierre",
        "display_credit": "Photo : Nathalie St-Pierre · rentrée, 2026",
        "use": "Selected for the interdisciplinary film's campus-community conclusion. Participants handle plants together during a January 2026 winter-welcome plant-cutting activity. Not a biology course, laboratory, or evidence of a specific degree pathway.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-03",
        "authorization_basis": REVIEW_CANDIDATE_AUTHORIZATION,
        "rights_status": REVIEW_CANDIDATE_RIGHTS,
        "expected_sha256": "20449bc5ea3b96c788da851af206738c9dcc81954e2af486c2410f23be3cef7c",
    },
    {
        "kind": "image",
        "filename": "math_workshop_2019.jpg",
        "candidate_id": "M2",
        "url": "https://actualites.uqam.ca/wp-content/uploads/2022/01/ateliers-scientifiques-4633-002.jpg",
        "source_page": "https://actualites.uqam.ca/2019/4-a-6-des-sciences-ateliers-gratuits-grand-public/",
        "credit": "Nathalie St-Pierre",
        "use": "Public mathematics workshop in 2019, not a regular undergraduate class. Limited to a 1000-pixel panel; never full-bleed at 1080p.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-03",
        "authorization_basis": REVIEW_CANDIDATE_AUTHORIZATION,
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
        "use": "User-selected opening for the October 4 maths revision. Président-Kennedy building and reflection with mathematical formulas; an architectural composite, not a posed group or a photograph of a research discussion.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-04",
        "authorization_basis": OCTOBER_4_AUTHORIZATION, "rights_status": RIGHTS_STATUS,
        "expected_sha256": "56de3054dbcbb6c7919fd25989883b0bc495673693b984f1965e201717f2f8ea",
    },
    {
        "kind": "image", "filename": "programmes_doubles_diplomes_autres_activites.jpg",
        "url": "https://fspd.uqam.ca/wp-content/uploads/sites/9/programmes_doubles_diplomes_autres_activites.jpg",
        "source_page": "https://fspd.uqam.ca/",
        "credit": "UQAM · Faculté de science politique et de droit",
        "credit_scope": "Source institution identified; individual photographer unspecified. Do not invent a photographer credit.",
        "use": "User-selected smiling-student campus-community illustration. Outdoor discussion on steps; 1200 by 675 pixels, bounded panel only. The source does not establish that the people study mathematics or take part in mentoring.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-04",
        "authorization_basis": OCTOBER_4_AUTHORIZATION, "rights_status": RIGHTS_STATUS,
        "expected_sha256": "b7400d0be0b3f2619c60dcb5bd0eea5b8868460f5dc6055f2b77356467b96439",
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
        "kind": "image", "filename": "redaction_sciences_2026.jpg",
        "url": "https://services-medias.uqam.ca/media/uploads/sites/4/2026/09/02145643/thesezvous.jpg",
        "source_page": "https://bibliotheques.uqam.ca/soutien-recherche-creation/seances-de-redaction-collective/",
        "credit": "Service des bibliothèques · UQAM",
        "use": "Students writing together at the Bibliothèque des sciences (KI-1100), autumn 2026; 1500 by 1125 pixels, bounded panel only.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "redaction_sciences_2026_no_red_bag.png",
        "retrieval": "local_derivative",
        "url": "https://services-medias.uqam.ca/media/uploads/sites/4/2026/09/02145643/thesezvous.jpg",
        "source_page": "https://bibliotheques.uqam.ca/soutien-recherche-creation/seances-de-redaction-collective/",
        "credit": "Service des bibliothèques · UQAM",
        "use": "October 4 maths-library panel, held stable across both support takes. Localized removal of the red bag at lower right; people, furniture and untouched carpet remain from the original photograph.",
        "derived_from": "redaction_sciences_2026.jpg",
        "derived_from_sha256": "c174ecc87674fbfeccab500d101b74a57805852f281caf1afa2efbc60324adcd",
        "expected_sha256": "54c7b818b0ec9770658e7a356a9c6c04a7fd2bd2a8d9cce1d8314b1a18f8bdc3",
        "modifications": "Red bag removed; generated carpet patch composited locally into the original photograph.",
        "modification_date": "2026-10-04",
        "modification_method": DERIVATIVE_METHOD,
        "reproduction": "Retain the approved local PNG and its pinned SHA-256. The URL retrieves only the untouched original, not this derivative. Restore the reviewed derivative from the versioned delivery; generating it again is not byte-reproducible.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-04",
        "authorization_basis": OCTOBER_4_AUTHORIZATION, "rights_status": RIGHTS_STATUS,
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
        "use": "Legacy unretouched Président-Kennedy exterior retained as the original source for the explicitly selected October 4 vehicle-removal derivative and for historical builds. The original vehicle-heavy image is not used in the new maths montage.",
        "authorization_basis": AUTHORIZATION_BASIS, "rights_status": RIGHTS_STATUS,
    },
    {
        "kind": "image", "filename": "president_kennedy_no_vehicles.png",
        "retrieval": "local_derivative",
        "url": "https://salledepresse.uqam.ca/wp-content/uploads/sites/16/2022/01/PK_hr-scaled.jpg",
        "source_page": UQAM_PAVILION_PHOTO_LIBRARY, "credit": "Photo : UQAM",
        "use": "User-selected October 4 maths location shot, replacing the Sciences biologiques pavilion photograph. Trucks and cars removed locally; preserve pedestrians, architecture, signage, lighting and untouched street surfaces.",
        "derived_from": "president_kennedy.jpg",
        "derived_from_sha256": "8e442e05872533317e8ee3c8191ee6b5a3d601914761ce664aaa71854c94ddee",
        "expected_sha256": "2f1ac03611e32bf7e58433a027cb653d6697923601284ff0f8a64772001d59da",
        "modifications": "Trucks and cars removed; generated patches composited locally into the original photograph.",
        "modification_date": "2026-10-04",
        "modification_method": DERIVATIVE_METHOD,
        "reproduction": "Retain the approved local PNG and its pinned SHA-256. The URL retrieves only the untouched original, not this derivative. Restore the reviewed derivative from the versioned delivery; generating it again is not byte-reproducible.",
        "selection_status": "user_editorial_selection_confirmed_2026-10-04",
        "authorization_basis": OCTOBER_4_AUTHORIZATION, "rights_status": RIGHTS_STATUS,
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
    if item.get("retrieval") == "local_derivative":
        raise RuntimeError("Local retouched assets cannot be downloaded from the original source URL; "
                           "restore the approved derivative from its versioned delivery")
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
    if item.get("retrieval") == "local_derivative":
        original = asset_dir / item["derived_from"]
        if not original.is_file():
            raise RuntimeError("Retouched asset's original is missing")
        if hashlib.sha256(original.read_bytes()).hexdigest() != item["derived_from_sha256"]:
            raise RuntimeError("Retouched asset's original differs from the recorded lineage")
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
        "purpose": "Inspected source and local-derivative inventory for the two UQAM introductory films; not a list of committed binaries",
        "assets": records,
    }
    (asset_dir / "sources.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# UQAM introductory-film asset inventory", "",
        "This inventory includes production assets and candidates; each record states its authorization and selection status.",
        "This is the inspected local source and derivative inventory, not a claim that all binaries are tracked by Git.",
        "Run the asset fetcher before rendering. Formal republication permission for UQAM photos is not inferred.", "",
        "Local retouched PNGs are never downloaded from an original-photo URL, including with `--force`.",
        "Restore their reviewed bytes from the versioned delivery and verify the pinned SHA-256; generative edits are not byte-reproducible.", "",
    ]
    for record in records:
        lines.extend([
            f"## {record['filename']}", f"- Type: {record['kind']}",
            f"- Source page: {record['source_page']}",
            f"- {'Untouched original source' if record.get('retrieval') == 'local_derivative' else 'Direct source'}: {record['url']}",
            f"- Credit: {record['credit']}", f"- Intended use: {record['use']}",
        ])
        for field, label in (("candidate_id", "Candidate ID"), ("selection_status", "Editorial selection"),
                             ("display_credit", "Proposed on-screen credit"), ("credit_scope", "Credit scope"),
                             ("authorization_basis", "Authorization basis"), ("rights_status", "Rights status"),
                             ("license", "License"), ("license_url", "License URL"),
                             ("retrieval", "Retrieval mode"), ("derived_from", "Original filename"),
                             ("derived_from_sha256", "Original SHA-256"),
                             ("modifications", "Modifications"), ("modification_date", "Modification date"),
                             ("modification_method", "Modification method"), ("reproduction", "Reproduction")):
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
    local_mode = parser.add_mutually_exclusive_group()
    local_mode.add_argument("--check", action="store_true", help="validate local assets without downloading")
    local_mode.add_argument("--manifest-only", action="store_true",
                            help="inspect local assets and regenerate the inventory without downloading")
    parser.add_argument("--asset-dir", type=Path, default=DEFAULT_ASSET_DIR)
    args = parser.parse_args()
    if args.list:
        for item in ASSETS:
            print(f"{item['filename']}: {item['source_page']}")
        return 0
    asset_dir = args.asset_dir.resolve()
    failures: list[tuple[str, str]] = []
    if not args.check and not args.manifest_only:
        for item in ASSETS:
            destination = asset_dir / item["filename"]
            if item.get("retrieval") == "local_derivative":
                print(f"LOCAL {destination} (retouched asset; never downloaded or overwritten)")
                continue
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
