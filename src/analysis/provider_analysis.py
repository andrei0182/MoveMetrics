from src.utils.money import clean_money_series


def analyze_providers(jobs_df):
    """
    Revenue/Cost/Profit per lead source. Assumes jobs_df is already clean
    and already passed through the business rules (src/rules/data_quality.py,
    applied once in pipeline.py) - this module does not re-apply rules,
    so there's a single place that decides what counts as a valid source.
    """

    data = jobs_df.copy()

    data["Charged"] = clean_money_series(data["Charged"])

    if "Cost" in data.columns:
        data["Cost"] = clean_money_series(data["Cost"])
    else:
        data["Cost"] = 0.0

    provider = (
        data
        .groupby("Source")
        .agg(
            Jobs=("Job #", "nunique"),
            Revenue=("Charged", "sum"),
            Cost=("Cost", "sum"),
            Average_Job=("Charged", "mean")
        )
        .reset_index()
    )

    provider["Profit"] = provider["Revenue"] - provider["Cost"]

    provider["Margin_%"] = 0.0
    revenue_mask = provider["Revenue"] > 0
    provider.loc[revenue_mask, "Margin_%"] = (
        provider.loc[revenue_mask, "Profit"]
        / provider.loc[revenue_mask, "Revenue"]
        * 100
    )

    total_revenue = provider["Revenue"].sum()

    provider["Revenue_%"] = 0.0
    if total_revenue > 0:
        provider["Revenue_%"] = provider["Revenue"] / total_revenue * 100

    provider = provider.sort_values(by="Profit", ascending=False)

    return provider
