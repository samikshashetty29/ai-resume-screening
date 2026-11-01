"""TF-IDF vectorization and cosine similarity."""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _vectorize(resume_text: str, job_text: str):
    """Return (vectorizer, vectors), or None when there are no usable words."""
    if not resume_text.strip() or not job_text.strip():
        return None

    # Keep tokens like c++, c#, node.js intact.
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        token_pattern=r"(?u)\b\w[\w\+\#\.]*",
    )
    try:
        return vectorizer, vectorizer.fit_transform([resume_text, job_text])
    except ValueError:
        # Raised when every token is a stop word (empty vocabulary).
        return None


def calculate_similarity(resume_text: str, job_text: str) -> float:
    """Return the TF-IDF cosine similarity of the two texts as a percentage (0-100).

    This is a text-similarity measure only, not a hiring probability.
    """
    result = _vectorize(resume_text, job_text)
    if result is None:
        return 0.0

    _, vectors = result
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(float(score) * 100, 2)


def top_shared_keywords(resume_text: str, job_text: str, limit: int = 10) -> list:
    """Return [(term, points)] for the terms adding most to the similarity score.

    The vectors have unit length, so the cosine similarity is the sum of
    resume_weight * job_weight over all terms. A term's points are its share of
    that sum, and all terms' points add up to the similarity percentage.
    """
    result = _vectorize(resume_text, job_text)
    if result is None:
        return []

    vectorizer, vectors = result
    points = vectors[0].multiply(vectors[1]).toarray()[0] * 100
    terms = vectorizer.get_feature_names_out()
    ranked = sorted(((terms[i], float(points[i])) for i in points.nonzero()[0]),
                    key=lambda item: (-item[1], item[0]))
    return ranked[:limit]
