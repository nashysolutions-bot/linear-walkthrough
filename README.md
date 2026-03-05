# linear-walkthrough

Generate self-contained, GitHub-styled HTML walkthroughs from GFM markdown.

Takes markdown files with code walkthroughs and produces single-file HTML pages with syntax highlighting, dark mode support, and Mermaid diagram rendering. Optionally launches an interactive server where you can select text and ask Claude follow-up questions.

## Quick Start

```bash
# File input → file output
uv run python main.py input.md -o output.html

# Stdin → stdout
cat input.md | uv run python main.py -o out.html

# Interactive server mode (opens browser)
uv run python main.py input.md --serve
```

## Features

- **GFM markdown** — tables, task lists, fenced code blocks
- **Syntax highlighting** — Pygments with light/dark theme support via `prefers-color-scheme`
- **Mermaid diagrams** — rendered client-side from fenced `mermaid` blocks
- **Self-contained output** — single HTML file with all CSS inlined
- **Interactive mode** — select text in the browser, ask Claude follow-up questions, responses appended to the source file

## Interactive Server Mode

```bash
uv run python main.py walkthrough.md --serve [-p PORT] [--cwd DIR]
```

Starts a local HTTP server (default port 7847) that renders your walkthrough with a text selection UI. Select any text and ask a question — Claude responds using the full walkthrough as context. Follow-up responses are appended to the original markdown file.

## Project Structure

```
main.py          - CLI entry point
renderer.py      - Markdown → HTML via markdown-it-py + Pygments
template.py      - Minijinja template loader + CSS
server.py        - Interactive server mode (stdlib http.server + claude subprocess)
templates/
  page.html              - Static output template
  page_interactive.html  - Interactive template with follow-up JS
```

## Tech Stack

- **Python 3.13+** managed with **uv**
- **markdown-it-py** — GFM parsing
- **Pygments** — syntax highlighting
- **minijinja** — HTML templating
- **Mermaid.js** — diagram rendering (CDN)

## Development

```bash
uv run ruff check .    # lint
uv run mypy .          # type check
uv run pytest          # test
```
