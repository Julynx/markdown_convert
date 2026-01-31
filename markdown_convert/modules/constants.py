"""
This module contains the constants used in the markdown_convert package.
Author: @julynx
"""

from .extras import (
    CheckboxExtra,
    CustomSpanExtra,
    HighlightExtra,
    TocExtra,
    VegaExtra,
)

RED = "31"
GREEN = "32"
YELLOW = "33"
BLUE = "34"
MAGENTA = "35"
CYAN = "36"

OPTIONS = (
    "markdown_file_path",
    "--mode",
    "--css",
    "--out",
    "--extras",
    "-h",
    "--help",
)

OPTIONS_MODES = ("once", "live", "debug")

EXTRAS = {
    "fenced-code-blocks": {
        "provided-by": "markdown2",
        "args": None,
    },
    "header-ids": {
        "provided-by": "markdown2",
        "args": True,
    },
    "breaks": {
        "provided-by": "markdown2",
        "args": {"on_newline": True},
    },
    "tables": {
        "provided-by": "markdown2",
        "args": True,
    },
    "latex": {
        "provided-by": "markdown2",
        "args": True,
    },
    "mermaid": {
        "provided-by": "markdown2",
        "args": None,
    },
    "strike": {
        "provided-by": "markdown2",
        "args": None,
    },
    "admonitions": {
        "provided-by": "markdown2",
        "args": None,
    },
    "checkboxes": {
        "provided-by": "markdown-convert",
        "args": CheckboxExtra,
    },
    "custom-spans": {
        "provided-by": "markdown-convert",
        "args": CustomSpanExtra,
    },
    "highlights": {
        "provided-by": "markdown-convert",
        "args": HighlightExtra,
    },
    "toc": {
        "provided-by": "markdown-convert",
        "args": TocExtra,
    },
    "vega-lite": {
        "provided-by": "markdown-convert",
        "args": VegaExtra,
    },
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


def resolve_extras(extras_list=None):
    """
    Resolve the extras to be used in the conversion.

    Args:
        extras_list (list=None): List of extras to use. If None, all extras are used.

    Returns:
        dict: A dictionary containing the keys "markdown2_extras" and "markdown_convert_extras"
    """
    if extras_list is None:
        selected_extras = EXTRAS
    else:
        selected_extras = {
            key: value for key, value in EXTRAS.items() if key in extras_list
        }

    markdown2_extras = {
        extra: config["args"]
        for extra, config in selected_extras.items()
        if config["provided-by"] == "markdown2"
    }

    markdown_convert_extras = {
        config["args"]
        for _, config in selected_extras.items()
        if config["provided-by"] == "markdown-convert"
    }

    return {
        "markdown2_extras": markdown2_extras,
        "markdown_convert_extras": markdown_convert_extras,
    }
