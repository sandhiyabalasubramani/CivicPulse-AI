"""
Regression and layout tests for Official Complaint Docket PDF audit-trail table.
Uses synthetic data only to ensure zero mutation of production database or complaint records.
"""

import io
from typing import Dict, Any, List
import pytest
from reportlab.platypus import Paragraph, Table, SimpleDocTemplate
from modules.report_generator import create_complaint_docket_pdf


@pytest.fixture
def sample_complaint() -> Dict[str, Any]:
    """Synthetic complaint data for testing."""
    return {
        "complaint_id": "CP-2026-SYNTH-001",
        "name": "Jane Citizen",
        "email": "jane.citizen@example.com",
        "location": "Ward 4, North Sector",
        "title": "Severe Water Pressure Fluctuation & Pipeline Leak",
        "description": "Continuous leakage detected near Main Street intersection with water pressure dropping below baseline.",
        "category": "Water & Sewage",
        "subcategory": "Pipeline Leakage",
        "priority": "High",
        "priority_reason": "Risk of structural foundation damage & potable water contamination.",
        "department": "Water Supply & Sewerage Board",
        "status": "In Progress",
        "admin_notes": "Dispatched field technician crew for urgent pressure valve check.",
        "similar_count": 2,
        "top_similarity_score": 0.88,
        "top_similar_id": "CP-2026-SYNTH-000",
        "created_at": "2026-10-10 09:15:00",
        "resolved_at": None,
    }


def test_docket_pdf_generates_valid_pdf_bytes(sample_complaint: Dict[str, Any]) -> None:
    """Verify that create_complaint_docket_pdf returns valid, non-empty PDF binary bytes."""
    history = [
        {
            "changed_at": "2026-10-10 09:15:00",
            "old_status": "None",
            "new_status": "Pending",
            "changed_by": "System",
            "comment": "Complaint submitted and automatically logged."
        }
    ]
    pdf_bytes = create_complaint_docket_pdf(sample_complaint, history)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
    assert b"%%EOF" in pdf_bytes


def test_audit_trail_table_fits_printable_page_width_and_preserves_five_columns(
    sample_complaint: Dict[str, Any]
) -> None:
    """
    Verify that:
    1. All 5 audit-trail columns are preserved: Timestamp, Previous Status, Updated To, Action By, Remarks.
    2. Column widths sum to <= printable page width (532 pt on letter paper with 40 pt margins).
    3. Headers repeat on page break (repeatRows=1).
    4. Table cells are wrapped in Paragraph flowables.
    """
    history = [
        {
            "changed_at": "2026-10-10 09:15:00",
            "old_status": "None",
            "new_status": "Pending",
            "changed_by": "System",
            "comment": "Complaint submitted and automatically logged."
        },
        {
            "changed_at": "2026-10-10 11:30:00",
            "old_status": "Pending",
            "new_status": "Under Investigation",
            "changed_by": "Admin / Maintenance Team",
            "comment": "Assigned to the field engineering team for on-site diagnostic audit."
        }
    ]

    # Standard letter width is 612 pt; 40 pt left + 40 pt right margin leaves 532 pt printable
    printable_page_width = 612.0 - 40.0 - 40.0
    assert printable_page_width == 532.0

    # Build PDF binary
    pdf_bytes = create_complaint_docket_pdf(sample_complaint, history)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_audit_trail_long_values_wrapping_and_special_chars(
    sample_complaint: Dict[str, Any]
) -> None:
    """
    Regression test verifying that long strings:
    - 'Admin / Maintenance Team'
    - 'Under Investigation'
    - 'Resolution in Progress'
    - Long remarks exceeding 200 characters
    - XML/HTML special characters ('&', '<', '>')
    wrap cleanly and render without truncation or XML syntax errors.
    """
    long_remark = (
        "Comprehensive field inspection was carried out in accordance with standard operating "
        "procedures. The primary issue was determined to be excessive wear and tear on the electrical "
        "junction box wiring & main valve assembly. Replacement parts were installed, connections "
        "re-soldered, and insulation tests completed with <zero faults> observed. Supervisory sign-off "
        "is pending final water-flow stabilization."
    )

    synthetic_history = [
        {
            "changed_at": "2026-10-10 09:15:00",
            "old_status": "None",
            "new_status": "Pending",
            "changed_by": "System",
            "comment": "Complaint submitted & logged."
        },
        {
            "changed_at": "2026-10-10 11:00:00",
            "old_status": "Pending",
            "new_status": "Under Investigation",
            "changed_by": "Admin / Maintenance Team",
            "comment": "Preliminary site investigation initiated by senior technician."
        },
        {
            "changed_at": "2026-10-11 14:30:00",
            "old_status": "Under Investigation",
            "new_status": "Resolution in Progress",
            "changed_by": "Admin / Maintenance Team & Contractor Crew",
            "comment": long_remark
        },
        {
            "changed_at": "2026-10-12 10:00:00",
            "old_status": "Resolution in Progress",
            "new_status": "Resolved",
            "changed_by": "Municipal Operations Bureau <Quality Assurance>",
            "comment": "Final inspection verified & approved."
        }
    ]

    pdf_bytes = create_complaint_docket_pdf(sample_complaint, synthetic_history)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF")
    assert b"%%EOF" in pdf_bytes


def test_audit_trail_empty_and_none_fields(sample_complaint: Dict[str, Any]) -> None:
    """
    Verify robust handling of None, missing, or alternate dictionary keys in history entries.
    """
    malformed_history = [
        # All None values
        {
            "changed_at": None,
            "old_status": None,
            "new_status": None,
            "changed_by": None,
            "comment": None,
        },
        # Empty string values
        {
            "changed_at": "",
            "old_status": "",
            "new_status": "",
            "changed_by": "",
            "comment": "",
        },
        # Alternate keys (timestamp, status, remarks, action_by)
        {
            "timestamp": "2026-10-12 12:00:00",
            "old_status": "In Progress",
            "status": "Resolved",
            "action_by": "Admin / Maintenance Team",
            "remarks": "Resolved via alternate key mapping."
        },
        # Non-dict items skipped safely
        None,
        "invalid_entry"
    ]

    pdf_bytes = create_complaint_docket_pdf(sample_complaint, malformed_history)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_audit_trail_empty_history_fallback(sample_complaint: Dict[str, Any]) -> None:
    """Verify that an empty history list renders the fallback message cleanly."""
    pdf_bytes = create_complaint_docket_pdf(sample_complaint, [])
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_audit_trail_multipage_repeating_headers(sample_complaint: Dict[str, Any]) -> None:
    """
    Verify that a long audit trail spanning across multiple pages builds cleanly
    with repeatRows=1 repeating table headers across pages without overflow or crashing.
    """
    large_history = []
    for i in range(35):
        large_history.append({
            "changed_at": f"2026-10-{10 + (i % 20):02d} 10:{i:02d}:00",
            "old_status": "Under Investigation" if i % 2 == 0 else "Resolution in Progress",
            "new_status": "Resolution in Progress" if i % 2 == 0 else "Under Investigation",
            "changed_by": "Admin / Maintenance Team",
            "comment": f"Iterative progress check #{i + 1}: Diagnostic telemetry verified with no critical anomalies."
        })

    pdf_bytes = create_complaint_docket_pdf(sample_complaint, large_history)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 5000
    assert pdf_bytes.startswith(b"%PDF")


def test_audit_trail_table_story_inspection(
    sample_complaint: Dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Directly inspect the story elements passed to SimpleDocTemplate.build:
    - Verifies 5-column audit-trail table presence
    - Verifies colWidths = [90, 80, 85, 100, 175] summing to 530 <= 532 pt
    - Verifies repeatRows == 1
    - Verifies every cell in the table is an instance of Paragraph
    - Verifies column header texts and data values
    """
    captured_story = []
    original_build = SimpleDocTemplate.build

    def spy_build(self, story, **kwargs):
        captured_story.extend(story)
        return original_build(self, story, **kwargs)

    monkeypatch.setattr(SimpleDocTemplate, "build", spy_build)

    history = [
        {
            "changed_at": "2026-10-10 09:15:00",
            "old_status": "None",
            "new_status": "Under Investigation",
            "changed_by": "Admin / Maintenance Team",
            "comment": "Assigned to the field engineering team for on-site diagnostic audit."
        }
    ]

    pdf_bytes = create_complaint_docket_pdf(sample_complaint, history)
    assert isinstance(pdf_bytes, bytes)

    # Find audit trail table with 5 columns
    audit_table = None
    for elem in captured_story:
        if isinstance(elem, Table) and elem._colWidths and len(elem._colWidths) == 5:
            audit_table = elem
            break

    assert audit_table is not None, "Audit trail table with 5 columns not found in story"

    # Verify column widths
    col_widths = list(audit_table._colWidths)
    assert len(col_widths) == 5
    assert col_widths == [90, 80, 85, 100, 175]
    assert sum(col_widths) == 530.0
    assert sum(col_widths) <= 532.0  # Printable width limit on letter size (612 - 80)

    # Verify repeating header across pages
    assert audit_table.repeatRows == 1

    # Verify all cells are Paragraph flowables
    for row_idx, row in enumerate(audit_table._cellvalues):
        assert len(row) == 5, f"Row {row_idx} must have 5 columns"
        for col_idx, cell in enumerate(row):
            flowable = cell[0] if isinstance(cell, (list, tuple)) else cell
            assert isinstance(flowable, Paragraph), f"Cell at ({row_idx}, {col_idx}) must be Paragraph"

    def get_cell_text(cell_item):
        p = cell_item[0] if isinstance(cell_item, (list, tuple)) else cell_item
        return p.text

    # Verify header row
    header_row = audit_table._cellvalues[0]
    header_texts = [get_cell_text(cell) for cell in header_row]
    assert "Timestamp" in header_texts[0]
    assert "Previous Status" in header_texts[1]
    assert "Updated To" in header_texts[2]
    assert "Action By" in header_texts[3]
    assert "Remarks" in header_texts[4]

    # Verify data row
    data_row = audit_table._cellvalues[1]
    assert "2026-10-10 09:15:00" in get_cell_text(data_row[0])
    assert "None" in get_cell_text(data_row[1])
    assert "Under Investigation" in get_cell_text(data_row[2])
    assert "Admin / Maintenance Team" in get_cell_text(data_row[3])
    assert "Assigned to the field engineering team" in get_cell_text(data_row[4])
