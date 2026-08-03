from src.utils.money import clean_money_series


def analyze_providers(jobs_df):
    """
    Revenue/Cost/Profit pe sursa/provider. Presupune jobs_df deja curat si
    deja trecut prin regulile de business (src/rules/data_quality.py aplicat
    in pipeline.py) - acest modul NU mai apeleaza clean_provider_names
    intern, ca sa nu existe doua locuri care aplica aceeasi regula.
    """

    data = jobs_df.copy()

    data["Charged"] = clean_money_series(data["Charged"])

    if "Cost" in data.columns:
        data["Cost"] = clean_money_series(data["Cost"])
    else:
        data["Cost"] = 0.0

    provider = (
        data
        .groupby("Sursa")
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

    provider = provider.sort_values(by="Revenue", ascending=False)

    return provider