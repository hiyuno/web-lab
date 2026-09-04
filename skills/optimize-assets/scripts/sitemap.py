#!/usr/bin/env python3
"""Phase 1: list the pages of a live site.

Reads /sitemap.xml (following sitemap indexes), then complements it with same-origin links
found on the home page, so pages missing from the sitemap still show up.

Usage:
  sitemap.py https://example.com            # markdown table
  sitemap.py https://example.com --json     # JSON for inventory/pages.json
"""
import argparse, json, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 assets-web-audit"}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def strip_ns(tag):
    return tag.split("}", 1)[-1]


def read_sitemap(url, seen=None):
    seen = seen if seen is not None else set()
    if url in seen:
        return []
    seen.add(url)
    try:
        xml = fetch(url)
        root = ET.fromstring(xml)
    except Exception as e:
        print(f"[warn] sitemap {url}: {e}", file=sys.stderr)
        return []
    urls = []
    kind = strip_ns(root.tag)
    for el in root.iter():
        if strip_ns(el.tag) == "loc" and el.text:
            loc = el.text.strip()
            if kind == "sitemapindex":
                urls += read_sitemap(loc, seen)
            else:
                urls.append(loc)
    return urls


def home_links(site):
    try:
        html = fetch(site)
    except Exception as e:
        print(f"[warn] home {site}: {e}", file=sys.stderr)
        return []
    origin = urllib.parse.urlsplit(site)
    out = []
    for href in re.findall(r'href=["\']([^"\'#?]+)', html):
        full = urllib.parse.urljoin(site, href)
        p = urllib.parse.urlsplit(full)
        if p.netloc != origin.netloc or p.scheme not in ("http", "https"):
            continue
        if re.search(r"\.(png|jpe?g|webp|avif|gif|svg|mp4|webm|pdf|css|js|xml|ico)$", p.path, re.I):
            continue
        out.append(urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, "", "")))
    return out


def norm(url):
    p = urllib.parse.urlsplit(url)
    path = p.path or "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return urllib.parse.urlunsplit((p.scheme, p.netloc.lower(), path, "", ""))


def slug_for(url):
    path = urllib.parse.urlsplit(url).path.strip("/")
    if not path:
        return "home"
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", path.replace("/", "__"))
    return s.strip("-") or "home"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-crawl", action="store_true", help="skip home-page link discovery")
    a = ap.parse_args()

    site = a.site if a.site.startswith("http") else "https://" + a.site
    site = site.rstrip("/") + "/"
    pages = {}
    for u in read_sitemap(urllib.parse.urljoin(site, "sitemap.xml")):
        pages.setdefault(norm(u), set()).add("sitemap")
    if not a.no_crawl:
        for u in home_links(site):
            pages.setdefault(norm(u), set()).add("nav")

    rows = [{"slug": slug_for(u), "url": u, "source": "+".join(sorted(src))}
            for u, src in pages.items()]
    rows.sort(key=lambda r: (r["slug"] != "home", r["url"]))

    if a.json:
        print(json.dumps({"site": site, "pages": rows}, indent=2, ensure_ascii=False))
    else:
        print("| # | slug | url | source |\n|---|---|---|---|")
        for i, r in enumerate(rows, 1):
            print(f"| {i} | {r['slug']} | {r['url']} | {r['source']} |")
        print(f"\n{len(rows)} pages", file=sys.stderr)


if __name__ == "__main__":
    main()
