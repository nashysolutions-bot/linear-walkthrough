from __future__ import annotations

import argparse
import sys
from pathlib import Path

from renderer import render_page


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
    args = parser.parse_args()

    if args.input:
        source = Path(args.input).read_text()
        fallback_title = Path(args.input).stem
    else:
        if sys.stdin.isatty():
            parser.error("No input file and no stdin data. Provide a file or pipe markdown in.")
        source = sys.stdin.read()
        fallback_title = None

    html = render_page(source, title=args.title, fallback_title=fallback_title)

    if args.output:
        Path(args.output).write_text(html)
    else:
        sys.stdout.write(html)


if __name__ == "__main__":
    main()
