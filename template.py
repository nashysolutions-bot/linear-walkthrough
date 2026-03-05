from pathlib import Path

from minijinja import Environment, Markup

TEMPLATE_DIR = Path(__file__).parent / "templates"

GITHUB_CSS = """
.markdown-body {
  -ms-text-size-adjust: 100%;
  -webkit-text-size-adjust: 100%;
  margin: 0 auto;
  max-width: 980px;
  padding: 45px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans",
    Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
  font-size: 16px;
  line-height: 1.5;
  word-wrap: break-word;
  color: #1f2328;
}

@media (prefers-color-scheme: dark) {
  .markdown-body { color: #e6edf3; background-color: #0d1117; }
  .markdown-body a { color: #58a6ff; }
  .markdown-body hr { background-color: #30363d; }
  .markdown-body blockquote { border-color: #3b434b; color: #9198a1; }
  .markdown-body h1, .markdown-body h2 { border-color: #30363d; }
  .markdown-body table tr { background-color: #0d1117; border-color: #30363d; }
  .markdown-body table tr:nth-child(2n) { background-color: #161b22; }
  .markdown-body table td, .markdown-body table th { border-color: #30363d; }
  .markdown-body code, .markdown-body pre { background-color: #161b22; }
  .markdown-body .highlight pre, .markdown-body pre { background-color: #161b22; }
}

@media (max-width: 767px) {
  .markdown-body { padding: 15px; }
}

.markdown-body a { color: #0969da; text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }

.markdown-body h1, .markdown-body h2, .markdown-body h3,
.markdown-body h4, .markdown-body h5, .markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}
.markdown-body h1 { font-size: 2em; padding-bottom: 0.3em; border-bottom: 1px solid #d1d9e0; }
.markdown-body h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #d1d9e0; }
.markdown-body h3 { font-size: 1.25em; }
.markdown-body h4 { font-size: 1em; }

.markdown-body p { margin-top: 0; margin-bottom: 16px; }

.markdown-body ul, .markdown-body ol {
  margin-top: 0; margin-bottom: 16px; padding-left: 2em;
}
.markdown-body li + li { margin-top: 0.25em; }

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  white-space: break-spaces;
  background-color: rgba(175, 184, 193, 0.2);
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
    "Liberation Mono", monospace;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  color: #1f2328;
  background-color: #f6f8fa;
  border-radius: 6px;
  position: relative;
}
.markdown-body pre code {
  padding: 0;
  margin: 0;
  font-size: 100%;
  white-space: pre;
  background: transparent;
  border: 0;
}

.markdown-body pre .code-lang {
  position: absolute;
  top: 4px;
  right: 8px;
  font-size: 11px;
  color: #656d76;
  user-select: none;
}

@media (prefers-color-scheme: dark) {
  .markdown-body pre { color: #e6edf3; background-color: #161b22; }
  .markdown-body pre .code-lang { color: #9198a1; }
}

.markdown-body blockquote {
  margin: 0 0 16px;
  padding: 0 1em;
  color: #656d76;
  border-left: 0.25em solid #d1d9e0;
}

.markdown-body hr {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: #d1d9e0;
  border: 0;
}

.markdown-body table {
  border-spacing: 0;
  border-collapse: collapse;
  margin-bottom: 16px;
  display: block;
  width: max-content;
  max-width: 100%;
  overflow: auto;
}
.markdown-body table th, .markdown-body table td {
  padding: 6px 13px;
  border: 1px solid #d1d9e0;
}
.markdown-body table th { font-weight: 600; }
.markdown-body table tr { background-color: #ffffff; border-top: 1px solid #d1d9e0; }
.markdown-body table tr:nth-child(2n) { background-color: #f6f8fa; }

.markdown-body img {
  max-width: 100%;
  box-sizing: border-box;
}

body {
  margin: 0;
  background-color: #ffffff;
}
@media (prefers-color-scheme: dark) {
  body { background-color: #0d1117; }
}
"""


def _load_template(name: str) -> str:
    return (TEMPLATE_DIR / name).read_text()


env = Environment(loader=_load_template)


def render_template(title: str, css: str, content: str) -> str:
    return env.render_template(
        "page.html",
        title=title,
        css=Markup(css),
        content=Markup(content),
    )


def render_interactive_template(title: str, css: str, content: str) -> str:
    return env.render_template(
        "page_interactive.html",
        title=title,
        css=Markup(css),
        content=Markup(content),
    )
