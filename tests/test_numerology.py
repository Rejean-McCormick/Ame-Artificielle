# Ame-Artificielle/tests/test_numerology.py

import pytest

from src.numerology import (
    NumerologyConfig,
    birth_day_number,
    build_signature,
    expression_number,
    invert_digit,
    life_path_number,
    name_total,
    name_total_consonants,
    name_total_vowels,
    normalize_name,
    pythagorean_letter_value,
    reduce_number,
)


def test_invert_digit_mapping():
    # 0 stays 0
    assert invert_digit(0) == 0

    # Mirror pairs
    assert invert_digit(1) == 9
    assert invert_digit(2) == 8
    assert invert_digit(3) == 7
    assert invert_digit(4) == 6
    assert invert_digit(5) == 5
    assert invert_digit(6) == 4
    assert invert_digit(7) == 3
    assert invert_digit(8) == 2
    assert invert_digit(9) == 1

    with pytest.raises(ValueError):
        invert_digit(10)

    with pytest.raises(ValueError):
        invert_digit(-1)


def test_reduce_number_basic_and_master_numbers():
    # basic reduction
    assert reduce_number(31) == 4  # 3+1
    assert reduce_number(999) == 9  # 9+9+9=27 -> 2+7=9

    # master numbers preserved
    assert reduce_number(11) == 11
    assert reduce_number(22) == 22
    assert reduce_number(33) == 33

    # reduction can land on master (29 -> 11)
    assert reduce_number(29, keep_master_numbers=(11, 22, 33)) == 11

    # if masters disabled, 11 reduces to 2
    assert reduce_number(29, keep_master_numbers=()) == 2

    with pytest.raises(ValueError):
        reduce_number(0, allow_zero=False)

    assert reduce_number(0, allow_zero=True) == 0


def test_pythagorean_letter_value_edges():
    # key boundaries in the standard mapping:
    assert pythagorean_letter_value("A") == 1
    assert pythagorean_letter_value("I") == 9
    assert pythagorean_letter_value("J") == 1
    assert pythagorean_letter_value("R") == 9
    assert pythagorean_letter_value("S") == 1
    assert pythagorean_letter_value("Z") == 8

    with pytest.raises(ValueError):
        pythagorean_letter_value("!")  # unsupported


def test_normalize_name_strips_accents_and_non_letters():
    assert normalize_name("Élise-Marie") == "ELISEMARIE"
    assert normalize_name(" Jean François  Tremblay ") == "JEANFRANCOISTREMBLAY"
    assert normalize_name("O'Connor") == "OCONNOR"
    assert normalize_name("123-__") == ""


def test_name_totals_simple_examples():
    # "ABC" -> 1+2+3 = 6
    assert name_total("ABC") == 6

    # vowels/consonants split (Y is treated as vowel here by design)
    assert name_total_vowels("ABC") == 1  # A only
    assert name_total_consonants("ABC") == 5  # B(2)+C(3)


def test_expression_number_simple():
    cfg = NumerologyConfig(keep_master_numbers=(11, 22, 33), apply_inversion=True)

    # "ABC" total=6 -> reduced=6 -> inverted=4
    out = expression_number("ABC", cfg=cfg)
    assert out["total"] == 6
    assert out["pythagorean"] == 6
    assert out["inverted"] == 4


def test_life_path_and_birth_day_known_date():
    cfg = NumerologyConfig(keep_master_numbers=(11, 22, 33), apply_inversion=True)

    # 1990-07-14: digits sum = 1+9+9+0+0+7+1+4 = 31 -> 4
    lp = life_path_number("1990-07-14", cfg=cfg)
    assert lp["total"] == 31
    assert lp["pythagorean"] == 4
    assert lp["inverted"] == 6

    # day 14 -> 1+4=5 (5 stays 5 when inverted)
    bd = birth_day_number("1990-07-14", cfg=cfg)
    assert bd["pythagorean"] == 5
    assert bd["inverted"] == 5


def test_build_signature_contains_expected_keys():
    cfg = NumerologyConfig(keep_master_numbers=(11, 22, 33), apply_inversion=True)

    sig = build_signature(name="ABC", dob="1990-07-14", cfg=cfg)

    # date-based
    assert "life_path" in sig
    assert "birth_day" in sig

    # name-based
    assert "expression" in sig
    assert "soul_urge" in sig
    assert "personality" in sig

    # sanity: inverted present when pythagorean is 1..9
    assert "inverted" in sig["life_path"]
    assert "inverted" in sig["expression"]
