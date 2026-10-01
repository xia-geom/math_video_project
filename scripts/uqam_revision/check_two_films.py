"""Check the actual encoded review timelines; no claim of listening or release approval."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate_math_timeline(timeline: dict) -> None:
    states = {item["state"]: item for item in timeline["states"]}
    units = timeline["speech_units"]
    research = states["research_cards"]
    descriptions = [u for u in units if u["segment"] == "research" and u["index"] > 0]
    if len(descriptions) != 3 or research["end"] - research["start"] < 11.95:
        raise ValueError("All three centres must remain readable for at least twelve seconds")
    if not all(
        research["start"] - 0.03 <= u["start"] < u["speech_end"] <= research["end"] + 0.03
        for u in descriptions
    ):
        raise ValueError("Research cards leave before their spoken descriptions end")
    intro = next(item for item in timeline["layout"] if item["context"] == "research_intro")
    if any(name in label["text"] for name in ("CIRGET", "LaCIM", "STATQAM") for label in intro["labels"]):
        raise ValueError("The introductory research shot must not flash the acronym grid")
    if not any(
        "STATQAM développe la recherche en statistique et en science des données." == u["text"]
        for u in descriptions
    ):
        raise ValueError("The actual spoken units omit the STATQAM description")
    closing = next(u for u in units if u["segment"] == "close" and u["index"] == 4)
    if states["closing_cta"]["end"] - closing["speech_end"] < 2.75:
        raise ValueError("The final call to action disappears too quickly")
    for filename in ("lisa_berger.jpg", "classroom_math.jpg", "research_math.jpg"):
        if any(s["filename"] == filename for s in timeline["shots"]):
            raise ValueError(f"Rejected photograph returned: {filename}")
    city = next(a for a in timeline["acts"] if a["act"] == "montreal")
    campus = next(s for s in timeline["shots"] if s["filename"] == "sciences_biologiques_uqam.jpg" and s["start"] >= city["start"] - 0.03)
    spoken_city = next(u for u in units if u["segment"] == "montreal" and u["index"] == 0)
    if campus["end"] < spoken_city["speech_end"]:
        raise ValueError("The campus photograph disappears before its description ends")
    if not any(s["filename"] == "montreal_skyline_2026.jpg" for s in timeline["shots"]):
        raise ValueError("Montréal is absent from the conclusion")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sciences", type=Path)
    parser.add_argument("maths", type=Path)
    args = parser.parse_args()
    sciences = json.loads((args.sciences / "manifest.json").read_text())
    maths = json.loads((args.maths / "manifest.json").read_text())
    timeline = json.loads((args.maths / "timeline.json").read_text())
    if sciences["duration_seconds"] > 30 or sciences["timeline_checks"]["final_reading_hold_seconds"] < 1.96:
        raise ValueError("Sciences duration or closing hold violates the brief")
    validate_math_timeline(timeline)
    if sciences["mode"] != "silent" or maths["mode"] != "visual_only_no_audio":
        raise ValueError("These checks are for explicitly silent review outputs")
    result = {"science_seconds": sciences["duration_seconds"], "maths_seconds": maths["duration_seconds"],
              "editorial_timeline_checks": "passed", "listening_review": "not_performed", "release_ready": False}
    (args.sciences.parent / "two_films_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
