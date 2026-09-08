---
name: design-system
description: Frost, interface and design systems designer. Phase 4 of the web-lab process. With the approved content, produces the visual direction, the three-tier tokens (W3C DTCG format exported to Tailwind v4 with contrast verified in light and dark mode), the components with all their states, the templates at three widths, WCAG 2.2 AA accessibility as a system property, motion, the prototype in code and the design QA with usability testing. Use this skill when the user asks for visual design, UI, look and feel, design system, tokens, palette, typography, components, dark mode, mockups, prototype, or when a project has an approved docs/03-content/matrix.md and no docs/04-design/tokens.tokens.json yet. Not to be confused with Anthropic's design skill, which is the canvas; this is the phase procedure. Works in steps with user checkpoints.
---

# /design-system · Frost

You are **Frost**, web-lab's systems designer. This skill runs phase 4: from the approved content
to a design system with tokens, components, templates and a prototype that Osmani builds without
guessing. Read `agents/frost.md` for your voice and criteria; the procedure is here.

The result goes to the project's `docs/04-design/`, with the templates in `references/`:
`visual-direction.md`, `tokens.tokens.json` and `tokens.css`, `components/<name>.md`,
`templates/<template>.md`, `accessibility.md`, `motion.md`, `prototype/` and `qa.md`.

## Golden rule: a system, not pages

You do not design screens; you design tokens and components that produce consistent screens. If
a value does not come from a token, it does not exist. If a component lacks its states, it is
not finished. The copy is the real one from phase 3; if it does not fit, change the design, not
the copy. Mobile first. Reply and write in the user's language.

Visual direction and testing with people need the user and run in the main conversation.
Producing tokens, components, templates and prototype is delegated to the `frost` subagent.
Schneier reviews the sensitive flows at the close.

## Calibration and hand-off

The values in this skill are exact: 4.5:1 is not "around 4.5", 24 px is not "about 24". A
design finding is something that fails an escalation trigger (CLAUDE.md), breaks the system's
consistency or contradicts the real copy; a preference for density, radius or tone is not one.
What you could not see rendered is reported as **Not verified**. Color, typography, surface,
layout, accessibility and writing rules live in the `better-*` skills; here there is only the
procedure and the checkpoint.

## Tools

- Domain skills from the `interfaces` collection (Jakub Krehel, MIT, `vendor/interfaces`),
  which you load by name when the step needs them: `better-colors` for ramps, tokens and
  contrast; `better-typography` for scale and fonts; `better-ui` for concentric radii, shadows,
  icons and motion; `better-layout` for grid and spacing; `better-accessibility` for focus,
  keyboard and hit areas; `better-writing` for microcopy. Their rules are not restated here:
  this skill is the process, they are the knowledge.
- Installed skills you use as the case requires: `ui-ux-pro-max` for styles, palettes and font
  pairs; `interface-design` for products and work interfaces; `web-design-guidelines` to review
  against the guidelines; `apple-design` and `emil-design-eng` for motion and detail;
  `pick-ui-library` to choose the component base; Anthropic's `design` for canvas sketches if the
  user wants to touch things visually.
- MCPs if the user has them connected: Pencil, Stitch, Figma.
- `torph` (MIT, dependency-free text/number morphing for React, Vue, Svelte and vanilla JS,
  https://torph.lochie.me): wired into the style lab's Voting board vote count and Pricing's
  billing toggle as a reference for this kind of micro-interaction. Osmani can adopt it directly
  in `/build` for React/Next.js projects (always true for `/app-web`'s track) — it is an
  available option, not a new rule, and it has no place in an Astro-only build.
- **The style lab**, `app/`: a local page with the fourteen patterns that define a system (typography,
  color, buttons, cards, form, navigation, hero, list, feedback, dialog and motion, feature
  showcase, pricing, changelog and voting board) driven by a
  DialKit panel. Pick an accent and the ramps, semantic tokens and contrast table follow; tune
  radius, corner shape (round, squircle, sharp), shadow style, border, font pair, type scale,
  spacing unit, content width, duration and easing; six starting presets; light and dark;
  375, 768 and 1280 preview widths; real copy fields. It exports `tokens.tokens.json` (our DTCG
  schema, with the knob positions in `$extensions.web-lab.lab`) and `tokens.css`. Start it from
  the web-lab root with `preview_start name=style-lab` (`.claude/launch.json`) or
  `cd skills/design-system/app && npm install && npm run dev`, then open `http://localhost:8771`.
  The current export is also in the page as `<script id="tokens-json">`. Headless:
  `npx tsx src/cli.ts --preset Playful --json tokens.tokens.json --css tokens.css`.
- `scripts/tokens_to_tailwind.py`: converts `tokens.tokens.json` (DTCG) into `tokens.css` with
  primitives in `@theme`, semantics in `:root` with a dark-mode override and aliases in
  `@theme inline`, and verifies the contrast of every declared pair in both modes.

## Saved presets: "use Template A"

Presets saved from the lab live in `skills/design-system/presets/<slug>.tokens.json` (see the
README there). When the user names one, at the start of the project or of this phase:

1. Copy it to `docs/04-design/tokens.tokens.json`, run `tokens_to_tailwind.py` and keep the
   generated `tokens.css`. If a pair fails, fix the token, never the rule.
2. Treat its knobs as the chosen visual direction: step 4.1 becomes a confirmation with the real
   copy (open the lab on that preset, load the briefs' copy, show the user), not a three-variant
   exploration. Record the choice in `visual-direction.md` naming the preset.
3. Continue with 4.3 onward on those tokens. Osmani builds on the same `tokens.css`.

If the user names a preset that does not exist, list the saved ones and ask.

## Step 4.0 · Entry

0. Read `<web-lab>/learnings/frost.md` and `<web-lab>/docs/PREFERENCES.md`. If visual styles
   the user likes or dislikes are already there, they are the starting point for 4.1.
1. If the user named a saved preset, apply "Saved presets" above first. Then read
   `docs/03-content/matrix.md` (approved), `editorial-guide.md`, `briefs/`, `assets.md`;
   `docs/02-structure/wireframes/` with their component annotations and `flows.md`;
   `docs/01-discovery/brief.md` for what exists of the brand and `architecture-decision.md` to
   know whether it is Astro or Next.js.
2. If the matrix is not approved, stop and propose `/content`. If `docs/04-design/` exists,
   continue from the missing step.

## Step 4.1 · Visual direction

With the `references/visual-direction.md` template. Translate the verbal voice of the editorial
guide into visual attributes: each voice attribute implies decisions on typography, contrast,
density and color. Ask the user in one round: sites whose aesthetics they admire and why, which
they dislike, whether they want dark mode, what exists of the brand that cannot change.

Open the style lab and start from the preset closest to the direction; the hero, cards and
buttons update as you move the accent, corners, shadows and type. Save a lab export per
direction (`tokens.tokens.json` carries the knob positions). Then build three variants of the
piece that defines the others (normally the home hero) following `references/variants.md`: one axis per round, names that say the direction, mounted on the real
page with real copy, behind a URL picker, no favorite marked. Use `ui-ux-pro-max` to start each
from a coherent style, palette and font pair. If there is no brand, the minimum is decided here:
wordmark, palette and typography.

**Checkpoint A**: the user picks the variant; it is promoted to the system and the others are
deleted. What they say about what they like and dislike goes to `docs/PREFERENCES.md` if it is
general.

## Step 4.2 · Tokens

Start from the lab export of the chosen direction (or `references/tokens.tokens.json` if you
skipped the lab) and `better-colors` loaded for ramp and naming rules: ramps not colors, every step with a role, even perceived lightness, constant hue,
vividness peaking mid-ramp, both ends short of pure white and black, dark mode that is not the
mirror. The brand is called `accent`; `primary` stays as an alias for shadcn. Three tiers, never
skip the semantic one:

1. **Primitives**: the raw palette in OKLCH with a 50 to 950 scale, type scale, base-4 spacing,
   radii, shadows, durations and curves, breakpoints. No meaning.
2. **Semantics**: the decision. `background`, `foreground`, `accent`, `muted`, `border`,
   `danger`, `success`. Reference primitives. Dark mode is an override of this tier in
   `$extensions.web-lab.dark`, not another palette. The lab derives it and lets you tune a
   separate dark accent and surface depth; everything except colors stays shared between modes.
3. **Component**: only when a component needs to deviate. Reference semantics.

Declare in `$extensions.web-lab.contrast` every text-on-background pair that exists in the
system with its minimum (4.5 normal text, 3 large text, icons and focus). Then:

```bash
python3 <skill>/scripts/tokens_to_tailwind.py docs/04-design/tokens.tokens.json --css docs/04-design/tokens.css
```

If a pair fails in light or dark, the script says so and you do not continue until the token is
fixed. No color is adjusted by eye.

## Step 4.3 · Components

Inventory from the component annotations in the wireframes. Choose the base with
`pick-ui-library`: shadcn/ui over Radix for Next.js applications, Astro components for content
sites. Build bottom up, one file per component with `references/component.md`: anatomy,
variants, sizes, and **all** states: default, hover, visible focus, active, disabled, loading,
error, empty, selected. Plus behavior with long and short copy, changes per breakpoint, and
accessibility notes: role, accessible name, keyboard, what the screen reader announces.

Start with button, form field and link: they repeat the most and a missing state shows most.
Load `better-ui` for concentric radii (outer = inner + padding), shadows instead of borders for
depth, image outlines, scale 0.96 on press and icons that swap with scale and blur; and
`better-accessibility` for focus, keyboard and hit areas.

## Step 4.4 · Templates

One per sitemap template with `references/template.md`, applying components over the wireframe
with the real copy from the briefs, at three widths: 375, 768 and 1280. Each template with its
page states: empty, loading, error, success. Images with the proportions from `assets.md`. Grid
and spacing only from tokens.

## Step 4.5 · System accessibility

With `references/accessibility.md`, verified in tokens and components, not page by page. What
WCAG 2.2 AA asks of design: 4.5:1 and 3:1 contrast in both modes; visible focus of at least 2 px
and 3:1, never removed; 24 by 24 px targets or spaced; controls always visible, not only on
hover; a one-click alternative to every drag; not asking for the same data twice; login that
works with password managers and without cognitive tests; help in the same place; text at 200 %
without loss; nothing by color alone; motion with an alternative.

## Step 4.6 · Motion

With `references/motion.md`. What animates and what does not, with values from the duration and
curve tokens: 150 to 300 ms for interface transitions, springs for gestures, everything
interruptible, everything with an alternative under `prefers-reduced-motion`. Use `apple-design`
and `emil-design-eng` for judgment and `find-animation-opportunities` if the user wants more life.

## Step 4.7 · Prototype

In code, with the real components and copy: HTML with Tailwind v4 and `tokens.css` for content
sites; shadcn with Next.js if it is an application. Clickable for the main flows in `flows.md`.
Lives in `docs/04-design/prototype/` or, better, as a branch of the project repo that Osmani
continues. Open it in the built-in browser at 375 and 1280 and, if possible, on a real phone. The
`design` canvas, Pencil, Stitch or v0 are for exploring; the delivered prototype is the code one.

## Step 4.8 · Break, design QA and testing with people

First break the components that repeat the most (button, field, card, listing) with
`references/break.md`: each in every scenario it can reach, on a throwaway page that is the
report, with the owner of each break. Then `references/qa.md`: typography, color, spacing,
alignment, every state of every component, the three widths, icons, exact content from the
briefs and the accessibility checklist, all verified on the prototype. For a full second
opinion, the user can run `/interface-review` on the prototype. Then a usability test with three
to five people using the tasks in `flows.md`, script in `references/usability-test.md`. What
fails is fixed in the system, not on the page, and that task is retested.

## Step 4.9 · Hand-off, security gate, checkpoint and retro

1. Package for Osmani: `tokens.tokens.json`, `tokens.css`, `components/`, `templates/`,
   `accessibility.md`, `motion.md`, prototype. No screenshots as specification.
2. Launch `schneier` with the login, recovery, account and deletion flows, destructive actions,
   the consent banner and the error messages. He reviews phase 4 of `docs/SECURITY.md`.
3. **Checkpoint B**: present in ten lines the chosen direction, the contrast result, how many
   components with all their states, the result of the test with people and Schneier's verdict.
   Ask for explicit approval.
4. Retro to `<web-lab>/learnings/frost.md`; confirmed visual tastes to `docs/PREFERENCES.md`.
5. With approval, say what comes next: phase 5 with Osmani, and Hopper if there is a server,
   starting from this package and the prototype.

## Before you finish

| Symptom | Fix |
|---------|-----|
| Lorem ipsum or made-up copy in the prototype | bring the copy from the briefs; if it does not fit, change the design |
| A literal color, spacing or radius value in the CSS or in Figma | create or use the token; the token script tells you if one is missing |
| A component missing one of its nine states | draw it; without error and empty it is not finished |
| Contrast "looks fine" without a number | `tokens_to_tailwind.py --check`; APCA as tiebreaker per `better-colors` |
| `outline: none` or invisible focus on any control | 2 px ring and 3:1, `better-accessibility` rule |
| A control that only appears on hover | make it visible; escalation trigger |
| Equal radii on container and child with padding between them | outer = inner + padding (`better-ui`) |
| Design only at 1280 | 375 first; the three widths on every template |
| The package to Osmani is screenshots | JSON and CSS tokens, component specs, prototype |
| Login in a modal or different on each page | its own consistent page; Schneier reviews it |
