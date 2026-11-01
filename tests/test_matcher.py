from datetime import datetime

import pytest

from src.matcher import calculate_similarity
from src.pdf_parser import PDFExtractionError, extract_text_from_pdf
from src.report_generator import generate_report


def test_identical_texts_score_100():
    text = "python developer with sql and machine learning experience"
    assert calculate_similarity(text, text) == pytest.approx(100.0)


def test_unrelated_texts_score_low():
    score = calculate_similarity("python sql pandas numpy", "chef cooking kitchen recipes")
    assert score == 0.0


def test_related_scores_higher_than_unrelated():
    job = "python developer sql machine learning"
    related = calculate_similarity("experienced python developer with sql", job)
    unrelated = calculate_similarity("experienced chef with pastry skills", job)
    assert related > unrelated


def test_stop_words_only_returns_zero():
    assert calculate_similarity("the and of", "a an the") == 0.0


def test_corrupt_pdf_raises():
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"this is not a pdf")


def test_empty_pdf_bytes_raises():
    with pytest.raises(PDFExtractionError):
        extract_text_from_pdf(b"")


def test_blank_pdf_raises_no_text():
    from io import BytesIO

    from pypdf import PdfWriter

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = BytesIO()
    writer.write(buf)
    with pytest.raises(PDFExtractionError, match="No selectable text"):
        extract_text_from_pdf(buf.getvalue())


def test_report_contents():
    skills = {"matched_skills": ["python"], "missing_skills": ["aws"]}
    report = generate_report("cv.pdf", 42.5, skills, datetime(2026, 1, 1, 9, 0, 0))
    assert "cv.pdf" in report
    assert "2026-01-01 09:00:00" in report
    assert "42.50%" in report
    assert "- python" in report and "- aws" in report
    assert "NOT a hiring probability" in report
