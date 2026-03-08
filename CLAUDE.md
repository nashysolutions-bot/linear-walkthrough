# linear-walkthrough

Generate self-contained, GitHub-styled HTML walkthroughs from GFM markdown.

## Quick Start

```bash
uv run linear-walkthrough input.md -o output.html   # file input
cat input.md | uv run linear-walkthrough -o out.html # stdin pipe
uv run linear-walkthrough input.md                   # stdout
uv run linear-walkthrough input.md --serve           # interactive server mode
uvx linear-walkthrough input.md -o output.html       # run from github
```

## Project Structure

```
linear_walkthrough/
  cli.py           - CLI entry point (argparse, stdin/file input, stdout/-o output)
  renderer.py      - Core rendering: markdown -> HTML via markdown-it-py + Pygments
  template.py      - Minijinja template loader, CSS constants, render_template()
  server.py        - Interactive server mode (stdlib http.server, claude subprocess)
  templates/
    page.html              - Jinja2 HTML template for static output
    page_interactive.html  - Interactive template with text selection + follow-up JS
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

## Interactive Server Mode

- `--serve` starts a local HTTP server (default port 7847) with text selection UI
- `--cwd` sets working directory for `claude` subprocess (defaults to input file's directory)
- Follow-ups use `claude -c -p` to continue conversation context
- Server seeds Claude with the full walkthrough on first start
- Follow-up responses are written to `.linear-walkthrough/followups/` alongside the input file
- Follow-up files use descriptive slugs (e.g. `1-broadcaster-handle.md`) instead of generic numbering
- Follow-up headings reflect the topic, not the internal prompt
- All client-side JS is vanilla (no frameworks, no build step)

## Dev Tools

```bash
uv run ruff check .    # lint
uv run mypy .          # type check
uv run pytest          # test
```

## Testing/examples
output files to ignore/ as it is gitignored
