import pandas as pd


def get_sheets(file_path):

    excel = pd.ExcelFile(file_path, engine="openpyxl")

    return excel.sheet_names


def _resolve_sheet_name(file_path, sheet_name):
    """
    Resolves the exact sheet name, tolerating trailing spaces / case
    differences (a common source of silent "sheet not found" failures
    when the expected name is hardcoded slightly differently in a
    couple of places).
    """

    available = get_sheets(file_path)

    if sheet_name in available:
        return sheet_name

    normalized = {name.strip().casefold(): name for name in available}
    target = sheet_name.strip().casefold()

    if target in normalized:
        return normalized[target]

    raise ValueError(
        f"Sheet '{sheet_name}' not found. Available sheets: {available}"
    )


def load_excel(file_path, sheet_name):

    resolved_sheet = _resolve_sheet_name(file_path, sheet_name)

    # first pass without header, to locate the real header row
    raw = pd.read_excel(
        file_path,
        sheet_name=resolved_sheet,
        header=None,
        engine="openpyxl"
    )

    header_row = None

    for index, row in raw.iterrows():
        values = row.astype(str).tolist()
        if "Job #" in values:
            header_row = index
            break

    if header_row is None:
        raise ValueError("Could not locate the header row (expected a 'Job #' column)")

    df = pd.read_excel(
        file_path,
        sheet_name=resolved_sheet,
        header=header_row,
        engine="openpyxl"
    )

    df = df.dropna(axis=1, how="all")

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df
