import re
import tomllib

import yaml


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML or TOML frontmatter from markdown content.

    Supports both YAML frontmatter (delimited by ---) and TOML frontmatter
    (delimited by +++). Returns parsed metadata and the remaining body.

    Args:
        content: Raw markdown content potentially containing frontmatter.

    Returns:
        Tuple of (frontmatter_dict, body_text):
            - frontmatter_dict: Parsed metadata (empty dict if none or parse error)
            - body_text: Content after frontmatter (or full content if no frontmatter)
    """
    yaml_match = re.match(r"^---\n(.*?)---\n(.*)$", content, re.DOTALL)
    if yaml_match:
        try:
            fm_content = yaml_match.group(1).strip()
            body = yaml_match.group(2)
            if not fm_content:
                return {}, body
            frontmatter = yaml.safe_load(fm_content)
            return frontmatter if frontmatter else {}, body
        except yaml.YAMLError:
            return {}, content

    toml_match = re.match(r"^\+\+\+\n(.*?)\+\+\+\n(.*)$", content, re.DOTALL)
    if toml_match:
        try:
            fm_content = toml_match.group(1).strip()
            body = toml_match.group(2)
            if not fm_content:
                return {}, body
            frontmatter = tomllib.loads(fm_content)
            return frontmatter if frontmatter else {}, body
        except tomllib.TOMLDecodeError:
            return {}, content

    return {}, content
