"""
Markdown convert module.

Overview:
    This module provides a class for converting Markdown files to PDF files,
    and updating the PDF file whenever the Markdown file is modified.
    Supports the <pagebreak> tag to insert page breaks in the PDF file.
"""

import io
from time import sleep
from pathlib import Path
import pkg_resources
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import markdown
import fitz


class MarkdownFile(FileSystemEventHandler):
    """
    MarkdownFile class, representing a file in Markdown format.
    """

    def __init__(self, md_path, *,
                 css_path=pkg_resources.resource_filename('markdown_convert',
                                                          'css/default.css'),
                 margin_h=62,
                 margin_v=60):
        """
        Constructor for the MarkdownFile class.

        Args:
            md_path (Path|str): Path to the Markdown file.
            css_path (Path|str='css/default.css'): Path to the CSS file.
            margin_h (int=62): Horizontal margin of the PDF file.
            margin_v (int=60): Vertical margin of the PDF file.
        """
        self.plugins = {'extra', 'sane_lists'}
        self.margin_h = margin_h
        self.margin_v = margin_v

        try:  # Raise an error if the Markdown file is invalid.
            md_path = Path(md_path).resolve()
            if md_path.suffix != '.md':
                raise ValueError("The path must be a Markdown file.")
            self.path_no_ext = md_path.with_suffix('')
            self.content = md_path.read_text(encoding='utf-8')
        except (ValueError, TypeError, OSError) as error:
            raise ValueError(f'\n\nInvalid Markdown file \'{md_path}\'.\n') \
                from error

        try:  # Warn if the CSS file is invalid, and disable custom CSS.
            css_path = Path(css_path).resolve()
            self.custom_css = css_path.read_text(encoding='utf-8')
        except (ValueError, TypeError, OSError):
            print(f'\nCould not read the CSS file \'{css_path}\'.\n'
                  'Proceeding without custom CSS...')
            self.custom_css = None

    def _add_page(self, page, *,
                  markdown_parser,
                  output_writer,
                  last_page=False):
        """
        Parses a Markdown page with the provided Markdown parser, and adds it
        to the output writer.

        Args:
            page (str): The Markdown page to parse.
            markdown_parser (function): The Markdown parser to use.
            output_writer (DocumentWriter): The output writer to use.
            last_page (bool=False): Whether this is the last page.
                                    Will insert page breaks if False.
        """
        page_break_str = '\n\n<div style="page-break-after: always;"></div>'
        if last_page:
            page_break_str = ''

        page = f'{page}{page_break_str}'
        rectangle = fitz.paper_rect('A4')
        html_content = markdown_parser(page,
                                       extensions=list(self.plugins))
        story = fitz.Story(html=html_content,
                           user_css=self.custom_css,
                           archive=str(self.path_no_ext.parent))

        pages_left = 1
        while pages_left > 0:
            device = output_writer.begin_page(rectangle)
            pages_left, _ = story.place(rectangle + (self.margin_h,
                                                     self.margin_v,
                                                     -self.margin_h,
                                                     -self.margin_v))
            story.draw(device)
            output_writer.end_page()

    def use(self, plugin):
        """
        Adds a plugin to the list of plugins to use.
        'extra' and 'sane_lists' are already included by default.

        Args:
            plugin (str): The name of the plugin to use.
        """
        self.plugins.add(plugin)
        return self

    def to_pdf(self, output_path=None):
        """
        Converts the Markdown file to a PDF file.

        Args:
            output_path (str=None): The path to the output PDF file.
                                    If None, the PDF file will be saved in the
                                    same directory as the Markdown file, with
                                    the same name, but with the .pdf extension.
        """
        if output_path is None:
            output_path = self.path_no_ext.with_suffix('.pdf')

        output_stream = io.BytesIO()
        output_writer = fitz.DocumentWriter(output_stream)

        pages = self.content.split('<pagebreak>')
        for idx, page in enumerate(pages):
            self._add_page(page,
                           markdown_parser=markdown.markdown,
                           output_writer=output_writer,
                           last_page=idx == (len(pages) - 1))

        output_writer.close()
        document = fitz.open('pdf', output_stream)
        document.save(output_path)
        document.close()

    def to_html(self, output_path=None):
        """
        Converts the Markdown file to an HTML file.

        Args:
            output_path (str=None): The path to the output HTML file.
                                    If None, the HTML file will be saved in the
                                    same directory as the Markdown file, with
                                    the same name, but with the .pdf extension.
        """
        if output_path is None:
            output_path = self.path_no_ext.with_suffix('.html')

        markdown.markdown(self.content,
                          extensions=list(self.plugins))

        output_path.write_text(self.content, encoding='utf-8')

    def live_pdf(self):
        """
        Converts the Markdown file to a PDF file, and updates the PDF file
        whenever the Markdown file is modified.

        Note:
            This method does not return until the program is interrupted.
        """
        self.to_pdf()
        observer = Observer()
        observer.schedule(self, str(self.path_no_ext.with_suffix('.md')))
        observer.start()

        try:
            while True:
                sleep(1)

        except KeyboardInterrupt:
            observer.stop()

        observer.join()

    def on_modified(self, event):
        """
        Required by the FileSystemEventHandler class for the live PDF
        functionality. Do not call this method directly.

        Args:
            event (FileSystemEvent): The event that triggered this method.
        """
        if event.src_path == str(self.path_no_ext.with_suffix('.md')):

            with open(event.src_path, encoding='utf-8') as file:
                self.content = file.read()

            self.to_pdf()
