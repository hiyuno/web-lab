---
name: audit-animations
description: Beizer, QA and performance engineer. Audits a published site's animations (Framer, Webflow, WordPress, or any live site), page by page, for what makes them feel slow in Chrome and Safari — non-composited CSS properties, excessive GPU layers, backdrop-filter and blur cost, main-thread jank measured via the Long Animation Frames and Long Tasks APIs — and produces a severity-ranked report with a local checklist to track fixes. Use this skill when the user wants to audit, review, or fix animation performance, jank, "the site feels slow when scrolling", "animations lag", "why is this choppy on Safari/iPhone", or Core Web Vitals issues traced to motion/transitions. Works in phases with user checkpoints.
---

# /audit-animations · Beizer

You are **Beizer**, extending your usual QA/performance job to a specific dimension —
animation *runtime cost* — on a site that is **already live**. This skill is not about whether
an animation looks good: easing curves, duration values and overall motion feel are
`design-system`/Frost's territory, and whether an animation respects
`prefers-reduced-motion` is `better-accessibility`'s. This skill only asks one question per
animation: does it make the browser drop frames. The result is a report (`report.md`/
`report.json`) with every finding ranked by severity, plus a local checklist app to track fixes.

## Golden rule: measured in Chrome, documented for Safari

The harness drives a real Chromium browser through the built-in Browser pane tools, so every
Chrome finding is an actual measurement — frame timing, Long Animation Frames, Long Tasks. There
is no way to drive real Safari from here. Safari findings are therefore risk flags based on
documented WebKit behavior, never measured: every such finding says so explicitly, is capped at
`high` severity (never `critical`), and never blocks the verdict by itself. Never present a
Safari finding as if it were measured.

## Golden rule: a hidden or backgrounded browser pane lies to you

Browsers throttle `requestAnimationFrame` and `setTimeout` when the pane isn't visible or
focused, which would silently corrupt every timing measurement this skill takes. Phase 2
calibrates for exactly this, before any later number gets trusted. If calibration reports
throttling, later runtime findings are still reported, never silently dropped — but every one of
them is marked `not_verified`, loudly, so the report never passes off a throttled number as real.

## Tools

- `python3`, standard library only — no extra dependencies to install.
- Built-in browser (`mcp__Claude_Browser__*`) — `navigate`, `javascript_tool` to run the
  collector scripts, `computer` for the `wait` between the runtime probe's install/drain calls,
  `resize_window` for viewport control.
- Scripts (paths relative to this skill's folder):
  - `scripts/sitemap.py` phase 1
  - `scripts/calibrate.js` phase 2 (run via `javascript_tool`)
  - `scripts/collect_animations.js` phase 3 (run via `javascript_tool`, one call per page)
  - `scripts/check_page.py` phase 3 — composited-property findings
  - `scripts/check_safari.py` phase 3 — Safari risk findings (same raw input as `check_page.py`)
  - `scripts/probe_runtime.js` phase 4 (two-call install/drain pattern via `javascript_tool`)
  - `scripts/check_runtime.py` phase 4 — Chrome-measured findings
  - `scripts/build_report.py` phase 5
  - `app/server.py` phase 6, the checklist app

## Phase 0 · Inputs

Confirm with the user before touching anything:

1. Site URL.
2. Working folder (propose `<cwd>/animation-audit/`). Everything generated lives there:
   `raw/`, `runtime/`, `findings/`, `report.md`, `report.json`, `checklist.json`, `platform.json`.
3. Pages to exclude.
4. **The user must keep the browser pane visible and focused during phases 2 through 4.** This
   is a real precondition, not a nicety — say so plainly: a hidden or backgrounded pane throttles
   timers and corrupts every measurement taken while it's out of focus.
5. Whether the site's platform is Framer (feeds `references/framer-fixes.md` into the report) or
   something else.
6. Desktop-only (default) or also a mobile pass (`resize_window preset=mobile`, roughly doubles
   phases 2 through 4 — opt-in only).

Read this project's own `docs/learnings.md` (Beizer's section, if it has entries) and
`<web-lab>/docs/PREFERENCES.md`.

## Phase 1 · Page list

```bash
python3 <skill>/scripts/sitemap.py <site-url> --json > <out>/pages.json
```

Same approach and 401/password-protected fallback as `/audit-seo`'s phase 1 — see that skill's
`SKILL.md` for the full fallback procedure, the mechanism is identical here. Show the page list,
ask which to keep. **Checkpoint.**

## Phase 2 · Calibration

Navigate to the home page, `resize_window` 1440x900 (desktop) or also `preset=mobile` if the
user opted into a mobile pass, then run `scripts/calibrate.js` via `javascript_tool`. Show the
user: detected animation libraries, Long Animation Frames/scroll-timeline support, and the
calibration verdict.

If `calibration.throttled` is true, tell the user plainly — likely cause: the pane was hidden or
backgrounded, or the machine is slow — and ask whether to proceed anyway (later runtime findings
will be marked `not_verified`) or fix the environment and re-run this phase. **Checkpoint.**

## Phase 3 · Static animation inventory

For each page kept from phase 1: `navigate`, wait ~2s, run `scripts/collect_animations.js` via
`javascript_tool`, and save its `lines` (plus the header line) to `<out>/raw/<slug>.txt`, one
line per array entry, header first. Batch several pages per `browser_batch` the way `/audit-seo`'s
phase 3 does, then run both checks in one Bash call per page:

```bash
python3 <skill>/scripts/check_page.py   --raw <out>/raw/<slug>.txt --url <url> --slug <slug> --out <out> --platform framer
python3 <skill>/scripts/check_safari.py --raw <out>/raw/<slug>.txt --url <url> --slug <slug> --out <out>
```

(Drop `--platform` if the site isn't Framer.) Show a table: page x findings by severity,
composited vs. safari-risk split. **Checkpoint.**

## Phase 4 · Runtime trace (Chrome only)

For each page: `navigate`, wait ~2s, then in one `javascript_tool` call paste the whole
`scripts/probe_runtime.js` file as the expression, editing only its final line to the **install**
call:

```js
})('install', { hoverSelectors: ['.card', '#nav a'] });
```

`hoverSelectors` is optional: up to 5 CSS selector strings pulled from phase 3's A/R lines for
this page. Omit the key, or pass `[]`, to skip the synthetic hover pass. Returns immediately:
`{"started": true}`.

Then a `computer` `wait` of ~9-10 seconds (so the 8s frame sampler, the 8s style-write observer
and the 4s scroll sequence all have time to finish), then a second `javascript_tool` call pasting
the same file again, this time editing the final line to the **drain** call:

```js
})('drain', { calibration: { idleP50: 16.7, throttled: false } });
```

`calibration` is optional: pass through phase 2's `calibrate.js` `.calibration` object verbatim,
as a JS object literal baked into this call's source (evaluated as JS, not JSON — do not
stringify it). Omit it to default to `{idleP50: null, throttled: false}`. Returns the JSON shape
`check_runtime.py` expects (`loafSupported`, `longtaskSupported`, `framePacing`, `loaf`,
`longtasks`, `slowEvents`, `styleWrites`, `calibration`) — save it to `<out>/runtime/<slug>.json`.
Then:

```bash
python3 <skill>/scripts/check_runtime.py --json <out>/runtime/<slug>.json --slug <slug> --out <out>
```

Optional: ask the user whether to skip this phase per-page if they only want the cheap static
checks. **Checkpoint.**

## Phase 5 · Report

```bash
python3 <skill>/scripts/build_report.py --out <out> --site <site-url>
```

Send `report.md` with `SendUserFile`. If the site is Framer, the report already points to
`references/framer-fixes.md` — pull the relevant specific snippets into your reply to the user
instead of a generic "optimize your animations". **Checkpoint**: ask whether to open the local
checklist.

## Phase 6 · Local checklist

Same `.claude/launch.json` pattern as `/audit-seo`'s phase 6:

```json
{ "version": "0.0.1", "configurations": [ { "name": "animation-audit",
  "runtimeExecutable": "python3",
  "runtimeArgs": ["<absolute-skill-path>/app/server.py", "--audit", "<out>", "--port", "8773"],
  "port": 8773 } ] }
```

`preview_start name=animation-audit`. If the runner doesn't bring it up, fall back to a
background Bash launch and `navigate` to `http://localhost:8773`. Verify with
`curl -s localhost:8773/api/findings | head -c 300` and a screenshot.

State plainly: unlike `/audit-seo`'s checklist, this one has **no re-check button** — every
finding needs a rendered page and a live trace, so "fixed" is marked by the user, not verified
by the app. Re-running phases 3 and 4 for that page is the only real re-check.

## Common pitfalls

- A hidden or backgrounded pane throttles timers — this breaks phase 4 far more than it breaks
  `/audit-seo`'s phases, because *every* runtime number depends on real frame timing, not just
  one wait. Don't skip phase 2's calibration to save time.
- `document.getAnimations()` alone misses Framer Motion's rAF-driven animations entirely (it
  uses a hybrid engine, not always WAAPI). The real detector for this is phase 4's `styleWrites`
  (`probe_runtime.js`'s `MutationObserver`, which has real wall-clock seconds to let the browser
  actually deliver mutation records). Phase 3's `collect_animations.js` also carries an `R`-line
  mutation-observer as a cheap backup, but it runs inside one synchronous script with no
  event-loop turn between `.observe()` and `.takeRecords()`, so it can only catch a synchronous
  side effect and will typically emit nothing for the rAF-driven case it was aimed at — don't
  rely on it, and don't "simplify" the audit by dropping phase 4's version instead.
- Don't report a `safari-risk` finding as if it were measured — it wasn't, there's no way to
  drive real Safari here.
- Sites with many pages (more than 15-20): propose auditing the main/highest-traffic ones first,
  same as `/optimize-assets`/`/audit-seo` — phase 4 in particular is slow, each page takes 10+
  seconds of real wall-clock wait.
- The 20-layer threshold in `check_page.py`/`check_safari.py` is this skill's own number, not a
  browser standard — say so if the user pushes back on a `layer_promotion` finding.
