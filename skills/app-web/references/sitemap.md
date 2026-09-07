# Sitemap · app site with feature forum

Starting sitemap for the `app-web` project type. Rosenfeld takes it into `/structure` instead of
a blank `skills/structure/references/sitemap.md`, cuts what this app does not need, renames pages
in the app's own vocabulary and fills the empty columns. Nothing here is signed until he signs it.

Date: [yyyy-mm-dd] · Author: Rosenfeld · Reviewed by: Schneier · Status: preset | proposal | signed on [date]

## Hierarchy

```mermaid
flowchart TD
  H[/ Home] --> F[/features]
  H --> P[/pricing]
  H --> C[/changelog]
  H --> B[/feedback]
  H --> D[/docs]
  F --> F1[/features/pillar-1]
  F --> F2[/features/pillar-2]
  B --> B1[/feedback/r/:id]
  B -.-> LG[/login]
  H -.-> S[/security]
  H -.-> L1[/privacy-notice]
  H -.-> L2[/terms]
  H -.-> E[404]
  H ==>|primary CTA| AS[App Store / direct download]
```

The download or App Store call to action is the hero, not a page. Do not create `/download`
unless the app ships several builds (Intel and Apple silicon, beta channel) that need explaining.

## Pages

Depth = clicks from the home. Data = what the page asks the visitor for.

| URL | One-sentence intent | Template | Depth | Primary keyword | Data requested | Priority |
|-----|---------------------|----------|-------|-----------------|----------------|----------|
| / | one promise, the product visual, 3–6 feature blocks, proof, pricing summary, one primary CTA | home | 0 | | none | 1 |
| /features | how the app solves the problem, pillar by pillar | features | 1 | | none | 1 |
| /features/[pillar] | one pillar in depth. Only if the app has several distinct pillars | features | 2 | | none | 2 |
| /pricing | tiers, what each includes, trial, refund and cancellation | pricing | 1 | | none | 1 |
| /changelog | shipped releases, newest first, in the app's voice | changelog | 1 | | none | 2 |
| /feedback | the public board: submit, vote, filter by status | board | 1 | | account, request text | 1 |
| /feedback/r/[id] | one request: body, vote count, status, comments, merged duplicates | request | 2 | | account, comment text | 1 |
| /security | privacy and security posture: what is collected, where it lives, how to ask for deletion | legal | 1 | | none | 1 |
| /docs or /support | how to use the app and how to get help. A single page linking out is enough if docs live elsewhere | docs | 1 | | none | 2 |
| /login | sign in to vote or submit. Reuses the app's existing auth | auth | 1 | credentials via the provider | 1 |
| /privacy-notice | LFPDPPP privacy notice covering app and forum | legal | 1 | | none | 3 |
| /terms | terms of use, including the forum's rules of conduct | legal | 1 | | none | 3 |
| 404 | orient and send back to the home | legal | | | none | 3 |

Add if the app needs them: `/blog` only when someone is committed to writing it, `/about` when
the maker being a known person is itself proof, `/press` when there is a press kit to hand out.
Do not add a page nobody owns.

`/security` is not optional on this project type: the forum is a public-write surface and its
users are covered by Mexico's 2025 LFPDPPP. If the app has accounts of its own, add
`/account` and `/account/delete` per the base sitemap.

## Templates

| Template | Pages that use it | Wireframe |
|----------|-------------------|-----------|
| home | / | wireframes/home.md |
| features | /features, /features/[pillar] | wireframes/features.md |
| pricing | /pricing | wireframes/pricing.md |
| changelog | /changelog | wireframes/changelog.md |
| board | /feedback | wireframes/board.md |
| request | /feedback/r/[id] | wireframes/request.md |
| docs | /docs | wireframes/docs.md |
| auth | /login | wireframes/auth.md |
| legal | /security, /privacy-notice, /terms, 404 | wireframes/legal.md |

`board`, `request`, `pricing` and `changelog` map to the four style-lab patterns Frost tunes in
phase 4: Voting board, Voting board (detail), Pricing and Changelog. Feature showcase lives
inside `home` and `features`.

## Page states

The forum templates carry states the marketing pages do not; each one is designed, not improvised:

- `board`: empty (no requests yet), loading, signed out (can read and filter, cannot vote),
  signed in, filtered to zero results, rate-limited.
- `request`: open, planned, in progress, shipped, declined, merged into another request,
  removed by moderation.

## Navigation systems

- **Global** (at most 7): Features · Pricing · Changelog · Feedback · Docs, plus the primary CTA
  as a button, visually distinct from the links.
- **Local**: pillar list inside `/features`; status filter and sort inside `/feedback`.
- **Contextual**: a shipped request links to its changelog entry and back; a feature block links
  to its pillar page; the FAQ links to `/docs` and `/feedback`.
- **Footer**: legal pages, `/security`, support email, App Store link, social if any.
- **Breadcrumbs**: yes on `/features/[pillar]` and `/feedback/r/[id]`.
- **Search**: inside `/feedback` always, so people find a request before filing a duplicate.
  Site-wide only if `/docs` grows past ~50 pages.
- **Languages**: per the spec. App Store badges are localized to the page they sit on.

## Changes versus the current site (redesigns)

If the app already has a landing page, an old `/roadmap`, or feature requests living in a
GitHub issues list or a Notion board, they are inventoried and mapped in `redirects.md`. Old
request URLs that people have linked to are redirected to their new `/feedback/r/[id]`, or to
`/feedback` when there is no equivalent. New pages: [ ] · Merged: [ ] · Removed: [ ]
