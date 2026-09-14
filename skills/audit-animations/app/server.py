#!/usr/bin/env python3
"""Local checklist app: shows the audit-animations report.json findings, grouped into the three
categories (composited, runtime, safari-risk), and lets you check them off as you fix them.

Unlike audit-seo's checklist app, there is NO re-check capability here at all: every finding in
this skill needs a rendered page plus a live browser trace (Phase 3's collect_animations.js or
Phase 4's probe_runtime.js), and this static Python server cannot open a browser. Re-checking a
finding means re-running that phase of the skill, not clicking a button here — the UI says so
instead of faking an action.

State lives in <audit>/checklist.json (id -> "open"|"resolved"), separate from report.json so
re-running the audit never wipes progress. Same State.save_status()/load() mechanism as
audit-seo/app/server.py — copied rather than reinvented.

Usage: server.py --audit animation-audit --port 8773
"""
import argparse, json, os, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(HERE, "static")


class State:
    def __init__(self, audit):
        self.audit = os.path.abspath(audit)
        self.checklist_path = os.path.join(self.audit, "checklist.json")
        self.load()

    def load(self):
        with open(os.path.join(self.audit, "report.json")) as f:
            self.report = json.load(f)
        try:
            with open(self.checklist_path) as f:
                self.status = json.load(f)
        except Exception:
            self.status = {}

    def save_status(self):
        tmp = self.checklist_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.status, f, indent=1)
        os.replace(tmp, self.checklist_path)

    def snapshot(self):
        findings = []
        for f in self.report["findings"]:
            f = dict(f)
            f["status"] = self.status.get(f["id"], f.get("status", "open"))
            findings.append(f)
        return {"site": self.report["site"], "findings": findings}

    def set_status(self, fid, status):
        if status not in ("open", "resolved"):
            raise ValueError("bad status")
        self.status[fid] = status
        self.save_status()


class Handler(BaseHTTPRequestHandler):
    state: State = None

    def log_message(self, *a):
        pass

    def _send(self, code, body):
        body = json.dumps(body).encode() if isinstance(body, (dict, list)) else body
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path):
        if not os.path.isfile(path):
            return self._send(404, {"error": "not found"})
        ctype = "text/html" if path.endswith(".html") else (
            "text/css" if path.endswith(".css") else "application/javascript")
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlsplit(self.path).path
        if path == "/":
            return self._file(os.path.join(STATIC, "index.html"))
        if path in ("/app.js", "/app.css"):
            return self._file(os.path.join(STATIC, path[1:]))
        if path == "/api/findings":
            return self._send(200, self.state.snapshot())
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(n) or b"{}")
        except ValueError:
            return self._send(400, {"error": "bad json"})
        S = self.state
        if self.path == "/api/status":
            try:
                S.set_status(body["id"], body["status"])
                return self._send(200, {"ok": True})
            except (ValueError, KeyError) as e:
                return self._send(400, {"error": str(e)})
        return self._send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default="animation-audit")
    ap.add_argument("--port", type=int, default=8773)
    a = ap.parse_args()
    Handler.state = State(a.audit)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"audit-animations checklist: http://localhost:{a.port} "
          f"({len(Handler.state.report['findings'])} findings)", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
