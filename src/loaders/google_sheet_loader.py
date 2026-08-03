import pandas as pd
import requests
from io import StringIO


def load_google_sheet(sheet_id, sheet_name=None, gid=None):
    """
    Load Google Sheet tab as pandas DataFrame.

    Priority:
    1. Sheet name (stable)
    2. gid
    3. first sheet
    """


    if sheet_name:
        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/gviz/tq?"
            f"tqx=out:csv&sheet={sheet_name}"
        )

    elif gid:

        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?"
            f"format=csv&gid={gid}"
        )

    else:

        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?"
            f"format=csv"
        )


    print("Loading Google Sheet:")
    print(url)


    session = requests.Session()

    # IMPORTANT:
    # evita proxy-ul Bosch care dă 407
    session.trust_env = False


    response = session.get(
        url,
        timeout=30
    )


    if response.status_code in (401, 403):

        raise PermissionError(
            """
Google Sheet access denied.

Check:
Share -> General access ->
Anyone with the link -> Viewer
"""
        )


    response.raise_for_status()


    df = pd.read_csv(
        StringIO(response.text)
    )


    # curățare coloane

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    # curățare text

    for col in df.select_dtypes(
        include="object"
    ).columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )


    return df