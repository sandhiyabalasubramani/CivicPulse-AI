"""
UI Components and Visual Helpers for CivicPulse AI.
Provides page headers, status/priority badges, metrics, and timeline visualizations.
"""

from html import escape
from typing import Any, Dict, List, Optional
import streamlit as st


# =========================================================
# CUSTOM CSS
# =========================================================

def inject_custom_css() -> None:
    """
    Inject CivicPulse AI design system styles.
    """
    st.markdown(
        """
        <style>
        .civic-title {
            font-size: 2rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.25rem;
        }

        .civic-subtitle {
            font-size: 1rem;
            color: #64748B;
            margin-bottom: 1rem;
        }

        .civicpulse-header {
            padding: 0.5rem 0 1rem 0;
            margin-bottom: 1.25rem;
            border-bottom: 1px solid #E2E8F0;
        }

        .civicpulse-title {
            font-size: 1.9rem;
            font-weight: 800;
            color: #0F172A;
            margin-bottom: 0.25rem;
            line-height: 1.25;
        }

        .civicpulse-subtitle {
            font-size: 1rem;
            color: #64748B;
        }

        .cp-ai-card {
            padding: 1.25rem;
            border-radius: 12px;
            border: 1px solid #E2E8F0;
            margin: 0.75rem 0;
            background: #FFFFFF;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
        }

        .cp-similarity-box {
            padding: 0.75rem 1rem;
            border-radius: 10px;
            border: 1px solid #FDE68A;
            background: #FFFBEB;
            margin-top: 1rem;
            margin-bottom: 0.5rem;
        }

        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
            margin: 2px;
            line-height: 1.2;
            vertical-align: middle;
        }

        .priority-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 700;
            margin: 2px;
            line-height: 1.2;
            vertical-align: middle;
        }

        .metric-card {
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
            background: #FFFFFF;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# STATUS BADGE
# =========================================================

def get_status_badge_html(status: str) -> str:
    """
    Return clean HTML badge for complaint status.
    Guaranteed single-line string with no trailing newlines to prevent markdown code fence bugs.
    """
    status_str = str(status or "Unknown").strip()
    safe_status = escape(status_str)

    palette = {
        "pending": ("#FEF3C7", "#92400E", "#FDE68A"),
        "assigned": ("#EDE9FE", "#5B21B6", "#DDD6FE"),
        "in progress": ("#DBEAFE", "#1E40AF", "#BFDBFE"),
        "resolved": ("#D1FAE5", "#065F46", "#A7F3D0"),
        "closed": ("#F1F5F9", "#475569", "#CBD5E1"),
    }
    bg, fg, border = palette.get(status_str.lower(), ("#F1F5F9", "#334155", "#CBD5E1"))

    return (
        f'<span class="status-badge" style="display:inline-block;padding:3px 10px;'
        f'border-radius:12px;font-size:12px;font-weight:700;margin:2px;'
        f'background-color:{bg};color:{fg};border:1px solid {border};line-height:1.2;">'
        f'{safe_status}</span>'
    )


# =========================================================
# PRIORITY BADGE
# =========================================================

def get_priority_badge_html(priority: str) -> str:
    """
    Return clean HTML badge for complaint priority.
    Guaranteed single-line string with no trailing newlines to prevent markdown code fence bugs.
    """
    priority_str = str(priority or "Medium").strip()
    safe_priority = escape(priority_str)

    palette = {
        "critical": ("#FEE2E2", "#991B1B", "#FECACA"),
        "high": ("#FFEDD5", "#9A3412", "#FED7AA"),
        "medium": ("#FEF3C7", "#854D0E", "#FDE68A"),
        "low": ("#E0F2FE", "#075985", "#BAE6FD"),
    }
    bg, fg, border = palette.get(priority_str.lower(), ("#F1F5F9", "#334155", "#E2E8F0"))

    return (
        f'<span class="priority-badge" style="display:inline-block;padding:3px 10px;'
        f'border-radius:12px;font-size:12px;font-weight:700;margin:2px;'
        f'background-color:{bg};color:{fg};border:1px solid {border};line-height:1.2;">'
        f'{safe_priority} Priority</span>'
    )


# =========================================================
# METRIC CARD
# =========================================================

def render_metric_card(
    title: str,
    value: Any,
    *args,
    **kwargs
) -> None:
    """
    Render a standard Streamlit metric card.
    """
    delta = kwargs.get("delta", None)
    help_text = kwargs.get("help", None)

    st.metric(
        label=str(title),
        value=str(value),
        delta=delta,
        help=help_text,
    )


# =========================================================
# PAGE HEADER
# =========================================================

def render_header(
    title: str,
    subtitle: str = "",
    icon: str = "",
    *args,
    **kwargs
) -> None:
    """
    Render a CivicPulse AI page header in clean, valid HTML.
    """
    title_str = str(title or "").strip()
    sub_str = str(subtitle or "").strip()
    icon_str = str(icon or "").strip()

    display_title = f"{icon_str} {title_str}".strip() if icon_str else title_str

    subtitle_html = (
        f'<div class="civicpulse-subtitle" style="font-size:1rem;color:#64748B;margin-top:4px;">'
        f'{escape(sub_str)}</div>'
        if sub_str
        else ""
    )

    header_html = (
        f'<div class="civicpulse-header" style="padding:0.5rem 0 1rem 0;margin-bottom:1.25rem;'
        f'border-bottom:1px solid #E2E8F0;">'
        f'<div class="civicpulse-title" style="font-size:1.9rem;font-weight:800;color:#0F172A;line-height:1.2;">'
        f'{escape(display_title)}</div>'
        f'{subtitle_html}'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


# =========================================================
# TIMELINE
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
        st.info("No audit history records are available for this complaint.")
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

        # Build clear, professional English action description
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
            f'<div style="margin-top:6px;font-size:0.88rem;color:#334155;line-height:1.4;">'
            f'{safe_action}</div>'
            if safe_action
            else ""
        )

        timeline_item_html = (
            f'<div style="border-left:4px solid #2563EB;background-color:#F8FAFC;'
            f'border-top:1px solid #E2E8F0;border-right:1px solid #E2E8F0;border-bottom:1px solid #E2E8F0;'
            f'border-radius:0 8px 8px 0;padding:10px 14px;margin-bottom:10px;">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">'
            f'<div>{badge_html}</div>'
            f'<span style="font-size:0.82rem;color:#64748B;font-weight:500;">{safe_time}</span>'
            f'</div>'
            f'{action_html}'
            f'</div>'
        )
        st.markdown(timeline_item_html, unsafe_allow_html=True)


# =========================================================
# OPTIONAL COMPATIBILITY HELPERS
# =========================================================

def render_status_badge(status: str) -> None:
    """
    Directly render a status badge.
    """
    st.markdown(get_status_badge_html(status), unsafe_allow_html=True)


def render_priority_badge(priority: str) -> None:
    """
    Directly render a priority badge.
    """
    st.markdown(get_priority_badge_html(priority), unsafe_allow_html=True)


def render_section_header(
    title: str,
    description: str = "",
    icon: str = ""
) -> None:
    """
    Render a generic section header.
    """
    heading = f"{icon} {title}".strip() if icon else title
    st.subheader(heading)
    if description:
        st.caption(description)