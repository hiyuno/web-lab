#!/usr/bin/env python3
"""Phase 3, step 3.0: generates the content matrix from the signed phase 2 sitemap.

Reads the "## Pages" table in docs/02-structure/sitemap.md (columns: URL, Intent, Template,
Depth, Primary keyword, Stories, Data requested, Priority) and writes matrix.md with one row per
page. With --briefs it also creates an empty brief per page in <out>/briefs/<slug>.md from
references/page-brief.md.

Usage:
  content_matrix.py docs/02-structure/sitemap.md                     # matrix to stdout
  content_matrix.py docs/02-structure/sitemap.md --briefs docs/03-content
"""
import argparse, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "references", "page-brief.md")


def slug_for(url):
    path = url.strip().strip("/")
    if not path or path == "404":
        return "home" if not path else "404"
    return re.sub(r"[^a-z0-9._-]+", "-", path.lower().replace("/", "__")).strip("-") or "home"


def parse_pages(md):
    m = re.search(r"^## Pages\s*$(.*?)(?=^## |\Z)", md, re.S | re.M)
    if not m:
        sys.exit("Could not find the '## Pages' section in the sitemap.")
    rows = []
    for line in m.group(1).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set(cells[0]) <= set("-: ") or cells[0].upper() == "URL":
            continue
        while len(cells) < 8:
            cells.append("")
        url, intent, template, depth, keyword, stories, data, prio = cells[:8]
        rows.append(dict(url=url, intent=intent, template=template, depth=depth,
                         keyword=keyword, stories=stories, data=data, prio=prio, slug=slug_for(url)))
    if not rows:
        sys.exit("The '## Pages' table has no rows.")
    return rows


def matrix_md(rows, project):
    out = [f"# Content matrix · {project}", "",
           f"Date: {date.today().isoformat()} · Author: Rosenfeld · Generated from docs/02-structure/sitemap.md",
           "", "Statuses: `brief` → `draft` → `review` → `approved`. One named final approver; at most two rounds.", "",
           "| URL | Template | Primary keyword | Intent | Brief | Status | Writes | Due | Round | Approver | Notes |",
           "|-----|----------|-----------------|--------|-------|--------|--------|-----|-------|----------|-------|"]
    for r in rows:
        out.append(f"| {r['url']} | {r['template']} | {r['keyword']} | {r['intent']} | "
                   f"[brief](briefs/{r['slug']}.md) | brief |  |  | 0/2 |  |  |")
    out += ["", "## Summary", "", f"- Pages: {len(rows)}", "- Approved: 0", "- Past due: 0", ""]
    return "\n".join(out)


def brief_md(r, template_text):
    t = template_text
    t = t.replace("[URL]", r["url"]).replace("[template]", r["template"] or "[template]")
    t = t.replace("[primary keyword]", r["keyword"] or "[primary keyword]")
    t = t.replace("[one-sentence intent]", r["intent"] or "[one-sentence intent]")
    t = t.replace("[S-xx]", r["stories"] or "[S-xx]").replace("[data requested]", r["data"] or "none")
    t = t.replace("[yyyy-mm-dd]", date.today().isoformat(), 1)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sitemap")
    ap.add_argument("--briefs", metavar="OUT_DIR", help="write matrix.md and briefs/<slug>.md into OUT_DIR")
    ap.add_argument("--project", default="[project]")
    a = ap.parse_args()

    rows = parse_pages(open(a.sitemap, encoding="utf-8").read())
    md = matrix_md(rows, a.project)
    if not a.briefs:
        print(md)
        return
    os.makedirs(os.path.join(a.briefs, "briefs"), exist_ok=True)
    mpath = os.path.join(a.briefs, "matrix.md")
    if os.path.exists(mpath):
        sys.exit(f"{mpath} already exists; not overwriting. Delete it or edit it by hand.")
    open(mpath, "w", encoding="utf-8").write(md)
    tpl = open(TEMPLATE, encoding="utf-8").read()
    created = 0
    for r in rows:
        p = os.path.join(a.briefs, "briefs", f"{r['slug']}.md")
        if os.path.exists(p):
            continue
        open(p, "w", encoding="utf-8").write(brief_md(r, tpl))
        created += 1
    print(f"matrix.md with {len(rows)} pages; {created} new briefs in {a.briefs}/briefs/")


if __name__ == "__main__":
    main()
