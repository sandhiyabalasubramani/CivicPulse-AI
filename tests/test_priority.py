"""
Unit tests for PriorityEngine rule-based scoring and explainability.
"""

import pytest
from modules.priority_engine import get_priority_engine


def test_priority_critical_fire_and_sparking():
    engine = get_priority_engine()
    res = engine.evaluate(
        title="Sparks seen",
        description="There is visible sparking and exposed wire with electric shock danger.",
        category="Electrical"
    )
    assert res["priority"] == "Critical"
    assert "Electrical" in res["primary_reason"] or "Shock" in res["primary_reason"] or "Risk" in res["primary_reason"]
    assert res["score"] >= 90


def test_priority_high_multiple_equipment_disruption():
    engine = get_priority_engine()
    res = engine.evaluate(
        title="Fan issue",
        description="Three fans not working in EEE Lab 2 and students having difficulty during exam session.",
        category="Electrical"
    )
    assert res["priority"] == "High"
    assert res["score"] >= 70


def test_priority_low_cosmetic():
    engine = get_priority_engine()
    res = engine.evaluate(
        title="Marker request",
        description="Please replace the empty whiteboard marker and dirty window whenever possible.",
        category="Infrastructure & Civil"
    )
    assert res["priority"] == "Low"
    assert res["score"] <= 30


def test_priority_medium_default():
    engine = get_priority_engine()
    res = engine.evaluate(
        title="Window latch loose",
        description="The window latch in faculty room needs standard tightening.",
        category="Infrastructure & Civil"
    )
    assert res["priority"] == "Medium"
    assert res["score"] == 50
