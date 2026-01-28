"""
Module for transforming HTML content.
"""

import re

from bs4 import BeautifulSoup
from .extras import create_checkbox, create_highlight, create_custom_span, create_toc


def create_html_document(html_content, css_content, csp):
    """
    Creates a complete HTML document with the given content, CSS, and Content Security Policy.
    Args:
        html_content (str): The HTML content to include in the body.
        css_content (str): The CSS styles to include in the head.
        csp (str): The Content Security Policy string.
    Returns:
        str: A complete HTML document as a string.
    """
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="Content-Security-Policy" content="{csp or ""}">
<style>
{css_content or ""}
</style>
</head>
<body>
{html_content or ""}
</body>
</html>"""


def create_sections(html_string):
    """
    Wraps each h2 or h3 and its following content in a <section> tag.
    The section ends when the next h2 or h3 is encountered, or the parent ends.

    Args:
        html_string (str): The input HTML string.
    Returns:
        str: The modified HTML string with sections wrapped.
    """
    soup = BeautifulSoup(html_string, "html.parser")

    for header in soup.find_all(["h2", "h3"]):
        new_section = soup.new_tag("section")
        header.insert_before(new_section)

        current = header
        while current is not None and (
            current == header or current.name not in ["h2", "h3"]
        ):
            next_sibling = current.next_sibling
            new_section.append(current)
            current = next_sibling

    return str(soup)


def render_mermaid_diagrams(html, *, nonce):
    """
    Renders Mermaid diagrams in the HTML content.

    Args:
        html (str): HTML content.
        nonce (str): Cryptographic nonce for CSP.
    Returns:
        str: HTML content with rendered Mermaid diagrams.
    """
    mermaid_script = f"""
<script type="module" nonce="{nonce}">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'default',
    themeVariables: {{}},
    fontFamily: 'arial, verdana, sans-serif'
  }});
</script>
"""

    if '<div class="mermaid">' in html:
        html = mermaid_script + html

    return html


def render_extra_features(html):
    """
    Renders extra features like checkboxes, highlights, and custom spans in the HTML content.

    Args:
        html (str): HTML content.
    Returns:
        str: HTML content with extra features rendered.
    """

    handlers = {
        "checkbox": create_checkbox,
        "highlight": create_highlight,
        "span": create_custom_span,
        "toc": create_toc,
    }

    master_pattern = re.compile(
        r"(?P<checkbox>\[\s\]|\[x\])|"
        r"(?P<highlight>==(?P<hl_content>.*?)==)|"
        r"(?P<span>(?P<cls>[a-zA-Z0-9_-]+)\{\{\s*(?P<sp_content>.*?)\s*\}\})|"
        r"(?P<toc>\[TOC(?:\s+depth=(?P<depth>\d+))?\])"
    )

    ignored_tags = {"code", "pre", "script", "style"}

    soup = BeautifulSoup(html, "html.parser")
    for text_node in soup.find_all(string=True):
        # Ignore text nodes within certain tags
        if text_node.parent.name in ignored_tags:
            continue

        # If no match, skip processing
        content = text_node.string
        if not master_pattern.search(content):
            continue

        new_nodes = []
        last_end = 0
        for match in master_pattern.finditer(content):
            start, end = match.span()

            # Append text before the match
            if start > last_end:
                new_nodes.append(content[last_end:start])

            kind = match.lastgroup

            # Call the appropriate handler
            handler = handlers.get(kind)
            if handler:
                try:
                    tag = handler(soup, match)
                    new_nodes.append(tag)
                except Exception as exc:
                    print(f"Warning: Handler for '{kind}' failed with exception: {exc}")
                    new_nodes.append(match.group(0))

            last_end = end

        # Append any remaining text after the last match
        if new_nodes:
            if last_end < len(content):
                new_nodes.append(content[last_end:])

            text_node.replace_with(*new_nodes)

    return str(soup)
