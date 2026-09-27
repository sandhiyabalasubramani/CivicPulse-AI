# CivicPulse AI

## Intelligent Complaint Management and Resolution Analytics Platform

CivicPulse AI is a software platform designed to simplify the process of submitting, analyzing, prioritizing, routing, tracking, and reporting civic complaints.

The system combines rule-based text processing, similarity analysis, priority evaluation, department routing, database management, analytics, and report generation into a single application.

It is designed as an academic and portfolio project demonstrating how software engineering, data processing, and AI-assisted techniques can be applied to a real-world complaint management workflow.

---

## 1. What Problem Does CivicPulse AI Solve?

In a traditional complaint management system, complaints may need to be manually:

* Read and understood
* Categorized
* Assigned to departments
* Prioritized
* Checked for duplicate complaints
* Updated through different statuses
* Analyzed for recurring issues
* Converted into reports

This can make complaint handling slower and make it difficult to identify recurring problems.

CivicPulse AI automates several of these steps.

A complaint can move through the following workflow:

```text
Citizen Complaint
       |
       v
Text Processing
       |
       v
Complaint Analysis
       |
       +------------------+
       |                  |
       v                  v
Category Detection    Priority Evaluation
       |                  |
       +--------+---------+
                |
                v
        Department Routing
                |
                v
      Similar Complaint Check
                |
                v
        Complaint Tracking
                |
                v
            Analytics
                |
                v
          Report Generation
```

---

## 2. How Does CivicPulse AI Work?

The system processes a complaint through multiple stages.

### Step 1: Complaint Submission

A user submits a complaint through the application.

Example:

```text
There is a large amount of garbage near the main road
and it has not been collected for several days.
```

The system receives the complaint text and begins processing it.

---

### Step 2: Text Processing

The complaint text is cleaned and normalized before analysis.

Typical processing includes:

* Converting text into a consistent format
* Removing unnecessary characters
* Normalizing text
* Extracting useful keywords
* Preparing text for classification and similarity analysis

This improves consistency during further processing.

---

### Step 3: Complaint Category Detection

The system analyzes keywords and complaint content to determine the most relevant category.

Possible categories include:

* Water Supply
* Roads
* Waste Management
* Electricity
* Drainage
* Street Lighting
* Public Safety
* Sanitation
* Other Civic Issues

For example:

```text
Complaint:
Garbage has not been collected for three days.

Detected Category:
Waste Management
```

---

### Step 4: Priority Evaluation

The system evaluates the complaint to determine its priority.

Factors can include:

* Severity
* Urgency
* Safety-related keywords
* Public impact
* Complaint content

Example:

```text
Complaint:
Open electrical wires are hanging near a school entrance.

Priority:
High
```

The priority engine helps identify complaints that may require faster attention.

---

### Step 5: Department Routing

After analyzing the complaint, CivicPulse AI determines the department that is most relevant to the issue.

Example:

```text
Complaint:
Street lights are not working in our area.

Category:
Street Lighting

Department:
Electrical Department
```

This reduces the need for manual department assignment.

---

### Step 6: Similar Complaint Detection

The system checks whether similar complaints already exist.

This helps identify:

* Duplicate complaints
* Recurring problems
* Multiple complaints about the same issue
* Frequently reported locations

The project uses text similarity techniques to compare complaint descriptions.

A similarity score can help determine how closely two complaints are related.

---

### Step 7: Complaint Tracking

Each complaint can move through different statuses.

Example:

```text
Pending
   |
   v
Assigned
   |
   v
In Progress
   |
   v
Resolved
   |
   v
Closed
```

The system maintains status history so that the progression of a complaint can be tracked.

---

### Step 8: Analytics

The analytics module provides information about complaint patterns.

It can analyze:

* Total complaints
* Complaint categories
* Complaint priorities
* Department distribution
* Location-based complaints
* Complaint status
* Recurring issues
* Resolution information

The analytics section helps users understand where and what types of civic problems are being reported.

---

### Step 9: Report Generation

CivicPulse AI includes report-generation functionality for complaint and analytics information.

Reports can help summarize:

* Complaint details
* Category
* Priority
* Department
* Status
* Resolution information
* Complaint trends

---

# 3. Main Features

## Complaint Management

* Submit complaints
* Store complaint information
* Track complaint status
* Maintain complaint history

## AI-Assisted Complaint Analysis

* Text processing
* Keyword-based analysis
* Category detection
* Priority evaluation
* Department routing

## Similarity Analysis

* Detect similar complaints
* Identify possible duplicates
* Compare complaint descriptions
* Identify recurring complaint patterns

## Status Management

Supported complaint lifecycle:

```text
Pending
Assigned
In Progress
Resolved
Closed
```

Status history is maintained to provide an audit trail of complaint updates.

## Analytics Dashboard

The analytics module provides insights based on:

* Category
* Location
* Department
* Priority
* Status

## Report Generation

The system provides report-generation functionality for complaint and analytics information.

## Database Support

The project contains:

* SQLite database support for the Streamlit application
* PostgreSQL database support for the FastAPI backend
* PostgreSQL schema
* SQLite-to-PostgreSQL migration utility

---

# 4. System Architecture

The project contains a Streamlit application and a FastAPI backend.

```text
                    +----------------------+
                    |       User           |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  Streamlit Frontend  |
                    |      app.py          |
                    +----------+-----------+
                               |
             +-----------------+-----------------+
             |                 |                 |
             v                 v                 v
      Submit Complaint     Tracker View    Analytics View
             |                 |                 |
             +-----------------+-----------------+
                               |
                               v
                    +----------------------+
                    |    Analysis Modules  |
                    +----------------------+
                    | Text Processing      |
                    | Complaint Analyzer   |
                    | Priority Engine      |
                    | Department Router    |
                    | Similarity Engine    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |      Database        |
                    +----------------------+
                    | SQLite              |
                    | PostgreSQL Backend   |
                    +----------------------+

                    FastAPI Backend
                          |
                          v
                  PostgreSQL Database
```

---

# 5. Technology Stack

## Frontend

* Python
* Streamlit

## Backend

* Python
* FastAPI
* Uvicorn

## Database

* SQLite
* PostgreSQL
* Psycopg

## AI and Data Processing

* Scikit-learn
* TF-IDF
* Cosine Similarity
* Rule-based text analysis

## Document Processing

* PyPDF2
* python-docx

## Testing

* Pytest

## Environment Management

* python-dotenv

---

# 6. Project Structure

```text
CivicPulse-AI/
|
+-- app.py
+-- README.md
+-- requirements.txt
+-- .gitignore
|
+-- backend/
|   +-- database.py
|   +-- main.py
|
+-- database/
|   +-- database.py
|   +-- migrate_sqlite_to_postgres.py
|   +-- postgres_schema.sql
|   +-- schema.py
|   +-- __init__.py
|
+-- data/
|   +-- sample_data.py
|   +-- __init__.py
|
+-- modules/
|   +-- complaint_analyzer.py
|   +-- department_router.py
|   +-- priority_engine.py
|   +-- report_generator.py
|   +-- similarity_engine.py
|   +-- text_processing.py
|   +-- __init__.py
|
+-- tests/
|   +-- test_analyzer.py
|   +-- test_database.py
|   +-- test_e2e_integration.py
|   +-- test_priority.py
|   +-- test_similarity.py
|   +-- __init__.py
|
+-- utils/
|   +-- ui_components.py
|   +-- validators.py
|   +-- __init__.py
|
+-- views/
    +-- admin_view.py
    +-- analytics_view.py
    +-- reports_view.py
    +-- submit_view.py
    +-- tracker_view.py
    +-- __init__.py
```

---

# 7. Important Modules

## app.py

Main Streamlit entry point.

It connects the application views and provides the user interface.

---

## modules/text_processing.py

Responsible for preparing complaint text for further analysis.

---

## modules/complaint_analyzer.py

Analyzes complaint information and identifies relevant complaint categories and attributes.

---

## modules/priority_engine.py

Evaluates complaint information and determines an appropriate priority level.

---

## modules/department_router.py

Maps complaint categories and keywords to the relevant department.

---

## modules/similarity_engine.py

Uses text similarity techniques to compare complaints and identify potentially similar complaints.

---

## modules/report_generator.py

Generates reports from complaint and analytics information.

---

## database/database.py

Handles SQLite database operations used by the Streamlit application.

It manages complaint records and status history.

---

## backend/database.py

Provides PostgreSQL database connectivity for the FastAPI backend.

The database connection is configured through the `DATABASE_URL` environment variable.

---

## backend/main.py

Contains the FastAPI backend and API endpoints.

The backend provides an API layer for interacting with complaint-related functionality.

---

## database/postgres_schema.sql

Contains the PostgreSQL database schema used by the backend.

---

## database/migrate_sqlite_to_postgres.py

Provides a migration utility for transferring complaint data from SQLite to PostgreSQL.

This is intended as a migration/setup utility rather than something that needs to be executed every time the application starts.

---

# 8. Database Architecture

CivicPulse AI currently contains two database paths.

### Streamlit Application

The Streamlit application uses SQLite through:

```text
database/database.py
```

SQLite is convenient for local development and demonstration.

### FastAPI Backend

The FastAPI backend uses PostgreSQL through:

```text
backend/database.py
```

The PostgreSQL connection is configured using:

```text
DATABASE_URL
```

in the `.env` file.

### Database Flow

```text
Streamlit Application
        |
        v
database/database.py
        |
        v
SQLite


FastAPI Backend
        |
        v
backend/database.py
        |
        v
PostgreSQL
```

The project also contains a migration utility for moving data from SQLite to PostgreSQL.

---

# 9. Environment Configuration

Create a `.env` file in the project root.

Example:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/civicpulse
```

Do not commit the `.env` file to GitHub.

The project `.gitignore` already excludes:

```text
.env
```

---

# 10. Installation

## Step 1: Clone the Repository

```bash
git clone https://github.com/sandhiyabalasubramani/CivicPulse-AI.git
```

Move into the project directory:

```bash
cd CivicPulse-AI
```

---

## Step 2: Create a Virtual Environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

---

# 11. Running the Streamlit Application

Start the Streamlit application with:

```powershell
streamlit run app.py
```

Streamlit will provide a local URL, normally similar to:

```text
http://localhost:8501
```

Open the displayed URL in a browser.

---

# 12. Running the FastAPI Backend

Start the backend using:

```powershell
uvicorn backend.main:app --reload
```

The backend normally runs at:

```text
http://127.0.0.1:8000
```

FastAPI automatically provides interactive API documentation at:

```text
http://127.0.0.1:8000/docs
```

---

# 13. PostgreSQL Setup

If PostgreSQL is being used for the backend:

1. Install PostgreSQL.
2. Create a PostgreSQL database.
3. Configure the `DATABASE_URL` in `.env`.
4. Apply the schema from:

```text
database/postgres_schema.sql
```

5. Start the FastAPI backend.

The exact PostgreSQL username, password, host, port, and database name depend on the local environment.

---

# 14. SQLite to PostgreSQL Migration

The project includes:

```text
database/migrate_sqlite_to_postgres.py
```

This utility can be used when existing SQLite complaint data needs to be transferred to PostgreSQL.

The migration process can be represented as:

```text
Existing SQLite Database
          |
          v
Migration Utility
          |
          v
PostgreSQL Database
```

Migration should be performed only when PostgreSQL setup and the required environment variables are configured.

---

# 15. Testing

The project uses Pytest.

Run all tests with:

```powershell
pytest -q
```

The test suite covers areas such as:

* Complaint analysis
* Database operations
* End-to-end integration
* Priority evaluation
* Similarity analysis

Example:

```text
tests/
|
+-- test_analyzer.py
+-- test_database.py
+-- test_e2e_integration.py
+-- test_priority.py
+-- test_similarity.py
```

---

# 16. Example Complaint Processing

Consider the following complaint:

```text
There is an open drainage problem near the school
and dirty water is flowing onto the road.
```

The system can process it approximately as follows:

```text
Complaint
   |
   v
Text Processing
   |
   v
Category Detection
   |
   +--> Drainage
   |
   v
Priority Evaluation
   |
   +--> Based on severity and impact
   |
   v
Department Routing
   |
   +--> Relevant civic department
   |
   v
Similarity Check
   |
   +--> Compare with existing complaints
   |
   v
Store and Track
   |
   v
Analytics and Reports
```

The exact classification and priority depend on the rules and data available in the application.

---

# 17. Complaint Status History

CivicPulse AI maintains a status history for complaints.

For example:

```text
Complaint Created
       |
       v
Pending
       |
       v
Assigned
       |
       v
In Progress
       |
       v
Resolved
       |
       v
Closed
```

Each status transition can be recorded in the status history.

This provides an audit trail and makes it possible to understand how a complaint progressed over time.

---

# 18. Analytics

The analytics module helps identify complaint patterns.

Examples of useful analysis include:

### Category Analysis

```text
Waste Management
Roads
Water Supply
Drainage
Electricity
Street Lighting
```

This can help identify which categories receive more complaints.

### Location Analysis

Complaints can be analyzed based on location to identify areas where similar issues are repeatedly reported.

### Department Analysis

Complaint distribution can be analyzed across departments.

### Priority Analysis

The system can display the distribution of complaints according to priority.

### Status Analysis

The application can show how many complaints are:

```text
Pending
Assigned
In Progress
Resolved
Closed
```

---

# 19. Similarity Detection

CivicPulse AI uses text similarity techniques to identify complaints that may describe similar problems.

A common approach used in the project is:

```text
Complaint Text
      |
      v
TF-IDF Representation
      |
      v
Vector Representation
      |
      v
Cosine Similarity
      |
      v
Similarity Score
```

TF-IDF converts text into numerical representations.

Cosine similarity compares the resulting vectors.

A higher similarity score indicates that two complaint texts are more similar according to the selected text-processing approach.

Similarity detection is useful for identifying potentially duplicate or recurring complaints.

---

# 20. AI Approach

The term "AI" in CivicPulse AI refers to a combination of automated text-processing and machine-learning-based techniques.

The current project includes:

* Rule-based keyword analysis
* Text normalization
* TF-IDF
* Cosine similarity
* Automated priority evaluation
* Automated department routing

The system is not presented as a large language model or generative AI system.

This distinction is important for understanding the actual technical implementation.

---

# 21. Key Design Principles

The project focuses on:

### Automation

Reduce repetitive manual complaint-processing tasks.

### Modularity

Separate complaint analysis, priority evaluation, routing, similarity detection, database operations, reports, and UI into different modules.

### Traceability

Maintain complaint status history.

### Data Analysis

Provide analytics based on complaint information.

### Extensibility

Keep the architecture modular so additional AI models, APIs, dashboards, and database services can be added later.

---

# 22. API

The FastAPI backend provides an API layer for backend functionality.

Interactive API documentation can be accessed through:

```text
http://127.0.0.1:8000/docs
```

When the backend is running, the Swagger interface can be used to inspect available endpoints and test supported API operations.

---

# 23. Security and Configuration Notes

Sensitive configuration should not be committed to GitHub.

The following files are intentionally ignored:

```text
.env
civicpulse.db
*.sqlite3
*.db-journal
civicpulse_backup_before_postgresql.db
```

This prevents local database files and environment credentials from being unnecessarily included in the public repository.

---

# 24. Current Limitations

CivicPulse AI is an academic and portfolio project.

The current implementation has several limitations:

* Classification depends on the implemented rules and available data.
* Priority evaluation is based on the project's configured logic.
* Similarity results depend on the text-processing approach and available complaint data.
* The Streamlit application and FastAPI backend currently use separate database paths.
* PostgreSQL integration is provided through the backend.
* The project does not currently depend on an external large language model API.
* Production-scale authentication and authorization are not the main focus of the current version.
* Large-scale deployment would require additional infrastructure and security configuration.

These limitations can be addressed in future versions.

---

# 25. Future Enhancements

Possible future improvements include:

* Large language model integration
* Multilingual complaint processing
* Voice-based complaint submission
* Mobile application
* Real-time notifications
* Email and SMS alerts
* Advanced duplicate detection
* Geospatial complaint visualization
* Role-based authentication
* Public complaint dashboards
* Cloud deployment
* Containerization using Docker
* Production PostgreSQL deployment
* Advanced predictive analytics
* Automated response generation

---

# 26. Why This Project?

CivicPulse AI demonstrates how software development and AI-assisted techniques can be combined to solve a practical civic problem.

The project covers multiple areas of software engineering:

```text
Frontend Development
        +
Backend Development
        +
Database Management
        +
Text Processing
        +
Machine Learning
        +
Analytics
        +
Testing
        +
Report Generation
```

It also demonstrates the importance of designing a system as multiple connected modules rather than implementing everything inside a single program.

---

# 27. Skills Demonstrated

This project demonstrates practical experience with:

* Python
* Streamlit
* FastAPI
* Uvicorn
* SQLite
* PostgreSQL
* Psycopg
* Scikit-learn
* TF-IDF
* Cosine Similarity
* Text Processing
* REST API Development
* Database Design
* Data Analytics
* Automated Testing
* Git and GitHub
* Modular Software Architecture

---

# 28. How the Complete System Fits Together

The complete conceptual workflow is:

```text
                    CIVIC COMPLAINT
                           |
                           v
                  +----------------+
                  | Text Processing |
                  +-------+--------+
                          |
                          v
                +--------------------+
                | Complaint Analysis |
                +---------+----------+
                          |
             +------------+------------+
             |            |            |
             v            v            v
         Category      Priority     Department
         Detection     Evaluation    Routing
             |            |            |
             +------------+------------+
                          |
                          v
                +--------------------+
                | Similarity Engine  |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Database Storage   |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Status Tracking    |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Analytics          |
                +---------+----------+
                          |
                          v
                +--------------------+
                | Report Generation  |
                +--------------------+
```

This workflow represents the overall architecture of CivicPulse AI.

---

# 29. Getting Started Quickly

For a basic local demonstration:

```powershell
git clone https://github.com/sandhiyabalasubramani/CivicPulse-AI.git

cd CivicPulse-AI

python -m venv venv

.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

streamlit run app.py
```

Then open the local Streamlit URL displayed in the terminal.

For backend development:

```powershell
uvicorn backend.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# 30. Repository

GitHub Repository:

```text
https://github.com/sandhiyabalasubramani/CivicPulse-AI
```

---

# 31. Author

**Sandhiya B**

B.E. Electrical and Electronics Engineering Student

Interested in:

* Python Development
* AI
* IoT
* Embedded Systems
* Software Development
* Data Processing

---

# 32. Project Summary

CivicPulse AI is an intelligent complaint management and resolution analytics platform that demonstrates how civic complaints can be processed through an automated software pipeline.

The system combines:

```text
Complaint Submission
        +
Text Processing
        +
Category Detection
        +
Priority Evaluation
        +
Department Routing
        +
Similarity Detection
        +
Status Tracking
        +
Database Management
        +
Analytics
        +
Report Generation
```

The project provides a modular foundation that can be extended toward a larger civic technology platform in the future.
