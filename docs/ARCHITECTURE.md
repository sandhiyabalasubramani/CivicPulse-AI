# CivicPulse AI — System Architecture & Technical Specifications

This document outlines the software architecture, component relationships, data flow pipelines, and technical design decisions powering **CivicPulse AI — AI-Powered Institutional Grievance Management and Hotspot Analytics Platform**.

---

## 1. High-Level System Architecture

CivicPulse AI is structured as a decoupled multi-tier web application consisting of a modern **Streamlit frontend client**, an asynchronous **FastAPI REST backend**, an intelligent **deterministic NLP and vector similarity pipeline**, a managed **PostgreSQL database (Neon)**, and on-demand **ReportLab PDF generation and CSV export engines**.

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

---

## 2. Component Breakdown

### 2.1. Presentation Tier (Streamlit Frontend)
- **Role:** Delivers an intuitive, responsive user interface accessible across desktop and mobile devices.
- **Key Modules:**
  - `app.py`: Application entry point; initializes configuration, custom typography, session state, and the branded sidebar navigation.
  - `views/submit_view.py`: Multi-section intake form for lodging complaints, validating inputs, and presenting real-time AI triage summaries.
  - `views/tracker_view.py`: Reference ID and email search view with an interactive 5-stage status stepper, status audit history, and on-demand PDF docket export.
  - `views/admin_view.py`: Operations center for administrative triage, multi-column search, filtering, and secure status transitions.
  - `views/analytics_view.py`: Interactive visualization dashboard featuring Plotly charts for department workloads, SLA adherence, and hotspot detection.
  - `views/reports_view.py`: Official governance briefing and executive summary generation module with direct PDF and CSV downloads.
  - `utils/ui_components.py`: Centralized design system with reusable cards, badges, metric tiles, and timeline widgets.
  - `utils/api_client.py`: Resilient HTTP wrapper mediating all communication between frontend views and the FastAPI backend.

### 2.2. Service Tier (FastAPI REST Backend)
- **Role:** Encapsulates business logic, complaint analysis, authentication enforcement, database queries, and status auditing.
- **Key Characteristics:**
  - Built with FastAPI (`backend/main.py`) running via Uvicorn.
  - Comprehensive Pydantic request models (`ComplaintRequest`, `StatusUpdateRequest`) for runtime data validation and email normalization.
  - Administrative endpoints protected by constant-time secret comparison (`X-Admin-Key` / `Bearer` tokens).
  - Production-ready error masking preventing stack traces and sensitive connection parameters from exposing to clients.
  - Health probe endpoint (`/health`) that reports database connectivity, table initialization status, and record counts.

### 2.3. Analytics & NLP Intelligence Tier
- **Rule-Based Complaint Analyzer (`modules/complaint_analyzer.py`):**
  - Uses an institutional taxonomy knowledge graph to classify complaints across 7 key sectors: *Electrical, Water & Plumbing, Network & IT, Cleaning & Sanitation, Infrastructure & Civil, Equipment & Machinery, and General Administration*.
  - Matches multi-word phrase patterns and subcategories to achieve accurate categorization without training overhead.
- **Explainable Priority Engine (`modules/priority_engine.py`):**
  - Scans complaint text for hazard signals across four discrete tiers: `Critical` (e.g. fire hazard, gas leak, electric shock), `High` (e.g. lab blackout, exam session disruption, main pipe burst), `Medium` (default operational issues), and `Low` (cosmetic or minor requests).
  - Returns numerical severity scores alongside human-readable rationale (e.g. *"Immediate Fire / Chemical Safety Hazard"*).
- **Intelligent Department Router (`modules/department_router.py`):**
  - Maps detected categories and subcategories to specific institutional maintenance divisions.
  - Calculates binding Target Service Level Agreements (SLAs) ranging from 4 hours (Security & Emergency) to 48 hours (Civil & Structural).
- **TF-IDF & Cosine Similarity Engine (`modules/similarity_engine.py`):**
  - Implements Scikit-learn's `TfidfVectorizer` to convert cleaned complaint texts into unigram/bigram numerical vector spaces.
  - Computes pairwise cosine similarity against all historical complaints.
  - Flags potential duplicate filings and groups recurring problems that share an operational threshold (default: $\ge 0.35$).

### 2.4. Document Generation Engine (ReportLab)
- **Role:** Generates publication-grade, vector-crisp PDF documents directly from structured data.
- **Key Modules (`modules/report_generator.py`):**
  - `create_complaint_docket_pdf`: Compiles a formal institutional resolution docket for individual complaints, including complete metadata, priority reasons, SLA deadlines, and the chronological audit history.
  - `create_summary_analytics_pdf`: Compiles a comprehensive institutional briefing summarizing total filings, resolution efficiency, department workload breakdown, and identified operational hotspots.

### 2.5. Persistence Tier (PostgreSQL Database)
- **Database Engine:** PostgreSQL (hosted on Neon Serverless PostgreSQL with SSL enforcement).
- **Driver:** `psycopg` (Version 3) using binary pooling (`psycopg_pool`) for high-concurrency connection reuse.
- **Fallback Architecture:** Includes SQLite compatibility modules (`database/database.py`, `database/schema.py`) to support offline local testing.

---

## 3. End-to-End Complaint Processing Workflow

The diagram below details the operational lifecycle of a grievance from initial intake through resolution and executive reporting:

```mermaid
sequenceDiagram
    autonumber
    actor Complainant as Student / Complainant
    participant Streamlit as Streamlit Frontend
    participant API as FastAPI Backend
    participant NLP as Intelligence Engines
    participant DB as PostgreSQL Database
    actor Admin as Institution Administrator
    participant ReportLab as ReportLab PDF Engine

    %% 1. Submission
    Complainant->>Streamlit: Enters complaint details (title, description, location)
    Streamlit->>Streamlit: Validates inputs (name, email format, minimum length)
    Streamlit->>API: POST /complaints (JSON payload)

    %% 2. Processing
    API->>NLP: Analyze text (ComplaintAnalyzer)
    NLP-->>API: Returns detected Category & Subcategory
    API->>NLP: Evaluate severity (PriorityEngine)
    NLP-->>API: Returns Priority (Critical/High/Med/Low) + Explainable Reason
    API->>NLP: Route division (DepartmentRouter)
    NLP-->>API: Returns Division Allocation & Target SLA
    API->>DB: Fetch historical complaints for comparison
    DB-->>API: Historical records
    API->>NLP: Calculate TF-IDF & Cosine Similarity (SimilarityEngine)
    NLP-->>API: Returns Top Similar Matches & Similarity Score

    %% 3. Persistence
    API->>DB: INSERT into complaints (assigned CP-XXXXXXXX ID)
    API->>DB: INSERT into status_history (status: Pending, author: System)
    API-->>Streamlit: HTTP 201 Created (Reference ID, Analysis, Routing)
    Streamlit-->>Complainant: Displays AI Triage Card & Reference ID

    %% 4. Administrative Triage
    Admin->>Streamlit: Opens Admin Operations Dashboard
    Streamlit->>API: GET /complaints (filtered query)
    API->>DB: SELECT from complaints
    DB-->>API: Records
    API-->>Streamlit: Complaints DataFrame
    Admin->>Streamlit: Updates status to "In Progress" with notes
    Streamlit->>API: PUT /complaints/{id}/status (Header: X-Admin-Key)
    API->>API: Verify Admin Key (Constant-time comparison)
    API->>DB: UPDATE complaints & INSERT into status_history
    DB-->>API: Commit OK
    API-->>Streamlit: Update confirmed

    %% 5. Docket & Report Generation
    Complainant->>Streamlit: Requests Complaint Docket PDF
    Streamlit->>ReportLab: create_complaint_docket_pdf(complaint, history)
    ReportLab-->>Streamlit: Binary PDF stream
    Streamlit-->>Complainant: Downloads official PDF docket
```

---

## 4. Database Schema Design

The relational database architecture is defined in `database/postgres_schema.sql` and consists of two optimized tables connected logically via `complaint_id`:

```mermaid
erDiagram
    COMPLAINTS ||--o{ STATUS_HISTORY : "tracks status changes"

    COMPLAINTS {
        SERIAL id PK
        TEXT complaint_id UK "Unique reference format: CP-XXXXXXXX"
        TEXT name "Complainant full name"
        TEXT email "Contact email address"
        TEXT location "Campus facility or room number"
        TEXT title "Brief title of complaint"
        TEXT description "Detailed grievance explanation"
        TEXT category "Detected or chosen primary category"
        TEXT subcategory "Detailed sub-classification"
        TEXT priority "Critical, High, Medium, or Low"
        TEXT priority_reason "Explainable diagnostic signal"
        TEXT department "Assigned maintenance division"
        TEXT status "Pending, Assigned, In Progress, Resolved, Closed"
        TEXT admin_notes "Administrative remarks"
        INTEGER similar_count "Number of similar complaints found"
        TEXT top_similar_id "Reference ID of highest matched record"
        REAL top_similarity_score "Cosine similarity coefficient (0.0 - 1.0)"
        TEXT created_at "ISO-8601 creation timestamp"
        TEXT updated_at "ISO-8601 modification timestamp"
        TEXT resolved_at "ISO-8601 completion timestamp"
    }

    STATUS_HISTORY {
        SERIAL id PK
        TEXT complaint_id FK "References complaints.complaint_id"
        TEXT old_status "Previous status state"
        TEXT new_status "Updated status state"
        TEXT changed_by "Actor (System, Administrator, or Staff)"
        TEXT comment "Transition remarks or update justification"
        TEXT changed_at "ISO-8601 event timestamp"
    }
```

### Database Performance Indexes
To guarantee fast query execution during dashboard filtering and high-frequency ticket lookups, the following B-tree indexes are implemented:
- `idx_complaints_complaint_id`: Accelerates exact lookups on ticket reference IDs.
- `idx_complaints_status`: Speeds up admin dashboard filtering by status pipeline.
- `idx_complaints_category`: Accelerates category aggregations and analytics charts.
- `idx_status_history_complaint_id`: Optimizes chronological timeline retrieval for complaint tracking.

---

## 5. Security & Reliability Architecture

| Security Measure | Implementation Mechanism | Purpose |
| :--- | :--- | :--- |
| **Administrative Authentication** | Constant-time HMAC string comparison (`hmac.compare_digest`) via `X-Admin-Key` or `Bearer` tokens. | Protects administrative updates and state transitions against timing attacks and unauthorized tampering. |
| **Fail-Closed Auth Design** | Automatic HTTP 500 rejection if `ADMIN_API_KEY` is undefined or empty. | Prevents endpoints from defaulting to open access in misconfigured environments. |
| **SQL Injection Prevention** | Fully parameterized SQL queries (`%s` placeholders via `psycopg3`). | Eliminates SQL injection vulnerabilities across all dynamic search and update operations. |
| **Input Validation** | Pydantic v2 data models with custom regex validators and normalized email structures. | Rejects malformed, excessive, or unparseable payloads before business processing. |
| **Information Exposure Prevention** | Global FastAPI exception handlers intercept unhandled internal exceptions. | Prevents database stack traces and connection strings from leaking to client responses. |
| **Encrypted Cloud Transport** | SSL mode enforced (`sslmode=require`) on remote database URLs. | Secures data-in-transit between the backend service and cloud PostgreSQL instances. |

---

## 6. Technical Stack Summary

- **Programming Language:** Python 3.10+
- **Frontend Framework:** Streamlit 1.35+
- **Backend Framework:** FastAPI 0.110+ running with Uvicorn ASGI
- **Relational Database:** PostgreSQL (Neon Serverless Cloud)
- **Database Driver:** `psycopg` 3.1+ with `psycopg_pool`
- **Machine Learning / NLP:** `scikit-learn` 1.4+ (TF-IDF Vectorization, Cosine Similarity), NumPy
- **Interactive Visualizations:** Plotly Express & Plotly Graph Objects 5.20+
- **Document Generation:** ReportLab 4.1+
- **Automated Testing:** Pytest 8.0+
