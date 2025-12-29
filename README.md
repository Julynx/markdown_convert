# markdown-convert

_Convert Markdown files to PDF from your command line._

`pip install markdown-convert`

<br>

[![Button Hover](https://img.shields.io/badge/Github-c9510c?style=for-the-badge)](https://github.com/Julynx/markdown-convert)
[![Button Hover](https://img.shields.io/badge/PyPi-006dad?style=for-the-badge)](https://pypi.org/project/markdown_convert)

<br>

<img src='https://i.imgur.com/uWDm7s0.png' width='80%'>

----

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
  - **LaTeX math equations:** `$...$` for inline and `$$...$$` for block equations.
  - **Syntax highlighting for code blocks:** Applied automatically based on the specified language.
  - **Live conversion:** `markdown-convert file.md --mode=live` updates the PDF every time the Markdown file changes.
  - **Custom CSS** `markdown-convert file.md --css=style.css` extends the default CSS with your own stylesheet.
  - **Pipe tables, header links, CSS paged media features and more!**

## Installation

`markdown-convert` is available on PyPI and can be installed via pip:

```bash
pip install markdown-convert
```

## Usage

### 1. From your terminal

Simply run `markdown-convert file.md` to convert `file.md` to `file.pdf`.

You can specify the following options:

- `--mode=once|live`: Convert the markdown file once (default) or live.
- `--css=[css_file_path]`: Use a custom CSS file.
- `--out=[output_file_path]`: Specify the output file path.

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
