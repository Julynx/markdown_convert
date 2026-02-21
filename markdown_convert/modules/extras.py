"""
Extras are defined as helper functions called by
render_extra_features from transform.py
"""

import html
import json
import logging
import re
from io import StringIO

import duckdb
import pandas as pd
import vl_convert
from bs4 import BeautifulSoup, Tag
from ruamel.yaml import YAML
from yaml_to_schemdraw import from_yaml_string

logger = logging.getLogger(__name__)


class ExtraFeature:
    """
    Base class for extra features that can be applied to HTML.

    Attributes:
        pattern (str): Regex pattern to match the extra feature in the HTML.
        run_before_stash (bool): Whether to run this extra before stashing code blocks.
        memory (dict): Shared ephemeral state across all extras during a single
            document conversion. Managed by render_extra_features in transform.py.
    """

    pattern = r""
    run_before_stash = False
    memory: dict = {}

    @staticmethod
    def replace(match, html_content):
        """
        Replaces the matched pattern with the rendered extra feature.

        Args:
            match (re.Match): The regex match object.
            html_content (str): The full HTML content.

        Returns:
            str: The replacement string.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement the replace method.")


class CheckboxExtra(ExtraFeature):
    """Extra feature for rendering checkboxes."""

    pattern = r"(?P<checkbox>\[\s\]|\[x\])"

    @staticmethod
    def replace(match, html_content):
        """
        Render a tag for a checkbox.

        Args:
            match: Element identified as a checkbox.
        Returns:
            str: Tag representing the checkbox.
        """
        status = "checked" if "[x]" in match.group("checkbox") else ""
        return f'<input type="checkbox" {status}>'


class HighlightExtra(ExtraFeature):
    """Extra feature for rendering highlighted text."""

    pattern = r"==(?P<content>.*?)=="

    @staticmethod
    def replace(match, html_content):
        """
        Render a tag for a highlight.

        Args:
            match: Element identified as a highlight.
        Returns:
            str: Tag representing the highlight.
        """
        content = match.group("content")
        return f'<span class="highlight">{content}</span>'


class CustomSpanExtra(ExtraFeature):
    """Extra feature for rendering custom spans with specific classes."""

    pattern = r"(?P<cls>[a-zA-Z0-9_-]+)\{\{\s*(?P<content>.*?)\s*\}\}"

    @staticmethod
    def replace(match, html_content):
        """
        Render a tag for a custom span.

        Args:
            match: Element identified as a custom span.
        Returns:
            str: Tag representing the custom span.
        """
        cls = match.group("cls")
        content = match.group("content")
        return f'<span class="{cls}">{content}</span>'


class TocExtra(ExtraFeature):
    """Extra feature for rendering a Table of Contents."""

    pattern = r"\[TOC(?:\s+depth=(?P<depth>\d+))?\]"

    @staticmethod
    def replace(match, html_content):
        """
        Render a tag for a table of contents.

        Args:
            match: Element identified as a table of contents.
        Returns:
            str: Tag representing the table of contents.
        """
        soup = BeautifulSoup(html_content, "html.parser")
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
    """Extra feature for rendering Vega-Lite diagrams from JSON or YAML."""

    pattern = (
        r"<pre[^>]*>"
        r"<code[^>]*class=[\"'][^\"]*language-vega[^\"]*[\"'][^>]*>"
        r"(?P<content>.*?)"
        r"</code>"
        r"</pre>"
    )
    run_before_stash = True

    @staticmethod
    def replace(match, html_content):
        """
        Render a tag for a vega-lite diagram from JSON or YAML.

        Args:
            match (re.Match): Element identified as a vega-lite diagram.
            html_content (str): The full HTML content.

        Returns:
            str: SVG tag representing the vega-lite diagram.
        """
        content = match.group("content")
        spec = None

        try:
            spec = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            try:
                yaml = YAML(typ="safe")
                spec = yaml.load(content)
            except Exception:
                logger.warning("Failed to parse Vega-Lite spec", exc_info=True)
                return match.group(0)

        if spec is None:
            return match.group(0)

        try:
            tag = vl_convert.vegalite_to_svg(spec)
            return f"<div class='vega-lite'>{tag}</div>"
        except Exception:
            logger.warning("Failed to convert Vega-Lite spec to SVG", exc_info=True)
            return match.group(0)


class SchemDrawExtra(ExtraFeature):
    """Extra feature for rendering schemdraw diagrams from JSON or YAML."""

    pattern = (
        r"<pre[^>]*>"
        r"<code[^>]*class=[\"'][^\"]*language-schemdraw[^\"]*[\"'][^>]*>"
        r"(?P<content>.*?)"
        r"</code>"
        r"</pre>"
    )
    run_before_stash = True

    @staticmethod
    def replace(match, html_content):
        """
        Render a tag for a schemdraw diagram from JSON or YAML.

        Args:
            match (re.Match): Element identified as a schemdraw diagram.
            html_content (str): The full HTML content.

        Returns:
            str: SVG tag representing the schemdraw diagram.
        """
        content = match.group("content")
        try:
            diagram = from_yaml_string(content)
            return f"<div class='schemdraw'>{diagram.get_imagedata('svg').decode('utf-8')}</div>"
        except Exception:
            logger.warning("Failed to convert schemdraw diagram", exc_info=True)
            return match.group(0)


class DuckDBTableExtra(ExtraFeature):
    """
    Extra feature for registering HTML tables as named DuckDB tables.

    Matches a <table> immediately followed by a <blockquote> containing a
    bracketed name like [students]. The table data is parsed and loaded into
    an in-memory DuckDB connection with filesystem access disabled.
    """

    pattern = (
        r"(?P<table><table\b[^>]*>(?:(?!<table\b).)*?</table>)"
        r"\s*<blockquote>\s*<p>"
        r"\[(?P<name>[a-zA-Z_]\w*)\]"
        r"\s*(?P<description>.*?)"
        r"</p>\s*</blockquote>"
    )
    run_before_stash = True

    @staticmethod
    def replace(match, html_content):
        """
        Parse the matched HTML table and register it in DuckDB.

        Args:
            match (re.Match): The regex match containing the table HTML and name.
            html_content (str): The full HTML content.

        Returns:
            str: The original table HTML without the blockquote naming tag.
        """
        table_html = match.group("table")
        table_name = match.group("name")

        try:
            dfs = pd.read_html(StringIO(table_html))
            if not dfs:
                raise ValueError("No tables found in HTML")

            df = dfs[-1]
            conn = _get_duckdb_connection()
            conn.register(table_name, df)
            logger.info("Registered DuckDB table '%s' (%d rows)", table_name, len(df))
        except Exception:
            logger.warning(
                "Failed to register table '%s' in DuckDB", table_name, exc_info=True
            )

        description = match.group("description").strip()
        if description:
            return f"{table_html}\n<blockquote><p>{description}</p></blockquote>"
        return table_html


class DuckDBQueryExtra(ExtraFeature):
    """
    Extra feature for executing inline DuckDB SQL expressions.

    Matches [query: <SQL>] anywhere in the document, executes the SQL against
    the shared DuckDB connection, and replaces the match with the result.
    Scalar results are injected inline; table-like results become HTML tables.
    """

    pattern = r"\[query:\s*(?P<expression>.+?)\]"

    @staticmethod
    def replace(match, html_content):
        """
        Execute the matched SQL expression and return the result.

        Args:
            match (re.Match): The regex match containing the SQL expression.
            html_content (str): The full HTML content.

        Returns:
            str: The query result as text or an HTML table.
        """
        expression = html.unescape(match.group("expression"))
        try:
            conn = _get_duckdb_connection()
            result = conn.execute(expression)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()

            if len(rows) == 1 and len(columns) == 1:
                return str(rows[0][0])

            return _render_html_table(columns, rows)
        except Exception:
            logger.warning(
                "Failed to execute DuckDB query: %s", expression, exc_info=True
            )
            return match.group(0)


def _get_duckdb_connection():
    """
    Lazily initialize and return a sandboxed in-memory DuckDB connection.

    The connection is stored in ExtraFeature.memory and reused across all
    extras during a single document conversion.
    """
    if "duckdb" not in ExtraFeature.memory:
        conn = duckdb.connect(":memory:")
        conn.execute("SET enable_external_access = false")
        ExtraFeature.memory["duckdb"] = conn
    return ExtraFeature.memory["duckdb"]


def _render_html_table(columns, rows):
    """
    Render a list of column names and row tuples into an HTML table string.

    Args:
        columns (list[str]): Column header names.
        rows (list[tuple]): Row data as tuples of values.

    Returns:
        str: An HTML <table> string.
    """
    header_cells = "".join(f"<th>{col}</th>" for col in columns)
    body_rows = "".join(
        "<tr>" + "".join(f"<td>{val}</td>" for val in row) + "</tr>" for row in rows
    )
    return (
        f"<table><thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{body_rows}</tbody></table>"
    )


def apply_extras(extras: set[ExtraFeature], html_content, before_stash=False):
    """
    Applies extra features to an html string.

    Args:
        extras: set[ExtraFeature] Extra features to apply.
        html_content: Complete html text, used by some extras like TOC.
        before_stash: Whether to run extras marked for pre-stash processing.

    Returns:
        str: The updated html.
    """
    for extra in extras:
        if extra.run_before_stash != before_stash:
            continue

        new_html = html_content
        while re.search(extra.pattern, html_content, flags=re.DOTALL):
            try:
                new_html = re.sub(
                    extra.pattern,
                    lambda match, ext=extra: ext.replace(
                        match, html_content=html_content
                    ),
                    html_content,
                    flags=re.DOTALL,
                )
            except Exception:
                logger.warning(
                    "An exception occurred while applying an extra", exc_info=True
                )

            if new_html == html_content:
                break
            html_content = new_html

    return html_content
