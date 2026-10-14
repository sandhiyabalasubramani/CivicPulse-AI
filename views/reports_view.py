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
from utils.api_client import api_client
from modules.report_generator import create_complaint_docket_pdf, create_summary_analytics_pdf
from utils.ui_components import render_header, render_metric_card


def render_reports_view():
    """Renders the executive reporting and PDF generation center."""
    render_header(
        title="Official Reports & PDF Export Center",
        subtitle="Generate printable PDF executive briefings, audit dockets, and export datasets.",
        icon="📑"
    )

    if not api_client.check_health():
        st.error(
            f"⚠️ Unable to connect to CivicPulse AI backend service ({api_client.base_url}). "
            "Please ensure the FastAPI service is running."
        )
        return

    try:
        df = api_client.get_all_complaints()
    except Exception as e:
        st.error(f"⚠️ Failed to retrieve complaints from backend: {str(e)}")
        return

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

        try:
            kpis = api_client.get_kpis()
        except Exception as e:
            st.error(f"⚠️ Error fetching complaint metrics from backend: {str(e)}")
            kpis = {}

        # Fallback or augment KPIs safely from df if missing or empty
        status_col = df["status"] if "status" in df.columns else pd.Series(dtype=object)
        prio_col = df["priority"] if "priority" in df.columns else pd.Series(dtype=object)

        if not kpis or not kpis.get("total"):
            total_cnt = len(df)
            pending_cnt = int((status_col == "Pending").sum())
            assigned_cnt = int((status_col == "Assigned").sum())
            in_prog_cnt = int((status_col == "In Progress").sum())
            resolved_cnt = int(status_col.isin(["Resolved", "Closed"]).sum())
            high_cnt = int((prio_col == "High").sum())
            crit_cnt = int((prio_col == "Critical").sum())
            rate_cnt = round((resolved_cnt / total_cnt * 100.0), 1) if total_cnt > 0 else 0.0
            kpis = {
                "total": total_cnt,
                "pending": pending_cnt,
                "assigned": assigned_cnt,
                "in_progress": in_prog_cnt,
                "resolved": resolved_cnt,
                "high_priority": high_cnt,
                "critical_priority": crit_cnt,
                "resolution_rate": rate_cnt,
                "avg_resolution_hours": kpis.get("avg_resolution_hours", 0.0) if kpis else 0.0
            }
        elif "assigned" not in kpis:
            kpis["assigned"] = int((status_col == "Assigned").sum())

        # Compute Category distribution DataFrame for PDF
        if "category" in df.columns and not df["category"].dropna().empty:
            cat_counts = df["category"].dropna().astype(str).str.strip().value_counts()
            cat_df = cat_counts.reset_index()
            cat_df.columns = ["category", "count"]

            # Calculate unresolved per category
            unresolved_map = {}
            for cat in cat_df["category"]:
                if "status" in df.columns:
                    unres_cnt = df[(df["category"] == cat) & (df["status"].isin(["Pending", "Assigned", "In Progress"]))].shape[0]
                else:
                    unres_cnt = 0
                unresolved_map[cat] = f"{unres_cnt} open"
            cat_df["unresolved"] = cat_df["category"].map(unresolved_map)
        else:
            cat_df = pd.DataFrame(columns=["category", "count", "unresolved"])

        # Compute Priority distribution DataFrame for PDF
        if "priority" in df.columns and not df["priority"].dropna().empty:
            prio_counts = df["priority"].dropna().astype(str).str.strip().value_counts()
            prio_df = prio_counts.reset_index()
            prio_df.columns = ["priority", "count"]

            prio_rates = {}
            for p in prio_df["priority"]:
                total_p = df[df["priority"] == p].shape[0]
                if "status" in df.columns:
                    res_p = df[(df["priority"] == p) & (df["status"].isin(["Resolved", "Closed"]))].shape[0]
                else:
                    res_p = 0
                rate = round((res_p / total_p * 100.0), 1) if total_p > 0 else 0.0
                prio_rates[p] = f"{res_p}/{total_p} ({rate}%)"
            prio_df["rate"] = prio_df["priority"].map(prio_rates)
        else:
            prio_df = pd.DataFrame(columns=["priority", "count", "rate"])

        # Safe helper to compute statistical mode without IndexError on empty/null series
        def _get_safe_mode(series: pd.Series, default: str = "N/A") -> str:
            if series is None or series.empty:
                return default
            cleaned = series.dropna().astype(str).str.strip()
            cleaned = cleaned[cleaned != ""]
            if cleaned.empty:
                return default
            mode_s = cleaned.mode()
            return str(mode_s.iloc[0]) if not mode_s.empty else default

        # Compute Hotspot info
        top_cat = _get_safe_mode(df["category"]) if "category" in df.columns else "N/A"
        top_cat_cnt = df[df["category"] == top_cat].shape[0] if (top_cat != "N/A" and "category" in df.columns) else 0

        top_loc = _get_safe_mode(df["location"]) if "location" in df.columns else "N/A"
        top_loc_cnt = df[df["location"] == top_loc].shape[0] if (top_loc != "N/A" and "location" in df.columns) else 0

        top_sub = _get_safe_mode(df["subcategory"]) if "subcategory" in df.columns else "N/A"
        top_sub_cnt = df[df["subcategory"] == top_sub].shape[0] if (top_sub != "N/A" and "subcategory" in df.columns) else 0

        if "status" in df.columns and "department" in df.columns:
            pending_dept_df = df[df["status"].isin(["Pending", "Assigned", "In Progress"])]
            top_dept = _get_safe_mode(pending_dept_df["department"], default="None")
            top_dept_cnt = pending_dept_df[pending_dept_df["department"] == top_dept].shape[0] if (top_dept != "None" and not pending_dept_df.empty) else 0
        else:
            top_dept = "None"
            top_dept_cnt = 0

        top_dept_backlog_text = f"{top_dept} ({top_dept_cnt} open tickets)" if top_dept != "None" else "None recorded"

        hotspots_dict = {
            "top_category": top_cat,
            "top_category_count": top_cat_cnt,
            "top_location": top_loc,
            "top_location_count": top_loc_cnt,
            "top_subcategory": top_sub,
            "top_subcategory_count": top_sub_cnt,
            "top_dept_backlog": top_dept_backlog_text
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
            comp_record, comp_hist = api_client.get_complaint(chosen_id)

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
            try:
                hist_df = api_client.get_all_status_history()
            except Exception:
                hist_df = pd.DataFrame()
            csv_history = hist_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Status History Audit CSV",
                data=csv_history,
                file_name=f"CivicPulse_Status_Audit_Export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
