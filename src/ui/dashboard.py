import streamlit as st

from src.pipeline import run_pipeline


def run_dashboard():
    """
    Doar afisare. Toata logica (loaders, cleaning, rules, analysis, KPIs)
    traieste in src/pipeline.py - acest modul nu stie si nu-i pasa de unde
    vin datele sau cum sunt calculate.
    """

    st.set_page_config(
        page_title="PFM Analytics Suite",
        layout="wide"
    )

    st.title("PFM Analytics Suite")
    st.subheader("Financial & Operational Dashboard")

    try:
        result = run_pipeline()
    except PermissionError as e:
        st.error(str(e))
        return

    st.caption(f"Sursa de date: {result['source']}")

    kpis = result["kpis"]
    provider_df = result["provider_df"]
    lead_funnel = result["lead_funnel"]

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
        st.caption("Conversion Rate per provider (%)")
        st.bar_chart(
            by_source.set_index("Sursa")["Conversion_Rate_%"]
        )

    with gcol2:
        st.caption("Cost per Conversie per provider ($)")
        cost_per_conversion = by_source[
            by_source["Cost_Per_Conversion"].notna()
        ]
        if len(cost_per_conversion) > 0:
            st.bar_chart(
                cost_per_conversion.set_index("Sursa")["Cost_Per_Conversion"]
            )
        else:
            st.info("Nicio sursa nu are conversii inca.")

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
        st.metric(
            "Pipeline necovertit",
            f"${kpis['Pipeline necovertit (Deposit/Quote)']:,.2f}"
        )

    st.divider()

    st.subheader("Revenue by Provider")
    st.bar_chart(provider_df.set_index("Sursa")["Revenue"])

    st.subheader("Provider Performance")
    st.dataframe(
        provider_df,
        use_container_width=True,
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
        use_container_width=True,
        column_config={
            "Cost": st.column_config.NumberColumn("Lead Cost", format="$%.2f"),
            "Cost_Per_Conversion": st.column_config.NumberColumn(
                "Cost per Conversie", format="$%.2f"
            ),
            "Conversion_Rate_%": st.column_config.NumberColumn(
                "Conversion Rate", format="%.2f%%"
            ),
        },
    )