#!/usr/bin/env python3
"""Phase 2: per-page "safari-risk" checks against the same raw line file as check_page.py.

Reuses check_page.py's parse_raw() — same file, same format, same directory, so importing it
locally avoids re-implementing the parser. See check_page.py's module docstring for the raw
line format.

Every finding here is a documented or heuristic *risk flag*, never a measurement: the harness
that runs this skill drives Chrome, not real Safari, so nothing in this file is confirmed
against actual Safari behavior. Severity is capped at "high" (common.finding() asserts that
category "safari-risk" can never be "critical" — these never block a launch on their own).

Usage: check_safari.py --raw <out>/raw/<slug>.txt --url <url> --slug <slug> --out <out>
"""
import argparse, re, sys
from common import finding, write_findings
from check_page import parse_raw

LAYER_THRESHOLD = 20  # same threshold as check_page.py's layer_promotion

BLUR_RE = re.compile(r"blur\(\s*([\d.]+)", re.I)


def check_backdrop_filter_animated(data, page):
    animating = {r["selector"] for r in data["A"]} | {r["selector"] for r in data["R"]}
    out, seen = [], set()
    for row in data["F"]:
        if row["kind"] != "backdrop-filter" or row["selector"] not in animating:
            continue
        if row["selector"] in seen:
            continue
        seen.add(row["selector"])
        out.append(finding(
            severity="high", category="safari-risk", page=page, where=row["selector"],
            before=f"backdrop-filter: {row['value']} on an element that is also animating.",
            after="Avoid animating an element that also has backdrop-filter, or test carefully "
                  "on real Safari/iOS before shipping.",
            why="Never measured here (this harness drives Chrome, not Safari) — documented "
                "risk: WebKit's own blog post introducing backdrop-filter says the effect "
                "forces the engine to perform more rendering passes and recommends using it "
                "only where it is most necessary.",
            source="backdrop_filter_animated", confidence="documented",
        ))
    return out


def check_will_change_backdrop(data, page):
    out, seen = [], set()
    for row in data["L"]:
        if row["reason"] != "backdrop-filter" or row["selector"] in seen:
            continue
        seen.add(row["selector"])
        out.append(finding(
            severity="medium", category="safari-risk", page=page, where=row["selector"],
            before="`will-change: backdrop-filter` (or an equivalent promotion hint) detected.",
            after="Confirm this is actually needed on Safari/iOS; remove if it isn't tied to an "
                  "active animation.",
            why="Never measured here. Lower confidence than the other Safari findings in this "
                "file: this is based on scattered developer reports of Safari-specific issues "
                "with `will-change: backdrop-filter`, not official WebKit documentation.",
            source="will_change_backdrop", confidence="heuristic",
        ))
    return out


def check_blur_radius_large(data, page):
    animating = {r["selector"] for r in data["A"]} | {r["selector"] for r in data["R"]}
    out, seen = [], set()
    for row in data["F"]:
        if row["kind"] not in ("filter", "backdrop-filter"):
            continue
        m = BLUR_RE.search(row["value"])
        if not m:
            continue
        try:
            radius = float(m.group(1))
        except ValueError:
            continue
        if radius < 10:
            continue
        key = (row["selector"], row["kind"])
        if key in seen:
            continue
        seen.add(key)
        is_animating = row["selector"] in animating
        out.append(finding(
            severity="medium" if is_animating else "low", category="safari-risk", page=page,
            where=row["selector"],
            before=f"{row['kind']}: {row['value']} ({radius}px blur)"
                   f"{' on an animating element' if is_animating else ''}.",
            after="Keep blur radius under 10px where possible.",
            why="Never measured here. Framer's own site-optimization help page recommends "
                "keeping blur values below 10 to maintain performance — this applies beyond "
                "Framer too, since it reflects a real GPU cost rather than a platform quirk.",
            source="blur_radius_large", confidence="documented",
        ))
    return out


def check_blend_mode_with_filter(data, page):
    by_selector = {}
    for row in data["F"]:
        by_selector.setdefault(row["selector"], set()).add(row["kind"])
    out = []
    for selector, kinds in by_selector.items():
        if "mix-blend-mode" in kinds and ("filter" in kinds or "backdrop-filter" in kinds):
            out.append(finding(
                severity="medium", category="safari-risk", page=page, where=selector,
                before="Element has both `mix-blend-mode` and `filter`/`backdrop-filter`.",
                after="Test this combination on real Safari/iOS; consider separating the blend "
                      "mode and the filter onto different elements.",
                why="Never measured here. This is a documented WebKit rendering bug — a "
                    "correctness AND performance issue, not performance alone — where the "
                    "blend mode gets ignored or misrendered when combined with a filter on the "
                    "same or related elements.",
                source="blend_mode_with_filter", confidence="documented",
            ))
    return out


def check_fixed_with_filter_ancestor(data, page):
    if not data["P"] or not data["F"]:
        return []
    return [finding(
        severity="medium", category="safari-risk", page=page, where="site-wide",
        before=f"Page has {len(data['P'])} fixed/sticky element(s) and {len(data['F'])} "
               "filter/backdrop-filter/mix-blend-mode element(s).",
        after="Check whether any filter/opacity/mix-blend-mode/transform sits between a "
              "fixed/sticky element and its intended containing block; move the effect if so.",
        why="Never measured here. This only flags the *possibility* — ancestor relationships "
            "aren't verifiable from this flat selector data. `filter`/`opacity`/"
            "`mix-blend-mode`/`transform` on an ancestor creates a stacking context but not a "
            "containing block for `position: fixed`, which can misplace or clip it on Safari.",
        source="fixed_with_filter_ancestor", confidence="documented",
    )]


def check_playback_rate_altered(data, page):
    out = []
    for row in data["A"]:
        rate = row["playback_rate"]
        if rate is None or rate == 1:
            continue
        out.append(finding(
            severity="low", category="safari-risk", page=page, where=row["selector"],
            before=f"Animation with playbackRate={rate}.",
            after="Keep `playbackRate` at 1; bake the rate change into the keyframes instead.",
            why="Never measured here. Safari loses hardware acceleration for animations with "
                "an altered playback rate, as documented by Motion's performance guide — same "
                "underlying fact as check_page.py's `timing_params` check, seen from the "
                "Safari-specific angle.",
            source="playback_rate_altered", confidence="documented",
        ))
    return out


def check_layer_budget_safari(data, page):
    selectors = {row["selector"] for row in data["L"]}
    if len(selectors) < LAYER_THRESHOLD:
        return []
    return [finding(
        severity="low", category="safari-risk", page=page, where="whole page",
        before=f"{len(selectors)} distinct elements promoted to their own compositor layer.",
        after="Reduce the number of simultaneously promoted layers, especially if this page "
              "matters on iOS/Safari.",
        why="Never measured here. No current authoritative source confirms Safari falls back "
            "to software rendering under GPU memory pressure sooner than Chrome — this is "
            "included as a low-confidence risk flag, not a documented fact.",
        source="layer_budget_safari", confidence="heuristic",
    )]


def check(data, page):
    findings = []
    findings += check_backdrop_filter_animated(data, page)
    findings += check_will_change_backdrop(data, page)
    findings += check_blur_radius_large(data, page)
    findings += check_blend_mode_with_filter(data, page)
    findings += check_fixed_with_filter_ancestor(data, page)
    findings += check_playback_rate_altered(data, page)
    findings += check_layer_budget_safari(data, page)
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    _, data, _ = parse_raw(a.raw)
    findings = check(data, a.slug)
    path = write_findings(a.out, f"safari-{a.slug}", findings)
    print(f"{len(findings)} findings -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
