import pytest

from src.cleaner import Cleaner

cleaner = Cleaner()


@pytest.mark.contract
def test_parse_frontmatter_yaml():
    content = """---
title: "Guide"
weight: 10
---
Content here"""
    frontmatter, body = cleaner.parse_frontmatter(content)
    assert frontmatter["title"] == "Guide"
    assert frontmatter["weight"] == 10
    assert body == "Content here"


@pytest.mark.contract
def test_parse_frontmatter_toml():
    content = """+++
title = "Guide"
weight = 10
+++
Content here"""
    frontmatter, body = cleaner.parse_frontmatter(content)
    assert frontmatter["title"] == "Guide"
    assert frontmatter["weight"] == 10
    assert body == "Content here"


@pytest.mark.contract
def test_parse_frontmatter_none():
    content = "Just content here"
    frontmatter, body = cleaner.parse_frontmatter(content)
    assert frontmatter == {}
    assert body == "Just content here"


@pytest.mark.contract
def test_parse_frontmatter_malformed():
    content = """---
invalid: yaml: syntax:
---
Content"""
    frontmatter, body = cleaner.parse_frontmatter(content)
    assert frontmatter == {}
    assert "Content" in body


@pytest.mark.contract
def test_clean_shortcodes_self_closing():
    content = "Before {{< toc >}} After"
    result = cleaner.clean_shortcodes(content)
    assert "Before" in result
    assert "After" in result
    assert "{{<" not in result


@pytest.mark.contract
def test_clean_shortcodes_content():
    content = """{{< note >}}
Important info.
{{< /note >}}"""
    result = cleaner.clean_shortcodes(content)
    assert "Important info." in result
    assert "{{<" not in result


@pytest.mark.contract
def test_clean_shortcodes_nested():
    content = """{{< warning >}}
{{< note >}}Nested content{{< /note >}}
{{< /warning >}}"""
    result = cleaner.clean_shortcodes(content)
    assert "Nested content" in result
    assert "{{<" not in result


@pytest.mark.contract
def test_clean_shortcodes_multiple():
    content = "{{< toc >}} Text {{< note >}}Info{{< /note >}} More"
    result = cleaner.clean_shortcodes(content)
    assert "Text" in result
    assert "Info" in result
    assert "{{<" not in result


@pytest.mark.contract
def test_clean_code_fences_linenos():
    content = """```python {linenos=true}
print("hello")
```"""
    expected = """```python
print("hello")
```"""
    assert cleaner.clean_code_fences(content) == expected


@pytest.mark.contract
def test_clean_code_fences_highlight():
    content = """```yaml {hl_lines=[1,2]}
key: value
other: value
```"""
    expected = """```yaml
key: value
other: value
```"""
    assert cleaner.clean_code_fences(content) == expected


@pytest.mark.contract
def test_clean_code_fences_multiple():
    content = """```python {linenos=true}
code1
```
Text between
```bash {hl_lines=[1]}
code2
```"""
    result = cleaner.clean_code_fences(content)
    assert "{linenos" not in result
    assert "{hl_lines" not in result
    assert "code1" in result
    assert "code2" in result


@pytest.mark.contract
def test_clean_links_ref():
    content = '[Guide]({{< ref "install.md" >}})'
    assert cleaner.clean_links(content) == "[Guide](install.md)"


@pytest.mark.contract
def test_clean_links_relref():
    content = '[Docs]({{< relref "docs/setup.md" >}})'
    assert cleaner.clean_links(content) == "[Docs](docs/setup.md)"


@pytest.mark.contract
def test_clean_links_preserve_standard():
    content = "[External](https://example.com)"
    assert cleaner.clean_links(content) == "[External](https://example.com)"


@pytest.mark.contract
def test_clean_links_preserve_static():
    content = "[Image](/static/img/pic.png)"
    assert cleaner.clean_links(content) == "[Image](/static/img/pic.png)"


@pytest.mark.contract
def test_normalize_whitespace_blank_lines():
    content = "Line1\n\n\n\n\nLine2"
    assert cleaner.normalize_whitespace(content) == "Line1\n\nLine2\n"


@pytest.mark.contract
def test_normalize_whitespace_trailing():
    content = "Line1   \nLine2  "
    assert cleaner.normalize_whitespace(content) == "Line1\nLine2\n"


@pytest.mark.contract
def test_normalize_whitespace_preserve_code():
    content = """```python
    indented
        more indented
```"""
    result = cleaner.normalize_whitespace(content)
    assert "    indented" in result
    assert "        more indented" in result


@pytest.mark.contract
def test_normalize_whitespace_final_newline():
    content = "Content without newline"
    result = cleaner.normalize_whitespace(content)
    assert result.endswith("\n")


@pytest.mark.contract
def test_clean_markdown_full_pipeline():
    content = """---
title: "Guide"
---
# Install

{{< note >}}
Important info
{{< /note >}}

```python {linenos=true}
code here
```

See [docs]({{< ref "other.md" >}})
"""
    frontmatter, cleaned = cleaner.clean_markdown(content)
    assert frontmatter["title"] == "Guide"
    assert "Important info" in cleaned
    assert "{{<" not in cleaned
    assert "{linenos" not in cleaned
    assert "[docs](other.md)" in cleaned


@pytest.mark.contract
def test_clean_markdown_preserves_length():
    content = "# Title\n\nLots of content here."
    _frontmatter, cleaned = cleaner.clean_markdown(content)
    assert len(cleaned) >= len(content) * 0.5


@pytest.mark.contract
def test_clean_markdown_empty_input():
    frontmatter, cleaned = cleaner.clean_markdown("")
    assert frontmatter == {}
    assert cleaned == ""
