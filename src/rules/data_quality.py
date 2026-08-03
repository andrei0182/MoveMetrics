import re

from config.settings import VALID_JOB_PREFIXES


JOB_ID_PATTERN = re.compile(
    r"^(" + "|".join(VALID_JOB_PREFIXES) + r")[A-Z0-9\-]+$"
)


def clean_provider_names(df):
    """
    Marcheaza ca 'unknown' doar randurile unde Sursa contine de fapt
    un Job # (semn ca datele au fost decalate cu o coloana in raportul
    sursa), nu o lista hardcodata de joburi.

    ATENTIE: lista veche hardcodata ["AL4170", "AL4470", "WB1031-DUP"]
    a fost eliminata - verificare directa pe Report_JUL.xlsx a aratat ca
    toate trei sunt joburi booked reale, cu Sursa reala (angieslist /
    website) si bani incasati real. Lista bloca gresit revenue-ul lor.
    """

    data = df.copy()

    if "Sursa" not in data.columns:
        return data

    looks_like_job_id = (
        data["Sursa"]
        .astype(str)
        .str.match(JOB_ID_PATTERN, na=False)
    )

    data.loc[looks_like_job_id, "Sursa"] = "unknown"

    return data


def data_quality_report(df):

    report = {}

    report["Rows"] = len(df)

    report["Missing Values"] = (
        df.isna()
        .sum()
        .sum()
    )

    report["Duplicates"] = (
        df.duplicated()
        .sum()
    )

    if "Sursa" in df.columns:
        report["Suspicious Sursa (arata ca Job #)"] = (
            df["Sursa"]
            .astype(str)
            .str.match(JOB_ID_PATTERN, na=False)
            .sum()
        )

    return report
