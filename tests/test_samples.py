"""End-to-end checks on the files in sample_data/ (regenerate with sample_data/make_samples.py)."""

from pathlib import Path

import pytest

from src.matcher import calculate_similarity
from src.pdf_parser import PDFExtractionError, extract_text_from_pdf
from src.skill_extractor import compare_skills
from src.text_preprocessing import clean_text

SAMPLES = Path(__file__).resolve().parent.parent / "sample_data"
RESUMES = SAMPLES / "resumes"
JOBS = SAMPLES / "jobs"
INVALID = SAMPLES / "invalid"

# Each resume and the job it was written for.
MATCHING_PAIRS = {
    "data_analyst_priya.pdf": "data_analyst.txt",
    "web_developer_arjun.pdf": "frontend_developer.txt",
    "ml_engineer_meera.pdf": "ml_engineer.txt",
    "java_backend_rahul.pdf": "java_backend.txt",
    "marketing_karan.pdf": "marketing_executive.txt",
    "hr_coordinator_neha.pdf": "hr_coordinator.txt",
    "finance_analyst_vikram.pdf": "finance_analyst.txt",
    "ui_ux_designer_ananya.pdf": "ui_ux_designer.txt",
    "devops_engineer_farhan.pdf": "devops_engineer.txt",
    "android_developer_diya.pdf": "android_developer.txt",
    "project_manager_rohan.pdf": "project_manager.txt",
    "two_column_tanvi.pdf": "data_analyst.txt",
    "two_column_kabir.pdf": "frontend_developer.txt",
}
# Jobs long enough to pass the app's validation.
FULL_JOBS = ["data_analyst.txt", "frontend_developer.txt", "ml_engineer.txt",
             "java_backend.txt", "hr_coordinator.txt", "marketing_executive.txt",
             "delivery_driver.txt", "finance_analyst.txt", "ui_ux_designer.txt",
             "devops_engineer.txt", "android_developer.txt", "project_manager.txt"]


def resume_text(name):
    return clean_text(extract_text_from_pdf((RESUMES / name).read_bytes()))


def job_text(name):
    return clean_text((JOBS / name).read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", sorted(p.name for p in RESUMES.glob("*.pdf")))
def test_every_sample_resume_extracts_text(name):
    assert len(resume_text(name).split()) > 30


def test_text_from_every_page_is_extracted():
    text = resume_text("java_backend_rahul.pdf")
    assert "finserve" in text      # page 1
    assert "cloudnine" in text     # page 2


@pytest.mark.parametrize("resume,job", MATCHING_PAIRS.items())
def test_resume_scores_highest_on_its_own_job(resume, job):
    text = resume_text(resume)
    own = calculate_similarity(text, job_text(job))
    others = [calculate_similarity(text, job_text(j)) for j in FULL_JOBS if j != job]
    assert own > max(others)


@pytest.mark.parametrize("resume,job", MATCHING_PAIRS.items())
def test_matching_pair_shares_most_job_skills(resume, job):
    result = compare_skills(resume_text(resume), job_text(job))
    assert len(result["matched_skills"]) >= len(result["missing_skills"])


def test_data_analyst_expected_skills():
    result = compare_skills(resume_text("data_analyst_priya.pdf"), job_text("data_analyst.txt"))
    assert {"python", "sql", "pandas", "power bi"} <= set(result["matched_skills"])
    assert {"tableau", "docker", "aws"} <= set(result["missing_skills"])


def test_web_developer_skills_with_symbols():
    result = compare_skills(resume_text("web_developer_arjun.pdf"), job_text("frontend_developer.txt"))
    assert {"node.js", "react", "typescript", "rest api"} <= set(result["matched_skills"])
    assert "graphql" in result["missing_skills"]


def test_fresher_cpp_not_counted_as_c_only():
    skills = compare_skills(resume_text("fresher_sneha.pdf"), "")["resume_skills"]
    assert {"c", "c++", "python"} <= set(skills)


def test_marketing_resume_scores_low_on_tech_jobs():
    text = resume_text("marketing_karan.pdf")
    for job in FULL_JOBS:
        if job == "marketing_executive.txt":
            continue
        assert calculate_similarity(text, job_text(job)) < 5


def test_job_without_known_skills():
    result = compare_skills(resume_text("data_analyst_priya.pdf"), job_text("delivery_driver.txt"))
    assert result["job_skills"] == []
    assert result["missing_skills"] == []


def test_too_short_job_fails_word_limit():
    # app.py requires at least 15 words in the job description.
    assert len((JOBS / "too_short.txt").read_text(encoding="utf-8").split()) < 15


@pytest.mark.parametrize("name,message", [
    ("scanned_no_text.pdf", "No selectable text"),
    ("corrupt.pdf", "could not be read"),
    ("not_really_a_pdf.pdf", "could not be read"),
    ("password_protected.pdf", "password-protected"),
])
def test_invalid_files_give_clear_errors(name, message):
    with pytest.raises(PDFExtractionError, match=message):
        extract_text_from_pdf((INVALID / name).read_bytes())


def test_marketing_resume_matches_marketing_skills():
    result = compare_skills(resume_text("marketing_karan.pdf"), job_text("marketing_executive.txt"))
    assert {"brand strategy", "social media marketing", "public speaking"} <= set(result["matched_skills"])
    assert result["missing_skills"] == ["excel"]
    assert result["skill_match"] > 80
