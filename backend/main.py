from fastapi import FastAPI, HTTPException, Depends, Header, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from pathlib import Path
from contextlib import asynccontextmanager
import sys
import uuid
from datetime import datetime
import os
import logging
import hmac
import psycopg
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any


# ============================================================
# PROJECT SETUP & LOGGING
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger("civicpulse_api")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)


# ============================================================
# PROJECT MODULES & DATABASE CONNECTION
# ============================================================

from modules.complaint_analyzer import get_analyzer
from modules.priority_engine import get_priority_engine
from modules.department_router import get_department_router
from modules.similarity_engine import get_similarity_engine
from backend.database import get_connection, ensure_schema, check_db_status, close_pool


# ============================================================
# FASTAPI APP & AUTHENTICATION CONFIGURATION
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager:
    1. Verifies/initializes PostgreSQL schema at startup (safe & idempotent).
    2. Closes database connection pool on shutdown.
    """
    logger.info("CivicPulse AI API starting up...")
    try:
        init_res = ensure_schema()
        if init_res.get("success"):
            logger.info("Database schema verification/initialization successful.")
        else:
            logger.warning("Database schema startup check: %s", init_res.get("message"))
    except Exception as e:
        logger.error("Failed to verify/initialize database schema at startup: %s", e)
    yield
    logger.info("CivicPulse AI API shutting down...")
    try:
        close_pool()
    except Exception:
        pass


app = FastAPI(
    title="CivicPulse AI API",
    description="Intelligent Grievance & Resolution Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for Streamlit Cloud and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

admin_bearer_scheme = HTTPBearer(auto_error=False)


def get_admin_api_key() -> str:
    """
    Retrieves the configured ADMIN_API_KEY from environment.
    Returns an empty string if not configured. Never uses hardcoded fallbacks.
    """
    return os.getenv("ADMIN_API_KEY", "").strip()


def verify_admin_auth(
    x_admin_key: Optional[str] = Header(None, alias="X-Admin-Key"),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    credentials: Optional[HTTPAuthorizationCredentials] = Security(admin_bearer_scheme)
) -> bool:
    """
    Enforces server-side authentication for admin-restricted operations.
    Validates against ADMIN_API_KEY using constant-time comparison.
    Fails closed with HTTP 500 if ADMIN_API_KEY is missing or empty in configuration.
    Supports X-Admin-Key, X-API-Key, or Bearer token Authorization headers.
    """
    token = None
    if x_admin_key:
        token = x_admin_key.strip()
    elif x_api_key:
        token = x_api_key.strip()
    elif credentials and credentials.credentials:
        token = credentials.credentials.strip()

    if not token:
        logger.warning("Admin status update rejected: Missing authentication credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Admin authentication credentials required."
        )

    expected_key = get_admin_api_key()
    if not expected_key:
        logger.error(
            "Admin authentication misconfiguration: ADMIN_API_KEY is not configured or empty. "
            "Rejecting status update request (fail-closed)."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: Admin authentication is not configured. Status updates are disabled."
        )

    if not hmac.compare_digest(token, expected_key):
        logger.warning("Admin status update rejected: Invalid admin key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid admin credentials."
        )

    return True


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """
    Global safe exception handler preventing unhandled internal stack traces
    or sensitive database errors from being exposed to the client.
    """
    logger.error("Unhandled server exception on %s %s: %s", request.method, request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred while processing your request. Please try again later."}
    )


# ============================================================
# REQUEST MODELS
# ============================================================

class ComplaintRequest(BaseModel):
    name: str
    email: EmailStr
    location: str
    title: str
    description: str
    category: str = "Auto-Detect"
    department: str = "Auto-Assign"

    @field_validator("email", mode="before")
    @classmethod
    def clean_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            v = v.strip().lower()
        return v


SUPPORTED_STATUSES = ["Pending", "Assigned", "In Progress", "Resolved", "Closed"]
SUPPORTED_PRIORITIES = ["Low", "Medium", "High", "Critical"]


class StatusUpdateRequest(BaseModel):
    new_status: str
    changed_by: Optional[str] = "Admin"
    comment: Optional[str] = ""
    admin_notes: Optional[str] = None
    priority: Optional[str] = None
    department: Optional[str] = None

    @field_validator("new_status")
    @classmethod
    def validate_new_status(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Status is required and cannot be empty.")
        clean_status = v.strip()
        for valid in SUPPORTED_STATUSES:
            if clean_status.lower() == valid.lower():
                return valid
        raise ValueError(
            f"Invalid status '{clean_status}'. Supported statuses are: {', '.join(SUPPORTED_STATUSES)}"
        )

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        clean_prio = v.strip()
        for valid in SUPPORTED_PRIORITIES:
            if clean_prio.lower() == valid.lower():
                return valid
        raise ValueError(
            f"Invalid priority '{clean_prio}'. Supported priorities are: {', '.join(SUPPORTED_PRIORITIES)}"
        )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "CivicPulse AI API is running",
        "status": "success"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    db_info = check_db_status()
    is_connected = db_info.get("connected", False)
    return {
        "status": "healthy",
        "service": "CivicPulse AI API",
        "database": {
            "status": "connected" if is_connected else "disconnected",
            "configured": db_info.get("configured", False),
            "tables_ready": db_info.get("tables_ready", False),
            "complaints_count": db_info.get("complaints_count", 0),
            "status_history_count": db_info.get("status_history_count", 0),
            "detail": db_info.get("detail", "")
        }
    }


# ============================================================
# ANALYZE COMPLAINT
# ============================================================

@app.post("/analyze")
def analyze_complaint(request: ComplaintRequest):
    try:
        # Complaint Analyzer
        analyzer = get_analyzer()
        analysis = analyzer.analyze(
            title=request.title,
            description=request.description,
            user_category=request.category
        )

        # Priority Engine
        priority_engine = get_priority_engine()
        priority_result = priority_engine.evaluate(
            title=request.title,
            description=request.description,
            category=analysis["category"]
        )

        # Department Router
        router = get_department_router()
        routing_result = router.route(
            category=analysis["category"],
            subcategory=analysis["subcategory"],
            user_department=request.department
        )

        return {
            "status": "success",
            "analysis": analysis,
            "priority": priority_result,
            "routing": routing_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Complaint analysis failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while analyzing the complaint. Please try again later."
        )


# ============================================================
# COMPLAINT COUNT
# ============================================================

@app.get("/complaints/count")
def complaints_count():
    conn = None
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM complaints")
                complaints = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM status_history")
                status_history = cur.fetchone()[0]

            return {
                "status": "success",
                "complaints": complaints,
                "status_history": status_history
            }
        except psycopg.errors.UndefinedTable:
            # Self-healing: if schema tables were missing, auto-create them and retry
            logger.info("Tables not found in /complaints/count. Ensuring schema...")
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except Exception:
                    pass
                conn = None
            ensure_schema()
            conn = get_connection()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM complaints")
                complaints = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM status_history")
                status_history = cur.fetchone()[0]

            return {
                "status": "success",
                "complaints": complaints,
                "status_history": status_history
            }

    except RuntimeError as re:
        logger.error("Database configuration error in /complaints/count: %s", re)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database service unavailable: {str(re)}"
        )
    except Exception as e:
        logger.error("Failed to fetch complaint counts: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve complaint statistics."
        )

    finally:
        if conn:
            conn.close()


# ============================================================
# LIST COMPLAINTS (FILTERING, SEARCH, ADMIN, ANALYTICS, REPORTS)
# ============================================================

@app.get("/complaints")
def list_complaints(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    email: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: Optional[int] = 1000,
    offset: Optional[int] = 0,
):
    conn = None
    try:
        conn = get_connection()
        query = """
            SELECT
                id, complaint_id, name, email, location, title, description,
                category, subcategory, priority, priority_reason, department,
                status, admin_notes, similar_count, top_similar_id, top_similarity_score,
                created_at, updated_at, resolved_at
            FROM complaints
            WHERE 1 = 1
        """
        params = []

        if category and category != "All":
            query += " AND LOWER(COALESCE(category, '')) = LOWER(%s)"
            params.append(category.strip())

        if priority and priority != "All":
            query += " AND LOWER(COALESCE(priority, '')) = LOWER(%s)"
            params.append(priority.strip())

        if status and status != "All":
            query += " AND LOWER(COALESCE(status, '')) = LOWER(%s)"
            params.append(status.strip())

        if location and location != "All":
            query += " AND LOWER(COALESCE(location, '')) = LOWER(%s)"
            params.append(location.strip())

        if department and department != "All":
            query += " AND LOWER(COALESCE(department, '')) = LOWER(%s)"
            params.append(department.strip())

        if email and email.strip():
            clean_email = email.strip().lower()
            query += " AND (LOWER(email) = %s OR LOWER(email) LIKE %s)"
            params.extend([clean_email, f"%{clean_email}%"])

        if search_query and search_query.strip():
            pattern = f"%{search_query.strip().lower()}%"
            query += """
                AND (
                    LOWER(complaint_id) LIKE %s
                    OR LOWER(COALESCE(title, '')) LIKE %s
                    OR LOWER(COALESCE(description, '')) LIKE %s
                    OR LOWER(COALESCE(name, '')) LIKE %s
                    OR LOWER(COALESCE(email, '')) LIKE %s
                    OR LOWER(COALESCE(location, '')) LIKE %s
                    OR LOWER(COALESCE(category, '')) LIKE %s
                    OR LOWER(COALESCE(subcategory, '')) LIKE %s
                    OR LOWER(COALESCE(department, '')) LIKE %s
                    OR LOWER(COALESCE(priority, '')) LIKE %s
                    OR LOWER(COALESCE(status, '')) LIKE %s
                )
            """
            params.extend([pattern] * 11)

        query += " ORDER BY created_at DESC, id DESC"

        if limit:
            query += " LIMIT %s"
            params.append(int(limit))
        if offset:
            query += " OFFSET %s"
            params.append(int(offset))

        with conn.cursor() as cur:
            cur.execute(query, tuple(params))
            rows = cur.fetchall()

        complaints = []
        for row in rows:
            complaints.append({
                "id": row[0],
                "complaint_id": row[1],
                "name": row[2],
                "email": row[3],
                "location": row[4],
                "title": row[5],
                "description": row[6],
                "category": row[7],
                "subcategory": row[8],
                "priority": row[9],
                "priority_reason": row[10],
                "department": row[11],
                "status": row[12],
                "admin_notes": row[13],
                "similar_count": row[14],
                "top_similar_id": row[15],
                "top_similarity_score": row[16],
                "created_at": row[17],
                "updated_at": row[18],
                "resolved_at": row[19]
            })

        return {
            "status": "success",
            "count": len(complaints),
            "complaints": complaints
        }
    except Exception as e:
        logger.error("Failed to list complaints: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve complaints."
        )
    finally:
        if conn:
            conn.close()


# ============================================================
# SEARCH COMPLAINTS BY EMAIL
# ============================================================

@app.get("/complaints/by-email/{email:path}")
def search_complaints_by_email(email: str):
    conn = None
    try:
        clean_email = email.strip().lower()
        if not clean_email:
            return {
                "status": "success",
                "count": 0,
                "complaints": []
            }

        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id, complaint_id, name, email, location, title, description,
                    category, subcategory, priority, priority_reason, department,
                    status, admin_notes, similar_count, top_similar_id, top_similarity_score,
                    created_at, updated_at, resolved_at
                FROM complaints
                WHERE LOWER(email) = %s OR LOWER(email) LIKE %s
                ORDER BY created_at DESC, id DESC
                """,
                (clean_email, f"%{clean_email}%")
            )
            rows = cur.fetchall()

        complaints = []
        for row in rows:
            complaints.append({
                "id": row[0],
                "complaint_id": row[1],
                "name": row[2],
                "email": row[3],
                "location": row[4],
                "title": row[5],
                "description": row[6],
                "category": row[7],
                "subcategory": row[8],
                "priority": row[9],
                "priority_reason": row[10],
                "department": row[11],
                "status": row[12],
                "admin_notes": row[13],
                "similar_count": row[14],
                "top_similar_id": row[15],
                "top_similarity_score": row[16],
                "created_at": row[17],
                "updated_at": row[18],
                "resolved_at": row[19]
            })

        return {
            "status": "success",
            "count": len(complaints),
            "complaints": complaints
        }
    except Exception as e:
        logger.error("Email search failed for email: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to search complaints by email."
        )
    finally:
        if conn:
            conn.close()


# ============================================================
# COMPLAINT KPIS & RESOLUTION METRICS
# ============================================================

@app.get("/complaints/kpis")
def get_complaint_kpis():
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM complaints")
            total = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Pending'")
            pending = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Assigned'")
            assigned = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'")
            in_progress = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM complaints WHERE status IN ('Resolved', 'Closed')")
            resolved = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM complaints WHERE priority = 'High'")
            high_priority = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM complaints WHERE priority = 'Critical'")
            critical_priority = cur.fetchone()[0]

            cur.execute(
                """
                SELECT created_at, resolved_at
                FROM complaints
                WHERE resolved_at IS NOT NULL AND status IN ('Resolved', 'Closed')
                """
            )
            resolved_rows = cur.fetchall()

        avg_res_hours = 0.0
        if resolved_rows:
            durations = []
            for created_val, resolved_val in resolved_rows:
                try:
                    c_str = str(created_val).replace("T", " ")
                    r_str = str(resolved_val).replace("T", " ")
                    c_dt = datetime.strptime(c_str[:19], "%Y-%m-%d %H:%M:%S")
                    r_dt = datetime.strptime(r_str[:19], "%Y-%m-%d %H:%M:%S")
                    diff_hours = (r_dt - c_dt).total_seconds() / 3600.0
                    if diff_hours >= 0:
                        durations.append(diff_hours)
                except Exception:
                    pass
            if durations:
                avg_res_hours = sum(durations) / len(durations)

        resolution_rate = (resolved / total * 100.0) if total > 0 else 0.0

        return {
            "status": "success",
            "kpis": {
                "total": total,
                "pending": pending,
                "assigned": assigned,
                "in_progress": in_progress,
                "resolved": resolved,
                "high_priority": high_priority,
                "critical_priority": critical_priority,
                "resolution_rate": round(resolution_rate, 1),
                "avg_resolution_hours": round(avg_res_hours, 1)
            }
        }
    except Exception as e:
        logger.error("KPI calculation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to calculate complaint metrics."
        )
    finally:
        if conn:
            conn.close()


# ============================================================
# DISTINCT COLUMN VALUES
# ============================================================

@app.get("/complaints/distinct/{column}")
def get_distinct_values(column: str):
    valid_columns = {
        "category": "category",
        "priority": "priority",
        "status": "status",
        "location": "location",
        "department": "department"
    }
    col_name = valid_columns.get(column.lower())
    if not col_name:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid column name: {column}"
        )

    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT DISTINCT {col_name} FROM complaints "
                f"WHERE {col_name} IS NOT NULL AND {col_name} != '' "
                f"ORDER BY {col_name} ASC"
            )
            values = [row[0] for row in cur.fetchall()]

        return {
            "status": "success",
            "column": col_name,
            "values": values
        }
    except Exception as e:
        logger.error("Failed to fetch distinct values for column %s: %s", column, e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve distinct values."
        )
    finally:
        if conn:
            conn.close()


# ============================================================
# UPDATE COMPLAINT STATUS & AUDIT LOG (ADMIN PROTECTED)
# ============================================================

@app.put("/complaints/{complaint_id}/status")
def update_complaint_status(
    complaint_id: str,
    request: StatusUpdateRequest,
    _auth: bool = Depends(verify_admin_auth)
):
    cid = complaint_id.strip() if complaint_id else ""
    if not cid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint ID cannot be empty."
        )

    conn = None
    try:
        conn = get_connection()
        now = datetime.now().isoformat(timespec="seconds")

        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, resolved_at FROM complaints WHERE complaint_id = %s",
                (cid,)
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Complaint '{cid}' not found"
                )

            old_status = row[0]
            current_resolved_at = row[1]
            new_resolved_at = current_resolved_at

            if request.new_status in ["Resolved", "Closed"] and not current_resolved_at:
                new_resolved_at = now
            elif request.new_status not in ["Resolved", "Closed"] and old_status in ["Resolved", "Closed"]:
                new_resolved_at = None

            update_query = """
                UPDATE complaints
                SET status = %s, updated_at = %s, resolved_at = %s
            """
            update_params = [request.new_status, now, new_resolved_at]

            if request.admin_notes is not None:
                update_query += ", admin_notes = %s"
                update_params.append(request.admin_notes)

            if request.priority is not None:
                update_query += ", priority = %s"
                update_params.append(request.priority)

            if request.department is not None:
                update_query += ", department = %s"
                update_params.append(request.department)

            update_query += " WHERE complaint_id = %s"
            update_params.append(cid)

            cur.execute(update_query, tuple(update_params))

            # Add to status_history log
            cur.execute(
                """
                INSERT INTO status_history (
                    complaint_id, old_status, new_status, changed_by, comment, changed_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    cid,
                    old_status,
                    request.new_status,
                    request.changed_by or "Admin",
                    request.comment or "",
                    now
                )
            )

        conn.commit()
        return {
            "status": "success",
            "message": f"Complaint {cid} updated to {request.new_status}"
        }
    except HTTPException:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        logger.error("Status update failed for complaint %s: %s", cid, e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while updating the complaint status."
        )
    finally:
        if conn:
            conn.close()


# ============================================================
# GET ALL STATUS HISTORY (AUDIT TRAIL)
# ============================================================

@app.get("/status-history")
def get_all_status_history(limit: Optional[int] = 5000):
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, complaint_id, old_status, new_status, changed_by, comment, changed_at
                FROM status_history
                ORDER BY changed_at DESC
                LIMIT %s
                """,
                (limit,)
            )
            rows = cur.fetchall()

        history = []
        for r in rows:
            history.append({
                "id": r[0],
                "complaint_id": r[1],
                "old_status": r[2],
                "new_status": r[3],
                "changed_by": r[4],
                "comment": r[5],
                "changed_at": r[6]
            })

        return {
            "status": "success",
            "count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error("Failed to fetch status history: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve status history."
        )
    finally:
        if conn:
            conn.close()


# ============================================================
# GET SINGLE COMPLAINT
# ============================================================

@app.get("/complaints/{complaint_id}")
def get_complaint(complaint_id: str):
    conn = None
    try:
        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    complaint_id,
                    name,
                    email,
                    location,
                    title,
                    description,
                    category,
                    subcategory,
                    priority,
                    priority_reason,
                    department,
                    status,
                    admin_notes,
                    similar_count,
                    top_similar_id,
                    top_similarity_score,
                    created_at,
                    updated_at,
                    resolved_at
                FROM complaints
                WHERE complaint_id = %s
                """,
                (complaint_id,)
            )

            row = cur.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Complaint '{complaint_id}' not found"
                )

            complaint = {
                "id": row[0],
                "complaint_id": row[1],
                "name": row[2],
                "email": row[3],
                "location": row[4],
                "title": row[5],
                "description": row[6],
                "category": row[7],
                "subcategory": row[8],
                "priority": row[9],
                "priority_reason": row[10],
                "department": row[11],
                "status": row[12],
                "admin_notes": row[13],
                "similar_count": row[14],
                "top_similar_id": row[15],
                "top_similarity_score": row[16],
                "created_at": row[17],
                "updated_at": row[18],
                "resolved_at": row[19]
            }

            cur.execute(
                """
                SELECT
                    old_status,
                    new_status,
                    changed_by,
                    comment,
                    changed_at
                FROM status_history
                WHERE complaint_id = %s
                ORDER BY changed_at ASC
                """,
                (complaint_id,)
            )

            history_rows = cur.fetchall()

            history = []
            for history_row in history_rows:
                history.append(
                    {
                        "old_status": history_row[0],
                        "new_status": history_row[1],
                        "changed_by": history_row[2],
                        "comment": history_row[3],
                        "changed_at": history_row[4]
                    }
                )

        return {
            "status": "success",
            "complaint": complaint,
            "history": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to fetch complaint %s: %s", complaint_id, e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while retrieving the complaint."
        )
    finally:
        if conn:
            conn.close()


# ============================================================
# CREATE COMPLAINT
# ============================================================

@app.post("/complaints")
def create_complaint(request: ComplaintRequest):
    conn = None
    try:
        # Complaint Analyzer
        analyzer = get_analyzer()
        analysis = analyzer.analyze(
            title=request.title,
            description=request.description,
            user_category=request.category
        )

        category = analysis["category"]
        subcategory = analysis["subcategory"]

        # Priority Engine
        priority_engine = get_priority_engine()
        priority_result = priority_engine.evaluate(
            title=request.title,
            description=request.description,
            category=category
        )

        priority = priority_result["priority"]
        priority_reason = priority_result["primary_reason"]

        # Department Router
        router = get_department_router()
        routing_result = router.route(
            category=category,
            subcategory=subcategory,
            user_department=request.department
        )

        assigned_department = routing_result["department"]

        # Similarity Engine
        similarity_engine = get_similarity_engine()

        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    complaint_id,
                    title,
                    description,
                    location,
                    category,
                    status,
                    priority,
                    created_at
                FROM complaints
                ORDER BY created_at DESC
                """
            )
            rows = cur.fetchall()

        existing_complaints = []
        for row in rows:
            existing_complaints.append(
                {
                    "complaint_id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "location": row[3],
                    "category": row[4],
                    "status": row[5],
                    "priority": row[6],
                    "created_at": row[7]
                }
            )

        similarity_result = similarity_engine.find_similar(
            new_title=request.title,
            new_description=request.description,
            existing_complaints=existing_complaints,
            new_location=request.location,
            top_k=5
        )

        similar_count = similarity_result["similar_count"]
        top_similar_id = similarity_result["top_complaint_id"]
        top_similarity_score = similarity_result["top_score"]

        complaint_id = "CP-" + uuid.uuid4().hex[:8].upper()
        now = datetime.now().isoformat(timespec="seconds")

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO complaints (
                    complaint_id,
                    name,
                    email,
                    location,
                    title,
                    description,
                    category,
                    subcategory,
                    priority,
                    priority_reason,
                    department,
                    status,
                    admin_notes,
                    similar_count,
                    top_similar_id,
                    top_similarity_score,
                    created_at,
                    updated_at,
                    resolved_at
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    complaint_id,
                    request.name,
                    request.email,
                    request.location,
                    request.title,
                    request.description,
                    category,
                    subcategory,
                    priority,
                    priority_reason,
                    assigned_department,
                    "Pending",
                    "",
                    similar_count,
                    top_similar_id,
                    top_similarity_score,
                    now,
                    now,
                    None
                )
            )

            database_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO status_history (
                    complaint_id,
                    old_status,
                    new_status,
                    changed_by,
                    comment,
                    changed_at
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    complaint_id,
                    "",
                    "Pending",
                    "System",
                    "Complaint submitted",
                    now
                )
            )

        conn.commit()

        return {
            "status": "success",
            "message": "Complaint submitted successfully",
            "complaint_id": complaint_id,
            "database_id": database_id,
            "analysis": analysis,
            "priority": priority_result,
            "routing": routing_result,
            "similarity": similarity_result
        }

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        logger.error("Complaint creation failed: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while submitting the complaint. Please try again later."
        )
    finally:
        if conn:
            conn.close()