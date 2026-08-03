from src.utils.money import clean_money_series


def analyze_providers(jobs_df):
    """
    Revenue pe sursa/provider. Presupune jobs_df deja curat si deja
    trecut prin regulile de business (src/rules/data_quality.py aplicat
    in pipeline.py) - acest modul NU mai apeleaza clean_provider_names
    intern, ca sa nu existe doua locuri care aplica aceeasi regula.
    """

    data = jobs_df.copy()

    data["Charged"] = clean_money_series(data["Charged"])

    provider = (
        data
        .groupby("Sursa")
        .agg(
            Jobs=("Job #", "nunique"),
            Revenue=("Charged", "sum"),
            Average_Job=("Charged", "mean")
        )
        .reset_index()
    )

    total_revenue = provider["Revenue"].sum()

    provider["Revenue_%"] = 0.0
    if total_revenue > 0:
        provider["Revenue_%"] = provider["Revenue"] / total_revenue * 100

    provider = provider.sort_values(by="Revenue", ascending=False)

    return provider
