import pandas as pd


def clean_money_value(value):
    """
    Converts a money value to float, regardless of locale format:
    - US style: "$1,050.00" (comma = thousands separator, dot = decimal)
    - European style: "1.050,00" or "1312,5" (comma = decimal separator)

    Why this matters: a local Excel file stores numbers as clean floats,
    but a live CSV export (e.g. from Google Sheets) renders numbers as
    TEXT formatted according to the sheet's locale. Blindly treating every
    comma as a thousands separator silently inflates values like "3750,08"
    into 375008 - a ~100x error on that row.
    """

    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value in ("", "-", "nan", "None"):
        return 0.0

    value = value.replace("$", "").strip()

    has_comma = "," in value
    has_dot = "." in value

    if has_comma and has_dot:
        # Both present: whichever comes last is the decimal separator.
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif has_comma:
        # Comma only: 1-2 digits after it => European decimal separator.
        # 3 digits after it => US thousands separator.
        after_comma = value.split(",")[-1]
        if len(after_comma) <= 2:
            value = value.replace(",", ".")
        else:
            value = value.replace(",", "")

    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def clean_money_series(series):
    return series.apply(clean_money_value)
