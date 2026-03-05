# claude-linear-walkthrough

Generate self-contained, GitHub-styled HTML walkthroughs from GFM markdown.

## Quick Start

```bash
uv run python main.py input.md -o output.html   # file input
cat input.md | uv run python main.py -o out.html # stdin pipe
uv run python main.py input.md                   # stdout
```

## Project Structure

```
main.py          - CLI entry point (argparse, stdin/file input, stdout/-o output)
renderer.py      - Core rendering: markdown -> HTML via markdown-it-py + Pygments
template.py      - Minijinja template loader, CSS constants, render_template()
templates/
  page.html      - Jinja2 HTML template for the output page
docs/plans/      - Design documents
```

## Tech Stack

- **Python 3.13+**, managed with **uv**
- **markdown-it-py** - GFM markdown parsing (linkify disabled, no extra dep needed)
- **Pygments** - Syntax highlighting (class-based CSS, `default` light / `github-dark` dark)
- **minijinja** - HTML templating (use `Markup()` to pass raw HTML/CSS)
- **Mermaid.js** - Diagram rendering (loaded from CDN in output HTML)

## Key Patterns

- Pygments uses class-based spans (not inline styles). Light/dark CSS generated via `HtmlFormatter.get_style_defs()` with `@media (prefers-color-scheme: dark)` wrapper.
- markdown-it-py's `gfm-like` preset has linkify disabled to avoid requiring the `linkify-it-py` dependency.
- The fence render rule override needs `_self` as first parameter (it's a method replacement).
- Template variables `css` and `content` must be wrapped in `Markup()` to prevent auto-escaping.

## Dev Tools

```bash
uv run ruff check .    # lint
uv run mypy .          # type check
uv run pytest          # test
```

## Testing/examples
output files to ignore/ as it is gitignored
