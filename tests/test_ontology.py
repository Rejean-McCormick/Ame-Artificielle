# Ame-Artificielle/tests/test_ontology.py
from __future__ import annotations

import json
from pathlib import Path

import pytest


def load_pi_ontology(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def ontology() -> dict:
    # Tests assume the repo root is the working directory when running pytest.
    path = Path("data/pi_ontology.json")
    if not path.exists():
        pytest.skip("data/pi_ontology.json not found; place ontology file in data/ to run tests.")
    return load_pi_ontology(path)


def test_has_digits_0_to_9_keys_or_known_missing(ontology: dict) -> None:
    """
    We expect digits 0..9. Current project note: digit "2" may be missing.
    This test enforces everything except "2" exists, and flags any other missing digit.
    """
    keys = set(ontology.keys())
    expected = {str(d) for d in range(10)}

    # Allowed known-missing key:
    allowed_missing = {"2"}

    missing = expected - keys
    unexpected_missing = missing - allowed_missing
    assert not unexpected_missing, f"Unexpected missing digit keys: {sorted(unexpected_missing)}"

    # If "2" is missing, ensure it's explicitly known rather than accidental.
    # (If present, that's good too.)
    if "2" in missing:
        assert "2" not in keys


def test_each_digit_entry_has_basic_structure(ontology: dict) -> None:
    """
    Each digit should have a dict payload.
    We accept minimal structure because traditions may vary.
    """
    for k, v in ontology.items():
        assert k.isdigit(), f"Ontology key {k!r} is not a digit string"
        d = int(k)
        assert 0 <= d <= 9, f"Digit key out of range: {d}"
        assert isinstance(v, dict), f"Digit {k} entry must be a dict"


def test_digit_entries_have_some_interpretation_text(ontology: dict) -> None:
    """
    Loose sanity check: each digit should contain at least one non-empty string
    somewhere in its nested dict.
    """
    def any_nonempty_string(obj) -> bool:
        if isinstance(obj, str):
            return obj.strip() != ""
        if isinstance(obj, dict):
            return any(any_nonempty_string(x) for x in obj.values())
        if isinstance(obj, list):
            return any(any_nonempty_string(x) for x in obj)
        return False

    for k, v in ontology.items():
        assert any_nonempty_string(v), f"Digit {k} entry appears to contain no text"


def test_no_nan_or_infinite_numbers_in_ontology(ontology: dict) -> None:
    """
    Ontology should be textual and/or finite numeric weights if present.
    """
    def check(obj) -> None:
        if isinstance(obj, float):
            assert obj == obj, "Found NaN in ontology"
            assert obj not in (float("inf"), float("-inf")), "Found infinity in ontology"
        elif isinstance(obj, dict):
            for x in obj.values():
                check(x)
        elif isinstance(obj, list):
            for x in obj:
                check(x)

    check(ontology)
