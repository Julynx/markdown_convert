# Custom Syntax

- [Custom Syntax](#custom-syntax)
  - [LaTeX Math Equations](#latex-math-equations)
  - [Mermaid Diagrams](#mermaid-diagrams)
  - [Vega-Lite Charts](#vega-lite-charts)
  - [Syntax Highlighted Code Blocks](#syntax-highlighted-code-blocks)
  - [Pipe Tables](#pipe-tables)
  - [Image alt-text attributes](#image-alt-text-attributes)
  - [Image captions](#image-captions)
  - [Custom Containers](#custom-containers)
  - [Page Breaks](#page-breaks)
  - [Table of Contents](#table-of-contents)
  - [Admonitions](#admonitions)

`markdown-convert` supports several syntax shortcuts and extensions to standard Markdown.

Below are the most notable features:

## LaTeX Math Equations

```text
Inline equation: $E = mc^2$

Block equation:

$$\int_a^b f(x) \,dx = F(b) - F(a)$$
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/math-equations.png' width='100%'>

## Mermaid Diagrams

    ```mermaid
    graph TD;
        A-->B;
        A-->C;
        B-->D;
        C-->D;
    ```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/mermaid-diagram.png' width='100%'>

<details>

<summary>All supported options</summary>

Check out [mermaid.js.org/intro/#diagram-types](https://mermaid.js.org/intro/#diagram-types) for all the supported diagrams.

</details>

## Vega-Lite Charts

    ```vega-lite
    $schema: https://vega.github.io/schema/vega-lite/v6.json
    description: A scatterplot showing body mass and flipper lengths of penguins.
    data:
      url: data/penguins.json
    mark: point
    encoding:
      x:
        field: Flipper Length (mm)
        type: quantitative
        scale:
          zero: false
      y:
        field: Body Mass (g)
        type: quantitative
        scale:
          zero: false
      color:
        field: Species
        type: nominal
      shape:
        field: Species
        type: nominal
    ```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/vega-chart.png' width='100%'>

<details>

<summary>All supported options</summary>

The diagram can be specified using JSON, or YAML (as shown above).

Check out [vega.github.io/vega-lite/examples](https://vega.github.io/vega-lite/examples/) for all the supported charts.

</details>

## Syntax Highlighted Code Blocks

    ```python
    def greet(name):
        return f"Hello, {name}!"
    ```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/syntax-highlighted-code.png' width='100%'>

## Pipe Tables

```text
| Name    | Age | City          |
| ------- | --- | ------------- |
| Alice   | 30  | New York      |
| Bob     | 25  | San Francisco |
| Charlie | 35  | Los Angeles   |
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/pipe-table.png' width='100%'>

## Image alt-text attributes

```markdown
![Flower ::shadow:: ::tiny::](assets/flower.png)
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/image-attributes.png' width='100%'>

<details>

<summary>All supported options</summary>

- Size: `::tiny::`, `::small::`, `::medium::`, `::large::`, `::full::`
- Positioning: `::inline::`, `::left::`, `::right::`
- Shape: `::circle::`, `::rounded::`
- Filters: `::shadow::`, `::border::`, `::invert::`, `::grayscale::`

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/size-attributes.png' width='100%'>

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/effects.png' width='100%'>

</details>

## Image captions

```markdown
![Flower](assets/flower2.png)_A beautiful flower._
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/image-caption.png' width='100%'>

## Custom Containers

```markdown
This text is hl{{highlighted}}.
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/custom-container.png' width='100%'>

<details>

<summary>All supported options</summary>

- Colors: `red/r`, `green/g`, `blue/b`, `yellow`, `orange`, `purple`, `white`, `black`, `gray`, `brown`, `pink`
- Underline: `underline/ul`
- Highlight: `highlight/hl`
- Key: `key`
- Positioning: `center`, `right`, `justify`
- Size: `big`, `small`

You can use any arbitrary name for a container and define a matching class in your custom CSS to style it, for example:

```markdown
This text is sm{{small text}}.
```

```css
/* custom.css */
/* Use: markdown-convert --css=custom.css */
.sm {
    font-size: 0.8em;
}
```

</details>

## Page Breaks

```markdown
Two consecutive horizontal rules insert a page break:

---

---

This text is rendered on a new page.
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/page-break.png' width='100%'>

## Table of Contents

```markdown
Use `[TOC]` to insert a dynamic Table of Contents with links into the PDF file.
You can specify a maximum depth by using `[TOC depth=3]`.

[TOC]
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/toc.png' width='100%'>

## Admonitions

```markdown
.. note::
   Useful information that users should know, even when skimming content.

.. tip::
   Helpful advice for doing things better or more easily.

.. important:: Read this
   Key information users need to know to achieve their goal.

.. warning::
   Urgent info that needs immediate user attention to avoid problems.

.. caution::
   Advises about risks or negative outcomes of certain actions.
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/admonitions.png' width='100%'>
