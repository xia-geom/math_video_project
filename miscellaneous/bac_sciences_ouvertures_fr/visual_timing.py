"""Pure timing and compositing helpers for the sparse photo-led film."""
from __future__ import annotations


def ease(value: float) -> float:
    """Cubic easing with no velocity discontinuity at either end."""
    x = max(0.0, min(1.0, value))
    return x * x * (3.0 - 2.0 * x)


def dissolve_opacities(progress: float) -> tuple[float, float]:
    """Keep the lower photo opaque: source-over then preserves total exposure.

    At the midpoint, two simultaneous fades produce weights 1/4 and 1/2,
    exposing black. An opaque lower layer instead produces weights 1/2, 1/2.
    """
    return 1.0, ease(progress)


def copy_opacities(elapsed: float, opening: bool = False) -> tuple[float, float]:
    """Never superimpose two messages; incoming copy follows the outgoing fade."""
    if opening:
        return 0.0, ease(elapsed / 0.55)
    return 1.0 - ease(elapsed / 0.28), ease((elapsed - 0.38) / 0.42)


def shot_plan(beat: dict, start: float, slot: float) -> list[dict]:
    """Expand visual inserts without changing a beat's narration or duration."""
    keys = beat.get("photos", [beat["background"]])
    length = slot / len(keys)
    return [
        {"key": key, "start": start + i * length,
         "end": start + (i + 1) * length, "beat": beat["id"]}
        for i, key in enumerate(keys)
    ]
