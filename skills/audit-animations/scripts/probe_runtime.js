// Phase 4: Chrome-measured runtime trace. Split into two separate javascript_tool calls because
// this needs to observe activity over several seconds, and a browser pane that goes hidden/
// backgrounded during that span throttles rAF/setTimeout to as little as once per second or once
// per minute — so nothing here is ever `await`ed inside a single tool call. install() starts
// everything and returns in well under a second; drain() reads back whatever got buffered on
// window.__animAudit. The orchestrating skill is responsible for the wait BETWEEN the two calls
// (via the `computer` tool's own `wait` action, not anything in this script).
//
// Exact invocation — paste this whole file as the javascript_tool expression, twice, editing
// only the final line each time:
//
//   1) Install (fire-and-forget, once per page trace). Last line of the pasted script:
//        })('install', { hoverSelectors: ['.card', '#nav a'] });
//      hoverSelectors is optional: up to 5 CSS selector strings pulled from phase 3's A/R lines
//      for this page. Omit the key, or pass [], to skip the synthetic hover pass. Returns
//      immediately: {"started": true}
//
//   2) Drain (once per page trace), issued after a `computer` tool `wait` of ~9-10 seconds so
//      the 8s frame sampler and the 4s scroll sequence both have time to finish. Last line:
//        })('drain', { calibration: { idleP50: 16.7, throttled: false } });
//      calibration is optional: pass through calibrate.js's `.calibration` object verbatim, as a
//      JS object literal baked into this call's source (this is evaluated as JS, not JSON parsed
//      — do not stringify it). Omit it to default to {idleP50: null, throttled: false}. Returns
//      the JSON shape check_runtime.py expects (loafSupported, longtaskSupported, framePacing,
//      loaf, longtasks, slowEvents, styleWrites, calibration).
(function (mode, opts) {
  opts = opts || {};

  if (mode === 'install') {
    if (!window.__animAudit) {
      window.__animAudit = { loaf: [], longtasks: [], events: [], frames: [], styleWrites: new Map() };
    }
    const store = window.__animAudit;
    if (!store.styleWrites) store.styleWrites = new Map();

    // long-animation-frame: Chrome/Edge only as of this writing. Safari and Firefox don't
    // support the entry type, and observing an unsupported type throws synchronously in some
    // engines — guard with the support check AND a try/catch so an unsupported browser just
    // skips this observer instead of failing the whole install() call.
    try {
      if (PerformanceObserver.supportedEntryTypes?.includes('long-animation-frame')) {
        new PerformanceObserver((list) => {
          store.loaf.push(...list.getEntries().map((e) => ({
            duration: e.duration,
            renderStart: e.renderStart,
            styleAndLayoutStart: e.styleAndLayoutStart,
            blockingDuration: e.blockingDuration,
            scripts: (e.scripts || []).map((s) => ({
              name: s.sourceFunctionName || s.name || '',
              duration: s.duration,
              forcedStyleAndLayoutDuration: s.forcedStyleAndLayoutDuration || 0,
            })),
          })));
        }).observe({ type: 'long-animation-frame', buffered: true });
      }
    } catch (e) { /* unsupported engine: leave store.loaf empty */ }

    try {
      if (PerformanceObserver.supportedEntryTypes?.includes('longtask')) {
        new PerformanceObserver((list) => {
          store.longtasks.push(...list.getEntries().map((e) => ({
            duration: e.duration, startTime: e.startTime,
          })));
        }).observe({ type: 'longtask', buffered: true });
      }
    } catch (e) { /* unsupported engine: leave store.longtasks empty */ }

    // `durationThreshold` is a constructor-time option of the `event` entry type's own
    // observe() call (per the Event Timing API spec) — it is not a filter applied after the
    // fact to whatever entries come back, it changes what the browser records in the first
    // place. Getting this wrong (e.g. filtering post-hoc) would silently miss nothing here, but
    // would waste effort recording every event; passing it into observe() is the correct API.
    try {
      if (PerformanceObserver.supportedEntryTypes?.includes('event')) {
        new PerformanceObserver((list) => {
          store.events.push(...list.getEntries().map((e) => ({
            name: e.name, duration: e.duration,
          })));
        }).observe({ type: 'event', durationThreshold: 40, buffered: true });
      }
    } catch (e) { /* unsupported engine: leave store.events empty */ }

    // Style-write observer: catches rAF-driven inline-style animations (e.g. Framer Motion's
    // hybrid engine, which writes `element.style.x = ...` directly from a requestAnimationFrame
    // callback rather than through the Web Animations API) that document.getAnimations() never
    // sees at all. collect_animations.js (phase 3) attempts the same idea with a MutationObserver
    // too, but does it inside one synchronous script with no event-loop turn between .observe()
    // and .takeRecords() — so no rAF callback, scroll dispatch, or mutation delivery can happen
    // in between, and it almost never fires. This install()/drain() pair is the one place in this
    // skill's design where real wall-clock seconds actually elapse, so the browser gets to
    // deliver mutation records normally.
    try {
      const STYLE_WRITE_MAX_MS = 8000; // same window as the frame sampler; don't outlive it by much
      const STYLE_WRITE_MAX_ELEMENTS = 50; // cap so a pathological page can't grow this unbounded

      // shortSelector() calls document.querySelectorAll() to find the shortest CSS path that
      // resolves uniquely — that DOM work must NEVER run inside the MutationObserver callback
      // below, because that callback fires during the very jank-measurement window this probe is
      // trying to measure: adding querySelectorAll() calls to the main thread while sampling main-
      // thread jank would make the probe itself the thing it's measuring. So the observer callback
      // only accumulates raw data keyed by element reference (see styleMo below); shortSelector()
      // is called from drain(), once per distinct element, well after the measurement window ends.

      // Short, readable selector: tagName(.upTo2Classes)?(:nth-of-type(n))? per ancestor. Same
      // algorithm as collect_animations.js's selectorFor — kept as its own local copy here since
      // this script has no module system to share it through, but the two MUST stay in sync:
      // check_runtime.py's apply_layers() matches this selector (emitted as a runtime finding's
      // `where`) against collect_animations.js's X lines by plain string equality, so any
      // divergence between the two copies silently breaks that match.
      //
      // Never truncate a token with an ellipsis: `sel.slice(0, 90) + '…'` used to produce
      // invalid CSS that document.querySelector throws on, which is exactly why ~30 runtime
      // findings were coming back with no layer path — phase 3 never resolves an invalid
      // selector, so it never appears as an X line either. Instead, trim whole ancestor segments
      // from the LEFT (outermost first) until the selector is short enough, preferring the most
      // specific (longest) candidate that both fits SELECTOR_MAX_LEN and resolves uniquely; if
      // nothing resolves uniquely, fall back to the shortest candidate that is still valid CSS.
      const SELECTOR_MAX_LEN = 120;
      const SELECTOR_MAX_DEPTH = 10; // safety cap on ancestors collected before trimming
      function shortSelector(el) {
        if (!el || el.nodeType !== 1) return '';
        const parts = [];
        let node = el;
        let depth = 0;
        while (node && node.nodeType === 1 && depth < SELECTOR_MAX_DEPTH) {
          let part = node.tagName.toLowerCase();
          if (typeof node.className === 'string' && node.className.trim()) {
            const cls = node.className.trim().split(/\s+/).filter(Boolean).slice(0, 2).join('.');
            if (cls && part.length + cls.length < 40) part += '.' + cls;
          }
          const parent = node.parentElement;
          if (parent) {
            const siblings = Array.prototype.filter.call(parent.children, (c) => c.tagName === node.tagName);
            if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
          }
          parts.unshift(part);
          node = parent;
          depth++;
        }
        let shortestValid = null;
        for (let start = 0; start < parts.length; start++) {
          const sel = parts.slice(start).join('>');
          if (sel.length > SELECTOR_MAX_LEN) continue;
          let count;
          try { count = document.querySelectorAll(sel).length; } catch { continue; }
          if (count === 0) continue;
          shortestValid = sel;
          if (count === 1) return sel;
        }
        return shortestValid != null ? shortestValid : (parts[parts.length - 1] || '');
      }

      // Same value-aware diff as collect_animations.js's parseStyleText/diffStyleProps: a prop
      // counts as changed if its value differs (not just if the prop name was added/removed) —
      // this is the common case for a rAF loop that keeps rewriting e.g. `left` every frame.
      function parseStyleText(t) {
        const map = new Map();
        (t || '').split(';').forEach((decl) => {
          const idx = decl.indexOf(':');
          if (idx === -1) return;
          const prop = decl.slice(0, idx).trim();
          const val = decl.slice(idx + 1).trim();
          if (prop) map.set(prop, val);
        });
        return map;
      }
      function diffStyleProps(oldText, newText) {
        const oldMap = parseStyleText(oldText);
        const newMap = parseStyleText(newText);
        const changed = new Set();
        for (const [k, v] of newMap) if (oldMap.get(k) !== v) changed.add(k);
        for (const k of oldMap.keys()) if (!newMap.has(k)) changed.add(k);
        return changed;
      }

      // store.styleWrites is keyed by element REFERENCE during the measurement window (Map<Element,
      // {props: Set<string>, writes: number}>) — no selector computation, no DOM reads beyond the
      // mutation record itself. Resolving the element to a selector string happens once per
      // element in drain(), after the window closes.
      const styleMo = new MutationObserver((records) => {
        for (const rec of records) {
          if (rec.type !== 'attributes' || rec.attributeName !== 'style') continue;
          const el = rec.target;
          if (!(el instanceof Element)) continue;
          const changed = diffStyleProps(rec.oldValue || '', el.style.cssText || '');
          if (!changed.size) continue;
          let entry = store.styleWrites.get(el);
          if (!entry) {
            if (store.styleWrites.size >= STYLE_WRITE_MAX_ELEMENTS) {
              continue; // cap reached: keep updating elements already tracked, skip new ones
            }
            entry = { props: new Set(), writes: 0 };
            store.styleWrites.set(el, entry);
          }
          for (const c of changed) entry.props.add(c);
          entry.writes++;
        }
      });
      styleMo.observe(document.body, {
        attributeFilter: ['style'], attributeOldValue: true, subtree: true,
      });
      // Disconnect after the same ~8s window as the frame sampler rather than leaving it running
      // for the lifetime of the page.
      setTimeout(() => { try { styleMo.disconnect(); } catch (e) {} }, STYLE_WRITE_MAX_MS);
    } catch (e) { /* MutationObserver unsupported or errored: leave store.styleWrites empty */ }

    // Frame pacing sampler: self-chaining rAF, capped at ~8s OR 480 samples, whichever comes
    // first. NOT awaited — install() returns long before this stops. Awaiting it here would
    // hang this tool call for up to 8s, and far longer than that if the pane is hidden (rAF
    // throttles to ~1/sec or ~1/min when backgrounded), which is exactly the failure mode this
    // whole install/drain split exists to avoid.
    (function sampleFrames() {
      const MAX_SAMPLES = 480;
      const MAX_MS = 8000;
      const start = performance.now();
      let last = null;
      function tick(ts) {
        if (last != null) store.frames.push(ts - last);
        last = ts;
        if (store.frames.length >= MAX_SAMPLES || performance.now() - start >= MAX_MS) return;
        requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    })();

    // Scripted scroll over ~4s via a setTimeout chain — NOT a blocking loop, NOT awaited — so
    // scroll-linked animations get a chance to fire while the observers above are live.
    (function scrollSequence() {
      const doc = document.scrollingElement || document.documentElement;
      const H = doc.scrollHeight;
      const STEPS = 16;
      const STEP_MS = 4000 / STEPS;
      let i = 0;
      function step() {
        i++;
        if (i > STEPS) { window.scrollTo(0, 0); return; }
        window.scrollTo(0, Math.floor((H * i) / STEPS));
        setTimeout(step, STEP_MS);
      }
      setTimeout(step, STEP_MS);
    })();

    // Optional synthetic hover pass on up to 5 selectors carried over from phase 3 — delayed so
    // it lands mid-trace instead of competing with whatever the page itself does right after
    // load. Silently skipped (per-selector) if a selector doesn't resolve to an element.
    if (Array.isArray(opts.hoverSelectors) && opts.hoverSelectors.length) {
      const sels = opts.hoverSelectors.slice(0, 5);
      setTimeout(() => {
        for (const sel of sels) {
          let el;
          try { el = document.querySelector(sel); } catch (e) { continue; }
          if (!el) continue;
          const r = el.getBoundingClientRect();
          const init = { bubbles: true, cancelable: true, clientX: r.left + r.width / 2, clientY: r.top + r.height / 2 };
          try {
            el.dispatchEvent(new PointerEvent('pointerover', init));
            el.dispatchEvent(new MouseEvent('mouseover', init));
          } catch (e) { /* ignore: best-effort synthetic hover */ }
        }
      }, 1500);
    }

    return { started: true };
  }

  if (mode === 'drain') {
    const store = window.__animAudit
      || { loaf: [], longtasks: [], events: [], frames: [], styleWrites: new Map() };

    const sortedFrames = store.frames.slice().sort((a, b) => a - b);
    const pct = (arr, p) => (arr.length ? arr[Math.min(arr.length - 1, Math.floor(arr.length * p))] : null);
    const framePacing = { p50: pct(sortedFrames, 0.5), p95: pct(sortedFrames, 0.95), count: store.frames.length };

    // Only jank-worthy long-animation-frame entries are worth shipping back; framePacing above
    // is already computed from ALL frame samples, not the filtered set below.
    const loaf = store.loaf.filter((e) => e.duration > 50);

    // store.styleWrites is a Map<Element, {props: Set<string>, writes: number}> during install() —
    // elements are resolved to selector strings HERE, after the measurement window, not inside the
    // MutationObserver callback (see the comment above styleMo in install()). Some elements may
    // have been removed from the document by now; shortSelector() still runs for them (its
    // querySelectorAll probes just return 0 matches and it falls back to the shortest ancestor
    // chain it collected while the element still existed) — they are not dropped here. Two
    // elements that resolve to the same selector are merged (props unioned, writes summed) before
    // the final array is built, so the output stays one entry per selector — same shape as before.
    const merged = new Map(); // selector -> { props: Set<string>, writes: number }
    for (const [el, data] of (store.styleWrites || new Map())) {
      const sel = shortSelector(el);
      if (!sel) continue; // defensive: shortSelector() only returns '' for a non-Element node
      const existing = merged.get(sel);
      if (existing) {
        for (const p of data.props) existing.props.add(p);
        existing.writes += data.writes;
      } else {
        merged.set(sel, { props: new Set(data.props), writes: data.writes });
      }
    }
    // JSON can't serialize a Map or a Set, so flatten into the array shape check_runtime.py's
    // runtime_non_composited_write check expects: [{ selector, props }].
    const styleWrites = [];
    for (const [selector, data] of merged) {
      styleWrites.push({ selector, props: [...data.props] });
    }

    const calibration = opts.calibration || { idleP50: null, throttled: false };

    return {
      loafSupported: PerformanceObserver.supportedEntryTypes?.includes('long-animation-frame') ?? false,
      longtaskSupported: PerformanceObserver.supportedEntryTypes?.includes('longtask') ?? false,
      framePacing,
      loaf,
      longtasks: store.longtasks,
      slowEvents: store.events,
      styleWrites,
      calibration,
    };
  }

  throw new Error('probe_runtime.js: unknown mode "' + mode + '"');
})('install', { hoverSelectors: [] });
