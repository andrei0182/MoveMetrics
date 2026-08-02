import pandas as pd
from pathlib import Path


INPUT_FILE = Path("data/raw/Report_JUL.xlsx")
OUTPUT_FILE = Path("data/processed/processed_jobs.xlsx")


def clean_money(series):

    def convert(value):

        if pd.isna(value):
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value)

        value = (
            value
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        try:
            return float(value)

        except:
            return 0.0

    return series.apply(convert)



def build_clean_jobs():

    print("Loading data...")

    df = pd.read_excel(
        INPUT_FILE
    )


    print("RAW ROWS:")
    print(len(df))


    # date

    df["Data"] = pd.to_datetime(
        df["Data"],
        errors="coerce"
    )


    # money

    df["Charged"] = clean_money(
        df["Charged"]
    )


    df["Cost"] = clean_money(
        df["Cost"]
    )


    # sort history

    df = df.sort_values(
        [
            "Job #",
            "Data"
        ]
    )


    # final status

    final_jobs = (
        df
        .groupby("Job #")
        .last()
        .reset_index()
    )


    # total cost

    costs = (
        df
        .groupby("Job #")["Cost"]
        .sum()
        .reset_index()
    )


    # total payments

    revenue = (
        df
        .groupby("Job #")["Charged"]
        .sum()
        .reset_index()
    )


    # remove old financial columns

    final_jobs = final_jobs.drop(
        columns=[
            "Cost",
            "Charged"
        ],
        errors="ignore"
    )


    # merge financials

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


    final_jobs["Profit"] = (
        final_jobs["Charged"]
        -
        final_jobs["Cost"]
    )


    final_jobs["Margin %"] = 0


    mask = final_jobs["Charged"] > 0


    final_jobs.loc[mask,"Margin %"] = (
        final_jobs.loc[mask,"Profit"]
        /
        final_jobs.loc[mask,"Charged"]
        *
        100
    )


    final_jobs.to_excel(
        OUTPUT_FILE,
        index=False
    )


    print()
    print("CLEAN JOBS CREATED")
    print("------------------")
    print("Jobs:", len(final_jobs))
    print("Revenue:", round(final_jobs["Charged"].sum(),2))
    print("Cost:", round(final_jobs["Cost"].sum(),2))
    print("Profit:", round(final_jobs["Profit"].sum(),2))


    return final_jobs



if __name__ == "__main__":

    build_clean_jobs()