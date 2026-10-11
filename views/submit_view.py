import requests
import streamlit as st
from datetime import datetime

from utils.validators import validate_complaint_form
from utils.api_client import API_URL


def render_submit_view():

    st.markdown(
        """
        <div class="civic-title">
            Submit Complaint
        </div>
        <div class="civic-subtitle">
            Submit a grievance and let CivicPulse AI analyze, prioritize,
            categorize and route it automatically.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    with st.form("complaint_form"):

        st.subheader("Complainant Details")

        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Name *",
                placeholder="Enter your name"
            )

        with col2:
            email = st.text_input(
                "Email *",
                placeholder="example@gmail.com"
            )

        location = st.text_input(
            "Location *",
            placeholder="Example: Karur Campus"
        )

        st.subheader("Complaint Details")

        title = st.text_input(
            "Complaint Title *",
            placeholder="Example: Street light not working"
        )

        description = st.text_area(
            "Complaint Description *",
            placeholder="Describe the issue clearly...",
            height=150
        )

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

        category = st.selectbox(
            "Category",
            category_options
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

        department = st.selectbox(
            "Department",
            department_options
        )

        submitted = st.form_submit_button(
            "Submit Complaint",
            use_container_width=True
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

    is_valid, validation_message = validate_complaint_form(
        complaint_data
    )

    if not is_valid:
        st.error(validation_message)
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

    with st.spinner("CivicPulse AI is analyzing your complaint..."):

        try:

            api_response = requests.post(
                f"{API_URL}/complaints",
                json=payload,
                timeout=15
            )

            if api_response.status_code not in [200, 201]:

                st.error(
                    f"Backend rejected the complaint "
                    f"(HTTP {api_response.status_code})"
                )

                try:
                    st.json(api_response.json())
                except Exception:
                    st.code(api_response.text)

                return

            api_data = api_response.json()

        except requests.exceptions.ConnectionError:

            st.error(
                "FastAPI backend is not running.\n\n"
                "Start it with:\n"
                "uvicorn backend.main:app --reload"
            )

            return

        except requests.exceptions.Timeout:

            st.error(
                "FastAPI backend request timed out."
            )

            return

        except requests.exceptions.RequestException as e:

            st.error(
                f"Backend connection error: {e}"
            )

            return

        except Exception as e:

            st.error(
                f"Unexpected error: {e}"
            )

            return

    if api_data.get("status") != "success":

        st.error(
            api_data.get(
                "message",
                "Complaint submission failed."
            )
        )

        return

    # ---------------------------------------------------------
    # Read all AI results directly from FastAPI
    # ---------------------------------------------------------

    complaint_id = api_data.get("complaint_id", "CP-PENDING")

    analysis = api_data.get("analysis", {})
    priority_result = api_data.get("priority", {})
    routing_result = api_data.get("routing", {})
    similarity_result = api_data.get("similarity", {})

    detected_category = analysis.get(
        "category",
        category
    )

    subcategory = analysis.get(
        "subcategory",
        ""
    )

    priority = priority_result.get(
        "priority",
        "Medium"
    )

    priority_score = priority_result.get(
        "score",
        50
    )

    priority_reason = priority_result.get(
        "primary_reason",
        ""
    )

    assigned_department = routing_result.get(
        "department",
        department
    )

    routing_type = routing_result.get(
        "routing_type",
        ""
    )

    sla_hours = routing_result.get(
        "sla_hours",
        ""
    )

    similar_count = similarity_result.get(
        "similar_count",
        0
    )

    top_similar_id = similarity_result.get(
        "top_complaint_id",
        ""
    )

    top_similarity_score = similarity_result.get(
        "top_score",
        0
    )

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

    # ---------------------------------------------------------
    # Success
    # ---------------------------------------------------------

    st.success(
        "Complaint submitted successfully!"
    )

    st.markdown(
        f"""
        <div class="cp-ai-card">

            <h3>Complaint Registered</h3>

            <p>
                <b>Complaint ID:</b>
                {complaint_id}
            </p>

            <p>
                <b>Category:</b>
                {detected_category}
            </p>

            <p>
                <b>Subcategory:</b>
                {subcategory}
            </p>

            <p>
                <b>Priority:</b>
                {priority}
            </p>

            <p>
                <b>Department:</b>
                {assigned_department}
            </p>

            <p>
                <b>Status:</b>
                Pending
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------------------------------------------------
    # AI Analysis
    # ---------------------------------------------------------

    st.subheader("AI Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Category",
            detected_category
        )

    with col2:
        st.metric(
            "Priority",
            priority
        )

    with col3:
        st.metric(
            "Status",
            "Pending"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Priority Score",
            priority_score
        )

    with col2:
        st.metric(
            "SLA",
            f"{sla_hours} hours"
            if sla_hours
            else "N/A"
        )

    with col3:
        st.metric(
            "Similar Complaints",
            similar_count
        )

    # ---------------------------------------------------------
    # Priority Reason
    # ---------------------------------------------------------

    if priority_reason:

        st.info(
            f"Priority Reason: {priority_reason}"
        )

    # ---------------------------------------------------------
    # Routing Information
    # ---------------------------------------------------------

    st.subheader("Department Routing")

    st.write(
        f"**Assigned Department:** {assigned_department}"
    )

    if routing_type:
        st.write(
            f"**Routing Type:** {routing_type}"
        )

    if sla_hours:
        st.write(
            f"**Service Level Agreement:** {sla_hours} hours"
        )

    if routing_result.get("contact_email"):
        st.write(
            f"**Department Contact:** "
            f"{routing_result['contact_email']}"
        )

    # ---------------------------------------------------------
    # Similarity / Duplicate Detection
    # ---------------------------------------------------------

    if similar_count > 0:

        st.markdown(
            """
            <div class="cp-similarity-box">
                <h4>Similar Complaints Detected</h4>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.warning(
            f"{similar_count} similar complaint(s) detected."
        )

        if top_similar_id:
            st.write(
                f"**Closest Complaint:** {top_similar_id}"
            )

        if isinstance(top_similarity_score, (int, float)):
            st.write(
                f"**Similarity Score:** "
                f"{float(top_similarity_score):.1%}"
            )

    # ---------------------------------------------------------
    # Complaint Docket
    # ---------------------------------------------------------

    st.markdown("---")

    st.subheader("Complaint Docket")

    st.markdown(
        f"""
        <div class="cp-ai-card">

            <h3>CivicPulse AI Docket</h3>

            <p>
                <b>Complaint ID:</b>
                {complaint_id}
            </p>

            <p>
                <b>Name:</b>
                {name}
            </p>

            <p>
                <b>Location:</b>
                {location}
            </p>

            <p>
                <b>Title:</b>
                {title}
            </p>

            <p>
                <b>Category:</b>
                {detected_category}
            </p>

            <p>
                <b>Subcategory:</b>
                {subcategory}
            </p>

            <p>
                <b>Priority:</b>
                {priority}
            </p>

            <p>
                <b>Department:</b>
                {assigned_department}
            </p>

            <p>
                <b>Status:</b>
                Pending
            </p>

            <p>
                <b>Created:</b>
                {datetime.now().strftime("%d-%m-%Y %H:%M")}
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )