def calculate_financials(jobs_df):
    """
    KPI financiare (Revenue/Cost/Profit/Margin) pe baza jobului deja
    curat si deja trecut prin regulile de business (jobs_df vine din
    pipeline.py, nu direct din Excel/Sheets).

    Acest modul NU citeste Excel si NU curata date - doar agrega.
    """

    revenue = jobs_df["Charged"].sum()
    cost = jobs_df["Cost"].sum()
    profit = revenue - cost

    margin = 0.0
    if revenue > 0:
        margin = (profit / revenue) * 100

    return {
        "Revenue": round(revenue, 2),
        "Cost": round(cost, 2),
        "Profit": round(profit, 2),
        "Margin %": round(margin, 2),
        "Jobs": jobs_df["Job #"].nunique(),
    }
