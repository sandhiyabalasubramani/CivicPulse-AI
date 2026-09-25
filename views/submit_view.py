"""
Complaint Submission View for CivicPulse AI.
Allows users to submit complaints with real-time NLP analysis,
TF-IDF duplicate detection, and immediate docket confirmation.
"""

import streamlit as st
from datetime import datetime
from database.database import get_db
from modules.complaint_analyzer import get_analyzer, CATEGORY_TAXONOMY
from modules.priority_engine import get_priority_engine
from modules.similarity_engine import get_similarity_engine
from modules.department_router import get_department_router
from utils.validators import validate_complaint_form
from utils.ui_components import (
    render_header,
    get_priority_badge_html,
    get_status_badge_html
)


def render_submit_view():
    """Renders the complaint submission form and post-submission results."""
    render_header(
        title="Submit a Grievance or Maintenance Request",
        subtitle="Our AI-assisted platform analyzes your issue, determines urgency, routes to the right team, and detects duplicates.",
        icon="📝"
    )

    db = get_db()
    analyzer = get_analyzer()
    priority_engine = get_priority_engine()
    similarity_engine = get_similarity_engine()
    router = get_department_router()

    # Form Container
    with st.form("complaint_submission_form", clear_on_submit=False):
        st.markdown("#### 👤 Complainant Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *", placeholder="e.g. Dr. Ramesh Sharma or Priya V", help="Your official name for ticket tracking.")
        with col2:
            email = st.text_input("Email Address *", placeholder="e.g. user@institution.edu", help="We will use this email for status tracking.")

        st.markdown("#### 📍 Incident Location & Details")
        location = st.text_input(
            "Specific Location *",
            placeholder="e.g. EEE Lab 2, Electrical Block 2nd Floor / Room 304",
            help="Building, Block, Lab, Floor, or Room number where the issue is located."
        )

        title = st.text_input(
            "Complaint Title *",
            placeholder="e.g. Three ceiling fans not working in EEE Lab 2",
            help="Brief summary of the issue."
        )

        description = st.text_area(
            "Detailed Description *",
            placeholder="Please describe what happened, what equipment is affected, the impact on students/staff, and any safety hazards...",
            height=130,
            help="Detailed description helps our NLP engine accurately classify category and evaluate priority."
        )

        st.markdown("#### ⚙️ Optional Overrides (Leave on Auto-Detect for AI Assistance)")
        col_cat, col_dept = st.columns(2)
        
        category_options = ["Auto-Detect"] + list(CATEGORY_TAXONOMY.keys())
        all_depts = ["Auto-Assign"] + router.get_all_departments()

        with col_cat:
            selected_category = st.selectbox(
                "Category (Optional)",
                options=category_options,
                index=0,
                help="Let our NLP system auto-detect the category, or select manually if you prefer."
            )

        with col_dept:
            selected_department = st.selectbox(
                "Department (Optional)",
                options=all_depts,
                index=0,
                help="Let our system route automatically, or specify a destination department."
            )

        submitted = st.form_submit_button("🚀 Submit & Analyze Complaint", use_container_width=True, type="primary")

    if submitted:
        form_payload = {
            "name": name,
            "email": email,
            "location": location,
            "title": title,
            "description": description
        }

        # 1. Validate Form Inputs
        is_valid, err_msg = validate_complaint_form(form_payload)
        if not is_valid:
            st.error(f"⚠️ **Validation Error:** {err_msg}")
            return

        with st.spinner("Analyzing complaint text, computing TF-IDF similarity vectors, and routing..."):
            # 2. NLP Analysis (Category & Subcategory)
            nlp_result = analyzer.analyze(
                title=title,
                description=description,
                user_category=selected_category
            )

            # 3. Priority Evaluation
            priority_result = priority_engine.evaluate(
                title=title,
                description=description,
                category=nlp_result["category"]
            )

            # 4. Department Routing & SLA
            routing_result = router.route(
                category=nlp_result["category"],
                subcategory=nlp_result["subcategory"],
                user_department=selected_department
            )

            # 5. TF-IDF & Cosine Similarity Check against existing complaints in SQLite
            existing_records = db.get_complaints_for_similarity()
            similarity_result = similarity_engine.find_similar(
                new_title=title,
                new_description=description,
                existing_complaints=existing_records,
                new_location=location,
                top_k=3
            )

            # 6. Save Complaint to SQLite
            new_record = {
                "name": name.strip(),
                "email": email.strip().lower(),
                "location": location.strip(),
                "title": title.strip(),
                "description": description.strip(),
                "category": nlp_result["category"],
                "subcategory": nlp_result["subcategory"],
                "priority": priority_result["priority"],
                "priority_reason": priority_result["primary_reason"],
                "department": routing_result["department"],
                "status": "Pending",
                "similar_count": similarity_result["similar_count"],
                "top_similar_id": similarity_result["top_complaint_id"],
                "top_similarity_score": similarity_result["top_score"],
            }

            complaint_id = db.insert_complaint(new_record)

        # 7. Render Confirmation Card
        st.success(f"🎉 **Complaint Successfully Registered! Reference ID: `{complaint_id}`**")

        st.markdown(f"""
            <div class="cp-ai-card">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #E2E8F0; padding-bottom: 8px; margin-bottom: 12px;">
                    <span style="font-weight: 800; font-size: 1.1rem; color: #1E293B;">Complaint Docket &bull; {complaint_id}</span>
                    <div>
                        {get_status_badge_html("Pending")}
                        &nbsp;
                        {get_priority_badge_html(priority_result["priority"])}
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; font-size: 0.9rem;">
                    <div><b>Category:</b> {nlp_result["category"]}</div>
                    <div><b>Subcategory:</b> {nlp_result["subcategory"]}</div>
                    <div><b>Assigned Department:</b> {routing_result["department"]}</div>
                    <div><b>Target SLA:</b> {routing_result["sla_hours"]} hours</div>
                    <div><b>Location:</b> {location}</div>
                    <div><b>Submitter:</b> {name} ({email})</div>
                </div>
                <div style="margin-top: 10px; font-size: 0.85rem; color: #475569;">
                    <b>Priority Signal:</b> {priority_result["primary_reason"]}
                </div>
                <div style="margin-top: 8px; font-size: 0.82rem; color: #64748B;">
                    <b>Extracted Keywords:</b> {', '.join([f'<code>{k}</code>' for k in nlp_result['keywords']]) if nlp_result['keywords'] else 'None'}
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 8. Render Similarity Warnings if detected
        if similarity_result["has_similar"]:
            st.markdown(f"""
                <div class="cp-similarity-box">
                    <div style="font-weight: 700; color: #92400E; font-size: 0.95rem; margin-bottom: 4px;">
                        ⚠️ Potential Similar / Duplicate Complaints Found ({similarity_result['similar_count']})
                    </div>
                    <div style="font-size: 0.85rem; color: #78350F; margin-bottom: 8px;">
                        Our TF-IDF & Cosine Similarity engine detected potential semantic overlap with existing tickets in the system.
                    </div>
                </div>
            """, unsafe_allow_html=True)

            for sim in similarity_result["matches"]:
                with st.expander(f"🔍 Similar Complaint: {sim['complaint_id']} — '{sim['title']}' ({sim['similarity_percentage']}% Match)", expanded=False):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**Description:** {sim['description']}")
                        st.caption(f"📍 Location: {sim['location']} | 🏷️ Category: {sim['category']} | 📅 Created: {sim['created_at']}")
                    with c2:
                        st.markdown(f"Status: {get_status_badge_html(sim['status'])}", unsafe_allow_html=True)
                        st.markdown(f"Priority: {get_priority_badge_html(sim['priority'])}", unsafe_allow_html=True)
                        st.metric("Similarity", f"{sim['similarity_percentage']}%")
        else:
            st.info("💡 **Similarity Analysis:** No historical duplicate or closely matching complaints found for this issue.")

        st.caption("ℹ️ You can track the live status and audit trail of this complaint anytime using the **Track Complaint** page.")
