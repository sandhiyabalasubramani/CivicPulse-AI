"""
Complaint Status Tracker View for CivicPulse AI.
Allows users to look up complaint status by Complaint ID or submitter email,
view live timeline updates, and download their official PDF resolution docket.
"""

import streamlit as st
from database.database import get_db
from modules.report_generator import create_complaint_docket_pdf
from utils.ui_components import (
    render_header,
    get_status_badge_html,
    get_priority_badge_html,
    render_timeline
)


def render_tracker_view():
    """Renders the complaint tracking and timeline inspection view."""
    render_header(
        title="Track Complaint Status & Timeline",
        subtitle="Lookup your complaint by Reference ID or Email to see real-time updates and resolution audit trails.",
        icon="🔍"
    )

    db = get_db()

    tab_id, tab_email = st.tabs(["🔎 Search by Complaint ID", "📧 Search by Registered Email"])

    # TAB 1: Search by Complaint ID
    with tab_id:
        c1, c2 = st.columns([3, 1])
        with c1:
            search_cid = st.text_input("Enter Complaint ID", placeholder="e.g. CP-2026-0001", key="track_cid_input").strip()
        with c2:
            st.write("")
            st.write("")
            btn_search_id = st.button("Search ID", use_container_width=True, type="primary")

        if search_cid or btn_search_id:
            if not search_cid:
                st.warning("Please enter a valid Complaint ID.")
            else:
                complaint = db.get_complaint(search_cid)
                if not complaint:
                    st.error(f"❌ No complaint found matching Reference ID **'{search_cid}'**. Please check your ID and try again.")
                else:
                    _render_complaint_detail_card(complaint, db)

    # TAB 2: Search by Email
    with tab_email:
        c1, c2 = st.columns([3, 1])
        with c1:
            search_email = st.text_input("Enter Submitter Email", placeholder="e.g. user@institution.edu", key="track_email_input").strip()
        with c2:
            st.write("")
            st.write("")
            btn_search_email = st.button("Search Email", use_container_width=True, type="primary")

        if search_email or btn_search_email:
            if not search_email:
                st.warning("Please enter your registered email address.")
            else:
                complaints = db.get_complaints_by_email(search_email)
                if not complaints:
                    st.info(f"ℹ️ No registered complaints found under email **'{search_email}'**.")
                else:
                    st.success(f"📋 Found **{len(complaints)}** complaint(s) filed by `{search_email}`.")
                    for comp in complaints:
                        with st.expander(f"📌 {comp['complaint_id']} — {comp['title']} ({comp['status']})", expanded=False):
                            _render_complaint_detail_card(comp, db)


def _render_complaint_detail_card(complaint: dict, db):
    """Renders complete complaint status card and action bar."""
    cid = complaint["complaint_id"]
    status = complaint["status"]
    priority = complaint["priority"]
    history = db.get_status_history(cid)

    st.markdown(f"""
        <div class="cp-ai-card">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; margin-bottom: 12px;">
                <span style="font-weight: 800; font-size: 1.15rem; color: #1E293B;">Complaint Docket &bull; {cid}</span>
                <div>
                    {get_status_badge_html(status)}
                    &nbsp;
                    {get_priority_badge_html(priority)}
                </div>
            </div>
            <div style="font-size: 1.05rem; font-weight: 700; color: #0F172A; margin-bottom: 8px;">
                {complaint['title']}
            </div>
            <div style="font-size: 0.9rem; color: #334155; margin-bottom: 12px; line-height: 1.5; background: #FFFFFF; padding: 10px; border-radius: 6px; border: 1px solid #E2E8F0;">
                {complaint['description']}
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; font-size: 0.88rem; color: #475569;">
                <div><b>📍 Location:</b> {complaint['location']}</div>
                <div><b>🏷️ Category:</b> {complaint['category']}</div>
                <div><b>📂 Subcategory:</b> {complaint['subcategory']}</div>
                <div><b>🏢 Department:</b> {complaint['department']}</div>
                <div><b>👤 Complainant:</b> {complaint['name']}</div>
                <div><b>📅 Submitted:</b> {complaint['created_at']}</div>
                <div><b>⏱️ Resolved:</b> {complaint['resolved_at'] or 'In Progress / Pending'}</div>
                <div><b>⚡ Priority Reason:</b> {complaint.get('priority_reason') or 'Rule-based analysis'}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if complaint.get("admin_notes"):
        st.info(f"💬 **Official Department Remarks:** {complaint['admin_notes']}")

    # Timeline Section
    st.markdown("##### 🕒 Audit Trail & Timeline")
    render_timeline(history)

    # PDF Download Action
    pdf_bytes = create_complaint_docket_pdf(complaint, history)
    st.download_button(
        label=f"📥 Download Official Docket PDF ({cid})",
        data=pdf_bytes,
        file_name=f"{cid}_Resolution_Docket.pdf",
        mime="application/pdf",
        key=f"download_pdf_{cid}"
    )
