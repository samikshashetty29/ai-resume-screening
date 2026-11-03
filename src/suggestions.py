"""Job-specific suggestions for improving a resume.

Everything here is rule-based and runs locally. Each suggestion comes from comparing
this resume with this job description, and quotes one of them where possible. The
advice is to show real experience better, never to add skills the person lacks.
"""

import re
from collections import Counter

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from src.skill_extractor import SKILLS, category_of, find_terms
from src.text_preprocessing import clean_text

HIGH, MEDIUM, LOW = "high", "medium", "low"
PRIORITY_ORDER = (HIGH, MEDIUM, LOW)

REQUIRED, MENTIONED, OPTIONAL = "required", "mentioned", "optional"
MAX_INDIVIDUAL_SKILLS = 5       # required skills listed one by one before grouping the rest
MAX_LISTED = 6                  # names shown in a grouped suggestion
MAX_KEYWORDS = 8
MIN_RESUME_WORDS = 120
MIN_REPEATS = 2                 # how often a job word must appear to count as a keyword
MIN_MERGED_HEADINGS = 2         # lines with a heading inside them that mean columns are mixed
MIN_SECTIONS_FOUND = 2          # headings needed before saying a section is missing
QUOTE_LENGTH = 140

_REQUIRED_RE = re.compile(r"\b(required|requirements?|must|essential|mandatory|need to have)\b", re.I)
_OPTIONAL_RE = re.compile(
    r"\b(a plus|preferred|nice to have|good to have|bonus|desirable|advantage|familiarity)\b", re.I)
_HEADING_START_RE = re.compile(
    r"^(required|requirements|qualifications|must have|essential|nice to have|good to have|"
    r"preferred|bonus|desirable)\b", re.I)
_BULLET_RE = re.compile(r"^\s*[-•*▪●◦·–]\s+")
_SENTENCE_END_RE = re.compile(r"(?<=[.!?;])\s+")

_YEARS_RE = re.compile(
    r"(\d{1,2})\s*\+?\s*(?:(?:-|–|to)\s*\d{1,2}\s*)?(?:years?|yrs?)(?:\s+of)?\s+(?:\w+\s+){0,3}?experience",
    re.I)
_DEGREE_RE = re.compile(
    r"\b(bachelor|master|degree|graduate|mba|ph\.?d|b\.?tech|m\.?tech|b\.?sc|m\.?sc|b\.?e\.?)\b"
    r"(?![a-z])", re.I)
_TITLE_LINE_RE = re.compile(r"^\s*(?:job title|position|role)\s*[:\-]\s*(.{3,60}?)\s*$", re.I | re.M)
_TITLE_WORDS = r"[A-Z][\w+#./-]*(?:\s+[A-Z][\w+#./-]*){0,4}"
_TITLE_HIRING_RE = re.compile(
    r"(?i:hiring|looking for|seeking)\s+(?:(?i:an?)\s+)?(?:(?i:experienced|talented|skilled|motivated)\s+)?"
    rf"({_TITLE_WORDS})")
_TITLE_WANTED_RE = re.compile(rf"^\s*({_TITLE_WORDS})\s+wanted\b", re.M)

_WEAK_PHRASES = ("responsible for", "worked on", "helped with", "helped to", "assisted with",
                 "assisted in", "duties included", "involved in", "participated in")

# Headings as they appear on resumes -> the section they belong to.
_SECTION_HEADINGS = {
    "summary": ("summary", "professional summary", "career summary", "profile",
                "professional profile", "objective", "career objective", "about me", "about"),
    "skills": ("skills", "key skills", "technical skills", "core skills", "core competencies",
               "skills & tools", "skills and tools", "competencies"),
    "experience": ("experience", "work experience", "professional experience", "employment",
                   "employment history", "work history", "internship", "internships"),
    "projects": ("projects", "key projects", "academic projects", "personal projects"),
    "education": ("education", "academic background", "academics", "education & training"),
    "other": ("certifications", "certificates", "awards", "achievements", "languages",
              "interests", "hobbies", "publications", "references", "activities"),
}
_HEADING_TO_SECTION = {h: s for s, headings in _SECTION_HEADINGS.items() for h in headings}

# Common job-advert words that say nothing about this particular job.
_GENERIC_JOB_WORDS = {
    "ability", "able", "apply", "benefits", "candidate", "candidates", "company", "work",
    "working", "role", "roles", "team", "teams", "job", "experience", "experienced", "skills",
    "skill", "strong", "good", "great", "excellent", "knowledge", "understanding", "join",
    "responsibilities", "requirements", "required", "preferred", "looking", "hiring", "years",
    "year", "new", "including", "ensure", "using", "use", "help", "support", "develop",
    "opportunity", "ideal", "plus", "must", "will", "you", "your", "our", "wanted",
}


def _suggestion(priority, category, title, detail):
    return {"priority": priority, "category": category, "title": title, "detail": detail}


def _quote(text):
    text = " ".join(text.split())
    return text if len(text) <= QUOTE_LENGTH else text[:QUOTE_LENGTH].rsplit(" ", 1)[0] + "..."


def _name_list(items):
    shown = ", ".join(items[:MAX_LISTED])
    return f"{shown} and {len(items) - MAX_LISTED} more" if len(items) > MAX_LISTED else shown


def split_job_sentences(job_text):
    """Return (sentence, heading_level) pairs from a job description.

    heading_level is REQUIRED or OPTIONAL when the sentence sits under a heading such
    as "Requirements:" or "Nice to have", otherwise None. Lines wrapped in the middle
    of a sentence are joined back together.
    """
    pairs = []
    heading_level = None
    buffer = []
    after_bullet = False

    def flush():
        if buffer:
            for sentence in _SENTENCE_END_RE.split(" ".join(buffer)):
                if sentence.strip():
                    pairs.append((sentence.strip(), heading_level))
            buffer.clear()

    for line in job_text.splitlines():
        stripped = line.strip()
        if not stripped:
            flush()
            after_bullet = False
            continue
        is_bullet = bool(_BULLET_RE.match(line))
        is_short = len(stripped.split()) <= 6
        # Without a closing colon, a heading is a bare phrase on its own line, so it can't
        # continue a wrapped sentence or contain punctuation ("Required: Python and SQL.").
        # PDFs often drop blank lines, so a heading may also come straight after a bullet.
        is_bare_heading = ((not buffer or after_bullet) and not re.search(r"[.,:;]", stripped)
                           and len(stripped.split()) <= 4 and _HEADING_START_RE.match(stripped))
        after_bullet = is_bullet
        if not is_bullet and is_short and (stripped.endswith(":") or is_bare_heading):
            flush()
            if _OPTIONAL_RE.search(stripped):
                heading_level = OPTIONAL
            elif _REQUIRED_RE.search(stripped) or "qualification" in stripped.lower():
                heading_level = REQUIRED
            else:
                heading_level = None
            continue
        if is_bullet:
            flush()
            stripped = _BULLET_RE.sub("", line).strip()
        buffer.append(stripped)
    flush()
    return pairs


def skill_importance(skill, job_sentences):
    """Return (importance, sentence) for a skill: how strongly the job asks for it."""
    best_rank, best_sentence = -1, ""
    ranks = {OPTIONAL: 0, MENTIONED: 1, REQUIRED: 2}
    for sentence, heading_level in job_sentences:
        if not find_terms(skill, clean_text(sentence)):
            continue
        # The sentence's own wording beats its heading.
        if _OPTIONAL_RE.search(sentence):
            level = OPTIONAL
        elif _REQUIRED_RE.search(sentence):
            level = REQUIRED
        else:
            level = heading_level or MENTIONED
        if ranks[level] > best_rank:
            best_rank, best_sentence = ranks[level], sentence
    if best_rank < 0:
        return MENTIONED, ""
    return {rank: level for level, rank in ranks.items()}[best_rank], best_sentence


def parse_sections(resume_text):
    """Split a resume into {section: text} using its headings.

    Text before the first heading goes under "header". Two-column PDFs can extract in
    a mixed-up order, so treat the result as a best effort.
    """
    sections = {"header": []}
    current = "header"
    for line in resume_text.splitlines():
        key = line.strip().rstrip(":").strip().lower()
        if key in _HEADING_TO_SECTION:
            current = _HEADING_TO_SECTION[key]
            sections.setdefault(current, [])
        else:
            sections[current].append(line)
    return {name: "\n".join(lines) for name, lines in sections.items()}


def columns_are_mixed(resume_text):
    """True when headings sit inside other lines, as when two columns merge row by row.

    Two-column PDFs can extract as "Kabir Sethi SUMMARY" and "SKILLS EXPERIENCE".
    """
    heading_words = {heading.upper() for heading in _HEADING_TO_SECTION if " " not in heading}
    merged = 0
    for line in resume_text.splitlines():
        words = line.split()
        if len(words) > 1 and line.strip().rstrip(":").lower() not in _HEADING_TO_SECTION:
            merged += any(word in heading_words for word in words)
    return merged >= MIN_MERGED_HEADINGS


def _sections_are_reliable(resume_text, sections):
    """Only trust "section not found" when the resume's headings were clearly read."""
    found = {"summary", "skills", "experience", "projects", "education"} & set(sections)
    return len(found) >= MIN_SECTIONS_FOUND and not columns_are_mixed(resume_text)


def extract_job_title(job_text):
    """Return the job title if the job description states one clearly, else None."""
    for pattern in (_TITLE_LINE_RE, _TITLE_HIRING_RE, _TITLE_WANTED_RE):
        match = pattern.search(job_text)
        if match:
            return match.group(1).strip().rstrip(".,")
    return None


def _max_years(text):
    return max((int(y) for y in _YEARS_RE.findall(text)), default=None)


def _is_alternative(skill, sentence, matched_skills):
    """True when the job offers a choice, e.g. "AWS or GCP", and the resume has the other one."""
    clean = clean_text(sentence)
    for term in find_terms(skill, clean):
        for other in matched_skills:
            for other_term in find_terms(other, clean):
                if f"{term} or {other_term}" in clean or f"{other_term} or {term}" in clean:
                    return True
    return False


def _missing_skill_detail(skill, sentence):
    quoted = f'The job says: "{_quote(sentence)}" ' if sentence else ""
    if category_of(skill) == "Soft skills":
        return (f"{quoted}Add a bullet with a real example that shows {skill}, if you have "
                f"one. An example says more than listing the word.")
    return (f"{quoted}If you have used {skill}, add it to your Skills section and to a project or "
            f"job bullet showing what you did with it. If you haven't, a small practice project "
            f"would give you something true to write.")


def _missing_skill_suggestions(job_sentences, skills):
    by_level = {REQUIRED: [], MENTIONED: [], OPTIONAL: []}
    for skill in skills["missing_skills"]:
        level, sentence = skill_importance(skill, job_sentences)
        if _is_alternative(skill, sentence, skills["matched_skills"]):
            level = OPTIONAL
        by_level[level].append((skill, sentence))

    result = []
    for skill, sentence in by_level[REQUIRED][:MAX_INDIVIDUAL_SKILLS]:
        result.append(_suggestion(HIGH, "Skills", f"Required skill not found: {skill}",
                                  _missing_skill_detail(skill, sentence)))
    extra = [s for s, _ in by_level[REQUIRED][MAX_INDIVIDUAL_SKILLS:]]
    if extra:
        result.append(_suggestion(HIGH, "Skills", "More required skills not found",
                                  f"The job also requires {_name_list(extra)}. Add the ones you "
                                  f"really have, with an example of each."))
    if by_level[MENTIONED]:
        names = [s for s, _ in by_level[MENTIONED]]
        priority = HIGH if not by_level[REQUIRED] else MEDIUM
        result.append(_suggestion(priority, "Skills", "Job skills not found in your resume",
                                  f"Mentioned in the job but not found in your resume: "
                                  f"{_name_list(names)}. Add any you have, using the job's exact words."))
    if by_level[OPTIONAL]:
        names = [s for s, _ in by_level[OPTIONAL]]
        result.append(_suggestion(LOW, "Skills", "Optional skills that could help",
                                  f"Not essential for this job, because they are preferred, a plus, "
                                  f"or an alternative to a skill you have: {_name_list(names)}. "
                                  f"Add any you have."))
    return result


def _wording_suggestion(resume_clean, job_clean, skills):
    pairs = []
    for skill in skills["matched_skills"]:
        job_terms, resume_terms = find_terms(skill, job_clean), find_terms(skill, resume_clean)
        if job_terms and resume_terms and not job_terms & resume_terms:
            job_term, resume_term = min(job_terms), min(resume_terms)
            # "rest api" vs "rest apis" is not worth changing.
            if re.sub(r"[^a-z0-9]|s$", "", job_term) != re.sub(r"[^a-z0-9]|s$", "", resume_term):
                pairs.append(f'"{resume_term}" → "{job_term}"')
    if not pairs:
        return []
    return [_suggestion(MEDIUM, "Wording", "Use the same words as the job description",
                        f"You have these skills but word them differently: {', '.join(pairs[:MAX_LISTED])}. "
                        f"Automated screening often looks for the exact phrase, so use the job's wording.")]


def _evidence_suggestions(sections, job_sentences, skills):
    """Skills listed in the Skills section but never shown in experience or projects."""
    evidence = clean_text(sections.get("experience", "") + "\n" + sections.get("projects", ""))
    if "skills" not in sections:
        return []
    if not evidence:
        return [_suggestion(HIGH, "Experience", "Add experience or projects",
                            "No experience or projects section was found, so nothing shows how you "
                            "used your skills. Add internships, coursework or personal projects "
                            "that relate to this job.")]

    listed_only = []
    for skill in skills["matched_skills"]:
        if not find_terms(skill, evidence) and category_of(skill) != "Soft skills":
            level, _ = skill_importance(skill, job_sentences)
            listed_only.append((level != REQUIRED, skill))
    if not listed_only:
        return []
    names = [skill for _, skill in sorted(listed_only)]
    return [_suggestion(MEDIUM, "Experience", "Prove the skills you only list",
                        f"The job asks for these and you list them, but your experience and projects "
                        f"don't show them: {_name_list(names)}. Add a bullet showing how you used "
                        f"each one; a demonstrated skill counts for more than a listed one.")]


def _summary_suggestions(sections, resume_clean, job_text, skills, reliable):
    title = extract_job_title(job_text)
    title_missing = title and clean_text(title) not in resume_clean
    role = title or "this role"
    if reliable and not sections.get("summary", "").strip():
        strengths = ", ".join(skills["matched_skills"][:3])
        focus = f" Lead with what the job and your resume share, such as {strengths}." if strengths else ""
        return [_suggestion(MEDIUM, "Summary", "Add a short summary aimed at this job",
                            f"No summary was found. Add two or three lines at the top saying how "
                            f"you fit {role}.{focus}")]
    if title_missing:
        return [_suggestion(LOW, "Summary", f'Mention "{title}" in your summary',
                            "This job title doesn't appear in your resume. If it fairly describes "
                            "you, or the role you're aiming for, say so in your summary.")]
    return []


def _layout_suggestion(resume_text):
    if not columns_are_mixed(resume_text):
        return []
    return [_suggestion(MEDIUM, "Layout", "Your columns were read mixed together",
                        "This PDF's text comes out with its columns merged line by line. Job "
                        "portals' screening software may read it the same way, so use a "
                        "one-column version when applying through one. Your skills were still "
                        "checked, but advice about sections was skipped because they couldn't "
                        "be told apart.")]


def _requirement_suggestions(resume_text, job_text):
    result = []
    wanted, stated = _max_years(job_text), _max_years(resume_text)
    if wanted is not None and stated is None:
        result.append(_suggestion(MEDIUM, "Experience", "State your years of experience",
                                  f"The job asks for {wanted}+ years of experience, but your resume "
                                  f"doesn't state a total. Say how much relevant experience you have "
                                  f"in your summary."))
    elif wanted is not None and stated < wanted:
        result.append(_suggestion(MEDIUM, "Experience", "Address the experience gap",
                                  f"The job asks for {wanted}+ years; your resume says {stated}. Don't "
                                  f"overstate it. Highlight your most relevant work so the quality of "
                                  f"your experience stands out."))
    if _DEGREE_RE.search(job_text) and "education" not in parse_sections(resume_text) \
            and not _DEGREE_RE.search(resume_text):
        result.append(_suggestion(MEDIUM, "Education", "Add your education",
                                  "The job mentions a degree, but no education was found in your "
                                  "resume. Add your qualifications if you have them."))
    return result


def _keyword_suggestion(resume_clean, job_clean):
    def singular(word):
        return word[:-1] if word.endswith("s") and not word.endswith(("ss", "is", "us")) else word

    def in_resume(word):
        # A shared start counts, so "deploy" is found in "deployed".
        return any(r.startswith(word) or (len(r) > 3 and word.startswith(r)) for r in resume_words)

    skill_words = {word for skill in SKILLS for word in skill.split()}
    resume_words = {singular(w) for w in resume_clean.split()}
    counts = Counter(singular(w) for w in job_clean.split() if w.isalpha() and len(w) > 2
                     and w not in ENGLISH_STOP_WORDS and w not in _GENERIC_JOB_WORDS
                     and w not in skill_words)
    keywords = [w for w, n in counts.most_common() if n >= MIN_REPEATS and not in_resume(w)]
    if not keywords:
        return []
    return [_suggestion(LOW, "Wording", "Include the job's repeated keywords",
                        f"The job repeats these words, but your resume doesn't use them: "
                        f"{', '.join(keywords[:MAX_KEYWORDS])}. Use them where they honestly "
                        f"describe your work.")]


def _writing_suggestions(sections, resume_text):
    result = []
    lines = (sections.get("experience", "") + "\n" + sections.get("projects", "")).splitlines()
    bullets = [_BULLET_RE.sub("", line).strip() for line in lines if _BULLET_RE.match(line)]
    without_numbers = [b for b in bullets if not re.search(r"\d", b)]
    if len(bullets) >= 2 and len(without_numbers) / len(bullets) > 2 / 3:
        result.append(_suggestion(MEDIUM, "Experience", "Add numbers to your results",
                                  f'Most of your bullets have no numbers, for example: '
                                  f'"{_quote(without_numbers[0])}" Add real figures where you can, '
                                  f'such as time saved, users, team size or percentage improved.'))

    lowered = resume_text.lower()
    weak = [phrase for phrase in _WEAK_PHRASES if phrase in lowered]
    if weak:
        phrases = ", ".join(f'"{phrase}"' for phrase in weak[:3])
        result.append(_suggestion(LOW, "Experience", "Use stronger action verbs",
                                  f"Phrases like {phrases} describe duties, not results. Start "
                                  f"bullets with verbs such as built, improved, led or reduced."))

    word_count = len(resume_text.split())
    if word_count < MIN_RESUME_WORDS:
        result.append(_suggestion(LOW, "General", "Add more detail",
                                  f"Your resume has only about {word_count} words. A little more "
                                  f"detail about your work gives this job's requirements more to "
                                  f"match against."))
    return result


def suggest_improvements(resume_text, job_text, skills) -> list:
    """Return suggestions for this resume and job, most important first.

    Each one is a dict with 'priority' (high/medium/low), 'category', 'title' and 'detail'.
    """
    resume_clean, job_clean = clean_text(resume_text), clean_text(job_text)
    job_sentences = split_job_sentences(job_text)
    sections = parse_sections(resume_text)
    reliable = _sections_are_reliable(resume_text, sections)

    suggestions = [
        *_missing_skill_suggestions(job_sentences, skills),
        *_layout_suggestion(resume_text),
        *(_evidence_suggestions(sections, job_sentences, skills) if reliable else []),
        *_requirement_suggestions(resume_text, job_text),
        *_wording_suggestion(resume_clean, job_clean, skills),
        *_summary_suggestions(sections, resume_clean, job_text, skills, reliable),
        *_keyword_suggestion(resume_clean, job_clean),
        *_writing_suggestions(sections, resume_text),
    ]
    return sorted(suggestions, key=lambda s: PRIORITY_ORDER.index(s["priority"]))
