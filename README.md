# markdown-convert

_Convert Markdown files to PDF from your command line._

`pip install markdown-convert`

<br>

[![Button Hover](https://img.shields.io/badge/Github-c9510c?style=for-the-badge)](https://github.com/Julynx/markdown-convert)
[![Button Hover](https://img.shields.io/badge/PyPi-006dad?style=for-the-badge)](https://pypi.org/project/markdown_convert)

<br>

<img src='https://i.imgur.com/kzoo3hs.png'>

<br>

---

- [markdown-convert](#markdown-convert)
  - [Why `markdown-convert`?](#why-markdown-convert)
  - [Installation](#installation)
  - [Usage](#usage)
    - [1. From your terminal](#1-from-your-terminal)
    - [2. As a Python library](#2-as-a-python-library)
    - [3. From the context menu of your file explorer](#3-from-the-context-menu-of-your-file-explorer)

## Why `markdown-convert`?

Unlike other similar tools, `markdown-convert`:

- Can be fully installed via `pip install markdown-convert`, with no external system-level dependencies.
- Comes with a sensible default CSS stylesheet out of the box.
- Supports:

  | **Feature**                                           | **Example**                                                                                        |
  | ----------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
  | **LaTeX Math Equations**                              | `$E=mc^2$` is rendered as a math equation.                                                         |
  | **Mermaid, Vega-Lite and Schemdraw Diagrams**         | ` ```mermaid ...` is rendered as a diagram.                                                        |
  | **Syntax-Highlighted Code Blocks**                    | ` ```python ...` gets syntax highlighting.                                                         |
  | **Admonitions**                                       | `!!! note` is styled as a note box.                                                                |
  | **Dynamic Table of Contents**                         | `[TOC]` inserts a Table of Contents.                                                               |
  | **Image Attributes**                                  | `![::shadow::](sky.png)` shows a shadow behind the image.                                          |
  | **Captions**                                          | `![sky](sky.png)_A beautiful sky_` shows a caption, centered below the image.                      |
  | **Tables and Queries**                                | `> [my_table]` under your table gives it a name,<br>`[query:select ... from my_table]` queries it. |
  | **Live conversion**                                   | `markdown-convert file.md --mode=live` updates the PDF every time the Markdown file changes.       |
  | **Custom CSS**                                        | `markdown-convert file.md --css=style.css` extends the default CSS with your own stylesheet.       |
  | **Task lists, containers, CSS paged media and more!** | ...                                                                                                |

  > [!NOTE]
  > Check out [CUSTOM_SYNTAX.md](https://github.com/Julynx/markdown_convert/blob/main/CUSTOM_SYNTAX.md) for all the extra features and how to use them.

## Installation

`markdown-convert` is available on PyPI and can be installed via pip:

```bash
pip install markdown-convert
```

## Usage

### 1. From your terminal

Simply run `markdown-convert file.md` to convert `file.md` to `file.pdf`.

You can specify the following options:

```text
Usage:
  markdown-convert [markdown_file_path] [options]

Options:
  --mode=once|live|debug
      Convert the markdown file once (default) or live.
      Use debug to preserve the intermediate html file.
  --css=[css_file_path]
      Use a custom CSS file.
  --out=[output_file_path]
      Specify the output file path.
  --extras=[extra1,extra2,...]
      Specify the extras to use. Uses all extras if not specified.
      Supported extras:
        admonitions,anchors,task-lists,math,custom-spans,highlights,
        syntax-highlighting,table-of-contents,vega-lite,inline-math,
        block-math,schemdraw,mermaid,dynamic-tables,dynamic-queries
  --security=default|strict
      Specify the security level.
      Strict mode disables inline HTML, internet access and JS,
      but local files can still be referenced.
      This improves security, but will break some extras.
```

For example: `markdown-convert README.md --mode=live --css=style.css --out=output.pdf` will convert `README.md` to `output.pdf` using `style.css` and update the PDF live as you edit the Markdown file.

### 2. As a Python library

You can also use `markdown-convert` as a library in your Python code:

```python
from markdown_convert import convert, convert_text, live_convert

# Convert your Markdown file and save it as a PDF file
convert('README.md', 'style.css', 'README.pdf')

# Convert your Markdown string and get the PDF bytes
pdf_bytes = convert_text('# Hello World', 'h1 { color: red; }')

# Convert your Markdown file to PDF every time it changes
live_convert('README.md', 'style.css', 'README.pdf')
```

### 3. From the context menu of your file explorer

Install the extension of your choice:

- For Windows Explorer: [markdown_convert_explorer](https://github.com/Julynx/markdown_convert_explorer)
- For Linux (Nautilus): [markdown_convert_nautilus](https://github.com/Julynx/markdown_convert_nautilus)

Then right click any Markdown file and select `Convert to PDF` to convert it.
