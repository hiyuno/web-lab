#!/usr/bin/env python3
"""Phase 3: merge every findings/*.json into report.json + report.md.

Follows web-lab's shared report format (CLAUDE.md "Shared review method"): one table per
category, ordered by severity then reach, ending in a one-word verdict. Three tables here
(composited, runtime, safari-risk) instead of audit-seo's two, and an extra Confidence column
since this skill mixes measured, documented and heuristic findings in the same report.

Usage: build_report.py --out <workdir> --site https://example.com
"""
import argparse, glob, json, os, sys
from common import SEVERITY_ORDER


def load_all(out_dir):
    findings = []
    for path in sorted(glob.glob(os.path.join(out_dir, "findings", "*.json"))):
        with open(path) as f:
            findings += json.load(f)
    return findings


def table(rows):
    if not rows:
        return "_No findings in this category._\n"
    lines = ["| Severity | Confidence | Where | Before | After | Why |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        cells = [r["severity"].upper(), r["confidence"], r["where"], r["before"], r["after"],
                 r["why"]]
        cells = [c.replace("|", "\\|").replace("\n", " ") for c in cells]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def render(site, findings, platform, ran_runtime, page_count):
    for f in findings:
        f.setdefault("confidence", "heuristic")
    verified = [f for f in findings if f["status"] != "not_verified"]
    not_verified = [f for f in findings if f["status"] == "not_verified"]

    composited = sorted([f for f in verified if f["category"] == "composited"],
                         key=lambda f: (SEVERITY_ORDER[f["severity"]], f["page"]))
    runtime = sorted([f for f in verified if f["category"] == "runtime"],
                      key=lambda f: (SEVERITY_ORDER[f["severity"]], f["page"]))
    safari = sorted([f for f in verified if f["category"] == "safari-risk"],
                     key=lambda f: (SEVERITY_ORDER[f["severity"]], f["page"]))

    has_critical = any(f["severity"] == "critical" and f["category"] in ("composited", "runtime")
                        for f in verified)
    has_open_high = any(f["severity"] == "high" for f in verified)
    counts = {s: sum(f["severity"] == s for f in verified) for s in SEVERITY_ORDER}

    out = [f"# Animation performance audit — {site}", ""]
    out.append(f"**Summary:** {counts['critical']} critical · {counts['high']} high · "
                f"{counts['medium']} medium · {counts['low']} low · {counts['info']} info. "
                f"{len(not_verified)} not verified finding(s) (do not count toward the verdict).")
    out.append("")
    out.append("## Composited (compositor-thread eligibility)")
    out.append("")
    out.append(table(composited))
    out.append("## Runtime (Chrome-measured jank)")
    out.append("")
    out.append(table(runtime))
    out.append("## Safari risk (documented/heuristic, never measured here)")
    out.append("")
    out.append(table(safari))

    if not_verified:
        out.append("## Not verified")
        out.append("")
        out.append("Findings the checks could still produce a number for, but that number "
                    "could not be trusted (e.g. a throttled measurement environment). Neither "
                    "a finding nor a pass.")
        out.append("")
        out.append(table(not_verified))

    if platform == "framer":
        out.append("Platform: Framer — see `references/framer-fixes.md` for exact fixes "
                    "instead of generic advice.")
        out.append("")

    if not verified:
        out.append(f"\n**No actionable findings.** Checked {page_count} page(s); runtime "
                    f"measurement {'ran' if ran_runtime else 'did not run'}.\n")
    else:
        verdict = "Blocked" if has_critical else "Approved"
        out.append(f"\n**Verdict: {verdict}**")
        if not has_critical and has_open_high:
            out.append("\nOpen `high` findings remain — they do not block, but are worth "
                        "prioritizing next.")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--site", required=True)
    a = ap.parse_args()

    findings = load_all(a.out)
    for f in findings:
        f.setdefault("status", "open")

    platform = None
    platform_path = os.path.join(a.out, "platform.json")
    if os.path.exists(platform_path):
        try:
            with open(platform_path) as fh:
                platform = (json.load(fh) or {}).get("platform")
        except Exception:
            platform = None

    ran_runtime = bool(glob.glob(os.path.join(a.out, "findings", "runtime-*.json")))
    page_count = len({f["page"] for f in findings}) if findings else 0

    report_json = os.path.join(a.out, "report.json")
    with open(report_json, "w") as fh:
        json.dump({"site": a.site, "findings": findings}, fh, indent=1, ensure_ascii=False)

    report_md = os.path.join(a.out, "report.md")
    with open(report_md, "w") as fh:
        fh.write(render(a.site, findings, platform, ran_runtime, page_count))

    print(f"{len(findings)} findings total -> {report_md}", file=sys.stderr)


if __name__ == "__main__":
    main()
