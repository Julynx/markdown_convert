"""
Module for transforming HTML content.
"""

import re


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
<meta http-equiv="Content-Security-Policy" content="{csp}">
<style>
{css_content}
</style>
</head>
<body>
{html_content}
</body>
</html>"""


def create_sections(html):
    """
    Creates h2 sections, from the first h2 to the next h2, wrapping them in <section> tags
    using regular expressions.
    Args:
        html (str): HTML content.
    Returns:
        HTML content with sections wrapped in <section> tags.
    """
    pattern = re.compile(r"(<h2.*?>.*?</h2>)(.*?)(?=(<h2.*?>|$))", re.DOTALL)

    def wrap_section(match):
        return f"<section>\n{match.group(1)}\n{match.group(2)}\n</section>\n"

    return pattern.sub(wrap_section, html)


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


def render_checkboxes(html):
    """
    Renders checkboxes in the HTML content by replacing input elements with SVG representations.
    Args:
        html (str): HTML content.
    Returns:
        str: HTML content with rendered checkboxes.
    """
    unchecked = "[ ]"
    checked = "[x]"

    unchecked_html = "<input type='checkbox'>"
    checked_html = "<input type='checkbox' checked>"

    html = html.replace(unchecked, unchecked_html)
    html = html.replace(checked, checked_html)
    return html
