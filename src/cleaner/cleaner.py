import logging
import re
import tomllib
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class Cleaner:
    def parse_frontmatter(self, content: str) -> tuple[dict, str]:
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

    def clean_links(self, content: str) -> str:
        content = re.sub(r'\{\{<\s*ref\s+"([^"]+)"\s*>\}\}', r"\1", content)
        return re.sub(r'\{\{<\s*relref\s+"([^"]+)"\s*>\}\}', r"\1", content)

    def clean_shortcodes(self, content: str) -> str:
        while re.search(r"\{\{<\s*(\w+)\s*>\}\}(.*?)\{\{<\s*/\1\s*>\}\}", content, re.DOTALL):
            content = re.sub(
                r"\{\{<\s*(\w+)\s*>\}\}(.*?)\{\{<\s*/\1\s*>\}\}", r"\2", content, flags=re.DOTALL
            )

        return re.sub(r"\{\{<\s*\w+\s*>\}\}", "", content)

    def clean_code_fences(self, content: str) -> str:
        return re.sub(r"(```\w+)\s*\{[^}]+\}", r"\1", content)

    def normalize_whitespace(self, content: str) -> str:
        parts = []
        in_code_block = False
        current_part = []

        for line in content.split("\n"):
            if line.strip().startswith("```"):
                if current_part:
                    text = "\n".join(current_part)
                    if not in_code_block:
                        text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
                        text = re.sub(r"\n{3,}", "\n\n", text)
                    parts.append(text)
                    current_part = []
                in_code_block = not in_code_block
                parts.append(line)
            else:
                current_part.append(line)

        if current_part:
            text = "\n".join(current_part)
            if not in_code_block:
                text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
                text = re.sub(r"\n{3,}", "\n\n", text)
            parts.append(text)

        result = "\n".join(parts)

        if result and not result.endswith("\n"):
            result += "\n"

        return result

    def clean_markdown(self, content: str) -> tuple[dict[str, Any], str]:
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

        frontmatter, body = self.parse_frontmatter(content)
        original_body_length = len(body)
        logger.debug(f"Parsed frontmatter, body length: {original_body_length}")

        body = self.clean_links(body)
        body = self.clean_shortcodes(body)
        body = self.clean_code_fences(body)
        body = self.normalize_whitespace(body)

        if body and len(body) < original_body_length * 0.5:
            logger.error(
                f"Over-cleaning detected: output {len(body)} < 50% of input {original_body_length}"
            )
            raise ValueError(
                f"Over-cleaning detected: output {len(body)} < 50% of input {original_body_length}"
            )

        logger.debug(f"Cleaning complete, final body length: {len(body)}")
        return frontmatter, body
