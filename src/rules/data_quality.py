import re

from config.settings import VALID_ID_PREFIXES


JOB_ID_PATTERN = re.compile(r"^(" + "|".join(VALID_ID_PREFIXES) + r")[A-Z0-9\-]+$")


def clean_provider_names(df):
    """
    Flags as 'unknown' only rows where Source actually contains what
    looks like a Job ID (a sign that columns got shifted during data
    entry/export), rather than relying on a hardcoded list of known-bad
    rows - a hardcoded list silently breaks the moment new data comes in.
    """

    data = df.copy()

    if "Source" not in data.columns:
        return data

    looks_like_job_id = (
        data["Source"]
        .astype(str)
        .str.match(JOB_ID_PATTERN, na=False)
    )

    data.loc[looks_like_job_id, "Source"] = "unknown"

    return data


def data_quality_report(df):

    report = {}

    report["Rows"] = len(df)
    report["Missing Values"] = df.isna().sum().sum()
    report["Duplicates"] = df.duplicated().sum()

    if "Source" in df.columns:
        report["Suspicious Source (looks like a Job ID)"] = (
            df["Source"]
            .astype(str)
            .str.match(JOB_ID_PATTERN, na=False)
            .sum()
        )

    return report
