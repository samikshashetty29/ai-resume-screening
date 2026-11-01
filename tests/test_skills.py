from src.skill_extractor import compare_skills, extract_skills
from src.text_preprocessing import clean_text


def test_detects_multiword_skills():
    skills = extract_skills(clean_text("Experience in Machine Learning and REST API design"))
    assert {"machine learning", "rest api"} <= skills


def test_java_not_matched_inside_javascript():
    skills = extract_skills(clean_text("Built apps with JavaScript"))
    assert "javascript" in skills
    assert "java" not in skills


def test_c_not_matched_inside_cpp_or_csharp():
    skills = extract_skills(clean_text("Wrote C++ and C# services"))
    assert {"c++", "c#"} <= skills
    assert "c" not in skills


def test_node_js_detected():
    assert "node.js" in extract_skills(clean_text("Backend in Node.js."))


def test_compare_skills_matched_and_missing():
    resume = clean_text("Python, SQL, Pandas and Git")
    job = clean_text("We need Python, SQL, Docker and AWS")
    result = compare_skills(resume, job)
    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["aws", "docker"]
