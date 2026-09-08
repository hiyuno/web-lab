#!/usr/bin/env python3
"""Phase 5: merge every findings/*.json into report.json + report.md.

Follows web-lab's shared report format (CLAUDE.md "Shared review method"): one table per
category, ordered by severity then reach, columns Severity · Where · Before · After · Why,
ending in a one-word verdict. Split into two tables (classic SEO vs. GEO/AEO) since they're
different audiences for the fix (the classic table is mostly "do this in Framer settings", the
GEO table is a newer, less certain area).

Usage: build_report.py --out <workdir> --site https://example.com
"""
import argparse, glob, json, os, sys

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def load_all(out_dir):
    findings = []
    for path in sorted(glob.glob(os.path.join(out_dir, "findings", "*.json"))):
        with open(path) as f:
            findings += json.load(f)
    return findings


def table(rows):
    if not rows:
        return "_No hay hallazgos en esta categoría._\n"
    lines = ["| Severity | Where | Before | After | Why |",
             "|---|---|---|---|---|"]
    for r in rows:
        cells = [r["severity"].upper(), r["where"], r["before"], r["after"], r["why"]]
        cells = [c.replace("|", "\\|").replace("\n", " ") for c in cells]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def render(site, findings):
    verified = [f for f in findings if f["status"] != "not_verified"]
    not_verified = [f for f in findings if f["status"] == "not_verified"]
    classic = sorted([f for f in verified if f["category"] == "classic"],
                      key=lambda f: (SEVERITY_ORDER[f["severity"]], f["page"]))
    geo = sorted([f for f in verified if f["category"] == "geo"],
                 key=lambda f: (SEVERITY_ORDER[f["severity"]], f["page"]))

    has_critical = any(f["severity"] == "critical" for f in verified)
    counts = {s: sum(f["severity"] == s for f in verified) for s in SEVERITY_ORDER}

    out = [f"# Auditoría SEO/GEO — {site}", ""]
    out.append(f"**Resumen:** {counts['critical']} critical · {counts['high']} high · "
                f"{counts['medium']} medium · {counts['low']} low · {counts['info']} info. "
                f"{len(not_verified)} hallazgo(s) no verificado(s) (no cuentan para el veredicto).")
    out.append("")
    out.append("## SEO clásico (Google y buscadores tradicionales)")
    out.append("")
    out.append(table(classic))
    out.append("## AI search / GEO-AEO (ChatGPT, Claude, Perplexity, AI Overviews)")
    out.append("")
    out.append(table(geo))
    if not_verified:
        out.append("## No verificado")
        out.append("")
        out.append("Se intentó revisar pero no se pudo confirmar (tráfico insuficiente, rate "
                    "limit, fetch fallido). No cuenta como hallazgo ni como aprobado.")
        out.append("")
        out.append(table(not_verified))
    out.append(f"\n**Veredicto: {'Blocked' if has_critical else 'Approved'}**\n")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--site", required=True)
    a = ap.parse_args()
    findings = load_all(a.out)
    for f in findings:
        f.setdefault("status", "open")

    report_json = os.path.join(a.out, "report.json")
    with open(report_json, "w") as fh:
        json.dump({"site": a.site, "findings": findings}, fh, indent=1, ensure_ascii=False)

    report_md = os.path.join(a.out, "report.md")
    with open(report_md, "w") as fh:
        fh.write(render(a.site, findings))

    print(f"{len(findings)} findings total -> {report_md}", file=sys.stderr)


if __name__ == "__main__":
    main()
