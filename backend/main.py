from fastapi import FastAPI
from pydantic import BaseModel
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.complaint_analyzer import get_analyzer

app = FastAPI(
    title="CivicPulse AI API",
    description="Intelligent Grievance Management & Resolution Platform",
    version="1.0.0"
)

analyzer = get_analyzer()


class ComplaintRequest(BaseModel):
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
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/analyze")
def analyze_complaint(request: ComplaintRequest):
    result = analyzer.analyze(
        title=request.title,
        description=request.description,
        user_category=request.category
    )

    return {
        "status": "success",
        "analysis": result
    }
