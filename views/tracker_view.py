"""
Complaint Status Tracker View for CivicPulse AI.
Tracks complaints through the FastAPI PostgreSQL backend or local SQLite database.
"""

from html import escape
from typing import Any, Dict, List, Optional
import requests
import streamlit as st

from modules.report_generator import create_complaint_docket_pdf
from utils.api_client import api_client, API_URL
from utils.ui_components import (
    get_priority_badge_html,
    get_status_badge_html,
    render_header,
    render_timeline,
)


def _normalize_history(
    raw_history: Optional[List[Dict[str, Any]]],
    complaint: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Normalizes history entries to ensure consistent keys for both
    render_timeline() and create_complaint_docket_pdf().
    """
    normalized: List[Dict[str, Any]] = []

    if raw_history:
        for entry in raw_history:
            item = dict(entry)
            new_status = item.get("new_status") or item.get("status") or "Unknown"
            old_status = item.get("old_status") or "None"
            changed_by = item.get("changed_by") or "System"
            comment = (
                item.get("comment")
                or item.get("remarks")
                or item.get("note")
                or ""
            )
            changed_at = (
                item.get("changed_at")
                or item.get("timestamp")
                or item.get("created_at")
                or ""
            )

            # Preserve keys for PDF report generation
            item["new_status"] = str(new_status)
            item["old_status"] = str(old_status)
            item["changed_by"] = str(changed_by)
            item["comment"] = str(comment)
            item["changed_at"] = str(changed_at)

            # Ensure keys for timeline display
            item["status"] = str(new_status)
            item["timestamp"] = str(changed_at)
            item["remarks"] = (
                f"Action by {changed_by}: {comment}"
                if comment
                else f"Action by {changed_by}"
            )

            normalized.append(item)

    # Initial fallback record if no audit entries exist
    if not normalized and complaint:
        initial_status = complaint.get("status") or "Pending"
        created_time = str(complaint.get("created_at") or "")
        normalized.append(
            {
                "old_status": "None",
                "new_status": str(initial_status),
                "changed_by": "System",
                "comment": "Complaint submitted and automatically logged.",
                "changed_at": created_time,
                "status": str(initial_status),
                "timestamp": created_time,
                "remarks": "Complaint submitted and automatically logged.",
            }
        )

    return normalized


def _render_complaint_card(
    complaint: Dict[str, Any],
    history: List[Dict[str, Any]],
    key_suffix: str = "",
) -> None:
    """
    Renders complaint details, status, priority, department,
    audit history timeline, and official PDF docket download in clear English.
    """
    cid = str(complaint.get("complaint_id", "N/A"))
    title = str(complaint.get("title", "Untitled Complaint"))
    description = str(complaint.get("description", "No description provided."))
    status = str(complaint.get("status", "Pending"))
    priority = str(complaint.get("priority", "Medium"))
    name = str(complaint.get("name", "Not specified"))
    email = str(complaint.get("email", "Not specified"))
    location = str(complaint.get("location", "Not specified"))
    category = str(complaint.get("category", "General"))
    subcategory = str(complaint.get("subcategory", "General"))
    department = str(complaint.get("department", "General Administration"))
    created_at = str(complaint.get("created_at", "Not recorded"))
    resolved_at = str(complaint.get("resolved_at") or "Pending resolution")
    priority_reason = str(
        complaint.get("priority_reason") or "Rule-based assessment"
    )
    admin_notes = str(complaint.get("admin_notes") or "").strip()

    status_badge = get_status_badge_html(status)
    priority_badge = get_priority_badge_html(priority)

    # 1. Main Complaint Detail Card (uses native Streamlit container to prevent raw HTML code blocks)
    with st.container(border=True):
        col_hdr_left, col_hdr_right = st.columns([3, 2])
        with col_hdr_left:
            st.markdown(
                f'<div style="font-weight:800;font-size:1.15rem;color:#1E293B;">'
                f'Complaint Reference: {escape(cid)}</div>',
                unsafe_allow_html=True,
            )
        with col_hdr_right:
            st.markdown(
                f'<div style="display:flex;justify-content:flex-end;align-items:center;gap:6px;">'
                f'{status_badge}{priority_badge}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(f"**Subject Title:** {title}")

        # Description container
        desc_box_html = (
            f'<div style="background-color:#F8FAFC;border:1px solid #E2E8F0;border-radius:6px;'
            f'padding:12px;margin:8px 0 14px 0;font-size:0.92rem;color:#334155;line-height:1.5;">'
            f'{escape(description)}</div>'
        )
        st.markdown(desc_box_html, unsafe_allow_html=True)

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"**Complainant:** {name}")
            st.markdown(f"**Email Address:** {email}")
            st.markdown(f"**Location Context:** {location}")
            st.markdown(f"**Category:** {category}")
        with col_m2:
            st.markdown(f"**Subcategory:** {subcategory}")
            st.markdown(f"**Assigned Department:** {department}")
            st.markdown(f"**Submission Date:** {created_at}")
            st.markdown(f"**Resolution Date:** {resolved_at}")

        if priority_reason:
            st.caption(f"**Priority Assessment Rationale:** {priority_reason}")

        if admin_notes:
            st.info(f"**Administrative Notes:** {admin_notes}")

    # 2. Semantic Similarity Flag
    similar_count = complaint.get("similar_count", 0) or 0
    if similar_count > 0:
        top_similar_id = complaint.get("top_similar_id", "N/A")
        top_score = complaint.get("top_similarity_score", 0.0) or 0.0
        score_percent = top_score * 100 if top_score <= 1.0 else top_score
        st.warning(
            f"⚠️ **Semantic Similarity Notice:** Identified {similar_count} potentially related "
            f"complaint(s) in the database. Closest historical match: `{top_similar_id}` "
            f"({score_percent:.1f}% semantic similarity)."
        )

    # 3. Chronological Audit History Timeline
    st.markdown("##### 🕒 Audit Trail & Status Timeline")
    normalized_history = _normalize_history(history, complaint)
    render_timeline(normalized_history)

    # 4. Official PDF Docket Download
    st.markdown("##### 📄 Official Complaint Docket")
    try:
        pdf_bytes = create_complaint_docket_pdf(complaint, normalized_history)
        st.download_button(
            label=f"📥 Download Official PDF Docket ({cid})",
            data=pdf_bytes,
            file_name=f"{cid}_Docket.pdf",
            mime="application/pdf",
            key=f"download_{cid}_{key_suffix}",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"❌ Failed to generate the official PDF docket: {str(e)}")


def render_tracker_view() -> None:
    """Render complaint tracking by reference ID or registered email in clear English."""
    render_header(
        title="Track Complaint Status & Timeline",
        subtitle="Look up real-time resolution progress and audit history for your grievances.",
        icon="🔎",
    )

    tab_id, tab_email = st.tabs(
        ["Search by Complaint ID", "Search by Registered Email"]
    )

    # -------------------------------------------------------------
    # TAB 1: Search by Complaint ID (FastAPI PostgreSQL Backend)
    # -------------------------------------------------------------
    with tab_id:
        st.markdown("#### 🎫 Track by Complaint Reference ID")
        st.caption(
            "Query live complaint status, priority, department, and audit history via the FastAPI backend service."
        )

        with st.form("search_by_id_form"):
            col_id_input, col_id_submit = st.columns([4, 1])

            with col_id_input:
                complaint_id_input = st.text_input(
                    "Complaint Reference ID",
                    value=st.session_state.get("tracker_id_query", ""),
                    placeholder="e.g., CP-2026-0001 or CP-3C418E94",
                    key="tracker_id_input_field",
                )

            with col_id_submit:
                st.write("")
                st.write("")
                search_id_btn = st.form_submit_button(
                    "Search Ticket",
                    type="primary",
                    use_container_width=True,
                )

        if search_id_btn:
            query_id = complaint_id_input.strip()
            if not query_id:
                st.warning("⚠️ Please enter a Complaint Reference ID.")
                st.session_state["tracker_id_query"] = ""
                st.session_state["tracker_id_result"] = None
                st.session_state["tracker_id_history"] = []
                st.session_state["tracker_id_error"] = None
            else:
                st.session_state["tracker_id_query"] = query_id
                with st.spinner(f"Retrieving complaint status for reference `{query_id}`..."):
                    try:
                        resp = requests.get(
                            f"{api_client.base_url}/complaints/{query_id}",
                            timeout=api_client.timeout,
                        )

                        if resp.status_code == 200:
                            data = resp.json()
                            complaint = data.get("complaint", data)
                            history = data.get("history", [])

                            # Fallback status history if empty
                            if not history:
                                try:
                                    history = api_client.get_status_history(query_id)
                                except Exception:
                                    history = []

                            st.session_state["tracker_id_result"] = complaint
                            st.session_state["tracker_id_history"] = history
                            st.session_state["tracker_id_error"] = None

                        elif resp.status_code == 404:
                            st.session_state["tracker_id_result"] = None
                            st.session_state["tracker_id_history"] = []
                            st.session_state["tracker_id_error"] = (
                                f"notFound:{query_id}"
                            )

                        else:
                            st.session_state["tracker_id_result"] = None
                            st.session_state["tracker_id_history"] = []
                            st.session_state["tracker_id_error"] = (
                                f"Backend service returned HTTP status {resp.status_code}: {resp.text}"
                            )

                    except requests.exceptions.ConnectionError:
                        st.session_state["tracker_id_result"] = None
                        st.session_state["tracker_id_history"] = []
                        st.session_state["tracker_id_error"] = (
                            "connectionError"
                        )

                    except requests.exceptions.Timeout:
                        st.session_state["tracker_id_result"] = None
                        st.session_state["tracker_id_history"] = []
                        st.session_state["tracker_id_error"] = (
                            "The request to the FastAPI backend service timed out. Please try again."
                        )

                    except requests.exceptions.RequestException as e:
                        st.session_state["tracker_id_result"] = None
                        st.session_state["tracker_id_history"] = []
                        st.session_state["tracker_id_error"] = (
                            f"Backend communication error: {str(e)}"
                        )

                    except Exception as e:
                        st.session_state["tracker_id_result"] = None
                        st.session_state["tracker_id_history"] = []
                        st.session_state["tracker_id_error"] = (
                            f"An unexpected error occurred: {str(e)}"
                        )

        id_err = st.session_state.get("tracker_id_error")
        if id_err == "connectionError":
            st.error(
                f"❌ The FastAPI backend service is unreachable at `{api_client.base_url}`.\n\n"
                "Please verify that the Render backend is live or configure `API_URL` in your Streamlit secrets."
            )
        elif id_err and id_err.startswith("notFound:"):
            missing_cid = id_err.split("notFound:", 1)[1]
            st.warning(
                f"🔍 No complaint record found for reference ID **{missing_cid}**. "
                f"Please verify the identifier and try again."
            )
        elif id_err:
            st.error(f"❌ {id_err}")

        found_complaint = st.session_state.get("tracker_id_result")
        if found_complaint:
            found_history = st.session_state.get("tracker_id_history", [])
            _render_complaint_card(
                found_complaint,
                found_history,
                key_suffix="id_tab",
            )

    # -------------------------------------------------------------
    # TAB 2: Search by Registered Email (FastAPI PostgreSQL Backend)
    # -------------------------------------------------------------
    with tab_email:
        st.markdown("#### 📧 Track by Registered Email")
        st.caption(
            "Retrieve all grievance records registered under your email address via the FastAPI backend service."
        )

        with st.form("search_by_email_form"):
            col_email_input, col_email_submit = st.columns([4, 1])

            with col_email_input:
                email_input = st.text_input(
                    "Registered Email Address",
                    value=st.session_state.get("tracker_email_query", ""),
                    placeholder="e.g., resident@institution.edu",
                    key="tracker_email_input_field",
                )

            with col_email_submit:
                st.write("")
                st.write("")
                search_email_btn = st.form_submit_button(
                    "Find Complaints",
                    type="primary",
                    use_container_width=True,
                )

        if search_email_btn:
            query_email = email_input.strip()
            if not query_email:
                st.warning("⚠️ Please enter a registered email address.")
                st.session_state["tracker_email_query"] = ""
                st.session_state["tracker_email_results"] = None
            else:
                st.session_state["tracker_email_query"] = query_email
                with st.spinner("Searching records for the registered email address..."):
                    try:
                        results = api_client.get_complaints_by_email(query_email)
                        st.session_state["tracker_email_results"] = results
                    except requests.exceptions.ConnectionError:
                        st.session_state["tracker_email_results"] = None
                        st.error(
                            f"❌ The FastAPI backend service is unreachable at `{api_client.base_url}`.\n\n"
                            "Please verify that the Render backend is live or configure `API_URL` in your Streamlit secrets."
                        )
                    except Exception as e:
                        st.session_state["tracker_email_results"] = None
                        st.error(f"❌ Failed to search complaints by email: {str(e)}")

        email_results = st.session_state.get("tracker_email_results")
        searched_email = st.session_state.get("tracker_email_query", "")

        if email_results is not None:
            if not email_results:
                st.info(
                    f"ℹ️ No registered complaints found for **{searched_email}**."
                )
            else:
                st.success(
                    f"✅ Found **{len(email_results)}** complaint(s) for **{searched_email}**."
                )

                if len(email_results) > 1:
                    complaint_options = [
                        c["complaint_id"] for c in email_results
                    ]

                    def format_option(cid: str) -> str:
                        matching = next(
                            (c for c in email_results if c["complaint_id"] == cid),
                            None,
                        )
                        if matching:
                            return f"{cid} - {matching.get('title', 'Untitled')} [{matching.get('status', 'Pending')}]"
                        return cid

                    selected_cid = st.selectbox(
                        "Select a complaint to inspect details and timeline:",
                        options=complaint_options,
                        format_func=format_option,
                        key="tracker_email_selected_cid",
                    )

                    chosen_complaint = next(
                        (c for c in email_results if c["complaint_id"] == selected_cid),
                        email_results[0],
                    )
                else:
                    chosen_complaint = email_results[0]

                # Retrieve history for chosen complaint from backend
                try:
                    chosen_history = api_client.get_status_history(
                        chosen_complaint["complaint_id"]
                    )
                except Exception:
                    chosen_history = []

                _render_complaint_card(
                    chosen_complaint,
                    chosen_history,
                    key_suffix="email_tab",
                )
