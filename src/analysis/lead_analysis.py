from src.utils.money import clean_money_series


def analyze_leads(jobs_df):
    """
    Lead funnel analysis, on top of jobs_df (already deduplicated by
    Job #, with the last known status and total Charged/Cost per lead).

    Important distinction: jobs_df contains ALL unique leads, regardless
    of status (voicemail, cancelled, booked...), not just the converted
    ones. "Converted" = leads that generated real revenue (Charged > 0).

    Cost_Per_Conversion = average cost to acquire ONE converted job from
    a given source (that source's total Cost / number of conversions).
    Left as None when a source has zero conversions, instead of 0 or
    infinity, so it doesn't misleadingly read as "free."
    """

    data = jobs_df.copy()

    if "Cost" in data.columns:
        data["Cost"] = clean_money_series(data["Cost"])
    else:
        data["Cost"] = 0.0

    total_leads = data["Job #"].nunique()

    converted_mask = data["Charged"] > 0
    converted_df = data[converted_mask]
    total_converted = converted_df["Job #"].nunique()

    conversion_rate = 0.0
    if total_leads > 0:
        conversion_rate = total_converted / total_leads * 100

    by_status = data["Status"].value_counts().reset_index()
    by_status.columns = ["Status", "Leads"]

    by_source = (
        data
        .groupby("Source")
        .agg(
            Leads=("Job #", "nunique"),
            Cost=("Cost", "sum"),
        )
        .reset_index()
    )

    converted_by_source = (
        converted_df
        .groupby("Source")["Job #"]
        .nunique()
        .reset_index(name="Converted")
    )

    by_source = by_source.merge(converted_by_source, on="Source", how="left")
    by_source["Converted"] = by_source["Converted"].fillna(0).astype(int)

    by_source["Conversion_Rate_%"] = 0.0
    leads_mask = by_source["Leads"] > 0
    by_source.loc[leads_mask, "Conversion_Rate_%"] = (
        by_source.loc[leads_mask, "Converted"]
        / by_source.loc[leads_mask, "Leads"]
        * 100
    )

    by_source["Cost_Per_Conversion"] = None
    converted_mask_source = by_source["Converted"] > 0
    by_source.loc[converted_mask_source, "Cost_Per_Conversion"] = (
        by_source.loc[converted_mask_source, "Cost"]
        / by_source.loc[converted_mask_source, "Converted"]
    )

    by_source = by_source.sort_values(by="Conversion_Rate_%", ascending=False)

    return {
        "Total Leads": total_leads,
        "Converted": total_converted,
        "Conversion Rate %": round(conversion_rate, 2),
        "by_status": by_status,
        "by_source": by_source,
    }
