from src.utils.money import clean_money_series


def calculate_kpis(jobs_df):
    """
    KPIs computed at the JOB level, not the ROW level - jobs_df must
    already be deduplicated (one row per Job #, e.g. the output of
    build_clean_jobs_from_df). Feeding it the raw multi-row report
    instead would make "Average Job Value" wrong (mean() over rows,
    not over jobs).
    """

    data = jobs_df.copy()

    if "Charged" in data.columns:
        data["Charged"] = clean_money_series(data["Charged"])
    else:
        data["Charged"] = 0.0

    kpis = {}

    total_jobs = data["Job #"].nunique() if "Job #" in data.columns else len(data)
    total_charged = data["Charged"].sum()

    kpis["Total Charged"] = total_charged
    kpis["Total Jobs"] = total_jobs
    kpis["Average Job Value"] = total_charged / total_jobs if total_jobs > 0 else 0.0

    kpis["Refunds"] = int((data["Charged"] < 0).sum()) if "Charged" in data.columns else 0

    # Deposit/quote value for leads that haven't converted to a real
    # charge yet - the closest computable equivalent of "open pipeline."
    if "Deposit" in data.columns:
        pipeline_mask = data["Charged"] <= 0
        kpis["Open Pipeline (Deposit/Quote)"] = (
            clean_money_series(data.loc[pipeline_mask, "Deposit"]).sum()
        )
    else:
        kpis["Open Pipeline (Deposit/Quote)"] = 0.0

    return kpis
