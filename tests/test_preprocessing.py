from src.text_preprocessing import clean_text


def test_lowercases_and_collapses_whitespace():
    assert clean_text("  Hello   WORLD \n\t ") == "hello world"


def test_removes_urls():
    assert clean_text("See https://example.com/x and www.site.org now") == "see and now"


def test_keeps_programming_symbols():
    cleaned = clean_text("Skills: C++, C#, Node.js; CI/CD!")
    assert "c++" in cleaned
    assert "c#" in cleaned
    assert "node.js" in cleaned
    assert "ci/cd" in cleaned


def test_drops_sentence_periods():
    assert clean_text("I know Python. I know SQL.") == "i know python i know sql"


def test_empty_input():
    assert clean_text("") == ""
