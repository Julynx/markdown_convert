"""
Extras are defined as helper functions called by
render_extra_features from transform.py
"""

import json
import re

import vl_convert as vlc
from bs4 import BeautifulSoup, Tag
from ruamel.yaml import YAML


class ExtraFeature:
    """
    Base class for extra features that can be applied to HTML.

    Attributes:
        pattern (str): Regex pattern to match the extra feature in the HTML.
        run_before_stash (bool): Whether to run this extra before stashing code blocks.
    """

    pattern = r""
    run_before_stash = False

    def replace(self, match, html):
        """
        Replaces the matched pattern with the rendered extra feature.

        Args:
            match (re.Match): The regex match object.
            html (str): The full HTML content.

        Returns:
            str: The replacement string.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the replace method.")


class CheckboxExtra(ExtraFeature):
    """
    Extra feature for rendering checkboxes.
    """

    pattern = r"(?P<checkbox>\[\s\]|\[x\])"

    def replace(match, html):
        """
        Render a tag for a checkbox.

        Args:
            match: Element identified as a checkbox
        Returns:
            str: tag representing the checkbox
        """
        status = "checked" if "[x]" in match.group("checkbox") else ""
        return f'<input type="checkbox" {status}>'


class HighlightExtra(ExtraFeature):
    """
    Extra feature for rendering highlighted text.
    """

    pattern = r"==(?P<content>.*?)=="

    def replace(match, html):
        """
        Render a tag for a highlight.

        Args:
            match: Element identified as a highlight
        Returns:
            str: tag representing the highlight
        """
        content = match.group("content")
        return f'<span class="highlight">{content}</span>'


class CustomSpanExtra(ExtraFeature):
    """
    Extra feature for rendering custom spans with specific classes.
    """

    pattern = r"(?P<cls>[a-zA-Z0-9_-]+)\{\{\s*(?P<content>.*?)\s*\}\}"

    def replace(match, html):
        """
        Render a tag for a custom span.

        Args:
            match: Element identified as a custom span
        Returns:
            str: tag representing the custom span
        """
        cls = match.group("cls")
        content = match.group("content")
        return f'<span class="{cls}">{content}</span>'


class TocExtra(ExtraFeature):
    """
    Extra feature for rendering a Table of Contents.
    """

    pattern = r"\[TOC(?:\s+depth=(?P<depth>\d+))?\]"

    def replace(match, html):
        """
        Render a tag for a table of contents

        Args:
            match: Element identified as a table of contents
        Returns:
            str: tag representing the table of contents
        """
        soup = BeautifulSoup(html, "html.parser")
        max_level = match.group("depth")
        max_level = 3 if max_level is None else int(max_level)

        headers = [
            header
            for header in soup.find_all(
                [f"h{index}" for index in range(1, max_level + 1)]
            )
            if header.get("id")
        ]
        if not headers:
            return ""

        tag: Tag = soup.new_tag("ul", attrs={"class": "toc"})
        active_list = {0: tag}
        last_list_element = {}

        for header in headers:
            level = int(header.name[1])

            if level not in active_list:
                parent_lvl = max(key for key in active_list if key < level)
                if last_list_element.get(parent_lvl):
                    sub_list = soup.new_tag("ul")
                    last_list_element[parent_lvl].append(sub_list)
                    active_list[level] = sub_list
                else:
                    active_list[level] = active_list[parent_lvl]

            active_list = {
                key: value for key, value in active_list.items() if key <= level
            }

            list_item = soup.new_tag("li")
            link = soup.new_tag("a", href=f"#{header['id']}")
            link.string = header.get_text(strip=True)
            list_item.append(link)

            active_list[level].append(list_item)
            last_list_element[level] = list_item

        return tag.prettify()


class VegaExtra(ExtraFeature):
    """
    Extra feature for rendering Vega-Lite diagrams from JSON or YAML.
    """

    pattern = (
        r"<pre[^>]*>"
        r"<code[^>]*class=[\"'][^\"]*language-vega[^\"]*[\"'][^>]*>"
        r"(?P<content>.*?)"
        r"</code>"
        r"</pre>"
    )
    run_before_stash = True

    def replace(match, html):
        """
        Render a tag for a vega lite diagram from JSON or YAML.

        Args:
            match (re.Match): Element identified as a vega lite diagram.
            html (str): The full HTML content.

        Returns:
            str: SVG tag representing the vega lite diagram.
        """
        content = match.group("content")
        spec = None

        try:
            spec = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            try:
                yaml = YAML(typ="safe")
                spec = yaml.load(content)
            except Exception as exc:
                print(f"WARNING: Failed to parse Vega-Lite spec: {exc}")
                return match.group(0)

        if spec is None:
            return match.group(0)

        try:
            tag = vlc.vegalite_to_svg(spec)
            return f"<div class='vega-lite'>{tag}</div>"
        except Exception as exc:
            print(f"WARNING: Failed to convert Vega-Lite spec to SVG: {exc}")
            return match.group(0)


def apply_extras(extras: set[ExtraFeature], html, before_stash=False):
    """
    Applies extra features to an html string.
    Args:
        extras: set[ExtraFeature] Extra features to apply
        html: complete html text, used by some extras like TOC.
    Returns:
        str: The updated html.
    """
    for extra in extras:
        if not extra.run_before_stash == before_stash:
            continue

        # Loop until the pattern no longer matches
        while re.search(extra.pattern, html, flags=re.DOTALL):
            new_html = html
            try:
                new_html = re.sub(
                    extra.pattern,
                    lambda match: extra.replace(match, html=html),
                    html,
                    flags=re.DOTALL,
                )
            except Exception as exc:
                print(
                    f"WARNING: An exception occurred while trying to apply an extra:\n{exc}"
                )
                pass

            # Safety break:
            if new_html == html:
                break
            html = new_html

    return html
