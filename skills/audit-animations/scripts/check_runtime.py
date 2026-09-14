#!/usr/bin/env python3
"""Phase 2: per-page "runtime" checks against a browser-measured JSON probe file.

Input is a JSON file (not pipe-lines — this one is small and structured), produced by a
browser-side probe script owned by another task, with this shape:

    {
      "loafSupported": true,
      "longtaskSupported": true,
      "framePacing": { "p50": 16.8, "p95": 34.2, "count": 240 },
      "loaf": [
        { "duration": 87.3, "renderStart": 12.1, "styleAndLayoutStart": 45.0,
          "blockingDuration": 20.0,
          "scripts": [ { "name": "myFunction", "duration": 40.2,
                          "forcedStyleAndLayoutDuration": 15.0 } ] }
      ],
      "longtasks": [ { "duration": 62.0, "startTime": 1234.5 } ],
      "slowEvents": [ { "name": "pointerover", "duration": 210.0 } ],
      "calibration": { "idleP50": 16.7, "throttled": false },
      "styleWrites": [ { "selector": "div.hero-bg", "props": ["left", "transform"] } ]
    }

`styleWrites` comes from probe_runtime.js's own MutationObserver, run over the same multi-second
install/drain window as everything else in this file — it's the real, observed counterpart to
check_page.py's static `unsupported_property` heuristic, catching rAF-driven inline-style
animations (e.g. Framer Motion's hybrid engine) that `document.getAnimations()` never sees at
all. Category is "composited" (it's the same "which property got animated" question as
check_page.py asks), not "runtime", even though it lives in this file.

Unlike composited/safari-risk findings, these are real browser measurements (confidence
"measured") — UNLESS `calibration.throttled` is true, in which case every finding in this file
is still produced (the raw numbers are reported) but marked `status="not_verified"` instead of
`"open"`, since the measurement environment (a hidden browser pane, or a slow machine) makes
the numbers untrustworthy as a real-device signal.

Framer layer coordinates: runtime findings are measured, not collected, so they carry no DOM
node — only a `where` string. The ones whose `where` is a real CSS selector
(`runtime_non_composited_write`) are enriched afterwards from the `X` lines of the same page's
phase 3 raw file, which phase 3 produced by resolving exactly these selectors in the live page.
Pass `--layers <out>/raw/<slug>.txt`, or let it default to that path when it exists. Findings
whose `where` is not a selector ("whole page", "frame @ 12ms", "event: pointerover") keep
`layer`/`text`/`y` as null, and so do selectors phase 3 could not resolve.

Usage: check_runtime.py --json <out>/runtime/<slug>.json --slug <slug> --out <out>
       [--layers <out>/raw/<slug>.txt]
"""
import argparse, json, os, sys
from common import finding, write_findings
from check_page import COMPOSITABLE_PROPS, _norm_prop, parse_raw


def _top_script(scripts):
    if not scripts:
        return None
    return max(scripts, key=lambda s: s.get("duration", 0))


def check_loaf_frames(payload, page, status, note):
    out = []
    for entry in payload.get("loaf") or []:
        duration = entry.get("duration", 0)
        if duration <= 50:
            continue
        severity = "high" if duration > 150 else "medium"
        top = _top_script(entry.get("scripts") or [])
        if top and top.get("forcedStyleAndLayoutDuration", 0) > 0:
            after = f"Fix layout thrashing in `{top.get('name', 'unknown')}`."
        else:
            after = "Reduce render work in this frame."
        out.append(finding(
            severity=severity, category="runtime", page=page,
            where=f"frame @ {entry.get('renderStart')}ms",
            before=(f"{duration}ms frame (renderStart={entry.get('renderStart')}, "
                    f"styleAndLayoutStart={entry.get('styleAndLayoutStart')}, "
                    f"blockingDuration={entry.get('blockingDuration')})."),
            after=after,
            why="A Long Animation Frame over 50ms is Chrome's own definition of a janky "
                "frame." + note,
            source="loaf_frames", confidence="measured", status=status,
        ))
    return out


def check_long_tasks(payload, page, status, note):
    tasks = payload.get("longtasks") or []
    if not tasks:
        return []
    total = sum(t.get("duration", 0) for t in tasks)
    return [finding(
        severity="medium", category="runtime", page=page, where="whole page",
        before=f"{len(tasks)} long tasks, total {total} ms.",
        after="Break up long synchronous work into smaller chunks that yield to the main "
              "thread.",
        why="The Long Tasks API is the main-thread-blocked signal used here; note this API is "
            "Chromium-only (not Safari/Firefox), so it is a Chrome-side signal only." + note,
        source="long_tasks", confidence="measured", status=status,
    )]


def check_frame_pacing(payload, page, status, note):
    pacing = payload.get("framePacing") or {}
    p95 = pacing.get("p95")
    if p95 is None or p95 <= 20:
        return []
    return [finding(
        severity="medium", category="runtime", page=page, where="whole page",
        before=f"p95 frame interval {p95}ms during scroll.",
        after="Target ~16.7ms (60fps).",
        why="This is the actual user-facing jank measurement; Apple's own target for smooth "
            "motion is also ~16.67ms per frame (60fps)." + note,
        source="frame_pacing", confidence="measured", status=status,
    )]


def check_slow_events(payload, page, status, note):
    out = []
    for ev in payload.get("slowEvents") or []:
        duration = ev.get("duration", 0)
        if duration <= 200:
            continue
        out.append(finding(
            severity="medium", category="runtime", page=page,
            where=f"event: {ev.get('name')}",
            before=f"`{ev.get('name')}` handler took {duration}ms.",
            after="Reduce work in this event handler, or defer non-critical work off the "
                  "interaction's critical path.",
            why="Interaction to Next Paint (INP) uses a 200ms threshold for a poor "
                "interaction; this handler alone exceeds it." + note,
            source="slow_events", confidence="measured", status=status,
        ))
    return out


def check_non_composited_write(payload, page, status, note):
    out = []
    for entry in payload.get("styleWrites") or []:
        props = entry.get("props") or []
        bad = [p for p in props if _norm_prop(p) not in COMPOSITABLE_PROPS]
        if not bad:
            continue
        out.append(finding(
            severity="high", category="composited", page=page,
            where=entry.get("selector", ""),
            before=f"Animates {', '.join(props)}.",
            after="Animate `transform`/`opacity` instead.",
            why=("Observed live during the runtime trace: this element's inline style was "
                 f"rewritten every frame for {', '.join(props)}, outside the compositor-safe "
                 "set — this is the rAF-driven pattern `document.getAnimations()` cannot see "
                 "(e.g. Framer Motion's hybrid engine), confirmed here by direct observation "
                 "rather than inferred." + note),
            source="runtime_non_composited_write", confidence="measured", status=status,
        ))
    return out


def load_layers(path):
    """Read the `X` lines of a phase 3 raw file: selector -> {layer, text, y}."""
    if not path or not os.path.exists(path):
        return {}
    try:
        _, data, _ = parse_raw(path)
    except Exception:
        return {}
    return data.get("X") or {}


def apply_layers(findings, layers):
    """Fill layer/text/y on every finding whose `where` matches a resolved selector. Returns the
    number of findings enriched, so the caller can report what the lookup actually covered."""
    if not layers:
        return 0
    n = 0
    for f in findings:
        meta = layers.get(f.get("where"))
        if not meta:
            continue
        f["layer"], f["text"], f["y"] = meta["layer"], meta["text"], meta["y"]
        n += 1
    return n


def check_api_support(payload, page, status, note):
    if payload.get("loafSupported", True):
        return []
    return [finding(
        severity="info", category="runtime", page=page, where="whole page",
        before="This browser does not support the Long Animation Frames API.",
        after="No action; runtime findings for this page rely on the coarser Long Tasks API "
              "only.",
        why="Long Animation Frames give per-script attribution inside a slow frame; without "
            "it, only aggregate Long Tasks durations are available." + note,
        source="loaf_unsupported", confidence="measured", status=status,
    )]


def check(payload, page):
    throttled = bool((payload.get("calibration") or {}).get("throttled"))
    status = "not_verified" if throttled else "open"
    note = (" The measurement environment was throttled (a hidden browser pane, or a slow "
            "machine) during this run, so this number is not trustworthy as a real-device "
            "signal." if throttled else "")

    findings = []
    findings += check_loaf_frames(payload, page, status, note)
    findings += check_long_tasks(payload, page, status, note)
    findings += check_frame_pacing(payload, page, status, note)
    findings += check_slow_events(payload, page, status, note)
    findings += check_non_composited_write(payload, page, status, note)
    findings += check_api_support(payload, page, status, note)
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--layers", default=None,
                     help="phase 3 raw file whose X lines resolve this page's selectors to "
                          "Framer layer paths (default: <out>/raw/<slug>.txt if it exists)")
    a = ap.parse_args()

    with open(a.json, encoding="utf-8", errors="replace") as fh:
        payload = json.load(fh)
    findings = check(payload, a.slug)

    layers_path = a.layers or os.path.join(a.out, "raw", f"{a.slug}.txt")
    enriched = apply_layers(findings, load_layers(layers_path))

    path = write_findings(a.out, f"runtime-{a.slug}", findings)
    print(f"{len(findings)} findings ({enriched} with a layer path) -> {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
