import re

MERMAID_SCRIPT = """
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>
"""


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


def render_mermaid_diagrams(html):
    """
    Renders Mermaid diagrams in the HTML content.

    Args:
        html (str): HTML content.
    Returns:
        str: HTML content with rendered Mermaid diagrams.
    """
    if '<div class="mermaid">' in html:
        html = MERMAID_SCRIPT + html

    return html
