# Variants · step 4.1

Adapted from `variant` in Jakub Krehel's `interfaces` collection (MIT). Here it is a Frost step
with a user checkpoint; there it is a skill only the user triggers.

## Different answers, not different tints

Three directions that differ only in accent color teach nothing. Each variant is a different
answer to the same brief on **one axis**:

| Axis | Rule owner | What varies |
|------|------------|-------------|
| Structure | `better-layout` | grouping, order, columns, what collapses |
| Density | `better-layout` | spacing scale, hit areas, how much fits |
| Emphasis | `better-colors` | where solid color goes, what recedes |
| Type | `better-typography` | scale steps, weight contrast, measure |
| Voice | `better-writing` | labels, tone, how much copy |

Pick one primary axis and give each variant a different position on it. Secondary choices follow
from the axis: a dense variant may need a smaller type step, and that is coherence, not a second
axis. Varying everything at once produces three unattributable results.

## The floor every variant clears

A variant that wins on looks and fails an escalation trigger (CLAUDE.md, shared review method) is
not a candidate. Accessible name on every control, keyboard reaches everything, visible focus,
nothing clips at 320 px, no meaning by color alone. The floor is not an axis and never trades
against one.

## Procedure

1. **One piece.** The whole home is not a piece; the hero or the product card is. Start with the
   one that defines the others and offer the rest as later rounds.
2. **Read the ground.** Editorial guide, wireframes, tokens if they exist, the user's tastes in
   `docs/PREFERENCES.md`. With no prior brand: neutral grays, one accent and the system font, and
   say so.
3. **Name the axis and the three positions before writing code.** Names that say the direction:
   `Quiet`, `Editorial`, `Dense`; never `Option A`. Three by default; five only if the space calls
   for it.
4. **Build them on the real page** of the prototype, with the real copy from the briefs and the
   real number of items. A URL parameter selects them (`?variant=dense`) and a floating control,
   visibly outside the design system, switches. One at a time, full size; thumbnails lie about
   space.
5. **Walk through them yourself first**, at 375 and 1280, with a clean console.
6. **Present the table and stop.** No favorite marked.

| Variant | Axis position | Right when | Costs |
|---------|---------------|------------|-------|
| | | | |

Say where the picker runs and at which width you judged. If asked which, answer by frequency of
use and product personality, not by which you enjoyed building.

7. **Checkpoint A.** The user chooses. Promote that variant into the system following the
   project's conventions and delete the rest and the picker, unless they ask for another round:
   then keep the picker and take new positions around the chosen one.

## Before you finish

| Symptom | Fix |
|---------|-----|
| Variants differ only in color or copy | move one to another axis position or cut it |
| Every axis varies at once | vary one; let the rest follow |
| Judged on a blank route | mount them on the page that will contain them |
| Lorem ipsum, three rows, "Jane Doe" | real copy and the real item count |
| The boldest one skips keyboard or focus | clear the floor or drop the direction |
| A favorite marked in the table | each one's cost and let the user choose |
| Picker styled with the project's tokens | keep it visibly outside the system |
| Picker left behind after promotion | delete it unless asked to keep it |
