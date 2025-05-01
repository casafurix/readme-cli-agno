"""Utility functions for Markdown generation."""

import urllib.parse
from typing import Dict, List, Optional


def generate_badge(
    label: str,
    message: str,
    color: str = "blue",
    style: str = "flat",
) -> str:
    """
    Generate a shield.io badge for the README.

    Args:
        label: Badge label (left side)
        message: Badge message (right side)
        color: Badge color (right side)
        style: Badge style

    Returns:
        Markdown for the badge
    """
    # URL encode the parameters
    label_encoded = urllib.parse.quote(label)
    message_encoded = urllib.parse.quote(message)

    # Create the shield.io URL
    badge_url = f"https://img.shields.io/badge/{label_encoded}-{message_encoded}-{color}?style={style}"

    # Generate the Markdown
    return f"![{label}]({badge_url})"


def create_code_block(
    code: str,
    language: str = "python",
) -> str:
    """
    Create a Markdown code block.

    Args:
        code: The code to include
        language: The programming language

    Returns:
        Formatted Markdown code block
    """
    return f"```{language}\n{code.strip()}\n```"


def create_table(
    headers: List[str],
    rows: List[List[str]],
) -> str:
    """
    Create a Markdown table.

    Args:
        headers: List of table headers
        rows: List of rows, each row being a list of strings

    Returns:
        Formatted Markdown table
    """
    # Create header row
    table = "| " + " | ".join(headers) + " |\n"

    # Create separator row
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    # Create data rows
    for row in rows:
        table += "| " + " | ".join(row) + " |\n"

    return table


def create_toc(sections: List[Dict[str, str]]) -> str:
    """
    Create a table of contents.

    Args:
        sections: List of sections, each being a dict with 'title' and 'level' keys

    Returns:
        Formatted Markdown TOC
    """
    toc = "## Table of Contents\n\n"

    for section in sections:
        title = section["title"]
        level = int(section.get("level", 2))

        # Create anchor
        anchor = title.lower().replace(" ", "-").replace(".",
                                                         "").replace("(", "").replace(")", "")

        # Add indentation based on header level
        indent = "  " * (level - 2) if level > 2 else ""

        toc += f"{indent}- [{title}](#{anchor})\n"

    return toc
