import pytest

from src.cleaning import (
    clean_code_fences,
    clean_links,
    clean_markdown,
    clean_shortcodes,
    normalize_whitespace,
    parse_frontmatter,
)


@pytest.fixture
def sample_markdown():
    return """---
title: Test Document
date: 2024-01-01
---

# Heading

This is a paragraph with {{< shortcode >}} and [link](http://example.com).

```python
def hello():
    print("world")
```

More content here with {{< another "param" >}} shortcode.
"""


@pytest.fixture
def large_markdown():
    lines = []
    lines.append("---")
    lines.append("title: Large Test")
    lines.append("---")
    lines.append("")
    for i in range(1000):
        lines.append(f"# Section {i}")
        lines.append("")
        lines.append(f"This is paragraph {i} with {{{{< shortcode >}}}} content.")
        lines.append(f"[Link {i}](http://example.com/{i})")
        lines.append("")
        lines.append("```python")
        lines.append(f"def function_{i}():")
        lines.append(f'    return "{i}"')
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


@pytest.mark.benchmark
def test_clean_markdown_throughput(benchmark, large_markdown):
    result = benchmark(clean_markdown, large_markdown)
    assert result is not None
    line_count = large_markdown.count("\n") + 1
    stats = benchmark.stats.stats
    lines_per_second = line_count / stats.mean
    assert lines_per_second > 10000, f"Throughput {lines_per_second:.0f} lines/sec below target"


@pytest.mark.benchmark
def test_parse_frontmatter_performance(benchmark, large_markdown):
    result = benchmark(parse_frontmatter, large_markdown)
    assert result is not None


@pytest.mark.benchmark
def test_clean_links_performance(benchmark, large_markdown):
    _, body = parse_frontmatter(large_markdown)
    result = benchmark(clean_links, body)
    assert result is not None


@pytest.mark.benchmark
def test_clean_shortcodes_performance(benchmark, large_markdown):
    _, body = parse_frontmatter(large_markdown)
    result = benchmark(clean_shortcodes, body)
    assert result is not None


@pytest.mark.benchmark
def test_clean_code_fences_performance(benchmark, large_markdown):
    _, body = parse_frontmatter(large_markdown)
    result = benchmark(clean_code_fences, body)
    assert result is not None


@pytest.mark.benchmark
def test_normalize_whitespace_performance(benchmark, large_markdown):
    _, body = parse_frontmatter(large_markdown)
    result = benchmark(normalize_whitespace, body)
    assert result is not None


@pytest.mark.benchmark
def test_full_pipeline_performance(benchmark, sample_markdown):
    result = benchmark(clean_markdown, sample_markdown)
    frontmatter, body = result
    assert isinstance(frontmatter, dict)
    assert isinstance(body, str)
    assert len(body) > 0
