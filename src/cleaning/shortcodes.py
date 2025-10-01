import re


def clean_shortcodes(content: str) -> str:
    """Remove Hugo shortcodes from markdown content.

    Removes both paired shortcodes ({{< name >}}...{{< /name >}}) and
    self-closing shortcodes ({{< name >}}), preserving inner content
    for paired shortcodes.

    Args:
        content: Markdown content potentially containing Hugo shortcodes.

    Returns:
        Content with shortcodes removed, preserving inner content of paired tags.
    """
    pattern = r"\{\{<\s*(\w+)\s*>\}\}(.*?)\{\{<\s*/\1\s*>\}\}"

    while re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, r"\2", content, flags=re.DOTALL)

    return re.sub(r"\{\{<\s*\w+\s*>\}\}", "", content)
