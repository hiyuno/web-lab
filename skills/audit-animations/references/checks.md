# Checks and criteria

Every check cites its source script (matches `finding.source` in `findings/*.json`) so a
disagreement can be traced back to logic, not vibes.

## Locating a finding: Framer layer path, not CSS selector

Every finding carries three locator fields alongside its `where` selector: `layer`, the
`data-framer-name` path of the element and its ancestors joined by " › " (outermost first, at
most 6 levels, consecutive duplicates collapsed), `text`, the first 40 characters of its own or
its nearest ancestor's text, and `y`, its absolute vertical position in the page. Framer emits
`data-framer-name` on every published layer with exactly the name shown in the editor's Layers
panel, so this path is the only address an author can act on — the published class names
(`div.framer-1bbl5cr`) appear nowhere in the editor. To find a flagged animation, press **Cmd+F
in the Layers panel** and search the last name of the path, then confirm with the quoted text
and the `↓ px` offset; the CSS selector stays in a secondary column for devtools.

`layer` is null for page-level findings (`whole page`, `site-wide` — no single element to name),
for elements Framer published without a layer name, and for runtime findings located by time or
event (`frame @ 12ms`, `event: pointerover`). `check_runtime.py` fills the locator on the
findings it can — those whose `where` is a real selector — from the `X` lines of the same page's
phase 3 raw file, which `collect_animations.js` produces when it is given `resolveSelectors`.

`where` itself is capped at 90 characters (ending in `…` past that) so `report.json` stays a
sane size at 1000+ findings — `scripts/overlay.py` ("Ver en la web") relies on `where` as a
live `document.querySelector` argument, so a truncated one is a real, expected cause of an
`unresolved` box there, not a bug in that script.

## Composited

| Check | Script | Criterion | Why |
|---|---|---|---|
| Non-composited property animated (`unsupportedCSSProperty`) | `check_page.unsupported_property` | Animation targets a property other than `transform`, `opacity`, `filter`, `backdrop-filter`, or `clip-path` (e.g. `width`, `height`, `top`, `left`, `margin`, `background-position`, `box-shadow`) | Lighthouse's `non-composited-animations` audit flags exactly this named failure reason: the browser cannot run the animation on the compositor thread, so every frame requires a main-thread layout or paint |
| `filterMayMovePixels` | `check_page.filter_moves_pixels` | `filter`/`backdrop-filter` animation includes a value that can move pixels outside the element's original bounds (`blur()`, `drop-shadow()`, `box-reflect()`) | Named failure reason in Lighthouse's `non-composited-animations` audit — forces a repaint instead of a pure compositor step |
| `nonReplaceCompositeMode` | `check_page.composite_mode` | Web Animations API animation sets `composite` to something other than `"replace"` | Named failure reason in Lighthouse's `non-composited-animations` audit |
| `unsupportedTimingParameters` | `check_page.timing_params` | Animation uses a `playbackRate` other than 1, or a fractional `iterationStart` | Named failure reason in Lighthouse's `non-composited-animations` audit; a non-default `playbackRate` also loses hardware acceleration on Safari specifically (Motion's performance guide) |
| `incompatibleAnimations` | `check_page.incompatible_animations` | Two animations on the same element target overlapping properties | Named failure reason in Lighthouse's `non-composited-animations` audit |
| Layer count over threshold | `check_page.layer_promotion` | More than 20 elements promoted to their own GPU layer on one page (`will-change`, `transform: translateZ`, etc.) — 20 is this skill's own threshold, not a browser standard | web.dev's layer-count guidance: each layer costs GPU memory and composite time; too many degrades the exact performance layers exist to buy |
| `will-change` left on indefinitely | `check_page.will_change_static` | `will-change` set on an element with no matching animation found on it | MDN's `will-change` guidance: it's a hint for an upcoming change, not a permanent promotion switch — misuse wastes memory on a layer that's never animated |
| Scroll/wheel/touch listener present | `check_page.scroll_listener_present` | A scroll-driven handler is detected on the page | Informational only — whether it's registered `passive` can't be determined from page-context JS after the page's own scripts already ran; the real signal is phase 4's frame pacing during scroll, not this static check |
| `contain`/`content-visibility` candidate | `check_page.containment_candidate` | Page has several animated elements and no structural way to verify containment from a flat element list | General, page-level advice (not a located finding) to consider `contain: layout`/`content-visibility` on large repeated animated sections — MDN's `contain` property: without it, a layout or paint change in one instance can force the browser to recheck siblings |
| Non-composited property animated, observed live | `check_runtime.runtime_non_composited_write` | A `styleWrites` entry from the phase 4 runtime trace (an element whose inline `style` was repeatedly rewritten during the 8s trace, captured by `probe_runtime.js`'s `MutationObserver`) names a property outside `COMPOSITABLE_PROPS` (the same allowlist `check_page.unsupported_property` uses, imported from `check_page.py` so the two can't drift apart) | This is the *observed* counterpart to `unsupported_property`: Framer Motion (and similar hybrid-engine libraries) drive animations via `requestAnimationFrame` writing inline styles directly, which `document.getAnimations()` cannot see at all. A `MutationObserver` running during phase 4's real multi-second trace is the only place in this skill's design that can actually catch it — phase 3's `collect_animations.js` attempts the same idea synchronously (see the "Runtime" note below), but browsers only deliver mutation records, rAF callbacks and dispatched events once the call stack is empty, which never happens inside one synchronous script, so that attempt almost never fires. Reported at `high` severity and `confidence: measured` (stronger than the static check's heuristic rows) because this is a direct observation, not an inference from a WAAPI object. Category is `composited` (it's the same question as `unsupported_property`, just answered differently) even though the script that produces it is `check_runtime.py` — see the cross-reference in the Runtime table below |

Lighthouse's `non-composited-animations` audit also names `transformDependsBoxSize` (a percentage/box-relative `transform` value) as a failure reason; this skill does not implement it as a separate check — it isn't reliably detectable from `getKeyframes()` output alone without re-deriving box size per keyframe, so it's left out rather than faked. If it turns out to matter in practice, it belongs next to `check_page.unsupported_property`.

## Runtime (Chrome-measured)

Everything below is measured by `probe_runtime.js`'s install/drain pair over a real multi-second
window, and checked by `check_runtime.py`. `runtime_non_composited_write` is measured the same
way, but is filed in the Composited table above because its `finding.category` is `"composited"`,
not `"runtime"` — it answers "which property got animated", not "how much did the main thread
jank".

| Check | Script | Criterion | Why |
|---|---|---|---|
| Long Animation Frame during the traced interaction | `check_runtime.loaf_frames` | A frame reported by the Long Animation Frames API exceeds 50ms of render/style/layout work while the probe was active; attribution to the specific script/handler is included in the same finding when Chrome reports it | Chrome for Developers' LoAF documentation: LoAF frames are the direct browser-native signal for jank-causing frames, with per-script attribution built in |
| Long Task during the traced interaction | `check_runtime.long_tasks` | A `PerformanceLongTaskTiming` entry exceeds 50ms during the install-to-drain window | Long Tasks API: the older, broader-browser-support fallback signal for main-thread blocking, paired with LoAF rather than replacing it |
| Frame pacing irregular | `check_runtime.frame_pacing` | Measured frame deltas during a hover/scroll interaction show high variance relative to the display's expected frame interval | Irregular pacing is what a user perceives as "choppy" even when no single frame crosses the LoAF threshold |
| Interaction latency over threshold | `check_runtime.slow_events` | Event timing entry (pointerdown/hover-triggered handler) shows processing + presentation delay above 200ms | INP's own "needs improvement" threshold, applied to the animation-triggering interaction specifically, not the whole page |
| Long Animation Frames API unsupported | `check_runtime.loaf_unsupported` | The browser driving the audit doesn't support `PerformanceObserver` for `long-animation-frame` | Informational — runtime findings then rely on the coarser Long Tasks API only; not a defect in the audited site |

## Safari risk (documented, not measured)

| Check | Script | Criterion | Why |
|---|---|---|---|
| `backdrop-filter` on an animated element | `check_safari.backdrop_filter_animated` | `backdrop-filter` present on an element that is itself animating | WebKit's own blog post introducing `backdrop-filter` describes it as one of the most expensive filter operations to keep live every frame |
| `will-change: backdrop-filter` | `check_safari.will_change_backdrop` | `will-change` explicitly names `backdrop-filter` | Lower confidence than the other rows here — based on scattered reports of layer churn on iOS, not official WebKit documentation; reported at `heuristic` confidence, not `documented` |
| Blur radius above Framer's own guidance | `check_safari.blur_radius_large` | `filter: blur()` or `backdrop-filter: blur()` radius ≥ 10px | Framer's own site-optimization help page: keep blur below 10px; above that, flatten to an image instead of a live effect |
| `mix-blend-mode` combined with `filter` | `check_safari.blend_mode_with_filter` | Same element combines `mix-blend-mode` with `filter`/`backdrop-filter` | Documented WebKit bug: this combination has a history of incorrect or unstable compositing behavior on Safari |
| `position: fixed`/`sticky` alongside a `filter`-applying element | `check_safari.fixed_with_filter_ancestor` | The page has both a `fixed`/`sticky` element and a `filter`/`backdrop-filter` element (ancestor relationship not verifiable from this data, so reported as a page-level possibility, not a confirmed match) | `filter` creates a new stacking/containing-block context in WebKit that can silently break `fixed`/`sticky` positioning on a real descendant — a correctness issue as much as a performance one |
| `playbackRate` changed on a running animation | `check_safari.playback_rate_altered` | Animation's `playbackRate` differs from 1 | Motion's own performance guide: a non-default `playbackRate` can drop an animation out of hardware-accelerated handling on WebKit |
| Layer budget on Safari | `check_safari.layer_budget_safari` | Same 20-layer threshold as the Chrome composited check, reported separately for Safari | **Unconfirmed folklore, not documented fact** — commonly repeated that Safari's compositor tolerates fewer simultaneous layers than Chrome's before falling back to software compositing, but no WebKit source confirms a specific number. Reported at low confidence; never upgrade this row's certainty in the write-up |

## Calibration notes

- This skill has no CDP access, so it doesn't read Chrome's own compositor verdict — it
  reimplements the property-allowlist heuristic from Lighthouse's `non-composited-animations`
  audit by inspecting computed styles and animation targets directly. A disagreement with
  Lighthouse's own run of the audit should be resolved in Lighthouse's favor.
- Runtime findings come from a single device with no CPU throttling applied. A fast Mac can
  hide jank that a mid-range phone would show plainly — that's why every runtime finding is
  paired with its composited-category root cause in the report: the composited finding is the
  one that holds regardless of the machine running it.
- Performance is not aesthetics and is not accessibility. Whether an animation's easing or
  duration looks right lives in `design-system`/Frost; whether it respects
  `prefers-reduced-motion` lives in `better-accessibility`. This skill cites both, restates
  neither.

## Sources

- Lighthouse `non-composited-animations` audit (googlechrome/lighthouse) — the source of the
  named failure reasons: `unsupportedCSSProperty`, `filterMayMovePixels`,
  `transformDependsBoxSize`, `nonReplaceCompositeMode`, `unsupportedTimingParameters`,
  `incompatibleAnimations`.
- web.dev — guidance on GPU layer counts and the cost of over-promoting elements.
- MDN Web Docs — `will-change` and `contain` property references.
- Chrome for Developers — Long Animation Frames (LoAF) API documentation.
- Long Tasks API specification (W3C) — main-thread blocking signal used as the LoAF fallback.
- web.dev — Interaction to Next Paint (INP) thresholds.
- WebKit blog — the post introducing `backdrop-filter` support and its cost.
- Framer help docs — site-optimization guidance on blur radius.
- WebKit bug tracker — `mix-blend-mode` + `filter` compositing issue.
- Motion (motion.dev) — performance guide on `playbackRate` and hardware acceleration.
