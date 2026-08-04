import pandas as pd

from config.settings import PROCESSED_FILE, LEADS_SHEET_NAME
from src.loaders.excel_loader import load_excel
from src.utils.money import clean_money_series


def _ensure_column(df, column_name, default=0.0):
    """If an expected column is missing (report structure varies over
    time), create it with a default instead of failing later."""

    if column_name not in df.columns:
        df[column_name] = default

    return df


def build_clean_jobs_from_df(df):
    """
    Collapses the raw report (multiple rows per Job #, one for each event:
    new lead, quoted, booked, a later payment on an already-booked job...)
    into a single row per Job #, with:
      - the last real status recorded for that job
      - all payments (Charged) summed across the job's whole history
      - total cost

    Pure function, testable without touching disk.
    """

    result = df.copy()

    if "Date" in result.columns:
        result["Date"] = pd.to_datetime(result["Date"], errors="coerce")

    result = _ensure_column(result, "Charged")
    result = _ensure_column(result, "Cost")

    result["Charged"] = clean_money_series(result["Charged"])
    result["Cost"] = clean_money_series(result["Cost"])

    # Rows with a missing date sort first, not last - otherwise a row
    # with no date could wrongly become the "last known status" of a job.
    result = result.sort_values(["Job #", "Date"], na_position="first")

    # The last REAL row (not .last(), which combines the last non-null
    # value per column across different rows - possibly a "Frankenstein"
    # row that never actually existed).
    final_jobs = (
        result
        .groupby("Job #")
        .tail(1)
        .reset_index(drop=True)
    )

    costs = result.groupby("Job #")["Cost"].sum().reset_index()
    revenue = result.groupby("Job #")["Charged"].sum().reset_index()

    final_jobs = final_jobs.drop(columns=["Cost", "Charged"], errors="ignore")
    final_jobs = final_jobs.merge(costs, on="Job #", how="left")
    final_jobs = final_jobs.merge(revenue, on="Job #", how="left")

    final_jobs["Cost"] = final_jobs["Cost"].fillna(0)
    final_jobs["Charged"] = final_jobs["Charged"].fillna(0)

    final_jobs["Profit"] = final_jobs["Charged"] - final_jobs["Cost"]

    final_jobs["Margin %"] = 0.0
    mask = final_jobs["Charged"] > 0
    final_jobs.loc[mask, "Margin %"] = (
        final_jobs.loc[mask, "Profit"] / final_jobs.loc[mask, "Charged"] * 100
    )

    return final_jobs


def build_clean_jobs(input_file, output_file=None):
    """I/O wrapper: reads an Excel file, writes the cleaned result to disk."""

    output_file = output_file or PROCESSED_FILE

    print("Loading data...")

    df = load_excel(input_file, LEADS_SHEET_NAME)

    print("RAW ROWS:", len(df))

    final_jobs = build_clean_jobs_from_df(df)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    final_jobs.to_excel(output_file, index=False)

    print()
    print("CLEAN JOBS CREATED")
    print("------------------")
    print("Jobs:", len(final_jobs))
    print("Revenue:", round(final_jobs["Charged"].sum(), 2))
    print("Cost:", round(final_jobs["Cost"].sum(), 2))
    print("Profit:", round(final_jobs["Profit"].sum(), 2))

    return final_jobs
