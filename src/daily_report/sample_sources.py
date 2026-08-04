"""
Generates synthetic sample data for the three input sources of the Daily
Report reconciliation workflow (Lead Source CSV, Payment/CC Export, Call
Log Import). Used both by the "Load sample data" buttons in the Streamlit
page and by tests, so the demo and the test suite share exactly the same
fixture-generation logic.
"""

import random
from datetime import datetime, timedelta

import pandas as pd

FIRST_NAMES = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis"]
SOURCES = ["Google Ads", "Facebook Ads", "Referral", "Website", "Yelp", "Direct Mail"]


def _fake_name(rng):
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def generate_sample_sources(report_date=None, seed=7):
    """
    Returns (leads_df, payments_df, calls_df) for a single day, with
    deliberate, realistic discrepancies between them:
      - a few leads marked 'booked' with NO matching payment
        (payment still pending / not yet collected)
      - a payment with no matching lead (data entry error - orphan charge)
      - a call log entry with no matching lead (a call that was never
        logged as a lead - dropped from the funnel)
    """

    rng = random.Random(seed)
    report_date = report_date or datetime.now().date()

    lead_ids = [f"JOB-{1000 + i}" for i in range(14)]

    # --- Leads ---
    leads_rows = []
    booked_ids = rng.sample(lead_ids, 6)
    for job_id in lead_ids:
        status = "booked" if job_id in booked_ids else rng.choice(
            ["quoted", "voicemail", "no_answer", "cancelled"]
        )
        leads_rows.append({
            "Job #": job_id,
            "Customer Name": _fake_name(rng),
            "Source": rng.choice(SOURCES),
            "Status": status,
            "Quoted Amount": round(rng.uniform(500, 2500), 2) if status != "voicemail" else 0,
        })
    leads_df = pd.DataFrame(leads_rows)

    # --- Payments: most booked leads get paid, one or two don't (still
    # pending), plus one orphan payment with no matching lead at all. ---
    payments_rows = []
    unpaid_ids = set(rng.sample(booked_ids, 2))
    for job_id in booked_ids:
        if job_id in unpaid_ids:
            continue
        amount = round(rng.uniform(400, 2200), 2)
        payments_rows.append({
            "Job #": job_id,
            "Amount": amount,
            "Method": rng.choice(["Credit Card", "ACH", "Cash"]),
        })
    payments_rows.append({
        "Job #": "JOB-9999",  # orphan: no matching lead
        "Amount": round(rng.uniform(400, 1200), 2),
        "Method": "Credit Card",
    })
    payments_df = pd.DataFrame(payments_rows)

    # --- Calls: one call for most leads, plus one call with no lead record ---
    calls_rows = []
    for job_id in lead_ids:
        if rng.random() < 0.85:
            calls_rows.append({
                "Job #": job_id,
                "Duration (min)": rng.randint(1, 22),
                "Agent": rng.choice(["Agent A", "Agent B", "Agent C"]),
            })
    calls_rows.append({
        "Job #": "JOB-8888",  # untracked: no matching lead
        "Duration (min)": rng.randint(1, 10),
        "Agent": "Agent B",
    })
    calls_df = pd.DataFrame(calls_rows)

    return leads_df, payments_df, calls_df
