"""
Utility functions for string manipulation.
Author: @julynx
"""

import platform


def color(color_code, text):
    """
    Colorize text.

    Args:
        text (str): The text to colorize.
        color (str): The color code.

    Returns:
        str: The colorized text.
    """

    # Disable if running on Windows
    if platform.system() == "Windows":
        return text

    return f"\033[{color_code}m{text}\033[0m"
