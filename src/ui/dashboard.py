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
    jobs_df = result["jobs_df"]

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

    st.subheader("Joburi (deduplicate)")
    st.dataframe(jobs_df, use_container_width=True)

    st.divider()

    st.subheader("Revenue by Provider")
    st.bar_chart(provider_df.set_index("Sursa")["Revenue"])

    st.subheader("Provider Performance")
    st.dataframe(
        provider_df,
        use_container_width=True,
        column_config={
            "Revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
            "Average_Job": st.column_config.NumberColumn("Average Job", format="$%.2f"),
            "Revenue_%": st.column_config.NumberColumn("Revenue %", format="%.2f%%"),
        },
    )