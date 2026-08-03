import pandas as pd


def clean_money_value(value):
    """
    Converteste o valoare monetara in float.
    Exemple: "$1,050.00" -> 1050.0 ; "-" -> 0.0 ; None -> 0.0
    """

    if pd.isna(value):
        return 0.0

    if isinstance(value, (int, float)):
        return float(value)

    value = str(value).strip()

    if value in ("", "-", "nan", "None"):
        return 0.0

    value = (
        value
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def clean_money_series(series):
    return series.apply(clean_money_value)
