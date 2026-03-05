from pathlib import Path

from minijinja import Environment, Markup

TEMPLATE_DIR = Path(__file__).parent / "templates"


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
