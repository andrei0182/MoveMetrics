from src.processing.build_clean_jobs import build_clean_jobs_from_df


def calculate_financials(df):
    """
    KPI financiare pe baza jobului deduplicat (un rand per Job #).
    Foloseste acelasi pipeline ca build_clean_jobs, ca sa nu mai
    diverga doua implementari ale aceleiasi logici de deduplicare.
    """

    final = build_clean_jobs_from_df(df)

    revenue = final["Charged"].sum()
    cost = final["Cost"].sum()
    profit = revenue - cost

    margin = 0.0
    if revenue > 0:
        margin = (profit / revenue) * 100

    return {
        "Revenue": round(revenue, 2),
        "Cost": round(cost, 2),
        "Profit": round(profit, 2),
        "Margin %": round(margin, 2),
        "Jobs": final["Job #"].nunique(),
    }
