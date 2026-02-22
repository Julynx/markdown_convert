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
import latex2mathml.converter as mathml
import pandas as pd
import vl_convert
from bs4 import BeautifulSoup, Tag
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from ruamel.yaml import YAML
from yaml_to_schemdraw import from_yaml_string

logger = logging.getLogger(__name__)


class ExtraFeature:
    """
    Base class for extra features that can be applied to HTML.

    Attributes:
        pattern (str): Regex pattern to match the extra feature in the HTML.
        execution_phase (int): Determines the order of execution.
                               Lower values run first.
            0-49: Runs before code blocks are protected
                  (e.g., anything that interacts with code blocks, like diagrams).
            50-99: Runs after protection, but before query execution
                  (e.g., table extraction).
            100+: Runs after protection and table extraction
                  (e.g., inline queries, highlighters).
        bypass_stashing_class (str): If the code contains this class, it will not be
                                     stashed during the protection phase.
        memory (dict): Shared ephemeral state across all extras during a single
                       document conversion. Managed by render_extra_features in
                       transform.py.
    """

    pattern = r""
    execution_phase = 100
    bypass_stashing_class = None

    @staticmethod
    def replace(match, html_content, memory=None):
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


class HighlightExtra(ExtraFeature):
    """Extra feature for rendering highlighted text."""

    pattern = r"==(?P<content>.*?)=="

    @staticmethod
    def replace(match, html_content, memory=None):
        """
        Render a tag for a highlight.

        Args:
            match: Element identified as a highlight.
        Returns:
            str: Tag representing the highlight.
        """
        content = match.group("content")
        return f'<span class="highlight">{content}</span>'


class SyntaxHighlightExtra(ExtraFeature):
    """Extra feature for rendering syntax highlighted code blocks."""

    pattern = (
        r"<pre[^>]*>\s*"
        r"<code[^>]*class=[\"'](?![^>]*highlighted)[^\"]*language-"
        r"(?P<lang>[a-zA-Z0-9_-]+)[^\"]*[\"'][^>]*>"
        r"(?P<code>.*?)"
        r"</code>\s*"
        r"</pre>"
    )
    execution_phase = 0

    @staticmethod
    def replace(match, html_content, memory=None):
        lang = match.group("lang")
        code = match.group("code")

        try:
            highlighted = highlight(
                code,
                get_lexer_by_name(lang),
                HtmlFormatter(nowrap=True, classprefix="pygments-"),
            )
        except ClassNotFound:
            highlighted = code

        return (
            f'<pre><code class="language-{lang} highlighted">{highlighted}</code></pre>'
        )


class CustomSpanExtra(ExtraFeature):
    """Extra feature for rendering custom spans with specific classes."""

    pattern = r"(?P<cls>[a-zA-Z0-9_-]+)\{\{\s*(?P<content>.*?)\s*\}\}"

    @staticmethod
    def replace(match, html_content, memory=None):
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


class InlineMathExtra(ExtraFeature):
    """Extra feature for rendering LaTeX math expressions."""

    # <eq> ... </eq> Inline equations
    pattern = r"<eq>(?P<content>.*?)</eq>"

    @staticmethod
    def replace(match, html_content, memory=None):
        """
        Render a tag for a LaTeX math expression.

        Args:
            match: Element identified as a LaTeX math expression.
        Returns:
            str: Tag representing the LaTeX math expression.
        """
        content = match.group("content")
        converted = mathml.convert(content)
        return converted


class BlockMathExtra(ExtraFeature):
    """Extra feature for rendering LaTeX math expressions."""

    # <eqn> ... </eqn> Block equations
    pattern = r"<eqn>(?P<content>.*?)</eqn>"

    @staticmethod
    def replace(match, html_content, memory=None):
        """
        Render a tag for a LaTeX math expression.

        Args:
            match: Element identified as a LaTeX math expression.
        Returns:
            str: Tag representing the LaTeX math expression.
        """
        content = match.group("content")
        converted = mathml.convert(content, display="block")
        return converted


class TocExtra(ExtraFeature):
    """Extra feature for rendering a Table of Contents."""

    pattern = r"\[TOC(?:\s+depth=(?P<depth>\d+))?\]"

    @staticmethod
    def replace(match, html_content, memory=None):
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


class MermaidExtra(ExtraFeature):
    """Extra feature for rendering mermaid diagrams."""

    pattern = (
        r"<pre[^>]*>"
        r"<code[^>]*class=[\"'][^\"]*language-mermaid[^\"]*[\"'][^>]*>"
        r"(?P<content>.*?)"
        r"</code>"
        r"</pre>"
    )
    execution_phase = 60
    bypass_stashing_class = "language-mermaid"

    @staticmethod
    def replace(match, html_content, memory=None):
        """
        Render a tag for a mermaid diagram.

        Args:
            match (re.Match): Element identified as a mermaid diagram.
            html_content (str): The full HTML content.

        Returns:
            str: SVG tag representing the mermaid diagram.
        """
        content = match.group("content")
        return f'<div class="mermaid">{content}</div>'


class VegaExtra(ExtraFeature):
    """Extra feature for rendering Vega-Lite diagrams from JSON or YAML."""

    pattern = (
        r"<pre[^>]*>"
        r"<code[^>]*class=[\"'][^\"]*language-vega[^\"]*[\"'][^>]*>"
        r"(?P<content>.*?)"
        r"</code>"
        r"</pre>"
    )
    execution_phase = 60
    bypass_stashing_class = "language-vega"

    @staticmethod
    def replace(match, html_content, memory=None):
        """
        Render a tag for a vega-lite diagram from JSON or YAML.

        Args:
            match (re.Match): Element identified as a vega-lite diagram.
            html_content (str): The full HTML content.

        Returns:
            str: SVG tag representing the vega-lite diagram.
        """

        def _replace_duckdb_query(spec):
            data_spec = spec.get("data", {})
            if isinstance(data_spec, dict) and "query" in data_spec:
                query = data_spec.pop("query")
                conn = _get_duckdb_connection(memory)
                table = conn.execute(query).df()

                # Handle dates for JSON serialization
                for col in table.select_dtypes(
                    include=["datetime", "datetimetz"]
                ).columns:
                    table[col] = table[col].astype(str)

                data_spec["values"] = table.to_dict(orient="records")

        content = match.group("content")
        spec = None

        # Parse JSON or YAML
        try:
            spec = json.loads(content)
        except (json.JSONDecodeError, TypeError):
            try:
                yaml = YAML(typ="safe")
                spec = yaml.load(content)
            except Exception as exc:
                logger.warning("Failed to parse Vega-Lite spec: %s", exc)
                return match.group(0)

        if spec is None:
            return match.group(0)

        # Dynamic query support
        try:
            _replace_duckdb_query(spec)
        except Exception as exc:
            logger.warning("Failed to execute query in Vega-Lite spec: %s", exc)
            return match.group(0)

        # Convert to SVG
        try:
            tag = vl_convert.vegalite_to_svg(spec)
            return f"<div class='vega-lite'>{tag}</div>"
        except Exception as exc:
            logger.warning("Failed to convert Vega-Lite spec to SVG: %s", exc)
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
    execution_phase = 0

    @staticmethod
    def replace(match, html_content, memory=None):
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
            svg_string = diagram.get_imagedata("svg").decode("utf-8")
            return f"<div class='schemdraw'>{svg_string}</div>"
        except Exception as exc:
            logger.warning("Failed to convert schemdraw diagram: %s", exc)
            return match.group(0)


class DynamicTableExtra(ExtraFeature):
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
    execution_phase = 50

    @staticmethod
    def replace(match, html_content, memory=None):
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
            tables = pd.read_html(StringIO(table_html))
            if not tables:
                raise ValueError("No tables found in HTML")

            table = tables[-1]
            conn = _get_duckdb_connection(memory)
            conn.register(table_name, table)
        except Exception as exc:
            logger.warning(
                "Failed to register table '%s' in DuckDB: %s", table_name, exc
            )

        description = match.group("description").strip()
        if description:
            return f"{table_html}\n<blockquote><p>{description}</p></blockquote>"
        return table_html


class DynamicQueryExtra(ExtraFeature):
    """
    Extra feature for executing inline DuckDB SQL expressions.

    Matches [query: <SQL>] anywhere in the document, executes the SQL against
    the shared DuckDB connection, and replaces the match with the result.
    Scalar results are injected inline; table-like results become HTML tables.
    """

    pattern = r"\[query:\s*(?P<expression>.+?)\]"
    execution_phase = 60

    @staticmethod
    def replace(match, html_content, memory=None):
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
            conn = _get_duckdb_connection(memory)
            result = conn.execute(expression)
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()

            if len(rows) == 1 and len(columns) == 1:
                return str(rows[0][0])

            return _render_html_table(columns, rows)
        except Exception as exc:
            logger.warning("Failed to execute DuckDB query: %s", exc)
            return match.group(0)


def _get_duckdb_connection(memory):
    """
    Lazily initialize and return a sandboxed in-memory DuckDB connection.

    The connection is stored in memory and reused across all
    extras during a single document conversion.

    Args:
        memory (dict): Shared ephemeral state across all extras during a single
                       document conversion.

    Returns:
        duckdb.DuckDB: The DuckDB connection.
    """
    if "duckdb" not in memory:
        conn = duckdb.connect(":memory:")
        conn.execute("SET enable_external_access = false")
        memory["duckdb"] = conn
    return memory["duckdb"]


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


def apply_extras(extras: list[ExtraFeature], html_content, memory=None):
    """
    Applies extra features to an html string in the order they are provided.

    Args:
        extras: list[ExtraFeature] Extra features to apply.
        html_content: Complete html text, used by some extras like TOC.

    Returns:
        str: The updated html.
    """
    for extra in extras:
        new_html = html_content
        while re.search(extra.pattern, html_content, flags=re.DOTALL):
            try:
                new_html = re.sub(
                    extra.pattern,
                    lambda match, html_content=html_content, ext=extra, memory=memory: (
                        ext.replace(
                            match,
                            html_content=html_content,
                            memory=memory,
                        )
                    ),
                    html_content,
                    flags=re.DOTALL,
                )
            except Exception as exc:
                logger.warning("An exception occurred while applying an extra: %s", exc)

            if new_html == html_content:
                break
            html_content = new_html

    return html_content
