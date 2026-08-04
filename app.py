"""
Entry point: sets up page config once, then builds the sidebar navigation
explicitly (st.navigation), so every page - including the main dashboard -
gets a proper title, icon, and grouping, instead of relying on filenames.
"""

import streamlit as st

from src.ui.dashboard import run_dashboard


st.set_page_config(page_title="MoveMetrics", page_icon="📊", layout="wide")

pages = {
    "Analytics": [
        st.Page(run_dashboard, title="Business Dashboard", icon="📊", default=True),
        st.Page("pages/1_Daily_Report.py", title="Daily Report", icon="📅"),
        st.Page("pages/3_Monthly_Analytics.py", title="Monthly Analytics", icon="📈"),
        st.Page("pages/2_Monthly_Reports.py", title="Monthly Reports", icon="📦"),
    ],
    "General": [
        st.Page("pages/4_Settings.py", title="Settings", icon="⚙️"),
    ],
}

navigation = st.navigation(pages)
navigation.run()
