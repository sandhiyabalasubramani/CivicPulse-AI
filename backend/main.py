from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import sys
import uuid
from datetime import datetime
import os

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from modules.complaint_analyzer import get_analyzer


def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured in the .env file"
        )

    return psycopg.connect(database_url)


app = FastAPI(
    title="CivicPulse AI API",
    description="Intelligent Grievance & Resolution Platform API",
    version="1.0.0"
)


class ComplaintRequest(BaseModel):
    name: str
    email: str
    location: str
    title: str
    description: str
    category: str = "Auto-Detect"


@app.get("/")
def root():
    return {
        "message": "CivicPulse AI API is running",
        "status": "success"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "CivicPulse AI API"
    }


@app.post("/analyze")
def analyze_complaint(request: ComplaintRequest):
    try:
        analyzer = get_analyzer()

        analysis = analyzer.analyze(
            title=request.title,
            description=request.description,
            user_category=request.category
        )

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@app.get("/complaints/count")
def complaints_count():
    try:
        conn = get_connection()

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM complaints")
            complaints = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM status_history")
            status_history = cur.fetchone()[0]

        conn.close()

        return {
            "status": "success",
            "complaints": complaints,
            "status_history": status_history
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )


@app.post("/complaints")
def create_complaint(request: ComplaintRequest):
    conn = None

    try:
        analyzer = get_analyzer()

        analysis = analyzer.analyze(
            title=request.title,
            description=request.description,
            user_category=request.category
        )

        complaint_id = "CP-" + uuid.uuid4().hex[:8].upper()

        now = datetime.now().isoformat(timespec="seconds")

        conn = get_connection()

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
                    analysis["category"],
                    analysis["subcategory"],
                    "Medium",
                    "",
                    analysis["category"],
                    "Pending",
                    "",
                    0,
                    "",
                    0.0,
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
        conn.close()

        return {
            "status": "success",
            "message": "Complaint submitted successfully",
            "complaint_id": complaint_id,
            "database_id": database_id,
            "analysis": analysis
        }

    except Exception as e:
        if conn:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

        raise HTTPException(
            status_code=500,
            detail=f"Complaint creation failed: {str(e)}"
        )
