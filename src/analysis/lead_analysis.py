from src.utils.money import clean_money_series


def analyze_leads(jobs_df):
    """
    Analiza funnel-ului de leaduri, pe baza jobs_df (deja deduplicat pe
    Job #, cu ultimul status si Charged/Cost insumate pe fiecare lead).

    Distinctie importanta: jobs_df contine TOATE leadurile unice, indiferent
    de status (voicemail, cancelled, booked...) - nu doar cele convertite.
    "Converted" = leadurile care au adus bani reali (Charged > 0).

    Cost_Per_Conversion = cat a costat, in medie, sa obtii UN job convertit
    de la o sursa (Cost total al sursei / numar de conversii). Daca o sursa
    are 0 conversii, e "fara conversii" (nu 0$ sau infinit) - se afiseaza
    separat, ca sa nu induca in eroare un cost per conversie de 0.
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

    by_status = (
        data["Status"]
        .value_counts()
        .reset_index()
    )
    by_status.columns = ["Status", "Leads"]

    by_source = (
        data
        .groupby("Sursa")
        .agg(
            Leads=("Job #", "nunique"),
            Cost=("Cost", "sum"),
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

    # Cost per conversie: doar acolo unde exista cel putin o conversie -
    # altfel ar aparea fals ca "0$ per conversie" pentru surse fara conversii.
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