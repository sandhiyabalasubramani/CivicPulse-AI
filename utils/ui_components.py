"""
UI Components and Visual Design System for CivicPulse AI.
Provides modern, colourful, SaaS-grade styling inspired by Linear, Stripe, and Notion.
Features high-contrast accessible typography (Poppins + Inter), custom KPI cards,
visual status steppers, AI analysis cards, and chronological audit timelines.
"""

from html import escape
from typing import Any, Dict, List, Optional
import streamlit as st


# =========================================================
# GLOBAL DESIGN SYSTEM & CUSTOM CSS
# =========================================================

def inject_custom_css() -> None:
    """
    Inject CivicPulse AI design system styles:
    - Google Fonts (Poppins & Inter)
    - Modern color palette (#172554, #2563EB, #6366F1, #8B5CF6, #0D9488, #06B6D4)
    - SaaS sidebar navigation
    - Custom KPI cards with hover elevation
    - Sleek buttons with smooth gradients
    - Form inputs with clear focus rings
    - Progress steppers and AI badge cards
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

        /* --------------------------------------------------
           CSS Reset & Global Typography
        -------------------------------------------------- */
        :root {
            --cp-navy: #172554;
            --cp-blue: #2563EB;
            --cp-indigo: #6366F1;
            --cp-violet: #8B5CF6;
            --cp-teal: #0D9488;
            --cp-cyan: #06B6D4;
            --cp-amber: #F59E0B;
            --cp-rose: #EF4444;
            --cp-bg: #F5F7FF;
            --cp-card-bg: #FFFFFF;
            --cp-text-main: #1E293B;
            --cp-text-sub: #64748B;
            --cp-border: #E2E8F0;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            color: var(--cp-text-main);
        }

        .stApp {
            background-color: var(--cp-bg) !important;
        }

        /* --------------------------------------------------
           Typography System
        -------------------------------------------------- */
        h1, h2, h3, h4, h5, h6,
        .civic-title, .civicpulse-title, .cp-heading {
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
            letter-spacing: -0.02em;
        }

        .civicpulse-header {
            padding: 0.5rem 0 1.25rem 0;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(226, 232, 240, 0.8);
        }

        .civicpulse-badge-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.1) 0%, rgba(99, 102, 241, 0.12) 100%);
            border: 1px solid rgba(99, 102, 241, 0.25);
            color: #4F46E5;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 8px;
        }

        .civicpulse-title {
            font-size: 2.15rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #4F46E5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.25;
            margin: 0;
        }

        .civicpulse-subtitle {
            font-size: 0.98rem;
            color: var(--cp-text-sub);
            margin-top: 6px;
            line-height: 1.55;
            font-weight: 400;
        }

        .civic-title {
            font-size: 2.15rem;
            font-weight: 700;
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 50%, #4F46E5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.25;
            margin-bottom: 4px;
        }

        .civic-subtitle {
            font-size: 0.98rem;
            color: var(--cp-text-sub);
            margin-bottom: 1.25rem;
            line-height: 1.55;
        }

        /* --------------------------------------------------
           Modern SaaS Sidebar Navigation
        -------------------------------------------------- */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #070B14 0%, #0F172A 40%, #172554 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        }

        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
            color: #F8FAFC !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.12) !important;
            margin: 14px 0 !important;
        }

        /* Sleek Radio Navigation as Interactive Menu Items */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            padding: 10px 14px !important;
            margin-bottom: 8px !important;
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer !important;
            width: 100% !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border-color: rgba(99, 102, 241, 0.5) !important;
            transform: translateX(4px) !important;
        }

        /* Active navigation item with vivid gradient glow */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked),
        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
            background: linear-gradient(135deg, rgba(37, 99, 235, 0.45) 0%, rgba(99, 102, 241, 0.55) 100%) !important;
            border-color: #818CF8 !important;
            box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
        }

        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label span {
            font-size: 0.92rem !important;
            font-weight: 600 !important;
            color: #FFFFFF !important;
        }

        /* Hide radio circle for a clean modern SaaS tab look */
        section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] > label div:first-child {
            display: none !important;
        }

        /* --------------------------------------------------
           Cards and Containers
        -------------------------------------------------- */
        .cp-card {
            background: #FFFFFF;
            border: 1px solid var(--cp-border);
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin-bottom: 1.25rem;
        }

        .cp-card:hover {
            box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.08), 0 4px 8px -2px rgba(0, 0, 0, 0.03);
        }

        .cp-ai-card {
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-left: 5px solid var(--cp-indigo);
            border-radius: 14px;
            padding: 20px;
            margin: 14px 0;
            box-shadow: 0 4px 18px rgba(99, 102, 241, 0.06);
        }

        .cp-similarity-box {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            border-left: 5px solid #F59E0B;
            border-radius: 12px;
            padding: 16px 18px;
            margin-top: 14px;
            margin-bottom: 14px;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.08);
        }

        /* Streamlit Native container borders styled as cards */
        div[data-testid="stVerticalBlock"] > div[style*="border:"] {
            border: 1px solid var(--cp-border) !important;
            border-radius: 16px !important;
            background: #FFFFFF !important;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
            padding: 20px !important;
        }

        /* --------------------------------------------------
           KPI Metric Cards
        -------------------------------------------------- */
        .cp-kpi-card {
            background: #FFFFFF;
            border: 1px solid var(--cp-border);
            border-radius: 14px;
            padding: 16px 18px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.05);
            transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1);
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .cp-kpi-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 24px -2px rgba(15, 23, 42, 0.1);
        }

        .cp-kpi-top-bar {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
        }

        .cp-kpi-label {
            font-size: 0.76rem;
            font-weight: 700;
            color: var(--cp-text-sub);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 4px;
        }

        .cp-kpi-value {
            font-family: 'Poppins', sans-serif;
            font-size: 1.85rem;
            font-weight: 700;
            color: #0F172A;
            line-height: 1.2;
            margin: 4px 0;
        }

        .cp-kpi-desc {
            font-size: 0.78rem;
            color: #64748B;
            font-weight: 500;
        }

        /* --------------------------------------------------
           Buttons & Interactive Elements
        -------------------------------------------------- */
        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"] {
            border-radius: 10px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 8px 18px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        /* Primary action button: vibrant gradient */
        .stButton > button[kind="primary"],
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(135deg, #2563EB 0%, #4F46E5 50%, #6366F1 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
        }

        .stButton > button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-1.5px) !important;
            box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
            filter: brightness(1.05) !important;
        }

        .stButton > button[kind="secondary"],
        button[data-testid="baseButton-secondary"] {
            background: #FFFFFF !important;
            color: var(--cp-text-main) !important;
            border: 1.5px solid var(--cp-border) !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        }

        .stButton > button[kind="secondary"]:hover,
        button[data-testid="baseButton-secondary"]:hover {
            border-color: var(--cp-indigo) !important;
            color: var(--cp-blue) !important;
            transform: translateY(-1px) !important;
        }

        /* Download button styling */
        div[data-testid="stDownloadButton"] > button {
            background: linear-gradient(135deg, #0D9488 0%, #059669 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(13, 148, 136, 0.25) !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stDownloadButton"] > button:hover {
            transform: translateY(-1.5px) !important;
            box-shadow: 0 6px 20px rgba(13, 148, 136, 0.35) !important;
            filter: brightness(1.05) !important;
        }

        /* --------------------------------------------------
           Input Fields & Form Elements
        -------------------------------------------------- */
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        div[data-baseweb="select"] > div {
            background-color: #FFFFFF !important;
            border-color: #CBD5E1 !important;
            border-radius: 10px !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }

        div[data-baseweb="input"]:focus-within > div,
        div[data-baseweb="textarea"]:focus-within > div,
        div[data-baseweb="select"]:focus-within > div {
            border-color: #4F46E5 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.18) !important;
        }

        input, textarea {
            color: #0F172A !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.95rem !important;
        }

        input::placeholder, textarea::placeholder {
            color: #94A3B8 !important;
        }

        label[data-testid="stWidgetLabel"] p {
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            color: #1E293B !important;
        }

        /* --------------------------------------------------
           Tabs Styling
        -------------------------------------------------- */
        div[data-testid="stTabs"] button[role="tab"] {
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            color: #64748B !important;
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 18px !important;
            transition: all 0.2s ease !important;
            border-bottom: 2px solid transparent !important;
        }

        div[data-testid="stTabs"] button[role="tab"]:hover {
            color: #2563EB !important;
        }

        div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
            color: #2563EB !important;
            border-bottom: 3px solid #2563EB !important;
            background: rgba(37, 99, 235, 0.04) !important;
        }

        /* --------------------------------------------------
           Expanders & Tables
        -------------------------------------------------- */
        div[data-testid="stExpander"] {
            background: #FFFFFF !important;
            border: 1px solid var(--cp-border) !important;
            border-radius: 12px !important;
            box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
            overflow: hidden !important;
        }

        div[data-testid="stExpander"] summary {
            font-weight: 600 !important;
            color: #1E293B !important;
        }

        /* Scrollbars */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #F1F5F9;
        }
        ::-webkit-scrollbar-thumb {
            background: #CBD5E1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #94A3B8;
        }

        /* Reduced motion accessibility */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation: none !important;
                transition: none !important;
            }
        }

        footer {
            visibility: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# STATUS BADGES
# =========================================================

def get_status_badge_html(status: str) -> str:
    """
    Return clean, colourful, accessible HTML badge for complaint status.
    Uses high-contrast color pairs and subtle indicator dot.
    """
    status_str = str(status or "Unknown").strip()
    safe_status = escape(status_str)
    s_lower = status_str.lower()

    # (Background, Text color, Border color, Icon dot color)
    palette = {
        "pending": ("#FEF3C7", "#92400E", "#FDE68A", "#D97706"),
        "assigned": ("#EDE9FE", "#5B21B6", "#DDD6FE", "#7C3AED"),
        "in progress": ("#DBEAFE", "#1E40AF", "#BFDBFE", "#2563EB"),
        "resolved": ("#D1FAE5", "#065F46", "#A7F3D0", "#059669"),
        "closed": ("#F1F5F9", "#334155", "#E2E8F0", "#64748B"),
    }
    bg, fg, border, dot = palette.get(s_lower, ("#F1F5F9", "#334155", "#CBD5E1", "#64748B"))

    return (
        f'<span class="status-badge" style="display:inline-flex;align-items:center;gap:6px;'
        f'padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:700;margin:2px;'
        f'background-color:{bg};color:{fg};border:1px solid {border};line-height:1.2;'
        f'box-shadow:0 1px 2px rgba(0,0,0,0.05);">'
        f'<span style="width:7px;height:7px;border-radius:50%;background-color:{dot};display:inline-block;"></span>'
        f'{safe_status}</span>'
    )


# =========================================================
# PRIORITY BADGES
# =========================================================

def get_priority_badge_html(priority: str) -> str:
    """
    Return clean, colourful, accessible HTML badge for complaint priority.
    """
    priority_str = str(priority or "Medium").strip()
    safe_priority = escape(priority_str)
    p_lower = priority_str.lower()

    # (Background, Text color, Border color, Icon)
    palette = {
        "critical": ("#FEE2E2", "#991B1B", "#FECACA", "🔴"),
        "high": ("#FFEDD5", "#9A3412", "#FED7AA", "🟠"),
        "medium": ("#FEF3C7", "#854D0E", "#FDE68A", "🟡"),
        "low": ("#E0F2FE", "#075985", "#BAE6FD", "🔵"),
    }
    bg, fg, border, icon = palette.get(p_lower, ("#F1F5F9", "#334155", "#E2E8F0", "⚪"))

    return (
        f'<span class="priority-badge" style="display:inline-flex;align-items:center;gap:5px;'
        f'padding:4px 12px;border-radius:20px;font-size:0.78rem;font-weight:700;margin:2px;'
        f'background-color:{bg};color:{fg};border:1px solid {border};line-height:1.2;'
        f'box-shadow:0 1px 2px rgba(0,0,0,0.05);">'
        f'<span>{icon}</span>'
        f'{safe_priority} Priority</span>'
    )


# =========================================================
# MODERN KPI METRIC CARD
# =========================================================

def render_metric_card(
    title: str,
    value: Any,
    *args,
    **kwargs
) -> None:
    """
    Render a modern, high-impact SaaS KPI card with top color strip,
    attractive metric number, and secondary caption.
    Maintains backward compatibility with delta and help kwargs.
    """
    # Extract description and color from positional args or kwargs
    desc = ""
    color = "#2563EB"
    icon = ""

    if len(args) >= 1 and isinstance(args[0], str):
        desc = args[0]
    elif "description" in kwargs:
        desc = str(kwargs["description"])

    if len(args) >= 2 and isinstance(args[1], str):
        color = args[1]
    elif "color" in kwargs:
        color = str(kwargs["color"])

    if len(args) >= 3 and isinstance(args[2], str):
        icon = args[2]
    elif "icon" in kwargs:
        icon = str(kwargs["icon"])

    # Fallback to standard st.metric if delta is explicitly provided
    if "delta" in kwargs and kwargs["delta"] is not None:
        st.metric(
            label=str(title),
            value=str(value),
            delta=kwargs["delta"],
            help=kwargs.get("help", None),
        )
        return

    safe_title = escape(str(title))
    safe_val = escape(str(value))
    safe_desc = escape(str(desc))
    safe_color = escape(str(color))
    safe_icon = escape(str(icon))

    icon_html = f'<span style="font-size:1.1rem;">{safe_icon}</span>' if safe_icon else ""
    desc_html = f'<div class="cp-kpi-desc">{safe_desc}</div>' if safe_desc else ""

    card_html = (
        f'<div class="cp-kpi-card" style="border-top:4px solid {safe_color};">'
        f'<div class="cp-kpi-label">'
        f'<span>{safe_title}</span>'
        f'{icon_html}'
        f'</div>'
        f'<div class="cp-kpi-value">{safe_val}</div>'
        f'{desc_html}'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


# =========================================================
# PAGE HERO HEADER
# =========================================================

def render_header(
    title: str,
    subtitle: str = "",
    icon: str = "",
    badge: str = "",
    *args,
    **kwargs
) -> None:
    """
    Render a CivicPulse AI page hero header with optional badge pill,
    modern gradient title, and elegant subtitle.
    """
    title_str = str(title or "").strip()
    sub_str = str(subtitle or "").strip()
    icon_str = str(icon or "").strip()
    badge_str = str(badge or kwargs.get("badge", "")).strip()

    display_title = f"{icon_str} {title_str}".strip() if icon_str else title_str

    badge_html = (
        f'<div class="civicpulse-badge-pill">{escape(badge_str)}</div>'
        if badge_str
        else ""
    )

    subtitle_html = (
        f'<div class="civicpulse-subtitle">{escape(sub_str)}</div>'
        if sub_str
        else ""
    )

    header_html = (
        f'<div class="civicpulse-header">'
        f'{badge_html}'
        f'<div class="civicpulse-title">{escape(display_title)}</div>'
        f'{subtitle_html}'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


# =========================================================
# STATUS STEPPER / PROGRESS TIMELINE
# =========================================================

def render_status_stepper(current_status: str) -> None:
    """
    Render a modern visual stepper timeline for complaint resolution:
    Pending -> Assigned -> In Progress -> Resolved
    Highlights completed steps with green checks and the active step with vibrant pulse.
    """
    steps = [
        ("Pending", "Submitted", "📥"),
        ("Assigned", "Routed", "🏢"),
        ("In Progress", "In Progress", "⚙️"),
        ("Resolved", "Resolved", "✅"),
    ]

    status_order = {
        "pending": 0,
        "assigned": 1,
        "in progress": 2,
        "resolved": 3,
        "closed": 4,
    }

    cur_idx = status_order.get(str(current_status or "").strip().lower(), 0)

    stepper_html = ['<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;padding:16px 20px;margin:12px 0 16px 0;box-shadow:0 2px 6px rgba(15,23,42,0.04);">']
    stepper_html.append('<div style="font-size:0.78rem;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:12px;">Resolution Progress Pipeline</div>')
    stepper_html.append('<div style="display:flex;align-items:center;justify-content:space-between;position:relative;">')

    for i, (key, label, icon) in enumerate(steps):
        is_completed = cur_idx > i or cur_idx == 4
        is_current = cur_idx == i and cur_idx != 4

        if is_completed:
            node_bg = "#10B981"
            node_fg = "#FFFFFF"
            node_border = "#059669"
            node_icon = "✓"
            text_color = "#0F172A"
            font_weight = "600"
        elif is_current:
            node_bg = "#2563EB"
            node_fg = "#FFFFFF"
            node_border = "#1D4ED8"
            node_icon = icon
            text_color = "#1D4ED8"
            font_weight = "700"
        else:
            node_bg = "#F1F5F9"
            node_fg = "#94A3B8"
            node_border = "#CBD5E1"
            node_icon = icon
            text_color = "#94A3B8"
            font_weight = "500"

        # Step Node
        stepper_html.append(
            f'<div style="display:flex;flex-direction:column;align-items:center;z-index:2;flex:1;">'
            f'<div style="width:36px;height:36px;border-radius:50%;background:{node_bg};color:{node_fg};'
            f'border:2px solid {node_border};display:flex;align-items:center;justify-content:center;'
            f'font-size:0.9rem;font-weight:700;box-shadow:0 2px 8px rgba(0,0,0,0.08);">'
            f'{node_icon}</div>'
            f'<div style="margin-top:6px;font-size:0.8rem;color:{text_color};font-weight:{font_weight};text-align:center;">'
            f'{label}</div>'
            f'</div>'
        )

        # Connector bar between steps
        if i < len(steps) - 1:
            line_color = "#10B981" if is_completed else ("#BFDBFE" if is_current else "#E2E8F0")
            stepper_html.append(
                f'<div style="flex:1;height:3px;background:{line_color};margin-top:-20px;z-index:1;border-radius:2px;"></div>'
            )

    stepper_html.append('</div></div>')
    st.markdown("".join(stepper_html), unsafe_allow_html=True)


# =========================================================
# CHRONOLOGICAL AUDIT TIMELINE
# =========================================================

def render_timeline(
    history: List[Dict[str, Any]],
    *args,
    **kwargs
) -> None:
    """
    Render complaint status audit history in a chronological, human-readable timeline.
    Uses safe HTML without newlines or markdown indentation to eliminate raw tag leaking.
    """
    if history is None:
        history = []

    if not history:
        st.info("ℹ️ No audit history records are currently available for this ticket.")
        return

    for item in history:
        if not isinstance(item, dict):
            item = {"status": str(item)}

        status_text = str(
            item.get("status")
            or item.get("new_status")
            or "Status Update"
        ).strip()

        timestamp_text = str(
            item.get("timestamp")
            or item.get("changed_at")
            or item.get("created_at")
            or "Recorded"
        ).strip()

        raw_remarks = str(
            item.get("remarks")
            or item.get("comment")
            or item.get("note")
            or item.get("admin_notes")
            or ""
        ).strip()

        changed_by = str(item.get("changed_by") or "").strip()

        if raw_remarks and changed_by:
            if raw_remarks.lower().startswith("action by"):
                action_text = raw_remarks
            else:
                action_text = f"Action by {changed_by}: {raw_remarks}"
        elif raw_remarks:
            action_text = raw_remarks
        elif changed_by:
            action_text = f"Action logged by {changed_by}"
        else:
            action_text = f"Status transitioned to {status_text}"

        badge_html = get_status_badge_html(status_text)
        safe_time = escape(timestamp_text)
        safe_action = escape(action_text)

        action_html = (
            f'<div style="margin-top:6px;font-size:0.88rem;color:#334155;line-height:1.5;">'
            f'{safe_action}</div>'
            if safe_action
            else ""
        )

        timeline_item_html = (
            f'<div style="border-left:4px solid #3B82F6;background-color:#FFFFFF;'
            f'border-top:1px solid #E2E8F0;border-right:1px solid #E2E8F0;border-bottom:1px solid #E2E8F0;'
            f'border-radius:0 12px 12px 0;padding:12px 16px;margin-bottom:10px;box-shadow:0 1px 3px rgba(0,0,0,0.03);">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
            f'<div>{badge_html}</div>'
            f'<span style="font-size:0.82rem;color:#64748B;font-weight:600;font-family:\'JetBrains Mono\', monospace;">🕒 {safe_time}</span>'
            f'</div>'
            f'{action_html}'
            f'</div>'
        )
        st.markdown(timeline_item_html, unsafe_allow_html=True)


# =========================================================
# AI ANALYSIS VISUAL CARD
# =========================================================

def render_ai_triage_card(
    category: str,
    subcategory: str,
    priority: str,
    priority_score: Any,
    department: str,
    sla_hours: Any = "",
    routing_type: str = "",
    priority_reason: str = ""
) -> None:
    """
    Renders an elegant, high-impact AI triage and department routing visual panel.
    Highlights intelligent classification without falsely claiming capabilities.
    """
    safe_cat = escape(str(category or "General"))
    safe_subcat = escape(str(subcategory or "General"))
    safe_dept = escape(str(department or "General Administration"))
    safe_reason = escape(str(priority_reason or "Automated keyword and rule triage"))
    safe_sla = escape(str(sla_hours or "N/A"))
    safe_routing = escape(str(routing_type or "Rule-based routing"))

    try:
        score_val = int(priority_score)
    except (ValueError, TypeError):
        score_val = 50

    # Color for score gauge
    if score_val >= 75:
        score_color = "#EF4444"
        score_label = "Critical Urgency"
    elif score_val >= 50:
        score_color = "#F59E0B"
        score_label = "Elevated Priority"
    else:
        score_color = "#10B981"
        score_label = "Standard Priority"

    prio_badge = get_priority_badge_html(priority)

    html = (
        f'<div style="background:linear-gradient(135deg, rgba(99,102,241,0.03) 0%, rgba(6,182,212,0.04) 100%);'
        f'border:1.5px solid #C7D2FE;border-radius:16px;padding:22px;margin:16px 0;box-shadow:0 4px 18px rgba(99,102,241,0.06);">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px;border-bottom:1px solid #E0E7FF;padding-bottom:12px;">'
        f'<div style="display:flex;align-items:center;gap:8px;">'
        f'<span style="font-size:1.3rem;">🤖</span>'
        f'<span style="font-family:\'Poppins\', sans-serif;font-weight:700;font-size:1.1rem;color:#1E1B4B;">CivicPulse AI Automated Triage</span>'
        f'<span style="background:#EEF2FF;color:#4F46E5;border:1px solid #C7D2FE;padding:2px 8px;border-radius:12px;font-size:0.72rem;font-weight:700;">TF-IDF + RULES</span>'
        f'</div>'
        f'<div>{prio_badge}</div>'
        f'</div>'
        f'<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));gap:14px;margin-bottom:14px;">'
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;padding:12px;">'
        f'<div style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;">Predicted Category</div>'
        f'<div style="font-size:1.05rem;font-weight:700;color:#0F172A;margin-top:2px;">{safe_cat}</div>'
        f'<div style="font-size:0.8rem;color:#6366F1;font-weight:500;">Sub: {safe_subcat}</div>'
        f'</div>'
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;padding:12px;">'
        f'<div style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;">Priority Score</div>'
        f'<div style="display:flex;align-items:center;gap:8px;margin-top:2px;">'
        f'<span style="font-family:\'Poppins\', sans-serif;font-size:1.3rem;font-weight:700;color:{score_color};">{score_val}/100</span>'
        f'<span style="font-size:0.75rem;color:{score_color};font-weight:600;">({score_label})</span>'
        f'</div>'
        f'<div style="background:#F1F5F9;border-radius:4px;height:5px;width:100%;margin-top:6px;overflow:hidden;">'
        f'<div style="background:{score_color};height:100%;width:{score_val}%;"></div>'
        f'</div>'
        f'</div>'
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;padding:12px;">'
        f'<div style="font-size:0.75rem;font-weight:700;color:#64748B;text-transform:uppercase;">Routed Department</div>'
        f'<div style="font-size:0.95rem;font-weight:700;color:#0F172A;margin-top:2px;">{safe_dept}</div>'
        f'<div style="font-size:0.8rem;color:#0D9488;font-weight:600;">⚡ SLA: {safe_sla} hours</div>'
        f'</div>'
        f'</div>'
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;padding:10px 14px;font-size:0.85rem;color:#334155;">'
        f'<span style="font-weight:600;color:#1E293B;">🔍 Assessment Rationale:</span> {safe_reason} '
        f'<span style="color:#64748B;">• Method: {safe_routing}</span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


# =========================================================
# COMPATIBILITY HELPERS
# =========================================================

def render_status_badge(status: str) -> None:
    """Directly render a status badge."""
    st.markdown(get_status_badge_html(status), unsafe_allow_html=True)


def render_priority_badge(priority: str) -> None:
    """Directly render a priority badge."""
    st.markdown(get_priority_badge_html(priority), unsafe_allow_html=True)


def render_section_header(
    title: str,
    description: str = "",
    icon: str = ""
) -> None:
    """Render a generic section header with modern typography."""
    heading = f"{icon} {title}".strip() if icon else title
    st.subheader(heading)
    if description:
        st.caption(description)