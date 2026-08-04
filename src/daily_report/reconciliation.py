"""
Cross-references leads, payments, and call log entries by Job # and
flags discrepancies - the core value of a "daily report" workflow for
any operations-heavy small business: catching what didn't line up
before it becomes a lost payment or a forgotten follow-up.

Pure function, no I/O, no Streamlit - fully testable in isolation.
"""

from src.utils.money import clean_money_series


def reconcile(leads_df, payments_df, calls_df):

    leads = leads_df.copy()
    payments = payments_df.copy()
    calls = calls_df.copy()

    if "Amount" in payments.columns:
        payments["Amount"] = clean_money_series(payments["Amount"])

    lead_ids = set(leads["Job #"]) if "Job #" in leads.columns else set()
    payment_ids = set(payments["Job #"]) if "Job #" in payments.columns else set()
    call_ids = set(calls["Job #"]) if "Job #" in calls.columns else set()

    booked_ids = set(
        leads.loc[leads["Status"] == "booked", "Job #"]
    ) if "Status" in leads.columns else set()

    # Booked leads with no matching payment - money that should have
    # come in but hasn't (or a payment that was never recorded).
    missing_payments = sorted(booked_ids - payment_ids)

    # Payments with no matching lead record at all - a data-entry error
    # or a charge that was never logged as a lead in the first place.
    orphan_payments = sorted(payment_ids - lead_ids)

    # Calls with no matching lead - a call that never got logged /
    # tracked into the funnel.
    untracked_calls = sorted(call_ids - lead_ids)

    total_leads = len(lead_ids)
    total_booked = len(booked_ids)
    total_revenue = payments["Amount"].sum() if "Amount" in payments.columns else 0.0
    total_calls = len(call_ids)

    is_clean = not (missing_payments or orphan_payments or untracked_calls)

    return {
        "date_summary": {
            "Total Leads": total_leads,
            "Booked": total_booked,
            "Payments Received": len(payment_ids),
            "Revenue": round(total_revenue, 2),
            "Calls Logged": total_calls,
        },
        "missing_payments": missing_payments,
        "orphan_payments": orphan_payments,
        "untracked_calls": untracked_calls,
        "is_clean": is_clean,
    }
