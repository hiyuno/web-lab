// Phase 2: run once per audit, on the home page, via the browser javascript_tool.
//
// Why the race: an rAF-based sampler that a tool call `await`s directly can hang for the full
// 45s tool timeout if the browser pane is hidden/backgrounded, because a hidden tab throttles
// requestAnimationFrame (and setTimeout) to as little as once per second or once per minute.
// Racing the sampler against a hard 4s setTimeout means a throttled pane still returns
// promptly — with a result that plainly reports too few / too-irregular samples, instead of
// never returning at all. This is the same constraint collect_assets.js's header comment
// describes for its scroll loop, applied here to a timed measurement instead of a scroll.
await (async function calibrate() {
  const TIMEOUT_MS = 4000;
  const MAX_SAMPLES = 30;

  const deltas = [];
  let stopped = false;

  const samplesDone = new Promise((resolve) => {
    let last = null;
    function step(ts) {
      if (stopped) return resolve();
      if (last != null) deltas.push(ts - last);
      last = ts;
      if (deltas.length >= MAX_SAMPLES) { stopped = true; return resolve(); }
      requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  });
  const timeout = new Promise((resolve) => setTimeout(resolve, TIMEOUT_MS));

  await Promise.race([samplesDone, timeout]);
  stopped = true; // stop the rAF chain if the timeout won the race, so it doesn't keep sampling
                   // after this call has already returned its result.

  const sorted = deltas.slice().sort((a, b) => a - b);
  const idleP50 = sorted.length ? sorted[Math.floor(sorted.length / 2)] : null;
  // "Throttled" covers two failure shapes, not just one: idleP50 far above ~16.7ms means real
  // throttling (hidden pane, or a genuinely slow device); idleP50 far below it, or a sample
  // count well short of MAX_SAMPLES, means the 4s race cut the sampler off early and what
  // little we collected is not a trustworthy baseline either way.
  const throttled = idleP50 == null
    || idleP50 < 14 || idleP50 > 40
    || sorted.length < MAX_SAMPLES * 0.5;

  const libs = [];
  if (window.Motion || window.__motion) libs.push('Motion');
  if (window.gsap) libs.push('gsap');
  if (window.ScrollTrigger) libs.push('ScrollTrigger');
  if (window.Lenis) libs.push('lenis');
  if (document.querySelector('[data-framer-name]')
      || document.querySelector('script[src*="framerusercontent.com"], link[href*="framerusercontent.com"]')) {
    libs.push('framer');
  }

  return {
    hardwareConcurrency: navigator.hardwareConcurrency,
    devicePixelRatio: window.devicePixelRatio,
    prefersReducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
    loafSupported: PerformanceObserver.supportedEntryTypes?.includes('long-animation-frame') ?? false,
    longtaskSupported: PerformanceObserver.supportedEntryTypes?.includes('longtask') ?? false,
    scrollTimelineSupported: CSS.supports('animation-timeline', 'scroll()'),
    libs,
    calibration: { idleP50, throttled },
  };
})();
