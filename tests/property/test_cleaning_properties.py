import re

from hypothesis import given
from hypothesis import strategies as st

from src.cleaning.code_fences import clean_code_fences
from src.cleaning.frontmatter import parse_frontmatter
from src.cleaning.links import clean_links
from src.cleaning.pipeline import clean_markdown
from src.cleaning.shortcodes import clean_shortcodes
from src.cleaning.whitespace import normalize_whitespace


@given(st.text())
def test_parse_frontmatter_always_returns_tuple(content):
    frontmatter, body = parse_frontmatter(content)
    assert isinstance(frontmatter, dict)
    assert isinstance(body, str)


@given(st.text())
def test_parse_frontmatter_preserves_content_length(content):
    frontmatter, body = parse_frontmatter(content)
    if not frontmatter:
        assert body == content


@given(st.text(min_size=1))
def test_clean_shortcodes_idempotent(content):
    cleaned_once = clean_shortcodes(content)
    cleaned_twice = clean_shortcodes(cleaned_once)
    assert cleaned_once == cleaned_twice


@given(st.text())
def test_clean_shortcodes_never_creates_shortcodes(content):
    if "{{<" not in content and "{{%" not in content:
        cleaned = clean_shortcodes(content)
        assert "{{<" not in cleaned
        assert "{{%" not in cleaned


@given(st.text())
def test_clean_code_fences_returns_string(content):
    result = clean_code_fences(content)
    assert isinstance(result, str)


@given(st.text(min_size=1))
def test_clean_code_fences_idempotent(content):
    cleaned_once = clean_code_fences(content)
    cleaned_twice = clean_code_fences(cleaned_once)
    assert cleaned_once == cleaned_twice


@given(st.text())
def test_clean_code_fences_preserves_simple_fences(content):
    if "```" in content and "{" not in content:
        result = clean_code_fences(content)
        assert result == content


@given(st.text())
def test_clean_links_returns_string(content):
    result = clean_links(content)
    assert isinstance(result, str)


@given(st.text(min_size=1))
def test_clean_links_idempotent(content):
    cleaned_once = clean_links(content)
    cleaned_twice = clean_links(cleaned_once)
    assert cleaned_once == cleaned_twice


@given(st.text())
def test_clean_links_never_creates_shortcodes(content):
    if "{{<" not in content:
        cleaned = clean_links(content)
        assert "{{<" not in cleaned


@given(st.text())
def test_normalize_whitespace_returns_string(content):
    result = normalize_whitespace(content)
    assert isinstance(result, str)


@given(st.text(min_size=1))
def test_normalize_whitespace_idempotent(content):
    normalized_once = normalize_whitespace(content)
    normalized_twice = normalize_whitespace(normalized_once)
    assert normalized_once == normalized_twice


@given(st.text())
def test_normalize_whitespace_no_trailing_spaces(content):
    result = normalize_whitespace(content)
    for line in result.split("\n"):
        assert not line.endswith(" "), f"Line has trailing space: {line!r}"


@given(st.text())
def test_normalize_whitespace_max_two_blank_lines(content):
    result = normalize_whitespace(content)
    assert "\n\n\n\n" not in result


@given(st.text())
def test_clean_markdown_returns_tuple(content):
    frontmatter, cleaned = clean_markdown(content)
    assert isinstance(frontmatter, dict)
    assert isinstance(cleaned, str)


@given(st.text(min_size=1))
def test_clean_markdown_idempotent(content):
    _, cleaned_once = clean_markdown(content)
    _, cleaned_twice = clean_markdown(cleaned_once)
    assert cleaned_once == cleaned_twice


@given(st.text())
def test_clean_markdown_removes_all_shortcodes(content):
    _, cleaned = clean_markdown(content)
    assert "{{<" not in cleaned
    assert "{{%" not in cleaned


@given(st.text())
def test_clean_markdown_no_code_fence_attributes(content):
    _, cleaned = clean_markdown(content)
    code_fence_pattern = re.compile(r"```\w+\s*\{[^}]+\}")
    assert not code_fence_pattern.search(cleaned)
