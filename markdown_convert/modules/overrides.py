"""
Overrides for markdown2.
"""

import markdown2


def tags(self, lexer_name: str) -> tuple[str, str]:
    """
    Overrides markdown2.FencedCodeBlocks.tags

    Provides support for the fenced code blocks language attribute without
    the need to have the highlightjs-lang extension enabled.
    """
    pre_class = self.md._html_class_str_from_tag("pre")
    if lexer_name:
        code_class = f' class="{lexer_name} language-{lexer_name}"'
    else:
        code_class = self.md._html_class_str_from_tag("code")
    return (f"<pre{pre_class}><code{code_class}>", "</code></pre>")


def _convert_double_match(self, match):
    """
    Overrides markdown2.Latex._convert_double_match

    Fixes bug #674 of latex macros that start with backslash n not being
    properly rendered.
    """
    return self.converter.convert(match.group(1).replace("\n", " "), display="block")


# Apply overrides on module import and expose markdown2
markdown2.FencedCodeBlocks.tags = tags
markdown2.Latex._convert_double_match = _convert_double_match
__all__ = ["markdown2"]
