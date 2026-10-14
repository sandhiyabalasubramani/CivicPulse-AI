"""
Analytics & Problem Hotspot Intelligence View for CivicPulse AI.
Provides interactive Plotly visualizations, department workload breakdown,
resolution time metrics, and data-driven hotspot analytics.
"""

from html import escape
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.api_client import api_client
from utils.ui_components import render_header, render_metric_card


def render_analytics_view():
    """Renders the executive analytics and problem hotspots dashboard."""
    render_header(
        title="Resolution Analytics & Problem Hotspot Intelligence",
        subtitle="Data-driven intelligence to uncover recurring operational failures, bottleneck divisions, and resolution trends.",
        icon="📊",
        badge="Executive Hotspot Intelligence"
    )

    if not api_client.check_health():
        st.error(
            f"⚠️ Unable to connect to CivicPulse AI backend service ({api_client.base_url}). "
            "Please ensure the FastAPI service is running."
        )
        return

    try:
        df = api_client.get_all_complaints()
    except Exception as e:
        st.error(f"⚠️ Failed to retrieve complaints from backend: {str(e)}")
        return

    if df.empty:
        st.info(
            "ℹ️ No complaint records found in database. "
            "Seed sample data or submit complaints to explore analytics."
        )
        return

    # Helper for Plotly styling
    def _apply_plotly_theme(fig, title_text: str):
        fig.update_layout(
            title=dict(
                text=f"<b>{title_text}</b>",
                font=dict(family="Poppins, sans-serif", size=15, color="#0F172A")
            ),
            font=dict(family="Inter, sans-serif", size=12, color="#475569"),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=46, b=10),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        )
        return fig

    # ============================================================
    # 1. HOTSPOT INTELLIGENCE SECTION
    # ============================================================
    st.markdown(
        """
        <div style="font-family:'Poppins', sans-serif;font-size:1.25rem;font-weight:700;color:#0F172A;margin-bottom:12px;">
            🔥 Operational Hotspot Telemetry
        </div>
        """,
        unsafe_allow_html=True
    )

    # Most reported category
    top_category = (
        df["category"].mode()[0]
        if not df["category"].empty
        else "N/A"
    )
    top_cat_count = (
        df[df["category"] == top_category].shape[0]
        if top_category != "N/A"
        else 0
    )

    # Most affected location
    top_location = (
        df["location"].mode()[0]
        if not df["location"].empty
        else "N/A"
    )
    top_loc_count = (
        df[df["location"] == top_location].shape[0]
        if top_location != "N/A"
        else 0
    )

    # Most common subcategory
    top_subcat = (
        df["subcategory"].mode()[0]
        if not df["subcategory"].empty
        else "N/A"
    )
    top_subcat_count = (
        df[df["subcategory"] == top_subcat].shape[0]
        if top_subcat != "N/A"
        else 0
    )

    # Department backlog
    pending_dept_df = df[
        df["status"].isin(
            ["Pending", "Assigned", "In Progress"]
        )
    ]
    top_dept_backlog = (
        pending_dept_df["department"].mode()[0]
        if not pending_dept_df.empty
        else "None"
    )
    top_dept_backlog_cnt = (
        pending_dept_df[
            pending_dept_df["department"] == top_dept_backlog
        ].shape[0]
        if top_dept_backlog != "None"
        else 0
    )

    # HOTSPOT METRIC CARDS
    hcol1, hcol2, hcol3, hcol4 = st.columns(4)

    with hcol1:
        render_metric_card(
            "Top Category Incident",
            top_category,
            f"{top_cat_count} incidents recorded",
            "#EF4444",
            "🏷️"
        )

    with hcol2:
        render_metric_card(
            "Highest Frequency Location",
            top_location,
            f"{top_loc_count} incidents recorded",
            "#F97316",
            "📍"
        )

    with hcol3:
        render_metric_card(
            "Most Common Issue",
            top_subcat,
            f"{top_subcat_count} incidents recorded",
            "#2563EB",
            "🔍"
        )

    with hcol4:
        render_metric_card(
            "Division Queue Backlog",
            top_dept_backlog,
            f"{top_dept_backlog_cnt} active tickets",
            "#8B5CF6",
            "🏢"
        )

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ============================================================
    # 2. KEY VISUALIZATIONS
    # ============================================================
    st.markdown(
        """
        <div style="font-family:'Poppins', sans-serif;font-size:1.25rem;font-weight:700;color:#0F172A;margin-bottom:12px;">
            📈 Grievance Distribution & Trend Visualizations
        </div>
        """,
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    # CHART 1: COMPLAINTS BY CATEGORY
    with chart_col1:
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]

        fig_cat = px.bar(
            cat_counts,
            x="Count",
            y="Category",
            orientation="h",
            text="Count",
            color="Count",
            color_continuous_scale="Blues"
        )
        _apply_plotly_theme(fig_cat, "Complaints by Functional Category")
        fig_cat.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # CHART 2: PRIORITY DISTRIBUTION
    with chart_col2:
        prio_counts = df["priority"].value_counts().reset_index()
        prio_counts.columns = ["Priority", "Count"]

        color_map = {
            "Critical": "#EF4444",
            "High": "#F97316",
            "Medium": "#F59E0B",
            "Low": "#0EA5E9"
        }

        fig_prio = px.pie(
            prio_counts,
            names="Priority",
            values="Count",
            hole=0.45,
            color="Priority",
            color_discrete_map=color_map
        )
        _apply_plotly_theme(fig_prio, "Grievance Breakdown by Urgency Level")
        st.plotly_chart(fig_prio, use_container_width=True)

    # CHART 3 & 4
    chart_col3, chart_col4 = st.columns(2)

    # CHART 3: STATUS BREAKDOWN
    with chart_col3:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        status_colors = {
            "Pending": "#F59E0B",
            "Assigned": "#8B5CF6",
            "In Progress": "#2563EB",
            "Resolved": "#0D9488",
            "Closed": "#64748B"
        }

        fig_stat = px.bar(
            status_counts,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map=status_colors,
            text="Count"
        )
        _apply_plotly_theme(fig_stat, "Complaints by Resolution Stage")
        fig_stat.update_layout(showlegend=False)
        st.plotly_chart(fig_stat, use_container_width=True)

    # CHART 4: LOCATION FREQUENCY
    with chart_col4:
        loc_counts = df["location"].value_counts().head(7).reset_index()
        loc_counts.columns = ["Location", "Count"]

        fig_loc = px.bar(
            loc_counts,
            x="Count",
            y="Location",
            orientation="h",
            color="Count",
            color_continuous_scale="Purples",
            text="Count"
        )
        _apply_plotly_theme(fig_loc, "Top Affected Campus Facilities")
        fig_loc.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_loc, use_container_width=True)

    # ============================================================
    # 3. TIMELINE TRENDS
    # ============================================================
    st.markdown(
        """
        <div style="font-family:'Poppins', sans-serif;font-size:1.25rem;font-weight:700;color:#0F172A;margin-top:10px;margin-bottom:12px;">
            📅 Grievance Logging Velocity Over Time
        </div>
        """,
        unsafe_allow_html=True
    )

    df["date_only"] = pd.to_datetime(
        df["created_at"],
        format="mixed",
        errors="coerce"
    ).dt.date

    time_trend = (
        df.groupby("date_only")
        .size()
        .reset_index(name="Complaints Submitted")
    )

    fig_time = px.area(
        time_trend,
        x="date_only",
        y="Complaints Submitted",
        color_discrete_sequence=["#2563EB"],
        markers=True
    )
    _apply_plotly_theme(fig_time, "Daily Inflow of Grievance Submissions")
    fig_time.update_layout(
        xaxis_title="Date",
        yaxis_title="Tickets Logged"
    )
    st.plotly_chart(fig_time, use_container_width=True)

    # ============================================================
    # 4. DYNAMIC HOTSPOT STRATEGIC RECOMMENDATIONS
    # ============================================================
    st.markdown(
        """
        <div style="font-family:'Poppins', sans-serif;font-size:1.25rem;font-weight:700;color:#0F172A;margin-top:16px;margin-bottom:12px;">
            💡 Facility Management Insights & Action Items
        </div>
        """,
        unsafe_allow_html=True
    )

    category_recommendations = {
        "Electrical": "Schedule preventive inspections of electrical panels, wiring, circuit breakers, and laboratory power equipment.",
        "Security & Safety": "Inspect external campus illumination, CCTV monitoring points, and safety egress doors.",
        "Infrastructure & Civil": "Dispatch structural team to inspect affected corridors, waterproofing, and masonry fixtures.",
        "Equipment & Machinery": "Execute scheduled maintenance audits and replace worn components on reported devices.",
        "Network & IT": "Inspect access points, fiber switches, and bandwidth distribution in the flagged zone.",
        "Cleaning & Sanitation": "Increase janitorial patrol frequency and service waste-disposal points.",
        "Water & Plumbing": "Conduct pressure tests on supply mains, check valves, and repair restroom drainage fixtures.",
        "Other": "Conduct physical spot-check to define root cause of miscellaneous submissions."
    }

    recommended_action = category_recommendations.get(
        top_category,
        "Schedule a targeted inspection based on the recurring complaint pattern."
    )

    category_percentage = round((top_cat_count / len(df)) * 100, 1)

    insights_card_html = (
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:16px;padding:22px;box-shadow:0 4px 18px rgba(15,23,42,0.04);">'
        f'<div style="display:grid;gap:14px;">'
        f'<div style="display:flex;align-items:flex-start;gap:12px;background:#FEF2F2;border:1px solid #FECACA;border-radius:10px;padding:14px;">'
        f'<span style="font-size:1.3rem;">🔧</span>'
        f'<div>'
        f'<div style="font-weight:700;color:#991B1B;font-size:0.92rem;">Primary Category Vulnerability ({category_percentage}% of total)</div>'
        f'<div style="color:#7F1D1D;font-size:0.86rem;margin-top:2px;"><b>{escape(str(top_category))}</b> issues dominate submissions. {escape(recommended_action)}</div>'
        f'</div>'
        f'</div>'
        f'<div style="display:flex;align-items:flex-start;gap:12px;background:#FFF7ED;border:1px solid #FED7AA;border-radius:10px;padding:14px;">'
        f'<span style="font-size:1.3rem;">🏢</span>'
        f'<div>'
        f'<div style="font-weight:700;color:#9A3412;font-size:0.92rem;">Geographic Problem Cluster</div>'
        f'<div style="color:#7C2D12;font-size:0.86rem;margin-top:2px;">Repeated complaints cluster around <b>{escape(str(top_location))}</b> with {top_loc_count} logged incidents. Prioritize a structural site review.</div>'
        f'</div>'
        f'</div>'
        f'<div style="display:flex;align-items:flex-start;gap:12px;background:#F5F3FF;border:1px solid #DDD6FE;border-radius:10px;padding:14px;">'
        f'<span style="font-size:1.3rem;">⏱️</span>'
        f'<div>'
        f'<div style="font-weight:700;color:#5B21B6;font-size:0.92rem;">Departmental Queue Pressure</div>'
        f'<div style="color:#4C1D95;font-size:0.86rem;margin-top:2px;"><b>{escape(str(top_dept_backlog))}</b> maintains the largest open workload ({top_dept_backlog_cnt} active tickets). Reallocate field technicians to prevent SLA breaches.</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(insights_card_html, unsafe_allow_html=True)