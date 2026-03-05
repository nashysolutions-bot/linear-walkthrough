from __future__ import annotations

import argparse
import sys
from pathlib import Path

from renderer import render_page, extract_title


def main():
    parser = argparse.ArgumentParser(
        description="Convert markdown walkthroughs to self-contained HTML",
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to markdown file (reads stdin if omitted)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (writes to stdout if omitted)",
    )
    parser.add_argument(
        "-t", "--title",
        help="Page title (auto-detected from first heading if omitted)",
    )
    parser.add_argument(
        "--serve", action="store_true",
        help="Start interactive server mode",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=7847,
        help="Server port (default: 7847)",
    )
    parser.add_argument(
        "--cwd",
        help="Working directory for claude subprocess (default: input file directory)",
    )
    args = parser.parse_args()

    if args.input:
        input_path = Path(args.input).resolve()
        source = input_path.read_text()
        fallback_title = input_path.stem
    else:
        if sys.stdin.isatty():
            parser.error("No input file and no stdin data. Provide a file or pipe markdown in.")
        source = sys.stdin.read()
        fallback_title = None
        input_path = None

    if args.serve:
        if input_path is None:
            parser.error("--serve requires a file argument (cannot use stdin)")

        from renderer import build_css
        from server import start_server

        title = args.title or extract_title(source) or fallback_title or "Walkthrough"
        cwd = Path(args.cwd) if args.cwd else input_path.parent

        start_server(
            source=source,
            title=title,
            port=args.port,
            cwd=cwd,
            input_path=input_path,
            css=build_css(),
        )
    else:
        html = render_page(source, title=args.title, fallback_title=fallback_title)

        if args.output:
            Path(args.output).write_text(html)
        else:
            sys.stdout.write(html)


if __name__ == "__main__":
    main()
