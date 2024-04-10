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


def drop_duplicates(lst):
    """
    Drops duplicates from the given list.

    Args:
        lst: List to remove duplicates from.

    Returns:
        List without duplicates.
    """
    return list(dict.fromkeys(lst))
