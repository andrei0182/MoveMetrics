import streamlit as st

from src.analysis.provider_analysis import analyze_providers
from src.excel.excel_loader import load_excel
from src.models.kpi import calculate_kpis


def run_dashboard():

    st.set_page_config(
        page_title="PFM Analytics Suite",
        layout="wide"
    )


    st.title(
        "PFM Analytics Suite"
    )

    st.subheader(
        "Financial & Operational Dashboard"
    )


    # Load data

    file = "data/raw/Report_JUL.xlsx"


    df = load_excel(
        file,
        "CHARGED "
    )
    
    provider_df = analyze_providers(df)
    

    kpis = calculate_kpis(df)


    # KPI cards

    col1, col2, col3 = st.columns(3)


    with col1:
        st.metric(
            "Total Charged",
            f"${kpis['Total Charged']:,.2f}"
        )


    with col2:
        st.metric(
            "Total Jobs",
            kpis["Total Jobs"]
        )


    with col3:
        st.metric(
            "Average Job",
            f"${kpis['Average Job Value']:,.2f}"
        )


    col4, col5 = st.columns(2)


    with col4:

        st.metric(
            "Refunds",
            kpis["Refunds"]
        )


    with col5:

        st.metric(
            "Outstanding",
            f"${kpis['Outstanding']:,.2f}"
        )


    st.divider()


    st.subheader(
        "Raw Data"
    )

    st.dataframe(
        df,
        use_container_width=True
    )
    st.divider()

    st.subheader(
        "Revenue by Provider"
    )

    st.bar_chart(
        provider_df.set_index("Sursa")["Revenue"]
    )


    st.subheader(
        "Provider Performance"
    )

    st.dataframe(
        provider_df,
        use_container_width=True
    )
