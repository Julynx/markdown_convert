"""
Utility functions for string manipulation.
Author: @julynx
"""


def color(color_code, text):
    """
    Colorize text.

    Args:
        text (str): The text to colorize.
        color (str): The color code.

    Returns:
        str: The colorized text.
    """
    return f"\033[{color_code}m{text}\033[0m"
