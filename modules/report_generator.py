"""
PDF Report Generator for CivicPulse AI using ReportLab.
Generates:
1. Individual Complaint Resolution Docket PDF
2. Executive Management Summary & Hotspot Analytics PDF
"""

import io
from datetime import datetime
from typing import Dict, List, Any, Optional

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether


def create_complaint_docket_pdf(complaint: Dict[str, Any], history: List[Dict[str, Any]]) -> bytes:
    """
    Builds a professional PDF docket for an individual complaint.
    Returns PDF binary bytes for download.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary_color = colors.HexColor("#1E293B")  # Dark slate
    accent_color = colors.HexColor("#2563EB")   # Royal blue
    text_dark = colors.HexColor("#0F172A")
    text_muted = colors.HexColor("#64748B")
    border_color = colors.HexColor("#E2E8F0")
    bg_light = colors.HexColor("#F8FAFC")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted
    )

    section_header = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    bold_label = ParagraphStyle(
        'BoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=primary_color
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("CivicPulse AI &bull; Official Complaint Docket", title_style))
    story.append(Paragraph(f"Complaint Reference: <b>{complaint.get('complaint_id', 'N/A')}</b> &bull; Generated on {datetime.now().strftime('%b %d, %Y %I:%M %p')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=2, spaceAfter=12))

    # 2. Key Metadata Summary Table
    cid = complaint.get("complaint_id", "N/A")
    status = complaint.get("status", "Pending")
    priority = complaint.get("priority", "Medium")
    category = complaint.get("category", "General")
    subcat = complaint.get("subcategory", "General")
    dept = complaint.get("department", "General Administration")
    loc = complaint.get("location", "N/A")
    created = complaint.get("created_at", "N/A")
    resolved = complaint.get("resolved_at") or "Not yet resolved"

    meta_data = [
        [
            Paragraph("<b>Complaint ID:</b>", bold_label), Paragraph(cid, body_style),
            Paragraph("<b>Status:</b>", bold_label), Paragraph(f"<b>{status}</b>", body_style)
        ],
        [
            Paragraph("<b>Priority Level:</b>", bold_label), Paragraph(f"<b>{priority}</b>", body_style),
            Paragraph("<b>Category:</b>", bold_label), Paragraph(category, body_style)
        ],
        [
            Paragraph("<b>Subcategory:</b>", bold_label), Paragraph(subcat, body_style),
            Paragraph("<b>Assigned Dept:</b>", bold_label), Paragraph(dept, body_style)
        ],
        [
            Paragraph("<b>Location:</b>", bold_label), Paragraph(loc, body_style),
            Paragraph("<b>Submitted On:</b>", bold_label), Paragraph(created, body_style)
        ],
        [
            Paragraph("<b>Resolved On:</b>", bold_label), Paragraph(str(resolved), body_style),
            Paragraph("<b>Priority Signal:</b>", bold_label), Paragraph(complaint.get("priority_reason") or "Rule-based analysis", body_style)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[105, 160, 105, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 0.75, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # 3. Submitter Information
    story.append(Paragraph("1. Complainant Details", section_header))
    sub_data = [
        [Paragraph("<b>Full Name:</b>", bold_label), Paragraph(complaint.get("name", "N/A"), body_style)],
        [Paragraph("<b>Email Address:</b>", bold_label), Paragraph(complaint.get("email", "N/A"), body_style)],
        [Paragraph("<b>Location Context:</b>", bold_label), Paragraph(complaint.get("location", "N/A"), body_style)],
    ]
    sub_table = Table(sub_data, colWidths=[120, 410])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 14))

    # 4. Complaint Substance & Description
    story.append(Paragraph("2. Grievance Statement", section_header))
    desc_content = [
        [Paragraph("<b>Subject Title:</b>", bold_label), Paragraph(f"<b>{complaint.get('title', 'N/A')}</b>", body_style)],
        [Paragraph("<b>Full Description:</b>", bold_label), Paragraph(complaint.get("description", "N/A"), body_style)],
        [Paragraph("<b>Admin Notes:</b>", bold_label), Paragraph(complaint.get("admin_notes") or "None recorded", body_style)],
    ]
    desc_table = Table(desc_content, colWidths=[120, 410])
    desc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(desc_table)
    story.append(Spacer(1, 14))

    # 5. NLP Similarity & Redundancy Insights
    story.append(Paragraph("3. AI / NLP Similarity Analysis", section_header))
    sim_count = complaint.get("similar_count", 0)
    sim_score = complaint.get("top_similarity_score", 0.0)
    top_sim_id = complaint.get("top_similar_id", "None")
    
    sim_text = f"TF-IDF & Cosine Similarity detected <b>{sim_count} potentially similar complaints</b> in historical database."
    if sim_count > 0:
        sim_text += f" Highest match reference: <b>{top_sim_id}</b> with <b>{round(sim_score * 100, 1)}%</b> semantic overlap."

    sim_data = [
        [Paragraph("<b>Similarity Check:</b>", bold_label), Paragraph(sim_text, body_style)]
    ]
    sim_table = Table(sim_data, colWidths=[120, 410])
    sim_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(sim_table)
    story.append(Spacer(1, 14))

    # 6. Status History Timeline Table
    story.append(Paragraph("4. Audit Trail & Status History", section_header))
    if history:
        hist_headers = [
            Paragraph("<b>Timestamp</b>", bold_label),
            Paragraph("<b>Previous</b>", bold_label),
            Paragraph("<b>Updated To</b>", bold_label),
            Paragraph("<b>Action By</b>", bold_label),
            Paragraph("<b>Remarks</b>", bold_label)
        ]
        hist_rows = [hist_headers]
        for h in history:
            hist_rows.append([
                Paragraph(h.get("changed_at", ""), body_style),
                Paragraph(h.get("old_status", ""), body_style),
                Paragraph(f"<b>{h.get('new_status', '')}</b>", body_style),
                Paragraph(h.get("changed_by", "Admin"), body_style),
                Paragraph(h.get("comment", "-") or "-", body_style)
            ])

        hist_table = Table(hist_rows, colWidths=[105, 75, 80, 80, 190])
        hist_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
            ('BOX', (0, 0), (-1, -1), 0.5, border_color),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light])
        ]))
        story.append(hist_table)
    else:
        story.append(Paragraph("No previous transitions recorded.", body_style))

    # Build Document
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes


def create_summary_analytics_pdf(
    kpis: Dict[str, Any],
    category_df: Any,
    priority_df: Any,
    hotspots: Dict[str, Any]
) -> bytes:
    """
    Builds an executive management summary & problem hotspot analytics report in PDF.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    primary_color = colors.HexColor("#1E293B")
    accent_color = colors.HexColor("#2563EB")
    text_dark = colors.HexColor("#0F172A")
    text_muted = colors.HexColor("#64748B")
    border_color = colors.HexColor("#CBD5E1")
    bg_light = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle(
        'ExecTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        'ExecSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted
    )

    section_header = ParagraphStyle(
        'ExecSection',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'ExecBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )

    bold_label = ParagraphStyle(
        'ExecBoldLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=primary_color
    )

    story = []

    # Title & Header
    story.append(Paragraph("CivicPulse AI &bull; Executive Resolution Report", title_style))
    story.append(Paragraph(f"System-wide Grievance Analytics & Hotspot Briefing &bull; {datetime.now().strftime('%B %d, %Y')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=2, spaceAfter=12))

    # 1. Key Performance Indicators (KPIs)
    story.append(Paragraph("1. Platform Operational Overview", section_header))
    kpi_data = [
        [
            Paragraph("<b>Total Complaints</b>", bold_label),
            Paragraph("<b>Pending</b>", bold_label),
            Paragraph("<b>In Progress</b>", bold_label),
            Paragraph("<b>Resolved</b>", bold_label),
            Paragraph("<b>Critical / High</b>", bold_label),
            Paragraph("<b>Avg Resolution</b>", bold_label)
        ],
        [
            Paragraph(f"<font size=12><b>{kpis.get('total', 0)}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#D97706'><b>{kpis.get('pending', 0)}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#2563EB'><b>{kpis.get('in_progress', 0)}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#16A34A'><b>{kpis.get('resolved', 0)}</b></font>", body_style),
            Paragraph(f"<font size=12 color='#DC2626'><b>{kpis.get('critical_priority', 0) + kpis.get('high_priority', 0)}</b></font>", body_style),
            Paragraph(f"<font size=12><b>{kpis.get('avg_resolution_hours', 0.0)} hrs</b></font>", body_style),
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[88, 88, 88, 88, 92, 86])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('BOX', (0, 0), (-1, -1), 0.75, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    # 2. Problem Hotspots Section
    story.append(Paragraph("2. Problem Hotspot Intelligence", section_header))
    hotspot_rows = [
        [Paragraph("<b>Most Reported Category:</b>", bold_label), Paragraph(f"{hotspots.get('top_category', 'N/A')} ({hotspots.get('top_category_count', 0)} incidents)", body_style)],
        [Paragraph("<b>Most Affected Location:</b>", bold_label), Paragraph(f"{hotspots.get('top_location', 'N/A')} ({hotspots.get('top_location_count', 0)} incidents)", body_style)],
        [Paragraph("<b>Most Common Subcategory:</b>", bold_label), Paragraph(f"{hotspots.get('top_subcategory', 'N/A')} ({hotspots.get('top_subcategory_count', 0)} incidents)", body_style)],
        [Paragraph("<b>Top Bottleneck Department:</b>", bold_label), Paragraph(f"{hotspots.get('top_dept_backlog', 'N/A')}", body_style)],
    ]
    hotspot_table = Table(hotspot_rows, colWidths=[160, 370])
    hotspot_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor("#86EFAC")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#BBF7D0")),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(hotspot_table)
    story.append(Spacer(1, 14))

    # 3. Category Breakdown Table
    story.append(Paragraph("3. Category Distribution Breakdown", section_header))
    cat_rows = [[
        Paragraph("<b>Category</b>", bold_label),
        Paragraph("<b>Count</b>", bold_label),
        Paragraph("<b>Percentage</b>", bold_label),
        Paragraph("<b>Pending / Unresolved</b>", bold_label)
    ]]

    if category_df is not None and not category_df.empty:
        total_c = category_df['count'].sum() if 'count' in category_df.columns else 1
        for _, r in category_df.iterrows():
            c_name = str(r.get('category', 'Unknown'))
            c_cnt = int(r.get('count', 0))
            c_pct = f"{round((c_cnt / total_c) * 100, 1)}%"
            c_unresolved = str(r.get('unresolved', '-'))
            cat_rows.append([
                Paragraph(c_name, body_style),
                Paragraph(str(c_cnt), body_style),
                Paragraph(c_pct, body_style),
                Paragraph(c_unresolved, body_style)
            ])
    else:
        cat_rows.append([Paragraph("No category data available.", body_style), Paragraph("-", body_style), Paragraph("-", body_style), Paragraph("-", body_style)])

    cat_table = Table(cat_rows, colWidths=[180, 80, 110, 160])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light])
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 14))

    # 4. Priority Breakdown Table
    story.append(Paragraph("4. Urgency & Priority Breakdown", section_header))
    prio_rows = [[
        Paragraph("<b>Priority Level</b>", bold_label),
        Paragraph("<b>Total Logged</b>", bold_label),
        Paragraph("<b>Resolution Rate</b>", bold_label)
    ]]
    if priority_df is not None and not priority_df.empty:
        for _, r in priority_df.iterrows():
            p_name = str(r.get('priority', 'Unknown'))
            p_cnt = int(r.get('count', 0))
            p_res = str(r.get('rate', '-'))
            prio_rows.append([
                Paragraph(f"<b>{p_name}</b>", body_style),
                Paragraph(str(p_cnt), body_style),
                Paragraph(p_res, body_style)
            ])
    else:
        prio_rows.append([Paragraph("No priority data available.", body_style), Paragraph("-", body_style), Paragraph("-", body_style)])

    prio_table = Table(prio_rows, colWidths=[180, 150, 200])
    prio_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ('BOX', (0, 0), (-1, -1), 0.5, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light])
    ]))
    story.append(prio_table)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
