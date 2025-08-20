"""
This file is used to import all the functions from the modules and make them
available to the user.
Author: @julynx
"""

from .modules.convert import convert, live_convert, convert_text
from .__main__ import main

__version__ = "1.2.15"
__all__ = ["convert", "live_convert", "convert_text", "main"]
