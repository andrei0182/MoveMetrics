import pandas as pd


def clean_money_value(value):
    """
    Converteste o valoare monetara in float, indiferent de format:
    - US: "$1,050.00" (virgula = separator de mii, punct = zecimale)
    - European: "1.050,00" sau "1312,5" (virgula = zecimale)

    Motiv: fisierul local (.xlsx) stocheaza numerele ca float curat,
    dar export-ul CSV live din Google Sheets scoate numerele ca TEXT
    formatat dupa locale-ul sheet-ului (european, cu virgula zecimala).
    Tratarea oarba a virgulei ca separator de mii (varianta veche)
    infla valori ca "3750,08" -> 375008, o eroare de ~100x pe acel rand.
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
        # Ambele prezente: ultimul simbol intalnit e separatorul zecimal.
        # "1.050,00" (european) sau "1,050.00" (US) - comparam pozitiile.
        if value.rfind(",") > value.rfind("."):
            value = value.replace(".", "").replace(",", ".")
        else:
            value = value.replace(",", "")
    elif has_comma:
        # Doar virgula: daca are exact 2 cifre dupa ea, e separator
        # zecimal european ("1312,5" cu 1 cifra sau "630,08" cu 2).
        # Altfel (3 cifre dupa virgula), e separator de mii US ("1,050").
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