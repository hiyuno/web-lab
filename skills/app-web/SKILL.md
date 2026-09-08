---
name: app-web
description: Project type. The marketing and product site for one of your own iOS or macOS apps, whose job is to explain the app and turn visitors into users, plus a public feature-request forum where users propose and vote on features and you review and ship the ones you pick. Presets the eight web-lab phases with app-specific inputs: extra discovery questions, the default sitemap (home, features, pricing, changelog, feedback, security, docs, legal), the app page brief, the Pricing, Feature showcase, Changelog and Voting board patterns, the forum's schema and rate limiting, and the public-write-surface security review. Use this skill when the user says "quiero un sitio para mi app", "página para vender mi app", "/app-web", "sitio de producto para [app]", "landing de mi app", "necesito un feature request board", "quiero que mis usuarios voten features", or asks for a product site, App Store landing page, changelog page or public roadmap for an app they own. Runs across phases with the usual checkpoints.
---

# /app-web · project type

This is not a phase. It is the on-ramp for one recurring project type: **a marketing and product
site for one of Yuno's own apps, plus a public feature-request forum**. The site explains the app
and converts visitors into users; the forum lets users propose and vote on features, and Yuno
marks them planned, in progress, shipped or declined.

It introduces no new phase number and writes no `docs/0N-*/` folder of its own. Each phase still
runs its own skill and writes to its normal location; `app-web` only tells each one what
app-specific input and checklist items to add. Read `CLAUDE.md` for the process and the rule
ownership table; the rules of content, design, performance, media, security and launch stay with
their owners and are not restated here.

**One site per app.** Not a shared multi-app site. Each app gets its own repo, domain and
`docs/`.

## Golden rule: one promise, one primary CTA, one place to ask for features

The home makes one promise, shows the product, and offers one primary call to action. Problem
before features; features before pricing; proof that names someone. Everything else on the page
competes with the CTA. The forum is the single public place where feature requests live, so the
answer to "can you add X?" is always the same link.

Sub-3 s load is a conversion requirement on this project type, not hygiene: it is measured
against the budget in `skills/build/references/lighthouserc.json` like any other site.

## Calibration and hand-off

**The architecture decision defaults to Next.js (application), not Astro.** The forum needs a
database, authenticated sessions and server actions from day one, so Cooper does not re-open
that decision each time: he records Next.js with the forum as the reason, and only argues for
Astro if the user drops the forum, which puts the project outside this skill.

**Hopper's track is always in scope.** This is not a static site with a widget. The forum is real
backend work: schema, auth, per-resource authorization, rate limiting and a moderation queue.

Exact here: one primary CTA above the fold, three to six feature blocks, an H1 of about eight
words at a plain reading level, and one vote per person per request enforced by a unique
`(request_id, voter_id)` index in the database, not in the UI. Copy you find less "professional"
is not a finding; a second competing primary CTA is.

## Step 0 · Entry

0. Read this project's own `docs/learnings.md` for every role this project touches (cooper,
   rosenfeld, frost, osmani, hopper, schneier), if it has entries yet, and
   `<web-lab>/docs/PREFERENCES.md`. This project type repeats across Yuno's apps, so prior
   lessons usually apply verbatim once promoted into the roles or this skill.
1. Confirm in one line: which app, which platforms, and that the forum is in scope. If the user
   wants no forum, see **Before you finish**.
2. If `docs/01-discovery/spec.md` already exists for this app, skip to the step that is missing.
3. If the user brings a filled `app-web-intake.md` from AppleAppLab, load it as the starting
   point before running the discovery add-on interview.

## Step 1 · Discovery add-on → `/discovery`, Cooper

Run `/discovery` as normal, and add `references/discovery-addon.md` to the interview: twelve
extra questions on platform and App Store listing, time to first value, the feature pillars, the
pricing model, real proof, existing auth to reuse for forum sign-in, who moderates the forum and
how fast, where release notes come from today, what the app collects about people, and the
domain.

Two answers steer everything downstream:

- **Time to first value** decides the primary CTA. Instant value → "Download"; setup or an
  account first → "Try it" or "Get started".
- **Existing auth** decides whether Hopper reuses the app's provider for forum sign-in or
  provisions a minimal one. Votes are authenticated, never anonymous or fingerprinted.

Cooper writes the architecture decision as Next.js with the forum as the stated reason, and the
threat model with Schneier includes the forum as a public-write surface from the start.

**Checkpoint A**: spec approved, with the app's platforms, the primary CTA, the pricing model,
the auth to reuse and the forum's moderation owner recorded in it.

## Step 2 · Structure → `/structure`, Rosenfeld

Hand Rosenfeld `references/sitemap.md` as the starting sitemap instead of a blank one: `/`,
`/features` (or `/features/*` when the app has several distinct pillars), `/pricing`,
`/changelog`, `/feedback`, `/security`, `/docs` or `/support`, and the legal pages. The download
or App Store call to action is the hero; it needs no page of its own.

He still does the real work: cutting what this app does not need, naming the pages in the app's
own vocabulary, the flows (visit → understand → download; user → submit a request → vote →
follow its status), the wireframes and, on a redesign, the redirect map. `/security` is not
optional here: the forum is a public-write surface and the app has users in Mexico under the 2025
LFPDPPP.

## Step 3 · Content → `/content`, Rosenfeld

Run `/content` as normal. The app-specific copy rules — hero promise and H1 length, the
problem→solution block before features, the three-to-six claim-plus-visual feature blocks, proof
that names people, pricing table, FAQ, changelog entries, and the App Store badge and screenshot
requirements — live in `skills/content/references/app-page-brief.md`; use it as the brief
template for the marketing pages.

Legal pages follow `skills/content/references/legal.md` as always. The `/security` page is
content written over what Schneier decides, not a new owner of security rules.

## Step 4 · Design → `/design-system`, Frost

Run `/design-system` as normal, from `skills/design-system/references/tokens.tokens.json` or a
saved preset. This project type needs four patterns from the style lab beyond the usual eight:
**Pricing**, **Feature showcase**, **Changelog** and **Voting board**. Frost tunes the direction
on those alongside the rest.

Request status badges (open, planned, in progress, shipped, declined) reuse the semantic tag
colors already in the token set — `accent`, `warning`, `success`, `danger` — plus `muted` for
declined. No new color tokens. Status is never carried by color alone: each badge has its label.

The product visual (interactive demo or short looping video, which converts better than a static
screenshot) is specified here and produced through `assets.md` and `/optimize-assets` with
Bellard, who owns weight, format and poster frames.

## Step 5 · Build → `/build`, Osmani and Hopper

Both tracks run.

**Osmani, frontend.** The marketing pages, the changelog feed and the forum's screens on the
approved tokens. The performance budget in `skills/build/references/lighthouserc.json` applies to
the marketing pages exactly as to any site, and on this project type a miss is a conversion
defect, not a nice-to-have. Headers and CSP per `skills/build/references/headers.md`.

**Hopper, backend.** The forum: requests, votes, comments, a status enum and duplicate merging
through a nullable `mergedIntoId`, on the server-only Drizzle and Zod data access layer pattern
in `skills/build/references/dal.md`, with sign-in reusing the app's existing auth. The schema,
the DAL functions, the one-vote-per-person index, rate limiting and the moderation queue are
specified in `skills/build/references/forum.md`; build from that file rather than inventing a
model.

## Step 6 · Security gate → `/security`, Schneier

The normal per-phase gate runs at every checkpoint. On top of it, Schneier reviews the forum
specifically as a **public-write surface** using
`skills/security/references/public-write-surfaces.md`: spam and abuse, the moderation queue and
who staffs it, personal data that users paste into request titles and comments under the 2025
LFPDPPP, what is shown publicly next to a vote, and deletion on request. That file's own "What
counts as a critical here" section sets what blocks the launch; nothing in it is restated here.

One thing to note and not over-engineer: Apple's rule from September 2026 requiring apps to
declare a social-media capability applies to a feature forum embedded **inside** the app. Yuno's
forum lives on the website only, so it does not apply now; revisit it only if an in-app version
is ever proposed.

**Checkpoint B**: staging up with the marketing pages and the forum, the budget met, Schneier's
verdict on the public-write surface, and the moderation owner named. Then `/qa` with Beizer and
`/launch` with Allspaw run as normal; Allspaw owns the domain, DNS and monitoring for this app's
own site.

## Step 7 · Retro

At the close of each phase, the usual retro, written into this app's own `docs/learnings.md`
(create it from `<web-lab>/docs/learnings-template.md` if it does not exist yet), under the
section for every role involved: cooper, rosenfeld, frost, osmani, hopper, schneier. Bring the
file to a web-lab session at project close so it merges into the persistent
`<web-lab>/learnings/<role>.md` files, with date and app name preserved. A correction about
style, tone or tooling goes to `docs/PREFERENCES.md` right then.

This project type recurs across Yuno's apps, so patterns compound: a question that turned out to
matter, a section that did not convert, a forum rule that stopped spam, and a lesson seen three
times gets promoted into this skill or into `references/discovery-addon.md`.

## Before you finish

| Symptom | Fix |
|---------|-----|
| The app has no App Store listing yet | primary CTA becomes the waitlist or TestFlight, not "Download"; no App Store badge until there is a real link, and no fake one as a placeholder |
| The app has no auth of its own | Hopper provisions a minimal one with an established provider in step 5; forum sign-in reuses it and the app adopts it later. Never fall back to anonymous or fingerprinted votes |
| Yuno wants to skip the forum for one app | this skill assumes the forum is in scope. If he truly does not want it, do not strip steps out of here: run the plain `/discovery` → `/structure` → `/content` → `/design-system` → `/build` path, where Astro is back on the table |
| More than one primary CTA above the fold | keep the one the time-to-first-value answer picked; demote the rest to secondary |
| Features listed before the problem they solve | problem→solution block first; a feature list with no stated problem does not convert |
| A static screenshot where the demo should be | interactive demo or short looping video, weight and format owned by `/optimize-assets` |
| Vague proof: "loved by thousands", "trusted by many" | name someone or drop the block; a claim without a source is not published (`/content` rule) |
| A white App Store badge on a light hero, or an English badge on a Spanish page | Apple's marketing guidelines: black badge by default, white only when black is visually heavy, badge localized to the page |
| Votes deduplicated only in the UI | unique `(request_id, voter_id)` index in the database; the UI is a convenience, not the control |
| The forum ships with no moderation queue or no named moderator | Schneier critical; name the person and their response time before launch |
| A `/security` page written by whoever wrote the marketing copy | it states what Schneier decided; he reviews it before it ships |
| Changelog entries written as commit messages | user-visible releases in the app's voice, per `app-page-brief.md` |
| Marketing pages over the Lighthouse budget because of the hero video | Bellard's job, not a budget exception |
