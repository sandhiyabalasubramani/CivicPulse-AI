"""
Admin Complaint Management View for CivicPulse AI.
Provides multi-criteria search & filtering, live KPI counters,
complaint inspection, status update workflows, and audit trail logging.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database.database import get_db
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

    db = get_db()
    router = get_department_router()

    # 1. Top KPI Summary Row
    kpis = db.get_kpis()
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        render_metric_card("Total Logged", kpis["total"], "All time grievances", "#1E293B")
    with col2:
        render_metric_card("Pending", kpis["pending"], "Awaiting triage", "#D97706")
    with col3:
        render_metric_card("In Progress", kpis["in_progress"], "Under active resolution", "#2563EB")
    with col4:
        render_metric_card("Resolved", kpis["resolved"], f"{kpis['resolution_rate']}% resolution rate", "#16A34A")
    with col5:
        render_metric_card("Critical / High", kpis["critical_priority"] + kpis["high_priority"], "High urgency tickets", "#DC2626")

    st.write("")

    # 2. Filters Bar
    with st.expander("🔍 Search & Filter Complaints", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)
        
        categories = ["All"] + db.get_distinct_values("category")
        priorities = ["All", "Critical", "High", "Medium", "Low"]
        statuses = ["All", "Pending", "Assigned", "In Progress", "Resolved", "Closed"]
        locations = ["All"] + db.get_distinct_values("location")

        with fcol1:
            filter_search = st.text_input("Text Search", placeholder="ID, keyword, name, room...", key="admin_search_input")
        with fcol2:
            filter_cat = st.selectbox("Category", options=categories, index=0, key="admin_filter_cat")
        with fcol3:
            filter_prio = st.selectbox("Priority", options=priorities, index=0, key="admin_filter_prio")
        with fcol4:
            filter_stat = st.selectbox("Status", options=statuses, index=0, key="admin_filter_stat")

    # 3. Retrieve Filtered DataFrame
    df = db.get_all_complaints(
        category=filter_cat,
        priority=filter_prio,
        status=filter_stat,
        search_query=filter_search
    )

    st.markdown(f"#### 📋 Grievance Tickets ({len(df)} records)")

    if df.empty:
        st.info("No complaints found matching the selected filter criteria.")
        return

    # Display clean table
    display_df = df[[
        "complaint_id", "title", "category", "priority", "location", "department", "status", "created_at"
    ]].copy()
    display_df.columns = ["Complaint ID", "Title", "Category", "Priority", "Location", "Department", "Status", "Created At"]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # 4. Interactive Complaint Detail Inspector & Status Management
    st.markdown("### 🛠️ Complaint Inspector & Status Resolution Workflow")
    
    complaint_ids = df["complaint_id"].tolist()
    selected_cid = st.selectbox("Select Complaint ID to Inspect / Update", options=complaint_ids, key="admin_select_cid")

    if selected_cid:
        complaint = db.get_complaint(selected_cid)
        if complaint:
            col_info, col_action = st.columns([3, 2])

            with col_info:
                st.markdown(f"""
                    <div class="cp-ai-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; margin-bottom: 10px;">
                            <span style="font-weight: 800; font-size: 1.1rem; color: #1E293B;">Ticket: {complaint['complaint_id']}</span>
                            <div>
                                {get_status_badge_html(complaint['status'])}
                                &nbsp;
                                {get_priority_badge_html(complaint['priority'])}
                            </div>
                        </div>
                        <div style="font-weight: 700; font-size: 1rem; color: #0F172A; margin-bottom: 6px;">
                            {complaint['title']}
                        </div>
                        <div style="font-size: 0.88rem; color: #334155; margin-bottom: 10px; background: #FFFFFF; padding: 8px; border-radius: 6px; border: 1px solid #E2E8F0;">
                            {complaint['description']}
                        </div>
                        <div style="font-size: 0.84rem; color: #475569; display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                            <div><b>Complainant:</b> {complaint['name']}</div>
                            <div><b>Email:</b> {complaint['email']}</div>
                            <div><b>Location:</b> {complaint['location']}</div>
                            <div><b>Category:</b> {complaint['category']}</div>
                            <div><b>Subcategory:</b> {complaint['subcategory']}</div>
                            <div><b>Assigned Dept:</b> {complaint['department']}</div>
                            <div><b>Created At:</b> {complaint['created_at']}</div>
                            <div><b>Resolved At:</b> {complaint['resolved_at'] or 'Pending'}</div>
                        </div>
                        <div style="margin-top: 8px; font-size: 0.82rem; color: #B45309;">
                            <b>Priority Rationale:</b> {complaint.get('priority_reason') or 'Rule-based evaluation'}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if complaint.get("similar_count", 0) > 0:
                    st.warning(f"⚠️ **Similarity Flag:** {complaint['similar_count']} potential matching complaint(s) found in historical database. Top match: `{complaint.get('top_similar_id', 'N/A')}` ({round(complaint.get('top_similarity_score', 0)*100, 1)}% score).")

                # Timeline & Audit Trail
                history = db.get_status_history(selected_cid)
                st.markdown("##### 🕒 Audit Trail & Status History")
                render_timeline(history)

                # PDF Docket Download
                pdf_bytes = create_complaint_docket_pdf(complaint, history)
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
                    curr_status_idx = ["Pending", "Assigned", "In Progress", "Resolved", "Closed"].index(complaint["status"]) if complaint["status"] in ["Pending", "Assigned", "In Progress", "Resolved", "Closed"] else 0
                    
                    new_status = st.selectbox(
                        "Transition Status To",
                        options=["Pending", "Assigned", "In Progress", "Resolved", "Closed"],
                        index=curr_status_idx
                    )

                    changed_by = st.text_input("Handler / Technician Name", value="Admin / Maintenance Team")

                    status_comment = st.text_area(
                        "Action / Progress Remarks",
                        placeholder="e.g. Technician dispatched / Parts replaced / Issue resolved...",
                        height=90
                    )

                    st.markdown("##### ⚙️ Administrative Overrides")
                    all_prio = ["Low", "Medium", "High", "Critical"]
                    curr_prio_idx = all_prio.index(complaint["priority"]) if complaint["priority"] in all_prio else 1
                    override_priority = st.selectbox("Override Priority Level", options=all_prio, index=curr_prio_idx)

                    all_dept_opts = router.get_all_departments()
                    curr_dept_idx = all_dept_opts.index(complaint["department"]) if complaint["department"] in all_dept_opts else 0
                    override_dept = st.selectbox("Re-assign Department", options=all_dept_opts, index=curr_dept_idx)

                    update_btn = st.form_submit_button("💾 Save Status & Log History", use_container_width=True, type="primary")

                    if update_btn:
                        success = db.update_complaint_status(
                            complaint_id=selected_cid,
                            new_status=new_status,
                            changed_by=changed_by,
                            comment=status_comment,
                            admin_notes=status_comment,
                            priority=override_priority,
                            department=override_dept
                        )
                        if success:
                            st.success(f"✅ Complaint `{selected_cid}` updated to **{new_status}**!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update complaint status. Please try again.")
