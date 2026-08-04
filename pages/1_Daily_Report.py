"""
Daily Report - multi-source reconciliation workflow.

Demonstrates a pattern common to any operations-heavy small business:
cross-checking leads, payments, and call activity for the day before
closing it out, and catching discrepancies (a booked job with no
payment, a payment with no matching lead, a call that never got
logged) before they turn into lost revenue or a missed follow-up.

Accepts real CSV uploads, or a "Load sample data" button per source
for a quick, self-contained demo.
"""

from io import BytesIO

import pandas as pd
import streamlit as st

from src.daily_report.reconciliation import reconcile
from src.daily_report.sample_sources import generate_sample_sources


st.title("Daily Report")
st.caption(
    "Multi-source reconciliation: cross-check leads, payments, and calls "
    "before closing out the day. Upload your own CSVs, or load sample data."
)

SOURCE_SPECS = {
    "leads": {
        "title": "📄 Lead Source CSV",
        "hint": "Expected columns: Job #, Customer Name, Source, Status, Quoted Amount",
    },
    "payments": {
        "title": "💳 Payment / CC Export",
        "hint": "Expected columns: Job #, Amount, Method",
    },
    "calls": {
        "title": "📞 Call Log Import",
        "hint": "Expected columns: Job #, Duration (min), Agent",
    },
}


def _load_all_samples():
    leads, payments, calls = generate_sample_sources()
    st.session_state["leads_df"] = leads
    st.session_state["payments_df"] = payments
    st.session_state["calls_df"] = calls


def _source_block(key):
    spec = SOURCE_SPECS[key]

    st.subheader(spec["title"])

    uploaded = st.file_uploader(
        f"Upload CSV", type="csv", key=f"upload_{key}", label_visibility="collapsed"
    )

    if uploaded is not None:
        st.session_state[f"{key}_df"] = pd.read_csv(uploaded)

    df = st.session_state.get(f"{key}_df")

    if df is not None:
        st.success(f"{len(df)} rows loaded")
        st.dataframe(df, width="stretch", height=150)
    else:
        st.info(spec["hint"])

    return df


st.button("⚡ Load sample data for all three sources", on_click=_load_all_samples)

col1, col2, col3 = st.columns(3)

with col1:
    leads_df = _source_block("leads")

with col2:
    payments_df = _source_block("payments")

with col3:
    calls_df = _source_block("calls")

st.divider()

st.subheader("✅ Team Verification")

v1 = st.checkbox("Payments verified against bank/CC statement")
v2 = st.checkbox("Leads verified against source platform")
v3 = st.checkbox("Call log verified against phone system")

all_loaded = leads_df is not None and payments_df is not None and calls_df is not None
all_verified = v1 and v2 and v3

st.divider()

generate_clicked = st.button(
    "▶️ Generate Report", disabled=not (all_loaded and all_verified)
)

if generate_clicked:
    st.session_state["report_result"] = reconcile(leads_df, payments_df, calls_df)

if not all_loaded:
    st.warning("Load all three data sources above before generating the report.")
elif not all_verified:
    st.warning("Complete team verification above before generating the report.")

if "report_result" in st.session_state:
    result = st.session_state["report_result"]

    st.divider()
    st.subheader("📊 Daily Summary")

    summary = result["date_summary"]
    cols = st.columns(len(summary))
    for col, (label, value) in zip(cols, summary.items()):
        if label == "Revenue":
            col.metric(label, f"${value:,.2f}")
        else:
            col.metric(label, value)

    if result["is_clean"]:
        st.success("No discrepancies found — everything reconciles cleanly.")
    else:
        if result["missing_payments"]:
            st.error(
                "Booked leads with no matching payment: "
                + ", ".join(result["missing_payments"])
            )
        if result["orphan_payments"]:
            st.error(
                "Payments with no matching lead record: "
                + ", ".join(result["orphan_payments"])
            )
        if result["untracked_calls"]:
            st.warning(
                "Calls with no matching lead: " + ", ".join(result["untracked_calls"])
            )

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([summary]).to_excel(writer, sheet_name="Summary", index=False)
        pd.DataFrame({
            "Missing Payments": pd.Series(result["missing_payments"]),
            "Orphan Payments": pd.Series(result["orphan_payments"]),
            "Untracked Calls": pd.Series(result["untracked_calls"]),
        }).to_excel(writer, sheet_name="Discrepancies", index=False)

    st.download_button(
        "⬇ Download Report (Excel)",
        data=output.getvalue(),
        file_name="daily_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
