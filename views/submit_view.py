from datetime import datetime
from html import escape
import requests
import streamlit as st

from utils.validators import validate_complaint_form
from utils.api_client import api_client, API_URL
from utils.ui_components import (
    render_hero_banner,
    render_header,
    get_status_badge_html,
    get_priority_badge_html,
    render_ai_triage_card
)


def render_submit_view():
    render_hero_banner()
    render_header(
        title="Submit Institutional Grievance",
        subtitle="Log a complaint and let CivicPulse AI analyze, categorize, prioritize, and route it automatically.",
        icon="📝",
        badge="AI-Powered Grievance Intake"
    )

    with st.form("complaint_form"):
        # Section 1: Complainant Details Card
        st.markdown(
            """
            <div style="
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-left: 4px solid #2563EB;
                border-radius: 12px;
                padding: 14px 18px;
                margin-bottom: 16px;
            ">
                <div style="font-family:'Poppins', sans-serif; font-size:1.05rem; font-weight:700; color:#0F172A;">
                    👤 Complainant Identification
                </div>
                <div style="font-size:0.82rem; color:#64748B;">
                    Provide your institutional contact information to receive status updates.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Full Name *",
                placeholder="e.g. Dr. Jane Smith or Student Name"
            )

        with col2:
            email = st.text_input(
                "Email Address *",
                placeholder="e.g. resident@campus.edu"
            )

        location = st.text_input(
            "Location / Facility Room *",
            placeholder="e.g. Block C, 3rd Floor Computer Lab or Central Library"
        )

        # Section 2: Complaint Details Card
        st.markdown(
            """
            <div style="
                background: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-left: 4px solid #6366F1;
                border-radius: 12px;
                padding: 14px 18px;
                margin-top: 16px;
                margin-bottom: 16px;
            ">
                <div style="font-family:'Poppins', sans-serif; font-size:1.05rem; font-weight:700; color:#0F172A;">
                    📋 Grievance Details & Classification
                </div>
                <div style="font-size:0.82rem; color:#64748B;">
                    Describe the issue clearly. CivicPulse AI will parse keywords, score priority, and route to division.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        title = st.text_input(
            "Complaint Title *",
            placeholder="e.g. Hazardous electrical sparking in laboratory switchboard"
        )

        description = st.text_area(
            "Detailed Description *",
            placeholder="Provide relevant facts, equipment numbers, symptoms, or safety hazards observed...",
            height=140
        )

        col_cat, col_dept = st.columns(2)

        category_options = [
            "Auto-Detect",
            "Security & Safety",
            "Electrical",
            "Infrastructure & Civil",
            "Equipment & Machinery",
            "Network & IT",
            "Cleaning & Sanitation",
            "Water & Plumbing"
        ]

        with col_cat:
            category = st.selectbox(
                "Category (or leave Auto-Detect)",
                category_options,
                index=0
            )

        department_options = [
            "Auto-Assign",
            "Campus Security & Safety Division",
            "Electrical Maintenance Division",
            "Infrastructure & Civil Division",
            "Equipment & Machinery Division",
            "Network & IT Division",
            "Cleaning & Sanitation Division",
            "Water & Plumbing Division"
        ]

        with col_dept:
            department = st.selectbox(
                "Department Routing (or leave Auto-Assign)",
                department_options,
                index=0
            )

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "🚀 Submit Grievance & Run AI Triage",
            use_container_width=True,
            type="primary"
        )

    if not submitted:
        return

    complaint_data = {
        "name": name.strip(),
        "email": email.strip(),
        "location": location.strip(),
        "title": title.strip(),
        "description": description.strip(),
        "category": category if category != "Auto-Detect" else ""
    }

    is_valid, validation_message = validate_complaint_form(complaint_data)

    if not is_valid:
        st.error(f"⚠️ Validation Error: {validation_message}")
        return

    payload = {
        "name": name.strip(),
        "email": email.strip(),
        "location": location.strip(),
        "title": title.strip(),
        "description": description.strip(),
        "category": category,
        "department": department
    }

    with st.spinner("🤖 CivicPulse AI is parsing keywords, analyzing urgency, and routing to division..."):
        api_url = api_client.base_url
        try:
            api_response = requests.post(
                f"{api_url}/complaints",
                json=payload,
                timeout=api_client.timeout
            )

            if api_response.status_code not in [200, 201]:
                st.error(
                    f"❌ Backend rejected the complaint (HTTP {api_response.status_code})"
                )
                try:
                    st.json(api_response.json())
                except Exception:
                    st.code(api_response.text)
                return

            api_data = api_response.json()

        except requests.exceptions.ConnectionError:
            st.error(
                f"⚠️ Unable to connect to CivicPulse AI backend at `{api_url}`.\n\n"
                "Please verify that the Render backend is live or configure `API_URL` in your Streamlit secrets."
            )
            return

        except requests.exceptions.Timeout:
            st.error(
                f"⏱️ The request to CivicPulse AI backend (`{api_url}`) timed out after {api_client.timeout}s. "
                "If running on Render free tier, the backend may take up to a minute to wake up from sleep. "
                "Please try again in a few moments."
            )
            return

        except requests.exceptions.RequestException as e:
            st.error(f"Backend communication error: {e}")
            return

        except Exception as e:
            st.error(f"Unexpected error: {e}")
            return

    if api_data.get("status") != "success":
        st.error(api_data.get("message", "Complaint submission failed."))
        return

    # Extract all results
    complaint_id = api_data.get("complaint_id", "CP-PENDING")
    analysis = api_data.get("analysis", {})
    priority_result = api_data.get("priority", {})
    routing_result = api_data.get("routing", {})
    similarity_result = api_data.get("similarity", {})

    detected_category = analysis.get("category", category)
    subcategory = analysis.get("subcategory", "")
    priority = priority_result.get("priority", "Medium")
    priority_score = priority_result.get("score", 50)
    priority_reason = priority_result.get("primary_reason", "")
    assigned_department = routing_result.get("department", department)
    routing_type = routing_result.get("routing_type", "")
    sla_hours = routing_result.get("sla_hours", "")

    similar_count = similarity_result.get("similar_count", 0)
    top_similar_id = similarity_result.get("top_complaint_id", "")
    top_similarity_score = similarity_result.get("top_score", 0)

    new_record = {
        "reference_id": complaint_id,
        "name": name.strip(),
        "email": email.strip(),
        "location": location.strip(),
        "title": title.strip(),
        "description": description.strip(),
        "category": detected_category,
        "subcategory": subcategory,
        "priority": priority,
        "department": assigned_department,
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }
    st.session_state["last_complaint"] = new_record

    # 1. Success Banner Card
    status_badge_html = get_status_badge_html("Pending")
    priority_badge_html = get_priority_badge_html(priority)

    success_card_html = (
        f'<div style="background:linear-gradient(135deg, rgba(16,185,129,0.06) 0%, rgba(37,99,235,0.06) 100%);'
        f'border:1.5px solid #A7F3D0;border-radius:16px;padding:22px;margin:20px 0;box-shadow:0 4px 18px rgba(16,185,129,0.08);">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">'
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="width:44px;height:44px;border-radius:50%;background:#10B981;color:#FFFFFF;display:flex;align-items:center;justify-content:center;font-size:1.4rem;font-weight:700;">✓</div>'
        f'<div>'
        f'<div style="font-family:\'Poppins\', sans-serif;font-size:1.25rem;font-weight:700;color:#065F46;">Grievance Successfully Registered</div>'
        f'<div style="font-size:0.86rem;color:#047857;">A tracking ticket has been generated and dispatched to the triage queue.</div>'
        f'</div>'
        f'</div>'
        f'<div style="display:flex;gap:6px;align-items:center;">{status_badge_html}{priority_badge_html}</div>'
        f'</div>'
        f'<div style="margin-top:16px;background:#FFFFFF;border:1px solid #E2E8F0;border-radius:12px;padding:14px 18px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;">'
        f'<div>'
        f'<span style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;">Tracking Reference ID</span>'
        f'<div style="font-family:\'JetBrains Mono\', monospace;font-size:1.4rem;font-weight:700;color:#1E3A8A;letter-spacing:0.04em;">{escape(str(complaint_id))}</div>'
        f'</div>'
        f'<div style="font-size:0.82rem;color:#64748B;">Save this reference identifier to check real-time resolution progress on the Tracker tab.</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(success_card_html, unsafe_allow_html=True)

    # 2. AI Analysis & Triage Visualization
    render_ai_triage_card(
        category=detected_category,
        subcategory=subcategory,
        priority=priority,
        priority_score=priority_score,
        department=assigned_department,
        sla_hours=sla_hours,
        routing_type=routing_type,
        priority_reason=priority_reason
    )

    # 3. Duplicate Similarity Warning (if applicable)
    if similar_count > 0:
        score_percent = float(top_similarity_score) * 100 if float(top_similarity_score) <= 1.0 else float(top_similarity_score)
        similarity_card_html = (
            f'<div class="cp-similarity-box">'
            f'<div style="display:flex;align-items:center;gap:8px;font-family:\'Poppins\', sans-serif;font-weight:700;color:#92400E;font-size:1rem;">'
            f'<span>⚠️</span> <span>Duplicate & Similarity Alert: {similar_count} Related Complaint(s) Found</span>'
            f'</div>'
            f'<div style="font-size:0.88rem;color:#78350F;margin-top:4px;">'
            f'Our semantic similarity model matched this submission with existing ticket <b>{escape(str(top_similar_id))}</b> '
            f'at <b>{score_percent:.1f}%</b> similarity. Technicians have been flagged to avoid redundant work.'
            f'</div>'
            f'</div>'
        )
        st.markdown(similarity_card_html, unsafe_allow_html=True)

    # 4. Official Complaint Docket Card
    created_time_str = datetime.now().strftime("%d-%m-%Y %H:%M")
    docket_html = (
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:16px;padding:22px;margin-top:20px;box-shadow:0 4px 18px rgba(15,23,42,0.04);">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #E2E8F0;padding-bottom:12px;margin-bottom:14px;">'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:1.2rem;">🏛️</span>'
        f'<span style="font-family:\'Poppins\', sans-serif;font-weight:700;font-size:1.1rem;color:#0F172A;">CivicPulse Official Complaint Docket</span>'
        f'</div>'
        f'<span style="font-family:\'JetBrains Mono\', monospace;font-size:0.85rem;color:#64748B;">{created_time_str}</span>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(220px, 1fr));gap:12px;font-size:0.88rem;">'
        f'<div><b style="color:#64748B;">Complainant:</b> <span style="color:#0F172A;font-weight:600;">{escape(name)}</span></div>'
        f'<div><b style="color:#64748B;">Email:</b> <span style="color:#0F172A;font-weight:600;">{escape(email)}</span></div>'
        f'<div><b style="color:#64748B;">Location:</b> <span style="color:#0F172A;font-weight:600;">{escape(location)}</span></div>'
        f'<div><b style="color:#64748B;">Title:</b> <span style="color:#0F172A;font-weight:600;">{escape(title)}</span></div>'
        f'<div><b style="color:#64748B;">Category:</b> <span style="color:#0F172A;font-weight:600;">{escape(str(detected_category))}</span></div>'
        f'<div><b style="color:#64748B;">Department:</b> <span style="color:#0F172A;font-weight:600;">{escape(str(assigned_department))}</span></div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(docket_html, unsafe_allow_html=True)