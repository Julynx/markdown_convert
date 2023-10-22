# markdown-convert

_Python package to convert Markdown files to other formats._

<br>
<p align="center">
  <img width="600" src="https://i.imgur.com/VZJc4cN.png">
</p>
<br>

With `markdown-convert`, you can easily convert a Markdown file to PDF
with the following features:

- User-defined CSS styles.
- Customizable document margins.
- Live PDF compilation.
- Manual insertion of page breaks.

To start using it, simply `pip install markdown-convert`.

<br>

## Usage example

```python
from markdown_convert import MarkdownFile

MarkdownFile("markdown.md").to_pdf()    # One time conversion
MarkdownFile("markdown.md").live_pdf()  # Real-time conversion
```

<br>

## Documentation

### MarkdownFile

#### __init__

- `md_path` - Path to the Markdown file.
- `css_path='css/default.css'` - Path to the CSS file.
- `margin_h=62` - Horizontal margin of the PDF file.
- `margin_v=60` - Vertical margin of the PDF file.

#### use

- `plugin` - Name of the [extension](https://python-markdown.github.io/extensions/) to add to the set of used extensions.

  > The extensions `extra` and `sane_lists` are included by default.

#### to_html

- `output_path=None` - Path to the output HTML file.

  > If not specified, the HTML file will have the same name, but with the `.html` extension.

#### to_pdf

- `output_path=None` - Path to the output PDF file.

  > If not specified, the PDF file will have the same name, but with the `.pdf` extension.

#### live_pdf

- (Takes no arguments).

  > The PDF file will be updated whenever the Markdown file changes on disk.

<br>

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).