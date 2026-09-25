"""
UI Components and Custom CSS for CivicPulse AI Streamlit interface.
Provides modern, clean, portfolio-grade styling, status badges, metric cards,
and visual timeline components.
"""

import streamlit as st
from typing import Dict, List, Any, Optional


def inject_custom_css():
    """Injects high-finish custom styling for a sleek, modern, professional dashboard look."""
    st.markdown("""
        <style>
        /* Main Theme Variables & Clean Typography */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Top Header Styling */
        .cp-header-container {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 1.5rem 2rem;
            border-radius: 12px;
            color: #f8fafc;
            margin-bottom: 1.5rem;
            border: 1px solid #334155;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        }

        .cp-header-title {
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #ffffff;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.6rem;
        }

        .cp-header-subtitle {
            font-size: 0.95rem;
            color: #94a3b8;
            margin-top: 0.35rem;
            font-weight: 400;
        }

        /* Modern Metric Card */
        .cp-metric-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 1.1rem 1.25rem;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
            transition: all 0.2s ease-in-out;
            height: 100%;
        }

        .cp-metric-card:hover {
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
            transform: translateY(-2px);
            border-color: #cbd5e1;
        }

        .cp-metric-label {
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 0.3rem;
        }

        .cp-metric-value {
            font-size: 1.75rem;
            font-weight: 800;
            color: #0f172a;
            line-height: 1.2;
            font-family: 'Inter', sans-serif;
        }

        .cp-metric-subtext {
            font-size: 0.75rem;
            color: #94a3b8;
            margin-top: 0.3rem;
        }

        /* Status Badges */
        .badge-pending {
            background-color: #FEF3C7;
            color: #92400E;
            border: 1px solid #FCD34D;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .badge-assigned {
            background-color: #EEF2FF;
            color: #4338CA;
            border: 1px solid #C7D2FE;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .badge-in-progress {
            background-color: #DBEAFE;
            color: #1E40AF;
            border: 1px solid #93C5FD;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .badge-resolved {
            background-color: #DCFCE7;
            color: #166534;
            border: 1px solid #86EFAC;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .badge-closed {
            background-color: #F1F5F9;
            color: #334155;
            border: 1px solid #CBD5E1;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        /* Priority Badges */
        .badge-critical {
            background-color: #FEE2E2;
            color: #991B1B;
            border: 1px solid #FCA5A5;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }

        .badge-high {
            background-color: #FFEDD5;
            color: #9A3412;
            border: 1px solid #FDBA74;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            display: inline-block;
        }

        .badge-medium {
            background-color: #E0F2FE;
            color: #0369A1;
            border: 1px solid #7DD3FC;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }

        .badge-low {
            background-color: #F3F4F6;
            color: #4B5563;
            border: 1px solid #D1D5DB;
            padding: 3px 9px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            display: inline-block;
        }

        /* AI Analysis Card */
        .cp-ai-card {
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-left: 4px solid #3B82F6;
            border-radius: 8px;
            padding: 1.25rem;
            margin: 1rem 0;
        }

        .cp-similarity-box {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            border-left: 4px solid #F59E0B;
            border-radius: 8px;
            padding: 1rem 1.2rem;
            margin: 0.75rem 0;
        }

        /* Timeline Items */
        .timeline-container {
            position: relative;
            padding-left: 20px;
            border-left: 2px solid #E2E8F0;
            margin-left: 10px;
            margin-top: 15px;
        }

        .timeline-item {
            position: relative;
            margin-bottom: 20px;
        }

        .timeline-point {
            position: absolute;
            left: -26px;
            top: 2px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #3B82F6;
            border: 2px solid #EFF6FF;
        }

        .timeline-time {
            font-size: 0.75rem;
            color: #94A3B8;
            font-family: 'JetBrains Mono', monospace;
        }

        .timeline-title {
            font-weight: 600;
            font-size: 0.88rem;
            color: #1E293B;
            margin: 2px 0;
        }

        .timeline-desc {
            font-size: 0.82rem;
            color: #64748B;
        }

        /* Code & Monospace Badges */
        .code-badge {
            font-family: 'JetBrains Mono', monospace;
            background: #F1F5F9;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #334155;
            border: 1px solid #E2E8F0;
        }

        /* Hotspot Highlight Cards */
        .hotspot-card {
            background: #FAFAFA;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 1.2rem;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)


def get_status_badge_html(status: str) -> str:
    """Returns HTML for modern status badge."""
    status_class_map = {
        "Pending": "badge-pending",
        "Assigned": "badge-assigned",
        "In Progress": "badge-in-progress",
        "Resolved": "badge-resolved",
        "Closed": "badge-closed"
    }
    css_class = status_class_map.get(status, "badge-pending")
    return f'<span class="{css_class}">{status}</span>'


def get_priority_badge_html(priority: str) -> str:
    """Returns HTML for modern priority badge."""
    prio_class_map = {
        "Critical": "badge-critical",
        "High": "badge-high",
        "Medium": "badge-medium",
        "Low": "badge-low"
    }
    css_class = prio_class_map.get(priority, "badge-medium")
    return f'<span class="{css_class}">{priority}</span>'


def render_metric_card(label: str, value: Any, subtext: str = "", color: str = "#0f172a"):
    """Renders a clean modern metric card container."""
    st.markdown(f"""
        <div class="cp-metric-card">
            <div class="cp-metric-label">{label}</div>
            <div class="cp-metric-value" style="color: {color};">{value}</div>
            {f'<div class="cp-metric-subtext">{subtext}</div>' if subtext else ''}
        </div>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, icon: str = "🏛️"):
    """Renders top hero header for pages."""
    st.markdown(f"""
        <div class="cp-header-container">
            <div class="cp-header-title">{icon} {title}</div>
            <div class="cp-header-subtitle">{subtitle}</div>
        </div>
    """, unsafe_allow_html=True)


def render_timeline(history: List[Dict[str, Any]]):
    """Renders visual status timeline in HTML."""
    if not history:
        st.info("No status transitions recorded yet.")
        return

    html_parts = ['<div class="timeline-container">']
    for entry in history:
        timestamp = entry.get("changed_at", "")
        old_s = entry.get("old_status", "")
        new_s = entry.get("new_status", "")
        by = entry.get("changed_by", "Admin")
        comment = entry.get("comment", "")
        
        status_text = f"Status changed to <b>{new_s}</b>" if old_s != "None" else f"Complaint logged with status <b>{new_s}</b>"
        
        html_parts.append(f"""
            <div class="timeline-item">
                <div class="timeline-point"></div>
                <div class="timeline-time">{timestamp} &bull; by {by}</div>
                <div class="timeline-title">{status_text}</div>
                {f'<div class="timeline-desc">{comment}</div>' if comment else ''}
            </div>
        """)
    html_parts.append('</div>')
    st.markdown("".join(html_parts), unsafe_allow_html=True)
