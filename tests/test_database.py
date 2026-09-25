"""
Unit tests for DatabaseManager SQLite operations and status audit logging.
"""

import os
import tempfile
import pytest
from database.database import DatabaseManager


import gc

@pytest.fixture
def temp_db():
    """Creates an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(db_path=path)
    yield db
    gc.collect()
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError:
        pass


def test_insert_and_get_complaint(temp_db):
    data = {
        "name": "Test User",
        "email": "test@domain.edu",
        "location": "Room 101",
        "title": "Air Conditioner Leaking",
        "description": "AC is dropping water continuously on the carpet.",
        "category": "Electrical",
        "subcategory": "Air Conditioner & HVAC",
        "priority": "High",
        "priority_reason": "Equipment water dripping",
        "department": "Electrical Maintenance Division",
        "status": "Pending"
    }

    cid = temp_db.insert_complaint(data)
    assert cid.startswith("CP-")

    retrieved = temp_db.get_complaint(cid)
    assert retrieved is not None
    assert retrieved["complaint_id"] == cid
    assert retrieved["name"] == "Test User"
    assert retrieved["priority"] == "High"
    assert retrieved["status"] == "Pending"


def test_status_update_and_history(temp_db):
    data = {
        "name": "Prof. Alan",
        "email": "alan@domain.edu",
        "location": "Lab 4",
        "title": "Broken bench",
        "description": "Desk leg broken in front row.",
        "category": "Infrastructure & Civil",
        "subcategory": "Furniture & Desks",
        "priority": "Low",
        "priority_reason": "Non-urgent furniture",
        "department": "Civil Works & Structural Maintenance",
        "status": "Pending"
    }

    cid = temp_db.insert_complaint(data)
    
    # Update status to In Progress
    success = temp_db.update_complaint_status(
        complaint_id=cid,
        new_status="In Progress",
        changed_by="Carpenter Joe",
        comment="Ordered wood joint spare part."
    )
    assert success is True

    # Update status to Resolved
    success2 = temp_db.update_complaint_status(
        complaint_id=cid,
        new_status="Resolved",
        changed_by="Carpenter Joe",
        comment="Bench repaired and stabilized."
    )
    assert success2 is True

    # Verify complaint record and resolved_at
    updated = temp_db.get_complaint(cid)
    assert updated["status"] == "Resolved"
    assert updated["resolved_at"] is not None

    # Verify history logs
    history = temp_db.get_status_history(cid)
    assert len(history) == 3  # Initial + In Progress + Resolved
    assert history[1]["new_status"] == "In Progress"
    assert history[2]["new_status"] == "Resolved"


def test_kpis_calculation(temp_db):
    temp_db.insert_complaint({
        "name": "User 1",
        "email": "u1@test.com",
        "location": "Loc A",
        "title": "Title 1",
        "description": "Desc 1",
        "category": "Electrical",
        "priority": "Critical",
        "status": "Pending"
    })
    temp_db.insert_complaint({
        "name": "User 2",
        "email": "u2@test.com",
        "location": "Loc B",
        "title": "Title 2",
        "description": "Desc 2",
        "category": "Water & Plumbing",
        "priority": "Medium",
        "status": "Resolved"
    })

    kpis = temp_db.get_kpis()
    assert kpis["total"] == 2
    assert kpis["pending"] == 1
    assert kpis["resolved"] == 1
    assert kpis["critical_priority"] == 1
