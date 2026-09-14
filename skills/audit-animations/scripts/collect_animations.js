// Phase 3: run in the page with the browser javascript_tool, one call per page, AFTER the page
// has loaded. Fully synchronous — same technique as optimize-assets/collect_assets.js: a
// hidden/backgrounded pane throttles setTimeout (and rAF) to ~1/sec or ~1/min, so this never
// awaits a sleep. The scroll below only needs to have *happened* by the time synchronous code
// reads the resulting DOM/style state a few lines later, not to have visually settled — so it's
// a plain `for` loop with no delay, immediately followed by the mutation read.
(() => {
  const MAX_LINES = 500; // cap so a pathological page (huge DOM, animation-heavy) truncates
  const lines = [];      // instead of producing a multi-thousand-line payload back to the tool
  let truncated = false;
  function pushLine(s) {
    if (lines.length >= MAX_LINES) { truncated = true; return false; }
    lines.push(s);
    return true;
  }

  // Short, readable selector: tagName(.upTo2Classes)?(:nth-of-type(n))?, capped to 4 ancestors
  // deep. Not a brittle full-DOM path — this is for a human reading the report, and it's
  // recomputed fresh each time rather than cached, so it stays correct as candidate sets grow.
  function selectorFor(el) {
    if (!el || el.nodeType !== 1) return '';
    const parts = [];
    let node = el;
    let depth = 0;
    while (node && node.nodeType === 1 && depth < 4) {
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
    const sel = parts.join('>');
    return sel.length > 90 ? sel.slice(0, 90) + '…' : sel;
  }

  // Install the MutationObserver BEFORE the scroll loop, then read it with takeRecords() rather
  // than the callback: a synchronous IIFE never yields to a microtask checkpoint, so the
  // callback would simply never run before this function returns, and takeRecords() drains
  // whatever is already queued instead.
  //
  // Honest limitation, confirmed by testing this against a live rAF-driven style-write loop:
  // because this whole call is synchronous end to end, ZERO real animation frames elapse
  // between .observe() and .takeRecords() — rAF callbacks (and the 'scroll' event) only run as
  // part of the browser's normal per-frame rendering step, which requires the JS call stack to
  // be empty, and it never is here. So this technique can only ever pick up a style mutation
  // that was applied SYNCHRONOUSLY as a side effect of something already running before this
  // script's stack unwinds (e.g. a synchronous scroll-triggered style recalc some engines still
  // perform) — it will typically emit nothing for the common case of a rAF-scheduled or
  // scroll-event-driven write (which includes Framer Motion's hybrid engine), even though that
  // is exactly the case R lines exist to catch. Left in per spec rather than silently dropped,
  // because it is cheap and occasionally does catch something; Phase 4's probe_runtime.js has
  // the multi-second real-time window this needs and would be the right place to add an
  // equivalent style-mutation observer if this gap needs closing for real.
  const mo = new MutationObserver(() => {});
  mo.observe(document.body, {
    attributes: true, attributeFilter: ['style'], attributeOldValue: true, subtree: true,
  });

  const doc = document.scrollingElement || document.documentElement;
  const H = doc.scrollHeight;
  for (let i = 1; i <= 12; i++) window.scrollTo(0, Math.floor((H * i) / 12));
  window.scrollTo(0, 0);

  const records = mo.takeRecords();
  mo.disconnect();

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
  const styleChanges = new Map(); // Element -> Set<propName>
  for (const rec of records) {
    if (rec.type !== 'attributes' || rec.attributeName !== 'style') continue;
    const el = rec.target;
    if (!(el instanceof Element)) continue;
    const changed = diffStyleProps(rec.oldValue || '', el.getAttribute('style') || '');
    if (!changed.size) continue;
    const set = styleChanges.get(el) || new Set();
    for (const c of changed) set.add(c);
    styleChanges.set(el, set);
  }

  // ---- A lines: document.getAnimations() ----
  let animations = [];
  try { animations = document.getAnimations(); } catch { animations = []; }
  const animEntries = []; // {selector, el, props: Set}
  for (const anim of animations) {
    const effect = anim.effect;
    const target = effect && effect.target;
    if (!target) continue;
    const sel = selectorFor(target);
    let props = [];
    try {
      const kfs = effect.getKeyframes ? effect.getKeyframes() : [];
      const propSet = new Set();
      for (const kf of kfs) {
        for (const k of Object.keys(kf)) {
          if (k === 'offset' || k === 'easing' || k === 'composite' || k === 'computedOffset') continue;
          propSet.add(k);
        }
      }
      props = [...propSet];
    } catch {}
    // `effect.composite` is the authored per-keyframe-effect value from the spec. Chrome also
    // exposes a resolved value via getComputedTiming().composite, but that key is not
    // consistently populated across Chrome versions — use the direct property first and only
    // fall back to computed timing (rather than guessing which one is "right" per spec, we take
    // whichever one the running engine actually filled in).
    let composite = effect && effect.composite;
    if (composite == null && effect && effect.getComputedTiming) {
      try { composite = effect.getComputedTiming().composite; } catch {}
    }
    let iterationStart = 0;
    try { iterationStart = effect.getTiming ? effect.getTiming().iterationStart : 0; } catch {}
    pushLine(['A', sel, props.join(','), composite || '-', anim.playbackRate, iterationStart, anim.playState].join('|'));
    animEntries.push({ selector: sel, el: target, props: new Set(props) });
  }

  // ---- R lines: MutationObserver diffs not already fully covered by an A line ----
  const rEntries = []; // {selector, el}
  for (const [el, propsSet] of styleChanges) {
    const sel = selectorFor(el);
    const props = [...propsSet];
    const existingAnim = animEntries.find((a) => a.selector === sel);
    if (existingAnim && props.every((p) => existingAnim.props.has(p))) continue; // pure duplicate
    if (pushLine(['R', sel, props.join(',')].join('|'))) rEntries.push({ selector: sel, el });
  }

  // ---- Candidate set for L / F / P: animated elements + their immediate ancestor, plus any
  // element whose inline style mentions will-change/translate3d/translateZ/backface-visibility.
  // Deliberately NOT every node in the document — getComputedStyle on every element in a large
  // page is the kind of thing that makes this script itself the next long task.
  const candidateEls = new Set();
  function addWithAncestor(el) {
    if (!el) return;
    candidateEls.add(el);
    if (el.parentElement) candidateEls.add(el.parentElement);
  }
  for (const a of animEntries) addWithAncestor(a.el);
  for (const r of rEntries) addWithAncestor(r.el);
  document.querySelectorAll('[style]').forEach((el) => {
    const s = el.getAttribute('style') || '';
    if (/will-change|translate3d|translateZ|backface-visibility/i.test(s)) candidateEls.add(el);
  });

  // ---- L lines ----
  const lSeen = new Set();
  function emitL(sel, reason) {
    const key = sel + '|' + reason;
    if (lSeen.has(key)) return;
    lSeen.add(key);
    pushLine(['L', sel, reason].join('|'));
  }
  for (const el of candidateEls) {
    const sel = selectorFor(el);
    const cs = getComputedStyle(el);
    if (cs.willChange && cs.willChange !== 'auto') emitL(sel, 'will-change');
    // getComputedStyle always resolves transform to matrix()/matrix3d() — translate3d/translateZ
    // can only be recovered from the *authored* inline style text, which is why this only catches
    // the inline-style case and misses the same transform set via a class or stylesheet rule.
    // Noted as a limitation rather than papered over with a guess.
    const inlineTransform = el.style && el.style.transform || '';
    if (inlineTransform.includes('translate3d')) emitL(sel, 'translate3d');
    else if (inlineTransform.includes('translateZ')) emitL(sel, 'translateZ');
    if (cs.backfaceVisibility === 'hidden') emitL(sel, 'backface-hidden');
    const bf = cs.backdropFilter || cs.getPropertyValue('backdrop-filter');
    if (bf && bf !== 'none') emitL(sel, 'backdrop-filter');
  }

  // ---- F lines ----
  const fSeen = new Set();
  for (const el of candidateEls) {
    const sel = selectorFor(el);
    const cs = getComputedStyle(el);
    const checks = [
      ['filter', cs.filter, 'none'],
      ['backdrop-filter', cs.backdropFilter || cs.getPropertyValue('backdrop-filter'), 'none'],
      ['mix-blend-mode', cs.mixBlendMode, 'normal'],
    ];
    for (const [kind, val, def] of checks) {
      if (!val || val === def) continue;
      const key = sel + '|' + kind;
      if (fSeen.has(key)) continue;
      fSeen.add(key);
      const value = val.length > 40 ? val.slice(0, 40) + '…' : val;
      pushLine(['F', sel, kind, value].join('|'));
    }
  }

  // ---- P lines: candidate set + a capped document-order scan (querySelectorAll('*') on the
  // whole page is too expensive to run getComputedStyle over; 300 elements in document order is
  // enough to catch nav bars / sticky headers without scanning a huge DOM). ----
  const allEls = document.querySelectorAll('*');
  const capped = allEls.length <= 300 ? Array.from(allEls) : Array.from(allEls).slice(0, 300);
  const pCandidates = new Set([...candidateEls, ...capped]);
  const pSeen = new Set();
  for (const el of pCandidates) {
    const cs = getComputedStyle(el);
    if (cs.position !== 'fixed' && cs.position !== 'sticky') continue;
    const sel = selectorFor(el);
    if (pSeen.has(sel)) continue;
    pSeen.add(sel);
    pushLine(['P', sel, cs.position].join('|'));
  }

  // ---- S line: best-effort heuristic only. Listeners added via addEventListener are invisible
  // to page-context JS running after the fact — there is no API to enumerate them without having
  // patched addEventListener before the page's own scripts ran, which this script (injected
  // after load, from outside the page) cannot do. So this only counts the two things that ARE
  // observable after the fact: the legacy on* handler properties, and inline on* attributes. ----
  let scrollCount = (typeof window.onscroll === 'function' ? 1 : 0)
    + (typeof window.onwheel === 'function' ? 1 : 0)
    + (typeof window.ontouchmove === 'function' ? 1 : 0);
  scrollCount += document.querySelectorAll('[onscroll], [onwheel]').length;
  pushLine(['S', 'scroll', scrollCount].join('|'));

  const p = location.pathname.replace(/^\/|\/$/g, '');
  const slug = p ? p.replace(/\//g, '__').replace(/[^A-Za-z0-9._-]+/g, '-') : 'home';
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches ? 1 : 0;
  const header = `page=${location.href}|slug=${slug}|dpr=${devicePixelRatio}|vw=${innerWidth}|vh=${innerHeight}|reducedMotion=${reducedMotion}`;

  return { header, lines, truncated };
})();
