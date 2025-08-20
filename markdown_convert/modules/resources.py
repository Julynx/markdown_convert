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

from .constants import BLUE, CYAN, GREEN, YELLOW, OPTIONS, OPTIONS_MODES
from .utils import color


def get_output_path(md_path, output_dir=None):
    """
    Get the output path for the pdf file.

    Args:
        md_path (str): The path to the markdown file.
        output_dir (str): The output directory.

    Returns:
        str: The output path.
    """
    md_path = Path(md_path)

    if output_dir is None:
        return md_path.parent / f"{md_path.stem}.pdf"

    output_dir = Path(output_dir)

    if output_dir.suffix == ".pdf":
        return output_dir

    return output_dir.parent / f"{Path(md_path).stem}.pdf"


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
    opt_1 = f"{color(BLUE, OPTIONS[1])}{color(CYAN, '=')}{color(CYAN, '|'.join(OPTIONS_MODES))}"
    opt_2 = (
        f"{color(BLUE, OPTIONS[2])}{color(CYAN, '=')}[{color(CYAN, 'css_file_path')}]"
    )
    opt_3 = f"{color(BLUE, OPTIONS[3])}{color(CYAN, '=')}[{color(CYAN, 'output_file_path')}]"

    usage = (
        "\n"
        "Usage:\n"
        f"  {commd}\n"
        "\n"
        "Options:\n"
        f"  {opt_1}\n"
        "    Convert the markdown file once (default) or live.\n"
        f"  {opt_2}\n"
        "    Use a custom CSS file.\n"
        f"  {opt_3}\n"
        "    Specify the output file path.\n"
    )
    return usage
