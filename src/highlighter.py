"""Show a resume or job description with its skills highlighted."""

import html

from src.charts import MATCHED_COLOR, MISSING_COLOR
from src.skill_extractor import find_spans

STYLES = {
    "matched": f"background:{MATCHED_COLOR}40;border-bottom:2px solid {MATCHED_COLOR};",
    "missing": f"background:{MISSING_COLOR}40;border-bottom:2px dashed {MISSING_COLOR};",
}
BOX_STYLE = ("white-space:pre-wrap;overflow-wrap:anywhere;max-height:420px;overflow-y:auto;"
             "padding:12px;border:1px solid rgba(128,128,128,0.35);border-radius:8px;"
             "font-size:0.9rem;line-height:1.6;")
MARK_STYLE = "color:inherit;padding:0 2px;border-radius:3px;"


def _mark(text, kind, tooltip):
    return (f'<mark style="{MARK_STYLE}{STYLES[kind]}" title="{html.escape(tooltip, quote=True)}">'
            f"{html.escape(text)}</mark>")


def highlight_text(text: str, matched, missing=()) -> str:
    """Return text as safe HTML with matched and missing skills marked.

    The text comes from uploaded files, so everything is escaped. The longest match
    wins where skills overlap.
    """
    spans = [(start, end, "matched", skill) for skill in matched
             for start, end in find_spans(skill, text)]
    spans += [(start, end, "missing", skill) for skill in missing
              for start, end in find_spans(skill, text)]
    spans.sort(key=lambda span: (span[0], span[0] - span[1]))

    parts, position = [], 0
    for start, end, kind, skill in spans:
        if start < position:
            continue  # overlaps a match already marked
        label = "Matched" if kind == "matched" else "Not detected in resume"
        parts += [html.escape(text[position:start]), _mark(text[start:end], kind, f"{label}: {skill}")]
        position = end
    parts.append(html.escape(text[position:]))
    return f'<div style="{BOX_STYLE}">{"".join(parts)}</div>'


def legend() -> str:
    return (_mark("Matched skill", "matched", "In both the resume and the job")
            + " &nbsp; "
            + _mark("Not detected in resume", "missing", "In the job only"))
