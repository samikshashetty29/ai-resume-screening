"""Tests for the improved resume draft and its PDF."""

from pathlib import Path

from src.pdf_parser import extract_text_from_pdf
from src.resume_builder import (build_resume_draft, job_wording, resume_pdf,
                                unfilled_placeholders)
from src.skill_extractor import compare_skills
from src.text_preprocessing import clean_text
from tests.test_suggestions import RESUME_PDF, SAMPLES, run_app

RESUME = """Asha Rao
asha@example.com
SKILLS
Python, JS, Docker, Photography
EXPERIENCE
Analyst, Metro Bank (2022 - present)
- Was responsible for cleaning customer data.
- Wrote SQL reports for 12 branch managers.
EDUCATION
B.Sc. Statistics, 2022
"""
JOB = """Job title: Data Analyst
We need 2+ years of experience. Required: Python, SQL and JavaScript.
Nice to have: Tableau and Git.
"""


def draft(resume=RESUME, job=JOB, confirmed=()):
    skills = compare_skills(clean_text(resume), clean_text(job))
    return build_resume_draft(resume, job, skills, confirmed)


def test_adds_a_summary_aimed_at_the_job():
    text = draft()
    assert text.index("SUMMARY") < text.index("SKILLS") < text.index("EXPERIENCE")
    assert "Seeking a Data Analyst role, bringing experience in JavaScript, Python and SQL." in text


def test_job_skills_come_first_in_the_jobs_wording():
    text = draft()
    key_line = next(line for line in text.splitlines() if line.startswith("Key skills:"))
    assert "JavaScript" in key_line and "JS" not in key_line
    assert "Other skills: Docker, Photography" in text


def test_missing_skills_are_added_only_when_confirmed():
    assert "Tableau" not in draft()
    text = draft(confirmed=["tableau"])
    assert "Tableau" in text.split("EXPERIENCE")[0]
    assert "[Show where you used Tableau: what you did and the result]" in text


def test_keeps_the_original_text_and_adds_reminders():
    text = draft()
    for line in ("Asha Rao", "Analyst, Metro Bank (2022 - present)", "B.Sc. Statistics, 2022"):
        assert line in text
    assert "cleaning customer data. [reword starting with an action verb" in text
    assert "for 12 branch managers." in text and "managers. [" not in text


def test_realistic_resume_labels_wrapping_and_bullets():
    resume = extract_text_from_pdf(
        (SAMPLES / "realistic_resumes" / "ishita_rao_data_analyst.pdf").read_bytes())
    text = draft(resume, (SAMPLES / "jobs" / "data_analyst.txt").read_text(), ["docker"])
    assert "Key skills: Python, SQL, Pandas" in text and "Languages:" not in text
    # The PDF wrapped this bullet over two lines; the draft joins it back up.
    assert "saving about 6 hours of manual work each week." in text
    assert "8%.\nJunior Data Analyst" in text
    assert "• [Show where you used Docker" in text


def test_mixed_columns_keep_the_text_below_a_note():
    resume = extract_text_from_pdf((SAMPLES / "resumes" / "two_column_kabir.pdf").read_bytes())
    text = draft(resume, (SAMPLES / "jobs" / "frontend_developer.txt").read_text())
    assert "couldn't be split into sections" in text
    assert resume.strip().splitlines()[0] in text


def test_placeholders_are_found():
    assert unfilled_placeholders("Built X [add a number] and [more]") == ["[add a number]", "[more]"]
    assert unfilled_placeholders("Built X for 40 users.") == []


def test_job_wording_falls_back_to_skill_name():
    assert job_wording("javascript", JOB) == "JavaScript"
    assert job_wording("docker", JOB) == "docker"


def test_pdf_can_be_read_back():
    text = draft() + "Café • “quotes” → done\n"
    pdf = resume_pdf(text)
    assert pdf.startswith(b"%PDF")
    extracted = extract_text_from_pdf(pdf)
    assert "Asha Rao" in extracted and "Cafe" in extracted and "SUMMARY" in extracted


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()
    assert not at.exception


def test_app_builds_a_resume_only_when_asked():
    at = run_app(RESUME_PDF, job_text=(SAMPLES / "jobs" / "data_analyst.txt").read_text())
    assert "Create an improved resume" in [s.value for s in at.subheader]
    assert not at.multiselect and not [t for t in at.text_area if "Priya Sharma" in t.value]

    click(at, "✨ Create an improved resume")
    editor = [t for t in at.text_area if "Priya Sharma" in t.value][0]
    assert "SUMMARY" in editor.value
    at.multiselect[0].select("tableau").run()
    assert not at.exception
    editor = [t for t in at.text_area if "Priya Sharma" in t.value][0]
    assert "[Show where you used Tableau" in editor.value
    assert any("reminder(s)" in w.value for w in at.warning)

    click(at, "Close the resume builder")
    assert not at.multiselect
    assert "✨ Create an improved resume" in [b.label for b in at.button]
