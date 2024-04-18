# markdown-convert

_Convert Markdown files to PDF from your command line._

### `pip install markdown-convert`

[<kbd> 🐱 GitHub </kbd>](https://github.com/Julynx/markdown-convert) [<kbd> 📦 PyPi </kbd>](https://pypi.org/project/markdown_convert) 

<img src='https://i.imgur.com/SZIz2gY.png' width='80%'>

`markdown-convert` is an elegant command-line tool that converts Markdown files to PDF, powered by the amazing `markdown2` and `weasyprint` libraries.

Unlike other similar tools, it relies solely on Python packages to do the job, eliminating the need for any external system-level dependencies when running on Linux.

If you're running Windows, you only need to install the GTK-3 runtime from the following link: [GTK-3 Runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases).

### Features

- ⚡️ Supports live compilation, so you can preview your PDF in real-time as you type.
- 🌸 Comes with beautiful CSS out of the box, making your documents look great from the start.
- 🎨 Syntax highlighting for code blocks included.
- 🪐 Designed for the 21st century, with relative links, pipe tables, and modern CSS paged media features.

### Usage

> Note: If you just installed the package, you may need to log out and log back in for the `markdown-convert` command to be registered to your PATH.

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
convert('README.md', 'style.css', 'README.pdf')

# Convert your Markdown file to PDF every time it changes
live_convert('README.md', 'style.css', 'README.pdf')
```

### Integrations

Right click a Markdown file and `Convert to PDF` with the [markdown_convert_explorer](https://github.com/Julynx/markdown_convert_explorer) and [markdown_convert_nautilus](https://github.com/Julynx/markdown_convert_nautilus) extensions for Windows and Linux.
