import os
import sys

from dotenv import load_dotenv
import streamlit as st


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


st.set_page_config(
    page_title="CivicPulse AI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)


from views.submit_view import render_submit_view
from views.tracker_view import render_tracker_view
from views.admin_view import render_admin_view
from views.analytics_view import render_analytics_view
from views.reports_view import render_reports_view


st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC;
    }

    section[data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    .civic-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #0F172A;
        margin-bottom: 0.2rem;
    }

    .civic-subtitle {
        font-size: 1rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }

    .cp-ai-card {
        background: white;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-top: 15px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    .cp-similarity-box {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-radius: 12px;
        padding: 15px;
        margin-top: 15px;
    }

    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding:10px 0 20px 0;
        ">
            <div style="
                font-size:3rem;
            ">
                🏛️
            </div>

            <div style="
                font-size:1.4rem;
                font-weight:800;
            ">
                CivicPulse AI
            </div>

            <div style="
                font-size:0.8rem;
                opacity:0.75;
                margin-top:4px;
            ">
                Intelligent Grievance Platform
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
            font-size:0.78rem;
            opacity:0.75;
            line-height:1.6;
        ">
            <b>⚙️ System</b><br><br>
            Python + Streamlit<br>
            FastAPI Backend<br>
            PostgreSQL Database<br>
            TF-IDF Similarity<br>
            AI-assisted Triage
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
        margin-top:50px;
        padding:20px;
        color:#94A3B8;
        font-size:0.8rem;
    ">
        CivicPulse AI • Intelligent Grievance & Resolution Platform
    </div>
    """,
    unsafe_allow_html=True
)