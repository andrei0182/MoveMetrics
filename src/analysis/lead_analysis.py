def analyze_leads(jobs_df):
    """
    Analiza funnel-ului de leaduri, pe baza jobs_df (deja deduplicat pe
    Job #, cu ultimul status si Charged insumat pe fiecare lead).

    Distinctie importanta: jobs_df contine TOATE leadurile unice, indiferent
    de status (voicemail, cancelled, booked...) - nu doar cele convertite.
    "Converted" = leadurile care au adus bani reali (Charged > 0).
    """

    total_leads = jobs_df["Job #"].nunique()

    converted_mask = jobs_df["Charged"] > 0
    converted_df = jobs_df[converted_mask]
    total_converted = converted_df["Job #"].nunique()

    conversion_rate = 0.0
    if total_leads > 0:
        conversion_rate = total_converted / total_leads * 100

    by_status = (
        jobs_df["Status"]
        .value_counts()
        .reset_index()
    )
    by_status.columns = ["Status", "Leads"]

    by_source = (
        jobs_df
        .groupby("Sursa")
        .agg(
            Leads=("Job #", "nunique"),
        )
        .reset_index()
    )

    converted_by_source = (
        converted_df
        .groupby("Sursa")["Job #"]
        .nunique()
        .reset_index(name="Converted")
    )

    by_source = by_source.merge(converted_by_source, on="Sursa", how="left")
    by_source["Converted"] = by_source["Converted"].fillna(0).astype(int)

    by_source["Conversion_Rate_%"] = 0.0
    leads_mask = by_source["Leads"] > 0
    by_source.loc[leads_mask, "Conversion_Rate_%"] = (
        by_source.loc[leads_mask, "Converted"]
        / by_source.loc[leads_mask, "Leads"]
        * 100
    )

    by_source = by_source.sort_values(by="Leads", ascending=False)

    return {
        "Total Leads": total_leads,
        "Converted": total_converted,
        "Conversion Rate %": round(conversion_rate, 2),
        "by_status": by_status,
        "by_source": by_source,
    }