from src.utils.money import clean_money_value


def test_dollar_and_comma_thousands_us_style():
    assert clean_money_value("$1,050.00") == 1050.0


def test_european_decimal_comma_one_digit():
    assert clean_money_value("1312,5") == 1312.5


def test_european_decimal_comma_two_digits():
    assert clean_money_value("3750,08") == 3750.08


def test_european_thousands_and_decimal():
    assert clean_money_value("1.050,00") == 1050.0


def test_us_thousands_comma_three_digits_after_comma():
    assert clean_money_value("1,050") == 1050.0


def test_negative_european_value():
    assert clean_money_value("-787,5") == -787.5


def test_dash_is_zero():
    assert clean_money_value("-") == 0.0


def test_none_and_nan_are_zero():
    assert clean_money_value(None) == 0.0
    assert clean_money_value(float("nan")) == 0.0


def test_numeric_passthrough():
    assert clean_money_value(840) == 840.0
    assert clean_money_value(840.5) == 840.5


def test_garbage_string_is_zero_not_a_crash():
    assert clean_money_value("N/A") == 0.0
