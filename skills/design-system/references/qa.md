# Design QA · [project]

Date: [yyyy-mm-dd] · Reviewer: Frost · On: prototype at [URL or branch] · Status: [ ] approved

Verified on the code prototype, at 375, 768 and 1280, in light and dark mode if it exists.

## Tokens

- [ ] No color, spacing, radius, shadow or duration outside `tokens.css` (search for literal values in the CSS)
- [ ] `tokens_to_tailwind.py --check` with no contrast failures
- [ ] Dark mode: semantic override only; nothing hardcoded

## Typography

- [ ] Family, size, line-height and tracking from the scale on every element
- [ ] Visible hierarchy: H1, H2, body and note are told apart without reading
- [ ] Line length 45 to 75 characters in body
- [ ] Real copy from the briefs, no truncation or overflow

## Components

- [ ] Every component in the inventory has its 9 states in the prototype
- [ ] Visible focus on all; targets ≥ 24 px; nothing hover-only
- [ ] The same component looks the same across all templates
- [ ] Long and short copy tested

## Templates and responsive

- [ ] 375: no horizontal scroll, accessible menu, images with ratio
- [ ] 768 and 1280: grid respected, max content width
- [ ] Page states: loading without shift, empty, error, success
- [ ] Images with the asset and ratio from assets.md; the hero one marked as priority

## Accessibility

- [ ] `accessibility.md` checklist complete
- [ ] Keyboard walkthrough of the main flows
- [ ] 200 % zoom and 320 px reflow
- [ ] Reduced motion on: nothing essential is lost

## Motion

- [ ] Only what is listed in `motion.md`, with duration and curve tokens
- [ ] Nothing pushes the layout

## Content and security

- [ ] Exact copy from the briefs, including microcopy and errors
- [ ] Login on its own page, `autocomplete`, show password, generic error
- [ ] Destructive actions with confirmation and separated
- [ ] Consent: reject as visible as accept
- [ ] Session visible on authenticated screens

## Findings

| # | Where | What | Severity | Fix in | Status |
|---|-------|------|----------|--------|--------|
| | | | blocker / major / minor | token / component / template | |
