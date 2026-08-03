from src.rules.data_quality import clean_provider_names
from src.utils.money import clean_money_series


def analyze_providers(jobs_df):
    """
    Revenue pe sursa/provider, calculat pe date la nivel de JOB
    (vezi build_clean_jobs_from_df) - altfel un job cu 2 randuri
    (ex. plata initiala + plata_job_vechi) ar fi numarat de 2 ori
    la 'Jobs', desi e un singur job.
    """

    data = jobs_df.copy()
    data = clean_provider_names(data)

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
