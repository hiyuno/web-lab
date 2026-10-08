# Motion with GSAP

The recipe Osmani follows once per project when `docs/04-design/motion.md` marks motion as GSAP.
Frost decides what animates and with which values; this file only says how to wire it. Verified
against the official docs (gsap.com, the Lenis README, MDN's `@view-transition`) on 2026-10-08;
re-check the version lines when you install.

## When

- Only when `motion.md` marks GSAP for something. Otherwise CSS transitions, zero extra JS.
- GSAP is for what CSS does badly: timelines, scroll-driven animation, text splitting, SVG
  drawing, inertia and drag.
- Hover, press and focus states are always CSS: interruptible and lighter (`better-ui`).
- A site that uses GSAP also gets Lenis smooth scroll. A site that does not use GSAP does not get
  Lenis.

## Install

From npm, never from a CDN, pinned to the 3.15 line:

```bash
pnpm add gsap@~3.15.0 lenis
pnpm add @gsap/react   # Next.js only
```

- The `gsap` package includes the plugins. Import only the ones the project uses, from their own
  path, and register them: `ScrollTrigger`, `SplitText`, `DrawSVGPlugin`, `CustomEase`,
  `InertiaPlugin`.

```ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";

gsap.registerPlugin(ScrollTrigger, SplitText);
```

- Bundlers may tree-shake a plugin that is only referenced through `registerPlugin`; registering
  it explicitly, and more than once, is harmless. A shared `lib/gsap.ts` that registers and
  re-exports keeps this in one place.
- License: GSAP uses its own Standard "No Charge" license (not MIT), and as of 2025 all plugins,
  SplitText and DrawSVG included, are free for commercial use. It restricts using GSAP in tools
  that let users build animations visually without code and compete with Webflow, and forbids
  removing its notices. A normal marketing site or application is unaffected. Read the current
  text at <https://gsap.com/standard-license/> before the first install of a project, and note
  it in `docs/05-development/frontend.md`. Lenis is MIT.

## GSAP + Lenis wiring

Lenis is driven by GSAP's ticker, and ScrollTrigger is updated on every Lenis scroll, exactly as
the Lenis README documents:

```ts
import Lenis from "lenis";
import "lenis/dist/lenis.css";

const lenis = new Lenis();

lenis.on("scroll", ScrollTrigger.update);

gsap.ticker.add((time) => {
  lenis.raf(time * 1000); // GSAP's time is in seconds, Lenis expects milliseconds
});

gsap.ticker.lagSmoothing(0);
```

- Do not also set `autoRaf: true`: GSAP's ticker is the only loop.
- Keep a reference to the function passed to `gsap.ticker.add` so it can be removed later.

## Reduced motion

The rule (what must change under `prefers-reduced-motion`) is owned by `better-accessibility`;
this is only the wiring. Gate every GSAP animation and Lenis itself behind
`gsap.matchMedia()` so nothing is created when the visitor asked for less motion:

```ts
const mm = gsap.matchMedia();

mm.add("(prefers-reduced-motion: no-preference)", () => {
  const lenis = new Lenis();
  lenis.on("scroll", ScrollTrigger.update);
  const tick = (time: number) => lenis.raf(time * 1000);
  gsap.ticker.add(tick);
  gsap.ticker.lagSmoothing(0);

  gsap.from(".hero-title", { y: 24, opacity: 0, duration: 0.6 });
  // ...every other animation and ScrollTrigger lives inside this handler

  return () => {
    gsap.ticker.remove(tick);
    lenis.destroy();
  };
});
```

- Animations and ScrollTriggers created inside the handler are recorded and reverted
  automatically when the query stops matching, or on `mm.revert()`. The returned function is
  only for what GSAP does not track: here, the ticker callback and the Lenis instance. Do not call
  `revert()` inside it.
- Under `reduce` the handler does not run: no Lenis, native scroll, and the content must be
  readable in its final state (no element hidden waiting for an animation that never starts).
  Set initial hidden states inside the handler (`gsap.from`, `gsap.set`), never in CSS.

## Astro

Page transitions on Astro are CSS cross-document view transitions, never `<ClientRouter />`
(imported from `astro:transitions`): it is incompatible with `security.csp`, which every site
keeps (`headers.md`). So every navigation is a full page load.

- Opt in from the global stylesheet, only when motion is allowed. Both pages of a navigation
  need the rule, and it only works between same-origin pages:

```css
@media (prefers-reduced-motion: no-preference) {
  @view-transition {
    navigation: auto;
  }
}
```

- Under `reduce` there is no transition, just the normal page load. Custom
  `::view-transition-old()` / `::view-transition-new()` animations and `view-transition-name`
  pairs go inside the same media query; values come from Frost's `motion.md`.
- Progressive enhancement: Chrome and Edge 126+ and Safari 18.2+ (macOS and iOS) run it; Firefox
  does not yet (MDN browser-compat-data, 2026-10-08), and navigates with no transition. Nothing
  may depend on it.
- One module script, loaded from the layout: `src/scripts/motion.ts`. Add it to the pages that
  animate, not to the whole site, when only some do. Astro bundles it as `type="module"`, which
  runs after the document is parsed, so it builds at the top level, once per page load, as in
  "Reduced motion" above:

```ts
import { gsap, ScrollTrigger } from "../lib/gsap"; // registers the plugins
import Lenis from "lenis";
import "lenis/dist/lenis.css";

const mm = gsap.matchMedia();
mm.add("(prefers-reduced-motion: no-preference)", () => {
  const lenis = new Lenis();
  lenis.on("scroll", ScrollTrigger.update);
  const tick = (time: number) => lenis.raf(time * 1000);
  gsap.ticker.add(tick);
  gsap.ticker.lagSmoothing(0);
  // ...this page's animations
  return () => {
    gsap.ticker.remove(tick);
    lenis.destroy();
  };
});
```

- No `astro:page-load`, `astro:before-swap` or `astro:after-swap` listeners: those events belong
  to `<ClientRouter />`. Each navigation discards the old document with its Lenis instance and
  animations, so nothing needs tearing down across pages. A page restored from the back/forward
  cache comes back as it was left, without re-running the script.
- Islands with `client:visible` or `client:idle` that animate on their own follow the Next.js
  rules below.

## Next.js

- Everything GSAP is a client component: `"use client"` at the top.
- Use `useGSAP` from `@gsap/react` instead of `useEffect`/`useLayoutEffect`: it wraps the code in
  a `gsap.context()` and reverts animations, ScrollTriggers and SplitText instances on unmount.
  Register it once and pass a `scope` ref so selectors only match inside the component:

```tsx
"use client";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP);

export function Hero() {
  const root = useRef<HTMLElement>(null);

  useGSAP(() => {
    const mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", () => {
      gsap.from(".hero-title", { y: 24, opacity: 0, duration: 0.6 });
    }, root.current ?? undefined); // third argument scopes the selectors
    return () => mm.revert();
  }, { scope: root });

  return <section ref={root}>{/* ... */}</section>;
}
```

- Animations created later (click handlers, timeouts) are not tracked: wrap them in
  `contextSafe`, from the object `useGSAP` returns.
- Lenis once, at the layout level, in a client provider using the React wrapper from
  `lenis/react`, with `root` so the instance is global and GSAP's ticker as the only loop. Render
  it only when motion is allowed:

```tsx
"use client";
import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ReactLenis, useLenis, type LenisRef } from "lenis/react";
import "lenis/dist/lenis.css";

gsap.registerPlugin(ScrollTrigger);

export function SmoothScroll({ children }: { children: React.ReactNode }) {
  const lenisRef = useRef<LenisRef>(null);
  const [motionOk, setMotionOk] = useState(false);

  useEffect(() => {
    const query = window.matchMedia("(prefers-reduced-motion: no-preference)");
    const sync = () => setMotionOk(query.matches);
    sync();
    query.addEventListener("change", sync);
    return () => query.removeEventListener("change", sync);
  }, []);

  useEffect(() => {
    if (!motionOk) return;
    const update = (time: number) => lenisRef.current?.lenis?.raf(time * 1000);
    gsap.ticker.add(update);
    gsap.ticker.lagSmoothing(0);
    return () => gsap.ticker.remove(update);
  }, [motionOk]);

  useLenis(() => ScrollTrigger.update()); // keep ScrollTrigger in step with Lenis

  return (
    <>
      {motionOk && <ReactLenis root options={{ autoRaf: false }} ref={lenisRef} />}
      {children}
    </>
  );
}
```

- Mount `SmoothScroll` in the root `layout.tsx`. A client component can wrap Server Component
  children, so the rest of the tree stays on the server.

## Performance

- Animate only `transform` and `opacity`. GSAP's `x`, `y`, `scale` and `rotation` are transforms;
  never animate `width`, `height`, `top`, `left` or `margin`.
- GSAP's ticker runs on the main thread, so a GSAP-driven `transform` write is not
  compositor-only. This is the cost `audit-animations` documents as a known gap for JS-driven
  transform writes (`skills/audit-animations/references/checks.md`, Calibration notes): the
  audit does not flag it, so keep the number of simultaneously animated elements small and
  measure on a mid-range phone.
- GSAP, its plugins and Lenis count against the initial-JS budget in `lighthouserc.json` (150 KB
  compressed). Import only the plugins used, and load the script per page or island, not
  site-wide, when only one page animates.
- Kill what you no longer need: ScrollTriggers and animations for content that left the screen
  for good, `SplitText` instances once their animation has finished (`revert()` restores the
  original markup), and the whole context on navigation or unmount as above.

No Barba: page transitions use the platform's or the framework's own (CSS `@view-transition` on
Astro, Next.js navigation).
