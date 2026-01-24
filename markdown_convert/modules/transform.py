"""
Module for transforming HTML content.
"""

import re

from bs4 import BeautifulSoup


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
    Avoids wrapping h2 tags that are inside <code> blocks.

    Args:
        html_string (str): The input HTML string.
    Returns:
        str: The modified HTML string with h2 sections wrapped.
    """
    soup = BeautifulSoup(html_string, "html.parser")

    for second_level_header in soup.find_all("h2"):
        new_section = soup.new_tag("section")
        second_level_header.insert_before(new_section)

        current = second_level_header
        while current is not None and (
            current == second_level_header or current.name != "h2"
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

    # Split by code blocks to avoid processing text inside them
    parts = re.split(r"(<code>.*?</code>)", html, flags=re.DOTALL)
    for part_index, _part in enumerate(parts):
        # Only process parts that are NOT code blocks
        if not parts[part_index].startswith("<code>"):
            parts[part_index] = parts[part_index].replace(unchecked, unchecked_html)
            parts[part_index] = parts[part_index].replace(checked, checked_html)

    return "".join(parts)


def create_spans(html):
    """
    Renders custom spans in the HTML content by replacing classname{{ content }} tags.
    Args:
        html (str): HTML content.
    Returns:
        str: HTML content with rendered custom spans.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Regex to match classname{{ content }}
    # It captures the class name and the content
    pattern = re.compile(r"([a-zA-Z0-9_-]+){{\s*(.*?)\s*}}")

    # We need to find all text nodes and replace the pattern
    for text_node in soup.find_all(string=True):
        # Skip text nodes inside code, pre, script, style tags
        if text_node.parent.name in ["code", "pre", "script", "style"]:
            continue

        content = str(text_node)
        if "{{" in content:
            new_content_nodes = []
            last_end = 0
            for match in pattern.finditer(content):
                # Add text before the match
                before = content[last_end : match.start()]
                if before:
                    new_content_nodes.append(soup.new_string(before))

                # Create the new span tag
                class_name = match.group(1)
                inner_text = match.group(2)
                new_span = soup.new_tag("span", attrs={"class": class_name})
                new_span.string = inner_text
                new_content_nodes.append(new_span)

                last_end = match.end()

            # Add remaining text after the last match
            after = content[last_end:]
            if after:
                new_content_nodes.append(soup.new_string(after))

            if new_content_nodes:
                # Replace the original text node with the new nodes
                for node in reversed(new_content_nodes):
                    text_node.insert_after(node)
                text_node.extract()

    return str(soup)
