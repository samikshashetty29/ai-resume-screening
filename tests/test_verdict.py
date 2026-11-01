"""Tests for the overall match level."""

from pathlib import Path

import pytest

from src.matcher import calculate_similarity
from src.pdf_parser import extract_text_from_pdf
from src.report_generator import generate_report
from src.skill_extractor import compare_skills
from src.text_preprocessing import clean_text
from src.verdict import assess_match

SAMPLES = Path(__file__).resolve().parent.parent / "sample_data"


def skills(matched, missing):
    total = len(matched) + len(missing)
    return {"matched_skills": matched, "missing_skills": missing,
            "skill_match": len(matched) / total * 100 if total else None}


def test_strong_needs_skills_and_meaning():
    assert assess_match(25, skills(["a", "b", "c", "d"], []), semantic=60)["level"] == "strong"
    # High skill match but low meaning similarity is only partial.
    assert assess_match(25, skills(["a", "b", "c", "d"], []), semantic=30)["level"] == "partial"


def test_tfidf_used_when_meaning_not_computed():
    assert assess_match(22, skills(["a", "b", "c", "d"], []))["level"] == "strong"
    assert assess_match(10, skills(["a", "b", "c", "d"], []))["level"] == "partial"


def test_weak_match():
    v = assess_match(3, skills(["a"], ["b", "c", "d", "e"]), semantic=20)
    assert v["level"] == "weak"
    assert v["label"] == "Weak match"


def test_no_job_skills_is_never_strong():
    v = assess_match(40, skills([], []), semantic=90)
    assert v["level"] == "partial"
    assert any("could not be compared" in r for r in v["reasons"])


def test_reasons_list_missing_skills_and_scores():
    v = assess_match(21.5, skills(["python"], ["aws", "docker"]), semantic=40.6)
    text = " ".join(v["reasons"])
    assert "Found 1 of 3 job skills" in text
    assert "aws, docker" in text
    assert "Meaning similarity is 40.6%" in text
    assert "not a judgement" in v["disclaimer"]


def test_long_missing_list_is_shortened():
    v = assess_match(5, skills([], [f"s{i}" for i in range(10)]))
    assert "and 4 more" in " ".join(v["reasons"])


def test_report_includes_match_level():
    report = generate_report("cv.pdf", 25, skills(["a", "b", "c", "d"], []), semantic=60)
    assert "Overall match:        Strong match" in report
    assert "not a judgement" in report


# Expected levels for the sample files, using TF-IDF + skills only (no AI model needed).
@pytest.mark.parametrize("resume,job,expected", [
    ("ml_engineer_meera", "ml_engineer", "strong"),
    ("java_backend_rahul", "java_backend", "strong"),
    ("marketing_karan", "marketing_executive", "strong"),
    ("data_analyst_priya", "data_analyst", "partial"),
    ("web_developer_arjun", "frontend_developer", "partial"),
    ("fresher_sneha", "frontend_developer", "weak"),
    ("marketing_karan", "ml_engineer", "weak"),
    ("data_analyst_priya", "delivery_driver", "weak"),
])
def test_sample_match_levels(resume, job, expected):
    raw = extract_text_from_pdf((SAMPLES / "resumes" / f"{resume}.pdf").read_bytes())
    r = clean_text(raw)
    j = clean_text((SAMPLES / "jobs" / f"{job}.txt").read_text(encoding="utf-8"))
    assert assess_match(calculate_similarity(r, j), compare_skills(r, j))["level"] == expected
