"""
Monthly Reports - turns the current source data into a downloadable
Excel workbook with one sheet per day plus a consolidated TOTAL sheet,
matching the daily-tabs-plus-total convention many operations teams
already use for their monthly reporting.
"""

import streamlit as st

from src.monthly_report.excel_generator import generate_monthly_workbook
from src.pipeline import run_pipeline


st.title("Monthly Reports")
st.caption(
    "Exports the current dataset as a multi-tab Excel workbook: one sheet "
    "per calendar day, plus a TOTAL sheet with everything combined."
)

try:
    result = run_pipeline()
except PermissionError as e:
    st.error(str(e))
    st.stop()

st.caption(f"Data source: {result['source']}")

raw_df = result["raw_df"]

st.subheader("Source Data Preview")
st.dataframe(raw_df.head(20), width="stretch")
st.caption(f"{len(raw_df)} total rows")

st.divider()

if st.button("📦 Generate Monthly Workbook"):
    workbook_bytes = generate_monthly_workbook(raw_df, date_column="Date")
    st.session_state["monthly_workbook"] = workbook_bytes
    st.success("Workbook generated — one sheet per day, plus TOTAL.")

if "monthly_workbook" in st.session_state:
    st.download_button(
        "⬇ Download Workbook (Excel)",
        data=st.session_state["monthly_workbook"],
        file_name="monthly_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
