"""
This module contains the constants used in the markdown_convert package.
Author: @julynx
"""

RED = '31'
GREEN = '32'
YELLOW = '33'
BLUE = '34'
MAGENTA = '35'
CYAN = '36'

OPTIONS = ('markdown_file_path',
           "--mode",
           '--css',
           "--out",
           "-h", "--help")

OPTIONS_MODES = ('once', 'live')

MD_EXTENSIONS = ["fenced-code-blocks",
                 "header-ids",
                 "tables"]
