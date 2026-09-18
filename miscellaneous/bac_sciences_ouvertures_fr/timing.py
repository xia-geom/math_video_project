"""Frame-exact, audio-first scheduling for this 20-second film only.

The original four scene durations are preferences, not independent floors.
No speech is shortened, resampled, accelerated, or silently regenerated.
"""
from __future__ import annotations

import math


class TimingBudgetError(ValueError):
    """Keep per-beat evidence available even when no frame is rendered."""

    def __init__(self, report: dict):
        self.report = report
        excess = report["required_seconds"] - report["target_seconds"]
        super().__init__(
            f"Narration plus reading/transition time exceeds the target by {excess:.3f}s. "
            "Shorten the indicated copy or explicitly approve a longer film; "
            "no speech was cut, sped up, or regenerated."
        )


def _frames(seconds: float, fps: int) -> int:
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError("Durations must be finite and nonnegative")
    return math.ceil(seconds * fps - 1e-8)


def plan_timeline(spec: dict, durations: list[float] | None, fps: int) -> dict:
    """Allocate a fixed total of frames after all four clips are measured.

    Silence can be redistributed; actual audio and minimum reading time cannot.
    Fractions are rounded upward for safety, never downward into speech.
    """
    if isinstance(fps, bool) or not isinstance(fps, int) or fps <= 0:
        raise ValueError("Expected a positive integer frame rate")
    beats = spec["beats"]
    target = float(spec["target_seconds"])
    total = round(target * fps)
    if abs(total / fps - target) > 1e-8:
        raise ValueError("Target must be an exact number of frames")
    if durations is not None and len(durations) != len(beats):
        raise ValueError("Measure exactly one audio clip for each beat")
    lead = _frames(spec["timing"]["lead_seconds"], fps)
    tails = [_frames(b["tail_seconds"], fps) for b in beats]
    preferred = [_frames(float(b["seconds"]), fps) for b in beats]
    if sum(preferred) != total:
        raise ValueError("Silent storyboard must sum to the exact target")
    speech = None if durations is None else [_frames(float(n), fps) for n in durations]
    minimum = [
        max(_frames(b["minimum_seconds"], fps), lead + tails[i] + (speech[i] if speech else 0))
        for i, b in enumerate(beats)
    ]
    report = {
        "policy": "audio_first_global_v1", "fps": fps, "target_seconds": target,
        "target_frames": total, "required_seconds": sum(minimum) / fps,
        "speech_seconds": None if speech is None else sum(durations),
        "beats": [
            {"id": b["id"], "speech_seconds": None if durations is None else durations[i],
             "minimum_frames": minimum[i], "preferred_frames": preferred[i]}
            for i, b in enumerate(beats)
        ],
    }
    if sum(minimum) > total:
        report["status"] = "rejected_before_render"
        raise TimingBudgetError(report)
    slots = minimum[:]
    # First approach the authored storyboard; then put spare time on the end card.
    for _ in range(total - sum(slots)):
        deficits = [preferred[i] - slots[i] for i in range(len(slots))]
        index = max(range(len(slots)), key=lambda i: (deficits[i], i))
        if deficits[index] <= 0:
            index = len(slots) - 1
        slots[index] += 1
    if durations is None:
        slots = preferred
    start = 0
    for i, b in enumerate(beats):
        row = report["beats"][i]
        row.update({
            "start_frame": start, "end_frame": start + slots[i],
            "start": start / fps, "end": (start + slots[i]) / fps,
            "lead_frames": lead, "tail_frames": tails[i], "caption": b["caption"],
            "speech_start": None if speech is None else (start + lead) / fps,
            "speech_end": None if speech is None else (start + lead) / fps + durations[i],
        })
        start += slots[i]
    report["status"] = "planned"
    return report
