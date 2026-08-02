import pandas as pd


def clean_money(series):

    def convert(value):

        if pd.isna(value):
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value).strip()

        if value in ["", "-", "nan", "None"]:
            return 0.0

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



def calculate_financials(df):

    result = df.copy()


    # ==================================
    # NORMALIZARE DATA
    # ==================================

    if "Data" in result.columns:

        result["Data"] = pd.to_datetime(
            result["Data"],
            errors="coerce"
        )


    # ==================================
    # NORMALIZARE BANI
    # ==================================

    result["Charged"] = clean_money(
        result["Charged"]
    )

    result["Cost"] = clean_money(
        result["Cost"]
    )


    # ==================================
    # SORTARE ISTORIC JOB
    # Ultimul rand = ultima evolutie
    # ==================================

    result = result.sort_values(
        [
            "Job #",
            "Data"
        ]
    )


    # ==================================
    # ULTIMUL STATUS AL JOBULUI
    #
    # Exemplu:
    #
    # AL4993
    # 29.07 scheduled_callback
    # 30.07 booked
    #
    # pastram booked
    #
    # ==================================

    final = (
        result
        .groupby("Job #")
        .tail(1)
        .reset_index(drop=True)
    )


    # ==================================
    # COST TOTAL PE JOB
    #
    # Costul poate aparea o singura data
    # pe prima aparitie a leadului
    #
    # ==================================

    job_cost = (
        result
        .groupby("Job #")["Cost"]
        .sum()
        .reset_index()
    )


    # ==================================
    # VENIT TOTAL PE JOB
    #
    # Include:
    # lead -> booked -> payment
    #
    # Ex:
    # AL4993 = 630
    #
    # ==================================

    job_charged = (
        result
        .groupby("Job #")["Charged"]
        .sum()
        .reset_index()
    )


    # ==================================
    # REFACEM TABEL FINAL
    # ==================================

    final = final.drop(
        columns=[
            "Cost",
            "Charged"
        ],
        errors="ignore"
    )


    final = final.merge(
        job_cost,
        on="Job #",
        how="left"
    )


    final = final.merge(
        job_charged,
        on="Job #",
        how="left"
    )


    final["Cost"] = (
        final["Cost"]
        .fillna(0)
    )


    final["Charged"] = (
        final["Charged"]
        .fillna(0)
    )


    # ==================================
    # KPI FINANCIAL
    # ==================================

    revenue = final["Charged"].sum()

    cost = final["Cost"].sum()

    profit = revenue - cost


    margin = 0

    if revenue > 0:

        margin = (
            profit /
            revenue
        ) * 100



    return {

        "Revenue": round(revenue, 2),

        "Cost": round(cost, 2),

        "Profit": round(profit, 2),

        "Margin %": round(margin, 2),

        "Jobs": final["Job #"].nunique()

    }