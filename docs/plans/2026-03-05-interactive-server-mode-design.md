# Interactive Server Mode Design

## Goal

Add a `--serve` mode that serves the rendered walkthrough as an interactive page. Users can highlight text, ask follow-up questions, and get responses from Claude — all appended to the page and saved locally as markdown.

## Architecture

Three components:

1. **Python server** (`server.py`) — stdlib `http.server`. Serves rendered HTML at `/`, handles `POST /ask` for follow-up questions. Calls `claude -c -p` via subprocess.
2. **Interactive HTML template** (`templates/page_interactive.html`) — extends static template with vanilla JS for text selection, prompt UI, and dynamic content appending.
3. **Followups file** — single `<input>_followups.md` that grows as questions are asked.

## CLI Interface

```bash
uv run python main.py input.md --serve                      # serve on :7847, auto-open
uv run python main.py input.md --serve -p 9000              # custom port
uv run python main.py input.md --serve --cwd /path/to/repo  # explicit cwd for claude
```

- `--serve` starts the interactive server instead of writing static HTML
- `-p` / `--port` sets the port (default: `7847`)
- `--cwd` sets the working directory for `claude` subprocess calls (default: parent directory of input markdown file)
- Auto-opens browser via `webbrowser.open()` after server starts

## Data Flow

```
User highlights text -> popup appears ("Explain more" / custom prompt)
  -> POST /ask { selected_text, prompt }
  -> server builds full prompt
  -> server runs: claude -c -p "<prompt>" (in --cwd directory)
  -> claude returns markdown
  -> server renders markdown -> HTML fragment via render_markdown()
  -> server appends markdown to followups file
  -> returns { html: "<fragment>" } as JSON
  -> JS appends fragment below existing content with <hr> separator
```

## Server Implementation (`server.py`)

### Routes

- `GET /` — serves the rendered interactive HTML page
- `POST /ask` — accepts JSON `{ selected_text, prompt }`, returns `{ html }` JSON

### First-run Context

Before starting the server, run an initial `claude -p` with the original walkthrough markdown so Claude has full context. Subsequent follow-ups use `claude -c -p` to continue the conversation.

The `claude` process runs with `cwd` set to `--cwd` or the directory containing the input markdown file. This gives Claude access to the project files for context.

### Prompts

**"Explain more" default prompt:**
```
Explain the following in more detail. Be concise. Respond in GitHub-flavored markdown format.

<selected_text>
```

**Custom prompt:**
```
<user_prompt>

Context:

<selected_text>
```

Both include the instruction to respond concisely in GFM.

### Followups File

- Saved as `<input_stem>_followups.md` alongside the input file
- Each follow-up appended with format:

```markdown
---

## Follow-up: <prompt summary>

<claude response>
```

## Interactive UI (Vanilla JS)

### Text Selection Popup

- Floating `<div>` shown on `mouseup` when text is selected within `.markdown-body`
- Positioned near selection end using `Range.getBoundingClientRect()`
- Two buttons: "Explain more" (immediate send) and "Ask..." (shows text input)
- Hidden on click-away or Escape
- Disabled while a request is in-flight

### Loading State

- Spinner + "Asking Claude..." appended at page bottom
- Auto-scroll to loading indicator
- Popup buttons disabled to prevent duplicate requests

### Response Rendering

- `<hr>` separator inserted before each response
- Server-rendered HTML fragment appended to `.markdown-body`
- `mermaid.run()` called on new content to render any diagrams
- Page scrolls to new section

### No Dependencies

- No frameworks, no build step
- Just DOM manipulation, `fetch()`, and CSS
- All JS inline in the template

## File Structure

```
server.py                        - HTTP server with GET / and POST /ask
templates/
  page.html                      - Static output template (unchanged)
  page_interactive.html          - Interactive template with selection JS
```

## Module Changes

- `main.py` — add `--serve`, `--port`, `--cwd` arguments. When `--serve`, import and start server.
- `renderer.py` — no changes. `render_markdown()` reused for follow-up rendering.
- `template.py` — add `render_interactive_template()` that uses `page_interactive.html`.
- `server.py` — new file. HTTP handler, claude subprocess management, followups file I/O.
