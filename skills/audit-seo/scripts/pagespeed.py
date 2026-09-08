#!/usr/bin/env python3
"""Phase 4: Core Web Vitals via the public PageSpeed Insights API.

No API key required for low-volume use (a handful of pages); pass GOOGLE_PAGESPEED_API_KEY in
the environment to raise the quota if the audit covers many pages. Field data (real users, CrUX)
is what Google actually uses for ranking; when a page/site has too little traffic for CrUX,
PSI omits `loadingExperience` and this script marks the finding **not_verified** instead of
reporting lab data as if it were the ranking signal.

Usage: pagespeed.py https://example.com/pricing --slug pricing --out <workdir> [--strategy mobile]
"""
import argparse, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from common import finding, write_findings

API = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
GOOD = {"LCP": 2500, "CLS": 0.1, "INP": 200}  # ms, unitless, ms


def run(url, strategy, key=None, timeout=60):
    params = {"url": url, "strategy": strategy, "category": "PERFORMANCE"}
    if key:
        params["key"] = key
    full = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"User-Agent": "seo-web-audit"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def metric_field(loading_experience, key):
    m = (loading_experience or {}).get("metrics", {}).get(key)
    if not m:
        return None
    return m.get("percentile"), m.get("category")  # category: FAST/AVERAGE/SLOW


def check(url, slug, strategy, key):
    findings = []
    try:
        data = run(url, strategy, key)
    except urllib.error.HTTPError as e:
        code = e.code
        findings.append(finding(
            severity="low", category="classic", page=slug, where=url,
            before=f"PageSpeed Insights respondió {code} (posible rate limit o URL no accesible "
                   "públicamente).",
            after="Reintentar más tarde o exportar `GOOGLE_PAGESPEED_API_KEY` para subir la "
                  "cuota.", why="", source="pagespeed", status="not_verified"))
        return findings
    except Exception as e:
        findings.append(finding(
            severity="low", category="classic", page=slug, where=url,
            before=f"No se pudo consultar PageSpeed Insights: {e}", after="Reintentar.",
            why="", source="pagespeed", status="not_verified"))
        return findings

    le = data.get("loadingExperience") or data.get("originLoadingExperience")
    field_source = "page" if data.get("loadingExperience") else (
        "origin" if data.get("originLoadingExperience") else None)
    if not field_source:
        lh = data.get("lighthouseResult", {})
        score = ((lh.get("categories") or {}).get("performance") or {}).get("score")
        findings.append(finding(
            severity="info", category="classic", page=slug, where=url,
            before="Sin datos de campo (CrUX) suficientes para esta página u origen — tráfico "
                   "insuficiente para que Google reporte Core Web Vitals reales.",
            after=f"Referencia de laboratorio (Lighthouse, no ranking real): performance score "
                  f"{round((score or 0) * 100)}/100. Revisar de nuevo cuando el sitio tenga más "
                  "tráfico.",
            why="Google usa datos de campo (CrUX, 28 días, p75) para ranking, no el score de "
                "laboratorio.", source="pagespeed", status="not_verified"))
        return findings

    for key_name, unit in (("LARGEST_CONTENTFUL_PAINT_MS", "LCP"),
                            ("INTERACTION_TO_NEXT_PAINT", "INP"),
                            ("CUMULATIVE_LAYOUT_SHIFT_SCORE", "CLS")):
        result = metric_field(le, key_name)
        if not result:
            continue
        value, category = result
        v = value / 1000 if unit == "CLS" else value
        good = GOOD[unit]
        if category != "FAST":
            severity = "high" if category == "SLOW" else "medium"
            unit_label = "ms" if unit != "CLS" else ""
            findings.append(finding(
                severity=severity, category="classic", page=slug, where=url,
                before=f"{unit} = {v}{unit_label} ({field_source} data, categoría {category}).",
                after=f"Optimizar hasta estar bajo {good}{unit_label} en el percentil 75 real de "
                      "usuarios.",
                why="Core Web Vitals es un factor de ranking directo desde 2021; INP (no FID) es "
                    "el estándar de responsividad en 2026.", source="pagespeed"))
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--strategy", default="mobile", choices=["mobile", "desktop"])
    a = ap.parse_args()
    key = os.environ.get("GOOGLE_PAGESPEED_API_KEY")
    findings = check(a.url, a.slug, a.strategy, key)
    path = write_findings(a.out, f"pagespeed-{a.slug}", findings)
    print(f"{len(findings)} findings -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
