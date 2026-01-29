"""
Module for transforming HTML content.
"""

import re

from bs4 import BeautifulSoup

from .extras import (
    apply_extras,
    ExtraFeature,
    CheckboxExtra,
    CustomSpanExtra,
    HighlightExtra,
    TocExtra,
    VegaExtra,
)


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
    Wraps each h2 and its following content in a <section> tag.
    The section ends when the next h2 is encountered, or the parent ends.

    Args:
        html_string (str): The input HTML string.
    Returns:
        str: The modified HTML string with sections wrapped.
    """
    soup = BeautifulSoup(html_string, "html.parser")

    for header in soup.find_all("h2"):
        new_section = soup.new_tag("section")
        header.insert_before(new_section)

        current = header
        while current is not None and (current == header or current.name != "h2"):
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


def render_extra_features(
    html,
    extras: set[ExtraFeature] = (
        CheckboxExtra,
        CustomSpanExtra,
        HighlightExtra,
        TocExtra,
        VegaExtra,
    ),
):
    """
    Renders extra features by protecting specific tags, applying regex
    transformations, and restoring the protected content.
    """
    placeholders = {}

    def stash(match):
        key = f"__PROTECTED_BLOCK_{len(placeholders)}__"
        placeholders[key] = match.group(0)
        return key

    # 0. Pre protection extras
    html = apply_extras(extras, html, before_stash=True)

    # 1. Protection: Replace ignored tags with unique hashes
    ignored_pattern = re.compile(
        r"<(code|pre|script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE
    )
    html = ignored_pattern.sub(stash, html)

    # 2. Transformations: Define patterns and their replacements
    html = apply_extras(extras, html, before_stash=False)

    # 3. Restoration: Replace hashes back with original content
    for key, original_content in placeholders.items():
        html = html.replace(key, original_content)

    return html
