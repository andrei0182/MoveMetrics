"""
Day-by-day trend analysis over the raw (pre-deduplication) report data.

Uses raw_df rather than the deduplicated jobs_df on purpose: jobs_df
collapses a job's whole history into a single row (attributed to its
last event date), which would misrepresent when leads actually arrived
or when money actually came in. raw_df, with one row per real event,
lets us attribute:
  - Revenue to the day it was actually collected
  - A lead to the day it first appeared (first-touch date)
  - A conversion to the day it actually converted (which may be later
    than the lead's first-touch date)
"""

import pandas as pd

from src.utils.money import clean_money_series


def analyze_trends(raw_df, date_column="Date"):

    data = raw_df.copy()

    if date_column not in data.columns:
        return pd.DataFrame(columns=["Date", "Revenue", "New Leads", "Conversions"])

    data[date_column] = pd.to_datetime(data[date_column], errors="coerce")
    data = data.dropna(subset=[date_column])

    if "Charged" in data.columns:
        data["Charged"] = clean_money_series(data["Charged"])
    else:
        data["Charged"] = 0.0

    revenue_by_day = (
        data.groupby(data[date_column].dt.date)["Charged"]
        .sum()
        .reset_index()
    )
    revenue_by_day.columns = ["Date", "Revenue"]

    first_seen = data.groupby("Job #")[date_column].min().dt.date
    leads_by_day = first_seen.value_counts().sort_index().reset_index()
    leads_by_day.columns = ["Date", "New Leads"]

    converted_rows = data[data["Charged"] > 0]
    conversions_by_day = (
        converted_rows.groupby(converted_rows[date_column].dt.date)["Job #"]
        .nunique()
        .reset_index()
    )
    conversions_by_day.columns = ["Date", "Conversions"]

    merged = (
        revenue_by_day
        .merge(leads_by_day, on="Date", how="outer")
        .merge(conversions_by_day, on="Date", how="outer")
        .fillna(0)
        .sort_values("Date")
        .reset_index(drop=True)
    )

    merged["New Leads"] = merged["New Leads"].astype(int)
    merged["Conversions"] = merged["Conversions"].astype(int)

    return merged
