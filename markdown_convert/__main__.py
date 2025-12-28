#!/usr/bin/env python3

"""
CLI interface to convert markdown files to pdf.
Author: @julynx
"""


from sys import exit as sys_exit

from argsdict import args
from .modules.constants import RED, OPTIONS, OPTIONS_MODES
from .modules.convert import convert, live_convert
from .modules.resources import get_css_path, get_output_path, get_usage
from .modules.utils import color
from .modules.validate import (
    validate_css_path,
    validate_markdown_path,
    validate_output_path,
)


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
            validate_markdown_path(md_path)
        except KeyError as key_err:
            raise IndexError("Missing 'markdown_file_path' argument.") from key_err
        except Exception as exc:
            raise IndexError(f"Invalid 'markdown_file_path' argument: {exc}") from exc

        # Get the mode
        try:
            mode = arg["--mode"]
            if mode not in OPTIONS_MODES:
                raise ValueError(f"Invalid mode: '{mode}'")
        except KeyError:
            mode = "once"

        # Get the CSS path
        try:
            css_path = arg["--css"]
            validate_css_path(css_path)
        except KeyError:
            css_path = get_css_path()
        except Exception as exc:
            raise IndexError(f"Invalid 'css_file_path' argument: {exc}") from exc

        # Get the output path
        output_path = None
        try:
            output_path = arg["--out"]
            validate_output_path(output_path)
            output_path = get_output_path(md_path, output_path)
        except KeyError:
            output_path = get_output_path(md_path, None)
        except Exception as exc:
            raise IndexError(f"Invalid 'output_path' argument: {exc}") from exc

        # Compile the markdown file
        print(f"\nGenerating PDF file from '{md_path}'...\n")
        if mode in ("once", "debug"):
            convert(md_path, css_path, output_path, dump_html=mode == "debug")
        else:
            live_convert(md_path, css_path, output_path)

        sys_exit(0)

    # pylint: disable=W0718
    except Exception as err:

        asked_for_help = "--help" in arg or "-h" in arg
        show_usage = isinstance(err, (IndexError, ValueError)) or asked_for_help

        if show_usage:
            print(get_usage())

        if not asked_for_help:
            print(color(RED, f"ERROR: {err}\n"))

        sys_exit(1)


if __name__ == "__main__":
    main()
