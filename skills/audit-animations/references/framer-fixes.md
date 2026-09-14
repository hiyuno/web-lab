# Framer-specific fixes

Framer gives a good baseline (clean URLs, automatic image optimization, a real animation
engine) but exposes only some of its knobs through the UI. This reference gives the exact lever
in the Framer UI for each finding type, or an honest "platform limitation" when there isn't one.

## Blur radius ≥ 10px on or behind animated content

Select the layer → **Effects** panel → **Blur** → lower the radius below 10px. Framer's own
guidance is explicit: keep blur under 10px for a live effect; above that, export the blurred
result as a flattened image (right-click → Export, or an image fill) instead of animating a live
blur. A static blurred image costs nothing per frame; a live one recomputes constantly.

## Scroll-triggered effects above the fold

Switch the layer's animation trigger from a scroll-linked effect to an **Appear** effect
(Interactions panel → Appear). Appear effects fire from Framer's own render pipeline before the
page's JS bundle finishes loading; scroll-triggered effects wait for JS to attach the scroll
listener, which is exactly the wrong tradeoff above the fold, where the goal is to show content
as fast as possible, not after a listener is ready.

## Animating size/position in the Effects panel instead of Move/Scale

If a layer's entrance or hover animation is driving `width`, `height`, `top` or `left` directly
in the Effects/Style panel, switch it to Framer's **Move** and **Scale** transform properties
instead. Move/Scale are transform-backed and stay on the compositor; width/height/position
animations force layout on every frame.

## Many simultaneous entrance animations on load

Reduce the number of layers animating in at once: either stagger them (Interactions panel →
stagger children) or cut the ones that don't earn their place. Per the cheapest-fix ladder in
`CLAUDE.md`, deleting an unnecessary entrance animation is a valid fix here, not a compromise —
keep total entrance time short rather than adding more staggering to hide a large count.

## `will-change`/layer explosion from stacking multiple Effects panel effects on one layer

Framer doesn't expose `will-change` or layer promotion directly — there is no UI toggle to fix
this at the property level. The fix is removing effects from the layer, not adding a hint: stack
fewer Effects panel entries (blur + shadow + blend mode + opacity animation all on one layer is
the common culprit) or split them across simpler layers. Per the cheapest-fix ladder, delete
before you add.

## Glass/backdrop-blur sections

This is the highest Safari-cost item this skill flags. Reduce the blur radius, shrink the area
that's blurred (a smaller card instead of a full-width band), or flatten the section to an image
if it doesn't need to react to what's behind it. There's no UI setting that makes a live
backdrop-blur cheap — the fix is always doing less of it.

## Sticky section with a filter/blend-mode ancestor

Move the `filter`/`backdrop-filter`/`mix-blend-mode` effect off the ancestor of the sticky
element and onto a sibling or a non-ancestor wrapper instead. In the Layers panel, check what's
above the sticky layer in the tree; if an effect sits there, that's the ancestor to fix. This is
as much a correctness fix (Safari can silently break the sticky positioning) as a performance
one.

## `contain`/`content-visibility` on repeated animated sections

Not exposed in the Framer UI. Inject via **Site Settings → Custom Code → End of `<head>` tag**,
a `<style>` block targeting the repeated section's class:

```html
<style>
  .repeated-animated-card { contain: layout paint; }
</style>
```

This is the escape hatch that makes most of this skill's non-UI-exposed fixes possible on
Framer at all — same role Custom Code plays in `/audit-seo`'s own `framer-fixes.md` for
injecting JSON-LD.

## Heavy self-hosted video behind an animated section

Out of scope for this skill — hand off to `/optimize-assets` with Bellard for format, bitrate
and dimension fixes, same cross-reference `/audit-seo`'s `framer-fixes.md` makes for media
weight.

## Native scroll-driven animation (`animation-timeline: scroll()`)

Only as a **progressive-enhancement** fix, never the sole implementation: `animation-timeline:
scroll()` isn't mature/Baseline enough yet to replace a JS-driven scroll animation outright.
Inject it behind an `@supports` check via Custom Code:

```html
<style>
  @supports (animation-timeline: scroll()) {
    .scroll-linked-element {
      animation-timeline: scroll();
      /* keep the existing JS-driven version as the fallback path */
    }
  }
</style>
```
