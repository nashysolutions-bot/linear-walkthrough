# Markdown to HTML Renderer Design

## Goal

Convert GFM markdown walkthroughs into self-contained, GitHub-styled HTML files suitable for embedding and distribution.

## Architecture

```
markdown string
    -> markdown-it-py (parse + render to HTML fragment)
    -> Pygments (syntax highlight code blocks)
    -> Mermaid.js (client-side diagram rendering)
    -> wrap in HTML template (inline CSS, GitHub-style + dark mode)
    -> output self-contained HTML file
```

## Dependencies

- `markdown-it-py[plugins]` -- GFM parsing and rendering
- `pygments` -- syntax highlighting for code blocks

No external tools required (no pandoc, no node).

## CLI Interface

```bash
# From file
uv run main.py walkthrough.md

# From stdin
cat walkthrough.md | uv run main.py

# Output to file instead of stdout
uv run main.py walkthrough.md -o output.html
```

Output goes to stdout by default, `-o` flag writes to a file.

## HTML Output

Single self-contained HTML file with all CSS inlined. Structure:

```html
<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    /* GitHub markdown-body CSS (from github-markdown-css, MIT) */
    /* Pygments syntax highlighting CSS (light + dark) */
  </style>
</head>
<body>
  <article class="markdown-body">
    {rendered_html}
  </article>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({ startOnLoad: true, theme: 'default' });</script>
</body>
</html>
```

### Styling

- Trimmed GitHub `markdown-body` CSS (MIT licensed via github-markdown-css)
- Pygments inline `<span>` styles for code highlighting
- `prefers-color-scheme: dark` media query for automatic light/dark mode
- Title extracted from first `# heading`, falling back to filename

### Code Blocks

- Language label in the top-right corner (e.g., "python")
- Syntax highlighting via Pygments
- Horizontal scroll for long lines

### Mermaid Diagrams

- Fenced code blocks with language `mermaid` render as `<div class="mermaid">` instead of highlighted code
- Mermaid.js loaded from CDN (~1.5MB, too large to inline)
- Future: `--inline-mermaid` flag for offline use

## Module Structure

```
linear-walkthrough/
  main.py        -- CLI entry point (argparse, stdin/file, output)
  renderer.py    -- Core: markdown -> HTML conversion
  template.py    -- HTML template string + CSS
  pyproject.toml
  README.md
```

### renderer.py

- `render_markdown(source: str) -> str` -- converts markdown to HTML fragment, routes mermaid blocks to `<div class="mermaid">`
- `render_page(source: str, title: str | None = None) -> str` -- wraps fragment in full HTML template

### template.py

- `HTML_TEMPLATE` -- HTML shell with `{title}`, `{content}` placeholders
- `GITHUB_CSS` -- trimmed GitHub markdown CSS
- `PYGMENTS_CSS` -- light + dark theme styles

### main.py

- Read from file arg or stdin
- Extract title from first heading or filename
- Call `render_page()`, write to stdout or `-o` file
