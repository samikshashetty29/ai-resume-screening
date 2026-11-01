"""Meaning-based similarity using a small local sentence-embedding model.

Unlike TF-IDF, this can tell that "built neural networks for image recognition"
is close to "deep learning and computer vision experience". The model
(all-MiniLM-L6-v2, about 90 MB) is downloaded once on first use and then runs
offline on the CPU. This module is optional: if sentence-transformers is not
installed, is_available() returns False and the app skips the semantic score.
"""

import re
from functools import lru_cache

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_WORDS = 60

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?;])\s+|\n+")


def is_available() -> bool:
    try:
        import sentence_transformers  # noqa: F401
    except ImportError:
        return False
    return True


@lru_cache(maxsize=1)
def load_model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME, device="cpu")


def chunk_text(text: str, max_words: int = CHUNK_WORDS) -> list:
    """Split text into chunks of whole sentences, each about max_words long.

    The model only reads ~256 tokens at a time, so long resumes are split up.
    """
    chunks, current = [], []
    for sentence in _SENTENCE_SPLIT_RE.split(text or ""):
        words = sentence.split()
        if not words:
            continue
        if current and len(current) + len(words) > max_words:
            chunks.append(" ".join(current))
            current = []
        current.extend(words)
        while len(current) > max_words:
            chunks.append(" ".join(current[:max_words]))
            current = current[max_words:]
    if current:
        chunks.append(" ".join(current))
    return chunks


def semantic_similarity(resume_text: str, job_text: str, model=None) -> float:
    """Return how well the resume covers the job description by meaning (0-100).

    Each part of the job description is compared with every part of the resume;
    the best match for each job part is kept, and these are averaged. Like the
    TF-IDF score, this is not a hiring probability.
    """
    resume_chunks = chunk_text(resume_text)
    job_chunks = chunk_text(job_text)
    if not resume_chunks or not job_chunks:
        return 0.0

    model = model or load_model()
    resume_vecs = model.encode(resume_chunks, normalize_embeddings=True)
    job_vecs = model.encode(job_chunks, normalize_embeddings=True)
    similarities = job_vecs @ resume_vecs.T          # cosine, since vectors are normalized
    score = float(similarities.max(axis=1).mean())
    return round(max(score, 0.0) * 100, 2)
