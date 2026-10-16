"""
Unit tests for CivicPulse AI Smart City Platform hero banner integration.
Verifies file existence in assets/ and static/, format validity, base64 resolution,
aspect ratio preservation, and accessible alt text.
"""

import os
from PIL import Image
from utils.ui_components import _get_hero_banner_base64, render_hero_banner


def test_hero_image_files_exist():
    """Verify image exists in both assets and static directories."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_img = os.path.join(project_root, "assets", "CivicPulse AI Smart City Platform.png")
    static_img = os.path.join(project_root, "static", "CivicPulse AI Smart City Platform.png")

    assert os.path.isfile(assets_img), f"Missing image in assets: {assets_img}"
    assert os.path.isfile(static_img), f"Missing image in static: {static_img}"
    assert os.path.getsize(assets_img) > 100000, "Assets image file is too small or empty"
    assert os.path.getsize(static_img) > 100000, "Static image file is too small or empty"


def test_hero_image_validity_and_dimensions():
    """Verify that the image is a valid PNG with expected dimensions."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_img = os.path.join(project_root, "assets", "CivicPulse AI Smart City Platform.png")

    with Image.open(assets_img) as img:
        assert img.format == "PNG"
        w, h = img.size
        assert w == 1672
        assert h == 941
        aspect_ratio = w / h
        assert 1.77 <= aspect_ratio <= 1.78, f"Unexpected aspect ratio: {aspect_ratio}"


def test_hero_banner_base64_resolution():
    """Verify base64 resolver returns a valid non-empty string."""
    b64 = _get_hero_banner_base64()
    assert b64 is not None
    assert isinstance(b64, str)
    assert len(b64) > 1000000


def test_render_hero_banner_execution(monkeypatch):
    """Verify render_hero_banner outputs valid HTML with required alt text."""
    rendered_markdowns = []

    def mock_markdown(body, unsafe_allow_html=False):
        rendered_markdowns.append(body)

    import streamlit as st
    monkeypatch.setattr(st, "markdown", mock_markdown)

    render_hero_banner()

    assert len(rendered_markdowns) >= 1
    html = rendered_markdowns[0]
    assert 'class="civicpulse-hero-container"' in html
    assert 'class="civicpulse-hero-frame"' in html
    assert 'class="civicpulse-hero-img"' in html
    assert 'alt="CivicPulse AI — Intelligent Grievance Platform"' in html
    assert 'role="region"' in html
    assert 'src="data:image/png;base64,' in html


def test_get_hero_banner_path_resolves_valid_file():
    """Verify get_hero_banner_path returns a valid absolute filesystem path."""
    from utils.ui_components import get_hero_banner_path
    banner_path = get_hero_banner_path()
    assert banner_path is not None
    assert os.path.isabs(banner_path)
    assert os.path.isfile(banner_path)
    assert os.path.getsize(banner_path) > 100000


def test_render_hero_banner_image_source_valid(monkeypatch):
    """Verify rendered image source decodes into genuine PNG image bytes."""
    import base64
    rendered_markdowns = []

    def mock_markdown(body, unsafe_allow_html=False):
        rendered_markdowns.append(body)

    import streamlit as st
    monkeypatch.setattr(st, "markdown", mock_markdown)

    render_hero_banner()

    html = rendered_markdowns[0]
    prefix = 'src="data:image/png;base64,'
    start_idx = html.find(prefix) + len(prefix)
    end_idx = html.find('"', start_idx)
    raw_b64 = html[start_idx:end_idx]

    img_bytes = base64.b64decode(raw_b64)
    assert img_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(img_bytes) > 1000000


def test_streamlit_static_serving_route():
    """Verify Streamlit static-file serving route correctly resolves the banner."""
    from starlette.applications import Starlette
    from starlette.testclient import TestClient
    from streamlit.web.server.starlette.starlette_routes import create_app_static_serving_routes

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_py_path = os.path.join(project_root, "app.py")
    routes = create_app_static_serving_routes(app_py_path, "")
    app = Starlette(routes=routes)
    client = TestClient(app)

    resp = client.get("/app/static/CivicPulse%20AI%20Smart%20City%20Platform.png")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "image/png"
    assert len(resp.content) > 1000000
    assert resp.content.startswith(b"\x89PNG")


def test_render_hero_banner_fallback_when_file_missing(monkeypatch):
    """Verify graceful fallback renders when banner image is genuinely missing."""
    rendered_markdowns = []

    def mock_markdown(body, unsafe_allow_html=False):
        rendered_markdowns.append(body)

    import streamlit as st
    monkeypatch.setattr(st, "markdown", mock_markdown)
    monkeypatch.setattr("utils.ui_components.get_hero_banner_path", lambda: None)
    monkeypatch.setattr("utils.ui_components._get_hero_banner_base64", lambda: None)

    render_hero_banner()

    assert len(rendered_markdowns) >= 1
    html = rendered_markdowns[0]
    assert 'class="civicpulse-hero-container"' in html
    assert 'class="civicpulse-hero-frame"' in html
    assert "CivicPulse AI — Intelligent Grievance Platform" in html

