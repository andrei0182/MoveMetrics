import pandas as pd

from src.rules.data_quality import clean_provider_names


def analyze_providers(df):

    data = df.copy()
    data = clean_provider_names(data)
    


    # Convert Charged to number
    data["Charged"] = (
        data["Charged"]
        .astype(str)
        .str.replace("$", "")
        .str.replace(",", "")
    )


    data["Charged"] = pd.to_numeric(
        data["Charged"],
        errors="coerce"
    ).fillna(0)


    provider = (
        data
        .groupby("Sursa")
        .agg(
            Jobs=("Job #", "count"),
            Revenue=("Charged", "sum"),
            Average_Job=("Charged", "mean")
        )
        .reset_index()
    )


    total_revenue = provider["Revenue"].sum()


    provider["Revenue_%"] = (
        provider["Revenue"]
        /
        total_revenue
        *
        100
    )


    provider = provider.sort_values(
        by="Revenue",
        ascending=False
    )


    return provider