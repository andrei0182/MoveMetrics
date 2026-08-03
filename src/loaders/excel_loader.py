import pandas as pd


def get_sheets(file_path):

    excel = pd.ExcelFile(file_path, engine="openpyxl")

    return excel.sheet_names


def _resolve_sheet_name(file_path, sheet_name):
    """
    Gaseste numele exact al sheet-ului, tolerand diferente de spatii/majuscule.
    Motiv: sheet-ul "CHARGED" din Report_JUL.xlsx a fost cautat in unele
    module ca "CHARGED " (cu spatiu) -> cautare exacta esua silentios.
    """

    available = get_sheets(file_path)

    if sheet_name in available:
        return sheet_name

    normalized = {name.strip().casefold(): name for name in available}
    target = sheet_name.strip().casefold()

    if target in normalized:
        return normalized[target]

    raise ValueError(
        f"Sheet '{sheet_name}' nu a fost gasit. Sheet-uri disponibile: {available}"
    )


def load_excel(
    file_path,
    sheet_name
):

    resolved_sheet = _resolve_sheet_name(file_path, sheet_name)

    # citim fara header
    raw = pd.read_excel(
        file_path,
        sheet_name=resolved_sheet,
        header=None,
        engine="openpyxl"
    )

    # cautam randul care contine "Job #"
    header_row = None

    for index, row in raw.iterrows():

        values = row.astype(str).tolist()

        if "Job #" in values:
            header_row = index
            break

    if header_row is None:
        raise ValueError(
            "Nu am gasit header-ul Excel"
        )

    # recitim cu header corect
    df = pd.read_excel(
        file_path,
        sheet_name=resolved_sheet,
        header=header_row,
        engine="openpyxl"
    )

    # eliminam coloane goale
    df = df.dropna(
        axis=1,
        how="all"
    )

    # curatam nume coloane
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df
