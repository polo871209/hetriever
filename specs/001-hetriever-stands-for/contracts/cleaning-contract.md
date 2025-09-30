# Hugo Syntax Cleaning Contract: Hugo Documentation Retriever

**Date**: 2025-09-30  
**Feature**: Hugo Documentation Retriever  
**Branch**: 001-hetriever-stands-for

## Overview

This contract defines functions for cleaning Hugo-specific syntax from Markdown documentation while preserving semantic content and structure. All operations are pure functions with comprehensive test coverage.

## Cleaning Pipeline

```
Raw Markdown → Parse Frontmatter → Clean Shortcodes → Clean Code Fences → 
Clean Links → Normalize Whitespace → Cleaned Content
```

## Core Functions

### 1. `parse_frontmatter`

Extract and parse frontmatter from Markdown file.

**Function Signature**:
```python
def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Extract frontmatter and content from Markdown.
    
    Args:
        content: Raw Markdown file content
        
    Returns:
        Tuple of (frontmatter_dict, content_without_frontmatter)
        
    Raises:
        FrontmatterParseError: Malformed YAML/TOML frontmatter
    """
```

**Supported Formats**:

**YAML** (delimited by `---`):
```markdown
---
title: "Installation Guide"
weight: 10
draft: false
tags: ["setup", "install"]
---
Content here...
```

**TOML** (delimited by `+++`):
```markdown
+++
title = "Installation Guide"
weight = 10
draft = false
tags = ["setup", "install"]
+++
Content here...
```

**Behavior**:
1. Detect frontmatter delimiter (`---` or `+++`)
2. Extract frontmatter block
3. Parse as YAML or TOML
4. Return frontmatter dict and remaining content
5. If no frontmatter, return empty dict and full content

**Validation Rules**:
- Frontmatter must start at beginning of file (no leading whitespace)
- Closing delimiter must match opening delimiter
- Frontmatter content must be valid YAML or TOML
- If parsing fails, log warning and return empty dict

**Test Cases**:
```python
def test_parse_yaml_frontmatter():
    content = """---
title: "Guide"
weight: 10
---
Content here"""
    frontmatter, body = parse_frontmatter(content)
    assert frontmatter["title"] == "Guide"
    assert frontmatter["weight"] == 10
    assert body == "Content here"

def test_parse_toml_frontmatter():
    content = """+++
title = "Guide"
weight = 10
+++
Content here"""
    frontmatter, body = parse_frontmatter(content)
    assert frontmatter["title"] == "Guide"
    assert body == "Content here"

def test_parse_no_frontmatter():
    content = "Just content here"
    frontmatter, body = parse_frontmatter(content)
    assert frontmatter == {}
    assert body == "Just content here"

def test_parse_malformed_frontmatter():
    content = """---
invalid: yaml: syntax:
---
Content"""
    frontmatter, body = parse_frontmatter(content)
    assert frontmatter == {}  # Fallback to empty dict
    assert "Content" in body
```

---

### 2. `clean_shortcodes`

Remove Hugo shortcodes while preserving content.

**Function Signature**:
```python
def clean_shortcodes(content: str) -> str:
    """
    Remove Hugo shortcodes from content.
    
    Args:
        content: Markdown content with shortcodes
        
    Returns:
        Content with shortcodes removed or replaced
        
    Raises:
        None (best-effort cleaning)
    """
```

**Shortcode Types**:

**1. Self-closing shortcodes** (remove entirely):
```markdown
{{< toc >}}                    → (removed)
{{< figure src="img.png" >}}   → (removed)
{{< youtube "VIDEO_ID" >}}     → (removed)
```

**2. Content shortcodes** (extract inner content):
```markdown
{{< note >}}
Important information here.
{{< /note >}}
→
Important information here.
```

**3. Inline shortcodes** (remove markup, keep text):
```markdown
{{< param "version" >}}        → (removed)
{{< ref "page.md" >}}          → (removed)
```

**Common Hugo Shortcodes**:
- `{{< note >}}`, `{{< warning >}}`, `{{< tip >}}` - Extract content
- `{{< figure >}}`, `{{< youtube >}}`, `{{< gist >}}` - Remove entirely
- `{{< ref >}}`, `{{< relref >}}` - Remove entirely
- `{{< highlight >}}`, `{{< code >}}` - Extract code content

**Behavior**:
1. Use regex to match shortcode patterns: `{{<.*?>}}` and `{{%.*?%}}`
2. For content shortcodes, extract inner content
3. For self-closing shortcodes, remove entirely
4. Preserve surrounding whitespace structure

**Test Cases**:
```python
def test_clean_self_closing_shortcodes():
    content = "Before {{< toc >}} After"
    assert clean_shortcodes(content) == "Before  After"

def test_clean_content_shortcodes():
    content = """{{< note >}}
Important info.
{{< /note >}}"""
    result = clean_shortcodes(content)
    assert "Important info." in result
    assert "{{<" not in result

def test_clean_nested_shortcodes():
    content = """{{< warning >}}
{{< note >}}Nested content{{< /note >}}
{{< /warning >}}"""
    result = clean_shortcodes(content)
    assert "Nested content" in result
    assert "{{<" not in result

def test_clean_multiple_shortcodes():
    content = "{{< toc >}} Text {{< note >}}Info{{< /note >}} More"
    result = clean_shortcodes(content)
    assert "Text" in result
    assert "Info" in result
    assert "{{<" not in result
```

---

### 3. `clean_code_fences`

Clean Hugo-specific code fence attributes while preserving code.

**Function Signature**:
```python
def clean_code_fences(content: str) -> str:
    """
    Remove Hugo code fence attributes, keep code content.
    
    Args:
        content: Markdown with code fences
        
    Returns:
        Content with cleaned code fences
    """
```

**Hugo Code Fence Extensions**:

**Line numbers** (remove):
```markdown
```python {linenos=true}
code here
```
→
```python
code here
```
```

**Line highlighting** (remove):
```markdown
```yaml {hl_lines=[2,3]}
line1
line2
line3
```
→
```yaml
line1
line2
line3
```
```

**Anchor IDs** (remove):
```markdown
```bash {#install-script}
./install.sh
```
→
```bash
./install.sh
```
```

**Behavior**:
1. Match code fence opening: `` ```lang {attrs} ``
2. Extract language identifier
3. Remove all Hugo attributes in `{...}`
4. Preserve code content and closing fence
5. Normalize to standard Markdown code fences

**Test Cases**:
```python
def test_clean_code_fence_linenos():
    content = """```python {linenos=true}
print("hello")
```"""
    expected = """```python
print("hello")
```"""
    assert clean_code_fences(content) == expected

def test_clean_code_fence_highlight():
    content = """```yaml {hl_lines=[1,2]}
key: value
other: value
```"""
    expected = """```yaml
key: value
other: value
```"""
    assert clean_code_fences(content) == expected

def test_clean_multiple_code_fences():
    content = """
```python {linenos=true}
code1
```
Text between
```bash {hl_lines=[1]}
code2
```"""
    result = clean_code_fences(content)
    assert "{linenos" not in result
    assert "{hl_lines" not in result
    assert "code1" in result
    assert "code2" in result
```

---

### 4. `clean_links`

Clean Hugo-specific link syntax to standard Markdown.

**Function Signature**:
```python
def clean_links(content: str) -> str:
    """
    Convert Hugo links to standard Markdown links.
    
    Args:
        content: Markdown with Hugo links
        
    Returns:
        Content with standard Markdown links
    """
```

**Hugo Link Types**:

**Ref links** (convert to relative):
```markdown
[Link]({{< ref "page.md" >}})
→
[Link](page.md)
```

**Relref links** (convert to relative):
```markdown
[Link]({{< relref "docs/guide.md" >}})
→
[Link](docs/guide.md)
```

**Static resources** (keep as-is):
```markdown
[Image](/static/img/diagram.png)
→
[Image](/static/img/diagram.png)
```

**Behavior**:
1. Match link patterns: `[text]({{< ref "path" >}})`
2. Extract link text and target path
3. Remove shortcode wrapper
4. Convert to standard Markdown link
5. Preserve external links unchanged

**Test Cases**:
```python
def test_clean_ref_links():
    content = '[Guide]({{< ref "install.md" >}})'
    assert clean_links(content) == '[Guide](install.md)'

def test_clean_relref_links():
    content = '[Docs]({{< relref "docs/setup.md" >}})'
    assert clean_links(content) == '[Docs](docs/setup.md)'

def test_preserve_standard_links():
    content = '[External](https://example.com)'
    assert clean_links(content) == '[External](https://example.com)'

def test_preserve_static_links():
    content = '[Image](/static/img/pic.png)'
    assert clean_links(content) == '[Image](/static/img/pic.png)'
```

---

### 5. `normalize_whitespace`

Normalize whitespace while preserving structure.

**Function Signature**:
```python
def normalize_whitespace(content: str) -> str:
    """
    Normalize whitespace in cleaned content.
    
    Args:
        content: Cleaned Markdown content
        
    Returns:
        Content with normalized whitespace
    """
```

**Normalization Rules**:
1. Collapse multiple blank lines to maximum 2 (preserve paragraph separation)
2. Remove trailing whitespace from lines
3. Ensure single newline at end of file
4. Preserve code block formatting (no changes inside fences)

**Behavior**:
1. Split content into code blocks and text
2. For text sections:
   - Remove trailing spaces from lines
   - Collapse 3+ blank lines to 2
3. For code blocks:
   - Preserve all whitespace exactly
4. Reassemble content

**Test Cases**:
```python
def test_normalize_multiple_blank_lines():
    content = "Line1\n\n\n\n\nLine2"
    assert normalize_whitespace(content) == "Line1\n\nLine2"

def test_normalize_trailing_whitespace():
    content = "Line1   \nLine2  "
    assert normalize_whitespace(content) == "Line1\nLine2"

def test_preserve_code_whitespace():
    content = """```python
    indented
        more indented
```"""
    result = normalize_whitespace(content)
    assert "    indented" in result
    assert "        more indented" in result

def test_ensure_final_newline():
    content = "Content without newline"
    result = normalize_whitespace(content)
    assert result.endswith("\n")
```

---

### 6. `clean_markdown`

Main cleaning function that orchestrates the pipeline.

**Function Signature**:
```python
def clean_markdown(content: str) -> tuple[dict[str, Any], str]:
    """
    Clean Hugo Markdown to standard Markdown.
    
    Args:
        content: Raw Markdown file content
        
    Returns:
        Tuple of (frontmatter_dict, cleaned_content)
        
    Raises:
        CleaningError: Critical cleaning failure
    """
```

**Pipeline Steps**:
```python
def clean_markdown(content: str) -> tuple[dict[str, Any], str]:
    frontmatter, body = parse_frontmatter(content)
    body = clean_shortcodes(body)
    body = clean_code_fences(body)
    body = clean_links(body)
    body = normalize_whitespace(body)
    return frontmatter, body
```

**Validation**:
- Output length must be at least 50% of input (detect over-cleaning)
- Output must not be empty (unless input was empty)
- Output must be valid UTF-8

**Test Cases**:
```python
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
    frontmatter, cleaned = clean_markdown(content)
    assert frontmatter["title"] == "Guide"
    assert "Important info" in cleaned
    assert "{{<" not in cleaned
    assert "{linenos" not in cleaned
    assert "[docs](other.md)" in cleaned

def test_clean_markdown_preserves_length():
    content = "# Title\n\nLots of content here."
    frontmatter, cleaned = clean_markdown(content)
    assert len(cleaned) >= len(content) * 0.5

def test_clean_markdown_empty_input():
    frontmatter, cleaned = clean_markdown("")
    assert frontmatter == {}
    assert cleaned == ""
```

---

## Edge Cases

### 1. Malformed Shortcodes

**Input**:
```markdown
{{< note >}}
Missing closing tag
```

**Behavior**: Best-effort cleaning, log warning, preserve content

**Output**:
```markdown
Missing closing tag
```

### 2. Nested Code Fences

**Input**:
````markdown
```markdown
This is a nested example:
```python
code
```
End of example
```
````

**Behavior**: Respect outermost fence, don't clean inner example

### 3. Mixed Frontmatter Delimiters

**Input**:
```markdown
---
title: "Guide"
+++
Content
```

**Behavior**: Invalid frontmatter, return empty dict, preserve all content

### 4. Unicode and Special Characters

**Input**:
```markdown
{{< note >}}
Smart quotes: "hello" 'world'
Em dash: — and ellipsis: …
{{< /note >}}
```

**Behavior**: Preserve all Unicode characters exactly

---

## Performance Characteristics

| Operation | Input Size | Target Time |
|-----------|------------|-------------|
| parse_frontmatter | 1KB | <1ms |
| clean_shortcodes | 10KB | <5ms |
| clean_code_fences | 10KB | <5ms |
| clean_links | 10KB | <5ms |
| normalize_whitespace | 10KB | <5ms |
| clean_markdown (full) | 10KB | <20ms |

**Optimization**:
- Use compiled regex patterns (module-level constants)
- Single-pass processing where possible
- Avoid repeated string concatenation (use lists + join)

---

## Constitutional Alignment

**Code Quality (I)**: Pure functions, single responsibility, comprehensive error handling.  
**Performance (III)**: Target 10K lines/sec cleaning throughput (500+ files/sec at 20 lines/file).  
**Python 3.13 (IV)**: Use pattern matching for frontmatter type detection, modern regex syntax.  
**User Experience (II)**: Preserve semantic content, provide warnings for malformed input.

---

## Implementation Notes

**Technology**:
- Python 3.13 stdlib `re` module for regex
- `tomllib` (stdlib) for TOML parsing
- `pyyaml` for YAML parsing (minimal external dependency)

**Testing**:
- Use `pytest` with parametrized tests
- Test data in `tests/fixtures/hugo_samples/`
- Property-based testing with `hypothesis` for edge cases

**Regex Patterns**:
```python
SHORTCODE_SELF_CLOSING = re.compile(r'{{[<|%]\s*(\w+)[^}]*[>|%]}}')
SHORTCODE_OPENING = re.compile(r'{{[<|%]\s*(\w+)\s*[>|%]}}')
SHORTCODE_CLOSING = re.compile(r'{{[<|%]\s*/(\w+)\s*[>|%]}}')
CODE_FENCE_ATTRS = re.compile(r'```(\w+)\s*\{[^}]+\}')
REF_LINK = re.compile(r'\[([^\]]+)\]\({{<\s*(?:rel)?ref\s+"([^"]+)"\s*>}}\)')
```

---

## Example End-to-End

**Input**:
```markdown
---
title: "Istio Installation"
weight: 10
tags: ["setup", "install"]
---

# Installation Guide

{{< warning >}}
Requires Kubernetes 1.28+
{{< /warning >}}

## Prerequisites

```bash {linenos=true,hl_lines=[2]}
kubectl version
istioctl version
```

See [architecture]({{< ref "concepts/architecture.md" >}}) for details.
```

**Output**:
```python
frontmatter = {
    "title": "Istio Installation",
    "weight": 10,
    "tags": ["setup", "install"]
}

cleaned_content = """# Installation Guide

Requires Kubernetes 1.28+

## Prerequisites

```bash
kubectl version
istioctl version
```

See [architecture](concepts/architecture.md) for details.
"""
```
