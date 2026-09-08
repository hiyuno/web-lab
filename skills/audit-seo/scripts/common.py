"""Shared helpers for audit-seo checks: a common finding shape every script writes,
so build_report.py only has to merge JSON files instead of knowing each check's internals.

Severity: critical | high | medium | low | info
Category: classic (Google/technical SEO) | geo (AI-search / answer-engine findability)
Status:   open | not_verified
"""
import json, os, re, urllib.request

UA = {"User-Agent": "Mozilla/5.0 seo-web-audit"}


def fetch(url, timeout=20, headers=None):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.getcode(), r.read().decode("utf-8", "replace"), dict(r.headers)


def fetch_status(url, timeout=20):
    """Like fetch but never raises for HTTP errors; returns (code, body_or_none, headers)."""
    try:
        return fetch(url, timeout=timeout)
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, body, dict(e.headers or {})
    except Exception as e:
        return None, str(e), {}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # tells urllib to stop and hand back the 3xx response as-is


def fetch_status_nofollow(url, timeout=20):
    """Like fetch_status but reports the FIRST response's status, not the one after following
    redirects — urlopen follows 3xx by default, which hides whether a redirect exists at all."""
    req = urllib.request.Request(url, headers=UA)
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.getcode(), None, dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, None, dict(e.headers or {})
    except Exception as e:
        return None, str(e), {}


_seq = {"n": 0}


def finding(*, severity, category, page, where, before, after, why, source, status="open"):
    _seq["n"] += 1
    assert severity in ("critical", "high", "medium", "low", "info")
    assert category in ("classic", "geo")
    return {
        "id": f"f{_seq['n']}-{source}",
        "severity": severity,
        "category": category,
        "page": page,       # slug, or "site" for site-wide checks
        "where": where,      # URL or file (robots.txt, sitemap.xml...)
        "before": before,
        "after": after,
        "why": why,
        "source": source,    # which script/check produced it, for references/checks.md lookup
        "status": status,
    }


def write_findings(out_dir, name, findings):
    path = os.path.join(out_dir, "findings")
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, f"{name}.json"), "w") as f:
        json.dump(findings, f, indent=1, ensure_ascii=False)
    return os.path.join(path, f"{name}.json")


def strip_tags(html):
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()
