# AI-Based Resume Screening and Job Matching System
## Implementation Plan and Project Architecture

## 1. Project Overview

**Project name:** AI-Based Resume Screening and Job Matching System

**Purpose:** Build a local web application that accepts a PDF resume and a job description, extracts and compares their text, identifies relevant skills, and presents a screening report.

**Primary users:** Students, job seekers, and recruiters who want an initial, explainable comparison between resume content and job requirements.

**Important limitation:** The similarity score is a text-similarity measure. It is not a hiring probability, a validated measure of candidate quality, or a substitute for human review.

## 2. Goals and Scope

### Goals
- Upload a resume in PDF format.
- Extract selectable text from the PDF.
- Accept a job description as text.
- Normalize text before comparison.
- Calculate TF-IDF vectors and cosine similarity using scikit-learn.
- Detect skills using a configurable keyword dictionary.
- Show matched skills and job-description skills not detected in the resume.
- Display a readable result page and allow a text report to be downloaded.
- Run locally without a paid API or GPU.

### In scope for the first version
- One resume per analysis.
- One job description per analysis.
- Text-based PDF files.
- TF-IDF and cosine similarity.
- Dictionary-based skill extraction.
- Streamlit user interface.

### Out of scope for the first version
- Automatic hiring decisions.
- Candidate ranking across many resumes.
- OCR for scanned/image-only PDFs.
- Login, database, cloud deployment, and recruiter accounts.
- Advanced semantic models or large language models.

## 3. High-Level Architecture

```text
+---------------------------+
|          User             |
| PDF Resume + Job Text     |
+-------------+-------------+
              |
              v
+---------------------------+
| Streamlit User Interface  |
| Upload / Text Input / Run |
+-------------+-------------+
              |
              v
+---------------------------+
| Input Validation          |
| PDF selected? Job text?   |
+-------------+-------------+
              |
              v
+---------------------------+
| PDF Text Extraction       |
| pypdf                     |
+-------------+-------------+
              |
              v
+---------------------------+
| Text Preprocessing        |
| lowercase, clean, spacing |
+-------------+-------------+
              |
              +-------------------------------+
              |                               |
              v                               v
+---------------------------+   +---------------------------+
| TF-IDF Vectorization      |   | Skill Keyword Extraction  |
| scikit-learn              |   | Configurable skill list   |
+-------------+-------------+   +-------------+-------------+
              |                               |
              v                               v
+---------------------------+   +---------------------------+
| Cosine Similarity         |   | Skill Set Comparison      |
| Text similarity score     |   | Matched / Not Detected    |
+-------------+-------------+   +-------------+-------------+
              |                               |
              +---------------+---------------+
                              |
                              v
                +---------------------------+
                | Results Dashboard         |
                | Score, skills, text preview|
                +-------------+-------------+
                              |
                              v
                +---------------------------+
                | Downloadable Text Report  |
                +---------------------------+
```

## 4. Main Components

### 4.1 Streamlit UI
**Responsibilities**
- Display the project title and instructions.
- Let the user upload a PDF.
- Accept a job description in a text area.
- Trigger analysis after the user clicks the Analyze button.
- Display validation errors and processing errors.
- Show similarity, skill results, and extracted text.
- Provide a report download.

**Implementation file:** `app.py`

### 4.2 Input Validation
Check that:
- A PDF file has been uploaded.
- The job description is not empty.
- The job description has enough text to compare meaningfully.
- The PDF is readable and contains selectable text.

If validation fails, show a useful message and stop processing.

### 4.3 PDF Text Extraction
Use `pypdf.PdfReader` to read each page and combine extracted text.

**Input:** Uploaded PDF bytes  
**Output:** Resume text string  
**Error cases:** Corrupt PDF, encrypted PDF, or scanned PDF with no text layer.

OCR can be added later for scanned documents.

### 4.4 Text Preprocessing
Normalize resume text and job-description text consistently:
- Convert text to lowercase.
- Remove URLs.
- Replace unwanted punctuation with spaces while retaining characters needed in terms such as `C++`, `C#`, and `Node.js`.
- Collapse repeated whitespace.
- Trim leading and trailing whitespace.

Keep the original extracted resume text separately for preview purposes.

### 4.5 TF-IDF Vectorization
Use scikit-learn's `TfidfVectorizer` to convert the resume and job description into numerical vectors.

Configuration in the current implementation:
- English stop-word removal.
- Unigrams and bigrams (`ngram_range=(1, 2)`).

TF-IDF weights terms according to their importance in the compared documents. This implementation fits the vectorizer to the two documents being compared; it does not train a supervised classifier.

### 4.6 Cosine Similarity
Use `cosine_similarity` to compare the two TF-IDF vectors.

Formula:

`similarity(A, B) = (A · B) / (||A|| × ||B||)`

Convert the value to a percentage for display:
`display_score = similarity * 100`

The percentage means textual similarity only. It must not be interpreted as a probability of getting hired.

### 4.7 Skill Extraction
Maintain a list of skill phrases such as Python, SQL, Pandas, NumPy, machine learning, Git, and REST API.

Search both the resume and job description using case-insensitive phrase matching. Use escaped keywords and word boundaries/guards to reduce accidental partial matches.

**Outputs**
- `resume_skills`: skills detected in the resume.
- `job_skills`: skills detected in the job description.
- `matched_skills`: intersection of the two sets.
- `missing_skills`: job skills not detected in the resume.

“Missing” means not found by the current dictionary matcher; the skill may be expressed using a synonym or different wording.

### 4.8 Results Dashboard
Display:
- Text similarity percentage.
- Number of matched skills.
- Number of job skills not detected.
- Matched-skill table.
- Not-detected-skill table.
- Extracted resume text preview.
- Download report button.

### 4.9 Report Generator
Create a text report containing:
- Resume filename.
- Report generation time.
- Similarity score.
- Matched skills.
- Job skills not detected in the resume.
- A limitation note explaining that this is not a hiring probability.

## 5. Data Flow

1. The user uploads a PDF resume.
2. The user pastes a job description.
3. The user clicks **Analyze Resume**.
4. The app validates the inputs.
5. `pypdf` extracts the resume text.
6. The app cleans both texts.
7. TF-IDF converts the texts to vectors.
8. Cosine similarity calculates a text-similarity score.
9. Skill extraction identifies known skills in both texts.
10. Set operations determine matched and not-detected skills.
11. Streamlit displays the results.
12. The user can download a text report.

## 6. Technology Stack

| Technology | Role |
|---|---|
| Python 3.10+ | Application language |
| Streamlit | Local web UI |
| scikit-learn | TF-IDF and cosine similarity |
| pypdf | PDF text extraction |
| Pandas | Tabular display of skills |
| `re` | Text cleaning and keyword matching |
| `datetime` | Report timestamp |

No database is required for the initial version. The uploaded file is processed in the running app session and is not intentionally sent to an external AI service.

## 7. Repository / Folder Structure

```text
ai_resume_screening/
├── app.py
├── requirements.txt
├── README.md
└── IMPLEMENT.md
```

### File responsibilities
- `app.py`: UI, validation, extraction, preprocessing, matching, results, report.
- `requirements.txt`: Python package dependencies.
- `README.md`: setup and usage instructions.
- `IMPLEMENT.md`: architecture and implementation plan.

For a larger version, split the code into modules:

```text
ai_resume_screening/
├── app.py
├── requirements.txt
├── README.md
├── IMPLEMENT.md
├── src/
│   ├── pdf_parser.py
│   ├── text_preprocessing.py
│   ├── skill_extractor.py
│   ├── matcher.py
│   └── report_generator.py
└── tests/
    ├── test_preprocessing.py
    ├── test_skills.py
    └── test_matcher.py
```

## 8. Installation and Execution

### Windows
```bash
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal, usually `http://localhost:8501`.

## 9. Functional Requirements

| ID | Requirement | Expected behavior |
|---|---|---|
| FR-01 | Upload PDF | Accept PDF files only |
| FR-02 | Validate job description | Reject empty or very short text |
| FR-03 | Extract PDF text | Return selectable text or show an error |
| FR-04 | Preprocess text | Normalize text for comparison |
| FR-05 | Calculate similarity | Display TF-IDF cosine similarity as a percentage |
| FR-06 | Detect skills | Find known skill phrases in both texts |
| FR-07 | Compare skills | Show matched and not-detected skills |
| FR-08 | Display results | Present metrics and tables |
| FR-09 | Download report | Generate a plain-text report |
| FR-10 | Explain limitations | Warn that similarity is not hiring probability |

## 10. Non-Functional Requirements
- **Usability:** Simple, clearly labeled interface.
- **Performance:** Typical text-based resumes should process quickly on a standard laptop.
- **Reliability:** Invalid files and empty inputs should produce readable error messages.
- **Privacy:** Prefer local execution; avoid logging or sharing resume contents unnecessarily.
- **Maintainability:** Keep skill keywords in one configurable list.
- **Fairness:** Do not use protected personal attributes or the score as the sole basis for hiring decisions.

## 11. Test Plan

| Test | Input | Expected result |
|---|---|---|
| T-01 | No PDF uploaded | Prompt to upload a PDF |
| T-02 | Empty job description | Prompt to enter a job description |
| T-03 | Very short job description | Ask for more detailed text |
| T-04 | Valid text-based PDF and job text | Show score and skill results |
| T-05 | PDF with no selectable text | Show a clear extraction error |
| T-06 | Resume and job share known skills | Show shared skills as matched |
| T-07 | Job contains a known skill absent from resume | Show it under skills not detected |
| T-08 | Download report selected | Download a `.txt` report |
| T-09 | Corrupt or unreadable PDF | Show an error without crashing the app |

## 12. Limitations and Risks
- Scanned/image-only PDFs require OCR, which is not included.
- The keyword dictionary cannot recognize every skill, abbreviation, or synonym.
- PDF formatting may cause text extraction errors.
- TF-IDF is lexical; it may not recognize meaning when wording differs.
- A high similarity score does not guarantee that a candidate meets the role's requirements.
- The skill matcher is not a validated assessment of candidate ability.
- Do not automatically reject candidates based on this prototype.

## 13. Future Enhancements
1. Add OCR for scanned resumes.
2. Support DOCX resumes.
3. Expand and externalize the skill dictionary in a JSON file.
4. Add multiple-resume comparison and sortable results.
5. Generate downloadable PDF reports.
6. Add a semantic similarity model and compare it with TF-IDF.
7. Add unit tests and a representative evaluation dataset.
8. Add user authentication only if a multi-user deployment is needed.
9. Add data retention controls and secure file handling before deployment.
10. Evaluate false matches and missed skills before using the tool in a real workflow.

## 14. Viva / Presentation Summary

**Problem:** Manually comparing resumes with job descriptions can take time.

**Solution:** Provide a local web interface that extracts resume text, compares it with job requirements, and highlights shared skills and possible skill gaps.

**Methods:** PDF extraction, text preprocessing, TF-IDF, cosine similarity, and keyword-based skill extraction.

**Output:** Similarity percentage, matched skills, skills not detected, text preview, and downloadable report.

**Conclusion:** The prototype demonstrates an explainable first-pass text comparison workflow. It should assist human review rather than make hiring decisions automatically.
