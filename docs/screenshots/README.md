# CivicPulse AI — Screenshot Gallery Guide

This directory holds the official screenshots demonstrating the **CivicPulse AI** platform interface across student, administrative, analytics, and reporting workflows.

---

## Required Screenshot Files

To maintain visual consistency and ensure that all Markdown links render correctly in [README.md](../../README.md), capture genuine screenshots of the live application and save them with the exact filenames below:

| File Name | Page / Workflow | Description |
| :--- | :--- | :--- |
| `home.png` | **Application Home / Navigation** | Landing view showing the branded sidebar navigation (`CivicPulse AI Enterprise v2.4`), system infrastructure status indicator, and initial view. |
| `submit-complaint.png` | **Submit Complaint View** | The multi-card complaint intake form with complainant identification inputs, title, description, category selector, and department dropdown. |
| `successful-registration.png` | **AI Triage & Registration Card** | Confirmation state rendered after submission showing generated Reference ID (`CP-XXXXXXXX`), detected category/subcategory, priority badge, routing SLA, and TF-IDF similarity warnings. |
| `tracking.png` | **Status Tracker View** | Grievance tracker tab displaying the visual 5-stage progress pipeline (`Pending` → `Assigned` → `In Progress` → `Resolved` → `Closed`), audit history, and complaint details. |
| `admin-dashboard.png` | **Admin Operations View** | The administrative control center displaying live KPI summary tiles, multi-parameter search/filters, complaint data table, and the secure status update modal. |
| `analytics.png` | **Analytics & Problem Hotspots** | Plotly visualization dashboard showing department workload distribution, category pie charts, resolution timelines, and high-frequency problem hotspots. |
| `pdf-report.png` | **Reports & PDF Export Center** | Report generation center showing executive PDF download options and the printable complaint docket view. |

---

## How to Capture High-Quality Screenshots

### 1. Launch the Application Locally or Visit the Live Demo
You can capture screenshots from either the production deployment or a local environment:
- **Live Streamlit App:** [https://civicpulse-ai-bqh964obd3wqrgkvsp82kk.streamlit.app/](https://civicpulse-ai-bqh964obd3wqrgkvsp82kk.streamlit.app/)
- **Local Application:**
  ```powershell
  # Start backend
  uvicorn backend.main:app --port 8000
  # In another terminal, start frontend
  streamlit run app.py
  ```
  Open `http://localhost:8501` in your browser.

### 2. Capture Guidelines
- **Resolution:** Set browser viewport to `1920 × 1080` (1080p) or `1440 × 900` at 100% zoom for crisp typography.
- **Theme:** Use the default light mode (configured in `.streamlit/config.toml`) to ensure high contrast and readability on GitHub.
- **Cleanliness:**
  - Close browser developer tools, inspection ribbons, and extension popups before taking screenshots.
  - Collapse or hide any personal browser bookmarks bar if capturing full browser windows.
  - Seed or use realistic sample complaints (e.g. laboratory AC issues, library lighting, or hostel plumbing) rather than test strings like `"test123"`.
- **Format:** Save files in lossless **PNG** format.
- **Location:** Place saved PNG images directly into this folder:
  ```text
  docs/
  └── screenshots/
      ├── home.png
      ├── submit-complaint.png
      ├── successful-registration.png
      ├── tracking.png
      ├── admin-dashboard.png
      ├── analytics.png
      └── pdf-report.png
  ```

---

*Note: Do not commit empty files, mockups, or unrelated images. GitHub will display the image references in the root README as soon as real files are saved to this folder.*
