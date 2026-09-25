"""
CivicPulse AI
Intelligent Complaint Management & Resolution Analytics Platform

Main Streamlit Application Entrypoint.
Handles routing, navigation, sidebar tools, and initial setup.
"""

import streamlit as st
import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from data.sample_data import seed_sample_data
from utils.ui_components import inject_custom_css
from views.submit_view import render_submit_view
from views.tracker_view import render_tracker_view
from views.admin_view import render_admin_view
from views.analytics_view import render_analytics_view
from views.reports_view import render_reports_view


def main():
    # 1. Page Configuration
    st.set_page_config(
        page_title="CivicPulse AI - Grievance Management & Analytics",
        page_icon="🏛️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 2. Inject Custom Theme & CSS
    inject_custom_css()

    # 3. Initialize Database and auto-seed sample records on first run
    db = get_db()
    seed_sample_data(db, force=False)

    # 4. Sidebar Navigation & Branding
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 10px 0 16px 0;">
                <h2 style="margin: 0; color: #1E293B; font-weight: 800; font-size: 1.5rem;">🏛️ CivicPulse AI</h2>
                <p style="margin: 4px 0 0 0; color: #64748B; font-size: 0.8rem; font-weight: 500;">
                    Intelligent Grievance & Resolution Platform
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        page_selection = st.radio(
            "Navigation Menu",
            options=[
                "📝 Submit Complaint",
                "🔍 Track Complaint",
                "🛡️ Admin Dashboard",
                "📊 Analytics & Hotspots",
                "📑 Reports & PDF Export"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("---")

        # System Information & Sample Data Tools
        st.markdown("##### ⚙️ System Controls")
        
        col_seed, col_reset = st.columns(2)
        with col_seed:
            if st.button("🌱 Re-Seed Data", use_container_width=True, help="Populate or refresh realistic sample complaint records."):
                count = seed_sample_data(db, force=True)
                st.success(f"Seeded {count} sample complaints!")
                st.rerun()

        with col_reset:
            if st.button("🗑️ Reset DB", use_container_width=True, help="Clear all complaints and start fresh."):
                db.reset_db()
                st.warning("Database cleared!")
                st.rerun()

        st.markdown("""
            <div style="background: #F1F5F9; border-radius: 8px; padding: 10px; margin-top: 20px; font-size: 0.75rem; color: #475569;">
                <b>🚀 Tech Stack & Engine:</b><br/>
                &bull; Python 3.11+ / Streamlit<br/>
                &bull; scikit-learn TF-IDF + Cosine Similarity<br/>
                &bull; Deterministic Priority Rules Engine<br/>
                &bull; SQLite Parameterized Storage<br/>
                &bull; ReportLab PDF Docket Engine<br/>
                &bull; Plotly Interactive Analytics
            </div>
        """, unsafe_allow_html=True)

    # 5. Route to Selected View
    if page_selection == "📝 Submit Complaint":
        render_submit_view()
    elif page_selection == "🔍 Track Complaint":
        render_tracker_view()
    elif page_selection == "🛡️ Admin Dashboard":
        render_admin_view()
    elif page_selection == "📊 Analytics & Hotspots":
        render_analytics_view()
    elif page_selection == "📑 Reports & PDF Export":
        render_reports_view()


if __name__ == "__main__":
    main()
