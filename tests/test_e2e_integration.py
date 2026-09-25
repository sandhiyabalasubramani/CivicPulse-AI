"""
End-to-End Integration Tests for CivicPulse AI.
Verifies the complete lifecycle of grievances:
Submission -> NLP Classification -> Priority Scoring -> TF-IDF Similarity ->
Database Insertion -> Status Lifecycle Transition -> PDF Generation.
"""

import os
import tempfile
import gc
import pytest
from database.database import DatabaseManager
from modules.complaint_analyzer import ComplaintAnalyzer
from modules.priority_engine import PriorityEngine
from modules.similarity_engine import SimilarityEngine
from modules.department_router import DepartmentRouter
from modules.report_generator import create_complaint_docket_pdf, create_summary_analytics_pdf
from data.sample_data import seed_sample_data


@pytest.fixture
def test_env():
    """Sets up an isolated database and test instances."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(db_path=path)
    analyzer = ComplaintAnalyzer()
    priority_engine = PriorityEngine()
    similarity_engine = SimilarityEngine(similarity_threshold=0.30)
    router = DepartmentRouter()

    # Pre-seed realistic data
    seed_sample_data(db, force=True)

    yield {
        "db": db,
        "analyzer": analyzer,
        "priority_engine": priority_engine,
        "similarity_engine": similarity_engine,
        "router": router,
        "db_path": path
    }

    gc.collect()
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_full_complaint_lifecycle(test_env):
    db = test_env["db"]
    analyzer = test_env["analyzer"]
    prio_engine = test_env["priority_engine"]
    sim_engine = test_env["similarity_engine"]
    router = test_env["router"]

    # 1. New Complaint input
    title = "Three ceiling fans not working in EEE Lab 2 and sparking"
    desc = "Three ceiling fans stopped in EEE Lab 2 and there is sparking from the regulator. High heat in class."
    loc = "EEE Lab 2"
    name = "Dr. Vikram Patel"
    email = "vikram.patel@institution.edu"

    # 2. NLP Analysis
    nlp_res = analyzer.analyze(title, desc)
    assert nlp_res["category"] == "Electrical"
    assert "Fan" in nlp_res["subcategory"] or "Wiring" in nlp_res["subcategory"]

    # 3. Priority Evaluation
    prio_res = prio_engine.evaluate(title, desc, category=nlp_res["category"])
    assert prio_res["priority"] in ["Critical", "High"]

    # 4. Department Routing
    routing_res = router.route(category=nlp_res["category"], subcategory=nlp_res["subcategory"])
    assert "Electrical" in routing_res["department"]

    # 5. TF-IDF Similarity Check
    existing_corpus = db.get_complaints_for_similarity()
    sim_res = sim_engine.find_similar(title, desc, existing_corpus, new_location=loc)
    assert sim_res["has_similar"] is True
    assert sim_res["similar_count"] >= 1

    # 6. Database Insertion
    new_data = {
        "name": name,
        "email": email,
        "location": loc,
        "title": title,
        "description": desc,
        "category": nlp_res["category"],
        "subcategory": nlp_res["subcategory"],
        "priority": prio_res["priority"],
        "priority_reason": prio_res["primary_reason"],
        "department": routing_res["department"],
        "status": "Pending",
        "similar_count": sim_res["similar_count"],
        "top_similar_id": sim_res["top_complaint_id"],
        "top_similarity_score": sim_res["top_score"]
    }
    complaint_id = db.insert_complaint(new_data)
    assert complaint_id.startswith("CP-")

    # 7. Status Workflow: Pending -> In Progress -> Resolved
    db.update_complaint_status(
        complaint_id=complaint_id,
        new_status="In Progress",
        changed_by="Technician Rahul",
        comment="Regulator wire isolated."
    )
    db.update_complaint_status(
        complaint_id=complaint_id,
        new_status="Resolved",
        changed_by="Technician Rahul",
        comment="Replaced faulty regulator and tested fans."
    )

    complaint = db.get_complaint(complaint_id)
    history = db.get_status_history(complaint_id)
    assert complaint["status"] == "Resolved"
    assert complaint["resolved_at"] is not None
    assert len(history) == 3

    # 8. Report Generation (PDF bytes)
    docket_pdf = create_complaint_docket_pdf(complaint, history)
    assert isinstance(docket_pdf, bytes)
    assert len(docket_pdf) > 1000  # PDF contains valid structured content

    kpis = db.get_kpis()
    exec_pdf = create_summary_analytics_pdf(
        kpis=kpis,
        category_df=None,
        priority_df=None,
        hotspots={"top_category": "Electrical", "top_category_count": 5}
    )
    assert isinstance(exec_pdf, bytes)
    assert len(exec_pdf) > 1000
