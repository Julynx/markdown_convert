"""
Module to convert a markdown file to a pdf file.
Author: @julynx
"""

import os
import secrets
import time
from datetime import datetime
from pathlib import Path

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright

from .autoinstall import ensure_chromium
from .constants import (
    BROWSER_ARGS,
    CSP_TEMPLATE,
    PDF_PARAMS,
    resolve_extras,
)
from .extras import MermaidExtra
from .resources import get_code_css_path, get_css_path, get_output_path
from .transform import (
    create_html_document,
    create_sections,
    render_extra_features,
    render_mermaid_diagrams,
)


def convert(
    markdown_path: Path,
    css_path: Path = None,
    output_path=None,
    *,
    extend_default_css=True,
    dump_html=False,
    extras=None,
    security_level="default",
):
    """
    Convert a markdown file to a pdf file.

    Args:
        markdown_path (str): Path to the markdown file.
        css_path (str=None): Path to the CSS file.
        output_path (str=None): Path to the output file.
        extend_default_css (bool=True): Extend the default CSS file.
        dump_html (bool=False): Dump the intermediate HTML to a file.
        extras (list=None): List of extras to use.
        security_level (str=None): Security level to use.
          "strict" disables JS, inline HTML and internet access.
    """
    markdown_text = (
        Path(markdown_path).read_text(encoding="utf-8")
        if markdown_path and Path(markdown_path).exists()
        else None
    )
    css_text = (
        Path(css_path).read_text(encoding="utf-8")
        if css_path and Path(css_path).exists()
        else None
    )

    if output_path is None:
        output_path = get_output_path(markdown_path, None)

    convert_text(
        markdown_text,
        css_text=css_text,
        output_path=output_path,
        base_dir=Path(markdown_path).resolve().parent,
        extend_default_css=extend_default_css,
        dump_html=dump_html,
        extras=extras,
        security_level=security_level,
    )


def live_convert(
    markdown_path,
    css_path=None,
    output_path=None,
    *,
    extend_default_css=True,
    extras=None,
    security_level="default",
):
    """
    Convert a markdown file to a pdf file and watch for changes.

    Args:
        markdown_path (str): Path to the markdown file.
        css_path (str=None): Path to the CSS file.
        output_path (str=None): Path to the output file.
        extend_default_css (bool=True): Extend the default CSS file.
        extras (list=None): List of extras to use.
        security_level (str=None): Security level to use.
          "strict" disables JS, inline HTML and internet access.
    """
    if css_path is None:
        css_path = get_css_path()

    if output_path is None:
        output_path = get_output_path(markdown_path, None)

    live_converter = LiveConverter(
        markdown_path,
        css_path,
        output_path,
        extend_default_css=extend_default_css,
        loud=True,
        extras=extras,
        security_level=security_level,
    )
    live_converter.observe()


def convert_text(
    markdown_text,
    css_text=None,
    output_path=None,
    *,
    base_dir=None,
    extend_default_css=True,
    dump_html=False,
    extras=None,
    security_level="default",
):
    """
    Convert markdown text to a pdf file.

    Args:
        markdown_text (str): Markdown text.
        css_text (str=None): CSS text.
        output_path (str=None): Path to the output file.
        base_dir (Path=None): Base directory for resolving relative paths.
        extend_default_css (bool=True): Extend the default CSS file.
        dump_html (bool=False): Dump the intermediate HTML to a file.
        extras (list=None): List of extras to use.
        security_level (str=None): Security level to use.
          "strict" disables JS, inline HTML and internet access.

    Returns:
        PDF file as bytes if output_path is None, else None.
    """
    default_css = Path(get_css_path()).read_text(encoding="utf-8")
    code_css = Path(get_code_css_path()).read_text(encoding="utf-8")

    if css_text is None:
        css_text = ""

    if extend_default_css:
        css_sources = [code_css, default_css, css_text]
    else:
        css_sources = [code_css, css_text]

    try:
        nonce = secrets.token_urlsafe(16)
        extras = resolve_extras(extras)

        markdown = MarkdownIt("js-default", {"breaks": True, "html": True})
        for extra in extras["markdown_it_extras"]:
            markdown.use(extra)

        html = markdown.render(markdown_text)

        html = create_sections(html)

        if MermaidExtra in extras["markdown_convert_extras"]:
            html = render_mermaid_diagrams(html, nonce=nonce)
        html = render_extra_features(html, extras=extras["markdown_convert_extras"])

        return _generate_pdf_with_playwright(
            html,
            output_path,
            css_content="\n".join(css_sources),
            base_dir=base_dir,
            dump_html=dump_html,
            nonce=nonce,
            security_level=security_level,
        )

    except Exception as exc:
        raise RuntimeError(exc) from exc


class LiveConverter:
    """
    Class to convert a markdown file to a pdf file and watch for changes.
    """

    def __init__(
        self,
        markdown_path,
        css_path,
        output_path,
        *,
        extend_default_css=True,
        loud=False,
        extras=None,
        security_level="default",
    ):
        """
        Initialize the LiveConverter class.

        Args:
            markdown_path (str): Path to the markdown file.
            css_path (str): Path to the CSS file.
            output_path (str): Path to the output file.
            extend_default_css (bool): Extend the default CSS file.
            extras (list=None): List of extras to use.
            security_level (str=None): Security level to use.
              "strict" disables JS, inline HTML and internet access.
        """
        self.md_path = Path(markdown_path).absolute()
        self.css_path = Path(css_path).absolute()
        self.output_path = output_path
        self.extend_default_css = extend_default_css
        self.loud = loud
        self.extras = extras
        self.security_level = security_level

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
            extras=self.extras,
            security_level=self.security_level,
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
                markdown_modified = self.get_last_modified_date(self.md_path)
                css_modified = self.get_last_modified_date(self.css_path)

                if (
                    markdown_modified != self.md_last_modified
                    or css_modified != self.css_last_modified
                ):
                    self.write_pdf()

                    self.md_last_modified = markdown_modified
                    self.css_last_modified = css_modified

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            if self.loud:
                print("\nInterrupted by user.\n", flush=True)


def _generate_pdf_with_playwright(
    html_content,
    output_path,
    *,
    css_content=None,
    base_dir=None,
    dump_html=False,
    nonce=None,
    security_level="default",
):
    """
    Generate a PDF from HTML content using Playwright.

    Args:
        html_content (str): HTML content to convert.
        output_path (str): Path to save the PDF file.
        css_content (str, optional): CSS content to inject.
        base_dir (Path, optional): Base directory for resolving relative paths in HTML.
        dump_html (bool, optional): Whether to dump the HTML content to a file.
        nonce (str, optional): Nonce for Content Security Policy.
        security_level (str=None): Security level to use.
          "strict" disables JS, inline HTML and internet access.
    """
    if nonce is None:
        raise ValueError("A nonce must be provided for CSP generation.")

    # This prevents arbitrary JavaScript injection while allowing Mermaid to work
    csp = CSP_TEMPLATE.format(nonce=nonce)
    full_html = create_html_document(html_content, css_content, csp)

    ensure_chromium()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, args=BROWSER_ARGS)
        context = browser.new_context(
            java_script_enabled=security_level != "strict",
            permissions=[],
            geolocation=None,
            accept_downloads=False,
            offline=security_level == "strict",
        )
        page = context.new_page()

        temp_html = None
        try:
            if base_dir:
                temp_file = (
                    f"{Path(output_path).stem}.html"
                    if output_path
                    else f".temp_{os.getpid()}.html"
                )
                temp_html = base_dir / temp_file
                temp_html.write_text(full_html, encoding="utf-8")
                page.goto(temp_html.as_uri(), wait_until="networkidle", timeout=30000)
            else:
                page.set_content(full_html, wait_until="networkidle", timeout=30000)

            pdf_params = {
                **PDF_PARAMS,
                "path": output_path,
            }

            pdf_bytes = page.pdf(**pdf_params)
            return None if output_path else pdf_bytes

        finally:
            browser.close()
            if temp_html and temp_html.exists() and not dump_html:
                temp_html.unlink()
