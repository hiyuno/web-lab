#!/usr/bin/env python3
"""Phase 2, step 2.1: inventory of an existing site, one row per URL.

Input: the JSON from optimize-assets/scripts/sitemap.py ({"pages": [{"url": ...}]}) or a text
file with one URL per line. Visits every URL and extracts HTTP status, title, meta description,
H1, canonical, meta robots, word count, internal links and forms.

Usage:
  inventory.py pages.json            # CSV to stdout
  inventory.py urls.txt --md         # Markdown table with an empty "decision" column
  inventory.py pages.json --json     # JSON
"""
import argparse, csv, html, json, re, sys, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser

UA = {"User-Agent": "Mozilla/5.0 web-lab-inventory"}


class Page(HTMLParser):
    def __init__(self, base):
        super().__init__(convert_charrefs=True)
        self.base = base
        self.origin = urllib.parse.urlsplit(base).netloc.lower()
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.robots = ""
        self.h1 = []
        self.internal = set()
        self.external = 0
        self.forms = 0
        self.inputs = []
        self.words = 0
        self._in = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript", "template"):
            self._skip += 1
        self._in.append(tag)
        if tag == "meta":
            name = (a.get("name") or a.get("property") or "").lower()
            if name == "description":
                self.description = (a.get("content") or "").strip()
            elif name == "robots":
                self.robots = (a.get("content") or "").strip()
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = urllib.parse.urljoin(self.base, a.get("href") or "")
        elif tag == "a" and a.get("href"):
            href = a["href"].strip()
            if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                return
            full = urllib.parse.urljoin(self.base, href)
            p = urllib.parse.urlsplit(full)
            if p.scheme not in ("http", "https"):
                return
            if p.netloc.lower() == self.origin:
                self.internal.add(urllib.parse.urlunsplit((p.scheme, p.netloc, p.path or "/", "", "")))
            else:
                self.external += 1
        elif tag == "form":
            self.forms += 1
        elif tag in ("input", "textarea", "select"):
            t = (a.get("type") or tag).lower()
            if t not in ("hidden", "submit", "button", "reset", "image"):
                self.inputs.append(a.get("name") or a.get("id") or t)

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "template") and self._skip:
            self._skip -= 1
        while self._in and self._in.pop() != tag:
            pass

    def handle_data(self, data):
        if self._skip:
            return
        if "title" in self._in and not self.title:
            self.title = data.strip()
        elif "h1" in self._in and data.strip():
            self.h1.append(re.sub(r"\s+", " ", data.strip()))
        if data.strip():
            self.words += len(data.split())


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            return r.status, r.geturl(), r.headers.get("content-type", ""), body
    except urllib.error.HTTPError as e:
        return e.code, url, "", b""
    except Exception as e:
        return 0, url, str(e), b""


def inspect(url):
    status, final, ctype, body = fetch(url)
    row = {"url": url, "status": status, "final_url": final if final != url else "",
           "title": "", "description": "", "h1": "", "canonical": "", "robots": "",
           "words": 0, "internal_links": 0, "external_links": 0, "forms": 0, "inputs": ""}
    if status != 200 or b"<" not in body:
        if ctype and status == 0:
            row["title"] = f"[error] {ctype}"
        return row, set()
    if "html" not in ctype.lower() and not body.lstrip()[:15].lower().startswith((b"<!doctype", b"<html")):
        row["title"] = f"[{ctype.split(';')[0]}]"
        return row, set()
    p = Page(final or url)
    try:
        p.feed(body.decode("utf-8", "replace"))
    except Exception:
        pass
    row.update(title=p.title, description=p.description, h1=" | ".join(p.h1),
               canonical="" if p.canonical.rstrip("/") == (final or url).rstrip("/") else p.canonical,
               robots=p.robots, words=p.words, internal_links=len(p.internal),
               external_links=p.external, forms=p.forms, inputs=", ".join(p.inputs))
    return row, p.internal


def load_urls(path):
    text = open(path, encoding="utf-8").read()
    if text.lstrip().startswith("{"):
        data = json.loads(text)
        return [p["url"] for p in data.get("pages", [])]
    return [l.strip() for l in text.splitlines() if l.strip() and not l.startswith("#")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="pages.json from sitemap.py or a file with one URL per line")
    ap.add_argument("--md", action="store_true", help="Markdown table with a decision column")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--discover", action="store_true",
                    help="add unlisted internal links it finds to the inventory")
    a = ap.parse_args()

    urls = load_urls(a.source)
    seen, queue, rows = set(), list(urls), []
    while queue:
        u = queue.pop(0)
        key = u.rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        print(f"[{len(rows)+1}] {u}", file=sys.stderr)
        row, internal = inspect(u)
        rows.append(row)
        if a.discover:
            for link in sorted(internal):
                if link.rstrip("/") not in seen and not re.search(r"\.(pdf|jpe?g|png|gif|svg|webp|mp4|zip|css|js)$", link, re.I):
                    queue.append(link)

    cols = ["url", "status", "final_url", "title", "description", "h1", "canonical", "robots",
            "words", "internal_links", "external_links", "forms", "inputs"]
    if a.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    elif a.md:
        def cell(v):
            return html.escape(str(v)).replace("|", "\\|")[:80]
        print("| url | status | title | meta description | h1 | canonical | robots | words | internal links | forms | fields | traffic | rankings | decision |")
        print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['url']} | {r['status']} | {cell(r['title'])} | {cell(r['description'])} | {cell(r['h1'])} | "
                  f"{cell(r['canonical'])} | {cell(r['robots'])} | {r['words']} | {r['internal_links']} | "
                  f"{r['forms']} | {cell(r['inputs'])} |  |  |  |")
        print(f"\n{len(rows)} URLs", file=sys.stderr)
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in cols})


if __name__ == "__main__":
    main()
