import pytest

from src.cleaner import Cleaner

cleaner = Cleaner()


@pytest.mark.edge_case
def test_parse_frontmatter_empty_yaml():
    content = """---
---
Content here"""
    frontmatter, body = cleaner.parse_frontmatter(content)
    assert frontmatter == {}
    assert body == "Content here"


@pytest.mark.edge_case
def test_parse_frontmatter_unicode():
    content = """---
title: "日本語タイトル"
emoji: "🎉"
---
Content with émojis and spëcial çhars"""
    frontmatter, body = cleaner.parse_frontmatter(content)
    assert frontmatter["title"] == "日本語タイトル"
    assert frontmatter["emoji"] == "🎉"
    assert "émojis" in body


@pytest.mark.edge_case
def test_clean_shortcodes_unclosed():
    content = "{{< note >}} Content without closing tag"
    result = cleaner.clean_shortcodes(content)
    assert "Content without closing tag" in result


@pytest.mark.edge_case
def test_clean_shortcodes_malformed():
    content = "{{< >}} {{< note Extra content"
    result = cleaner.clean_shortcodes(content)
    assert isinstance(result, str)
