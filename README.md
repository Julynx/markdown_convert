# markdown-convert

_Convert Markdown files to PDF from your command line._

### `pip install markdown-convert`
<img src='https://i.imgur.com/UuJL8Ls.png' width='80%'>

`markdown-convert` is an elegant command-line tool that converts Markdown files to PDF.

It is powered by the amazing `markdown2` and `weasyprint` libraries, and unlike other similar tools, it relies solely on Python packages to do the job, eliminating the need for any external system-level dependencies.

### Features

- ⚡️ Supports live compilation, so you can preview your PDF in real-time as you type.
- 🌸 Comes with beautiful CSS out of the box, making your documents look great from the start.
- 🎨 Syntax highlighting for code blocks included.
- 🪐 Designed for the 21st century, with relative links, pipe tables, and modern CSS paged media features.

### Usage

Run `markdown-convert -h` right from your terminal to check out the available options:

```bash
Usage:
  markdown-convert [markdown_file_path] [options]

Options:
  --mode=once|live
    Convert the markdown file once (default) or live.
  --css=[css_file_path]
    Use a custom CSS file.
  --out=[output_file_path]
    Specify the output file path.
```

...or import any of the functions from the package to use them in your own code:

```python
from markdown_convert import convert, live_convert

# Convert your Markdown file to PDF once
convert('README.md', "style.css", 'README.pdf')

# Convert your Markdown file to PDF every time it changes
live_convert('README.md', "style.css", 'README.pdf')
```
