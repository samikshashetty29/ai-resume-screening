# AI-Based Resume Screening and Job Matching System

A local Streamlit app that compares a PDF resume with a job description using
TF-IDF cosine similarity, a keyword skill dictionary with synonyms, and an optional
local AI model that compares meaning. See `IMPLEMENT.md` for
the full architecture.

> The scores measure how similar the texts are. They are **not** a hiring
> probability and should assist, not replace, human review.

## Setup (Windows)

```bash
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

On macOS/Linux use `python3 -m venv .venv` and `source .venv/bin/activate`.

Open the URL shown in the terminal (usually http://localhost:8501).

## Features

- **Overall match level** (Strong / Partial / Weak) with the reasons and a suggested
  next step. It describes how well the resume matches the job description, not the
  person's ability. Thresholds are in `src/verdict.py`.
- **Three scores**, each shown as a gauge:
  - *Text similarity* – TF-IDF cosine similarity (word overlap).
  - *Skill match* – the share of the job's skills found in the resume.
  - *Meaning similarity* – uses the local `all-MiniLM-L6-v2` model, so
    "built neural networks" can match "deep learning". The model (about 90 MB)
    is downloaded on first use, then runs offline. This is optional: without
    `sentence-transformers` installed, the checkbox is disabled.
- **Skill dictionary** for tech, marketing, HR, finance, design and soft skills,
  with **synonyms** (e.g. JS → JavaScript, K8s → Kubernetes, NLP → natural
  language processing). Edit `SKILL_CATEGORIES` and `SYNONYMS` in
  `src/skill_extractor.py`.
- **Chart** of matched vs not-detected job skills by category.
- **Keyword highlighting**: the resume and job description are shown side by side with
  matched skills and skills not detected marked, including synonyms.
- **Top shared keywords chart**: the words adding most to the text similarity score.
- **Job description as text or PDF**: paste it, or upload a text-based PDF.
- **Suggestions to improve the resume for this job**, ranked by importance. They use
  the job's own wording to separate required skills from optional ones, and flag:
  skills not found, skills listed but not shown in experience, different wording,
  years of experience, education, the summary, repeated keywords, and bullets without
  numbers. They run locally and are rule-based, so no AI service sees your resume.
  Only add what is true of your experience. Rules are in `src/suggestions.py`.
- **Downloadable text report** with all scores, skills and suggestions.

## Usage

1. Upload a text-based PDF resume.
2. Paste the job description or upload it as a PDF (at least 15 words).
3. Click **Analyze Resume**.
4. Review the three scores, the skills chart, matched skills, skills not detected,
   and the suggestions for improving the resume.
5. Click **Download report (.txt)** to save the results.

## Project structure

```text
app.py                    Streamlit UI and validation
src/pdf_parser.py         PDF text extraction (pypdf)
src/text_preprocessing.py Text cleaning
src/skill_extractor.py    Skill dictionary, synonyms and matching
src/semantic_matcher.py   Meaning-based similarity (optional AI model)
src/suggestions.py        Job-specific resume suggestions
src/highlighter.py        Skill highlighting in the resume and job text
src/charts.py             Plotly gauges and charts
src/matcher.py            TF-IDF + cosine similarity
src/report_generator.py   Plain-text report
tests/                    pytest unit tests
sample_data/              Sample resumes, job descriptions and invalid files (see its README)
```

## Running tests

```bash
python -m pytest
```

## Limitations

- Scanned/image-only PDFs are not supported (no OCR), for resumes or job descriptions.
- Suggestions come from text rules, so they can miss things or misread a resume.
  They are prompts to check, not instructions.
- Two-column PDFs may extract with their columns merged. The app detects this, warns
  about it and skips advice about sections, but it does not rebuild the columns.
- Skill detection only finds words in the dictionary; synonyms may be missed.
- TF-IDF is lexical and does not understand meaning; the AI score helps, but it
  is still a similarity measure, not a judgement of the candidate.
