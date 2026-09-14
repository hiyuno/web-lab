#!/usr/bin/env python3
"""Phase 2: per-page "composited" checks against a browser-collected raw line file.

The raw file is written by a browser-side JS collector (owned by another task, not this
script) before this script runs. Format: one header line, then one data line per
finding-worthy element, pipe-delimited, first field a type tag:

    page=<url>|slug=<slug>|dpr=<n>|vw=<n>|vh=<n>|reducedMotion=<0|1>
    A|<selector>|<props>|<composite>|<playbackRate>|<iterationStart>|<playState>|<layer>|<text>|<y>
    R|<selector>|<props>|<layer>|<text>|<y>
    L|<selector>|<reason>|<layer>|<text>|<y>
    F|<selector>|<kind>|<value>|<layer>|<text>|<y>
    P|<selector>|<position>|<layer>|<text>|<y>
    X|<selector>|<layer>|<text>|<y>
    S|scroll|<count>

Every line that carries a selector ends with the same three Framer-locator fields, `-` when
empty: <layer> is the `data-framer-name` path of the element and its ancestors joined by " › "
(what the Framer editor's Layers panel shows), <text> the first 40 characters of its own or its
nearest ancestor's text, <y> its absolute vertical position in the page in CSS px. Raw files
written before these fields existed parse fine — the three values come back as None.

- A: a Web Animations API animation from document.getAnimations(). <props> is a comma-joined
  list of animated CSS property names (camelCase, as returned by getKeyframes()).
- R: an element that received repeated inline `style` writes during a scripted scroll (e.g. a
  rAF-driven library animation) — these never show up in getAnimations().
- L: a promoted/likely-GPU-layer element. <reason> one of will-change/translate3d/translateZ/
  backface-hidden/backdrop-filter.
- F: an element with a visual effect. <kind> one of filter/backdrop-filter/mix-blend-mode.
- P: a position:fixed or position:sticky element.
- S: one line, scroll listener count detected heuristically (best-effort: passive flag cannot
  be detected from page-context JS after the page's own scripts already ran).

Usage: check_page.py --raw <out>/raw/<slug>.txt --url <url> --slug <slug> --out <out>
       [--platform framer|other]
"""
import argparse, json, os, re, sys
from common import finding, write_findings, unescape_field, parse_int_field

# GPU-safe / compositable property allowlist for the unsupported_property check. transform and
# opacity are the only fully compositor-only properties; filter/backdrop-filter/clip-path are
# accepted here too (Chrome CAN composite these in many cases) — the specific pixel-moving-filter
# case (blur/drop-shadow/box-reflect) is its own separate check below, not blanket-flagged here.
#
# Named constant (not just a local literal) because check_runtime.py's runtime_non_composited_write
# check answers the same question from a live observation instead of this static heuristic, and
# imports this exact set so the two allowlists can't drift apart. Compared via _norm_prop(), which
# lowercases and strips dashes — so "backdropFilter", "backdrop-filter" and "backdropfilter" (and
# same for clip-path) all normalize to the single form listed here.
COMPOSITABLE_PROPS = {"transform", "opacity", "filter", "backdropfilter", "clippath"}
ALLOWED_PROPS = COMPOSITABLE_PROPS  # backward-compat alias, kept in case anything else imports it

MOVES_PIXELS_RE = re.compile(r"(blur|drop-shadow|box-reflect)\(", re.I)

LAYER_THRESHOLD = 20  # this skill's own threshold, not a browser or spec standard


def _norm_prop(p):
    return p.strip().replace("-", "").lower()


def _to_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _meta(fields, start):
    """The three trailing Framer-locator fields of a raw line, or Nones for a pre-locator file."""
    layer = unescape_field(fields[start]) if len(fields) > start else None
    text = unescape_field(fields[start + 1]) if len(fields) > start + 1 else None
    y = parse_int_field(fields[start + 2]) if len(fields) > start + 2 else None
    return {"layer": layer, "text": text, "y": y}


def loc(row):
    """Pull just the locator keys out of a parsed row, as kwargs for common.finding()."""
    return {"layer": row.get("layer"), "text": row.get("text"), "y": row.get("y")}


def parse_raw(path):
    """Returns (header dict, {"A":[...], "R":[...], "L":[...], "F":[...], "P":[...], "X":{...}},
    scroll_count). "X" maps a caller-requested selector to its locator dict."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip()]
    header = {}
    if lines:
        for part in lines[0].split("|"):
            if "=" in part:
                k, _, v = part.partition("=")
                header[k] = v
    data = {"A": [], "R": [], "L": [], "F": [], "P": [], "X": {}}
    scroll_count = 0
    for line in lines[1:]:
        fields = line.split("|")
        tag, rest = fields[0], fields[1:]
        if tag == "A" and len(rest) >= 6:
            selector, props, composite, rate, iter_start, play_state = rest[:6]
            data["A"].append({
                **_meta(rest, 6),
                "selector": selector,
                "props": [p.strip() for p in props.split(",") if p.strip()],
                "composite": composite,
                "playback_rate": _to_float(rate),
                "iteration_start": _to_float(iter_start),
                "play_state": play_state,
            })
        elif tag == "R" and len(rest) >= 2:
            selector, props = rest[:2]
            data["R"].append({"selector": selector, **_meta(rest, 2),
                               "props": [p.strip() for p in props.split(",") if p.strip()]})
        elif tag == "L" and len(rest) >= 2:
            selector, reason = rest[:2]
            data["L"].append({"selector": selector, "reason": reason, **_meta(rest, 2)})
        elif tag == "F" and len(rest) >= 3:
            selector, kind, value = rest[:3]
            data["F"].append({"selector": selector, "kind": kind, "value": value,
                               **_meta(rest, 3)})
        elif tag == "P" and len(rest) >= 2:
            selector, position = rest[:2]
            data["P"].append({"selector": selector, "position": position, **_meta(rest, 2)})
        elif tag == "X" and len(rest) >= 2:
            data["X"][unescape_field(rest[0]) or rest[0]] = _meta(rest, 1)
        elif tag == "S" and len(rest) >= 2:
            scroll_count = int(rest[1]) if rest[1].isdigit() else 0
    return header, data, scroll_count


def check_unsupported_property(data, page):
    out = []
    for kind, severity, certainty in (("A", "high", "confirmed via the Web Animations API"),
                                       ("R", "medium", "detected via repeated inline style "
                                                        "writes, so full WAAPI context is "
                                                        "unknown")):
        for row in data[kind]:
            bad = [p for p in row["props"] if _norm_prop(p) not in ALLOWED_PROPS]
            if not bad:
                continue
            out.append(finding(
                severity=severity, category="composited", page=page, where=row["selector"],
                before=f"Animates {', '.join(row['props'])}.",
                after="Animate `transform`/`opacity` instead, or precompute the value with a "
                      "keyframe on those two properties.",
                why="Non-composited properties force layout/paint on every frame — same "
                    f"criterion as Lighthouse's `non-composited-animations` audit ({certainty}).",
                source="unsupported_property", **loc(row),
            ))
    return out


def check_filter_moves_pixels(data, page):
    animating = {r["selector"] for r in data["A"]} | {r["selector"] for r in data["R"]}
    out, seen = [], set()
    for row in data["F"]:
        if row["kind"] not in ("filter", "backdrop-filter"):
            continue
        if not MOVES_PIXELS_RE.search(row["value"]):
            continue
        if row["selector"] not in animating:
            continue
        key = (row["selector"], row["kind"])
        if key in seen:
            continue
        seen.add(key)
        out.append(finding(
            severity="medium", category="composited", page=page, where=row["selector"],
            before=f"{row['kind']}: {row['value']} on an element that is animating.",
            after="Avoid blur()/drop-shadow()/box-reflect() on an animating element; keep the "
                  "effect static and animate transform/opacity separately if possible.",
            why="blur(), drop-shadow() and box-reflect() can move or sample neighboring pixels, "
                "so Chrome can't composite them — same as Lighthouse's `filterMayMovePixels` "
                "reason.",
            source="filter_moves_pixels", **loc(row),
        ))
    return out


def check_composite_mode(data, page):
    out = []
    for row in data["A"]:
        if row["composite"] and row["composite"] != "replace":
            out.append(finding(
                severity="medium", category="composited", page=page, where=row["selector"],
                before=f"Animation composite mode is `{row['composite']}`.",
                after="Use the default `replace` composite mode unless layering keyframes on "
                      "top of each other is strictly required.",
                why="Non-`replace` composite modes aren't compositable (Lighthouse's "
                    "`nonReplaceCompositeMode`).",
                source="composite_mode", **loc(row),
            ))
    return out


def check_timing_params(data, page):
    out = []
    for row in data["A"]:
        rate, iter_start = row["playback_rate"], row["iteration_start"]
        rate_bad = rate is not None and rate != 1
        iter_bad = iter_start is not None and iter_start != 0
        if not (rate_bad or iter_bad):
            continue
        parts = []
        if rate_bad:
            parts.append(f"playbackRate={rate}")
        if iter_bad:
            parts.append(f"iterationStart={iter_start}")
        why = ("Unsupported timing parameters force main-thread animation (Lighthouse's "
               "`unsupportedTimingParameters`).")
        confidence = "heuristic"
        if rate_bad:
            why += (" Safari specifically loses hardware acceleration when `playbackRate !== "
                     "1`, as documented by Motion's performance guide.")
            confidence = "documented"
        out.append(finding(
            severity="low", category="composited", page=page, where=row["selector"],
            before=f"Animation with {', '.join(parts)}.",
            after="Keep `playbackRate` at 1 and `iterationStart` at 0; bake any rate or offset "
                  "change into the keyframes instead.",
            why=why, source="timing_params", confidence=confidence, **loc(row),
        ))
    return out


def check_incompatible_animations(data, page):
    by_selector = {}
    for row in data["A"]:
        by_selector.setdefault(row["selector"], []).append(row)
    out = []
    for selector, rows in by_selector.items():
        if len(rows) < 2:
            continue
        overlap = any(set(rows[i]["props"]) & set(rows[j]["props"])
                      for i in range(len(rows)) for j in range(i + 1, len(rows)))
        if not overlap:
            continue
        all_props = sorted({p for r in rows for p in r["props"]})
        out.append(finding(
            severity="medium", category="composited", page=page, where=selector,
            before=f"{len(rows)} animations on the same element, overlapping on: "
                   f"{', '.join(all_props)}.",
            after="Merge into a single animation, or make sure no two animations target the "
                  "same property on this element at the same time.",
            why="Lighthouse's `incompatibleAnimations`: one non-composited animation on a "
                "target can knock a composited one on the same target back to the main thread "
                "too.",
            source="incompatible_animations", **loc(rows[0]),
        ))
    return out


def check_layer_promotion(data, page):
    selectors = sorted({row["selector"] for row in data["L"]})
    if len(selectors) < LAYER_THRESHOLD:
        return []
    return [finding(
        severity="medium", category="composited", page=page, where="whole page",
        nodes=selectors[:5],
        before=f"{len(selectors)} distinct elements promoted to their own compositor layer.",
        after="Reduce how many layers are promoted at once; drop `will-change` and similar "
              "hints from elements that aren't actively animating.",
        why=f"This skill's own threshold ({LAYER_THRESHOLD}+ layers on one page, not a browser "
            "standard): every composited layer costs memory and per-frame management overhead, "
            "per web.dev's \"stick to compositor-only properties and manage layer count\" "
            "guidance.",
        source="layer_promotion",
    )]


def check_will_change_static(data, page):
    animating = {r["selector"] for r in data["A"]} | {r["selector"] for r in data["R"]}
    out, seen = [], set()
    for row in data["L"]:
        if row["reason"] != "will-change" or row["selector"] in animating:
            continue
        if row["selector"] in seen:
            continue
        seen.add(row["selector"])
        out.append(finding(
            severity="medium", category="composited", page=page, where=row["selector"],
            before="`will-change` is set but no animation (WAAPI or rAF-driven) was detected "
                   "on this element.",
            after="Remove the permanent `will-change`, or toggle it on shortly before the "
                  "change and off right after.",
            why="MDN's `will-change` guidance: it should be a short-lived hint around an "
                "actual change, not a permanent declaration in static CSS.",
            source="will_change_static", **loc(row),
        ))
    return out


def check_scroll_listener_present(scroll_count, page):
    if scroll_count <= 0:
        return []
    return [finding(
        severity="info", category="composited", page=page, where="whole page",
        before=f"{scroll_count} scroll/wheel/touchmove listener(s) detected.",
        after="No action from this alone; look at frame pacing during scroll in the runtime "
              "phase for the real signal.",
        why="Whether these listeners are passive (and so don't block scrolling) can't be "
            "determined statically once the page's own scripts have already run — this only "
            "flags that listeners exist, it is not a judgment on them.",
        source="scroll_listener_present",
    )]


def check_containment_candidate(data, page):
    total = len(data["A"]) + len(data["R"])
    if total < 3:
        return []
    return [finding(
        severity="info", category="composited", page=page, where="site-wide",
        before=f"{total} animated elements detected on this page (flat list of selectors, no "
               "DOM tree available to confirm which share a container).",
        after="Consider `contain: layout` or `content-visibility` on large repeated animated "
              "sections, where they do share a common container.",
        why="General advice, not a located finding: this data is per-element selectors, not a "
            "DOM tree, so an honest containment check isn't possible from it. See MDN's "
            "`contain` property.",
        source="containment_candidate",
    )]


def check(data, scroll_count, page):
    findings = []
    findings += check_unsupported_property(data, page)
    findings += check_filter_moves_pixels(data, page)
    findings += check_composite_mode(data, page)
    findings += check_timing_params(data, page)
    findings += check_incompatible_animations(data, page)
    findings += check_layer_promotion(data, page)
    findings += check_will_change_static(data, page)
    findings += check_scroll_listener_present(scroll_count, page)
    findings += check_containment_candidate(data, page)
    return findings


def record_platform(out_dir, platform):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "platform.json")
    payload = {"platform": platform}
    if os.path.exists(path):
        try:
            with open(path) as fh:
                existing = json.load(fh)
            if isinstance(existing, dict):
                existing.update(payload)
                payload = existing
        except Exception:
            pass
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", required=True)
    ap.add_argument("--url", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--platform", choices=["framer", "other"], default=None,
                     help="stored once per audit in <out>/platform.json for build_report.py")
    a = ap.parse_args()

    header, data, scroll_count = parse_raw(a.raw)
    findings = check(data, scroll_count, a.slug)
    path = write_findings(a.out, f"page-{a.slug}", findings)

    if a.platform:
        record_platform(a.out, a.platform)

    print(f"{len(findings)} findings -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
