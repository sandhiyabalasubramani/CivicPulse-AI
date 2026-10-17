<div align="center">

# 🏛️ CivicPulse AI
### AI-Powered Institutional Grievance Management & Hotspot Analytics Platform

An enterprise-grade grievance management, automated triage, and operational intelligence platform designed for universities, corporate campuses, and large-scale institutions.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Neon](https://img.shields.io/badge/Neon-Serverless_PostgreSQL-00E599?style=for-the-badge&logo=neon&logoColor=black)](https://neon.tech/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-TF--IDF_%26_Cosine-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Interactive_Analytics-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![ReportLab](https://img.shields.io/badge/ReportLab-PDF_Generation-D12420?style=for-the-badge)](https://www.reportlab.com/)
[![Render](https://img.shields.io/badge/Render-Backend_Hosting-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://render.com/)
[![Tests](https://img.shields.io/badge/Tests-101%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](tests/)

<br/>

[🚀 Live Streamlit Application](https://civicpulse-ai-bqh964obd3wqrgkvsp82kk.streamlit.app/) • [⚡ FastAPI Backend Service](https://civicpulse-ai-api-5g8h.onrender.com) • [📖 Interactive Swagger API Docs](https://civicpulse-ai-api-5g8h.onrender.com/docs) • [💻 GitHub Repository](https://github.com/sandhiyabalasubramani/CivicPulse-AI)

</div>

---

## 📋 Project Overview

> **Project documentation:** [System Architecture](docs/ARCHITECTURE.md) · [Production Readiness Checklist](docs/PRODUCTION_READINESS.md) · [Test Suite](tests/) · [Environment Template](.env.example)


Institutional facility management across universities, colleges, and municipal offices frequently suffers from communication bottlenecks. Grievance reports submitted via disconnected spreadsheets, phone calls, or paper forms often lack categorization, miss urgency assessments, lead to duplicate maintenance dispatches, and provide zero status transparency to citizens.

**CivicPulse AI** solves this operational deficit by uniting modern full-stack web technologies with deterministic NLP intelligence. The platform automates the grievance intake lifecycle:
- Ingests institutional complaints through an accessible, mobile-responsive web portal.
- Classifies grievances into distinct categories and subcategories using an institutional domain taxonomy.
- Evaluates urgency and safety hazards to assign deterministic priority levels and binding Service Level Agreements (SLAs).
- Discovers potential duplicate filings and recurring problems using **TF-IDF vectorization and cosine similarity**.
- Automatically routes grievances to designated maintenance divisions.
- Maintains an immutable, chronological status audit log throughout the resolution lifecycle.
- Empowers executives with interactive Plotly analytics to identify systemic failure hotspots and generate downloadable PDF reports.

> **Technical Clarification on AI Capabilities:**
> CivicPulse AI employs **deterministic rule-based triage** (domain taxonomy keyword graphs and priority signal matching) combined with **scikit-learn TF-IDF vector embeddings and cosine similarity analysis** for duplicate discovery. The platform deliberately does not rely on opaque deep learning models or generative AI hallucinations, ensuring that institutional priority assignments and department routings remain 100% explainable, deterministic, and auditable.

---

## 🌐 Live Demo

The platform is deployed and fully accessible online:

| Component | Endpoint Link | Deployment Environment |
| :--- | :--- | :--- |
| **Streamlit Web Application** | [civicpulse-ai.streamlit.app](https://civicpulse-ai-bqh964obd3wqrgkvsp82kk.streamlit.app/) | Streamlit Community Cloud |
| **FastAPI Backend Server** | [civicpulse-ai-api-5g8h.onrender.com](https://civicpulse-ai-api-5g8h.onrender.com) | Render Web Service |
| **Interactive API Documentation** | [civicpulse-ai-api-5g8h.onrender.com/docs](https://civicpulse-ai-api-5g8h.onrender.com/docs) | Swagger UI / OpenAPI 3.0 |
| **Source Code Repository** | [github.com/sandhiyabalasubramani/CivicPulse-AI](https://github.com/sandhiyabalasubramani/CivicPulse-AI) | GitHub |

> ⏳ **Note on Cloud Service Wake-Up:**
> The FastAPI backend service is hosted on Render's free tier. If the service has been inactive, the server automatically spins down to conserve resources and may require 30 to 60 seconds to wake up upon receiving the first web request.

---

## ✨ Key Features

Each core capability in CivicPulse AI is implemented and verified against the repository codebase:

1. **Institutional Complaint Submission:** Provides a structured multi-section web form for logging facility grievances with client-side and server-side validation.
2. **Complainant Identification & Complaint Details:** Collects verified complainant contact details, location contexts, descriptive titles, and detailed incident explanations.
3. **Category & Subcategory Classification:** Automatically categorizes grievances across 7 institutional domains (Electrical, Water & Plumbing, Network & IT, Cleaning & Sanitation, Infrastructure & Civil, Equipment & Machinery, Other) using taxonomy keyword matching.
4. **Priority Assessment & SLA Assignment:** Computes deterministic severity tiers (Critical, High, Medium, Low) with explicit explainability signals and assigns target resolution deadlines.
5. **Department Routing:** Automatically allocates complaints to the appropriate division (e.g. Substation Operations, HVAC Unit, Desktop Hardware Cell) based on subcategory rules.
6. **TF-IDF & Cosine Similarity Detection:** Vectorizes incoming complaint text using scikit-learn and calculates cosine similarity against historical records to flag potential duplicates.
7. **Complaint Reference ID Generation:** Issues a unique, non-sequential reference identifier formatted as `CP-XXXXXXXX` for every submitted ticket.
8. **Complaint Tracking:** Enables citizens to look up live status timelines, metadata cards, and audit histories using either their Reference ID or registered email address.
9. **Admin Dashboard & Complaint Search:** Provides campus administrators with real-time KPI tiles, multi-parameter filtering, full-text keyword searches, and a tabular grievance management grid.
10. **Status Updates & Audit History:** Facilitates administrative state transitions (`Pending` → `Assigned` → `In Progress` → `Resolved` → `Closed`) while writing timestamped audit entries to the database.
11. **Analytics, Charts & Complaint Hotspots:** Renders interactive Plotly visual charts breaking down category distributions, department workloads, average resolution hours, and high-frequency problem hotspots.
12. **PDF Complaint Docket & Report Generation:** Compiles and exports printable, publication-grade individual resolution dockets and institutional executive summary briefing PDFs using ReportLab.
13. **PostgreSQL Database Persistence:** Stores all complaint metadata, foreign keys, timestamps, and status transition logs in a hosted PostgreSQL database with connection pooling.
14. **FastAPI Backend & Health-Check Endpoint:** Exposes a high-performance RESTful API with automated schema initialization, constant-time administrative authentication, and detailed `/health` diagnostics.

---

## 📸 Visual Overview and Interface Gallery

CivicPulse AI features a clean, responsive interface powered by modern glassmorphic styling, real-time KPI metrics, Plotly analytics, and ReportLab document export.

<div align="center">

![CivicPulse AI Smart City Platform](assets/CivicPulse%20AI%20Smart%20City%20Platform.png)

*CivicPulse AI — Intelligent Grievance Management & Hotspot Analytics Platform Overview*

</div>

### Verified Platform Views & Capabilities
| View / Module | Primary Capabilities & Workflow |
| :--- | :--- |
| **📝 Submit Complaint** | Multi-card intake form with complainant details, location, description, auto-categorization, priority scoring, and department routing. |
| **🔍 Track Complaint** | Visual 5-stage status progress pipeline (`Pending` → `Assigned` → `In Progress` → `Resolved` → `Closed`), incident metadata card, audit history, and PDF docket export. |
| **🛡️ Admin Operations** | Administrative control center with live KPI summary tiles, multi-parameter search/filters, tabular complaint grid, and secure status transitions. |
| **📊 Analytics & Hotspots** | Plotly telemetry dashboard displaying category distribution, department workload allocation, resolution timelines, and recurring hotspot analytics. |
| **📑 Reports & PDF Export** | Document export center generating printable individual complaint dockets (`.pdf`), executive briefing summaries (`.pdf`), and raw CSV records. |

> 📷 **Screenshot Capture Guidelines:**
> For instructions on capturing and contributing UI screenshots from the live deployment or local environment, refer to [`docs/screenshots/README.md`](docs/screenshots/README.md).

---

## 🏗️ System Architecture Diagram

CivicPulse AI adopts a decoupled multi-tier architecture. The Streamlit frontend interacts with the FastAPI backend over secure HTTP REST protocols, while the backend mediates all database persistence, automated AI triage, and status auditing.

```mermaid
flowchart TD
    subgraph UI["🖥️ Streamlit Frontend UI"]
        direction TB
        V_Submit["📝 Grievance Submission Portal<br/><code>views/submit_view.py</code>"]
        V_Track["🔍 Live Complaint Tracker<br/><code>views/tracker_view.py</code>"]
        V_Admin["🛡️ Admin Operations Control Center<br/><code>views/admin_view.py</code>"]
        V_Analytics["📊 Analytics & Hotspots Dashboard<br/><code>views/analytics_view.py</code>"]
        V_Reports["📑 Governance Reports View<br/><code>views/reports_view.py</code>"]
        API_Client["Unified API Client<br/><code>utils/api_client.py</code>"]

        V_Submit --> API_Client
        V_Track --> API_Client
        V_Admin --> API_Client
        V_Analytics --> API_Client
        V_Reports --> API_Client
    end

    subgraph Exports["📤 PDF Reports & CSV Export"]
        direction TB
        PDF_Docket["📄 Single Complaint Docket PDF<br/>(ReportLab Vector Document)"]
        PDF_Summary["📊 Executive Summary Analytics PDF<br/>(ReportLab Governance Briefing)"]
        CSV_Export["📥 Tabular Grievance Records<br/>(Raw CSV Data Export)"]
    end

    subgraph API["⚡ FastAPI REST Backend Server"]
        direction TB
        FastAPI_App["FastAPI Application Server<br/><code>backend/main.py</code><br/>(/complaints, /health, /docs)"]
        Admin_Auth["Admin Auth Guard<br/>Constant-Time HMAC (X-Admin-Key)"]
        FastAPI_App --- Admin_Auth
    end

    subgraph AI["🤖 AI Triage & Analytics Pipeline"]
        direction TB
        AI_Triage["1. AI Triage & Classification<br/><code>modules/complaint_analyzer.py</code><br/>(Domain Taxonomy Matching)"]
        Priority_Eng["2. Explainable Priority Engine<br/><code>modules/priority_engine.py</code><br/>(Urgency & Safety Hazard Scoring)"]
        Dept_Router["3. Department Router<br/><code>modules/department_router.py</code><br/>(Division Allocation & Target SLA)"]
        Duplicate_Detect["4. Duplicate Detection Engine<br/><code>modules/similarity_engine.py</code><br/>(TF-IDF & Cosine Similarity)"]

        AI_Triage --> Priority_Eng
        Priority_Eng --> Dept_Router
        Dept_Router --> Duplicate_Detect
    end

    subgraph DB["🗄️ PostgreSQL Persistence Tier"]
        direction TB
        DB_Pool["Connection Pool (psycopg3)<br/><code>backend/database.py</code>"]
        T_Complaints[("Table: complaints<br/>(Grievances, Priority, SLAs, Meta)")]
        T_History[("Table: status_history<br/>(Immutable Chronological Audit Log)")]
        DB_Pool --> T_Complaints
        DB_Pool --> T_History
    end

    %% Main End-to-End Pipeline
    API_Client -- "HTTP REST (JSON Payloads)" --> FastAPI_App
    FastAPI_App -- "Intake & Triage" --> AI_Triage
    Duplicate_Detect -- "Persist Ticket & Similarity" --> DB_Pool
    FastAPI_App -- "Queries & Status Updates" --> DB_Pool

    %% Export Generation
    V_Track -. "Generate Docket" .-> PDF_Docket
    V_Reports -. "Generate Executive Briefing" .-> PDF_Summary
    V_Reports -. "Download Filtered Dataset" .-> CSV_Export
```

> 📄 For in-depth technical specifications, component descriptions, and query lifecycles, refer to [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## 🔄 Complaint Processing Workflow

The diagram below details the sequence of operations executed from the moment a user files a complaint through resolution and final archiving:

```mermaid
flowchart TD
    Start(["User Submits Complaint Form"]) --> ValCheck{"Input Validation<br/>Email and Fields Valid?"}

    ValCheck -- No --> ShowErr["Display Form Validation Error"]
    ValCheck -- Yes --> CallAPI["POST /complaints Payload to FastAPI"]

    CallAPI --> TriageNode["1. Complaint Analyzer<br/>Taxonomy Keyword and Subcategory Matching"]
    TriageNode --> PrioNode["2. Priority Engine<br/>Scan Hazard Signals to Assign Score and SLA"]
    PrioNode --> RouteNode["3. Department Router<br/>Determine Maintenance Division and Support Contact"]

    RouteNode --> FetchHistory["Fetch Existing Complaint Corpus from DB"]
    FetchHistory --> SimNode["4. Similarity Engine<br/>TF-IDF Vectorization and Cosine Similarity Evaluation"]

    SimNode --> IDGen["Generate Unique Reference ID: CP-XXXXXXXX"]
    IDGen --> DBInsert["Insert Record into PostgreSQL 'complaints'<br/>Insert Initial Entry into 'status_history'"]

    DBInsert --> Resp201["Return HTTP 201 Success Response"]
    Resp201 --> ShowConfirm["Display Interactive AI Triage Card to Citizen"]

    ShowConfirm --> CitizenTrack["Citizen Tracks Ticket via Reference ID or Email"]
    ShowConfirm --> AdminReview["Admin Inspects Grievance in Control Center"]

    AdminReview --> StatusUpdate{"Admin Updates Status<br/>Pending to Assigned to In Progress to Resolved"}
    StatusUpdate --> PutReq["PUT /complaints/:id/status<br/>Validated via Secret Admin Key"]
    PutReq --> LogHistory["Update 'complaints' Table<br/>Append Entry to 'status_history'"]

    LogHistory --> AnalyticsSink["Plotly Hotspot Analytics Updated"]
    LogHistory --> PDFExport["Generate Official PDF Docket and Executive Summary"]

    classDef step fill:#FFFFFF,stroke:#0284C7,stroke-width:2px;
    classDef decision fill:#FEF3C7,stroke:#D97706,stroke-width:2px;
    classDef err fill:#FEE2E2,stroke:#DC2626,stroke-width:2px;

    class Start,CallAPI,TriageNode,PrioNode,RouteNode,FetchHistory,SimNode,IDGen,DBInsert,Resp201,ShowConfirm,CitizenTrack,AdminReview,PutReq,LogHistory,AnalyticsSink,PDFExport step;
    class ValCheck,StatusUpdate decision;
    class ShowErr err;
```

---

## 🛠️ Technology Stack

All dependencies and frameworks used in CivicPulse AI have been verified against `requirements.txt` and the codebase:

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | Streamlit (`>=1.35.0`) | Rapid development of interactive, stateful web interfaces and multi-view navigation. |
| **Backend REST API** | FastAPI (`>=0.110.0`) | High-performance asynchronous REST API framework with automatic OpenAPI documentation. |
| **ASGI Server** | Uvicorn (`>=0.29.0`) | Lightning-fast ASGI web server implementation for running FastAPI in production. |
| **Primary Database** | PostgreSQL 16 | ACID-compliant relational persistence for grievances, foreign key relationships, and audit trails. |
| **Database Cloud Host** | Neon | Serverless PostgreSQL cloud hosting featuring autoscaling and branchable databases. |
| **Database Driver & Pool** | `psycopg` & `psycopg_pool` (`>=3.1.0`) | Native Python PostgreSQL driver offering binary parameter serialization and thread-safe connection pooling. |
| **Data Processing** | Pandas (`>=2.2.0`) & NumPy (`>=1.26.0`) | Tabular data manipulation, aggregation, and vectorized numerical transformations. |
| **NLP & Vector Similarity** | Scikit-Learn (`>=1.4.0`) | TF-IDF text vectorization (`TfidfVectorizer`) and pairwise cosine similarity calculation (`cosine_similarity`). |
| **Data Visualization** | Plotly (`>=5.20.0`) | Dynamic, interactive charts for departmental distribution, category share, and problem hotspot intelligence. |
| **Document Generation** | ReportLab (`>=4.1.0`) | Programmatic generation of vector-quality printable PDF complaint dockets and executive briefings. |
| **Validation & Schemas** | Pydantic (`>=2.0`) & Email-Validator | Strict runtime request parsing, data normalization, and email format validation. |
| **HTTP Client** | Requests (`>=2.31.0`) & HTTPX (`>=0.27.0`) | Resilient client-side HTTP communication, timeout handling, and test client requests. |
| **Automated Testing** | Pytest (`>=8.0.0`) | Comprehensive unit, security, and integration test execution framework. |
| **Version Control** | Git & GitHub | Distributed version control, codebase tracking, and collaborative portfolio hosting. |
| **Frontend Cloud Host** | Streamlit Community Cloud | Continuous deployment hosting platform for the Streamlit web application. |
| **Backend Cloud Host** | Render | Managed cloud hosting platform for the FastAPI backend service. |

---

## 📁 Repository Structure

The following tree represents the verified file and directory organization of the CivicPulse AI repository:

```text
CivicPulse-AI/
├── .streamlit/
│   └── config.toml               # Streamlit theme customization and server configurations
├── backend/
│   ├── database.py               # PostgreSQL connection pooling, SSL enforcement, and schema init
│   └── main.py                   # FastAPI REST API routes, models, authentication, and error handling
├── database/
│   ├── database.py               # SQLite database manager for local/offline testing
│   ├── init_db.py                # Database initialization script
│   ├── migrate_sqlite_to_postgres.py # Data migration utility from SQLite to PostgreSQL
│   ├── postgres_schema.sql       # Production PostgreSQL DDL table definitions and B-tree indexes
│   └── schema.py                 # SQL schema definitions for SQLite
├── data/
│   └── sample_data.py            # Representative institutional grievance seeds for testing
├── docs/
│   ├── ARCHITECTURE.md           # Deep-dive architecture specifications and technical workflows
│   └── screenshots/
│       └── README.md             # Capture guide and filename reference for application screenshots
├── modules/
│   ├── complaint_analyzer.py     # Rule-based category and subcategory taxonomy classifier
│   ├── department_router.py      # Division routing logic and target SLA calculation
│   ├── priority_engine.py        # Deterministic urgency scorer with explainable diagnostic signals
│   ├── report_generator.py       # ReportLab PDF docket and executive briefing generator
│   ├── similarity_engine.py      # Scikit-learn TF-IDF vectorization and cosine similarity matcher
│   └── text_processing.py        # String sanitization, keyword extraction, and tokenization utilities
├── tests/
│   ├── test_admin_status_update.py # Status transition validation and edge cases
│   ├── test_analyzer.py          # Category taxonomy classification tests
│   ├── test_api_security.py      # Authentication, timing protection, and fail-closed security tests
│   ├── test_database.py          # Database queries and index tests
│   ├── test_database_init_and_cloud.py # Cloud connection pooling and auto-recovery tests
│   ├── test_docket_pdf.py        # ReportLab single docket PDF generation tests
│   ├── test_e2e_integration.py   # End-to-end complaint submission and tracking tests
│   ├── test_priority.py          # Priority engine hazard detection tests
│   ├── test_similarity.py        # TF-IDF similarity calculation and threshold tests
│   └── test_summary_pdf.py       # Executive summary PDF report generation tests
├── utils/
│   ├── api_client.py             # Unified API client mediating Streamlit-FastAPI communication
│   ├── ui_components.py          # Custom CSS design system, metric cards, steppers, and badges
│   └── validators.py             # Form validation utilities for complaint submission
├── .env.example                  # Safe configuration template containing placeholder variable names
├── .gitignore                    # Git ignore file excluding virtual environments, caches, and secrets
├── app.py                        # Streamlit application entry point and sidebar controller
├── requirements.txt              # Production dependency specifications
└── README.md                     # Comprehensive project documentation
```

---

## 💻 Installation and Local Setup

Follow these step-by-step instructions to set up and run CivicPulse AI locally on **Windows PowerShell**.

### 1. Prerequisites
- **Python:** Version `3.10` or higher installed ([Download Python](https://www.python.org/downloads/)).
- **Git:** Installed and configured ([Download Git](https://git-scm.com/)).
- **PostgreSQL Database:** Either a local PostgreSQL instance or a free cloud database from [Neon](https://neon.tech/).

### 2. Clone the Repository
Open Windows PowerShell and clone the project:
```powershell
git clone https://github.com/sandhiyabalasubramani/CivicPulse-AI.git
cd CivicPulse-AI
```

### 3. Create and Activate a Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment in PowerShell
.\venv\Scripts\Activate.ps1
```
> *If you encounter a PowerShell script execution error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` and re-run the activation script.*

### 4. Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy the template configuration file to `.env`:
```powershell
Copy-Item .env.example .env
```
Open `.env` in any text editor and supply your PostgreSQL connection string and a secret administrative key:
```ini
# PostgreSQL Connection URL (e.g. from Neon or local Postgres)
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/civicpulse

# Secret Administrator Key for Protected Operations
ADMIN_API_KEY=your_secure_random_admin_api_key_here

# FastAPI Backend URL used by Streamlit client
API_URL=http://127.0.0.1:8000
```
*(Never commit `.env` containing real credentials to version control).*

> 💡 **Port Consistency:** Port `8000` is the standard local development port configured identically across `.env.example`, `utils/api_client.py`, and `README.md`. If port `8000` is already in use by another service on your machine, you can run Uvicorn on an alternate port (e.g. `--port 8001`) and update `API_URL=http://127.0.0.1:8001` in your `.env` file accordingly.

### 6. Start the FastAPI Backend (Terminal 1)
In your first PowerShell terminal, run:
```powershell
uvicorn backend.main:app --reload --port 8000
```
- The backend will automatically verify and initialize database tables (`complaints` and `status_history`).
- Access the FastAPI root: `http://127.0.0.1:8000`
- Access Backend Health Probe: `http://127.0.0.1:8000/health`
- Access Interactive Swagger API Docs: `http://127.0.0.1:8000/docs`

### 7. Start the Streamlit Frontend (Terminal 2)
Open a **second PowerShell terminal**, navigate to the project directory, activate the virtual environment, and launch the frontend:
```powershell
cd "C:\Users\sandhiya B\OneDrive\Desktop\CivicPulse-AI"
.\venv\Scripts\Activate.ps1
streamlit run app.py
```
- Streamlit will open the application automatically at `http://localhost:8501`.

---

## 📡 API Documentation

The FastAPI backend exposes RESTful endpoints supporting JSON serialization, automatic schema generation, and constant-time authentication.

Interactive Swagger documentation is available at `http://127.0.0.1:8000/docs` or the live cloud endpoint:
🔗 **[https://civicpulse-ai-api-5g8h.onrender.com/docs](https://civicpulse-ai-api-5g8h.onrender.com/docs)**

### Key Implemented Endpoints

| Method | Endpoint Path | Description | Required Inputs |
| :---: | :--- | :--- | :--- |
| `GET` | `/health` | Diagnostic probe reporting API operational status, database connectivity, and record counts. | None |
| `POST` | `/complaints` | Ingests a new complaint, runs AI categorization, priority evaluation, department routing, TF-IDF similarity, and stores the ticket in PostgreSQL. | **Body (JSON):** `name`, `email`, `location`, `title`, `description`, `category` *(opt)*, `department` *(opt)* |
| `GET` | `/complaints` | Fetches filtered complaints for admin management, analytics, and reports. Supports pagination. | **Query Params:** `category`, `priority`, `status`, `location`, `department`, `email`, `search_query`, `limit`, `offset` |
| `GET` | `/complaints/{complaint_id}` | Retrieves full record details and chronological status history for a specific reference ID. | **Path Param:** `complaint_id` (e.g. `CP-XXXXXXXX`) |
| `PUT` | `/complaints/{complaint_id}/status` | **Admin Protected:** Updates complaint status, priority, notes, and records an immutable audit log entry. | **Headers:** `X-Admin-Key` or `Authorization: Bearer <key>`<br/>**Body (JSON):** `new_status`, `changed_by`, `comment`, `admin_notes` |
| `GET` | `/complaints/by-email/{email}` | Searches and returns all complaint records associated with a citizen's email address. | **Path Param:** `email` |
| `GET` | `/complaints/kpis` | Returns aggregated metrics (total, pending, in progress, resolved, high priority, resolution rate, average resolution hours). | None |
| `GET` | `/complaints/distinct/{column}` | Returns unique non-empty values for filtering dropdowns (`category`, `priority`, `status`, `location`, `department`). | **Path Param:** `column` |
| `GET` | `/status-history` | Retrieves complete chronological status change audit entries across all complaints. | **Query Params:** `limit` *(default: 5000)* |
| `POST` | `/analyze` | Dry-run endpoint that evaluates category, priority, and department routing without persisting to the database. | **Body (JSON):** `title`, `description`, `category` *(opt)*, `department` *(opt)* |
| `GET` | `/complaints/count` | Returns total complaint and status history record counts with self-healing schema creation. | None |

---

## 🗄️ Database Overview

CivicPulse AI utilizes a normalized PostgreSQL relational database schema.

### 1. `complaints` Table
Stores primary incident records, complainant identification, triage attributes, and resolution timestamps:
- `id`: Auto-incrementing integer primary key (`SERIAL PRIMARY KEY`).
- `complaint_id`: Unique institutional reference string (e.g. `CP-3C418E94`). Indexed for $O(1)$ lookups.
- `name`, `email`, `location`: Complainant contact and physical campus location coordinates.
- `title`, `description`: Grievance subject and full problem description.
- `category`, `subcategory`: Classified issue domain.
- `priority`, `priority_reason`: Severity level (`Critical`, `High`, `Medium`, `Low`) and diagnostic explanation.
- `department`: Allocated maintenance division.
- `status`: Current lifecycle phase (`Pending`, `Assigned`, `In Progress`, `Resolved`, `Closed`).
- `admin_notes`: Optional administrative remarks.
- `similar_count`, `top_similar_id`, `top_similarity_score`: TF-IDF vector similarity metrics.
- `created_at`, `updated_at`, `resolved_at`: ISO-8601 timestamps tracking resolution durations.

### 2. `status_history` Table
Provides an audit log tracking state transitions:
- `id`: Auto-incrementing primary key.
- `complaint_id`: Foreign ticket reference string. Indexed for efficient history retrieval.
- `old_status`, `new_status`: Pre- and post-transition state values.
- `changed_by`: Responsible actor (e.g. `"System"`, `"Admin"`, or officer name).
- `comment`: Reason or operational remarks accompanying the state change.
- `changed_at`: Timestamp recording the exact moment of transition.

---

## 🔒 Security

CivicPulse AI implements defense-in-depth security practices:

### Implemented Security Measures
- **Environment Separation:** All database credentials, URLs, and administrator keys are loaded strictly from environment variables or deployment secrets (`.env` is excluded in `.gitignore`).
- **Fail-Closed Administrative Authentication:** Endpoints modifying grievance states require authentication via `X-Admin-Key` or `Bearer` tokens. If `ADMIN_API_KEY` is unconfigured, the backend safely defaults to rejecting requests with HTTP 500 rather than opening access.
- **Constant-Time Verification:** Administrative key strings are evaluated using Python's `hmac.compare_digest` to prevent timing analysis attacks.
- **SQL Injection Immunization:** All database operations utilize parameterized queries with native `%s` placeholders via `psycopg3`. No dynamic string interpolation is performed.
- **Pydantic Data Validation:** Incoming payloads are parsed through strict Pydantic v2 schemas, trimming whitespace, lowercasing emails, and enforcing status whitelists.
- **Exception Sanitization:** Global exception handlers catch unexpected runtime errors and return generic error responses, preventing database internal connection strings or stack traces from reaching clients.
- **Encrypted Transport:** Cloud PostgreSQL connections enforce `sslmode=require`, ensuring end-to-end encrypted database traffic.

### Recommended Future Enhancements
- Implementation of JSON Web Tokens (JWT) or OAuth2 with institutional Single Sign-On (SSO).
- Granular Role-Based Access Control (RBAC) separating field technicians, supervisors, and executive viewers.
- Automated API rate-limiting via Redis to mitigate denial-of-service abuse.

---

## 🧪 Testing and Validation

The repository contains an automated test suite implemented in `pytest`. All **101 tests** have been executed and verified in the local environment:

```powershell
pytest
```

### Verified Test Results
```text
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\sandhiya B\OneDrive\Desktop\CivicPulse-AI
collected 101 items

tests/test_admin_status_update.py ............................           [ 27%]
tests/test_analyzer.py ......                                            [ 33%]
tests/test_api_security.py ....................                          [ 53%]
tests/test_database.py ...                                               [ 56%]
tests/test_database_init_and_cloud.py ................                   [ 72%]
tests/test_docket_pdf.py .......                                         [ 79%]
tests/test_e2e_integration.py .                                          [ 80%]
tests/test_hero_banner.py ........                                       [ 88%]
tests/test_priority.py ....                                              [ 92%]
tests/test_similarity.py ..                                              [ 94%]
tests/test_summary_pdf.py ......                                         [100%]

======================= 101 passed, 1 warning in 8.51s ========================
```

### Test Coverage Highlights
- **`test_api_security.py` (20 tests):** Verifies timing-attack resistant key comparison, missing key rejection, malformed headers, and fail-closed behaviors.
- **`test_admin_status_update.py` (28 tests):** Validates status transitions, invalid status handling, timestamp recording, audit trail inserts, case-insensitivity, whitespace trimming, and view rendering.
- **`test_analyzer.py` & `test_priority.py` (10 tests):** Tests keyword taxonomy classification accuracy, hazard signal detection, and priority scoring.
- **`test_similarity.py` (2 tests):** Verifies TF-IDF cosine similarity calculations, threshold triggers, and empty corpus handling.
- **`test_docket_pdf.py` & `test_summary_pdf.py` (13 tests):** Validates ReportLab PDF stream generation, layout bounds, and table flowables.
- **`test_database_init_and_cloud.py` & `test_database.py` (19 tests):** Confirms schema idempotency, connection recovery, and index creation.
- **`test_hero_banner.py` (8 tests):** Confirms platform image asset existence, format validity, dimension ratio, base64 data encoding, absolute filesystem path resolution, image source decoding, Starlette static file route resolution, and graceful missing-file fallback.
- **`test_e2e_integration.py` (1 test):** Exercises the complete intake, analysis, persistence, and retrieval round-trip.

---

## 🚀 Limitations and Future Enhancements

The following roadmap items represent architectural improvements planned for future releases:

1. **Automated Notification Dispatch (Email / SMS / WhatsApp):** Integrate Twilio or SendGrid APIs to dispatch instant status notifications when a ticket advances through stages.
2. **Granular Role-Based Access Control (RBAC):** Introduce distinct role profiles (Complainant, Maintenance Technician, Department Head, Super Admin) with scoped permissions.
3. **Automated SLA Escalation Engine:** Implement automated cron jobs that flag unresolved grievances approaching SLA breaches and trigger supervisor alerts.
4. **Interactive Campus GIS Mapping:** Integrate Leaflet/Folium geospatial maps to visualize problem hotspots geographically across campus facility blueprints.
5. **Multi-Lingual NLP & Image OCR:** Support regional language input translation and optical character recognition (OCR) for attached maintenance photographs.
6. **Continuous Integration & Deployment (CI/CD):** Add GitHub Actions workflows to automatically run the 101-test validation suite on every pull request.

---

## 👩‍💻 Author

**Sandhiya B**
*B.E. Electrical and Electronics Engineering Student*
GitHub: [@sandhiyabalasubramani](https://github.com/sandhiyabalasubramani)

---

<div align="center">

*CivicPulse AI was engineered to demonstrate modern full-stack system design, deterministic natural language processing, relational data modeling, and enterprise documentation standards.*

⭐ **If you find this project informative or useful, please consider giving it a star on GitHub!**

</div>
