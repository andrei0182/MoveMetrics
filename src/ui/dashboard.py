import altair as alt
import streamlit as st

from src.pipeline import run_pipeline


def _ordered_bar_chart(
    df, x_col, y_col, order, y_title=None, label_fmt=None, color_by_sign=False
):
    """
    Bar chart with:
    - EXPLICIT order on the x-axis (per `order`) - Streamlit's built-in
      st.bar_chart sorts string categories alphabetically and ignores the
      DataFrame's actual row order
    - a numeric label rendered directly on each bar (label_fmt = a Python
      function formatting the value, e.g. lambda v: f"${v:,.0f}")
    - optional green/red coloring by sign (used for Profit: green when
      a source is profitable, red when it's a net loss)
    """

    chart_df = df.copy()

    if label_fmt:
        chart_df["_label"] = chart_df[y_col].map(label_fmt)
    else:
        chart_df["_label"] = chart_df[y_col].astype(str)

    base = alt.Chart(chart_df).encode(
        x=alt.X(f"{x_col}:N", sort=order, title=None),
    )

    if color_by_sign:
        color = alt.condition(
            alt.datum[y_col] >= 0,
            alt.value("#2ecc71"),
            alt.value("#e74c3c"),
        )
        bars = base.mark_bar().encode(
            y=alt.Y(f"{y_col}:Q", title=y_title or y_col),
            color=color,
            tooltip=[x_col, y_col],
        )
    else:
        bars = base.mark_bar(color="#4C78A8").encode(
            y=alt.Y(f"{y_col}:Q", title=y_title or y_col),
            tooltip=[x_col, y_col],
        )

    text = base.mark_text(
        align="center", baseline="bottom", dy=-4, fontSize=11,
    ).encode(
        y=alt.Y(f"{y_col}:Q"),
        text="_label:N",
    )

    st.altair_chart(bars + text, width="stretch")


def run_dashboard():
    """
    Display only. All logic (loaders, cleaning, rules, analysis, KPIs)
    lives in src/pipeline.py - this module doesn't know or care where
    the data comes from or how it's computed.
    """

    st.title("MoveMetrics")
    st.subheader("Moving Company Analytics Suite")

    try:
        result = run_pipeline()
    except PermissionError as e:
        st.error(str(e))
        return

    st.caption(f"Data source: {result['source']} (synthetic - no real customer data)")

    kpis = result["kpis"]
    provider_df = result["provider_df"]
    lead_funnel = result["lead_funnel"]
    profit_order = result["profit_order"]

    st.subheader("Lead Pipeline")

    lcol1, lcol2, lcol3 = st.columns(3)

    with lcol1:
        st.metric("Total Leads", lead_funnel["Total Leads"])

    with lcol2:
        st.metric("Converted Jobs", lead_funnel["Converted"])

    with lcol3:
        st.metric("Conversion Rate", f"{lead_funnel['Conversion Rate %']:.2f}%")

    by_source = lead_funnel["by_source"]

    gcol1, gcol2 = st.columns(2)

    with gcol1:
        st.caption("Conversion Rate by Source (%)")
        _ordered_bar_chart(
            by_source, "Source", "Conversion_Rate_%", profit_order,
            y_title="Conversion Rate %",
            label_fmt=lambda v: f"{v:.1f}%",
        )

    with gcol2:
        st.caption("Cost per Conversion by Source ($)")
        cost_per_conversion = by_source[by_source["Cost_Per_Conversion"].notna()]
        if len(cost_per_conversion) > 0:
            _ordered_bar_chart(
                cost_per_conversion, "Source", "Cost_Per_Conversion", profit_order,
                y_title="Cost per Conversion ($)",
                label_fmt=lambda v: f"${v:,.0f}",
            )
        else:
            st.info("No source has any conversions yet.")

    st.divider()

    st.subheader("Financial")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Charged", f"${kpis['Total Charged']:,.2f}")

    with col2:
        st.metric("Total Jobs", kpis["Total Jobs"])

    with col3:
        st.metric("Average Job", f"${kpis['Average Job Value']:,.2f}")

    col4, col5 = st.columns(2)

    with col4:
        st.metric("Refunds", kpis["Refunds"])

    with col5:
        st.metric("Open Pipeline", f"${kpis['Open Pipeline (Deposit/Quote)']:,.2f}")

    st.divider()

    st.subheader("Profit by Source")
    st.caption("Sorted from most profitable to net loss · green = profit, red = loss")
    _ordered_bar_chart(
        provider_df, "Source", "Profit", profit_order,
        y_title="Profit ($)",
        label_fmt=lambda v: f"${v:,.0f}",
        color_by_sign=True,
    )

    st.subheader("Source Performance")
    st.dataframe(
        provider_df,
        width="stretch",
        column_config={
            "Revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
            "Cost": st.column_config.NumberColumn("Lead Cost", format="$%.2f"),
            "Profit": st.column_config.NumberColumn("Profit", format="$%.2f"),
            "Average_Job": st.column_config.NumberColumn("Average Job", format="$%.2f"),
            "Margin_%": st.column_config.NumberColumn("Margin %", format="%.2f%%"),
            "Revenue_%": st.column_config.NumberColumn("Revenue %", format="%.2f%%"),
        },
    )

    st.subheader("Conversion by Source")
    st.dataframe(
        lead_funnel["by_source"],
        width="stretch",
        column_config={
            "Cost": st.column_config.NumberColumn("Lead Cost", format="$%.2f"),
            "Cost_Per_Conversion": st.column_config.NumberColumn(
                "Cost per Conversion", format="$%.2f"
            ),
            "Conversion_Rate_%": st.column_config.NumberColumn(
                "Conversion Rate", format="%.2f%%"
            ),
        },
    )
