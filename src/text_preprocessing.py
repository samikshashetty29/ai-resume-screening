"""Text normalization shared by the resume and the job description."""

import re

_URL_RE = re.compile(r"(https?://\S+|www\.\S+)")
# Keep letters, digits, whitespace, and the characters needed for terms such as
# C++, C#, Node.js, and CI/CD. Everything else becomes a space.
_UNWANTED_RE = re.compile(r"[^a-z0-9\s\+\#\.\-/]")
# A period is only meaningful inside a token (node.js); drop trailing/leading ones.
_STRAY_PERIOD_RE = re.compile(r"(?<![a-z0-9])\.|\.(?![a-z0-9])")
_WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Lowercase, strip URLs and unwanted punctuation, and collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = _URL_RE.sub(" ", text)
    text = _UNWANTED_RE.sub(" ", text)
    text = _STRAY_PERIOD_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()
