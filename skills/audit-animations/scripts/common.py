"""Shared helpers for audit-animations checks: a common finding shape every script writes,
so build_report.py only has to merge JSON files instead of knowing each check's internals.

Severity:   critical | high | medium | low | info
Category:   composited (compositor-thread eligibility) | runtime (Chrome-measured jank) |
            safari-risk (documented/heuristic Safari-only risk, never measured here)
Confidence: measured (real browser measurement) | documented (cited from an official or
            near-official source) | heuristic (this skill's own threshold or best-effort signal)
Status:     open | not_verified

Unlike audit-seo's common.py, this skill never fetches a URL itself: the raw per-page data
comes from a browser-side JS collector (line files) or a browser-side probe (JSON files) that
the calling skill writes before invoking these scripts. So there are no fetch/fetch_status
helpers here.
"""
import json, os

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
CATEGORIES = ("composited", "runtime", "safari-risk")
CONFIDENCES = ("measured", "documented", "heuristic")

_seq = {"n": 0}


def finding(*, severity, category, page, where, before, after, why, source,
            status="open", confidence="heuristic", nodes=None):
    assert severity in SEVERITY_ORDER
    assert category in CATEGORIES
    assert confidence in CONFIDENCES
    assert not (category == "safari-risk" and severity == "critical")  # safari-risk never blocks
    _seq["n"] += 1
    return {
        "id": f"f{_seq['n']}-{source}",
        "severity": severity,
        "category": category,
        "page": page,        # slug, or "site" for page-independent checks
        "where": where,       # selector, URL, or "site-wide" for page-independent checks
        "nodes": nodes or [],  # additional selector paths sharing the same root cause
        "before": before,
        "after": after,
        "why": why,
        "source": source,     # which check produced it, for references lookup
        "status": status,
        "confidence": confidence,
    }


def write_findings(out_dir, name, findings):
    path = os.path.join(out_dir, "findings")
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, f"{name}.json"), "w") as f:
        json.dump(findings, f, indent=1, ensure_ascii=False)
    return os.path.join(path, f"{name}.json")
