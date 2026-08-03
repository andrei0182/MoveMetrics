import pandas as pd

from config.settings import PROCESSED_FILE, REPORT_FILE, CHARGED_SHEET
from src.excel.excel_loader import load_excel
from src.utils.money import clean_money_series


def build_clean_jobs_from_df(df):
    """
    Transforma raportul brut (mai multe randuri per Job #, cate unul
    pentru fiecare eveniment: lead nou, quoted, booked, plata_job_vechi...)
    intr-un singur rand per Job #, cu:
      - ultimul status real inregistrat (nu un amestec de coloane)
      - suma tuturor incasarilor (Charged) pe job
      - costul total pe job

    Functie pura, testabila fara fisiere pe disc.
    """

    result = df.copy()

    if "Data" in result.columns:
        result["Data"] = pd.to_datetime(
            result["Data"],
            errors="coerce"
        )

    result["Charged"] = clean_money_series(result["Charged"])
    result["Cost"] = clean_money_series(result["Cost"])

    # Randurile fara data merg la inceput, nu la final -
    # altfel un rand cu Data lipsa devine "ultimul status" al jobului
    # din cauza sortarii implicite (na_position="last").
    result = result.sort_values(
        ["Job #", "Data"],
        na_position="first"
    )

    # Ultimul RAND real (nu ultima valoare non-null pe fiecare coloana -
    # .last() combina campuri din randuri diferite si poate crea
    # un rand "Frankenstein" care nu a existat niciodata ca atare).
    final_jobs = (
        result
        .groupby("Job #")
        .tail(1)
        .reset_index(drop=True)
    )

    costs = (
        result
        .groupby("Job #")["Cost"]
        .sum()
        .reset_index()
    )

    revenue = (
        result
        .groupby("Job #")["Charged"]
        .sum()
        .reset_index()
    )

    final_jobs = final_jobs.drop(
        columns=["Cost", "Charged"],
        errors="ignore"
    )

    final_jobs = final_jobs.merge(costs, on="Job #", how="left")
    final_jobs = final_jobs.merge(revenue, on="Job #", how="left")

    final_jobs["Cost"] = final_jobs["Cost"].fillna(0)
    final_jobs["Charged"] = final_jobs["Charged"].fillna(0)

    final_jobs["Profit"] = final_jobs["Charged"] - final_jobs["Cost"]

    final_jobs["Margin %"] = 0.0
    mask = final_jobs["Charged"] > 0

    final_jobs.loc[mask, "Margin %"] = (
        final_jobs.loc[mask, "Profit"]
        / final_jobs.loc[mask, "Charged"]
        * 100
    )

    return final_jobs


def build_clean_jobs(input_file=None, output_file=None):
    """Wrapper de I/O: citeste din Excel, scrie rezultatul pe disc."""

    input_file = input_file or REPORT_FILE
    output_file = output_file or PROCESSED_FILE

    print("Loading data...")

    df = load_excel(input_file, CHARGED_SHEET)

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


if __name__ == "__main__":
    build_clean_jobs()
