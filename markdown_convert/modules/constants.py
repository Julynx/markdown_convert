"""
This module contains the constants used in the markdown_convert package.
Author: @julynx
"""

RED = "31"
GREEN = "32"
YELLOW = "33"
BLUE = "34"
MAGENTA = "35"
CYAN = "36"

OPTIONS = ("markdown_file_path", "--mode", "--css", "--out", "-h", "--help")

OPTIONS_MODES = ("once", "live", "debug")

MARKDOWN_EXTENSIONS = {
    "fenced-code-blocks": None,
    "header-ids": True,
    "breaks": {"on_newline": True},
    "tables": True,
    "latex": True,
    "mermaid": None,
    "strike": None,
    "admonitions": None,
}

BROWSER_ARGS = [
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
]

CSP_TEMPLATE = (
    "default-src 'none'; "
    "script-src 'nonce-{nonce}' https://cdn.jsdelivr.net; "  # <- Script for Mermaid diagrams
    "script-src-elem 'nonce-{nonce}' https://cdn.jsdelivr.net; "
    "style-src 'unsafe-inline'; "
    "img-src data: https: file:; "
    "font-src data: https:; "
    "connect-src https://cdn.jsdelivr.net;"
)

PDF_PARAMS = {
    "format": "A4",
    "print_background": True,
    "margin": {
        "top": "20mm",
        "bottom": "20mm",
        "left": "20mm",
        "right": "20mm",
    },
    "path": None,  # <- Replace with actual output path when used
}
