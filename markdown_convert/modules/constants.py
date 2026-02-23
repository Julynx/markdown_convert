"""
This module contains the constants used in the markdown_convert package.
Author: @julynx
"""

from mdit_py_plugins.admon import admon_plugin
from mdit_py_plugins.anchors import anchors_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from .extras import (
    BlockMathExtra,
    CustomSpanExtra,
    DynamicQueryExtra,
    DynamicTableExtra,
    HighlightExtra,
    InlineMathExtra,
    MermaidExtra,
    SchemDrawExtra,
    SyntaxHighlightExtra,
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
    "--security",
    "-h",
    "--help",
)

OPTIONS_MODES = ("once", "live", "debug")

OPTIONS_SECURITY = ("default", "strict")

EXTRAS = {
    "admonitions": {
        "provided-by": "markdown-it",
        "extra": admon_plugin,
    },
    "anchors": {
        "provided-by": "markdown-it",
        "extra": anchors_plugin,
    },
    "task-lists": {
        "provided-by": "markdown-it",
        "extra": tasklists_plugin,
    },
    "math": {
        "provided-by": "markdown-it",
        "extra": dollarmath_plugin,
        "args": {
            "double_inline": True,
        },
    },
    "custom-spans": {
        "provided-by": "markdown-convert",
        "extra": CustomSpanExtra,
    },
    "highlights": {
        "provided-by": "markdown-convert",
        "extra": HighlightExtra,
    },
    "syntax-highlighting": {
        "provided-by": "markdown-convert",
        "extra": SyntaxHighlightExtra,
    },
    "table-of-contents": {
        "provided-by": "markdown-convert",
        "extra": TocExtra,
    },
    "vega-lite": {
        "provided-by": "markdown-convert",
        "extra": VegaExtra,
    },
    "inline-math": {
        "provided-by": "markdown-convert",
        "extra": InlineMathExtra,
    },
    "block-math": {
        "provided-by": "markdown-convert",
        "extra": BlockMathExtra,
    },
    "schemdraw": {
        "provided-by": "markdown-convert",
        "extra": SchemDrawExtra,
    },
    "mermaid": {
        "provided-by": "markdown-convert",
        "extra": MermaidExtra,
    },
    "dynamic-tables": {
        "provided-by": "markdown-convert",
        "extra": DynamicTableExtra,
    },
    "dynamic-queries": {
        "provided-by": "markdown-convert",
        "extra": DynamicQueryExtra,
    },
}

BROWSER_ARGS = [
    "--disable-dev-shm-usage",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--no-zygote",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-sync",
    "--disable-translate",
    "--hide-scrollbars",
    "--metrics-recording-only",
    "--mute-audio",
    "--safebrowsing-disable-auto-update",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding",
    "--disable-background-timer-throttling",
]

CSP_TEMPLATE = (
    "default-src 'none'; "
    "script-src 'nonce-{nonce}' https://cdn.jsdelivr.net; "  # <- Script for Mermaid
    "script-src-elem 'nonce-{nonce}' https://cdn.jsdelivr.net; "
    "style-src 'unsafe-inline'; "
    "img-src data: https: file:; "
    "font-src data: https: file:; "
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
        dict: A dictionary containing the keys "markdown_it_extras" and
              "markdown_convert_extras"
    """
    if extras_list is None:
        selected_extras = EXTRAS
    else:
        selected_extras = {
            key: value for key, value in EXTRAS.items() if key in extras_list
        }

    markdown_it_extras = tuple(
        value
        for value in selected_extras.values()
        if value["provided-by"] == "markdown-it"
    )
    markdown_convert_extras = tuple(
        value
        for value in selected_extras.values()
        if value["provided-by"] == "markdown-convert"
    )

    return {
        "markdown_it_extras": markdown_it_extras,
        "markdown_convert_extras": markdown_convert_extras,
    }
