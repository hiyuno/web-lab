# Break · step 4.8

Adapted from `break` in Jakub Krehel's `interfaces` collection (MIT). Renders a component in
every scenario that can reach it, on a throwaway page that is the report. A component built
against the happy path looks finished until real content arrives.

It observes, does not judge. A finding is something that visibly broke, named in the vocabulary
of the skill that owns the fix. Here isolation is deliberate: you are not judging how it looks in
context, but whether it defends itself with the worst content.

## Procedure

1. **One component per run.** The contact form is not a component; its text field is. With
   several candidates, list and ask which.
2. **Infer the scenarios from the component**, not from the menu. Read its props, slots, states
   and data. Each axis has a cue that says whether it applies; keep only the matching ones and
   say in one line which you dropped.
3. **Build the throwaway page**: a test route inside the prototype, the real component imported
   untouched, one instance per scenario in a single column with a text label above. No styles of
   its own, no simulated themes, no live data. Widths are fixed containers on the same page, never
   a window resize.
4. **Look once.** Load, skim top to bottom and note what visibly broke: "the text escapes the
   right edge", never "the spacing feels tight". One load is the budget. Mark each break under its
   label on the page.
5. **Report and stop.** Breaks first:

| Scenario | Observed | Owner |
|----------|----------|-------|
| One unbreakable 60-character string | overflows the card, no wrap and no truncation | `better-typography` |
| Zero items | blank region with no message | `better-writing` |

"Everything survived" is a complete report. Say which scenarios are on the page and where it runs.
Do not fix unasked; when fixing, follow the owner and re-render only what failed.

6. **Leave the page up** until the user says they are done; it is half the report.

## Axes and cues

| Axis | Cue to include it | Scenarios |
|------|-------------------|-----------|
| Content length | renders text the team does not write | empty · one word · typical · several sentences · one unbreakable string |
| Content shape | text may come from users or foreign locales | emoji alone and mixed · right-to-left text · mixed direction · diacritics and tall scripts · numbers in columns |
| Quantity | repeats over items | zero · one · the realistic count · ten times the realistic count |
| Container | always | 320 px · squeezed by a flex or grid sibling · very wide |
| State | the component has the state as a prop | loading · error · disabled (hover and focus the user tries with the keyboard) |
| Environment | the project supports the mode; not simulated, the user toggles it | dark mode · 200 % zoom · reduced motion |

Typical owners: wrapping and truncation in `better-typography`; no room in `better-layout`;
source copy in `better-writing`; empty states in `better-writing` and `better-layout`; states in
`better-accessibility`; dark mode in `better-colors`.

## Before you finish

| Symptom | Fix |
|---------|-----|
| Every axis against every component | only the ones the cue admits, and say which you dropped |
| A predicted failure reported as observed | render it or leave it out |
| A scenario missing the content it was given | the page is broken, not the component; make it client code and re-check |
| A lookalike component rebuilt in the page | import the real one |
| The page restyles or re-themes the component | layout, fonts and tokens as they are; only labels and widths |
| Window resized per scenario | fixed containers; one load shows them all |
| Break in the table with no mark on the page | note it under its label |
| Page deleted in the same turn as the report | delete it only when the user says so |
