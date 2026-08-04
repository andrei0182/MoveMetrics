"""
Monthly Analytics - day-by-day trends: revenue collected, new leads,
and conversions over the reporting period. Complements the aggregate
totals on the main Business Dashboard with a view of how the month
actually unfolded.
"""

import streamlit as st

from src.analysis.trend_analysis import analyze_trends
from src.pipeline import run_pipeline


st.title("Monthly Analytics")
st.caption("Day-by-day trends over the reporting period.")

try:
    result = run_pipeline()
except PermissionError as e:
    st.error(str(e))
    st.stop()

st.caption(f"Data source: {result['source']}")

trends = analyze_trends(result["raw_df"], date_column="Date")

if len(trends) == 0:
    st.info("No dated activity found in the current dataset.")
    st.stop()

trends_indexed = trends.set_index("Date")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Revenue", f"${trends['Revenue'].sum():,.2f}")

with col2:
    st.metric("Total New Leads", int(trends["New Leads"].sum()))

with col3:
    st.metric("Total Conversions", int(trends["Conversions"].sum()))

st.divider()

st.subheader("Revenue Over Time")
st.line_chart(trends_indexed["Revenue"])

col4, col5 = st.columns(2)

with col4:
    st.subheader("New Leads Over Time")
    st.line_chart(trends_indexed["New Leads"])

with col5:
    st.subheader("Conversions Over Time")
    st.line_chart(trends_indexed["Conversions"])

st.divider()

st.subheader("Daily Detail")
st.dataframe(
    trends,
    width="stretch",
    column_config={
        "Revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
    },
)
