def calculate_financials(jobs_df):
    """
    Revenue/Cost/Profit/Margin, computed on the already-clean, already
    business-rules-applied job-level data (jobs_df comes from the
    pipeline, not straight from Excel/Sheets - this module doesn't read
    files and doesn't clean data.
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
