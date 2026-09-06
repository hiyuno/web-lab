# Motion · [project]

Date: [yyyy-mm-dd] · Author: Frost · Tokens: duration.*, ease.* · Reference: apple-design, emil-design-eng skills

## Principles

- Motion explains a change of state or place. If it explains nothing, it does not animate.
- Interruptible: the user can change their mind halfway.
- Fast: 150 to 300 ms for interface; springs only for gestures and dragged elements.
- Nothing essential depends on motion. Under `prefers-reduced-motion: reduce`, transitions at 0 ms or opacity fades.

## What animates

| Element | Property | Duration | Curve | Reduced motion |
|---------|----------|----------|-------|----------------|
| Button hover | background color | duration.fast | ease.out | same (it is not motion) |
| Menu / popover appear | opacity + translateY 4 px | duration.normal | ease.out | opacity only |
| Sheet or modal | translateY / scale 0.98 → 1 | duration.slow | ease.spring | opacity only |
| Page change | opacity | duration.page | ease.in-out | none |
| Accordion | height (grid-template-rows) | duration.normal | ease.out | instant |
| Toast | translateY + opacity | duration.normal | ease.out | opacity only |
| Loading skeletons | opacity pulse | 1.5 s loop | linear | static |

## What does not animate

- Text while it is being read. Layout that pushes content (causes CLS).
- Nothing in an infinite loop except loading indicators.
- Parallax and scroll effects unless the user explicitly decides so.

## Gestures (applications only)

| Gesture | Where | Physics | Cancellation |
|---------|-------|---------|--------------|
| Drag sheet to close | mobile sheet | ease.spring | returns if < 40 % |
| One-click alternative (WCAG 2.5.7) | visible close button | | |

## Implementation (for Osmani)

- CSS `transition` with tokens; View Transitions for page changes (`react-view-transitions` skill on Next.js).
- Global `@media (prefers-reduced-motion: reduce)` that reduces durations to 0.01 ms except opacity.
