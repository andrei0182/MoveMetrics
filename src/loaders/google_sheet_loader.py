import pandas as pd
import requests
from io import StringIO


def load_google_sheet(sheet_id, sheet_name=None, gid=None):
    """
    Loads a Google Sheets tab as a DataFrame, via CSV export.

    Prefers the gviz endpoint (query by sheet name) over gid - a sheet
    name stays stable even if tabs get reordered, whereas a gid can
    silently point at the wrong tab after a reorder.

    Requires the sheet to be shared "Anyone with the link - Viewer",
    otherwise the request fails with 401/403 (sheet is private).
    """

    if sheet_name:
        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
        )
    elif gid:
        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv&gid={gid}"
        )
    else:
        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv"
        )

    response = requests.get(url, timeout=30)

    if response.status_code in (401, 403):
        raise PermissionError(
            "Could not access this Google Sheet. Check that it's shared "
            "as 'Anyone with the link - Viewer' (Share button, top right)."
        )

    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    return df
