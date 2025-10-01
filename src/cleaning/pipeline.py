import logging
from typing import Any

from .code_fences import clean_code_fences
from .frontmatter import parse_frontmatter
from .links import clean_links
from .shortcodes import clean_shortcodes
from .whitespace import normalize_whitespace

logger = logging.getLogger(__name__)


def clean_markdown(content: str) -> tuple[dict[str, Any], str]:
    """Clean markdown content through multi-stage processing pipeline.

    Orchestrates a series of cleaning operations to prepare markdown for semantic search:
    1. Parse and extract frontmatter (YAML/TOML)
    2. Clean markdown links to plain text
    3. Remove Hugo shortcodes
    4. Clean code fences (preserve or remove based on patterns)
    5. Normalize whitespace

    Includes safety check to prevent over-cleaning (>50% content loss).

    Args:
        content: Raw markdown content including optional frontmatter.

    Returns:
        A tuple of (frontmatter_dict, cleaned_body):
            - frontmatter_dict: Parsed frontmatter metadata (empty dict if none)
            - cleaned_body: Cleaned markdown body text

    Raises:
        ValueError: If cleaning removes more than 50% of content (over-cleaning protection).
    """
    logger.debug("Starting markdown cleaning pipeline")
    if not content:
        logger.warning("Empty content provided to clean_markdown")
        return {}, ""

    frontmatter, body = parse_frontmatter(content)
    original_body_length = len(body)
    logger.debug(f"Parsed frontmatter, body length: {original_body_length}")

    body = clean_links(body)
    body = clean_shortcodes(body)
    body = clean_code_fences(body)
    body = normalize_whitespace(body)

    if body and len(body) < original_body_length * 0.5:
        logger.error(
            f"Over-cleaning detected: output {len(body)} < 50% of input {original_body_length}"
        )
        raise ValueError(
            f"Over-cleaning detected: output {len(body)} < 50% of input {original_body_length}"
        )

    logger.debug(f"Cleaning complete, final body length: {len(body)}")
    return frontmatter, body
