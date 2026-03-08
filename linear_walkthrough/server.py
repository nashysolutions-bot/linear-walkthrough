from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from linear_walkthrough.renderer import render_markdown, render_page


def _clean_env() -> dict[str, str]:
    """Clone the environment with CLAUDE_CODE vars removed so claude subprocess works from within Claude Code."""
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("CLAUDE_CODE"):
            env.pop(key)
    return env


class WalkthroughHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._respond(200, "text/html", self._build_page())
        elif self.path.startswith("/followups/") and self.path.endswith(".html"):
            filename = Path(self.path).name
            if "/" in filename or "\\" in filename or ".." in filename:
                self._respond(403, "text/plain", "Forbidden")
                return
            filepath = self.server.followups_dir / filename
            if filepath.is_file():
                self._respond(200, "text/html", filepath.read_text())
            else:
                self._respond(404, "text/plain", "Not found")
        else:
            self._respond(404, "text/plain", "Not found")

    def do_POST(self):
        if self.path != "/ask":
            self._respond(404, "text/plain", "Not found")
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        data = json.loads(body)

        selected_text = data.get("selected_text", "")
        prompt = data.get("prompt", "")

        full_prompt = f"{prompt}\n\nContext:\n\n{selected_text}"

        try:
            md_response = self._call_claude(full_prompt)
        except Exception as e:
            self._respond(500, "text/plain", str(e))
            return

        # Write follow-up to a separate file and serve as a static page
        self.server.followup_counter += 1
        n = self.server.followup_counter
        summary = prompt[:80] if len(prompt) > 80 else prompt
        entry = f"# Follow-up: {summary}\n\n> {selected_text[:200]}{'...' if len(selected_text) > 200 else ''}\n\n{md_response}\n"

        md_path = self.server.followups_dir / f"followup-{n}.md"
        html_path = self.server.followups_dir / f"followup-{n}.html"
        md_path.write_text(entry)
        html_path.write_text(render_page(entry, title=f"Follow-up: {summary}"))

        url = f"/followups/followup-{n}.html"
        response = json.dumps({"url": url})
        self._respond(200, "application/json", response)

    def _build_page(self) -> str:
        from linear_walkthrough.template import render_interactive_template

        source = self.server.input_path.read_text()
        content = render_markdown(source)
        return render_interactive_template(
            title=self.server.title,
            css=self.server.css,
            content=content,
        )

    def _call_claude(self, prompt: str) -> str:
        cmd = ["claude", "-p", prompt, "--output-format", "text"]
        if self.server.conversation_started:
            cmd.insert(1, "-c")

        result = subprocess.run(
            cmd,
            cwd=self.server.cwd,
            env=_clean_env(),
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"claude exited with code {result.returncode}: {result.stderr}"
            )

        self.server.conversation_started = True
        return result.stdout

    def _respond(self, status: int, content_type: str, body: str):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, format, *args):
        pass


class WalkthroughServer(HTTPServer):
    input_path: Path
    title: str
    css: str
    cwd: Path
    conversation_started: bool
    pr_context: str
    followup_counter: int
    followups_dir: Path


def _detect_pr_ref(source: str) -> str | None:
    """Extract a PR reference from markdown content.

    Looks for GitHub PR URLs like https://github.com/owner/repo/pull/123
    and returns 'owner/repo#123' for use with gh CLI.
    """
    match = re.search(
        r"https?://github\.com/([^/]+/[^/]+)/pull/(\d+)", source
    )
    if match:
        return f"{match.group(1)}#{match.group(2)}"
    return None


def _fetch_pr_context(pr_ref: str, cwd: Path) -> str:
    """Fetch PR info and diff using gh CLI. Returns context string or empty."""
    # Parse owner/repo#number or just #number
    match = re.match(r"(?:([^#]+)#)?(\d+)$", pr_ref)
    if not match:
        return ""

    repo_part = match.group(1)  # owner/repo or None
    pr_number = match.group(2)

    base_cmd = ["gh", "pr"]
    repo_args = ["-R", repo_part] if repo_part else []

    parts = []
    try:
        # Fetch PR metadata
        view_result = subprocess.run(
            [*base_cmd, "view", pr_number, *repo_args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if view_result.returncode == 0:
            parts.append(f"## PR Info\n\n{view_result.stdout}")

        # Fetch PR diff
        diff_result = subprocess.run(
            [*base_cmd, "diff", pr_number, *repo_args],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if diff_result.returncode == 0:
            diff = diff_result.stdout
            # Truncate very large diffs
            if len(diff) > 50000:
                diff = diff[:50000] + "\n... (diff truncated)"
            parts.append(f"## PR Diff\n\n```diff\n{diff}\n```")
    except Exception:
        pass

    return "\n\n".join(parts)


def start_server(
    source: str,
    title: str,
    port: int,
    cwd: Path,
    input_path: Path,
    css: str,
    pr: str | None = None,
):
    try:
        server = WalkthroughServer(("127.0.0.1", port), WalkthroughHandler)
    except OSError as e:
        if e.errno == 98 or e.errno == 48:  # EADDRINUSE: Linux=98, macOS=48
            print(f"Error: port {port} is already in use. Try a different port with -p.")
            raise SystemExit(1) from None
        raise
    server.input_path = input_path
    server.title = title
    server.css = css
    server.cwd = cwd
    server.conversation_started = False
    server.pr_context = ""
    server.followup_counter = 0
    server.followups_dir = input_path.parent / "followups"
    server.followups_dir.mkdir(exist_ok=True)

    # Resolve PR context
    pr_ref = pr or _detect_pr_ref(source)
    if pr_ref:
        print(f"Fetching PR context for {pr_ref}...")
        server.pr_context = _fetch_pr_context(pr_ref, cwd)
        if server.pr_context:
            print("PR context loaded.")
        else:
            print("Could not fetch PR context (is `gh` installed and authenticated?).")

    # Seed claude with the original walkthrough context
    def seed_context():
        try:
            seed_prompt = "You are helping explain a code walkthrough. Respond in GitHub-flavored markdown syntax. Prefer using Mermaid.js diagrams (```mermaid fenced blocks) when visualizations would help. Here is the full walkthrough for context. Do not respond with anything other than 'OK'."
            seed_prompt += f"\n\n{source}"
            if server.pr_context:
                seed_prompt += f"\n\nHere is the pull request information and diff for additional context:\n\n{server.pr_context}"

            subprocess.run(
                [
                    "claude",
                    "-p",
                    seed_prompt,
                    "--output-format",
                    "text",
                ],
                cwd=cwd,
                env=_clean_env(),
                capture_output=True,
                text=True,
                timeout=300,
            )
            server.conversation_started = True
        except Exception:
            pass

    threading.Thread(target=seed_context, daemon=True).start()

    url = f"http://127.0.0.1:{port}"
    print(f"Serving walkthrough at {url}")
    webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()
