#!/usr/bin/env python3
"""Phase 6 (optional) "Ver en la web": paint a page's findings on top of the live site.

Reads the merged `report.json` (built by build_report.py), keeps only the findings for one
page whose `where` is a real element selector (drops "whole page"/"site-wide" page-level
findings and runtime findings located by time — `frame @ 12ms` — or event instead of by
element), groups them by selector so one element gets one box even if several checks fired on
it, and prints a single self-contained JS snippet to stdout.

The snippet embeds its data as a JS literal instead of fetching report.json at runtime: the
browser pane this is meant to run in (the built-in Browser pane / javascript_tool) cannot fetch
localhost paths from the page's own origin, since the audited site is a different origin than
the local audit folder. So the whole point of this script is to bake the (already filtered,
already small) data straight into the JS text.

Paste the printed snippet into `javascript_tool` after navigating to the page it was generated
for — selectors are page-specific and will mostly fail to resolve on the wrong page. The
snippet is idempotent (running it again replaces the previous overlay) and returns
`{painted, unresolved, high, medium}` as its last expression, which javascript_tool shows back.

This is a QA/demo aid, not one of the audit's own checks — it paints report.json findings, it
doesn't produce new ones, so it writes nothing under findings/ and build_report.py never reads
its output.

Usage:
    python3 overlay.py --out <audit-dir> --page <slug> [--min-severity medium] [--max 60] > overlay.js
"""
import argparse, json, os, sys
from common import SEVERITY_ORDER

COLORS = {
    "critical": "#eb5757",
    "high": "#eb5757",
    "medium": "#d99a00",
    "low": "#4c9cff",
    "info": "#4c9cff",
}

# where values that name a moment in time or the whole page rather than one DOM element —
# never worth (or able to) draw a box for.
NON_ELEMENT_WHERE = {"whole page", "site-wide"}


def is_element_selector(where):
    if not where:
        return False
    if where in NON_ELEMENT_WHERE:
        return False
    if where.startswith("frame @") or where.startswith("event:"):
        return False
    return True


def short_label(finding):
    """Last segment of the Framer layer path, or a trimmed selector when there is none."""
    layer = finding.get("layer")
    if layer:
        last = layer.split(" › ")[-1].strip()
        if last:
            return last
    where = finding["where"]
    # last simple segment of the selector, trimmed — good enough as a fallback label when
    # Framer published no data-framer-name for this element.
    last = where.split(">")[-1].strip()
    if len(last) > 28:
        last = last[:27] + "…"
    return last


def group_findings(findings, min_severity, max_boxes):
    threshold = SEVERITY_ORDER[min_severity]
    kept = [f for f in findings if is_element_selector(f.get("where"))
            and SEVERITY_ORDER[f["severity"]] <= threshold]

    groups = {}
    order = []  # selectors in first-seen JSON order, for priority sorting below
    for f in kept:
        sel = f["where"]
        if sel not in groups:
            groups[sel] = []
            order.append(sel)
        groups[sel].append(f)

    def best_severity(items):
        return min(SEVERITY_ORDER[i["severity"]] for i in items)

    # Priority: every selector whose best finding is high/critical first (JSON order), then
    # every selector whose best finding is medium (JSON order); low/info only appear here at
    # all if --min-severity let them through, and sort after medium.
    def sort_key(sel):
        return (best_severity(groups[sel]), order.index(sel))

    ordered = sorted(order, key=sort_key)[:max_boxes]

    boxes = []
    for sel in ordered:
        items = sorted(groups[sel], key=lambda i: SEVERITY_ORDER[i["severity"]])
        top = items[0]
        sources = []
        for i in items:
            if i["source"] not in sources:
                sources.append(i["source"])
        boxes.append({
            "selector": sel,
            "severity": top["severity"],
            "color": COLORS.get(top["severity"], COLORS["low"]),
            "label": short_label(top),
            "checks": sources[:3],
            "count": len(items),
        })
    return boxes


# The runtime half: one self-contained JS expression. Kept as a plain string (not an f-string)
# so its many `${...}` template literals don't collide with Python formatting — the one Python
# substitution (the embedded data array) is done with a plain str.replace on a unique marker.
OVERLAY_JS = r"""
(() => {
  const DATA = __BEIZER_DATA__;
  const ROOT_ID = "beizer-overlay-root";
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const prev = document.getElementById(ROOT_ID);
  if (prev) prev.remove();
  if (window.__beizerOverlayCleanup) {
    try { window.__beizerOverlayCleanup(); } catch (e) {}
  }

  const root = document.createElement("div");
  root.id = ROOT_ID;
  document.body.appendChild(root);

  const style = document.createElement("style");
  style.textContent = `
    #${ROOT_ID} { position: static; }
    #${ROOT_ID} .beizer-box {
      position: absolute; pointer-events: none; z-index: 2147483000;
      border-width: 2px; border-style: solid; box-sizing: border-box;
    }
    #${ROOT_ID} .beizer-label {
      position: absolute; top: 0; left: 0; transform: translateY(-100%);
      font: 11px/1.4 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      color: #fff; padding: 1px 5px; white-space: nowrap; border-radius: 2px 2px 0 0;
    }
    #${ROOT_ID} .beizer-panel {
      position: fixed; top: 12px; right: 12px; z-index: 2147483001;
      background: #1c1c1e; color: #f2f2f2; font: 12px/1.5 -apple-system, system-ui, sans-serif;
      padding: 10px 12px; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,.35);
      pointer-events: auto; min-width: 190px;
    }
    #${ROOT_ID} .beizer-panel h4 { margin: 0 0 6px; font-size: 12px; font-weight: 600; }
    #${ROOT_ID} .beizer-row { display: flex; align-items: center; gap: 6px; margin: 2px 0; }
    #${ROOT_ID} .beizer-swatch { width: 10px; height: 10px; border-radius: 2px; flex: none; }
    #${ROOT_ID} .beizer-btns { margin-top: 8px; display: flex; gap: 6px; }
    #${ROOT_ID} button.beizer-btn {
      font: 11px ui-monospace, monospace; padding: 4px 8px; border-radius: 5px; border: 0;
      cursor: pointer; pointer-events: auto;
    }
    #${ROOT_ID} button.beizer-next { background: #eb5757; color: #fff; }
    #${ROOT_ID} button.beizer-close { background: #3a3a3c; color: #f2f2f2; }
    @keyframes beizer-blink { 0%,100% { outline-color: transparent; } 50% { outline-color: #fff; } }
    #${ROOT_ID} .beizer-blink {
      animation: beizer-blink 0.35s ease-in-out 3;
      outline: 3px solid transparent; outline-offset: 2px;
    }
  `;
  root.appendChild(style);

  const boxLayer = document.createElement("div");
  root.appendChild(boxLayer);

  const resolved = []; // { el, box, sev }
  const unresolved = [];
  let high = 0, medium = 0;

  for (const f of DATA) {
    let el = null;
    try {
      el = document.querySelector(f.selector);
    } catch (e) {
      unresolved.push({ selector: f.selector, reason: "invalid selector (" + e.message + ")" });
      continue;
    }
    if (!el) {
      unresolved.push({ selector: f.selector, reason: "not found on this page" });
      continue;
    }
    if (f.severity === "high" || f.severity === "critical") high++;
    else if (f.severity === "medium") medium++;

    const box = document.createElement("div");
    box.className = "beizer-box";
    box.style.borderColor = f.color;
    const label = document.createElement("div");
    label.className = "beizer-label";
    label.style.background = f.color;
    label.textContent = f.label + (f.checks && f.checks[0] ? " · " + f.checks[0] : "")
      + (f.count > 1 ? " (×" + f.count + ")" : "");
    box.appendChild(label);
    boxLayer.appendChild(box);
    resolved.push({ el, box, sev: f.severity });
  }

  function place() {
    for (const r of resolved) {
      const rect = r.el.getBoundingClientRect();
      const top = rect.top + window.scrollY;
      const left = rect.left + window.scrollX;
      r.box.style.top = top + "px";
      r.box.style.left = left + "px";
      r.box.style.width = Math.max(rect.width, 2) + "px";
      r.box.style.height = Math.max(rect.height, 2) + "px";
    }
  }
  place();

  let rafPending = false;
  function scheduleReplace() {
    if (rafPending) return;
    rafPending = true;
    requestAnimationFrame(() => { rafPending = false; place(); });
  }
  window.addEventListener("resize", scheduleReplace);
  window.addEventListener("scroll", scheduleReplace, { passive: true });

  // Legend + controls panel
  const panel = document.createElement("div");
  panel.className = "beizer-panel";
  panel.innerHTML = `
    <h4>Beizer &middot; animation audit</h4>
    <div class="beizer-row"><span class="beizer-swatch" style="background:#eb5757"></span>high/critical: ${high}</div>
    <div class="beizer-row"><span class="beizer-swatch" style="background:#d99a00"></span>medium: ${medium}</div>
    <div class="beizer-row"><span class="beizer-swatch" style="background:#4c9cff"></span>low/info</div>
    <div class="beizer-row">unresolved: ${unresolved.length}</div>
    <div class="beizer-btns">
      <button type="button" class="beizer-btn beizer-next">Siguiente ▶</button>
      <button type="button" class="beizer-btn beizer-close">✕</button>
    </div>
  `;
  root.appendChild(panel);

  const reds = resolved.filter(r => r.sev === "high" || r.sev === "critical");
  let redIdx = -1;
  function goNext() {
    if (!reds.length) return;
    redIdx = (redIdx + 1) % reds.length;
    const target = reds[redIdx];
    target.box.scrollIntoView({ behavior: reducedMotion ? "auto" : "smooth", block: "center" });
    if (!reducedMotion) {
      target.box.classList.remove("beizer-blink");
      // force reflow so re-adding the class restarts the animation on repeated clicks
      void target.box.offsetWidth;
      target.box.classList.add("beizer-blink");
    }
  }
  panel.querySelector(".beizer-next").addEventListener("click", goNext);
  window.__beizerOverlayNext = goNext;

  function cleanup() {
    window.removeEventListener("resize", scheduleReplace);
    window.removeEventListener("scroll", scheduleReplace);
    delete window.__beizerOverlayNext;
    delete window.__beizerOverlayCleanup;
    const r = document.getElementById(ROOT_ID);
    if (r) r.remove();
  }
  panel.querySelector(".beizer-close").addEventListener("click", cleanup);
  window.__beizerOverlayCleanup = cleanup;

  return { painted: resolved.length, unresolved: unresolved.length, high, medium, unresolvedDetail: unresolved };
})()
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="audit working folder (has report.json)")
    ap.add_argument("--page", required=True, help="exact page slug, e.g. home or home.mobile")
    ap.add_argument("--min-severity", default="medium", choices=list(SEVERITY_ORDER))
    ap.add_argument("--max", type=int, default=60, help="max boxes (selectors) to paint")
    a = ap.parse_args()

    report_path = os.path.join(a.out, "report.json")
    with open(report_path) as f:
        report = json.load(f)
    all_findings = [f for f in report["findings"] if f["page"] == a.page]
    if not all_findings:
        print(f"No findings for page '{a.page}' in {report_path}. Known pages: "
              + ", ".join(sorted({f['page'] for f in report['findings']})), file=sys.stderr)
        sys.exit(1)

    boxes = group_findings(all_findings, a.min_severity, a.max)
    if not boxes:
        print(f"No element-level findings at >= {a.min_severity} for page '{a.page}'.",
              file=sys.stderr)
        sys.exit(1)

    data_json = json.dumps(boxes, ensure_ascii=False)
    print(OVERLAY_JS.replace("__BEIZER_DATA__", data_json).strip())


if __name__ == "__main__":
    main()
