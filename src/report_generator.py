"""Plain-text screening report."""

from datetime import datetime

from src.verdict import assess_match

LIMITATION_NOTE = (
    "These scores measure how similar the resume text is to the job description "
    "(word overlap, skill keywords and, if enabled, meaning). They are NOT a hiring "
    "probability or a validated measure of candidate quality. 'Not detected' skills "
    "were simply not found by the keyword dictionary and may be present under "
    "different wording. Use this report to assist, not replace, human review."
)


def _bullet_list(items) -> str:
    return "\n".join(f"  - {item}" for item in items) if items else "  (none)"


def _pct(value) -> str:
    return f"{value:.2f}%" if value is not None else "n/a"


def _suggestion_lines(suggestions) -> list:
    if not suggestions:
        return []
    lines = ["Suggestions to improve this resume for this job", "-" * 50]
    for item in suggestions:
        lines += [f"[{item['priority'].upper()}] {item['title']}", f"  {item['detail']}"]
    return lines + ["Only add what is true of your experience.", ""]


def generate_report(filename: str, similarity: float, skills: dict, generated_at=None,
                    semantic=None, suggestions=None) -> str:
    generated_at = generated_at or datetime.now()
    verdict = assess_match(similarity, skills, semantic)
    matched, missing = skills["matched_skills"], skills["missing_skills"]
    skill_match = skills.get("skill_match")
    skill_line = _pct(skill_match)
    if skill_match is not None:
        skill_line += f"  ({len(matched)} of {len(matched) + len(missing)} job skills)"

    lines = [
        "AI-Based Resume Screening and Job Matching Report",
        "=" * 50,
        f"Resume file:          {filename}",
        f"Generated at:         {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Text similarity:      {similarity:.2f}%  (TF-IDF word overlap)",
        f"Skill match:          {skill_line}",
        f"Semantic similarity:  {_pct(semantic)}  (meaning, AI model)",
        "",
        f"Overall match:        {verdict['label']}",
        f"  {verdict['summary']}",
        *[f"  - {reason}" for reason in verdict["reasons"]],
        f"  Note: {verdict['disclaimer']}",
        "",
        f"Matched skills ({len(matched)}):",
        _bullet_list(matched),
        "",
        f"Job skills not detected in resume ({len(missing)}):",
        _bullet_list(missing),
        "",
        *_suggestion_lines(suggestions),
        "Limitations",
        "-" * 50,
        LIMITATION_NOTE,
        "",
    ]
    return "\n".join(lines)
