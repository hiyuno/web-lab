# System accessibility · [project]

Date: [yyyy-mm-dd] · Author: Frost · Level: WCAG 2.2 AA · Verified in tokens and components, not page by page.

## Contrast (verified by `tokens_to_tailwind.py`)

| Pair | Minimum | Light | Dark | Ok |
|------|---------|-------|------|----|
| foreground / background | 4.5 | | | |
| muted-foreground / background | 4.5 | | | |
| accent-foreground / accent | 4.5 | | | |
| ring / background | 3 | | | |

Large text (≥ 24 px, or ≥ 18.66 px bold) and graphical components: 3:1. Text over images: color
layer or box behind; never by eye.

## WCAG 2.2 AA checklist for design

Perceivable
- [ ] Nothing is communicated by color alone: icon, text or pattern in addition to color
- [ ] Text resizable to 200 % without losing content or function
- [ ] Reflow at 320 px width without horizontal scroll
- [ ] Adjustable text spacing (line-height 1.5, paragraphs 2×) without breaking
- [ ] Images with content carry alt from assets.md; decorative ones `alt=""`

Operable
- [ ] Visible focus on every interactive element: ≥ 2 px, 3:1 against the background, never removed (2.4.11)
- [ ] Targets ≥ 24 × 24 px or with enough space between them (2.5.8)
- [ ] No control appears only on hover or focus (3.2.7)
- [ ] Every drag action has a one-click alternative (2.5.7)
- [ ] Logical focus order without traps; "skip to content" link
- [ ] No content flashing more than 3 times per second
- [ ] Animations with an alternative under `prefers-reduced-motion`; nothing essential depends on motion
- [ ] Hover and focus show the same; content that appears can be dismissed with Escape

Understandable
- [ ] Help (contact, chat, FAQ) in the same place on every page (3.2.6)
- [ ] The same data is not requested twice in a flow; it is prefilled or offered as a choice (3.3.8)
- [ ] Login works with password managers and paste; no cognitive tests or memory CAPTCHAs (3.3.7)
- [ ] Visible labels on every field; placeholder does not replace the label
- [ ] Errors identified next to the field, with text that says how to correct
- [ ] Consistent navigation across pages

Robust (for Osmani)
- [ ] Native elements before ARIA: `<button>`, `<a>`, `<input>`, `<dialog>`
- [ ] Accessible name on every control; landmarks: header, nav, main, footer

## Per component

| Component | Role | Name | Keyboard | Announces | Pending |
|-----------|------|------|----------|-----------|---------|
| | | | | | |

## Decisions and exceptions

| What | Why | Alternative offered | Approved by |
|------|-----|---------------------|-------------|
| | | | |
