# BRIEF: markdown-convert

> Convert Markdown files to PDF from your command line.

## 1. Overview (README)

```markdown
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
... (truncated) [Read more](file:///D:/_DISK_/_Documentos_/Mis_repositorios/markdown-convert/README.md)
```

## 2. Dependencies

```text
argsdict==1.0.0
markdown2>=2.4.13,<3
pygments>=2.17.2,<3
latex2mathml>=3.78.1
playwright>=1.57.0
beautifulsoup4>=4.14.3
install-playwright>=1.0.0
vl-convert-python>=1.9.0.post1
ruamel-yaml>=0.19.1
yaml-to-schemdraw>=0.1.2
```

## 3. Directory Structure

```text
markdown-convert/
├── assets
    ├── admonitions.png
    ├── custom-container.png
    ├── effects.png
    ├── flower.png
    ├── flower2.png
    ├── image-attributes.png
    ├── image-caption.png
    ├── math-equations.png
    ├── mermaid-diagram.png
    ├── page-break.png
    ├── pipe-table.png
    ├── schemdraw-diagram.png
    ├── size-attributes.png
    ├── syntax-highlighted-code.png
    ├── toc.png
    └── vega-chart.png
├── markdown_convert
    ├── modules
        ├── __init__.py
        ├── autoinstall.py
        ├── constants.py
        ├── convert.py
        ├── extras.py
        ├── overrides.py
        ├── resources.py
        ├── transform.py
        ├── utils.py
        └── validate.py
    ├── __init__.py
    ├── __main__.py
    ├── code.css
    └── default.css
├── .gitignore
├── .python-version
├── CUSTOM_SYNTAX.md
├── LICENSE
├── README.md
├── TODO.md
├── pyproject.toml
└── uv.lock
```

## 4. Import Tree

```text
- markdown_convert\__init__.py
  - markdown_convert\__main__.py
    - markdown_convert\modules\constants.py
      - markdown_convert\modules\extras.py
    - markdown_convert\modules\convert.py
      - markdown_convert\modules\autoinstall.py
        - markdown_convert\modules\constants.py (...)
        - markdown_convert\modules\utils.py
      - markdown_convert\modules\constants.py (...)
      - markdown_convert\modules\overrides.py
      - markdown_convert\modules\resources.py
        - markdown_convert\modules\constants.py (...)
        - markdown_convert\modules\utils.py
      - markdown_convert\modules\transform.py
        - markdown_convert\modules\extras.py
    - markdown_convert\modules\resources.py (...)
    - markdown_convert\modules\utils.py
    - markdown_convert\modules\validate.py
  - markdown_convert\modules\convert.py (...)

- markdown_convert\modules\__init__.py
```

## 5. Module Definitions

### markdown_convert\__main__.py

```text
- def main()
```

### markdown_convert\modules\autoinstall.py

```text
- def ensure_chromium(loud)
- def is_browser_installed(browser)
```

### markdown_convert\modules\constants.py

```text
- def resolve_extras(extras_list)
```

### markdown_convert\modules\convert.py

```text
- def convert(markdown_path: Path, css_path: Path, output_path)
- def live_convert(markdown_path, css_path, output_path)
- def convert_text(markdown_text, css_text, output_path)
- class LiveConverter
  - def get_last_modified_date(self, file_path)
  - def write_pdf(self)
  - def observe(self, poll_interval)
```

### markdown_convert\modules\extras.py

```text
- class ExtraFeature
  - def replace(match, html)
- class CheckboxExtra(ExtraFeature)
  - def replace(match, html)
- class HighlightExtra(ExtraFeature)
  - def replace(match, html)
- class CustomSpanExtra(ExtraFeature)
  - def replace(match, html)
- class TocExtra(ExtraFeature)
  - def replace(match, html)
- class VegaExtra(ExtraFeature)
  - def replace(match, html)
- class SchemDrawExtra(ExtraFeature)
  - def replace(match, html)
- def apply_extras(extras: set[ExtraFeature], html, before_stash)
```

### markdown_convert\modules\overrides.py

```text
- def tags(self, lexer_name: str) -> tuple[str, str]
```

### markdown_convert\modules\resources.py

```text
- def get_output_path(markdown_path, output_dir)
- def get_css_path()
- def get_code_css_path()
- def get_usage()
```

### markdown_convert\modules\transform.py

```text
- def create_html_document(html_content, css_content, csp)
- def create_sections(html_string)
- def render_mermaid_diagrams(html)
- def render_extra_features(html, extras: set[ExtraFeature])
```

### markdown_convert\modules\utils.py

```text
- def color(color_code, text)
```

### markdown_convert\modules\validate.py

```text
- def validate_markdown_path(markdown_path)
- def validate_css_path(css_path)
- def validate_output_path(output_dir)
```
