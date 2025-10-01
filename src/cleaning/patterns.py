"""Compiled regex patterns for markdown cleaning operations.

This module provides pre-compiled regex patterns used across cleaning modules
for consistent pattern matching and performance optimization.
"""

import re

SHORTCODE_SELF_CLOSING = re.compile(r"{{[<|%]\s*(\w+)[^}]*[>|%]}}")
SHORTCODE_OPENING = re.compile(r"{{[<|%]\s*(\w+)\s*[>|%]}}")
SHORTCODE_CLOSING = re.compile(r"{{[<|%]\s*/(\w+)\s*[>|%]}}")
CODE_FENCE_ATTRS = re.compile(r"```(\w+)\s*\{[^}]+\}")
REF_LINK = re.compile(r"\[([^\]]+)\]\({{<\s*(?:rel)?ref\s+\"([^\"]+)\"\s*>}}\)")
FRONTMATTER_YAML = re.compile(r"^---\s*\n(.*?)^---\s*\n", re.DOTALL | re.MULTILINE)
FRONTMATTER_TOML = re.compile(r"^\+\+\+\s*\n(.*?)^\+\+\+\s*\n", re.DOTALL | re.MULTILINE)
MULTIPLE_NEWLINES = re.compile(r"\n{3,}")
TRAILING_WHITESPACE = re.compile(r"[ \t]+$", re.MULTILINE)
