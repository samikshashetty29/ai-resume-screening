"""Dictionary-based skill extraction.

Edit SKILL_CATEGORIES to add or remove skills, and SYNONYMS to add other ways of
writing a skill (for example "js" for "javascript"). Matching is case-insensitive
and uses guards so that, for example, "java" does not match inside "javascript"
and "c" does not match inside "c++".
"""

import re
from functools import lru_cache

SKILL_CATEGORIES = {
    "Programming": [
        "python", "java", "javascript", "typescript", "c", "c++", "c#", "golang",
        "rust", "kotlin", "swift", "php", "ruby", "scala", "matlab",
    ],
    "Web": [
        "html", "css", "react", "angular", "vue", "node.js", "express",
        "django", "flask", "fastapi", "spring boot", "rest api", "graphql",
    ],
    "Data & ML": [
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "pandas", "numpy",
        "scikit-learn", "tensorflow", "pytorch", "keras", "machine learning",
        "deep learning", "natural language processing", "computer vision",
        "data analysis", "data visualization", "statistics", "matplotlib",
        "seaborn", "power bi", "tableau", "excel", "spark", "hadoop",
    ],
    "DevOps & Tools": [
        "git", "github", "docker", "kubernetes", "aws", "azure", "gcp",
        "linux", "ci/cd", "jenkins", "jira", "agile", "scrum",
    ],
    "Marketing": [
        "digital marketing", "social media marketing", "seo", "content marketing",
        "email marketing", "copywriting", "brand strategy", "market research",
        "google analytics", "event planning",
    ],
    "HR": [
        "recruitment", "talent acquisition", "onboarding", "payroll",
        "employee engagement", "performance management",
    ],
    "Finance": [
        "accounting", "financial analysis", "financial modeling", "budgeting",
        "auditing", "taxation",
    ],
    "Design": [
        "figma", "adobe photoshop", "adobe illustrator", "canva", "ui design",
        "ux design",
    ],
    "Soft skills": [
        "communication", "teamwork", "leadership", "problem solving",
        "public speaking", "time management", "critical thinking",
        "attention to detail", "project management", "stakeholder management",
    ],
}

# Other ways of writing a skill -> the skill name used in SKILL_CATEGORIES.
SYNONYMS = {
    "javascript": ["js", "ecmascript"],
    "typescript": ["ts"],
    "c++": ["cpp"],
    "c#": ["c sharp", "csharp"],
    "golang": ["go language"],
    "react": ["react.js", "reactjs"],
    "vue": ["vue.js", "vuejs"],
    "angular": ["angularjs", "angular.js"],
    "node.js": ["nodejs", "node js"],
    "express": ["express.js", "expressjs"],
    "rest api": ["rest apis", "restful api", "restful apis", "restful services"],
    "postgresql": ["postgres"],
    "mongodb": ["mongo db"],
    "scikit-learn": ["sklearn", "scikit learn"],
    "machine learning": ["ml"],
    "deep learning": ["neural networks", "neural network"],
    "natural language processing": ["nlp"],
    "computer vision": ["image recognition", "image processing"],
    "data visualization": ["data visualisation", "dashboards"],
    "statistics": ["statistical analysis", "statistical modeling"],
    "power bi": ["powerbi"],
    "excel": ["ms excel", "microsoft excel", "spreadsheets"],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud", "google cloud platform"],
    "azure": ["microsoft azure"],
    "ci/cd": ["ci cd", "continuous integration", "continuous delivery"],
    "social media marketing": ["social media"],
    "seo": ["search engine optimization", "search engine optimisation"],
    "copywriting": ["copy writing", "writing copy"],
    "recruitment": ["recruiting"],
    "event planning": ["event management", "organizing events", "organized events"],
    "teamwork": ["team work", "team player"],
    "problem solving": ["problem-solving", "analytical thinking"],
    "attention to detail": ["detail-oriented", "detail oriented"],
    "public speaking": ["presentation skills"],
    "adobe photoshop": ["photoshop"],
    "adobe illustrator": ["illustrator"],
    "ux design": ["user experience"],
    "ui design": ["user interface design"],
}

SKILLS = [skill for skills in SKILL_CATEGORIES.values() for skill in skills]
_CATEGORY_OF = {skill: cat for cat, skills in SKILL_CATEGORIES.items() for skill in skills}


def category_of(skill: str) -> str:
    return _CATEGORY_OF.get(skill, "Other")


@lru_cache(maxsize=None)
def _pattern_for(skill: str) -> re.Pattern:
    # Guard against letters/digits and the symbol characters that form other
    # skill names (+, #, .) so "c" won't match "c++" or "c#".
    terms = [skill] + SYNONYMS.get(skill, [])
    # Allow any whitespace between words, as PDF text can wrap in the middle of a skill.
    alternatives = "|".join(re.escape(t.lower()).replace(r"\ ", r"\s+")
                            for t in sorted(terms, key=len, reverse=True))
    return re.compile(
        r"(?<![a-z0-9\+\#\.])(?:" + alternatives + r")(?![a-z0-9\+\#]|\.[a-z0-9])",
        re.IGNORECASE,
    )


def find_terms(skill: str, text: str) -> set:
    """Return the words in text that matched this skill, including synonyms."""
    return {match.group(0).lower() for match in _pattern_for(skill).finditer(text)}


def find_spans(skill: str, text: str) -> list:
    """Return the (start, end) position of every mention of this skill in text."""
    return [match.span() for match in _pattern_for(skill).finditer(text)]


def extract_skills(text: str, skills=None) -> set:
    """Return the set of known skills (by their main name) found in text."""
    if not text:
        return set()
    skills = SKILLS if skills is None else skills
    return {skill for skill in skills if _pattern_for(skill).search(text)}


def compare_skills(resume_text: str, job_text: str, skills=None) -> dict:
    """Compare skills found in the resume against those in the job description.

    skill_match is the percentage of job skills found in the resume, or None
    when no known skills were found in the job description.
    """
    resume_skills = extract_skills(resume_text, skills)
    job_skills = extract_skills(job_text, skills)
    matched = resume_skills & job_skills
    return {
        "resume_skills": sorted(resume_skills),
        "job_skills": sorted(job_skills),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(job_skills - resume_skills),
        "skill_match": round(len(matched) / len(job_skills) * 100, 2) if job_skills else None,
    }
