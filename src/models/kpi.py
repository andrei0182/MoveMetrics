from src.utils.money import clean_money_series


def calculate_kpis(jobs_df):
    """
    Calculeaza KPI la nivel de JOB, nu la nivel de RAND.

    ATENTIE: functia primeste un df deja deduplicat (un rand per Job #,
    de ex. output-ul build_clean_jobs_from_df). Daca i se da df-ul brut
    din raport (mai multe randuri per job), 'Average Job Value' iese
    gresit, pentru ca df.mean() se calculeaza pe randuri, nu pe joburi.

    Coloanele vechi cerute aici ("Total job (iulie)", "Rest de incasat",
    "De verificat") nu exista in sheet-ul CHARGED real din Report_JUL.xlsx
    (coloanele reale sunt: Job #, Nume Client, Sursa, Data, Status,
    Charged, Deposit, Cost) - functia pica garantat la orice apel real.
    Inlocuite cu KPI calculabile din datele care exista efectiv.
    """

    data = jobs_df.copy()

    if "Charged" in data.columns:
        data["Charged"] = clean_money_series(data["Charged"])
    else:
        data["Charged"] = 0.0

    kpis = {}

    total_jobs = data["Job #"].nunique() if "Job #" in data.columns else len(data)
    total_charged = data["Charged"].sum()

    kpis["Total Charged"] = total_charged
    kpis["Total Jobs"] = total_jobs

    kpis["Average Job Value"] = (
        total_charged / total_jobs if total_jobs > 0 else 0.0
    )

    if "Charged" in data.columns:
        kpis["Refunds"] = int((data["Charged"] < 0).sum())
    else:
        kpis["Refunds"] = 0

    # Valoare oferite (Deposit) pentru joburi care inca nu au Charged >0,
    # adica pipeline necovertit inca in incasare - cel mai apropiat
    # echivalent calculabil de "Outstanding" din datele disponibile.
    if "Deposit" in data.columns:
        pipeline_mask = data["Charged"] <= 0
        kpis["Pipeline necovertit (Deposit/Quote)"] = (
            clean_money_series(data.loc[pipeline_mask, "Deposit"]).sum()
        )
    else:
        kpis["Pipeline necovertit (Deposit/Quote)"] = 0.0

    return kpis
