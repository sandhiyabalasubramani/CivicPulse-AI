"""
Analytics & Problem Hotspot Intelligence View for CivicPulse AI.
Provides interactive Plotly visualizations, department workload breakdown,
resolution time metrics, and data-driven hotspot analytics.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.database import get_db
from utils.ui_components import render_header, render_metric_card


def render_analytics_view():
    """Renders the executive analytics and problem hotspots dashboard."""
    render_header(
        title="Resolution Analytics & Problem Hotspot Intelligence",
        subtitle="Data-driven insights to uncover recurring failures, bottleneck departments, and resolution performance.",
        icon="📊"
    )

    db = get_db()
    df = db.get_all_complaints()

    if df.empty:
        st.info("ℹ️ No complaint records found in database. Seed sample data from the sidebar to explore analytics.")
        return

    # 1. Hotspot Intelligence Section
    st.markdown("### 🔥 Problem Hotspot Analysis")
    
    # Calculate hotspots dynamically from DB data
    top_category = df["category"].mode()[0] if not df["category"].empty else "N/A"
    top_cat_count = df[df["category"] == top_category].shape[0] if top_category != "N/A" else 0

    top_location = df["location"].mode()[0] if not df["location"].empty else "N/A"
    top_loc_count = df[df["location"] == top_location].shape[0] if top_location != "N/A" else 0

    top_subcat = df["subcategory"].mode()[0] if not df["subcategory"].empty else "N/A"
    top_subcat_count = df[df["subcategory"] == top_subcat].shape[0] if top_subcat != "N/A" else 0

    pending_dept_df = df[df["status"].isin(["Pending", "Assigned", "In Progress"])]
    top_dept_backlog = pending_dept_df["department"].mode()[0] if not pending_dept_df.empty else "None"
    top_dept_backlog_cnt = pending_dept_df[pending_dept_df["department"] == top_dept_backlog].shape[0] if top_dept_backlog != "None" else 0

    hcol1, hcol2, hcol3, hcol4 = st.columns(4)
    with hcol1:
        render_metric_card("Most Reported Category", top_category, f"{top_cat_count} incidents recorded", "#DC2626")
    with hcol2:
        render_metric_card("Most Affected Location", top_location, f"{top_loc_count} incidents recorded", "#EA580C")
    with hcol3:
        render_metric_card("Most Common Issue", top_subcat, f"{top_subcat_count} incidents recorded", "#2563EB")
    with hcol4:
        render_metric_card("Top Department Queue", top_dept_backlog, f"{top_dept_backlog_cnt} active tickets", "#7C3AED")

    st.write("")

    # 2. Key Visualizations Grid
    st.markdown("### 📈 Grievance Distribution & Trend Visualizations")

    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: Complaints by Category
    with chart_col1:
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_cat = px.bar(
            cat_counts,
            x="Count",
            y="Category",
            orientation="h",
            title="<b>Complaints by Category</b>",
            color="Count",
            color_continuous_scale="Blues",
            text="Count"
        )
        fig_cat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # Chart 2: Priority Distribution Donut
    with chart_col2:
        prio_counts = df["priority"].value_counts().reset_index()
        prio_counts.columns = ["Priority", "Count"]
        
        color_map = {
            "Critical": "#DC2626",
            "High": "#EA580C",
            "Medium": "#2563EB",
            "Low": "#64748B"
        }
        
        fig_prio = px.pie(
            prio_counts,
            names="Priority",
            values="Count",
            title="<b>Complaints by Priority Level</b>",
            hole=0.45,
            color="Priority",
            color_discrete_map=color_map
        )
        fig_prio.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig_prio, use_container_width=True)

    chart_col3, chart_col4 = st.columns(2)

    # Chart 3: Status Breakdown
    with chart_col3:
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        status_colors = {
            "Pending": "#F59E0B",
            "Assigned": "#6366F1",
            "In Progress": "#3B82F6",
            "Resolved": "#10B981",
            "Closed": "#475569"
        }
        fig_stat = px.bar(
            status_counts,
            x="Status",
            y="Count",
            title="<b>Complaints by Current Status</b>",
            color="Status",
            color_discrete_map=status_colors,
            text="Count"
        )
        fig_stat.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10),
            showlegend=False
        )
        st.plotly_chart(fig_stat, use_container_width=True)

    # Chart 4: Location Frequency
    with chart_col4:
        loc_counts = df["location"].value_counts().head(7).reset_index()
        loc_counts.columns = ["Location", "Count"]
        fig_loc = px.bar(
            loc_counts,
            x="Count",
            y="Location",
            orientation="h",
            title="<b>Top Affected Campus Locations</b>",
            color="Count",
            color_continuous_scale="Reds",
            text="Count"
        )
        fig_loc.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_loc, use_container_width=True)

    # Chart 5: Timeline Trends
    st.markdown("### 📅 Grievance Logging & Resolution Trends Over Time")
    df["date_only"] = pd.to_datetime(df["created_at"]).dt.date
    time_trend = df.groupby("date_only").size().reset_index(name="Complaints Submitted")
    
    fig_time = px.area(
        time_trend,
        x="date_only",
        y="Complaints Submitted",
        title="<b>Daily Inflow of Grievance Submissions</b>",
        color_discrete_sequence=["#2563EB"],
        markers=True
    )
    fig_time.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title="Date",
        yaxis_title="Tickets Logged"
    )
    st.plotly_chart(fig_time, use_container_width=True)

    # Hotspot Strategic Recommendations
    st.markdown("### 💡 Facility Management Insights & Action Items")
    st.markdown(f"""
        - ⚡ **Electrical Infrastructure Alert:** `{top_category}` constitutes the largest share of issues ({round((top_cat_count/len(df))*100, 1)}% of total complaints). Proactive preventive maintenance checks on fan capacitors and switchboards in `{top_location}` are recommended.
        - 🏢 **Location Concentration:** Hotspot analysis reveals repeated complaints originate from `{top_location}`. A targeted physical inspection of this facility could preempt further tickets.
        - ⏱️ **Department Workload:** `{top_dept_backlog}` currently has the highest open queue of unresolved tickets. Resource reallocation or specialized technician assignment is advised.
    """)
