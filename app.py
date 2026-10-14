import os
import sys

from dotenv import load_dotenv
import streamlit as st


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


st.set_page_config(
    page_title="CivicPulse AI — Intelligent Grievance Platform",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.ui_components import inject_custom_css
from views.submit_view import render_submit_view
from views.tracker_view import render_tracker_view
from views.admin_view import render_admin_view
from views.analytics_view import render_analytics_view
from views.reports_view import render_reports_view

# Inject the global design system & custom CSS
inject_custom_css()


with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:12px 0 18px 0;">
            <div style="
                display:inline-flex;
                align-items:center;
                justify-content:center;
                width:58px;
                height:58px;
                border-radius:16px;
                background:linear-gradient(135deg,#2563EB 0%,#6366F1 50%,#8B5CF6 100%);
                box-shadow:0 6px 20px rgba(99,102,241,0.4);
                font-size:1.85rem;
                margin-bottom:10px;
            ">
                🏛️
            </div>
            <div style="
                font-family:'Poppins', sans-serif;
                font-size:1.35rem;
                font-weight:700;
                color:#FFFFFF;
                letter-spacing:-0.02em;
            ">
                CivicPulse AI
            </div>
            <div style="
                display:inline-flex;
                align-items:center;
                gap:5px;
                background:rgba(255,255,255,0.08);
                border:1px solid rgba(255,255,255,0.15);
                border-radius:20px;
                padding:2px 10px;
                font-size:0.72rem;
                font-weight:600;
                color:#CBD5E1;
                margin-top:6px;
                letter-spacing:0.04em;
            ">
                <span style="width:6px;height:6px;border-radius:50%;background:#10B981;display:inline-block;box-shadow:0 0 8px #10B981;"></span>
                ENTERPRISE v2.4
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "📝 Submit Complaint",
            "🔍 Track Complaint",
            "🛡️ Admin Dashboard",
            "📊 Analytics & Hotspots",
            "📑 Reports & PDF Export"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown(
        """
        <div style="
            background:rgba(255,255,255,0.05);
            border:1px solid rgba(255,255,255,0.1);
            border-radius:12px;
            padding:12px 14px;
            margin-top:10px;
        ">
            <div style="
                display:flex;
                align-items:center;
                justify-content:space-between;
                font-size:0.75rem;
                font-weight:700;
                color:#94A3B8;
                text-transform:uppercase;
                letter-spacing:0.06em;
                margin-bottom:8px;
            ">
                <span>Infrastructure</span>
                <span style="color:#10B981;display:flex;align-items:center;gap:4px;">
                    <span style="width:6px;height:6px;border-radius:50%;background:#10B981;display:inline-block;"></span>
                    Live
                </span>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;">
                <span style="background:rgba(255,255,255,0.08);color:#E2E8F0;padding:2px 7px;border-radius:6px;font-size:0.7rem;font-weight:600;">FastAPI</span>
                <span style="background:rgba(255,255,255,0.08);color:#E2E8F0;padding:2px 7px;border-radius:6px;font-size:0.7rem;font-weight:600;">PostgreSQL</span>
                <span style="background:rgba(255,255,255,0.08);color:#E2E8F0;padding:2px 7px;border-radius:6px;font-size:0.7rem;font-weight:600;">TF-IDF AI</span>
                <span style="background:rgba(255,255,255,0.08);color:#E2E8F0;padding:2px 7px;border-radius:6px;font-size:0.7rem;font-weight:600;">Streamlit</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


if page == "📝 Submit Complaint":
    render_submit_view()

elif page == "🔍 Track Complaint":
    render_tracker_view()

elif page == "🛡️ Admin Dashboard":
    render_admin_view()

elif page == "📊 Analytics & Hotspots":
    render_analytics_view()

elif page == "📑 Reports & PDF Export":
    render_reports_view()


st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:60px;
        padding:24px;
        color:#94A3B8;
        font-size:0.82rem;
        border-top:1px solid #E2E8F0;
    ">
        <b>CivicPulse AI</b> • Intelligent Grievance Resolution & Hotspot Analytics Platform
    </div>
    """,
    unsafe_allow_html=True
)