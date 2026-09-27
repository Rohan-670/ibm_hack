#!/usr/bin/env python3
"""
RepoPilot Web Application -- zero-dependency (stdlib only, no Flask, no pip).

Run:
    python web_app.py          # opens http://localhost:8000
    python web_app.py --port 9000 --no-browser
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import mimetypes
import os
import re
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

REPO_ROOT     = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR    = os.path.join(REPO_ROOT, "web", "static")
TEMPLATES_DIR = os.path.join(REPO_ROOT, "web", "templates")

# ── Markdown -> HTML ──────────────────────────────────────────────────────────

def md_to_html(text):
    lines = text.split("\n")
    html_lines = []
    in_code = in_table = in_ul = False
    for line in lines:
        if line.startswith("```"):
            if in_ul:   html_lines.append("</ul>");         in_ul   = False
            if in_table:html_lines.append("</tbody></table>"); in_table = False
            if in_code: html_lines.append("</code></pre>"); in_code = False
            else:
                lang = line[3:].strip()
                cls  = f' class="language-{lang}"' if lang else ""
                html_lines.append(f'<pre><code{cls}>'); in_code = True
            continue
        if in_code:
            html_lines.append(_esc(line)); continue
        if line.startswith("|"):
            if in_ul: html_lines.append("</ul>"); in_ul = False
            cells = [c.strip() for c in line.strip("|").split("|")]
            if all(re.match(r"^[-: ]+$", c) for c in cells): continue
            if not in_table:
                html_lines.append('<table class="md-table"><tbody>'); in_table = True
            tag = "td"
            row = "".join(f"<{tag}>{_inline(c)}</{tag}>" for c in cells)
            html_lines.append(f"<tr>{row}</tr>")
            continue
        if in_table: html_lines.append("</tbody></table>"); in_table = False
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            if in_ul: html_lines.append("</ul>"); in_ul = False
            n = len(m.group(1))
            html_lines.append(f"<h{n}>{_inline(m.group(2))}</h{n}>"); continue
        m = re.match(r"^\s*[-*]\s+(.*)", line)
        if m:
            if not in_ul: html_lines.append("<ul>"); in_ul = True
            html_lines.append(f"<li>{_inline(m.group(1))}</li>"); continue
        m = re.match(r"^\s*\d+\.\s+(.*)", line)
        if m:
            if not in_ul: html_lines.append("<ul>"); in_ul = True
            html_lines.append(f"<li>{_inline(m.group(1))}</li>"); continue
        if in_ul and line.strip() == "":
            html_lines.append("</ul>"); in_ul = False
        if line.strip() == "":
            html_lines.append("<br>"); continue
        html_lines.append(f"<p>{_inline(line)}</p>")
    if in_ul:    html_lines.append("</ul>")
    if in_table: html_lines.append("</tbody></table>")
    if in_code:  html_lines.append("</code></pre>")
    return "\n".join(html_lines)


def _esc(t):
    return t.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


def _inline(text):
    text = text.replace("\U0001f6ab", '<span class="badge blocker">BLOCKER</span>')
    text = text.replace("\u26a0\ufe0f", '<span class="badge warning">WARNING</span>')
    text = text.replace("\u2139\ufe0f", '<span class="badge info">INFO</span>')
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*",     r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`",     r"<code>\1</code>", text)
    text = re.sub(r"_(.+?)_",       r"<em>\1</em>", text)
    return text

# ── Request handler ───────────────────────────────────────────────────────────

class RepoPilotHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args): pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/") or "/"
        qs     = parse_qs(parsed.query)

        if path.startswith("/static/"):
            return self._serve_static(path[8:])
        if path == "/stream/pr":
            return self._stream_run(["pr",
                qs.get("base",   ["master"])[0],
                qs.get("branch", ["feature/bulk-update"])[0]])
        if path == "/stream/onboard":
            return self._stream_run(["onboard"])
        if path == "/api/report/pr":
            return self._api_report("release-report.md")
        if path == "/api/report/onboard":
            return self._api_report("onboarding-brief.md")
        if path == "/api/agents":
            return self._send_json(_parse_agent_findings())

        pages = {
            "/":               self._page_dashboard,
            "/pr":             self._page_pr,
            "/onboarding":     self._page_onboarding,
            "/agents":         self._page_agents,
            "/report/pr":      self._page_report_pr,
            "/report/onboard": self._page_report_onboard,
        }
        handler = pages.get(path)
        if handler: handler()
        else: self._send(404, "text/plain", b"Not found")

    # ── Pages ─────────────────────────────────────────────────────────────────

    def _page_dashboard(self):
        score_raw = _last_score()
        try:   score_int = int(score_raw)
        except: score_int = -1
        score_class = ("ok" if score_int >= 80 else "warn" if score_int >= 50 else "bad") if score_int >= 0 else ""
        self._send_html(_render("index.html", {
            "branch_pills": _branch_pills(),
            "log":          _git_log(),
            "score":        score_raw,
            "score_class":  score_class,
        }))

    def _page_pr(self):
        self._send_html(_render("pr_analysis.html", {}))

    def _page_onboarding(self):
        self._send_html(_render("onboarding.html", {}))

    def _page_agents(self):
        self._send_html(_render("agents.html", {
            "agent_data_json": json.dumps(_parse_agent_findings()),
        }))

    def _page_report_pr(self):
        md = _read_file(os.path.join(REPO_ROOT, "release-report.md"))
        self._send_html(_render("report.html", {
            "title":   "Release Readiness Report",
            "content": md_to_html(md) if md else "<p>No report yet — run PR Analysis first.</p>",
        }))

    def _page_report_onboard(self):
        md = _read_file(os.path.join(REPO_ROOT, "onboarding-brief.md"))
        self._send_html(_render("report.html", {
            "title":   "Onboarding Brief",
            "content": md_to_html(md) if md else "<p>No brief yet — run Onboarding first.</p>",
        }))

    # ── SSE streaming ─────────────────────────────────────────────────────────

    def _stream_run(self, mode_args):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        mode = mode_args[0]
        cmd  = [sys.executable, "-m", "orchestrator.run", f"--mode={mode}"]
        if mode == "pr" and len(mode_args) == 3:
            cmd += [f"--base={mode_args[1]}", f"--branch={mode_args[2]}"]

        def _send_event(data):
            for line in data.splitlines():
                self.wfile.write(f"data: {line}\n".encode())
            self.wfile.write(b"\n")
            self.wfile.flush()

        try:
            proc = subprocess.Popen(
                cmd, cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            for line in proc.stdout:
                _send_event(line.rstrip("\n"))
            proc.wait()
            _send_event(f"__DONE__:{proc.returncode}")
        except Exception as exc:
            _send_event(f"__ERROR__:{exc}")

    # ── API ───────────────────────────────────────────────────────────────────

    def _api_report(self, filename):
        md = _read_file(os.path.join(REPO_ROOT, filename))
        self._send_json({"content": md or "", "html": md_to_html(md) if md else ""})

    # ── Static & helpers ──────────────────────────────────────────────────────

    def _serve_static(self, rel_path):
        full = os.path.join(STATIC_DIR, rel_path)
        if not os.path.isfile(full):
            self._send(404, "text/plain", b"Not found"); return
        mime, _ = mimetypes.guess_type(full)
        with open(full, "rb") as fh:
            self._send(200, mime or "application/octet-stream", fh.read())

    def _send(self, code, ctype, body):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html):
        self._send(200, "text/html; charset=utf-8", html.encode("utf-8"))

    def _send_json(self, data):
        body = json.dumps(data).encode()
        self._send(200, "application/json", body)

# ── Template renderer ─────────────────────────────────────────────────────────

def _render(name, ctx):
    path = os.path.join(TEMPLATES_DIR, name)
    with open(path, encoding="utf-8") as fh:
        t = fh.read()
    for k, v in ctx.items():
        t = t.replace("{{" + k + "}}", str(v) if not isinstance(v, str) else v)
    return t

# ── Helpers ───────────────────────────────────────────────────────────────────

def _read_file(path):
    if not os.path.isfile(path): return ""
    with open(path, encoding="utf-8", errors="replace") as fh: return fh.read()

def _git_log():
    try:
        return subprocess.check_output(
            ["git", "-C", REPO_ROOT, "log", "--oneline", "--all"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except: return ""

def _branch_pills():
    try:
        out = subprocess.check_output(
            ["git", "-C", REPO_ROOT, "branch", "-a"],
            text=True, stderr=subprocess.DEVNULL)
        pills = []
        for line in out.strip().splitlines():
            active = line.startswith("*")
            name   = line.strip().lstrip("* ")
            cls    = "branch-pill active-branch" if active else "branch-pill"
            pills.append(f'<span class="{cls}">{name}</span>')
        return "\n".join(pills)
    except: return ""

def _last_score():
    md = _read_file(os.path.join(REPO_ROOT, "release-report.md"))
    m  = re.search(r"## Score:\s*(\d+)\s*/\s*100", md)
    return m.group(1) if m else "0"

def _parse_agent_findings():
    AGENTS = [
        {"id":"diff-analyst",    "name":"diff-analyst",    "mode":"pr",      "icon":"search",    "color":"var(--accent)",
         "desc":"Detects breaking API changes: field renames, new env vars, new routes.",
         "tasks":["Scan git diff for dict/JSON key renames","Flag new os.environ/os.getenv calls","Detect new route decorators","Annotate each finding with file, line, and churn score"],
         "source":"orchestrator/agents/diff_analyst.py","categories":["breaking_change"]},
        {"id":"test-gap-agent",  "name":"test-gap-agent",  "mode":"pr",      "icon":"flask",     "color":"var(--red)",
         "desc":"Finds new endpoints with zero test coverage. Auto-writes unittest stubs.",
         "tasks":["Parse diff for new route decorators","Search existing tests for each new route path","Flag untested routes as blockers","Auto-generate a unittest stub in suggested-tests/"],
         "source":"orchestrator/agents/test_gap.py","categories":["test_gap"]},
        {"id":"doc-sync-agent",  "name":"doc-sync-agent",  "mode":"pr",      "icon":"file-text", "color":"var(--yellow)",
         "desc":"Checks README endpoint table, response contract examples, and CHANGELOG entries.",
         "tasks":["Detect new routes not in README.md","Find field renames where README shows old name","Flag PRs that change API behavior without touching CHANGELOG.md"],
         "source":"orchestrator/agents/doc_sync.py","categories":["doc_drift"]},
        {"id":"compliance-agent","name":"compliance-agent","mode":"pr",      "icon":"shield",    "color":"var(--green)",
         "desc":"Validates env var docs, hardcoded secrets scan, setup/test command docs.",
         "tasks":["Cross-check os.environ reads against .env.example","Scan source for secret literal patterns","Check README has install and test commands","Write setup-checklist.json for onboarding-agent to reuse"],
         "source":"orchestrator/agents/compliance.py","categories":["compliance"]},
        {"id":"onboarding-agent","name":"onboarding-agent","mode":"onboard", "icon":"book-open", "color":"var(--accent2)",
         "desc":"Generates onboarding brief: architecture, glossary, checklist, safest tasks, quiz.",
         "tasks":["Extract architecture from AGENTS.md","Build where-things-live table","Define domain glossary","Reuse setup-checklist.json (no recompute)","Rank files by git churn for safest first tasks","Embed self-check quiz"],
         "source":"orchestrator/agents/onboarding.py","categories":["onboarding"]},
    ]
    md = _read_file(os.path.join(REPO_ROOT, "release-report.md"))
    findings_by_cat = {}
    if md:
        for m in re.finditer(
            r"- \*\*\[(\w+)\]\*\*\s+`([^`]*)`\s+\u2014\s+([^\n]+)(?:\n\s+-\s+Fix:\s+([^\n]+))?", md):
            cat  = m.group(1)
            item = {"loc": m.group(2), "description": m.group(3).strip(), "fix": (m.group(4) or "").strip()}
            findings_by_cat.setdefault(cat, []).append(item)
    timings = {}
    for m in re.finditer(r"`([^`]+)`:\s+started \+[\d.]+s.*?elapsed ([\d.]+)s", md):
        timings[m.group(1)] = float(m.group(2))
    score_m = re.search(r"## Score:\s*(\d+)\s*/\s*100", md)
    score   = int(score_m.group(1)) if score_m else None
    for agent in AGENTS:
        agent_findings = []
        for cat in agent["categories"]:
            agent_findings.extend(findings_by_cat.get(cat, []))
        agent["finding_count"] = len(agent_findings)
        agent["findings"]      = agent_findings
        agent["elapsed"]       = timings.get(agent["id"])
        agent["last_score"]    = score
    return {"agents": AGENTS, "score": score, "has_report": bool(md)}

# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RepoPilot Web UI")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    os.makedirs(STATIC_DIR,    exist_ok=True)
    os.makedirs(TEMPLATES_DIR, exist_ok=True)
    server = ThreadingHTTPServer(("", args.port), RepoPilotHandler)
    server.daemon_threads = True
    url = f"http://localhost:{args.port}"
    print(f"\n  RepoPilot Web UI  ->  {url}")
    print(f"  Press Ctrl+C to stop.\n")
    sys.stdout.flush()
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
