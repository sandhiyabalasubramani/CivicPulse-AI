"""
Unit tests for ComplaintAnalyzer and text processing utilities.
"""

import pytest
from modules.complaint_analyzer import ComplaintAnalyzer, get_analyzer
from modules.text_processing import clean_text, tokenize, extract_keywords


def test_clean_text_contractions_and_whitespace():
    raw = "The light isn't working and it's   very dark here!"
    cleaned = clean_text(raw)
    assert "is not" in cleaned
    assert "it is" in cleaned
    assert "  " not in cleaned


def test_tokenize_stopwords():
    raw = "Please kindly look into the broken fan in Room 101."
    tokens = tokenize(raw, remove_stopwords=True)
    assert "broken" in tokens
    assert "fan" in tokens
    assert "please" not in tokens
    assert "kindly" not in tokens


def test_category_classification_electrical():
    analyzer = get_analyzer()
    res = analyzer.analyze(
        title="Fan issue",
        description="Three ceiling fans are not rotating and switchboard is dead in EEE Lab 2."
    )
    assert res["category"] == "Electrical"
    assert "Fan" in res["subcategory"] or "Ventilation" in res["subcategory"]
    assert res["confidence"] > 0.3


def test_category_classification_water():
    analyzer = get_analyzer()
    res = analyzer.analyze(
        title="Tap broken",
        description="Major water pipe leakage and leaking faucet in 2nd floor restroom."
    )
    assert res["category"] == "Water & Plumbing"
    assert "Leakage" in res["subcategory"] or "Tap" in res["subcategory"]


def test_category_classification_network():
    analyzer = get_analyzer()
    res = analyzer.analyze(
        title="No wifi",
        description="Wi-Fi router is offline and ethernet internet cable is disconnected in library."
    )
    assert res["category"] == "Network & IT"
    assert "Wi-Fi" in res["subcategory"] or "Internet" in res["subcategory"]


def test_keyword_extraction():
    analyzer = get_analyzer()
    res = analyzer.analyze(
        title="Air conditioner failure",
        description="The AC cooling unit stopped working in Server Room."
    )
    assert len(res["keywords"]) > 0
