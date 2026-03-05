from __future__ import annotations

import json
import subprocess
import threading
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from renderer import render_markdown


class WalkthroughHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self._respond(200, "text/html", self._build_page())
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

        # Append to the original markdown file
        summary = prompt[:80] if len(prompt) > 80 else prompt
        entry = f"\n---\n\n## Follow-up: {summary}\n\n> {selected_text[:200]}{'...' if len(selected_text) > 200 else ''}\n\n{md_response}\n"
        with open(self.server.input_path, "a") as f:
            f.write(entry)

        # Return rendered HTML fragment of just the response
        html_fragment = render_markdown(entry)
        response = json.dumps({"html": html_fragment})
        self._respond(200, "application/json", response)

    def _build_page(self) -> str:
        from template import render_interactive_template

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
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise RuntimeError(f"claude exited with code {result.returncode}: {result.stderr}")

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


def start_server(
    source: str,
    title: str,
    port: int,
    cwd: Path,
    input_path: Path,
    css: str,
):
    server = WalkthroughServer(("127.0.0.1", port), WalkthroughHandler)
    server.input_path = input_path
    server.title = title
    server.css = css
    server.cwd = cwd
    server.conversation_started = False

    # Seed claude with the original walkthrough context
    def seed_context():
        try:
            subprocess.run(
                ["claude", "-p", f"You are helping explain a code walkthrough. Here is the full walkthrough for context. Do not respond with anything other than 'OK'.\n\n{source}", "--output-format", "text"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=60,
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
