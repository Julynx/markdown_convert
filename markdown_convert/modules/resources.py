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

from .constants import (
    BLUE,
    CYAN,
    EXTRAS,
    GREEN,
    OPTIONS,
    OPTIONS_MODES,
    OPTIONS_SECURITY,
    YELLOW,
)
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

    def _wrap_by_length(items: list, max_len=20, indent="  "):
        if not items:
            return ""

        lines = []
        current_line = []
        current_length = 0

        for item in items:
            item_len = len(item) + (1 if current_line else 0)

            if current_length + item_len > max_len and current_line:
                lines.append(",".join(current_line) + ",")
                current_line = [item]
                current_length = len(item)
            else:
                current_line.append(item)
                current_length += item_len

        if current_line:
            lines.append(",".join(current_line))

        return indent + f"\n{indent}".join(lines)

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
    option_four = f"{color(BLUE, OPTIONS[4])}{color(CYAN, '=')}[{color(CYAN, 'extra1,extra2,...')}]"
    extras_str = _wrap_by_length(list(EXTRAS.keys()), max_len=60, indent="        ")
    option_five = f"{color(BLUE, OPTIONS[5])}{color(CYAN, '=')}{color(CYAN, '|'.join(OPTIONS_SECURITY))}"

    usage = (
        "\n"
        "Usage:\n"
        f"  {commd}\n"
        "\n"
        "Options:\n"
        f"  {option_one}\n"
        "      Convert the markdown file once (default) or live.\n"
        "      Use debug to preserve the intermediate html file.\n"
        f"  {option_two}\n"
        "      Use a custom CSS file.\n"
        f"  {option_three}\n"
        "      Specify the output file path.\n"
        f"  {option_four}\n"
        "      Specify the extras to use. Uses all extras if not specified.\n"
        f"      Supported extras:\n{extras_str}\n"
        f"  {option_five}\n"
        "      Specify the security level.\n"
        "      Strict mode disables inline HTML, internet access and JS,\n"
        "      but local files can still be referenced.\n"
        "      This improves security, but will break some extras.\n"
    )
    return usage
