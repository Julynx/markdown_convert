"""
Module to convert a markdown file to a pdf file.
Author: @julynx
"""

import os
import re
import time
from datetime import datetime
from pathlib import Path

import markdown2
from playwright.sync_api import sync_playwright

from .constants import MD_EXTENSIONS
from .resources import get_code_css_path, get_css_path, get_output_path
from .utils import drop_duplicates


def _generate_pdf_with_playwright(
    html_content,
    output_path,
    *,
    css_content=None,
    base_dir=None,
    dump_html=False,
):
    """
    Generate a PDF from HTML content using Playwright.

    Args:
        html_content (str): HTML content to convert.
        output_path (str): Path to save the PDF file.
        css_content (str, optional): CSS content to inject.
        base_dir (Path, optional): Base directory for resolving relative paths in HTML.
        dump_html (bool, optional): Whether to dump the HTML content to a file.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Handle loading based on presence of base_dir
        temp_html = None
        try:
            if base_dir:
                temp_html = base_dir / f".temp_{os.getpid()}.html"
                temp_html.write_text(html_content, encoding="utf-8")
                page.goto(temp_html.as_uri(), wait_until="networkidle")
            else:
                page.set_content(html_content, wait_until="networkidle")

            if css_content:
                page.add_style_tag(content=css_content)

            pdf_params = {
                "format": "A4",
                "print_background": True,
                "margin": {"top": "20mm", "bottom": "20mm", "left": "20mm", "right": "20mm"},
                "path": output_path,
            }  # Playwright ignores None paths

            pdf_bytes = page.pdf(**pdf_params)
            return None if output_path else pdf_bytes

        finally:
            browser.close()
            if temp_html and temp_html.exists() and not dump_html:
                temp_html.unlink()


def _get_css_content(css_sources):
    """
    Get the CSS content from a list of CSS file paths.

    Args:
        css_sources (list): List of CSS file paths.
    Returns:
        str: Combined CSS content.
    """
    css_buffer = ""
    for css_file in css_sources:
        css_buffer += Path(css_file).read_text(encoding="utf-8") + "\n"
    return css_buffer


def _create_sections(html):
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


def convert(
    md_path,
    css_path=None,
    output_path=None,
    *,
    extend_default_css=True,
    dump_html=False,
):
    """
    Convert a markdown file to a pdf file.

    Args:
        md_path (str): Path to the markdown file.
        css_path (str=None): Path to the CSS file.
        output_path (str=None): Path to the output file.
        extend_default_css (bool=True): Extend the default CSS file.
        dump_html (bool=False): Dump the intermediate HTML to a file.
    """
    if css_path is None:
        css_path = get_css_path()

    if output_path is None:
        output_path = get_output_path(md_path, None)

    if extend_default_css:
        css_sources = [get_code_css_path(), get_css_path(), css_path]
    else:
        css_sources = [get_code_css_path(), css_path]

    css_sources = drop_duplicates(css_sources)

    try:
        html = markdown2.markdown_path(md_path, extras=MD_EXTENSIONS)
        html = _create_sections(html)

        _generate_pdf_with_playwright(
            html,
            output_path,
            css_content=_get_css_content(css_sources),
            base_dir=Path(md_path).resolve().parent,
            dump_html=dump_html,
        )

    except Exception as exc:
        raise RuntimeError(exc) from exc


def live_convert(md_path, css_path=None, output_path=None, *, extend_default_css=True):
    """
    Convert a markdown file to a pdf file and watch for changes.

    Args:
        md_path (str): Path to the markdown file.
        css_path (str=None): Path to the CSS file.
        output_path (str=None): Path to the output file.
        extend_default_css (bool=True): Extend the default CSS file.
    """
    if css_path is None:
        css_path = get_css_path()

    if output_path is None:
        output_path = get_output_path(md_path, None)

    live_converter = LiveConverter(
        md_path,
        css_path,
        output_path,
        extend_default_css=extend_default_css,
        loud=True,
    )
    live_converter.observe()


def convert_text(md_text, css_text=None, *, extend_default_css=True):
    """
    Convert markdown text to a pdf file.

    Args:
        md_text (str): Markdown text.
        css_text (str=None): CSS text.
        extend_default_css (bool=True): Extend the default CSS file.

    Returns:
        PDF file as bytes.
    """
    default_css = Path(get_css_path()).read_text(encoding="utf-8")
    code_css = Path(get_code_css_path()).read_text(encoding="utf-8")

    if css_text is None:
        css_text = default_css

    if extend_default_css:
        css_sources = [code_css, default_css, css_text]
    else:
        css_sources = [code_css, css_text]

    try:
        html = markdown2.markdown(md_text, extras=MD_EXTENSIONS)
        html = _create_sections(html)

        return _generate_pdf_with_playwright(
            html,
            None,
            css_content=_get_css_content(css_sources),
        )

    except Exception as exc:
        raise RuntimeError(exc) from exc


class LiveConverter:
    """
    Class to convert a markdown file to a pdf file and watch for changes.
    """

    def __init__(self, md_path, css_path, output_path, *, extend_default_css=True, loud=False):
        """
        Initialize the LiveConverter class.

        Args:
            md_path (str): Path to the markdown file.
            css_path (str): Path to the CSS file.
            output_path (str): Path to the output file.
            extend_default_css (bool): Extend the default CSS file.
        """
        self.md_path = Path(md_path).absolute()
        self.css_path = Path(css_path).absolute()
        self.output_path = output_path
        self.extend_default_css = extend_default_css
        self.loud = loud

        self.md_last_modified = None
        self.css_last_modified = None

    def get_last_modified_date(self, file_path):
        """
        Get the last modified date of a file.

        Args:
            file_path (str): Path to the file.

        Returns:
            Last modified date of the file.
        """
        return os.path.getmtime(file_path)

    def write_pdf(self):
        """
        Write the pdf file.
        """
        convert(
            self.md_path,
            self.css_path,
            self.output_path,
            extend_default_css=self.extend_default_css,
        )
        if self.loud:
            print(f"- PDF file updated: {datetime.now()}", flush=True)

    def observe(self, poll_interval=1):
        """
        Observe the markdown and CSS files. Calls write_pdf() when a file is
        modified.
        """
        self.write_pdf()

        self.md_last_modified = self.get_last_modified_date(self.md_path)
        self.css_last_modified = self.get_last_modified_date(self.css_path)

        try:
            while True:

                md_modified = self.get_last_modified_date(self.md_path)
                css_modified = self.get_last_modified_date(self.css_path)

                if md_modified != self.md_last_modified or css_modified != self.css_last_modified:

                    self.write_pdf()

                    self.md_last_modified = md_modified
                    self.css_last_modified = css_modified

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            if self.loud:
                print("\nInterrupted by user.\n", flush=True)
