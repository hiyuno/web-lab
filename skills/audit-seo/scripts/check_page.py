#!/usr/bin/env python3
"""Step 3: per-page checks against a saved copy of the rendered HTML.

Takes the *rendered* HTML (after JS ran) so it works on Framer/Webflow/React sites, not just
static markup. The calling skill saves it with the browser tool's javascript_tool
(`document.documentElement.outerHTML`) before calling this script — see SKILL.md step 3.

Title and meta-description thresholds are the canonical numbers owned by `skills/seo`
(target title 50-60 chars / ~600px, meta 120-160 chars / ~920px desktop; flag too-short below
30 / 70). Keep them in sync with that skill, not the other way around.

Usage: check_page.py --html page.html --url https://example.com/pricing --slug pricing --out <workdir>
"""
import argparse, json, re, sys
from common import finding, write_findings, strip_tags

DATE_RE = re.compile(
    r"\b(20\d{2}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}\s+(?:de\s+)?"
    r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre"
    r"|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*,?\s*20\d{2})\b", re.I)
FRESHNESS_WORDS = re.compile(r"\b(actualizado|updated|publicado|published|last modified)\b", re.I)


def tag(html, name):
    m = re.search(rf"(?is)<{name}[^>]*>(.*?)</{name}>", html)
    return m.group(1).strip() if m else None


def meta(html, attr, value):
    m = re.search(rf'(?is)<meta[^>]+{attr}=["\']{re.escape(value)}["\'][^>]*content=["\']([^"\']*)["\']', html)
    if m:
        return m.group(1).strip()
    m = re.search(rf'(?is)<meta[^>]+content=["\']([^"\']*)["\'][^>]*{attr}=["\']{re.escape(value)}["\']', html)
    return m.group(1).strip() if m else None


def link_rel(html, rel):
    m = re.search(rf'(?is)<link[^>]+rel=["\']{rel}["\'][^>]*href=["\']([^"\']*)["\']', html)
    if m:
        return m.group(1)
    m = re.search(rf'(?is)<link[^>]+href=["\']([^"\']*)["\'][^>]*rel=["\']{rel}["\']', html)
    return m.group(1) if m else None


def json_ld_blocks(html):
    out = []
    for m in re.finditer(r'(?is)<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html):
        raw = m.group(1).strip()
        try:
            data = json.loads(raw)
        except Exception:
            out.append({"error": "invalid JSON", "raw": raw[:200]})
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict):
                out.append(item)
    return out


def schema_types(blocks):
    types = set()
    for b in blocks:
        t = b.get("@type") if isinstance(b, dict) else None
        if isinstance(t, list):
            types.update(t)
        elif t:
            types.add(t)
        for g in (b.get("@graph") if isinstance(b, dict) else None) or []:
            if isinstance(g, dict) and g.get("@type"):
                types.add(g["@type"] if isinstance(g["@type"], str) else ",".join(g["@type"]))
    return types


def check(html, url, slug):
    f = []
    kw = dict(page=slug, where=url)

    title = tag(html, "title")
    if not title:
        f.append(finding(severity="critical", category="classic", **kw,
                          before="No <title>.", after="Add a unique <title>, 50-60 characters.",
                          why="The title is the strongest on-page signal and what shows as the "
                              "search result's heading.", source="title"))
    elif not (30 <= len(title) <= 60):
        f.append(finding(severity="medium", category="classic", **kw,
                          before=f'<title>{title}</title> ({len(title)} characters).',
                          after="Target 50-60 characters (~600px), keyword near the start; below "
                                "30 is too short, above 60 risks truncation.",
                          why="Outside the range it gets truncated in results or reads as too "
                              "thin.", source="title"))

    desc = meta(html, "name", "description")
    if not desc:
        f.append(finding(severity="high", category="classic", **kw,
                          before="No meta description.",
                          after="Add a meta description of 120-160 characters summarizing the "
                                "page and its primary keyword.",
                          why="Google often uses it as the snippet; without one it generates an "
                              "automatic snippet you do not control.", source="meta_description"))
    elif not (70 <= len(desc) <= 160):
        f.append(finding(severity="low", category="classic", **kw,
                          before=f"Meta description of {len(desc)} characters.",
                          after="Target 120-160 characters (front-load the key message in the "
                                "first ~120 for mobile); below 70 wastes snippet space, above 160 "
                                "truncates.",
                          why="Too short wastes snippet space; too long gets truncated.",
                          source="meta_description"))

    h1s = re.findall(r"(?is)<h1[^>]*>(.*?)</h1>", html)
    h1s = [strip_tags(h) for h in h1s if strip_tags(h)]
    if len(h1s) == 0:
        f.append(finding(severity="high", category="classic", **kw,
                          before="No <h1>.", after="Add exactly one H1 that describes the page's "
                          "topic.", why="The H1 is the clearest hierarchy signal for search "
                          "engines and screen readers.", source="h1"))
    elif len(h1s) > 1:
        f.append(finding(severity="medium", category="classic", **kw,
                          before=f"{len(h1s)} <h1> elements: {h1s[:3]}",
                          after="Keep a single H1 per page; the rest become H2/H3.",
                          why="Multiple H1s dilute the main-topic signal.", source="h1"))

    canonical = link_rel(html, "canonical")
    if not canonical:
        f.append(finding(severity="medium", category="classic", **kw,
                          before="No <link rel=\"canonical\">.",
                          after="Add a canonical pointing to the page's definitive URL.",
                          why="Without a canonical, content reachable through URL variants "
                              "(with/without slash, parameters) can be treated as duplicate.",
                          source="canonical"))

    robots = meta(html, "name", "robots")
    if robots and "noindex" in robots.lower():
        f.append(finding(severity="critical", category="classic", **kw,
                          before=f'<meta name="robots" content="{robots}">',
                          after="Remove noindex if this page should appear in search engines.",
                          why="noindex removes the page from Google's results entirely, even if "
                              "the rest of the SEO is perfect.", source="meta_robots"))

    lang = re.search(r'(?is)<html[^>]+lang=["\']([^"\']+)["\']', html)
    if not lang:
        f.append(finding(severity="low", category="classic", **kw,
                          before="<html> has no lang attribute.",
                          after='Add lang="es" (or the matching language).',
                          why="It helps search engines and screen readers identify the content's "
                              "language.", source="lang"))

    imgs = re.findall(r"(?is)<img\b([^>]*)>", html)
    missing_alt = 0
    for attrs in imgs:
        if not re.search(r'(?is)\balt=["\']', attrs):
            missing_alt += 1
    if missing_alt:
        f.append(finding(severity="medium", category="classic", **kw,
                          before=f"{missing_alt} of {len(imgs)} <img> without an alt attribute.",
                          after="Add descriptive alt (empty alt=\"\" only if purely decorative).",
                          why="Alt text is an accessibility and image-SEO signal; its absence is "
                              "also a high-severity accessibility finding.", source="alt_text"))

    og_title = meta(html, "property", "og:title")
    og_desc = meta(html, "property", "og:description")
    og_image = meta(html, "property", "og:image")
    if not (og_title and og_desc and og_image):
        missing = [n for n, v in (("og:title", og_title), ("og:description", og_desc),
                                   ("og:image", og_image)) if not v]
        f.append(finding(severity="low", category="classic", **kw,
                          before=f"Missing Open Graph tags: {', '.join(missing)}.",
                          after="Complete og:title, og:description and og:image (Framer: Settings "
                                "→ SEO → Open Graph Image per page).",
                          why="Without these, links shared on social/WhatsApp/Slack render with "
                              "no preview or a generic one.", source="open_graph"))

    blocks = json_ld_blocks(html)
    types = schema_types(blocks)
    if not blocks:
        f.append(finding(severity="medium", category="classic", **kw,
                          before="No JSON-LD (schema.org) blocks.",
                          after="Add at least Organization (or LocalBusiness) at the site level, "
                                "and the type that applies per page (Article, Product, "
                                "SoftwareApplication...) via Framer's custom code block.",
                          why="In 2026 schema is part of the technical baseline, not an extra: it "
                              "helps rich results in Google and gives AI engines an explicit "
                              "description of what the entity/page is.", source="schema"))
    elif any("error" in b for b in blocks):
        f.append(finding(severity="high", category="classic", **kw,
                          before="A JSON-LD block has invalid JSON.",
                          after="Fix the syntax; validate with Google's Rich Results Test before "
                                "publishing.", why="Invalid JSON-LD is ignored completely, as if "
                                "it did not exist.", source="schema"))

    text = strip_tags(html)
    words = len(text.split())
    if words < 150:
        f.append(finding(severity="low", category="classic", **kw,
                          before=f"~{words} words of visible text.",
                          after="If this is a content page (not a deliberately short form/landing), "
                                "expand to 300+ words with real substance.",
                          why="Very thin pages rarely rank and give little citable material for "
                              "AI.", source="word_count", status="not_verified"))

    if not DATE_RE.search(text) and not FRESHNESS_WORDS.search(text):
        f.append(finding(severity="low", category="geo", **kw,
                          before="No visible publication/update date in the text.",
                          after="Show a visible date (\"Updated: Sep 2026\") alongside the schema "
                                "`dateModified`.",
                          why="AI engines (Perplexity especially) strongly prioritize content "
                              "with verifiable freshness; without a visible date they cannot "
                              "confirm it.", source="freshness"))

    first_chunk = text[:400]
    if len(first_chunk) < 40:
        f.append(finding(severity="low", category="geo", **kw,
                          before="The first block of visible text is very short or empty.",
                          after="Open the page with 1-2 sentences summarizing what it is and for "
                                "whom, in plain text (not only inside an image or animation).",
                          why="A clear summary up top is what an LLM most easily quotes verbatim "
                              "when answering a related question.",
                          source="citability", status="not_verified"))

    return f, {"title": title, "description": desc, "h1": h1s, "canonical": canonical,
               "schema_types": sorted(types), "word_count": words}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    with open(a.html, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    findings, summary = check(html, a.url, a.slug)
    path = write_findings(a.out, f"page-{a.slug}", findings)
    print(json.dumps(summary, ensure_ascii=False), file=sys.stderr)
    print(f"{len(findings)} findings -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
