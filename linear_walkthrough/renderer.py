from __future__ import annotations

import re

from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer

from linear_walkthrough.template import render_template


def _highlight_code(code: str, lang: str) -> str:
    """Syntax-highlight a code block using Pygments."""
    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = guess_lexer(code)
    except Exception:
        lexer = TextLexer()

    formatter = HtmlFormatter(nowrap=True, style="default")
    highlighted = highlight(code, lexer, formatter)

    lang_label = f'<span class="code-lang">{lang}</span>' if lang else ""
    return f'<pre>{lang_label}<code class="highlight">{highlighted}</code></pre>'


def _sanitise_mermaid(code: str) -> str:
    """Escape characters that break Mermaid's client-side parser.

    Angle brackets in node labels (e.g. ``Something<Baton<Intent>>``) are
    interpreted as HTML tags by the browser before Mermaid sees them.
    HTML-escaping them keeps the diagram source intact for the parser.
    """
    code = code.replace("&", "&amp;")
    code = code.replace("<", "&lt;")
    code = code.replace(">", "&gt;")
    return code


def _render_mermaid(code: str) -> str:
    """Wrap mermaid code in a div for client-side rendering."""
    return f'<pre class="mermaid">{_sanitise_mermaid(code)}</pre>'


def _make_renderer() -> MarkdownIt:
    """Create a configured markdown-it instance."""
    md = MarkdownIt("gfm-like").disable("linkify")
    tasklists_plugin(md)

    # Override fence rendering for syntax highlighting + mermaid
    def fence(_self, tokens, idx, options, env):
        token = tokens[idx]
        lang = token.info.strip().split()[0] if token.info else ""
        code = token.content

        if lang == "mermaid":
            return _render_mermaid(code)
        return _highlight_code(code, lang)

    md.add_render_rule("fence", fence)
    return md


_md = _make_renderer()


def render_markdown(source: str) -> str:
    """Convert GFM markdown to an HTML fragment."""
    return _md.render(source)


def extract_title(source: str) -> str | None:
    """Extract the first H1 heading from markdown source."""
    match = re.search(r"^#\s+(.+)$", source, re.MULTILINE)
    return match.group(1).strip() if match else None


def render_page(
    source: str,
    title: str | None = None,
    fallback_title: str | None = None,
) -> str:
    """Convert markdown to a self-contained HTML page."""
    if title is None:
        title = extract_title(source) or fallback_title or "Walkthrough"

    content = render_markdown(source)
    css = build_css()
    return render_template(title=title, css=css, content=content)


def build_css() -> str:
    """Build the Pygments syntax highlighting CSS (light/dark)."""
    light_fmt = HtmlFormatter(style="default")
    dark_fmt = HtmlFormatter(style="github-dark")
    light_css = light_fmt.get_style_defs("code.highlight")
    dark_css = dark_fmt.get_style_defs("code.highlight")

    return light_css + "\n@media (prefers-color-scheme: dark) {\n" + dark_css + "\n}\n"
