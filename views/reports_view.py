"""
Reports View for CivicPulse AI.
Enables generation and instant download of:
1. Executive Management Summary & Hotspot Analytics PDF
2. Individual Grievance Resolution Docket PDFs
3. Raw Data CSV Exports for operational analysis.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from database.database import get_db
from modules.report_generator import create_complaint_docket_pdf, create_summary_analytics_pdf
from utils.ui_components import render_header, render_metric_card


def render_reports_view():
    """Renders the executive reporting and PDF generation center."""
    render_header(
        title="Official Reports & PDF Export Center",
        subtitle="Generate printable PDF executive briefings, audit dockets, and export datasets.",
        icon="📑"
    )

    db = get_db()
    df = db.get_all_complaints()

    if df.empty:
        st.info("ℹ️ No complaint records found. Please seed sample data or submit complaints to generate reports.")
        return

    tab_summary, tab_single, tab_csv = st.tabs([
        "📊 Executive Summary Report (PDF)",
        "📄 Individual Complaint Docket (PDF)",
        "💾 Raw CSV Data Export"
    ])

    # TAB 1: Executive Summary Report
    with tab_summary:
        st.markdown("#### 🏛️ Executive Resolution & Hotspot Summary PDF")
        st.write("Generates an official management summary detailing institutional resolution rates, department workloads, category distributions, and problem hotspots.")

        kpis = db.get_kpis()

        # Compute Category distribution DataFrame for PDF
        cat_df = df["category"].value_counts().reset_index()
        cat_df.columns = ["category", "count"]
        
        # Calculate unresolved per category
        unresolved_map = {}
        for cat in cat_df["category"]:
            unres_cnt = df[(df["category"] == cat) & (df["status"].isin(["Pending", "Assigned", "In Progress"]))].shape[0]
            unresolved_map[cat] = f"{unres_cnt} open"
        cat_df["unresolved"] = cat_df["category"].map(unresolved_map)

        # Compute Priority distribution DataFrame for PDF
        prio_df = df["priority"].value_counts().reset_index()
        prio_df.columns = ["priority", "count"]
        
        prio_rates = {}
        for p in prio_df["priority"]:
            total_p = df[df["priority"] == p].shape[0]
            res_p = df[(df["priority"] == p) & (df["status"].isin(["Resolved", "Closed"]))].shape[0]
            rate = round((res_p / total_p * 100), 1) if total_p > 0 else 0.0
            prio_rates[p] = f"{res_p}/{total_p} ({rate}%)"
        prio_df["rate"] = prio_df["priority"].map(prio_rates)

        # Compute Hotspot info
        top_cat = df["category"].mode()[0] if not df["category"].empty else "N/A"
        top_cat_cnt = df[df["category"] == top_cat].shape[0] if top_cat != "N/A" else 0

        top_loc = df["location"].mode()[0] if not df["location"].empty else "N/A"
        top_loc_cnt = df[df["location"] == top_loc].shape[0] if top_loc != "N/A" else 0

        top_sub = df["subcategory"].mode()[0] if not df["subcategory"].empty else "N/A"
        top_sub_cnt = df[df["subcategory"] == top_sub].shape[0] if top_sub != "N/A" else 0

        pending_dept_df = df[df["status"].isin(["Pending", "Assigned", "In Progress"])]
        top_dept = pending_dept_df["department"].mode()[0] if not pending_dept_df.empty else "None"
        top_dept_cnt = pending_dept_df[pending_dept_df["department"] == top_dept].shape[0] if top_dept != "None" else 0

        hotspots_dict = {
            "top_category": top_cat,
            "top_category_count": top_cat_cnt,
            "top_location": top_loc,
            "top_location_count": top_loc_cnt,
            "top_subcategory": top_sub,
            "top_subcategory_count": top_sub_cnt,
            "top_dept_backlog": f"{top_dept} ({top_dept_cnt} open tickets)"
        }

        with st.spinner("Compiling PDF Executive Report..."):
            summary_pdf_bytes = create_summary_analytics_pdf(
                kpis=kpis,
                category_df=cat_df,
                priority_df=prio_df,
                hotspots=hotspots_dict
            )

        col_btn, _ = st.columns([2, 2])
        with col_btn:
            st.download_button(
                label="📥 Download Executive Summary PDF",
                data=summary_pdf_bytes,
                file_name=f"CivicPulse_Executive_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

    # TAB 2: Single Complaint Docket
    with tab_single:
        st.markdown("#### 📄 Single Complaint Docket PDF")
        st.write("Generate a printable PDF ticket with full complainant details, AI similarity notes, priority evaluation, and complete chronological audit trail.")

        all_ids = df["complaint_id"].tolist()
        chosen_id = st.selectbox("Select Complaint ID for Docket Generation", options=all_ids, key="report_single_cid")

        if chosen_id:
            comp_record = db.get_complaint(chosen_id)
            comp_hist = db.get_status_history(chosen_id)
            
            if comp_record:
                st.write(f"**Selected Ticket:** `{chosen_id}` — *{comp_record['title']}* (Status: **{comp_record['status']}**)")
                
                single_pdf_bytes = create_complaint_docket_pdf(comp_record, comp_hist)
                
                st.download_button(
                    label=f"📥 Download Docket PDF ({chosen_id})",
                    data=single_pdf_bytes,
                    file_name=f"{chosen_id}_Docket.pdf",
                    mime="application/pdf",
                    type="primary"
                )

    # TAB 3: CSV Data Export
    with tab_csv:
        st.markdown("#### 💾 Export Raw Datasets to CSV")
        st.write("Export complaints table and status history audit logs for secondary analysis or spreadsheet review.")

        c1, c2 = st.columns(2)
        with c1:
            csv_complaints = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Complaints CSV (All Records)",
                data=csv_complaints,
                file_name=f"CivicPulse_Complaints_Export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with c2:
            with db.get_connection() as conn:
                hist_df = pd.read_sql_query("SELECT * FROM status_history ORDER BY changed_at DESC", conn)
            csv_history = hist_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Status History Audit CSV",
                data=csv_history,
                file_name=f"CivicPulse_Status_Audit_Export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
