import pandas as pd
import requests
from io import StringIO


def load_google_sheet(sheet_id, sheet_name=None, gid=None):
    """
    Citeste un tab dintr-un Google Sheet ca DataFrame, direct prin export CSV.

    Foloseste endpoint-ul gviz (query by sheet name) daca sheet_name e dat -
    e mai robust decat gid, pentru ca gid-urile se pot schimba daca cineva
    reordoneaza tab-urile, dar numele tab-ului ("CHARGED") ramane stabil.

    Necesita ca sheet-ul sa fie partajat "Anyone with the link - Viewer",
    altfel cererea esueaza cu 401 (sheet-ul e privat).

    NOTA: nu foloseste requests.Session cu trust_env=False (incercare
    anterioara de a ocoli proxy-ul corporate) - pe o retea care obliga
    tot traficul prin proxy, ocolirea proxy-ului duce direct la eroare
    de DNS, nu rezolva nimic. Local, sursa de date ramane fisierul Excel
    (vezi config/settings.py); Google Sheets functioneaza doar din medii
    fara proxy restrictiv (ex. Streamlit Cloud).
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

    response = requests.get(
        url,
        timeout=30
    )

    if response.status_code in (401, 403):
        raise PermissionError(
            "Nu am acces la Google Sheet-ul cerut. Verifica ca e partajat "
            "'Anyone with the link - Viewer' (buton Share, colt dreapta-sus)."
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

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].astype(str).str.strip()

    return df