"""
Utility functions for regex based text processing.
"""

import re

CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]+`")
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
ASSET_LINK_RE = pattern = re.compile(
    r"!\[.*?\]\((.*?\.(?:png|jpg|jpeg|webp|gif|bmp|mp4|mov|avi|mkv))\)", 
    re.IGNORECASE
)


def protect_code(text: str):
    """
    Temporarily replaces code blocks and inline code with placeholders.

    Args:
        text (str): Input text.

    Returns:
        tuple[str, list[str]]: Modified text and list of protected code blocks.
    """
    protected = []

    def repl(match):
        protected.append(match.group(0))
        return f"@@CODE{len(protected)-1}@@"

    text = CODE_BLOCK_RE.sub(repl, text)
    text = INLINE_CODE_RE.sub(repl, text)
    return text, protected


def restore_code(text: str, protected: list):
    """
    Restores previously protected code blocks into the text.

    Args:
        text (str): Text with placeholders.
        protected (list): Original code blocks.

    Returns:
        str: Restored text.
    """
    for i, block in enumerate(protected):
        text = text.replace(f"@@CODE{i}@@", block)
    return text


def link_text(text: str, pages: set):
    """
    Wraps page names with [[...]] links.

    Args:
        text (str): Input text.
        pages (set): Set of known page names.

    Returns:
        tuple[str, int]: Modified text and number of replacements.
    """
    total_changes = 0

    for page in sorted(pages, key=len, reverse=True):
        pattern = (
            r"(?<!\[\[)"
            r"(?<!#)"
            r"(" + re.escape(page) + r")"
            r"([a-zäöüß]*)"
            r"(?!\]\])"
        )

        def repl(match):
            return f"[[{match.group(1)}]]{match.group(2)}"

        text, count = re.subn(pattern, repl, text)
        total_changes += count

    return text, total_changes
