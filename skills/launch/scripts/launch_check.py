#!/usr/bin/env python3
"""Phase 7, step 7.7: first-60-minutes verification against production.

Reuses skills/qa/scripts/crawl_check.py (crawl, 404, redirects, metadata, robots, sitemap,
HTTPS, headers, sensitive paths) and adds what only matters on cutover day, ordered by cost of
failure: access (robots/noindex, certificate), identity (200/404/canonical) and continuity
(every old-site URL responds 200 or a direct 301, never 404).

Usage:
  launch_check.py https://example.mx --redirects docs/02-structure/redirects.md \
      --seo docs/03-content/seo.md --old-urls docs/02-structure/pages.json > docs/07-launch/first-60-minutes.md
"""
import argparse, datetime as dt, json, os, subprocess, sys, urllib.parse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
CRAWL = os.path.normpath(os.path.join(HERE, "..", "..", "qa", "scripts", "crawl_check.py"))
DOMAIN = os.path.join(HERE, "domain_check.py")


def status(url, follow=False):
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedir)
    try:
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "web-lab-launch-check"}), timeout=15) as r:
            return r.status, r.headers.get("Location", "")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location", "") or ""
    except Exception:
        return 0, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--redirects")
    ap.add_argument("--seo")
    ap.add_argument("--old-urls", help="pages.json of the old site (phase 2) or txt with one URL per line")
    ap.add_argument("--max", type=int, default=300)
    a = ap.parse_args()
    base = a.base if a.base.startswith("http") else "https://" + a.base
    base = base.rstrip("/") + "/"
    host = urllib.parse.urlsplit(base).netloc

    cmd = [sys.executable, CRAWL, base, "--json", "--max", str(a.max)]
    if a.redirects: cmd += ["--redirects", a.redirects]
    if a.seo: cmd += ["--seo", a.seo]
    crawl = json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout or "{}")
    findings = crawl.get("findings", [])

    dom = {}
    if os.path.exists(DOMAIN):
        out = subprocess.run([sys.executable, DOMAIN, host.split(":")[0], "--json"], capture_output=True, text=True).stdout
        try:
            dom = json.loads(out)
        except Exception:
            dom = {}
        has_http = any("http responds" in f["what"].lower() for f in findings)
        for x in dom.get("findings", []):
            if has_http and "http://" in x["what"].lower():
                continue  # already reported by the crawl
            findings.append({"sev": x["sev"], "where": host, "what": x["what"], "fix": x["fix"]})

    # continuity: old-site URLs
    cont = []
    if a.old_urls and os.path.exists(a.old_urls):
        txt = open(a.old_urls, encoding="utf-8").read()
        urls = [p["url"] for p in json.loads(txt).get("pages", [])] if txt.lstrip().startswith("{") else [l.strip() for l in txt.splitlines() if l.strip()]
        for u in urls:
            path = urllib.parse.urlsplit(u).path or "/"
            st, loc = status(urllib.parse.urljoin(base, path.lstrip("/")))
            ok = st == 200 or st in (301, 308)
            chain = False
            if st in (301, 308) and loc:
                st2, _ = status(urllib.parse.urljoin(base, loc))
                chain = st2 in (301, 302, 307, 308)
                ok = ok and st2 == 200
            cont.append({"path": path, "status": st, "location": loc, "ok": ok and not chain})
            if not ok or chain:
                findings.append({"sev": "critical", "where": path, "what": f"old-site URL responds {st}" + (" with a chain" if chain else ""), "fix": "direct 301 to its equivalent; never 404 on cutover day"})

    # classification by cost of failure
    def tier(f):
        w = f["what"].lower()  # only the finding text, not the URL
        if any(k in w for k in ("old-site", "chain", "redirect", "sitemap")): return "3 Continuity"
        if any(k in w for k in ("canonical", "h1", "<title>", "title", "responds 4", "responds 5")): return "2 Identity"
        if any(k in w for k in ("noindex", "robots", "disallow", "certificate", "tls", "http responds", "http://", "hsts", "csp")): return "1 Access"
        return "4 Improvement"
    for f in findings: f["tier"] = tier(f)
    order = {"blocker": 0, "critical": 1, "major": 2, "minor": 3, "trivial": 4}
    findings.sort(key=lambda f: (f["tier"], order.get(f["sev"], 5)))

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"# First-60-minutes verification · {base} · {now}\n")
    blockers = [f for f in findings if f["tier"] in ("1 Access", "3 Continuity") and f["sev"] in ("blocker", "critical")]
    print(f"**Decision**: {'ROLLBACK if not fixed in minutes: ' + str(len(blockers)) + ' critical access or continuity finding(s)' if blockers else 'continue; no access or continuity criticals'}\n")
    print(f"Pages crawled: {len(crawl.get('pages', []))} · Old URLs verified: {len(cont)} · Findings: {len(findings)}\n")
    print("## Findings by cost of failure\n\n| Tier | Severity | Where | What | Fix |\n|---|---|---|---|---|")
    for f in findings:
        print(f"| {f['tier']} | {f['sev']} | {f['where']} | {f['what'].replace('|', '/')} | {f['fix']} |")
    if not findings:
        print("| — | — | — | no findings | — |")
    if cont:
        print("\n## Continuity · old-site URLs\n\n| Path | Code | Location | Ok |\n|---|---|---|---|")
        for c in cont:
            print(f"| {c['path']} | {c['status']} | {c['location']} | {'yes' if c['ok'] else 'NO'} |")
    print("\n## Manual in the first hour\n")
    for item in ("Main form submitted and received", "Login and recovery (if any) with a test user", "Analytics: page and conversion events fire once, respect consent",
                 "Sitemap submitted to Search Console and Bing; home indexing requested", "Sentry errors: zero new in 60 min", "Availability: no alerts", "Launch annotation in analytics"):
        print(f"- [ ] {item}")
    sys.exit(1 if blockers else 0)


if __name__ == "__main__":
    main()
