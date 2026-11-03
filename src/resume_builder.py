"""Build an improved draft of a resume for one job, and save it as a PDF.

The draft reuses the person's own text. It adds a summary aimed at the job, moves the
skills the job asks for to the front in the job's own wording, and leaves reminders
in [square brackets] where details should be added. It never invents experience:
skills the resume doesn't mention are only added when the person confirms them.
"""

import re
import unicodedata

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from src.skill_extractor import category_of, find_spans, find_terms
from src.suggestions import (_BULLET_RE, _HEADING_TO_SECTION, _WEAK_PHRASES, REQUIRED,
                             _max_years, _sections_are_reliable, extract_job_title,
                             parse_sections, skill_importance, split_job_sentences)
from src.text_preprocessing import clean_text

MAX_SUMMARY_SKILLS = 3
MAX_BULLET_HINTS = 4            # bullets that get a reminder to add a number or reword
WRAPPED_LINE_LENGTH = 85        # a line this long was probably wrapped by the PDF
_PLACEHOLDER_RE = re.compile(r"\[[^\[\]\n]+\]")
_ITEM_SPLIT_RE = re.compile(r"[,;|•\n]|(?<=[a-z])\.\s+")
_LABEL_RE = re.compile(r"^[A-Za-z][A-Za-z &/]{1,30}:\s*")
# Characters the PDF's built-in font can't show -> a close substitute.
_PDF_REPLACEMENTS = {"•": "-", "●": "-", "▪": "-", "◦": "-", "–": "-", "—": "-", "→": "->",
                     "‘": "'", "’": "'", "“": '"', "”": '"', "…": "...", " ": " "}


def job_wording(skill, job_text):
    """Return the skill as the job description writes it, e.g. "Power BI" or "JS"."""
    spans = find_spans(skill, job_text)
    if spans:
        start, end = spans[0]
        return " ".join(job_text[start:end].split())
    return skill


def _join_names(names):
    return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"


def _join_wrapped_lines(lines):
    """Join lines that a PDF wrapped in the middle of a sentence or bullet."""
    joined = []
    for line in lines:
        stripped = line.strip()
        previous = joined[-1].strip() if joined else ""
        continues = stripped and previous and not _BULLET_RE.match(line) and (
            stripped[0].islower()
            or (len(previous) >= WRAPPED_LINE_LENGTH and previous[-1] not in ".!?;:"))
        if continues:
            joined[-1] = f"{joined[-1].rstrip()} {stripped}"
        else:
            joined.append(line)
    return joined


def _split_blocks(resume_text):
    """Split a resume into [section, heading, lines] blocks, keeping each original heading."""
    blocks = [["header", None, []]]
    for line in resume_text.splitlines():
        key = line.strip().rstrip(":").strip().lower()
        if key in _HEADING_TO_SECTION:
            blocks.append([_HEADING_TO_SECTION[key], line.strip(), []])
        else:
            blocks[-1][2].append(line.rstrip())
    for block in blocks:
        block[2] = _join_wrapped_lines(block[2])
        while block[2] and not block[2][0].strip():
            block[2].pop(0)
        while block[2] and not block[2][-1].strip():
            block[2].pop()
    return blocks


def _ranked_matched_skills(skills, job_text):
    """Matched skills that the job requires come first; soft skills are left out."""
    job_sentences = split_job_sentences(job_text)
    hard = [s for s in skills["matched_skills"] if category_of(s) != "Soft skills"]
    return sorted(hard, key=lambda s: skill_importance(s, job_sentences)[0] != REQUIRED)


def _summary_line(resume_text, job_text, skills):
    title = extract_job_title(job_text)
    years = _max_years(resume_text)
    names = [job_wording(s, job_text) for s in _ranked_matched_skills(skills, job_text)]
    names = names[:MAX_SUMMARY_SKILLS]
    experience = f"{years} years of experience" if years else "experience"
    if title:
        article = "an" if title[0].lower() in "aeiou" else "a"
        if names:
            return f"Seeking {article} {title} role, bringing {experience} in {_join_names(names)}."
        return f"Seeking {article} {title} role."
    if names:
        return f"{experience[0].upper()}{experience[1:]} in {_join_names(names)}."
    return None


def _use_job_wording(item, skills, job_text):
    """Write a skill the way the job does, e.g. "JS" -> "JavaScript"."""
    for skill in skills["matched_skills"]:
        wording = job_wording(skill, job_text)
        for start, end in reversed(find_spans(skill, item)):
            found = item[start:end]
            # Only change real differences, not "REST API" vs "REST APIs" or letter case.
            if re.sub(r"[^a-z0-9]|s$", "", found.lower()) != re.sub(r"[^a-z0-9]|s$", "", wording.lower()):
                item = item[:start] + wording + item[end:]
    return item


def _skills_lines(skills_text, skills, job_text, confirmed):
    # Drop group labels such as "Languages:" so only the skills themselves are listed.
    items = [_LABEL_RE.sub("", item.strip()).rstrip(".").strip()
             for item in _ITEM_SPLIT_RE.split(skills_text)]
    items = [item for item in items if item]
    job_skills = skills["job_skills"]
    key, other = [], []
    for item in items:
        if any(find_terms(skill, item) for skill in job_skills):
            key.append(_use_job_wording(item, skills, job_text))
        else:
            other.append(item)
    for skill in _ranked_matched_skills(skills, job_text) + list(confirmed):
        if not any(find_terms(skill, item) for item in key):
            wording = job_wording(skill, job_text)
            # Start list items with a capital, but keep mixed case such as "iOS" as written.
            key.append(wording[0].upper() + wording[1:] if wording.islower() else wording)
    lines = [f"Key skills: {', '.join(key)}"] if key else []
    return lines + ([f"Other skills: {', '.join(other)}"] if other else [])


def _bullet_hints(lines, budget):
    """Add reminders to bullets that have no numbers or start with a weak phrase."""
    result = []
    for line in lines:
        if budget and _BULLET_RE.match(line) and not _PLACEHOLDER_RE.search(line):
            lowered = line.lower()
            if any(phrase in lowered for phrase in _WEAK_PHRASES):
                line += " [reword starting with an action verb such as built, led or improved]"
                budget -= 1
            elif not re.search(r"\d", line):
                line += " [add a number, e.g. time saved, users or % improved]"
                budget -= 1
        result.append(line)
    return result, budget


def _evidence_lines(confirmed, bullet="-"):
    lines = []
    for skill in confirmed:
        if category_of(skill) == "Soft skills":
            lines.append(f"{bullet} [Give a real example that shows {skill}]")
        else:
            lines.append(f"{bullet} [Show where you used {skill}: what you did and the result]")
    return lines


def _render(blocks):
    parts = []
    for _, heading, lines in blocks:
        text = "\n".join(([heading] if heading else []) + lines).strip("\n")
        if text:
            parts.append(text)
    return "\n\n".join(parts) + "\n"


def build_resume_draft(resume_text, job_text, skills, confirmed_skills=()) -> str:
    """Return an improved plain-text draft of the resume, aimed at this job.

    confirmed_skills are job skills the resume doesn't mention but the person says
    they have. They are added to the skills, with a reminder to show where they were used.
    """
    confirmed = [s for s in skills["missing_skills"] if s in set(confirmed_skills)]
    confirmed_wording = [job_wording(s, job_text) for s in confirmed]
    summary = _summary_line(resume_text, job_text, skills)
    sections = parse_sections(resume_text)

    if not _sections_are_reliable(resume_text, sections):
        # The sections can't be told apart, so add the new parts above the original text.
        blocks = []
        if summary:
            blocks.append(["summary", "SUMMARY", [summary]])
        skill_lines = _skills_lines("", skills, job_text, confirmed)
        blocks.append(["skills", "SKILLS", skill_lines])
        blocks.append(["other", None, [
            "[The text below couldn't be split into sections, often because of a two-column "
            "layout. Move it under clear headings such as EXPERIENCE and EDUCATION, then "
            "delete this note.]", *_evidence_lines(confirmed_wording), "",
            *resume_text.strip().splitlines()]])
        return _render(blocks)

    blocks = _split_blocks(resume_text)
    header = [b for b in blocks if b[0] == "header"]
    summary_blocks = [b for b in blocks if b[0] == "summary"]
    skills_blocks = [b for b in blocks if b[0] == "skills"]
    rest = [b for b in blocks if b[0] not in ("header", "summary", "skills")]

    title = extract_job_title(job_text)
    title_missing = bool(title) and clean_text(title) not in clean_text(resume_text)
    if summary_blocks:
        if summary and title_missing:
            summary_blocks[0][2].insert(0, summary)
    elif summary:
        summary_blocks = [["summary", "SUMMARY", [summary]]]

    skills_text = "\n".join(line for b in skills_blocks for line in b[2])
    heading = skills_blocks[0][1] if skills_blocks else "SKILLS"
    skills_blocks = [["skills", heading, _skills_lines(skills_text, skills, job_text, confirmed)]]

    budget = MAX_BULLET_HINTS
    for block in rest:
        if block[0] in ("experience", "projects"):
            block[2], budget = _bullet_hints(block[2], budget)
    # Write new bullets with the same symbol the resume uses.
    bullet = next((line.strip()[0] for b in rest for line in b[2] if _BULLET_RE.match(line)), "-")
    evidence = _evidence_lines(confirmed_wording, bullet)
    if evidence:
        target = next((b for b in rest if b[0] == "experience"),
                      next((b for b in rest if b[0] == "projects"), None))
        if target is None:
            target = ["experience", "EXPERIENCE", []]
            rest.insert(0, target)
        target[2].extend(evidence)

    return _render(header + summary_blocks + skills_blocks + rest)


def unfilled_placeholders(text) -> list:
    """Return the [square bracket] reminders still in the text."""
    return _PLACEHOLDER_RE.findall(text)


def _pdf_safe(text):
    for char, replacement in _PDF_REPLACEMENTS.items():
        text = text.replace(char, replacement)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", "replace").decode("latin-1")


def resume_pdf(text) -> bytes:
    """Lay out a plain-text resume as a one-column PDF: name, headings, bullets."""
    pdf = FPDF(format="A4")
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(True, margin=16)
    pdf.add_page()
    full_width = pdf.w - pdf.l_margin - pdf.r_margin
    name_done = False

    for raw in _pdf_safe(text).splitlines():
        line = raw.strip()
        if not line:
            pdf.ln(2.5)
            continue
        if not name_done:
            pdf.set_font("Helvetica", "B", 17)
            pdf.multi_cell(full_width, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            name_done = True
        elif line.rstrip(":").lower() in _HEADING_TO_SECTION:
            pdf.ln(1.5)
            pdf.set_font("Helvetica", "B", 11.5)
            pdf.cell(full_width, 6.5, line.rstrip(":").upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(150, 150, 150)
            pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
            pdf.ln(1.5)
        elif _BULLET_RE.match(raw):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_x(pdf.l_margin + 2)
            pdf.cell(4, 5, "-")
            pdf.multi_cell(full_width - 6, 5, _BULLET_RE.sub("", raw).strip(),
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(full_width, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    return bytes(pdf.output())
