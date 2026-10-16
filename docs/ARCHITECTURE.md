# CivicPulse AI — System Architecture & Technical Specifications

This document outlines the software architecture, component relationships, data flow pipelines, and technical design decisions powering **CivicPulse AI — AI-Powered Institutional Grievance Management and Hotspot Analytics Platform**.

---

## 1. High-Level System Architecture

CivicPulse AI is structured as a decoupled multi-tier web application consisting of a modern **Streamlit frontend client**, an asynchronous **FastAPI REST backend**, a managed cloud **PostgreSQL database (Neon)**, and local **ReportLab document generation engines**.

```mermaid
flowchart TB
    subgraph ClientLayer["Frontend Client Tier (Streamlit)"]
        UI["Streamlit Application<br/><code>app.py</code>"]
        V_Submit["Submit View<br/><code>views/submit_view.py</code>"]
        V_Track["Tracker View<br/><code>views/tracker_view.py</code>"]
        V_Admin["Admin Dashboard<br/><code>views/admin_view.py</code>"]
        V_Analytics["Analytics & Hotspots<br/><code>views/analytics_view.py</code>"]
        V_Reports["Reports & PDF Export<br/><code>views/reports_view.py</code>"]
        ApiClient["Unified API Client<br/><code>utils/api_client.py</code>"]
        PdfGen["Local PDF Generator<br/><code>modules/report_generator.py</code>"]

        UI --> V_Submit
        UI --> V_Track
        UI --> V_Admin
        UI --> V_Analytics
        UI --> V_Reports
        V_Submit --> ApiClient
        V_Track --> ApiClient
        V_Admin --> ApiClient
        V_Analytics --> ApiClient
        V_Reports --> ApiClient
        V_Reports --> PdfGen
        V_Track --> PdfGen
    end

    subgraph ApiLayer["Application Backend Tier (FastAPI)"]
        API["FastAPI REST Server<br/><code>backend/main.py</code>"]
        AuthMiddleware["Admin Auth Guard<br/>Constant-time HMAC"]
        
        subgraph EngineLayer["Intelligence & Routing Engines"]
            Analyzer["Complaint Analyzer<br/>Taxonomy Keyword Matcher"]
            PriorityEng["Priority Engine<br/>Deterministic Signal Scorer"]
            DeptRouter["Department Router<br/>SLA & Division Allocator"]
            SimEngine["Similarity Engine<br/>TF-IDF & Cosine Similarity"]
        end

        DBPool["PostgreSQL Connection Pool<br/><code>backend/database.py</code>"]
    end

    subgraph DataLayer["Persistence Tier (PostgreSQL)"]
        DB[(Cloud PostgreSQL<br/>Neon / Managed Instance)]
        T_Complaints[("Table: complaints")]
        T_History[("Table: status_history")]
        DB --> T_Complaints
        DB --> T_History
    end

    ApiClient -- "HTTPS / JSON REST Calls" --> API
    API --> AuthMiddleware
    API --> Analyzer
    API --> PriorityEng
    API --> DeptRouter
    API --> SimEngine
    API --> DBPool
    DBPool -- "psycopg3 (SSL Mode Require)" --> DB
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
