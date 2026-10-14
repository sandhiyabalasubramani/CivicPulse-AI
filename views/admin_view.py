"""
Admin Complaint Management View for CivicPulse AI.
Provides multi-criteria search & filtering, live KPI counters,
complaint inspection, status update workflows, and audit trail logging.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api_client import api_client
from modules.report_generator import create_complaint_docket_pdf
from modules.department_router import get_department_router
from utils.ui_components import (
    render_header,
    render_metric_card,
    get_status_badge_html,
    get_priority_badge_html,
    render_timeline
)


def render_admin_view():
    """Renders the administrative complaint management dashboard."""
    render_header(
        title="Admin Complaint Management & Operations",
        subtitle="Filter, inspect, route, and update status of all submitted institutional grievances.",
        icon="🛡️"
    )

    if not api_client.check_health():
        st.error(
            f"⚠️ Unable to connect to CivicPulse AI backend service ({api_client.base_url}). "
            "Please ensure the FastAPI service is running."
        )
        return

    router = get_department_router()

    # 1. Top KPI Summary Row
    try:
        kpis = api_client.get_kpis()
    except Exception as e:
        st.error(f"⚠️ Error fetching complaint metrics from backend: {str(e)}")
        kpis = {}

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        render_metric_card(
            "Total Logged",
            kpis.get("total", 0),
            "All time grievances",
            "#1E293B"
        )

    with col2:
        render_metric_card(
            "Pending",
            kpis.get("pending", 0),
            "Awaiting triage",
            "#D97706"
        )

    with col3:
        render_metric_card(
            "Assigned",
            kpis.get("assigned", 0),
            "Routed to department",
            "#7C3AED"
        )

    with col4:
        render_metric_card(
            "In Progress",
            kpis.get("in_progress", 0),
            "Under active resolution",
            "#2563EB"
        )

    with col5:
        render_metric_card(
            "Resolved",
            kpis.get("resolved", 0),
            f"{kpis.get('resolution_rate', 0)}% resolution rate",
            "#16A34A"
        )

    with col6:
        render_metric_card(
            "Critical / High",
            kpis.get("critical_priority", 0) + kpis.get("high_priority", 0),
            "High urgency tickets",
            "#DC2626"
        )

    st.write("")

    # 2. Filters Bar
    with st.expander("🔍 Search & Filter Complaints", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)

        try:
            categories = ["All"] + api_client.get_distinct_values("category")
        except Exception:
            categories = ["All"]

        priorities = ["All", "Critical", "High", "Medium", "Low"]
        statuses = ["All", "Pending", "Assigned", "In Progress", "Resolved", "Closed"]

        try:
            locations = ["All"] + api_client.get_distinct_values("location")
        except Exception:
            locations = ["All"]

        with fcol1:
            filter_search = st.text_input(
                "Text Search",
                placeholder="ID, keyword, name, room...",
                key="admin_search_input"
            )

        with fcol2:
            filter_cat = st.selectbox(
                "Category",
                options=categories,
                index=0,
                key="admin_filter_cat"
            )

        with fcol3:
            filter_prio = st.selectbox(
                "Priority",
                options=priorities,
                index=0,
                key="admin_filter_prio"
            )

        with fcol4:
            filter_stat = st.selectbox(
                "Status",
                options=statuses,
                index=0,
                key="admin_filter_stat"
            )

    # 3. Retrieve Filtered DataFrame
    try:
        df = api_client.get_all_complaints(
            category=filter_cat,
            priority=filter_prio,
            status=filter_stat,
            search_query=filter_search
        )
    except Exception as e:
        st.error(f"⚠️ Failed to retrieve complaints from backend: {str(e)}")
        df = pd.DataFrame()

    st.markdown(f"#### 📋 Grievance Tickets ({len(df)} records)")

    if df.empty:
        st.info("No complaints found matching the selected filter criteria.")
        return

    # Display clean table
    display_df = df[[
        "complaint_id",
        "title",
        "category",
        "priority",
        "location",
        "department",
        "status",
        "created_at"
    ]].copy()

    display_df.columns = [
        "Complaint ID",
        "Title",
        "Category",
        "Priority",
        "Location",
        "Department",
        "Status",
        "Created At"
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # 4. Interactive Complaint Detail Inspector & Status Management
    st.markdown("### 🛠️ Complaint Inspector & Status Resolution Workflow")

    complaint_ids = df["complaint_id"].tolist()

    selected_cid = st.selectbox(
        "Select Complaint ID to Inspect / Update",
        options=complaint_ids,
        key="admin_select_cid"
    )

    if selected_cid:
        complaint, history = api_client.get_complaint(selected_cid)

        if complaint:
            col_info, col_action = st.columns([3, 2])

            with col_info:
                st.subheader(complaint["title"])

                col_meta1, col_meta2, col_meta3 = st.columns(3)
                with col_meta1:
                    st.write(f"**Ticket:** {complaint['complaint_id']}")
                with col_meta2:
                    st.write(f"**Status:** {complaint['status']}")
                with col_meta3:
                    st.write(f"**Priority:** {complaint['priority']}")

                st.write(complaint["description"])

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Complainant:** {complaint['name']}")
                    st.write(f"**Email:** {complaint['email']}")
                    st.write(f"**Location:** {complaint['location']}")
                    st.write(f"**Category:** {complaint['category']}")
                with col2:
                    st.write(f"**Subcategory:** {complaint['subcategory']}")
                    st.write(f"**Assigned Dept:** {complaint['department']}")
                    st.write(f"**Created At:** {complaint['created_at']}")
                    st.write(f"**Resolved At:** {complaint['resolved_at'] or 'Pending'}")

                st.caption(
                    f"**Priority Rationale:** {complaint.get('priority_reason') or 'Rule-based evaluation'}"
                )

                if complaint.get("similar_count", 0) > 0:
                    st.warning(
                        f"⚠️ **Similarity Flag:** "
                        f"{complaint['similar_count']} potential matching complaint(s) "
                        f"found in historical database. "
                        f"Top match: `{complaint.get('top_similar_id', 'N/A')}` "
                        f"({round(complaint.get('top_similarity_score', 0) * 100, 1)}% score)."
                    )

                # Timeline & Audit Trail
                st.markdown("##### 🕒 Audit Trail & Status History")
                render_timeline(history)

                # PDF Docket Download
                pdf_bytes = create_complaint_docket_pdf(
                    complaint,
                    history
                )

                st.download_button(
                    label=f"📥 Export Official PDF Docket ({selected_cid})",
                    data=pdf_bytes,
                    file_name=f"{selected_cid}_Docket.pdf",
                    mime="application/pdf",
                    key=f"admin_download_{selected_cid}"
                )

            with col_action:
                st.markdown("#### 📝 Update Ticket Status")

                with st.form(f"update_status_form_{selected_cid}"):

                    curr_status_idx = (
                        ["Pending", "Assigned", "In Progress", "Resolved", "Closed"].index(
                            complaint["status"]
                        )
                        if complaint["status"] in [
                            "Pending",
                            "Assigned",
                            "In Progress",
                            "Resolved",
                            "Closed"
                        ]
                        else 0
                    )

                    new_status = st.selectbox(
                        "Transition Status To",
                        options=[
                            "Pending",
                            "Assigned",
                            "In Progress",
                            "Resolved",
                            "Closed"
                        ],
                        index=curr_status_idx
                    )

                    changed_by = st.text_input(
                        "Handler / Technician Name",
                        value="Admin / Maintenance Team"
                    )

                    status_comment = st.text_area(
                        "Action / Progress Remarks",
                        placeholder="e.g. Technician dispatched / Parts replaced / Issue resolved...",
                        height=90
                    )

                    st.markdown("##### ⚙️ Administrative Overrides")

                    all_prio = [
                        "Low",
                        "Medium",
                        "High",
                        "Critical"
                    ]

                    curr_prio_idx = (
                        all_prio.index(complaint["priority"])
                        if complaint["priority"] in all_prio
                        else 1
                    )

                    override_priority = st.selectbox(
                        "Override Priority Level",
                        options=all_prio,
                        index=curr_prio_idx
                    )

                    all_dept_opts = router.get_all_departments()

                    curr_dept_idx = (
                        all_dept_opts.index(complaint["department"])
                        if complaint["department"] in all_dept_opts
                        else 0
                    )

                    override_dept = st.selectbox(
                        "Re-assign Department",
                        options=all_dept_opts,
                        index=curr_dept_idx
                    )

                    update_btn = st.form_submit_button(
                        "💾 Save Status & Log History",
                        use_container_width=True,
                        type="primary"
                    )

                    if update_btn:
                        result = api_client.update_complaint_status(
                            complaint_id=selected_cid,
                            new_status=new_status,
                            changed_by=changed_by,
                            comment=status_comment,
                            admin_notes=status_comment,
                            priority=override_priority,
                            department=override_dept
                        )

                        if result:
                            st.success(
                                f"✅ Complaint `{selected_cid}` updated to **{new_status}**!"
                            )
                            st.rerun()
                        else:
                            error_detail = (
                                getattr(result, "message", None)
                                or "Please verify your configuration and try again."
                            )
                            st.error(
                                f"❌ Failed to update complaint status: {error_detail}"
                            )