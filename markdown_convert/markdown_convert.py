#!/usr/bin/env python3

"""
CLI interface to convert markdown files to pdf.
Author: @julynx
"""

import os
import subprocess
from pathlib import Path
from sys import exit as sys_exit
from argsdict import args
from string_grab import grab_all

RED = '31'
GREEN = '32'
YELLOW = '33'
BLUE = '34'
MAGENTA = '35'
CYAN = '36'
WHITE = '37'

SIGINT = 2

OPTIONS = ('markdown_file_path', '--mode', '--css', '--extract-opts')
MODES = ('once', 'watch')
EXTRACT_VALS = ('true', 'false')


def main():
    """
    Convert a markdown file to a pdf file.
    """
    try:
        # Load and validate arguments
        arg = args(["markdown_file_path"])
        for key in set(arg.keys()) - set(OPTIONS):
            raise IndexError(f"Invalid option: '{key}'")

        # Get the markdown path
        try:
            md_path = arg["markdown_file_path"]
        except KeyError as key_err:
            raise IndexError("Missing 'markdown_file_path' argument.") \
                from key_err

        # Get the conversion mode
        mode = arg.get("--mode", 'once')
        if mode not in MODES:
            raise IndexError(f"Invalid mode: '{mode}'")

        # Get the CSS path
        try:
            css_path = arg["--css"]
        except KeyError:
            def_css = f"{Path.home()}/.local/share/pandoc/default.css"
            css_path = def_css if Path(def_css).exists() else None

        # Get the extract options if needed
        extract = arg.get("--extract-opts", 'true') == 'true'

        # Set the watch command
        watch_command = ["inotifywait", "-e", "close_write", md_path, css_path]

        # Compile the markdown file once
        if mode == 'once':
            print(f'\nGenerating PDF file from \'{md_path}\'...\n')
            convert(md_path, css_path, extract)  # raises RuntimeError

        # Watch the markdown file for changes
        elif mode == 'watch':
            handle = None
            try:
                handle = aconvert(md_path, css_path, extract)
                print(f'\nWatching \'{md_path}\' for changes...\n')
                while True:
                    subprocess.call(watch_command)
                    aconvert_stop(handle)
                    handle = aconvert(md_path, css_path, extract)

            except KeyboardInterrupt:
                print('\nExiting...\n')

            finally:
                aconvert_stop(handle)

        sys_exit(0)

    except Exception as err:
        if isinstance(err, (IndexError, ValueError)):
            print(get_usage())
        print(c(f"ERROR: {err}\n", RED))
        sys_exit(1)


def convert(md_path, css_path, extract_args=False):
    """
    Convert a markdown file to a pdf file.

    Args:
        md_path (str): Path to the markdown file.
        css_path (str): Path to the CSS file.
        extra_args (bool): Extract arguments from 'md_path' to pass to pandoc.

    Raises:
        RuntimeError: If the conversion fails.
    """
    if extract_args:
        extra_args = extract_opts(md_path)

    convert_command = _build_convert_command(md_path, css_path,
                                             extra_args=extra_args)

    try:
        with open(os.devnull, 'w') as dev_null:
            subprocess.check_call(convert_command, stdin=dev_null, stdout=dev_null, stderr=dev_null)
    except subprocess.CalledProcessError as err:
        raise RuntimeError(f"Command '{' '.join(convert_command)}'\n       "
                           f"returned non-zero exit status {err.returncode}.") \
            from err


def aconvert(md_path, css_path, extract_args=False):
    """
    Asynchronous version of convert.

    Args:
        md_path (str): Path to the markdown file.
        css_path (str): Path to the CSS file.
        extra_args (bool): Extract arguments from 'md_path' to pass to pandoc.

    Returns:
        handle: A subprocess handle. (Popen object)
    """
    if extract_args:
        extra_args = extract_opts(md_path)

    convert_command = _build_convert_command(md_path, css_path,
                                             extra_args=extra_args)

    return subprocess.Popen(convert_command)


def aconvert_stop(handle):
    """
    Stop an asynchronous conversion.

    Args:
        handle: A subprocess handle. (Popen object)
    """
    if handle:
        handle.send_signal(SIGINT)
        handle.wait()


def _build_convert_command(md_path, css_path, *, extra_args=None):
    """
    Build the command to convert a markdown file to a pdf file.

    Args:
        md_path (str): Path to the markdown file.
        css_path (str): Path to the CSS file.
        extra_args (list): Extra arguments to pass to pandoc.

    Returns:
        list: The command to convert the markdown file to a pdf file.
    """
    extra_args = extra_args if extra_args is not None else []

    cmd = ["pandoc",
           "--pdf-engine", "wkhtmltopdf",
           *extra_args,
           "--pdf-engine-opt=--enable-local-file-access",
           "--pdf-engine-opt=--disable-smart-shrinking",
           "-i", md_path,
           "-o", md_path.replace('.md', '.pdf')]

    if css_path is not None:
        cmd += ["--css", css_path]

    return cmd


def extract_opts(md_path, max_opt_len=1024):
    """
    Extract '--pdf-engine-opt' options from a markdown file.

    Args:
        md_path (str): Path to the markdown file.
        max_opt_len (int): Maximum length of an option.

    Returns:
        list: The extracted options.
    """
    def _sanitize(text):
        """
        Remove all non-alphanumeric characters from a string.
        Allows hyphens and brackets.

        Args:
            text (str): The text to sanitize.

        Returns:
            str: The sanitized text.
        """
        allowed = "-[] "
        return ''.join([c for c in text if c.isalnum() or c in allowed])

    file_contents = Path(md_path).read_text()

    clean_opts = []
    for option_group in grab_all(file_contents, start='[option]: <> (', end=')'):

        if len(option_group) > max_opt_len:
            continue

        formatted_options = []
        for idx, option in enumerate(option_group.split(" ", maxsplit=1)):

            option = _sanitize(option)

            if not option.startswith("-") and idx == 0:
                formatted_options.append(f"--{option}")
            else:
                formatted_options.append(option)

        clean_opts += [f"--pdf-engine-opt={opt}" for opt in formatted_options]

    return clean_opts


def get_usage():
    """
    Returns a message describing how to use the program.

    Returns:
        str: The usage message.
    """
    commd = f"{c('md_to_pdf', GREEN)} [{c(OPTIONS[0], YELLOW)}] [{c('options', BLUE)}]"
    opt_1 = c(OPTIONS[1], BLUE) + c("=", CYAN) + c('|'.join(MODES), CYAN)
    opt_2 = c(OPTIONS[2], BLUE) + c("=", CYAN) + c('"~/.local/share/pandoc/default.css"', CYAN)
    opt_3 = c(OPTIONS[3], BLUE) + c("=", CYAN) + c('|'.join(EXTRACT_VALS), CYAN)
    syntax_example = c("[option]: <> (footer-center [page])", CYAN)

    usage = ("\n"
             "Usage:\n"
             f"  {commd}\n"
             "\n"
             "Options:\n"
             f"  {opt_1}\n"
             "    Compile once (default), or every time the file changes.\n"
             "\n"
             f"  {opt_2}\n"
             "    Use a custom CSS file provided as an argument, or the file\n"
             "    above if it exists (default).\n"
             "\n"
             f"  {opt_3}\n"
             "    Extract '--pdf-engine-opt' options from the Markdown file.\n"
             "    Can be set to 'true' (default) or 'false'.\n"
             "    '--enable-local-file-access' and '--disable-smart-shrinking'\n"
             "    are always included. Some options are disabled for security.\n"
             f"    Example syntax: {syntax_example}\n"
             )
    return usage


def c(text, color):
    """
    Colorize text.

    Args:
        text (str): The text to colorize.
        color (str): The color code.

    Returns:
        str: The colorized text.
    """
    return f"\033[{color}m{text}\033[0m"


if __name__ == '__main__':
    main()
