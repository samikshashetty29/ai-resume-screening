"""Tests for synonyms, skill-match score, categories, charts and the report."""

from datetime import datetime

from src.charts import score_gauge, skills_by_category_chart
from src.report_generator import generate_report
from src.skill_extractor import SKILLS, SYNONYMS, category_of, compare_skills, extract_skills
from src.text_preprocessing import clean_text


def skills_in(text):
    return extract_skills(clean_text(text))


# --- Synonyms --------------------------------------------------------------

def test_synonyms_map_to_main_skill_name():
    found = skills_in("Built JS apps with ReactJS and NodeJS on K8s, data in Postgres")
    assert {"javascript", "react", "node.js", "kubernetes", "postgresql"} <= found
    assert not {"js", "reactjs", "nodejs", "k8s", "postgres"} & found


def test_more_synonyms():
    found = skills_in("Strong in ML, NLP, sklearn and Amazon Web Services. Team player.")
    assert {"machine learning", "natural language processing", "scikit-learn",
            "aws", "teamwork"} <= found


def test_synonym_and_main_name_count_once():
    result = compare_skills(clean_text("Experience with NLP"),
                            clean_text("Natural Language Processing required"))
    assert result["matched_skills"] == ["natural language processing"]
    assert result["missing_skills"] == []


def test_synonyms_respect_word_boundaries():
    # "ml" must not match inside "html"; "ts" not inside "results".
    found = skills_in("HTML pages with great results")
    assert "machine learning" not in found
    assert "typescript" not in found


def test_every_synonym_points_to_a_known_skill():
    assert set(SYNONYMS) <= set(SKILLS)


# --- Non-tech skills and categories ---------------------------------------

def test_non_tech_skills_detected():
    found = skills_in("SEO, copywriting, payroll, budgeting, Figma and public speaking")
    assert {"seo", "copywriting", "payroll", "budgeting", "figma", "public speaking"} <= found


def test_categories():
    assert category_of("python") == "Programming"
    assert category_of("payroll") == "HR"
    assert category_of("copywriting") == "Marketing"
    assert category_of("not a skill") == "Other"


def test_no_duplicate_skills():
    assert len(SKILLS) == len(set(SKILLS))


# --- Skill-match score ----------------------------------------------------

def test_skill_match_percentage():
    result = compare_skills(clean_text("python sql"), clean_text("python sql docker aws"))
    assert result["skill_match"] == 50.0


def test_skill_match_none_without_job_skills():
    assert compare_skills(clean_text("python"), clean_text("drive a van"))["skill_match"] is None


# --- Charts ---------------------------------------------------------------

def test_gauge_figures():
    assert score_gauge(42.0, "x").data[0].value == 42.0
    assert score_gauge(None, "x").data[0].value == 0


def test_category_chart_counts():
    fig = skills_by_category_chart(["python", "sql", "payroll"], ["docker"])
    matched, missing = fig.data
    counts = dict(zip(matched.y, matched.x))
    assert counts == {"Data & ML": 1, "DevOps & Tools": 0, "HR": 1, "Programming": 1}
    assert dict(zip(missing.y, missing.x))["DevOps & Tools"] == 1


# --- Report ---------------------------------------------------------------

def test_report_includes_new_scores():
    skills = {"matched_skills": ["python"], "missing_skills": ["aws"], "skill_match": 50.0}
    report = generate_report("cv.pdf", 30.0, skills, datetime(2026, 1, 1), semantic=61.25)
    assert "Skill match:          50.00%  (1 of 2 job skills)" in report
    assert "Semantic similarity:  61.25%" in report


def test_report_without_semantic_or_skills():
    skills = {"matched_skills": [], "missing_skills": [], "skill_match": None}
    report = generate_report("cv.pdf", 1.0, skills)
    assert "Skill match:          n/a" in report
    assert "Semantic similarity:  n/a" in report
