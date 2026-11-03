"""Streamlit UI for the AI-Based Resume Screening and Job Matching System.

Run with:  streamlit run app.py
"""

import pandas as pd
import streamlit as st

from src import semantic_matcher
from src.charts import score_gauge, skills_by_category_chart, top_keywords_chart
from src.highlighter import highlight_text, legend
from src.matcher import calculate_similarity, top_shared_keywords
from src.pdf_parser import PDFExtractionError, extract_text_from_pdf
from src.report_generator import LIMITATION_NOTE, generate_report
from src.resume_builder import build_resume_draft, job_wording, resume_pdf, unfilled_placeholders
from src.skill_extractor import category_of, compare_skills
from src.suggestions import HIGH, LOW, MEDIUM, suggest_improvements
from src.text_preprocessing import clean_text
from src.verdict import assess_match

MIN_JOB_WORDS = 15
PASTE_JOB, UPLOAD_JOB = "Paste text", "Upload PDF"
SUGGESTION_GROUPS = {HIGH: "🔴 Do these first", MEDIUM: "🟡 Worth doing", LOW: "⚪ Small improvements"}
SEMANTIC_AVAILABLE = semantic_matcher.is_available()


@st.cache_resource(show_spinner=False)
def get_semantic_model():
    return semantic_matcher.load_model()


def skills_table(skill_names):
    return pd.DataFrame({"Skill": skill_names,
                         "Category": [category_of(s) for s in skill_names]})


def show_resume_builder(result, skills, missing, run_key):
    """Let the person pick skills they have, edit the draft and download it."""
    confirmed = st.multiselect(
        "Job skills you really have that your resume doesn't mention",
        missing, format_func=lambda s: job_wording(s, result["job_raw"]),
        key=f"confirmed_{run_key}",
        help="These are added to your skills, with a reminder to show where you used them.")
    draft = build_resume_draft(result["resume_raw"], result["job_raw"], skills, confirmed)
    edited = st.text_area("Edit your resume", value=draft, height=480,
                          key=f"draft_{run_key}_{abs(hash(draft))}")
    st.caption("Changing the skills above rebuilds the draft and replaces your edits.")
    reminders = unfilled_placeholders(edited)
    if reminders:
        st.warning(f"{len(reminders)} reminder(s) in [square brackets] are still in the draft. "
                   f"Replace them with real details or delete them before sending.")
    stem = result["filename"].rsplit(".", 1)[0]
    d1, d2, _ = st.columns([1, 1, 2])
    d1.download_button("Download resume (.pdf)", data=resume_pdf(edited),
                       file_name=f"improved_resume_{stem}.pdf", mime="application/pdf")
    d2.download_button("Download resume (.txt)", data=edited,
                       file_name=f"improved_resume_{stem}.txt", mime="text/plain")


st.set_page_config(page_title="Resume Screening", page_icon="📄", layout="wide")

st.title("📄 AI-Based Resume Screening and Job Matching")
st.write(
    "Upload a text-based PDF resume and add a job description as text or a PDF. The app compares "
    "the two using TF-IDF cosine similarity, a keyword skill dictionary with synonyms, "
    "and optionally an AI model that compares meaning."
)
st.info(LIMITATION_NOTE)
st.caption("Your files are used only for this analysis and are not saved by this app. "
           "Avoid uploading documents with sensitive details such as ID numbers.")

col_left, col_right = st.columns(2)
with col_left:
    uploaded_file = st.file_uploader("Resume (PDF only)", type=["pdf"])
    use_semantic = st.checkbox(
        "Also compare by meaning (AI model)",
        value=SEMANTIC_AVAILABLE,
        disabled=not SEMANTIC_AVAILABLE,
        help="Uses the all-MiniLM-L6-v2 model locally. It is downloaded once "
             "(about 90 MB) on first use, then runs offline.",
    )
    if not SEMANTIC_AVAILABLE:
        st.caption("Install `sentence-transformers` to enable meaning-based comparison.")
with col_right:
    job_source = st.radio("Job description", [PASTE_JOB, UPLOAD_JOB], horizontal=True)
    if job_source == PASTE_JOB:
        job_file = None
        job_description = st.text_area("Job description text", height=220,
                                       label_visibility="collapsed",
                                       placeholder="Paste the full job description here...")
    else:
        job_description = ""
        job_file = st.file_uploader("Job description (PDF only)", type=["pdf"])

if st.button("Analyze Resume", type="primary"):
    # Input validation
    if uploaded_file is None:
        st.error("Please upload a PDF resume.")
        st.stop()
    if job_source == UPLOAD_JOB:
        if job_file is None:
            st.error("Please upload the job description PDF.")
            st.stop()
        try:
            job_description = extract_text_from_pdf(job_file.getvalue())
        except PDFExtractionError as exc:
            st.error(f"Job description PDF: {exc}")
            st.stop()
    if not job_description.strip():
        st.error("Please enter a job description.")
        st.stop()
    if len(job_description.split()) < MIN_JOB_WORDS:
        st.error(
            f"The job description is too short. Please provide at least "
            f"{MIN_JOB_WORDS} words for a meaningful comparison."
        )
        st.stop()

    with st.spinner("Analyzing..."):
        try:
            resume_raw = extract_text_from_pdf(uploaded_file.getvalue())
        except PDFExtractionError as exc:
            st.error(f"Resume PDF: {exc}")
            st.stop()

        resume_clean = clean_text(resume_raw)
        job_clean = clean_text(job_description)
        similarity = calculate_similarity(resume_clean, job_clean)
        skills = compare_skills(resume_clean, job_clean)
        keywords = top_shared_keywords(resume_clean, job_clean)
        suggestions = suggest_improvements(resume_raw, job_description, skills)

    semantic = None
    if use_semantic and SEMANTIC_AVAILABLE:
        with st.spinner("Comparing meaning with the AI model (the first run downloads it)..."):
            try:
                # The model reads natural sentences, so give it the original text.
                semantic = semantic_matcher.semantic_similarity(
                    resume_raw, job_description, model=get_semantic_model())
            except Exception as exc:
                st.warning(f"Meaning-based comparison failed, so it was skipped: {exc}")

    st.session_state["result"] = {
        "filename": uploaded_file.name,
        "resume_raw": resume_raw,
        "job_raw": job_description,
        "suggestions": suggestions,
        "keywords": keywords,
        "similarity": similarity,
        "semantic": semantic,
        "skills": skills,
    }

result = st.session_state.get("result")
if result:
    skills = result["skills"]
    matched, missing = skills["matched_skills"], skills["missing_skills"]
    st.divider()
    st.subheader("Results")

    verdict = assess_match(result["similarity"], skills, result["semantic"])
    show_box = {"strong": st.success, "partial": st.warning, "weak": st.error}[verdict["level"]]
    show_box(f"**Overall: {verdict['label']}**  \n{verdict['summary']}",
             icon={"strong": "✅", "partial": "⚠️", "weak": "❌"}[verdict["level"]])
    with st.expander("Why this match level?", expanded=True):
        for reason in verdict["reasons"]:
            st.markdown(f"- {reason}")
        st.caption(verdict["disclaimer"])

    g1, g2, g3 = st.columns(3)
    g1.plotly_chart(score_gauge(result["similarity"], "Text similarity (TF-IDF)"),
                    width="stretch")
    g2.plotly_chart(score_gauge(skills["skill_match"], "Skill match"),
                    width="stretch")
    g3.plotly_chart(score_gauge(result["semantic"], "Meaning similarity (AI)"),
                    width="stretch")
    g1.caption("Overlap of words and two-word phrases.")
    if skills["skill_match"] is not None:
        g2.caption(f"{len(matched)} of {len(skills['job_skills'])} job skills found in the resume.")
    else:
        g2.caption("No known skills found in the job description.")
    g3.caption("How well each part of the job description is covered by meaning."
               if result["semantic"] is not None else "Not computed for this run.")

    if skills["job_skills"]:
        st.plotly_chart(skills_by_category_chart(matched, missing), width="stretch")
    else:
        st.warning("No known skills were detected in the job description. "
                   "You can extend the dictionary in src/skill_extractor.py.")

    t1, t2 = st.columns(2)
    with t1:
        st.markdown(f"**✅ Matched skills ({len(matched)})**")
        if matched:
            st.dataframe(skills_table(matched), hide_index=True)
        else:
            st.write("No shared skills detected.")
    with t2:
        st.markdown(f"**⚠️ Job skills not detected in resume ({len(missing)})**")
        if missing:
            st.dataframe(skills_table(missing), hide_index=True)
        elif skills["job_skills"]:
            st.write("All detected job skills were found in the resume.")

    st.subheader("See the match in the text")
    st.html(legend())
    h1, h2 = st.columns(2)
    with h1:
        st.markdown("**Resume**")
        st.html(highlight_text(result["resume_raw"], matched))
    with h2:
        st.markdown("**Job description**")
        st.html(highlight_text(result["job_raw"], matched, missing))
    if result["keywords"]:
        st.plotly_chart(top_keywords_chart(result["keywords"]), width="stretch")
        st.caption("This shows why the text similarity score came out as it did: each word's "
                   "points are its share of that score. A word scores more when it stands out "
                   "in both texts.")
    else:
        st.write("The resume and job description share no significant words.")

    st.subheader("How to improve this resume for this job")
    if result["suggestions"]:
        st.caption("Only add what is true of your experience. These suggestions come from "
                   "comparing the text, so use your own judgement.")
        for priority, heading in SUGGESTION_GROUPS.items():
            items = [s for s in result["suggestions"] if s["priority"] == priority]
            if items:
                with st.expander(f"{heading} ({len(items)})", expanded=priority == HIGH):
                    for item in items:
                        # A bare $ would start a math formula in Streamlit markdown.
                        text = f"**{item['title']}**  \n{item['detail']}".replace("$", r"\$")
                        st.markdown(text)
    else:
        st.success("No major gaps were found between this resume and the job description.")

    st.subheader("Create an improved resume")
    st.caption("Optional: a draft built from your own resume for this job, with a summary aimed "
               "at the role, the job's skills first and in its wording, and reminders in "
               "[square brackets] where you should add details. Nothing is invented, so edit "
               "the draft before using it.")
    # A new analysis gets fresh widgets, so old choices can't refer to skills no longer listed.
    run_key = abs(hash((result["filename"], result["resume_raw"], result["job_raw"])))
    builder_key = f"builder_open_{run_key}"
    if not st.session_state.get(builder_key):
        if st.button("✨ Create an improved resume"):
            st.session_state[builder_key] = True
            st.rerun()
    else:
        if st.button("Close the resume builder"):
            st.session_state[builder_key] = False
            st.rerun()
        show_resume_builder(result, skills, missing, run_key)

    st.subheader("Screening report")
    report = generate_report(result["filename"], result["similarity"], skills,
                             semantic=result["semantic"], suggestions=result["suggestions"])
    st.download_button(
        "Download report (.txt)",
        data=report,
        file_name=f"screening_report_{result['filename'].rsplit('.', 1)[0]}.txt",
        mime="text/plain",
    )

