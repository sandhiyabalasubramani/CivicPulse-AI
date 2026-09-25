"""
Unit tests for SimilarityEngine (TF-IDF & Cosine Similarity).
"""

import pytest
from modules.similarity_engine import SimilarityEngine, get_similarity_engine


def test_similarity_detection_positive_pair():
    engine = SimilarityEngine(similarity_threshold=0.30)
    
    existing = [
        {
            "complaint_id": "CP-2026-0001",
            "title": "Three fans are not working in EEE Lab 2",
            "description": "Ceiling fans are stopped and students having difficulty in EEE Lab 2.",
            "location": "EEE Lab 2",
            "category": "Electrical",
            "status": "Pending",
            "priority": "High",
            "created_at": "2026-09-20 10:00:00"
        },
        {
            "complaint_id": "CP-2026-0002",
            "title": "Water leakage in 3rd floor washroom",
            "description": "Tap is leaking and water overflowing on floor.",
            "location": "Washroom Floor 3",
            "category": "Water & Plumbing",
            "status": "Resolved",
            "priority": "Medium",
            "created_at": "2026-09-21 11:00:00"
        }
    ]

    new_title = "Two ceiling fans stopped working in EEE Lab 2"
    new_desc = "Fans in EEE Lab 2 are not rotating during class."
    new_loc = "EEE Lab 2"

    result = engine.find_similar(
        new_title=new_title,
        new_description=new_desc,
        existing_complaints=existing,
        new_location=new_loc
    )

    assert result["has_similar"] is True
    assert result["similar_count"] >= 1
    assert result["top_complaint_id"] == "CP-2026-0001"
    assert result["top_score"] > 0.40
    assert result["matches"][0]["label"] == "Potentially similar complaint"


def test_similarity_empty_existing():
    engine = get_similarity_engine()
    result = engine.find_similar(
        new_title="Projector bulb fused",
        new_description="Projector not showing display in Room 101.",
        existing_complaints=[]
    )
    assert result["has_similar"] is False
    assert result["similar_count"] == 0
    assert result["matches"] == []
