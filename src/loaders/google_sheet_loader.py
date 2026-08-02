import pandas as pd
import requests
from io import StringIO


def load_google_sheet(sheet_id, gid=None):

    if gid:
        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv&gid={gid}"
        )
    else:
        url = (
            f"https://docs.google.com/spreadsheets/d/"
            f"{sheet_id}/export?format=csv"
        )


    response = requests.get(
        url,
        timeout=30
    )


    response.raise_for_status()


    df = pd.read_csv(
        StringIO(response.text)
    )


    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )


    return df