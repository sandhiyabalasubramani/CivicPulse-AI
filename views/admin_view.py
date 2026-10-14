"""
Admin Complaint Management View for CivicPulse AI.
Provides multi-criteria search & filtering, live KPI counters,
complaint inspection, status update workflows, and audit trail logging.
"""

from html import escape
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
    render_timeline,
    render_status_stepper
)


def render_admin_view():
    """Renders the administrative complaint management dashboard."""
    render_header(
        title="Administrative Grievance Operations",
        subtitle="Inspect, route, prioritize, and log status transitions for all institutional grievances.",
        icon="🛡️",
        badge="Enterprise Control Center"
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
            "All-time grievances",
            "#172554",
            "📊"
        )

    with col2:
        render_metric_card(
            "Pending",
            kpis.get("pending", 0),
            "Awaiting triage",
            "#F59E0B",
            "⏳"
        )

    with col3:
        render_metric_card(
            "Assigned",
            kpis.get("assigned", 0),
            "Routed to division",
            "#8B5CF6",
            "🏢"
        )

    with col4:
        render_metric_card(
            "In Progress",
            kpis.get("in_progress", 0),
            "Under active triage",
            "#2563EB",
            "⚙️"
        )

    with col5:
        render_metric_card(
            "Resolved",
            kpis.get("resolved", 0),
            f"{kpis.get('resolution_rate', 0)}% resolution rate",
            "#0D9488",
            "✅"
        )

    with col6:
        render_metric_card(
            "Critical / High",
            kpis.get("critical_priority", 0) + kpis.get("high_priority", 0),
            "Urgent attention needed",
            "#EF4444",
            "🚨"
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 2. Filters Bar
    with st.expander("🔍 Search & Filter Complaints", expanded=True):
        fcol1, fcol2, fcol3, fcol4 = st.columns(4)

        try:
            categories = ["All"] + api_client.get_distinct_values("category")
        except Exception:
            categories = ["All"]

        priorities = ["All", "Critical", "High", "Medium", "Low"]
        statuses = ["All", "Pending", "Assigned", "In Progress", "Resolved", "Closed"]

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

    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;margin:16px 0 10px 0;">'
        f'<div style="font-family:\'Poppins\', sans-serif;font-weight:700;font-size:1.15rem;color:#0F172A;">'
        f'📋 Grievance Tickets <span style="background:#EEF2FF;color:#4F46E5;border:1px solid #C7D2FE;font-size:0.8rem;padding:2px 8px;border-radius:12px;margin-left:6px;">{len(df)} records</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if df.empty:
        st.info("ℹ️ No complaints found matching the selected filter criteria.")
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

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    st.divider()

    # 4. Interactive Complaint Detail Inspector & Status Management
    st.markdown(
        """
        <div style="font-family:'Poppins', sans-serif;font-size:1.3rem;font-weight:700;color:#0F172A;margin-bottom:6px;">
            🛠️ Complaint Inspector & Status Resolution Workflow
        </div>
        <div style="font-size:0.88rem;color:#64748B;margin-bottom:14px;">
            Select any complaint from the active queue to inspect full telemetry, update resolution milestones, or re-route departments.
        </div>
        """,
        unsafe_allow_html=True
    )

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
                status_badge = get_status_badge_html(complaint["status"])
                priority_badge = get_priority_badge_html(complaint["priority"])

                with st.container(border=True):
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;border-bottom:1px solid #E2E8F0;padding-bottom:10px;margin-bottom:12px;">'
                        f'<div>'
                        f'<span style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;">Ticket Identifier:</span> '
                        f'<span style="font-family:\'JetBrains Mono\', monospace;font-weight:700;font-size:1.2rem;color:#1E3A8A;background:#EFF6FF;border:1px solid #BFDBFE;padding:2px 8px;border-radius:6px;">{escape(str(complaint["complaint_id"]))}</span>'
                        f'</div>'
                        f'<div style="display:flex;gap:6px;">{status_badge}{priority_badge}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown(f"### {complaint['title']}")

                    # Description
                    desc_html = (
                        f'<div style="background-color:#F8FAFC;border:1px solid #E2E8F0;border-left:4px solid #3B82F6;'
                        f'border-radius:0 10px 10px 0;padding:12px 14px;margin:8px 0 14px 0;font-size:0.92rem;color:#334155;line-height:1.6;">'
                        f'{escape(str(complaint["description"]))}</div>'
                    )
                    st.markdown(desc_html, unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**👤 Complainant:** {complaint['name']}")
                        st.markdown(f"**📧 Email:** {complaint['email']}")
                        st.markdown(f"**📍 Location:** {complaint['location']}")
                        st.markdown(f"**🏷️ Category:** {complaint['category']}")
                    with col2:
                        st.markdown(f"**📑 Subcategory:** {complaint['subcategory']}")
                        st.markdown(f"**🏢 Assigned Dept:** {complaint['department']}")
                        st.markdown(f"**📅 Created At:** {complaint['created_at']}")
                        st.markdown(f"**🏁 Resolved At:** {complaint['resolved_at'] or 'Pending'}")

                    st.caption(
                        f"🤖 **Priority Assessment Rationale:** {complaint.get('priority_reason') or 'Rule-based evaluation'}"
                    )

                    if complaint.get("similar_count", 0) > 0:
                        top_score_val = complaint.get("top_similarity_score", 0) or 0
                        top_score_pct = top_score_val * 100 if top_score_val <= 1.0 else top_score_val
                        st.warning(
                            f"⚠️ **Semantic Similarity Alert:** "
                            f"{complaint['similar_count']} potential matching complaint(s) found. "
                            f"Top match: `{complaint.get('top_similar_id', 'N/A')}` "
                            f"({top_score_pct:.1f}% score)."
                        )

                # Timeline & Audit Trail
                st.markdown("##### 🕒 Audit Trail & Status History")
                render_timeline(history)

                # PDF Docket Download
                try:
                    pdf_bytes = create_complaint_docket_pdf(complaint, history)
                    st.download_button(
                        label=f"📥 Export Official PDF Docket ({selected_cid})",
                        data=pdf_bytes,
                        file_name=f"{selected_cid}_Docket.pdf",
                        mime="application/pdf",
                        key=f"admin_download_{selected_cid}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Failed to generate PDF: {str(e)}")

            with col_action:
                with st.container(border=True):
                    st.markdown(
                        """
                        <div style="font-family:'Poppins', sans-serif;font-size:1.1rem;font-weight:700;color:#0F172A;border-bottom:1px solid #E2E8F0;padding-bottom:8px;margin-bottom:12px;">
                            📝 Update Ticket Status
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

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

                        st.markdown(
                            """
                            <div style="font-size:0.88rem;font-weight:700;color:#475569;margin-top:10px;margin-bottom:6px;">
                                ⚙️ Administrative Overrides
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

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