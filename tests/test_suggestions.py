"""Tests for resume suggestions and for uploading the job description as a PDF."""

from datetime import datetime
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.pdf_parser import extract_text_from_pdf
from src.report_generator import generate_report
from src.skill_extractor import compare_skills, find_terms
from src.suggestions import (HIGH, LOW, MEDIUM, OPTIONAL, REQUIRED, MENTIONED, columns_are_mixed,
                             extract_job_title, parse_sections, skill_importance,
                             split_job_sentences, suggest_improvements)
from src.text_preprocessing import clean_text

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "sample_data"

RESUME = """Asha Rao - Data Analyst
SUMMARY
Data analyst with 2 years of experience in reporting.
SKILLS
Python, SQL, Docker
EXPERIENCE
- Wrote SQL reports for the sales team.
- Was responsible for cleaning customer data.
- Maintained the weekly dashboard files.
EDUCATION
B.Sc. Statistics, 2023
"""


def suggest(resume, job):
    return suggest_improvements(resume, job, compare_skills(clean_text(resume), clean_text(job)))


def by_title(suggestions, text):
    return [s for s in suggestions if text in s["title"]]


def full_text(suggestions):
    return " ".join(s["title"] + " " + s["detail"] for s in suggestions)


# --- Reading the job description --------------------------------------------

def test_wrapped_lines_are_joined_into_one_sentence():
    pairs = split_job_sentences("Strong Python is\nessential for this role. Next sentence.")
    assert pairs[0][0] == "Strong Python is essential for this role."


def test_headings_apply_to_their_bullets():
    job = "Requirements:\n- Python\n- SQL\n\nNice to have:\n- Docker\n"
    sentences = split_job_sentences(job)
    assert skill_importance("python", sentences)[0] == REQUIRED
    assert skill_importance("docker", sentences)[0] == OPTIONAL


@pytest.mark.parametrize("sentence, expected", [
    ("Python is required.", REQUIRED),
    ("You must know Python.", REQUIRED),
    ("Python is a plus.", OPTIONAL),
    ("Experience with Python is preferred.", OPTIONAL),
    ("You will use Python daily.", MENTIONED),
])
def test_skill_importance_from_wording(sentence, expected):
    assert skill_importance("python", split_job_sentences(sentence))[0] == expected


@pytest.mark.parametrize("job, title", [
    ("We are hiring a Data Analyst to join us.", "Data Analyst"),
    ("Job Title: Senior Web Developer\nMore text.", "Senior Web Developer"),
    ("Machine Learning Engineer wanted to build models.", "Machine Learning Engineer"),
    ("Join our friendly team and do great things.", None),
])
def test_extract_job_title(job, title):
    assert extract_job_title(job) == title


def test_parse_sections_finds_headings_in_any_case():
    sections = parse_sections("Name\nWork Experience:\n- Did things\nskills\nPython\n")
    assert "Did things" in sections["experience"]
    assert "Python" in sections["skills"]
    assert "Name" in sections["header"]


def test_find_terms_reports_the_words_used():
    assert find_terms("machine learning", "strong ml background") == {"ml"}


# --- Missing skills ---------------------------------------------------------

def test_required_skill_is_high_and_quotes_the_job():
    found = by_title(suggest(RESUME, "Kubernetes is required for this job."), "Required skill")
    assert found[0]["priority"] == HIGH
    assert "kubernetes" in found[0]["title"]
    assert "Kubernetes is required for this job." in found[0]["detail"]


def test_optional_skill_is_low():
    result = suggest(RESUME, "Kubernetes is a plus.")
    assert not by_title(result, "Required skill")
    assert by_title(result, "Optional skills")[0]["priority"] == LOW


def test_alternative_to_a_skill_the_resume_has_is_not_required():
    # The job accepts either one, and the resume has Docker.
    result = suggest(RESUME, "Required: experience with Docker or Kubernetes.")
    assert not by_title(result, "Required skill")
    assert "kubernetes" in by_title(result, "Optional skills")[0]["detail"]


def test_no_alternative_when_resume_has_neither():
    result = suggest(RESUME, "Required: experience with AWS or Azure.")
    assert len(by_title(result, "Required skill")) == 2


def test_many_required_skills_are_grouped():
    job = "Required: AWS, Azure, Kubernetes, Linux, Java, Rust, Kotlin."
    result = suggest(RESUME, job)
    assert len(by_title(result, "Required skill")) == 5
    assert len(by_title(result, "More required skills")) == 1


def test_soft_skill_advice_asks_for_an_example():
    detail = by_title(suggest(RESUME, "Leadership is essential."), "Required skill")[0]["detail"]
    assert "real example" in detail


def test_advice_never_tells_people_to_claim_skills_outright():
    text = full_text(suggest(RESUME, "Kubernetes is required. AWS is a plus."))
    assert "If you have used kubernetes" in text
    assert "Add any you have" in text


# --- Evidence and wording ---------------------------------------------------

def test_skill_only_listed_is_flagged():
    result = suggest(RESUME, "We need Python and SQL skills.")
    detail = by_title(result, "Prove the skills")[0]["detail"]
    assert "python" in detail
    assert "sql" not in detail  # used in an experience bullet


def test_no_experience_section_is_high():
    resume = "Asha\nSKILLS\nPython\nEDUCATION\nB.Sc.\n"
    found = by_title(suggest(resume, "We need Python."), "Add experience")
    assert found[0]["priority"] == HIGH


def test_no_sections_found_makes_no_claim_about_evidence():
    result = suggest("Asha knows Python and SQL and has built many things.", "We need Python.")
    assert not by_title(result, "Prove the skills")
    assert not by_title(result, "Add experience")


def test_different_wording_is_flagged():
    resume = RESUME.replace("Python, SQL", "Python, ML, SQL")
    detail = by_title(suggest(resume, "We need machine learning."), "same words")[0]["detail"]
    assert '"ml" → "machine learning"' in detail


def test_same_wording_is_not_flagged():
    assert not by_title(suggest(RESUME, "We need Python and SQL."), "same words")


def test_plural_is_not_a_wording_difference():
    resume = RESUME.replace("Python, SQL", "Python, REST APIs, SQL")
    assert not by_title(suggest(resume, "We build a REST API."), "same words")


# --- Summary, years, education, keywords, writing ---------------------------

def test_missing_summary_uses_the_job_title():
    resume = RESUME.replace("SUMMARY\nData analyst with 2 years of experience in reporting.\n", "")
    found = by_title(suggest(resume, "We are hiring a Data Engineer to work on Python."), "summary")
    assert found[0]["priority"] == MEDIUM
    assert "Data Engineer" in found[0]["detail"]


def test_job_title_missing_from_resume():
    found = by_title(suggest(RESUME, "We are hiring a Data Engineer to join."), "Mention")
    assert found[0]["title"] == 'Mention "Data Engineer" in your summary'


def test_experience_gap_is_flagged_without_overstating():
    detail = by_title(suggest(RESUME, "Needs 5+ years of experience in reporting."),
                      "experience gap")[0]["detail"]
    assert "5+" in detail and "says 2" in detail and "overstate" in detail


def test_enough_years_is_not_flagged():
    result = suggest(RESUME, "Needs 2 years of experience in reporting.")
    assert not by_title(result, "experience gap")


def test_years_not_stated_in_resume():
    resume = RESUME.replace("with 2 years of experience in", "working in")
    assert by_title(suggest(resume, "Needs 3-5 years of relevant experience."), "years of experience")


def test_missing_education_when_job_needs_a_degree():
    resume = RESUME.replace("EDUCATION\nB.Sc. Statistics, 2023\n", "")
    assert by_title(suggest(resume, "A bachelor degree is needed."), "Add your education")
    assert not by_title(suggest(RESUME, "A bachelor degree is needed."), "Add your education")


def test_repeated_keywords_ignore_word_forms_already_in_resume():
    resume = RESUME + "- Deployed reports.\n"
    job = "Deploy reports. Deploy often. Budget review. Budget planning. Budget again."
    detail = by_title(suggest(resume, job), "keywords")[0]["detail"]
    assert "budget" in detail
    assert "deploy" not in detail


def test_bullets_without_numbers():
    found = by_title(suggest(RESUME, "We need Python."), "numbers")
    assert "Wrote SQL reports for the sales team." in found[0]["detail"]


def test_bullets_with_numbers_are_not_flagged():
    resume = RESUME.replace("sales team", "12 sales teams").replace("customer data", "9000 records")
    assert not by_title(suggest(resume, "We need Python."), "numbers")


def test_weak_phrases_are_quoted():
    assert '"responsible for"' in by_title(suggest(RESUME, "We need Python."), "action verbs")[0]["detail"]


def test_sorted_by_priority():
    order = [s["priority"] for s in suggest(RESUME, "Kubernetes is required. AWS is a plus.")]
    assert order == sorted(order, key=[HIGH, MEDIUM, LOW].index)


def test_different_jobs_give_different_suggestions():
    assert full_text(suggest(RESUME, "Kubernetes is required.")) != \
        full_text(suggest(RESUME, "Payroll is required."))


# --- Sample data ------------------------------------------------------------

def test_sample_with_either_or_job_requirement():
    resume = extract_text_from_pdf((SAMPLES / "resumes" / "ml_engineer_meera.pdf").read_bytes())
    job = (SAMPLES / "jobs" / "ml_engineer.txt").read_text()
    result = suggest(resume, job)  # the job says "AWS or GCP" and the resume has AWS
    assert not [s for s in result if s["priority"] == HIGH and "gcp" in s["detail"]]


@pytest.mark.parametrize("job", sorted(p.stem for p in (SAMPLES / "jobs").glob("*.txt")))
def test_job_pdf_gives_same_suggestions_as_its_text(job):
    resume = extract_text_from_pdf((SAMPLES / "resumes" / "data_analyst_priya.pdf").read_bytes())
    from_text = suggest(resume, (SAMPLES / "jobs" / f"{job}.txt").read_text())
    job_pdf = extract_text_from_pdf((SAMPLES / "jobs" / f"{job}.pdf").read_bytes())
    assert [s["title"] for s in suggest(resume, job_pdf)] == [s["title"] for s in from_text]


# --- Two-column resumes -----------------------------------------------------

def sample(resume, job):
    text = extract_text_from_pdf((SAMPLES / "resumes" / f"{resume}.pdf").read_bytes())
    return suggest(text, (SAMPLES / "jobs" / f"{job}.txt").read_text())


def test_columns_stored_in_order_are_read_normally():
    text = extract_text_from_pdf((SAMPLES / "resumes" / "two_column_tanvi.pdf").read_bytes())
    assert not columns_are_mixed(text)
    assert {"skills", "summary", "experience", "projects"} <= set(parse_sections(text))
    result = sample("two_column_tanvi", "data_analyst")
    assert not by_title(result, "columns")
    assert by_title(result, "Prove the skills")


def test_merged_columns_are_detected():
    text = extract_text_from_pdf((SAMPLES / "resumes" / "two_column_kabir.pdf").read_bytes())
    assert columns_are_mixed(text)


def test_merged_columns_give_a_warning_not_false_claims():
    result = sample("two_column_kabir", "frontend_developer")
    assert by_title(result, "columns")[0]["priority"] == MEDIUM
    assert not by_title(result, "Add a short summary")  # the resume has one
    assert not by_title(result, "Add experience")
    assert not by_title(result, "Prove the skills")


def test_merged_columns_still_find_skills():
    text = extract_text_from_pdf((SAMPLES / "resumes" / "two_column_kabir.pdf").read_bytes())
    job = (SAMPLES / "jobs" / "frontend_developer.txt").read_text()
    matched = compare_skills(clean_text(text), clean_text(job))["matched_skills"]
    assert {"react", "typescript", "node.js", "rest api"} <= set(matched)


@pytest.mark.parametrize("path", sorted(p.stem for p in (SAMPLES / "resumes").glob("*.pdf")
                                        if not p.stem.endswith("kabir")))
def test_normal_layouts_are_not_called_mixed(path):
    text = extract_text_from_pdf((SAMPLES / "resumes" / f"{path}.pdf").read_bytes())
    assert not columns_are_mixed(text)


def test_full_line_headings_are_not_mixed():
    text = "PROFESSIONAL EXPERIENCE\n- Work\nTECHNICAL SKILLS\nPython\nWORK EXPERIENCE\n"
    assert not columns_are_mixed(text)


def test_one_or_two_found_headings_decide_section_claims():
    # Only one heading was recognised, so the missing summary can't be trusted.
    result = suggest("Asha\nSKILLS\nPython and SQL\n", "We are hiring a Data Engineer to join.")
    assert not by_title(result, "Add a short summary")


# --- Report -----------------------------------------------------------------

def report(suggestions):
    skills = {"matched_skills": [], "missing_skills": [], "skill_match": None}
    return generate_report("cv.pdf", 10.0, skills, datetime(2026, 1, 1), suggestions=suggestions)


def test_report_includes_suggestions():
    text = report([{"priority": HIGH, "category": "Skills", "title": "Add AWS", "detail": "Because."}])
    assert "[HIGH] Add AWS" in text and "Because." in text


def test_report_without_suggestions_has_no_section():
    assert "Suggestions to improve" not in report([])


# --- The app itself ---------------------------------------------------------

def run_app(resume=None, job_pdf=None, job_text=None):
    """Drive app.py the way a user would. Pass PDF bytes for uploads."""
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    at.checkbox[0].set_value(False).run()  # keep these tests offline
    if job_pdf is not None:
        at.radio[0].set_value("Upload PDF").run()
    if resume is not None:
        at.file_uploader[0].upload("resume.pdf", resume, "application/pdf").run()
    if job_pdf is not None and job_pdf is not False:
        at.file_uploader[1].upload("job.pdf", job_pdf, "application/pdf").run()
    if job_text is not None:
        at.text_area[0].set_value(job_text).run()
    at.button[0].click().run()
    assert not at.exception
    return at


def page_text(at):
    return " ".join(e.value for e in [*at.markdown, *at.subheader, *at.success, *at.error])


RESUME_PDF = (SAMPLES / "resumes" / "data_analyst_priya.pdf").read_bytes()


def test_app_analyzes_with_job_pdf():
    at = run_app(RESUME_PDF, job_pdf=(SAMPLES / "jobs" / "data_analyst.pdf").read_bytes())
    assert not at.error
    text = page_text(at)
    assert "How to improve this resume for this job" in text
    assert "Required skill not found: problem solving" in text


def test_app_still_analyzes_pasted_text():
    at = run_app(RESUME_PDF, job_text=(SAMPLES / "jobs" / "data_analyst.txt").read_text())
    assert not at.error
    assert "Required skill not found: problem solving" in page_text(at)


def test_app_asks_for_job_pdf_when_missing():
    at = run_app(RESUME_PDF, job_pdf=False)
    assert at.error[0].value == "Please upload the job description PDF."


@pytest.mark.parametrize("name", ["corrupt.pdf", "scanned_no_text.pdf", "password_protected.pdf"])
def test_app_reports_bad_job_pdf(name):
    at = run_app(RESUME_PDF, job_pdf=(SAMPLES / "invalid" / name).read_bytes())
    assert at.error[0].value.startswith("Job description PDF:")


def test_app_rejects_short_job_pdf():
    at = run_app(RESUME_PDF, job_pdf=_short_pdf())
    assert "too short" in at.error[0].value


def test_app_names_the_resume_in_resume_errors():
    at = run_app((SAMPLES / "invalid" / "corrupt.pdf").read_bytes(),
                 job_text=(SAMPLES / "jobs" / "data_analyst.txt").read_text())
    assert at.error[0].value.startswith("Resume PDF:")


def _short_pdf():
    import importlib.util

    spec = importlib.util.spec_from_file_location("make_samples", SAMPLES / "make_samples.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_pdf([["Too short to compare."]])
