# User preferences

Stable decisions and tastes of Yuno that apply to every role and project. Roles read it on
start. It is updated when a preference is confirmed in a phase retro or when the user states it
explicitly. Every line carries the date it was confirmed.

## Way of working

- 2026-09-05 · Language: the repository (skills, roles, docs, templates, code, commits) is in
  English. Roles talk to the user in the user's language, normally Spanish. Project
  deliverables are written in the language the spec sets.
- 2026-09-04 · One phase at a time, with explicit approval between phases. Never advance by
  assuming yes.
- 2026-09-05 · First the researched industry standard, then the skill, and adjustments come
  from testing it on real projects.
- 2026-09-05 · Security as a cross-cutting criterion with veto power, not as a final phase.
- 2026-09-04 · Short summaries, tables for findings and numbers, commands in code blocks.
- 2026-09-05 · Interface knowledge comes from Jakub Krehel's `interfaces` collection as a
  dependency (submodule); our skills only carry process. Each rule lives in one place.
- 2026-09-05 · Review method: evidence not taste, "Not verified" instead of assuming, one-word
  verdict, escalation triggers, cheapest fix first.

- 2026-09-06 · Rule, not a preference: the orchestrator never does the work itself. Every task
  goes to an agent (an existing role when there is one, otherwise a general-purpose agent) with
  the smallest model that covers it: Haiku for small well-specified edits, Sonnet for standard
  implementation from a spec or template, Opus for judgment, research and security. The
  orchestrator writes the instruction, picks the model, verifies and commits.
- 2026-10-05 · Cooper is the project lead and the main session's identity: he talks with the
  user, researches and brainstorms when the idea is vague, runs discovery, and organizes the team
  through every phase. Opens with "¿Qué web vamos a hacer hoy?".
- 2026-10-05 · The ladder, same as AppleAppLab: Yuno → Yubot → Web Master → Cooper → roles.
  Nobody skips a level. Cooper does not modify himself or the team; he proposes and the Web
  Master (`/web-master`, web-lab only) decides with Yuno. Rules in [`LADDER.md`](LADDER.md).

## Stack and tools

- 2026-09-04 · Astro for content sites, Next.js for applications, Tailwind v4 with tokens,
  Vercel as default hosting. *Hosting superseded on 2026-10-08: Vercel only.*
- 2026-09-04 · Tools without heavy dependencies: Python stdlib, Pillow, ffmpeg. Node only when
  truly needed. Exception agreed on 2026-09-05: the style lab uses Vite, React and DialKit
  because DialKit is the control panel the user asked for.
- 2026-09-04 · Roles are named after a real figure in their discipline.
- 2026-09-05 · Brand token: `accent` in the semantic tier, with `primary` as an alias so shadcn
  does not break.
- 2026-10-08 · GSAP 3.15 for animation that CSS transitions can't do well (timelines,
  scroll-driven, SplitText, DrawSVG), only on sites with real animation; simple sites stay on CSS.
  Every site that uses GSAP also gets Lenis smooth scroll, switched off under
  prefers-reduced-motion. No Barba: page transitions use the framework's own (Astro View
  Transitions, Next.js). *Astro View Transitions superseded on 2026-10-08, below.*
- 2026-10-08 · One route per layer: hosting on Vercel only (no Netlify); auth with Better Auth
  only, no alternative listed, never home-grown; Astro 6 for content sites; Drizzle as the only
  ORM. *Astro 6 superseded on 2026-10-08, below.*
- 2026-10-08 · Astro 7 for content sites (`astro@^7`), replacing Astro 6 above.
- 2026-10-08 · Page transitions on Astro are CSS cross-document view transitions
  (`@view-transition { navigation: auto; }`), off under prefers-reduced-motion; no
  `<ClientRouter />`, so Astro's built-in CSP (`security.csp`) stays on every site.
- 2026-10-08 · Cookies: the default is a consent banner with Accept and Reject equally easy,
  honoring Global Privacy Control (GPC present = treated as rejected, no dark pattern), nothing
  non-essential before consent. Reference tool: Klaro (open source, BSD-3-Clause, self-hosted — no
  SaaS dependency; chosen over Cookiebot, which is a paid Usercentrics SaaS). Documented exception:
  a site using cookieless analytics only (e.g. Plausible) needs no banner.

## Context

- 2026-09-05 · Based in Mexico: the 2025 LFPDPPP applies (in force since 21 March 2025,
  authority Secretaría Anticorrupción y Buen Gobierno); GDPR if there are users in Europe.

## Design and content

To be discovered in the first projects: preferred voice, visual styles liked and disliked,
recurring references.
