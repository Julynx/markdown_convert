"""
This module contains functions to validate the input paths.
Author: @julynx
"""

from pathlib import Path


def validate_markdown_path(md_path):
    """
    Validate the markdown file path.

    Args:
        md_path (str): The path to the markdown file.

    Raises:
        FileNotFoundError: If the file is not found.
        ValueError: If the file is not a Markdown file.
    """
    if not Path(md_path).is_file():
        raise FileNotFoundError(f"File not found: '{md_path}'")

    if not md_path.endswith(".md"):
        raise ValueError("File must be a Markdown file.")


def validate_css_path(css_path):
    """
    Validate the CSS file path.

    Args:
        css_path (str): The path to the CSS file.

    Raises:
        FileNotFoundError: If the file is not found.
        ValueError: If the file is not a CSS file.
    """
    if not Path(css_path).is_file():
        raise FileNotFoundError(f"File not found: '{css_path}'")

    if not css_path.endswith(".css"):
        raise ValueError("File must be a CSS file.")


def validate_output_path(output_dir):
    """
    Validate the output directory path.

    Args:
        output_dir (str): The path to the output directory.

    Raises:
        FileNotFoundError: If the directory is not found.
    """
    check_dir = Path(output_dir)

    if output_dir.endswith(".pdf"):
        check_dir = check_dir.parent

    if not check_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: '{check_dir}'")
