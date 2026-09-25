"""
Views package for CivicPulse AI Streamlit pages.
"""

from .submit_view import render_submit_view
from .tracker_view import render_tracker_view
from .admin_view import render_admin_view
from .analytics_view import render_analytics_view
from .reports_view import render_reports_view

__all__ = [
    "render_submit_view",
    "render_tracker_view",
    "render_admin_view",
    "render_analytics_view",
    "render_reports_view"
]
