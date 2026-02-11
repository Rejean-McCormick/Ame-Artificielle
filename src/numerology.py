# Ame-Artificielle/src/numerology.py
"""
Numerology utilities (Pythagorean + optional inversion).

Core idea:
- Compute Pythagorean values (1..9) from names / dates.
- Reduce to a single digit (or keep master numbers if configured).
- Apply inversion mapping (9 -> 1, 1 -> 9, ..., 5 -> 5) when requested.

Conventions:
- inv(0)=0
- inv(d)=10-d for d in 1..9
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
import unicodedata
from typing import Dict, Iterable, List, Optional, Tuple, Union


@dataclass(frozen=True)
class NumerologyConfig:
    """
    Configuration for numerology reductions.
    - keep_master_numbers: master numbers that should not be reduced (e.g., 11, 22, 33).
    - apply_inversion: whether to output inverted digit(s) in the helpers that support it.
    """
    keep_master_numbers: Tuple[int, ...] = (11, 22, 33)
    apply_inversion: bool = True


# -------------------------
# Normalization helpers
# -------------------------

def _strip_accents(s: str) -> str:
    # Convert accents to base chars: "É" -> "E"
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def normalize_name(name: str) -> str:
    """
    Normalize a human name for letter-to-number mapping:
    - strip accents
    - uppercase
    - keep letters A-Z only (remove spaces, hyphens, punctuation, digits)
    """
    s = _strip_accents(name).upper()
    return re.sub(r"[^A-Z]", "", s)


# -------------------------
# Core numeric transforms
# -------------------------

def invert_digit(d: int) -> int:
    """
    Inverted Pythagorean digit mapping:
    1<->9, 2<->8, 3<->7, 4<->6, 5->5, 0->0.
    """
    if d == 0:
        return 0
    if 1 <= d <= 9:
        return 10 - d
    raise ValueError(f"invert_digit expects 0..9, got {d}")


def sum_digits(n: int) -> int:
    return sum(int(ch) for ch in str(abs(n)))


def reduce_number(
    n: int,
    keep_master_numbers: Iterable[int] = (11, 22, 33),
    allow_zero: bool = False,
) -> int:
    """
    Reduce an integer to a single digit (1..9) by repeated digit-summing.
    Optionally keep master numbers (11, 22, 33) unreduced.

    If allow_zero=True, 0 reduces to 0; otherwise 0 is invalid.
    """
    if n == 0:
        if allow_zero:
            return 0
        raise ValueError("reduce_number got 0 but allow_zero=False")

    masters = set(keep_master_numbers)

    x = abs(n)
    while True:
        if x in masters:
            return x
        if x < 10:
            return x
        x = sum_digits(x)


# -------------------------
# Pythagorean letter mapping
# -------------------------

# Standard Pythagorean numerology: A=1..I=9, J=1..R=9, S=1..Z=8
_PYTHAGOREAN_MAP: Dict[str, int] = {
    **{ch: val for ch, val in zip("ABCDEFGHI", range(1, 10))},
    **{ch: val for ch, val in zip("JKLMNOPQR", range(1, 10))},
    **{ch: val for ch, val in zip("STUVWXYZ", list(range(1, 9)))},
}

_VOWELS = set("AEIOUY")


def pythagorean_letter_value(ch: str) -> int:
    ch = ch.upper()
    if ch not in _PYTHAGOREAN_MAP:
        raise ValueError(f"Unsupported character for mapping: {ch!r}")
    return _PYTHAGOREAN_MAP[ch]


def name_total(name: str) -> int:
    """
    Total (unreduced) Pythagorean value for a name (letters A-Z only after normalization).
    """
    n = normalize_name(name)
    return sum(pythagorean_letter_value(ch) for ch in n)


def name_total_vowels(name: str) -> int:
    n = normalize_name(name)
    return sum(pythagorean_letter_value(ch) for ch in n if ch in _VOWELS)


def name_total_consonants(name: str) -> int:
    n = normalize_name(name)
    return sum(pythagorean_letter_value(ch) for ch in n if ch not in _VOWELS)


# -------------------------
# Date-based numbers
# -------------------------

DateInput = Union[date, datetime, str, Tuple[int, int, int]]


def _parse_date(d: DateInput) -> date:
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    if isinstance(d, tuple) and len(d) == 3:
        y, m, day = d
        return date(int(y), int(m), int(day))
    if isinstance(d, str):
        # Accept "YYYY-MM-DD" (preferred) and "YYYY/MM/DD"
        s = d.strip().replace("/", "-")
        return date.fromisoformat(s)
    raise TypeError(f"Unsupported date input: {type(d)}")


def life_path_number(dob: DateInput, cfg: NumerologyConfig = NumerologyConfig()) -> Dict[str, int]:
    """
    Life Path:
    Sum digits of full date of birth (YYYYMMDD) then reduce.

    Returns both:
    - pythagorean (reduced/master)
    - inverted (if cfg.apply_inversion and reduced is 1..9)
    """
    dt = _parse_date(dob)
    digits = f"{dt.year:04d}{dt.month:02d}{dt.day:02d}"
    total = sum(int(ch) for ch in digits)
    reduced = reduce_number(total, keep_master_numbers=cfg.keep_master_numbers, allow_zero=False)

    out = {"total": total, "pythagorean": reduced}
    if cfg.apply_inversion and 1 <= reduced <= 9:
        out["inverted"] = invert_digit(reduced)
    return out


def birth_day_number(dob: DateInput, cfg: NumerologyConfig = NumerologyConfig()) -> Dict[str, int]:
    """
    Day number: reduce the day-of-month.
    """
    dt = _parse_date(dob)
    reduced = reduce_number(dt.day, keep_master_numbers=cfg.keep_master_numbers, allow_zero=False)

    out = {"pythagorean": reduced}
    if cfg.apply_inversion and 1 <= reduced <= 9:
        out["inverted"] = invert_digit(reduced)
    return out


# -------------------------
# Name-based core numbers
# -------------------------

def expression_number(name: str, cfg: NumerologyConfig = NumerologyConfig()) -> Dict[str, int]:
    """
    Expression / Destiny number: reduce full name total.
    """
    total = name_total(name)
    reduced = reduce_number(total, keep_master_numbers=cfg.keep_master_numbers, allow_zero=False)

    out = {"total": total, "pythagorean": reduced}
    if cfg.apply_inversion and 1 <= reduced <= 9:
        out["inverted"] = invert_digit(reduced)
    return out


def soul_urge_number(name: str, cfg: NumerologyConfig = NumerologyConfig()) -> Dict[str, int]:
    """
    Soul Urge / Heart's Desire: reduce vowel total.
    """
    total = name_total_vowels(name)
    if total == 0:
        # Some names might have no vowels after normalization (rare). Keep safe behavior.
        reduced = 0
    else:
        reduced = reduce_number(total, keep_master_numbers=cfg.keep_master_numbers, allow_zero=False)

    out = {"total": total, "pythagorean": reduced}
    if cfg.apply_inversion and 1 <= reduced <= 9:
        out["inverted"] = invert_digit(reduced)
    return out


def personality_number(name: str, cfg: NumerologyConfig = NumerologyConfig()) -> Dict[str, int]:
    """
    Personality number: reduce consonant total.
    """
    total = name_total_consonants(name)
    if total == 0:
        reduced = 0
    else:
        reduced = reduce_number(total, keep_master_numbers=cfg.keep_master_numbers, allow_zero=False)

    out = {"total": total, "pythagorean": reduced}
    if cfg.apply_inversion and 1 <= reduced <= 9:
        out["inverted"] = invert_digit(reduced)
    return out


# -------------------------
# Combined signature
# -------------------------

def build_signature(
    name: Optional[str] = None,
    dob: Optional[DateInput] = None,
    cfg: NumerologyConfig = NumerologyConfig(),
) -> Dict[str, Dict[str, int]]:
    """
    Build a minimal signature dict from name and/or date of birth.

    Returns keys conditionally:
    - life_path, birth_day (if dob provided)
    - expression, soul_urge, personality (if name provided)
    """
    sig: Dict[str, Dict[str, int]] = {}

    if dob is not None:
        sig["life_path"] = life_path_number(dob, cfg=cfg)
        sig["birth_day"] = birth_day_number(dob, cfg=cfg)

    if name is not None:
        sig["expression"] = expression_number(name, cfg=cfg)
        sig["soul_urge"] = soul_urge_number(name, cfg=cfg)
        sig["personality"] = personality_number(name, cfg=cfg)

    return sig


if __name__ == "__main__":
    # Quick sanity run
    cfg = NumerologyConfig(keep_master_numbers=(11, 22, 33), apply_inversion=True)
    print(build_signature(name="Jean-François Tremblay", dob="1990-07-14", cfg=cfg))
