"""
Module to convert a markdown file to a pdf file.
Author: @julynx
"""

import os
import platform
import time
from datetime import datetime
from pathlib import Path

import markdown2
import weasyprint


from .resources import get_css_path, get_code_css_path, get_output_path


def convert(md_path, css_path=None, output_path=None):
    """
    Convert a markdown file to a pdf file.

    Args:
        md_path (str): Path to the markdown file.
        css_path (str=None): Path to the CSS file.
        output_path (str=None): Path to the output file.
    """
    if css_path is None:
        css_path = get_css_path()

    if output_path is None:
        output_path = get_output_path(md_path, None)

    try:
        html = markdown2.markdown_path(md_path,
                                       extras=["fenced-code-blocks",
                                               "toc",
                                               "tables"])

        (weasyprint
         .HTML(string=html)
         .write_pdf(target=output_path,
                    stylesheets=[css_path,
                                 get_code_css_path()]))

    except Exception as exc:
        raise RuntimeError(exc) from exc


class LiveConverter():
    """
    Class to convert a markdown file to a pdf file and watch for changes.
    """

    def __init__(self, md_path, css_path, output_path, *, loud=False):
        """
        Initialize the LiveConverter class.

        Args:
            md_path (str): Path to the markdown file.
            css_path (str): Path to the CSS file.
            output_path (str): Path to the output file.
        """
        self.md_path = Path(md_path).absolute()
        self.css_path = Path(css_path).absolute()
        self.output_path = output_path
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
        if platform.system() == 'Windows':
            return os.path.getmtime(file_path)

        return os.path.getmtime(file_path)

    def write_pdf(self):
        """
        Write the pdf file.
        """
        convert(self.md_path, self.css_path, self.output_path)
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


def live_convert(md_path, css_path, output_path):
    """
    Convert a markdown file to a pdf file and watch for changes.

    Args:
        md_path (str): Path to the markdown file.
        css_path (str): Path to the CSS file.
        output_path (str): Path to the output file.
    """
    live_converter = LiveConverter(md_path, css_path, output_path,
                                   loud=True)
    live_converter.observe()
