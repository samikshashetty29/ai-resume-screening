"""Overall match level (Strong / Partial / Weak) with the reasons behind it.

This describes how well the resume TEXT matches the job description. It is not a
judgement of the person's ability and must not be used as a hiring decision.
Thresholds were chosen by looking at the sample data; adjust them here.
"""

STRONG_SKILL_MATCH = 75     # % of job skills found in the resume
STRONG_SEMANTIC = 55        # meaning similarity %
STRONG_TFIDF = 20           # used instead of meaning when the AI score is off
PARTIAL_SKILL_MATCH = 40
PARTIAL_SEMANTIC = 45
PARTIAL_TFIDF = 12

LEVELS = {
    "strong": ("Strong match",
               "The resume covers most of the job's requirements. A good candidate to "
               "shortlist for human review or an interview."),
    "partial": ("Partial match",
                "The resume covers some of the job's requirements. Check the skills not "
                "detected before deciding; they may be described in other words."),
    "weak": ("Weak match",
             "The resume shows little overlap with this job description. A quick human "
             "check is still worthwhile, as relevant experience may be worded differently."),
}

DISCLAIMER = ("Based only on the resume text compared with the job description. It is "
              "not a judgement of the person's ability; a person should make the final decision.")


def _describe(value, strong, partial):
    if value >= strong:
        return "high"
    if value >= partial:
        return "moderate"
    return "low"


def assess_match(similarity: float, skills: dict, semantic=None) -> dict:
    """Return {'level', 'label', 'summary', 'reasons', 'disclaimer'}."""
    skill_match = skills.get("skill_match")
    matched, missing = skills["matched_skills"], skills["missing_skills"]

    # The meaning score is preferred; TF-IDF stands in when it was not computed.
    if semantic is not None:
        text_strong, text_partial = semantic >= STRONG_SEMANTIC, semantic >= PARTIAL_SEMANTIC
    else:
        text_strong, text_partial = similarity >= STRONG_TFIDF, similarity >= PARTIAL_TFIDF

    if skill_match is not None:
        strong = skill_match >= STRONG_SKILL_MATCH and text_strong
        partial = skill_match >= PARTIAL_SKILL_MATCH or text_partial or similarity >= PARTIAL_TFIDF
    else:
        strong = False  # without known job skills there is too little evidence for "strong"
        partial = text_partial or similarity >= PARTIAL_TFIDF
    level = "strong" if strong else "partial" if partial else "weak"

    reasons = []
    if skill_match is not None:
        reasons.append(f"Found {len(matched)} of {len(matched) + len(missing)} job skills "
                       f"({skill_match:.0f}%, {_describe(skill_match, STRONG_SKILL_MATCH, PARTIAL_SKILL_MATCH)}).")
        if missing:
            shown = ", ".join(missing[:6]) + (f" and {len(missing) - 6} more" if len(missing) > 6 else "")
            reasons.append(f"Not detected in the resume: {shown}.")
    else:
        reasons.append("No known skills were found in the job description, so skills could not be compared.")
    if semantic is not None:
        reasons.append(f"Meaning similarity is {semantic:.1f}% "
                       f"({_describe(semantic, STRONG_SEMANTIC, PARTIAL_SEMANTIC)}).")
    reasons.append(f"Text similarity is {similarity:.1f}% "
                   f"({_describe(similarity, STRONG_TFIDF, PARTIAL_TFIDF)}).")

    label, summary = LEVELS[level]
    return {"level": level, "label": label, "summary": summary,
            "reasons": reasons, "disclaimer": DISCLAIMER}
