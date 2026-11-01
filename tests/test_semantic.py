"""Tests for the meaning-based matcher. Skipped if the model is not installed/downloadable."""

from pathlib import Path

import pytest

from src.pdf_parser import extract_text_from_pdf
from src.semantic_matcher import chunk_text, is_available, load_model, semantic_similarity

SAMPLES = Path(__file__).resolve().parent.parent / "sample_data"


def test_chunk_text_keeps_sentences_and_limits_size():
    text = "One two three. Four five six. " * 30
    chunks = chunk_text(text, max_words=10)
    assert all(len(c.split()) <= 10 for c in chunks)
    assert " ".join(chunks).split() == text.split()


def test_chunk_text_empty():
    assert chunk_text("") == []


@pytest.fixture(scope="module")
def model():
    if not is_available():
        pytest.skip("sentence-transformers is not installed")
    try:
        return load_model()
    except Exception as exc:  # e.g. no internet on first download
        pytest.skip(f"model could not be loaded: {exc}")


def test_paraphrase_scores_higher_than_unrelated(model):
    job = "Experience with deep learning and computer vision."
    paraphrase = "Built neural networks that recognise objects in photos."
    unrelated = "Planned weddings and managed catering for large events."
    assert semantic_similarity(paraphrase, job, model) > semantic_similarity(unrelated, job, model) + 15


def test_identical_text_scores_about_100(model):
    text = "Python developer with SQL experience."
    assert semantic_similarity(text, text, model) > 99


def test_sample_resume_matches_its_job_best(model):
    meera = extract_text_from_pdf((SAMPLES / "resumes" / "ml_engineer_meera.pdf").read_bytes())
    karan = extract_text_from_pdf((SAMPLES / "resumes" / "marketing_karan.pdf").read_bytes())
    ml_job = (SAMPLES / "jobs" / "ml_engineer.txt").read_text(encoding="utf-8")
    assert semantic_similarity(meera, ml_job, model) > semantic_similarity(karan, ml_job, model)
