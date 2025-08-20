"""
Module to convert a markdown file to a pdf file.
Author: @julynx
"""

import os
import sys
import time
import warnings
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from io import StringIO
from pathlib import Path

import markdown2
import weasyprint

from .resources import get_css_path, get_code_css_path, get_output_path
from .utils import drop_duplicates
from .constants import MD_EXTENSIONS


def _suppress_warnings():
    """
    Suppress all warnings in production while preserving critical error handling.
    Only errors and exceptions will be shown.
    """
    # Suppress all warnings but keep errors
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    warnings.filterwarnings('ignore', category=PendingDeprecationWarning)
    warnings.filterwarnings('ignore', category=ImportWarning)
    warnings.filterwarnings('ignore', category=ResourceWarning)


def _silent_pdf_generation(func, *args, **kwargs):
    """
    Execute PDF generation function while suppressing all non-critical output.
    Preserves exceptions and critical errors.
    """
    _suppress_warnings()
    
    # Capture stdout and stderr to filter out warnings
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            result = func(*args, **kwargs)
        
        # Check if there were any critical errors in stderr
        stderr_content = stderr_capture.getvalue()
        if stderr_content and any(keyword in stderr_content.lower()
                                for keyword in ['error', 'exception', 'traceback', 'failed']):
            # Print only critical errors, not warnings
            print(stderr_content, file=sys.stderr)
        
        return result
        
    except Exception as exc:
        # Always re-raise actual exceptions
        raise exc


def convert(md_path, css_path=None, output_path=None,
            *, extend_default_css=True):
    """
    Convert a markdown file to a pdf file.

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

    if extend_default_css:
        css_sources = [get_code_css_path(), get_css_path(), css_path]
    else:
        css_sources = [get_code_css_path(), css_path]

    css_sources = drop_duplicates(css_sources)

    try:
        html = markdown2.markdown_path(md_path,
                                       extras=MD_EXTENSIONS)

        # Use silent PDF generation to suppress warnings
        _silent_pdf_generation(
            lambda: weasyprint
            .HTML(string=html, base_url='.')
            .write_pdf(target=output_path,
                      stylesheets=list(css_sources))
        )

    except Exception as exc:
        raise RuntimeError(exc) from exc


def live_convert(md_path, css_path=None, output_path=None,
                 *, extend_default_css=True):
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

    live_converter = LiveConverter(md_path, css_path, output_path,
                                   extend_default_css=extend_default_css,
                                   loud=True)
    live_converter.observe()


def convert_text(md_text, css_text=None,
                 *, extend_default_css=True):
    """
    Convert markdown text to a pdf file.

    Args:
        md_text (str): Markdown text.
        css_text (str=None): CSS text.
        extend_default_css (bool=True): Extend the default CSS file.

    Returns:
        PDF file as bytes.
    """
    default_css = Path(get_css_path()).read_text(encoding='utf-8')
    code_css = Path(get_code_css_path()).read_text(encoding='utf-8')

    if css_text is None:
        css_text = default_css

    if extend_default_css:
        css_sources = [code_css, default_css, css_text]
    else:
        css_sources = [code_css, css_text]

    css_sources = [weasyprint.CSS(string=css)
                   for css in drop_duplicates(css_sources)]

    try:
        html = markdown2.markdown(md_text,
                                  extras=MD_EXTENSIONS)

        # Use silent PDF generation to suppress warnings
        return _silent_pdf_generation(
            lambda: weasyprint
            .HTML(string=html, base_url='.')
            .write_pdf(stylesheets=css_sources)
        )

    except Exception as exc:
        raise RuntimeError(exc) from exc


class LiveConverter():
    """
    Class to convert a markdown file to a pdf file and watch for changes.
    """

    def __init__(self, md_path, css_path, output_path,
                 *, extend_default_css=True,
                 loud=False):
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
        convert(self.md_path, self.css_path, self.output_path,
                extend_default_css=self.extend_default_css)
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

                if md_modified != self.md_last_modified or \
                        css_modified != self.css_last_modified:

                    self.write_pdf()

                    self.md_last_modified = md_modified
                    self.css_last_modified = css_modified

                time.sleep(poll_interval)

        except KeyboardInterrupt:
            if self.loud:
                print("\nInterrupted by user.\n", flush=True)
            return
