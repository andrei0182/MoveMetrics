import pandas as pd

from config.settings import PROCESSED_FILE, REPORT_FILE, CHARGED_SHEET
from src.loaders.excel_loader import load_excel
from src.utils.money import clean_money_series


def _ensure_column(df, column_name, default=0.0):
    """
    Daca o coloana lipseste din raport, o creeaza.
    """

    if column_name not in df.columns:
        df[column_name] = default

    return df



def build_clean_jobs_from_df(df):
    """
    Curata raportul brut si transforma datele intr-un singur rand/job.

    Output:
    - un singur rand pentru fiecare Job #
    - suma Charged pe job
    - suma Cost pe job
    - Profit
    - Margin %
    """

    result = df.copy()


    # ==========================
    # NORMALIZARE DATA
    # ==========================

    if "Move Date" in result.columns:

        result["Move Date"] = pd.to_datetime(
            result["Move Date"],
            errors="coerce"
        )

        date_column = "Move Date"


    elif "Data" in result.columns:

        result["Data"] = pd.to_datetime(
            result["Data"],
            errors="coerce"
        )

        date_column = "Data"


    else:

        date_column = None



    # ==========================
    # COLOANE NECESARE
    # ==========================

    result = _ensure_column(
        result,
        "Charged"
    )

    result = _ensure_column(
        result,
        "Cost"
    )


    result["Charged"] = clean_money_series(
        result["Charged"]
    )


    result["Cost"] = clean_money_series(
        result["Cost"]
    )


    # ==========================
    # SORTARE CRONOLOGICA
    # ==========================

    if date_column:

        result = result.sort_values(
            [
                "Job #",
                date_column
            ],
            na_position="first"
        )


    # ==========================
    # ULTIMUL EVENIMENT AL JOBULUI
    # ==========================

    final_jobs = (
        result
        .groupby("Job #")
        .tail(1)
        .reset_index(drop=True)
    )


    # ==========================
    # TOTALURI FINANCIARE
    # ==========================

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



    # eliminam valorile vechi
    final_jobs = final_jobs.drop(
        columns=[
            "Cost",
            "Charged"
        ],
        errors="ignore"
    )


    # adaugam totalurile
    final_jobs = final_jobs.merge(
        costs,
        on="Job #",
        how="left"
    )


    final_jobs = final_jobs.merge(
        revenue,
        on="Job #",
        how="left"
    )


    final_jobs["Cost"] = (
        final_jobs["Cost"]
        .fillna(0)
    )


    final_jobs["Charged"] = (
        final_jobs["Charged"]
        .fillna(0)
    )


    # ==========================
    # PROFIT
    # ==========================

    final_jobs["Profit"] = (
        final_jobs["Charged"]
        -
        final_jobs["Cost"]
    )


    # ==========================
    # MARGIN
    # ==========================

    final_jobs["Margin %"] = 0.0


    mask = final_jobs["Charged"] > 0


    final_jobs.loc[mask, "Margin %"] = (
        final_jobs.loc[mask, "Profit"]
        /
        final_jobs.loc[mask, "Charged"]
        *
        100
    )


    return final_jobs




def build_clean_jobs(input_file=None, output_file=None):
    """
    Citeste Excel si salveaza fisierul procesat.
    """

    input_file = input_file or REPORT_FILE
    output_file = output_file or PROCESSED_FILE


    print("Loading data...")


    df = load_excel(
        input_file,
        CHARGED_SHEET
    )


    print(
        "RAW ROWS:",
        len(df)
    )


    final_jobs = build_clean_jobs_from_df(
        df
    )


    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    final_jobs.to_excel(
        output_file,
        index=False
    )


    print()
    print("CLEAN JOBS CREATED")
    print("------------------")

    print(
        "Jobs:",
        len(final_jobs)
    )

    print(
        "Revenue:",
        round(
            final_jobs["Charged"].sum(),
            2
        )
    )

    print(
        "Cost:",
        round(
            final_jobs["Cost"].sum(),
            2
        )
    )

    print(
        "Profit:",
        round(
            final_jobs["Profit"].sum(),
            2
        )
    )


    return final_jobs




if __name__ == "__main__":

    build_clean_jobs()