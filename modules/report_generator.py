"""
PDF Report Generator for CivicPulse AI using ReportLab.
Generates:
1. Individual Complaint Resolution Docket PDF
2. Executive Management Summary & Hotspot Analytics PDF
"""

import html
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

    audit_header_style = ParagraphStyle(
        'AuditHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=primary_color,
        wordWrap='CJK'
    )

    audit_body_style = ParagraphStyle(
        'AuditBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=text_dark,
        wordWrap='CJK'
    )

    audit_status_style = ParagraphStyle(
        'AuditStatus',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=text_dark,
        wordWrap='CJK'
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("CivicPulse AI &bull; Official Complaint Docket", title_style))
    story.append(Paragraph(f"Complaint Reference: <b>{complaint.get('complaint_id', 'N/A')}</b> &bull; Generated on {datetime.now().strftime('%b %d, %Y %I:%M %p')}", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=2, spaceAfter=12))

    # 2. Key Metadata Summary Table
    cid = html.escape(str(complaint.get("complaint_id") or "N/A"))
    status = html.escape(str(complaint.get("status") or "Pending"))
    priority = html.escape(str(complaint.get("priority") or "Medium"))
    category = html.escape(str(complaint.get("category") or "General"))
    subcat = html.escape(str(complaint.get("subcategory") or "General"))
    dept = html.escape(str(complaint.get("department") or "General Administration"))
    loc = html.escape(str(complaint.get("location") or "N/A"))
    created = html.escape(str(complaint.get("created_at") or "N/A"))
    resolved = html.escape(str(complaint.get("resolved_at") or "Not yet resolved"))
    p_signal = html.escape(str(complaint.get("priority_reason") or "Rule-based analysis"))

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
            Paragraph("<b>Resolved On:</b>", bold_label), Paragraph(resolved, body_style),
            Paragraph("<b>Priority Signal:</b>", bold_label), Paragraph(p_signal, body_style)
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
    name_val = html.escape(str(complaint.get("name") or "N/A"))
    email_val = html.escape(str(complaint.get("email") or "N/A"))
    loc_val = html.escape(str(complaint.get("location") or "N/A"))
    sub_data = [
        [Paragraph("<b>Full Name:</b>", bold_label), Paragraph(name_val, body_style)],
        [Paragraph("<b>Email Address:</b>", bold_label), Paragraph(email_val, body_style)],
        [Paragraph("<b>Location Context:</b>", bold_label), Paragraph(loc_val, body_style)],
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
    title_val = html.escape(str(complaint.get("title") or "N/A"))
    desc_val = html.escape(str(complaint.get("description") or "N/A"))
    admin_notes_val = html.escape(str(complaint.get("admin_notes") or "None recorded"))
    desc_content = [
        [Paragraph("<b>Subject Title:</b>", bold_label), Paragraph(f"<b>{title_val}</b>", body_style)],
        [Paragraph("<b>Full Description:</b>", bold_label), Paragraph(desc_val, body_style)],
        [Paragraph("<b>Admin Notes:</b>", bold_label), Paragraph(admin_notes_val, body_style)],
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
            Paragraph("<b>Timestamp</b>", audit_header_style),
            Paragraph("<b>Previous Status</b>", audit_header_style),
            Paragraph("<b>Updated To</b>", audit_header_style),
            Paragraph("<b>Action By</b>", audit_header_style),
            Paragraph("<b>Remarks</b>", audit_header_style)
        ]
        hist_rows = [hist_headers]
        for h in history:
            if not isinstance(h, dict):
                continue
            ts = html.escape(str(h.get("changed_at") or h.get("timestamp") or h.get("created_at") or "-")).strip() or "-"
            old_st = html.escape(str(h.get("old_status") or "None")).strip() or "None"
            new_st = html.escape(str(h.get("new_status") or h.get("status") or "-")).strip() or "-"
            by = html.escape(str(h.get("changed_by") or h.get("action_by") or "Admin")).strip() or "Admin"
            rem = html.escape(str(h.get("comment") or h.get("remarks") or h.get("note") or "-")).strip() or "-"

            hist_rows.append([
                Paragraph(ts, audit_body_style),
                Paragraph(old_st, audit_body_style),
                Paragraph(f"<b>{new_st}</b>", audit_status_style),
                Paragraph(by, audit_body_style),
                Paragraph(rem, audit_body_style)
            ])

        if len(hist_rows) > 1:
            hist_table = Table(hist_rows, colWidths=[90, 80, 85, 100, 175], repeatRows=1)
            hist_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
                ('BOX', (0, 0), (-1, -1), 0.5, border_color),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light])
            ]))
            story.append(hist_table)
        else:
            story.append(Paragraph("No previous transitions recorded.", body_style))
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
    kpis = kpis or {}
    total_val = kpis.get('total', 0) or 0
    pending_val = kpis.get('pending', 0) or 0
    assigned_val = kpis.get('assigned', 0) or 0
    in_progress_val = kpis.get('in_progress', 0) or 0
    resolved_val = kpis.get('resolved', 0) or 0
    crit_val = kpis.get('critical_priority', 0) or 0
    high_val = kpis.get('high_priority', 0) or 0
    crit_high_total = crit_val + high_val
    avg_res_val = kpis.get('avg_resolution_hours', 0.0) or 0.0

    story.append(Paragraph("1. Platform Operational Overview", section_header))
    kpi_data = [
        [
            Paragraph("<b>Total Complaints</b>", bold_label),
            Paragraph("<b>Pending</b>", bold_label),
            Paragraph("<b>Assigned</b>", bold_label),
            Paragraph("<b>In Progress</b>", bold_label),
            Paragraph("<b>Resolved</b>", bold_label),
            Paragraph("<b>Critical / High</b>", bold_label),
            Paragraph("<b>Avg Resolution</b>", bold_label)
        ],
        [
            Paragraph(f"<font size=11><b>{total_val}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#D97706'><b>{pending_val}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#7C3AED'><b>{assigned_val}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#2563EB'><b>{in_progress_val}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#16A34A'><b>{resolved_val}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#DC2626'><b>{crit_high_total}</b></font>", body_style),
            Paragraph(f"<font size=11><b>{avg_res_val} hrs</b></font>", body_style),
        ]
    ]

    kpi_table = Table(kpi_data, colWidths=[76, 74, 74, 76, 76, 78, 78])
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
    hotspots = hotspots or {}
    top_cat = html.escape(str(hotspots.get('top_category', 'N/A') or 'N/A'))
    top_cat_cnt = hotspots.get('top_category_count', 0) or 0
    top_loc = html.escape(str(hotspots.get('top_location', 'N/A') or 'N/A'))
    top_loc_cnt = hotspots.get('top_location_count', 0) or 0
    top_sub = html.escape(str(hotspots.get('top_subcategory', 'N/A') or 'N/A'))
    top_sub_cnt = hotspots.get('top_subcategory_count', 0) or 0
    top_dept = html.escape(str(hotspots.get('top_dept_backlog', 'N/A') or 'N/A'))

    story.append(Paragraph("2. Problem Hotspot Intelligence", section_header))
    hotspot_rows = [
        [Paragraph("<b>Most Reported Category:</b>", bold_label), Paragraph(f"{top_cat} ({top_cat_cnt} incidents)", body_style)],
        [Paragraph("<b>Most Affected Location:</b>", bold_label), Paragraph(f"{top_loc} ({top_loc_cnt} incidents)", body_style)],
        [Paragraph("<b>Most Common Subcategory:</b>", bold_label), Paragraph(f"{top_sub} ({top_sub_cnt} incidents)", body_style)],
        [Paragraph("<b>Top Bottleneck Department:</b>", bold_label), Paragraph(top_dept, body_style)],
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

    if category_df is not None and hasattr(category_df, 'empty') and not category_df.empty:
        try:
            total_c = float(category_df['count'].sum()) if 'count' in category_df.columns else 0.0
        except Exception:
            total_c = 0.0
        if total_c <= 0:
            total_c = 1.0

        for _, r in category_df.iterrows():
            c_name = html.escape(str(r.get('category', 'Unknown') or 'Unknown'))
            try:
                c_cnt = int(r.get('count', 0) or 0)
            except (ValueError, TypeError):
                c_cnt = 0
            c_pct = f"{round((c_cnt / total_c) * 100, 1)}%"
            c_unresolved = html.escape(str(r.get('unresolved', '-') or '-'))
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
    if priority_df is not None and hasattr(priority_df, 'empty') and not priority_df.empty:
        for _, r in priority_df.iterrows():
            p_name = html.escape(str(r.get('priority', 'Unknown') or 'Unknown'))
            try:
                p_cnt = int(r.get('count', 0) or 0)
            except (ValueError, TypeError):
                p_cnt = 0
            p_res = html.escape(str(r.get('rate', '-') or '-'))
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
