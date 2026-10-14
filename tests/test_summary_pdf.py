"""
Regression and layout tests for Executive Management Summary & Hotspot Analytics PDF.
Verifies:
1. Valid PDF generation with all 7 grievance categories, priorities, KPIs, and hotspots.
2. Exact matching of column names ("category", "count", "unresolved") and ("priority", "count", "rate").
3. Safe handling of empty datasets, missing columns, None types, and zero counts.
4. Robust escaping of XML characters (&, <, >) in category names and hotspot values.
5. Table layout conformance with letter page printable widths (<= 532 pt).
"""

import io
from typing import Dict, Any
import pandas as pd
import pypdf
import pytest
from reportlab.platypus import Paragraph, Table, SimpleDocTemplate

from modules.report_generator import create_summary_analytics_pdf


@pytest.fixture
def sample_kpis() -> Dict[str, Any]:
    return {
        "total": 29,
        "pending": 19,
        "assigned": 1,
        "in_progress": 2,
        "resolved": 7,
        "high_priority": 6,
        "critical_priority": 2,
        "resolution_rate": 24.1,
        "avg_resolution_hours": 10.4
    }


@pytest.fixture
def sample_categories_df() -> pd.DataFrame:
    """All 7 institutional categories with counts and unresolved status."""
    return pd.DataFrame([
        {"category": "Security & Safety", "count": 18, "unresolved": "14 open"},
        {"category": "Electrical", "count": 5, "unresolved": "3 open"},
        {"category": "Infrastructure & Civil", "count": 2, "unresolved": "1 open"},
        {"category": "Water & Plumbing", "count": 1, "unresolved": "1 open"},
        {"category": "Network & IT", "count": 1, "unresolved": "1 open"},
        {"category": "Cleaning & Sanitation", "count": 1, "unresolved": "1 open"},
        {"category": "Equipment & Machinery", "count": 1, "unresolved": "0 open"},
    ])


@pytest.fixture
def sample_priorities_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"priority": "Medium", "count": 20, "rate": "5/20 (25.0%)"},
        {"priority": "High", "count": 6, "rate": "1/6 (16.7%)"},
        {"priority": "Critical", "count": 2, "rate": "1/2 (50.0%)"},
        {"priority": "Low", "count": 1, "rate": "0/1 (0.0%)"},
    ])


@pytest.fixture
def sample_hotspots() -> Dict[str, Any]:
    return {
        "top_category": "Security & Safety",
        "top_category_count": 18,
        "top_location": "Karur Main Campus",
        "top_location_count": 12,
        "top_subcategory": "Campus Lighting & Night Safety",
        "top_subcategory_count": 14,
        "top_dept_backlog": "Campus Security & Safety Division (14 open tickets)"
    }


def test_summary_pdf_generates_valid_pdf_with_all_sections(
    sample_kpis, sample_categories_df, sample_priorities_df, sample_hotspots
):
    """Verifies that create_summary_analytics_pdf returns valid, non-empty PDF binary bytes."""
    pdf_bytes = create_summary_analytics_pdf(
        kpis=sample_kpis,
        category_df=sample_categories_df,
        priority_df=sample_priorities_df,
        hotspots=sample_hotspots
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")
    assert b"%%EOF" in pdf_bytes

    # Inspect rendered PDF text content
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1
    page_text = reader.pages[0].extract_text()

    # Section 1: KPIs
    assert "Platform Operational Overview" in page_text
    assert "29" in page_text
    assert "19" in page_text
    assert "10.4 hrs" in page_text

    # Section 2: Hotspots
    assert "Problem Hotspot Intelligence" in page_text
    assert "Security & Safety (18 incidents)" in page_text
    assert "Karur Main Campus" in page_text
    assert "Campus Lighting & Night Safety" in page_text
    assert "Campus Security & Safety Division" in page_text

    # Section 3: All 7 Categories
    assert "Category Distribution Breakdown" in page_text
    expected_categories = [
        "Security & Safety", "Electrical", "Infrastructure & Civil",
        "Water & Plumbing", "Network & IT", "Cleaning & Sanitation",
        "Equipment & Machinery"
    ]
    for cat in expected_categories:
        assert cat in page_text, f"Category '{cat}' should be rendered in PDF"

    # Section 4: All 4 Priorities
    assert "Urgency & Priority Breakdown" in page_text
    for prio in ["Medium", "High", "Critical", "Low"]:
        assert prio in page_text, f"Priority '{prio}' should be rendered in PDF"


def test_summary_pdf_handles_none_and_empty_inputs_safely():
    """Verifies safe fallback rendering when None or empty structures are passed."""
    # 1. All None
    pdf_bytes_none = create_summary_analytics_pdf(
        kpis=None,
        category_df=None,
        priority_df=None,
        hotspots=None
    )
    assert isinstance(pdf_bytes_none, bytes)
    assert len(pdf_bytes_none) > 1000

    reader_none = pypdf.PdfReader(io.BytesIO(pdf_bytes_none))
    text_none = reader_none.pages[0].extract_text()
    assert "No category data available." in text_none
    assert "No priority data available." in text_none
    assert "N/A (0 incidents)" in text_none

    # 2. Empty DataFrames and dicts
    pdf_bytes_empty = create_summary_analytics_pdf(
        kpis={},
        category_df=pd.DataFrame(),
        priority_df=pd.DataFrame(),
        hotspots={}
    )
    assert isinstance(pdf_bytes_empty, bytes)
    assert len(pdf_bytes_empty) > 1000

    reader_empty = pypdf.PdfReader(io.BytesIO(pdf_bytes_empty))
    text_empty = reader_empty.pages[0].extract_text()
    assert "No category data available." in text_empty
    assert "No priority data available." in text_empty


def test_summary_pdf_special_characters_and_xml_escaping():
    """Verifies that XML special characters (&, <, >, quotes) in categories or hotspots do not crash ReportLab."""
    special_cats = pd.DataFrame([
        {"category": "Water & Plumbing <Phase 1>", "count": 3, "unresolved": "2 & 1 open"},
        {"category": "Research & Development [Lab > 2]", "count": 1, "unresolved": "1 open"}
    ])
    special_prios = pd.DataFrame([
        {"priority": "Critical & Urgent <Risk>", "count": 2, "rate": "1/2 (50.0%)"}
    ])
    special_hotspots = {
        "top_category": "Water & Plumbing <Urgent>",
        "top_category_count": 3,
        "top_location": "Main Hall & Block A",
        "top_location_count": 3,
        "top_subcategory": "Pipes & Fixtures <Standard>",
        "top_subcategory_count": 2,
        "top_dept_backlog": "Maintenance & Civil Dept <Zone 1> (2 open tickets)"
    }

    pdf_bytes = create_summary_analytics_pdf(
        kpis={"total": 4, "pending": 2, "critical_priority": 2},
        category_df=special_cats,
        priority_df=special_prios,
        hotspots=special_hotspots
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1500


def test_summary_pdf_table_story_inspection(
    sample_kpis, sample_categories_df, sample_priorities_df, sample_hotspots, monkeypatch
):
    """
    Directly inspects story elements passed to SimpleDocTemplate.build:
    - Verifies printable page width limit (532 pt).
    - Verifies all 4 tables exist and column widths sum to <= 532 pt.
    - Verifies all cells contain Paragraph flowables.
    """
    captured_story = []
    original_build = SimpleDocTemplate.build

    def spy_build(self, story, **kwargs):
        captured_story.extend(story)
        return original_build(self, story, **kwargs)

    monkeypatch.setattr(SimpleDocTemplate, "build", spy_build)

    create_summary_analytics_pdf(
        kpis=sample_kpis,
        category_df=sample_categories_df,
        priority_df=sample_priorities_df,
        hotspots=sample_hotspots
    )

    tables = [elem for elem in captured_story if isinstance(elem, Table)]
    assert len(tables) == 4, f"Expected 4 tables in summary report, found {len(tables)}"

    printable_page_width = 612.0 - 40.0 - 40.0  # 532.0 pt
    for idx, table in enumerate(tables):
        col_widths = list(table._colWidths)
        total_width = sum(col_widths)
        assert total_width <= printable_page_width, (
            f"Table {idx} total width {total_width} exceeds printable limit {printable_page_width}"
        )
        for row_idx, row in enumerate(table._cellvalues):
            for col_idx, cell in enumerate(row):
                flowable = cell[0] if isinstance(cell, (list, tuple)) else cell
                assert isinstance(flowable, Paragraph), f"Table {idx} cell ({row_idx}, {col_idx}) must be Paragraph"


def test_reports_view_data_preparation_flow():
    """
    Simulates the exact data preparation logic implemented in views/reports_view.py
    and verifies that real complaint records produce the expected DataFrame formats.
    """
    # Sample realistic records
    complaints = [
        {"category": "Electrical", "priority": "Critical", "status": "Pending", "location": "EEE Lab", "subcategory": "Wiring", "department": "Electrical Dept"},
        {"category": "Electrical", "priority": "High", "status": "In Progress", "location": "EEE Lab", "subcategory": "Fan", "department": "Electrical Dept"},
        {"category": "Electrical", "priority": "High", "status": "Resolved", "location": "EEE Lab", "subcategory": "Fan", "department": "Electrical Dept"},
        {"category": "Water & Plumbing", "priority": "Medium", "status": "Resolved", "location": "Block B", "subcategory": "Tap", "department": "Plumbing Dept"},
        {"category": "Security & Safety", "priority": "Low", "status": "Pending", "location": "Gate 1", "subcategory": "CCTV", "department": "Security Dept"},
    ]
    df = pd.DataFrame(complaints)

    # 1. Category DataFrame
    cat_counts = df["category"].dropna().astype(str).str.strip().value_counts()
    cat_df = cat_counts.reset_index()
    cat_df.columns = ["category", "count"]
    unresolved_map = {}
    for cat in cat_df["category"]:
        unres_cnt = df[(df["category"] == cat) & (df["status"].isin(["Pending", "Assigned", "In Progress"]))].shape[0]
        unresolved_map[cat] = f"{unres_cnt} open"
    cat_df["unresolved"] = cat_df["category"].map(unresolved_map)

    assert "category" in cat_df.columns
    assert "count" in cat_df.columns
    assert "unresolved" in cat_df.columns
    assert cat_df[cat_df["category"] == "Electrical"]["count"].iloc[0] == 3
    assert cat_df[cat_df["category"] == "Electrical"]["unresolved"].iloc[0] == "2 open"

    # 2. Priority DataFrame
    prio_counts = df["priority"].dropna().astype(str).str.strip().value_counts()
    prio_df = prio_counts.reset_index()
    prio_df.columns = ["priority", "count"]
    prio_rates = {}
    for p in prio_df["priority"]:
        tot_p = df[df["priority"] == p].shape[0]
        res_p = df[(df["priority"] == p) & (df["status"].isin(["Resolved", "Closed"]))].shape[0]
        rate = round((res_p / tot_p * 100.0), 1) if tot_p > 0 else 0.0
        prio_rates[p] = f"{res_p}/{tot_p} ({rate}%)"
    prio_df["rate"] = prio_df["priority"].map(prio_rates)

    assert "priority" in prio_df.columns
    assert "count" in prio_df.columns
    assert "rate" in prio_df.columns
    assert prio_df[prio_df["priority"] == "Critical"]["count"].iloc[0] == 1
    assert prio_df[prio_df["priority"] == "Critical"]["rate"].iloc[0] == "0/1 (0.0%)"
    assert prio_df[prio_df["priority"] == "Medium"]["rate"].iloc[0] == "1/1 (100.0%)"

    # 3. Hotspots
    def _get_safe_mode(series: pd.Series, default: str = "N/A") -> str:
        if series is None or series.empty:
            return default
        cleaned = series.dropna().astype(str).str.strip()
        cleaned = cleaned[cleaned != ""]
        if cleaned.empty:
            return default
        mode_s = cleaned.mode()
        return str(mode_s.iloc[0]) if not mode_s.empty else default

    top_cat = _get_safe_mode(df["category"])
    top_cat_cnt = df[df["category"] == top_cat].shape[0]
    top_loc = _get_safe_mode(df["location"])
    top_loc_cnt = df[df["location"] == top_loc].shape[0]
    top_sub = _get_safe_mode(df["subcategory"])
    top_sub_cnt = df[df["subcategory"] == top_sub].shape[0]

    pending_dept_df = df[df["status"].isin(["Pending", "Assigned", "In Progress"])]
    top_dept = _get_safe_mode(pending_dept_df["department"], default="None")
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

    assert hotspots_dict["top_category"] == "Electrical"
    assert hotspots_dict["top_category_count"] == 3
    assert hotspots_dict["top_location"] == "EEE Lab"
    assert hotspots_dict["top_location_count"] == 3
    assert hotspots_dict["top_dept_backlog"] == "Electrical Dept (2 open tickets)"

    # Generate PDF
    kpis = {
        "total": 5, "pending": 2, "in_progress": 1, "resolved": 2,
        "high_priority": 2, "critical_priority": 1, "avg_resolution_hours": 4.5
    }
    pdf_bytes = create_summary_analytics_pdf(kpis, cat_df, prio_df, hotspots_dict)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000


def test_summary_pdf_kpi_status_reconciliation(sample_categories_df, sample_priorities_df, sample_hotspots):
    """
    Verifies that all complaint statuses (Pending, Assigned, In Progress, Resolved)
    reconcile exactly to total complaints, and that Assigned is rendered in the PDF.
    """
    kpis = {
        "total": 29,
        "pending": 19,
        "assigned": 1,
        "in_progress": 2,
        "resolved": 7,
        "high_priority": 6,
        "critical_priority": 2,
        "resolution_rate": 24.1,
        "avg_resolution_hours": 12.5
    }
    # Mathematical reconciliation
    status_sum = kpis["pending"] + kpis["assigned"] + kpis["in_progress"] + kpis["resolved"]
    assert status_sum == kpis["total"], f"Status sum {status_sum} must equal total {kpis['total']}"

    pdf_bytes = create_summary_analytics_pdf(
        kpis=kpis,
        category_df=sample_categories_df,
        priority_df=sample_priorities_df,
        hotspots=sample_hotspots
    )
    assert isinstance(pdf_bytes, bytes)
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    extracted_text = reader.pages[0].extract_text()
    assert "Assigned" in extracted_text
    assert "Pending" in extracted_text
    assert "In Progress" in extracted_text
    assert "Resolved" in extracted_text
    assert "29" in extracted_text
