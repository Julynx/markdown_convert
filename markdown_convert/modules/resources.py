"""
This module contains functions that are used to get the output path, the CSS
path, and the usage message.
Author: @julynx
"""

from pathlib import Path

try:
    # Python 3.9+
    from importlib.resources import files
except ImportError:
    # Fallback for older Python versions
    from importlib_resources import files

from .constants import BLUE, CYAN, GREEN, OPTIONS, OPTIONS_MODES, YELLOW
from .utils import color


def get_output_path(markdown_path, output_dir=None):
    """
    Get the output path for the pdf file.

    Args:
        markdown_path (str): The path to the markdown file.
        output_dir (str): The output directory.

    Returns:
        str: The output path.
    """
    markdown_path = Path(markdown_path)

    if output_dir is None:
        return markdown_path.parent / f"{markdown_path.stem}.pdf"

    output_dir = Path(output_dir)

    if output_dir.suffix == ".pdf":
        return output_dir

    return output_dir.parent / f"{Path(markdown_path).stem}.pdf"


def get_css_path():
    """
    Get the path to the default CSS file.

    Returns:
        str: The path to the default CSS file.
    """
    package_files = files("markdown_convert")
    css_file = package_files / "default.css"
    return str(css_file)


def get_code_css_path():
    """
    Get the path to the code CSS file.

    Returns:
        str: The path to the code CSS file.
    """
    package_files = files("markdown_convert")
    css_file = package_files / "code.css"
    return str(css_file)


def get_usage():
    """
    Returns a message describing how to use the program.

    Returns:
        str: The usage message.
    """
    commd = (
        f"{color(GREEN, 'markdown-convert')} "
        f"[{color(YELLOW, OPTIONS[0])}] [{color(BLUE, 'options')}]"
    )
    option_one = (
        f"{color(BLUE, OPTIONS[1])}{color(CYAN, '=')}"
        f"{color(CYAN, '|'.join(OPTIONS_MODES))}"
    )
    option_two = (
        f"{color(BLUE, OPTIONS[2])}{color(CYAN, '=')}[{color(CYAN, 'css_file_path')}]"
    )
    option_three = f"{color(BLUE, OPTIONS[3])}{color(CYAN, '=')}[{color(CYAN, 'output_file_path')}]"

    usage = (
        "\n"
        "Usage:\n"
        f"  {commd}\n"
        "\n"
        "Options:\n"
        f"  {option_one}\n"
        "    Convert the markdown file once (default) or live.\n"
        f"  {option_two}\n"
        "    Use a custom CSS file.\n"
        f"  {option_three}\n"
        "    Specify the output file path.\n"
    )
    return usage
