"""
Module for transforming HTML content.
"""

import re

from bs4 import BeautifulSoup
from string_grab import grab

from .extras import ExtraFeature, apply_extras


def create_html_document(html_content, css_content, csp):
    """
    Creates a complete HTML document with the given content, CSS, and
    Content Security Policy.
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
    securityLevel: 'strict',
    theme: 'default',
    themeVariables: {{}},
    fontFamily: 'arial, verdana, sans-serif'
  }});
</script>
"""
    if '<code class="language-mermaid">' in html:
        html = mermaid_script + html

    return html


def render_extra_features(html, extras: set[ExtraFeature]):
    """
    Renders extra features by protecting specific tags, applying regex
    transformations, and restoring the protected content.
    """
    memory = {}

    try:
        placeholders = {}

        # Sort extras by phase
        sorted_extras = sorted(extras, key=lambda e: getattr(e, "execution_phase", 100))
        bypass_stashing_classes = [
            extra.bypass_stashing_class
            for extra in extras
            if extra.bypass_stashing_class
        ]

        # Partition into pre-stash and post-stash groups
        pre_stash_extras = [
            extra
            for extra in sorted_extras
            if getattr(extra, "execution_phase", 100) < 50
        ]
        post_stash_extras = [
            extra
            for extra in sorted_extras
            if getattr(extra, "execution_phase", 100) >= 50
        ]

        def stash(match):
            text = match.group(0)
            try:
                classes = grab(
                    text,
                    start='<pre><code class="',
                    end='"',
                )
                if any(cls in classes for cls in bypass_stashing_classes):
                    return text
            except LookupError:
                pass

            key = f"__PROTECTED_BLOCK_{len(placeholders)}__"
            placeholders[key] = text
            return key

        # 0. Pre protection extras (e.g., Diagrams)
        html = apply_extras(pre_stash_extras, html, memory)

        # 1. Protection: Replace ignored tags with unique hashes
        ignored_pattern = re.compile(
            r"<(code|pre|script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE
        )
        html = ignored_pattern.sub(stash, html)

        # 2. Transformations: Define patterns and their replacements
        html = apply_extras(post_stash_extras, html, memory)

        # 3. Restoration: Replace hashes back with original content
        for key, original_content in placeholders.items():
            html = html.replace(key, original_content)

        return html

    finally:
        conn = memory.get("duckdb")
        if conn:
            conn.close()
        memory = {}
