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

# ---- Raw line file encoding ----------------------------------------------------------------
# The raw per-page files collect_animations.js writes are pipe-delimited, and two of the fields
# added for Framer layer paths (`layer`, `text`) come from author-controlled strings that may
# legitimately contain a "|". Rather than switch the whole format to something quoted, the
# collector escapes the separator to U+00A6 BROKEN BAR before emitting a field, and the parsers
# here turn it back. Defined on this side (not only in the JS) so both halves share one constant.
FIELD_SEP = "|"
FIELD_ESCAPE = "\u00a6"   # BROKEN BAR — never produced by the collector except as an escape
LAYER_SEP = " \u203a "     # " › " between Framer layer names, outermost first
LAYER_MAX_DEPTH = 6        # at most this many data-framer-name levels in one path
TEXT_MAX = 40              # first N characters of the element's (or nearest ancestor's) text
EMPTY_FIELD = "-"          # what the collector writes for an absent layer/text/y


def escape_field(s):
    """Make a string safe to place between two FIELD_SEPs in a raw line."""
    return (s or "").replace(FIELD_SEP, FIELD_ESCAPE).replace("\n", " ").replace("\r", " ")


def unescape_field(s):
    """Inverse of escape_field(); also maps the collector's EMPTY_FIELD to None."""
    if s is None:
        return None
    s = s.replace(FIELD_ESCAPE, FIELD_SEP)
    return None if s == EMPTY_FIELD or s == "" else s


def parse_int_field(s):
    """Parse a `y` field: an integer, or None for EMPTY_FIELD / anything unparseable."""
    if s is None or s in (EMPTY_FIELD, ""):
        return None
    try:
        return int(float(s))
    except (TypeError, ValueError):
        return None


SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
CATEGORIES = ("composited", "runtime", "safari-risk")
CONFIDENCES = ("measured", "documented", "heuristic")

_seq = {"n": 0}


def finding(*, severity, category, page, where, before, after, why, source,
            status="open", confidence="heuristic", nodes=None,
            layer=None, text=None, y=None):
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
        # Framer layer coordinates, so a finding can be located in the editor's Layers panel
        # instead of in a CSS class the author never wrote. All three are None for page-level
        # findings ("whole page"/"site-wide") and for any element with no data-framer-name.
        "layer": layer,       # "Hero › Title" — data-framer-name path, outermost first
        "text": text,         # first 40 chars of the element's own or nearest ancestor's text
        "y": y,               # absolute vertical position in the page, in CSS px
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
