# Ame-Artificielle/src/interpolation.py
from __future__ import annotations

from typing import Dict, Mapping, Optional

TraitVector = Dict[str, float]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation: (1-t)*a + t*b."""
    t = clamp(t)
    return (1.0 - t) * a + t * b


def blend_vectors(a: Mapping[str, float], b: Mapping[str, float], t: float) -> TraitVector:
    """
    Blend two trait vectors key-wise. Missing keys are treated as 0.0.
    t=0 -> a, t=1 -> b.
    """
    t = clamp(t)
    keys = set(a.keys()) | set(b.keys())
    out: TraitVector = {}
    for k in keys:
        out[k] = lerp(float(a.get(k, 0.0)), float(b.get(k, 0.0)), t)
    return out


def add_scaled(base: Mapping[str, float], overlay: Mapping[str, float], scale: float) -> TraitVector:
    """Return base + scale*overlay (key-wise)."""
    out: TraitVector = dict(base)
    for k, v in overlay.items():
        out[k] = float(out.get(k, 0.0)) + float(v) * float(scale)
    return out


def normalize_l1(v: Mapping[str, float], target_sum: float = 1.0) -> TraitVector:
    """
    L1 normalize by absolute sum. Useful when you want vectors comparable
    across profiles. If the vector is all zeros, returns a copy unchanged.
    """
    s = sum(abs(float(x)) for x in v.values())
    if s <= 1e-12:
        return dict(v)
    scale = float(target_sum) / s
    return {k: float(x) * scale for k, x in v.items()}


def axis_position(axis_digit: int) -> float:
    """
    Map axis_digit in [1..9] to a continuous position t in [0..1].
    Convention: 1 -> intellect pole, 9 -> instinct pole.
      t_instinct = (d-1)/8
      t_intellect = 1 - t_instinct
    """
    if not isinstance(axis_digit, int):
        raise TypeError("axis_digit must be an int in [1..9]")
    if axis_digit < 1 or axis_digit > 9:
        raise ValueError("axis_digit must be in [1..9]")
    return (axis_digit - 1) / 8.0


def interpolate_axis(
    *,
    axis_digit: int,
    intellect: Mapping[str, float],
    instinct: Mapping[str, float],
    mid_overlays: Optional[Mapping[int, Mapping[str, float]]] = None,
    mid_strength: float = 0.25,
    normalize: bool = False,
) -> TraitVector:
    """
    Interpolate between intellect (axis=1) and instinct (axis=9) templates.

    Optionally, apply a digit-specific overlay for digits 2..8 to represent
    "emotion / myth / event" modulation (your matrix middle band).

    Parameters
    ----------
    axis_digit:
        1..9 where 1 is intellect pole and 9 is instinct pole.
    intellect, instinct:
        Trait templates (dict-like) for the two poles.
    mid_overlays:
        Dict keyed by digit (typically 2..8) mapping to overlay vectors.
        Example: {2: {...}, 3: {...}, ..., 8: {...}}
    mid_strength:
        Scaling factor applied when an overlay exists for axis_digit.
    normalize:
        If True, L1-normalize the output vector.

    Returns
    -------
    TraitVector
        The blended (and optionally modulated) trait vector.
    """
    t_instinct = axis_position(axis_digit)
    base = blend_vectors(intellect, instinct, t_instinct)

    if mid_overlays and axis_digit in mid_overlays:
        base = add_scaled(base, mid_overlays[axis_digit], mid_strength)

    if normalize:
        base = normalize_l1(base, target_sum=1.0)

    return base
