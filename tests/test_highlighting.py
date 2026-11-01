"""Tests for skill highlighting and the top shared keywords."""

import html
import re
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.charts import top_keywords_chart
from src.highlighter import highlight_text, legend
from src.matcher import calculate_similarity, top_shared_keywords
from src.skill_extractor import compare_skills, find_spans
from src.text_preprocessing import clean_text

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "sample_data"


def marks(html_text):
    return html_text.count("<mark")


def test_marks_matched_and_missing_differently():
    out = highlight_text("Python and Docker", ["python"], ["docker"])
    assert marks(out) == 2
    assert ">Python</mark>" in out and ">Docker</mark>" in out
    assert "solid" in out and "dashed" in out


def test_keeps_original_capitals_and_marks_every_mention():
    out = highlight_text("PYTHON then python", ["python"])
    assert marks(out) == 2 and ">PYTHON</mark>" in out and ">python</mark>" in out


def test_marks_synonyms():
    assert ">ML</mark>" in highlight_text("Strong ML skills", ["machine learning"])


def test_skill_wrapped_across_lines_is_marked():
    assert marks(highlight_text("Machine\nlearning work", ["machine learning"])) == 1
    assert find_spans("machine learning", "machine\n  learning") == [(0, 18)]


def test_java_not_marked_inside_javascript():
    assert marks(highlight_text("JavaScript", ["java"])) == 0


def test_overlapping_matches_are_marked_once():
    # "social media" is a synonym of a skill; "social media marketing" is the longer match.
    out = highlight_text("social media marketing", ["social media marketing", "digital marketing"])
    assert marks(out) == 1


def test_uploaded_text_cannot_inject_html():
    out = highlight_text('<script>alert(1)</script> "Python" & <b>SQL</b>', ["python", "sql"])
    assert "<script>" not in out and "<b>" not in out
    assert "&lt;script&gt;" in out and "&amp;" in out
    assert marks(out) == 2


def test_text_is_unchanged_apart_from_marks():
    text = "Line one: C++ & Python\n\n  Indented <tag> line"
    out = highlight_text(text, ["c++", "python"])
    without_tags = re.sub(r"<[^>]+>", "", out)
    assert html.unescape(without_tags) == text


def test_no_skills_gives_plain_text():
    assert marks(highlight_text("Nothing here", [])) == 0


def test_legend_covers_both_kinds():
    assert marks(legend()) == 2
    assert "Not detected" in legend()


# --- Top shared keywords ----------------------------------------------------

RESUME = "python developer building sql reports and python dashboards for finance teams"
JOB = "python developer needed for sql reports in a retail company"


def test_points_add_up_to_the_similarity_score():
    keywords = top_shared_keywords(RESUME, JOB, limit=1000)
    assert sum(p for _, p in keywords) == pytest.approx(calculate_similarity(RESUME, JOB), abs=0.01)


def test_only_shared_terms_are_returned_biggest_first():
    keywords = top_shared_keywords(RESUME, JOB)
    terms = [t for t, _ in keywords]
    assert "python" in terms and "finance" not in terms and "retail" not in terms
    points = [p for _, p in keywords]
    assert points == sorted(points, reverse=True)


def test_limit():
    assert len(top_shared_keywords(RESUME, JOB, limit=2)) == 2


@pytest.mark.parametrize("resume, job", [("", "python"), ("the and of", "a an the")])
def test_no_keywords_for_unusable_text(resume, job):
    assert top_shared_keywords(resume, job) == []


def test_nothing_shared():
    assert top_shared_keywords("chef cooking", "python sql") == []


def test_keyword_chart_keeps_order():
    fig = top_keywords_chart([("python", 5.0), ("sql", 2.0)])
    assert list(fig.data[0].y) == ["python", "sql"]
    assert fig.layout.yaxis.autorange == "reversed"


# --- Text wrapped in a PDF --------------------------------------------------

def test_skill_matching_on_cleaned_text_still_works():
    result = compare_skills(clean_text("Machine\nLearning"), clean_text("machine learning"))
    assert result["matched_skills"] == ["machine learning"]


# --- The app itself ---------------------------------------------------------

def run_app(resume_name, job_name):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    if not at.checkbox[0].disabled:  # keep these tests offline
        at.checkbox[0].set_value(False).run()
    at.file_uploader[0].upload("resume.pdf", (SAMPLES / "resumes" / resume_name).read_bytes(),
                               "application/pdf").run()
    at.text_area[0].set_value((SAMPLES / "jobs" / job_name).read_text()).run()
    at.button[0].click().run()
    assert not at.exception  # a "Weak match" verdict also shows as a red box, so errors are allowed
    return at


def test_app_shows_highlighted_texts():
    at = run_app("data_analyst_priya.pdf", "data_analyst.txt")
    assert "See the match in the text" in [s.value for s in at.subheader]
    blocks = [b.proto.body for b in at.get("html")]
    assert len(blocks) == 3  # legend, resume, job
    assert "dashed" not in blocks[1]        # a resume has no "not detected" skills
    assert ">Python</mark>" in blocks[1]
    assert ">Tableau</mark>" in blocks[2]   # not detected, marked in the job


def test_app_handles_job_with_no_known_skills():
    at = run_app("marketing_karan.pdf", "delivery_driver.txt")
    assert "See the match in the text" in [s.value for s in at.subheader]
