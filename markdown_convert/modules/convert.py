"""
Module to convert a markdown file to a pdf file.
Author: @julynx
"""

import os
import time
from datetime import datetime
from pathlib import Path

import markdown2
from playwright.sync_api import sync_playwright

from .resources import get_css_path, get_code_css_path, get_output_path
from .utils import drop_duplicates
from .constants import MD_EXTENSIONS


def _generate_pdf_with_playwright(html_content, output_path):
    """
    Generate a PDF from HTML content using Playwright.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        # Wait for any potential resources to load
        page.wait_for_load_state("networkidle")

        pdf_params = {
            "format": "A4",
            "print_background": True,
            "margin": {
                "top": "20mm",
                "bottom": "20mm",
                "left": "20mm",
                "right": "20mm",
            },
        }

        if output_path:
            page.pdf(path=output_path, **pdf_params)
            browser.close()
            return None

        pdf_bytes = page.pdf(**pdf_params)
        browser.close()
        return pdf_bytes


def _embed_css_in_html(html, css_sources):
    """
    Embed CSS styles into HTML content.

    Args:
        html (str): HTML content.
        css_sources (list): List of CSS file paths.

    Returns:
        HTML content with embedded CSS styles.
    """
    css_buffer = ""
    for css_file in css_sources:
        css_buffer += Path(css_file).read_text(encoding="utf-8") + "\n"

    style_tag = f"<style>\n{css_buffer}\n</style>\n"
    return f"<!DOCTYPE html>\n<html>\n<head>\n{style_tag}</head>\n<body>\n{html}\n</body>\n</html>"


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
        html = _embed_css_in_html(html, css_sources)

        if dump_html:
            html_dump_path = Path(output_path).with_suffix(".html")
            html_dump_path.write_text(html, encoding="utf-8")

        _generate_pdf_with_playwright(html, output_path)

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
        md_path, css_path, output_path, extend_default_css=extend_default_css, loud=True
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
        html = _embed_css_in_html(html, css_sources)

        return _generate_pdf_with_playwright(html, None)

    except Exception as exc:
        raise RuntimeError(exc) from exc


class LiveConverter:
    """
    Class to convert a markdown file to a pdf file and watch for changes.
    """

    def __init__(
        self, md_path, css_path, output_path, *, extend_default_css=True, loud=False
    ):
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

                if (
                    md_modified != self.md_last_modified
                    or css_modified != self.css_last_modified
                ):

                    self.write_pdf()

                    self.md_last_modified = md_modified
                    self.css_last_modified = css_modified

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            if self.loud:
                print("\nInterrupted by user.\n", flush=True)
