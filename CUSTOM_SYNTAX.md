# Custom Syntax

- [Custom Syntax](#custom-syntax)
  - [LaTeX Math Equations](#latex-math-equations)
  - [Mermaid Diagrams](#mermaid-diagrams)
  - [Vega-Lite Charts](#vega-lite-charts)
  - [Schemdraw Diagrams](#schemdraw-diagrams)
  - [Syntax Highlighted Code Blocks](#syntax-highlighted-code-blocks)
  - [Pipe Tables](#pipe-tables)
  - [Dynamic Tables and Queries](#dynamic-tables-and-queries)
  - [Image Alt-text Attributes](#image-alt-text-attributes)
  - [Image Captions](#image-captions)
  - [Custom Containers](#custom-containers)
  - [Page Breaks](#page-breaks)
  - [Table of Contents](#table-of-contents)
  - [Admonitions](#admonitions)

`markdown-convert` supports several syntax shortcuts and extensions to standard Markdown.

Below are the most notable features:

## LaTeX Math Equations

> _Extra: `latex` (enabled by default)_

```text
Inline equation: $E = mc^2$

Block equation:

$$\int_a^b f(x) \,dx = F(b) - F(a)$$
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/math-equations.png' width='100%'>

## Mermaid Diagrams

> _Extra: `mermaid` (enabled by default)_

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

> _Extra: `vega-lite` (enabled by default)_

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

With the `dynamic-tables` and `dynamic-queries` extras (enabled by default), you can use a table as the source for a chart:

    | department  | employees | satisfaction |
    | ----------- | --------- | ------------ |
    | Engineering | 45        | 8.2          |
    | Sales       | 30        | 7.5          |
    | Marketing   | 15        | 8.9          |
    | HR          | 8         | 9.1          |

    > [company_stats] Department statistics for 2026

    ```vega
    $schema: https://vega.github.io/schema/vega-lite/v5.json
    width: 400
    height: 300
    description: A bar chart showing employees per department
    data:
      query: "SELECT department, employees FROM company_stats ORDER BY employees DESC"
    mark: bar
    encoding:
      x:
        field: department
        type: nominal
        axis: {labelAngle: 0}
      y:
        field: employees
        type: quantitative
    ```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/vega-chart-with-query.png' width='100%'>

Check out [vega.github.io/vega-lite/examples](https://vega.github.io/vega-lite/examples/) for all the supported charts.

</details>

## Schemdraw Diagrams

> _Extra: `schemdraw` (enabled by default)_

    ```schemdraw
    V1:
      - elements.SourceV
      - label: ["5V"]

    line1:
      - elements.Line
      - right: [0.75]

    S1:
      - elements.SwitchSpdt2: [{ action: close }]
      - up
      - anchor: ["b"]
      - label: ["$t=0$", { loc: rgt }]

    line2:
      - elements.Line
      - right: [0.75]
      - at: ["S1.c"]

    R1:
      - elements.Resistor
      - down
      - label: ["$100\\Omega$"]
      - label: [["+", "$v_o$", "-"], { loc: bot }]

    line3:
      - elements.Line
      - to: ["V1.start"]

    C1:
      - elements.Capacitor
      - at: ["S1.a"]
      - toy: ["V1.start"]
      - label: ["1$\\mu$F"]
      - dot
    ```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/schemdraw-diagram.png' width='100%'>

<details>

<summary>All supported options</summary>

The diagram must be specified using YAML.

The example above is equivalent to the following Python code:

```python
with schemdraw.Drawing() as d:
    V1 = elm.SourceV().label('5V')
    elm.Line().right(d.unit*.75)
    S1 = elm.SwitchSpdt2(action='close').up().anchor('b').label('$t=0$', loc='rgt')
    elm.Line().right(d.unit*.75).at(S1.c)
    elm.Resistor().down().label(r'$100\Omega$').label(['+','$v_o$','-'], loc='bot')
    elm.Line().to(V1.start)
    elm.Capacitor().at(S1.a).toy(V1.start).label(r'1$\mu$F').dot()
```

Check out [schemdraw.readthedocs.io](https://schemdraw.readthedocs.io/en/stable/) and [yaml-to-schemdraw](https://pypi.org/project/yaml-to-schemdraw/) for more information.

</details>

## Syntax Highlighted Code Blocks

> _Extra: `fenced-code-blocks` (enabled by default)_

    ```python
    def greet(name):
        return f"Hello, {name}!"
    ```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/syntax-highlighted-code.png' width='100%'>

## Pipe Tables

> _Extra: `tables` (enabled by default)_

```text
| Name    | Age | City          |
| ------- | --- | ------------- |
| Alice   | 30  | New York      |
| Bob     | 25  | San Francisco |
| Charlie | 35  | Los Angeles   |
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/pipe-table.png' width='100%'>

## Dynamic Tables and Queries

> _Extra: `dynamic-tables` and `dynamic-queries` (enabled by default)_

```markdown
| Product | Price | Quantity |
| ------- | ----- | -------- |
| Apple   | 1     | 10       |
| Banana  | 2     | 20       |
| Orange  | 3     | 30       |

> [sales] Sales data for fruits

- The average price is [query: select avg(price) from sales] dollars.
- The total quantity is [query: select sum(quantity) from sales].

Fruits with price > 2:

[query: select * from sales where price > 2]
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/dynamic-tables.png' width='100%'>

## Image Alt-text Attributes

> _Provided by the default CSS_

```markdown
![Flower ::shadow:: ::tiny::](assets/flower.png)
````

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

## Image Captions

> _Provided by the default CSS_

```markdown
![Flower](assets/flower2.png)_A beautiful flower._
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/image-caption.png' width='100%'>

## Custom Containers

> _Extra: `custom-spans` (enabled by default)_

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
overline{{This text}} has a line over it.
```

```css
/* custom.css */
/* Use: markdown-convert --css=custom.css */
.overline {
  text-decoration: overline;
}
```

</details>

## Page Breaks

> _Provided by the default CSS_

```markdown
Two consecutive horizontal rules insert a page break:

---

---

This text is rendered on a new page.
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/page-break.png' width='100%'>

## Table of Contents

> _Extra `toc` (enabled by default)_

```markdown
Use `[TOC]` to insert a dynamic Table of Contents with links into the PDF file.
You can specify a maximum depth by using `[TOC depth=3]`.

[TOC]
```

<img src='https://raw.githubusercontent.com/Julynx/markdown_convert/refs/heads/main/assets/toc.png' width='100%'>

## Admonitions

> _Extra `admonitions` (enabled by default)_

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
