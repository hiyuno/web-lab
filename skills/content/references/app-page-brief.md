# App page brief · [app name]

Companion to `page-brief.md`, not a replacement: use that template's fields (intent, audience,
SEO, headings, microcopy, internal links, review) for every page below. This file adds what is
specific to a marketing/product website for one of Yuno's own iOS/macOS apps plus its public
feature-request forum — the page types, the order, and the fields those page types need that a
generic brief does not ask for. Loaded by the `/app-web` skill.

Date: [yyyy-mm-dd] · App: [name] · Platforms: [iOS | macOS | iOS + macOS] · Writes: [name] ·
Approver: [name]

## Site-wide inputs (collect once, reuse on every page)

- One-sentence promise: [ ] (the app's job, not its feature list)
- App Store URL: [ ] · Mac App Store URL (if applicable): [ ]
- App Store badge language for the target market: [ ] (Spanish for Mexico if that is the
  audience) — use Apple's own badge assets from
  developer.apple.com/app-store/marketing/guidelines, black badge by default, white only if black
  reads too heavy against the page background, never redraw or recolor the badge
- Has a web component with its own signup? [yes → CTA can be "Get started" | no → CTA is
  "Download" / "Get the app"]
- Named proof available today: [testimonials with real name/role/company | install count | App
  Store rating | press logos | none yet]. Anything not on this list stays out of the copy — see
  "Proof TBD" below, never a placeholder client name.
- Support/contact email shown on the site: [ ]
- Maker contact line, for a solo-built app (a real trust signal, not boilerplate): [ ] (e.g. "I
  build this myself. Have an idea? Email me or ping me on X.") Place it near a feature or widget
  list, or in the footer — wherever it reads as a genuine offer to hear from users, not a
  contact-us afterthought. Skip entirely if the app isn't solo-built, or Yuno doesn't want to be
  its public face.
- Privacy notice URL (real, approved page): [ ]

### Proof TBD

If proof is not secured yet, say so here instead of writing a placeholder quote or a stock
number. Design may use dummy proof to lay out the page; this brief may not.

| Page/block that needs proof | What kind | Status | Owner | Due |
|------------------------------|-----------|--------|-------|-----|
| | quote / install count / rating / press logo | TBD | | |

---

## Home

Fill `page-brief.md`'s fields (intent, audience, SEO, headings, microcopy, links, review) plus:

### Structure order

Problem → solution → product → features → proof → pricing → FAQ. Do not lead with features:
the reader has to recognize the problem before a feature list means anything to them, and
features-first tests worse on conversion. Do not reorder without a reason recorded here.

### Hero

- Promise (one sentence, the reason this app exists): [ ]
- H1: [ ] — under ~8 words / ~44 characters, states the promise, not a feature name
- Primary CTA: [Download / Get the app | Get started, only if there is a web signup] → [target]
- Secondary CTA (optional): [ ] → [target]
- Product visual: [short looping video | interactive demo] — prefer this over a static
  screenshot in the hero; screenshots belong in the feature section below, not here
- Visual shows: [the one moment that sells the promise, not a menu of features]

### Problem block

- The problem in the reader's words (not the app's): [ ]
- Who has this problem: [ ]

### Solution block

- How the app solves it, one paragraph: [ ]
- Direct answer (40-60 words, per `page-brief.md`): [ ]

### Feature showcase (3-6 blocks, no exceptions)

One claim + one visual per block. No block ships without a visual. A claim is one concrete
sentence ("Search finds text inside PDFs, not just filenames"), not a category label
("Powerful search").

When the app's features map to distinct moments or contexts (a work mode, a daily routine, a
business view), frame the claim as that moment ("Focused work.", "Your everyday.", "Your
business.") instead of a capability name ("Custom modes."). This reads as a story of the
reader's day, not a spec list. Use it only when it genuinely fits — a plain benefit sentence
beats a forced persona.

| # | Claim (one sentence, concrete) | Visual | Visual type |
|---|----------------------------------|--------|-------------|
| 1 | | | screenshot / short clip / diagram |
| 2 | | | |
| 3 | | | |

### Proof block

Named quotes first (real name, role, company) — they beat aggregate numbers. List install
counts, ratings and press logos as secondary, only if genuinely available.

| Proof | Type | Name/role/company or source | Verified by | Where it goes |
|-------|------|------------------------------|-------------|----------------|
| | named quote / install count / rating / press logo | | | home, block [n] |

### Pricing teaser

One line pointing to the Pricing page: [ ]. No plan details duplicated here.

### FAQ

3-5 questions a skeptical reader still has after seeing pricing. Pull the two pricing
objections from the Pricing page's FAQ if they apply site-wide.

| Question | Answer (plain language) |
|----------|--------------------------|
| | |

### Content inputs needed from Yuno

- [ ] Final promise sentence and any wording he wants kept verbatim
- [ ] Real quotes (name, role, company) or explicit "not yet" for each
- [ ] Screen recording or clip for the hero visual
- [ ] Confirmation of which CTA applies (Download vs. Get started)

### What NOT to do

- Do not open with a feature grid before the problem is stated.
- Do not use a static screenshot as the hero visual when a clip or demo is available.
- Do not invent a testimonial, install count, or press logo. Mark it TBD instead.
- Do not stack more than 6 feature blocks; cut to the ones that differentiate.
- Do not force a persona/moment framing onto features that don't naturally map to one.

---

## Features

Fill `page-brief.md`'s fields plus:

### Purpose

Give the reader who is already past the "what is this" stage the full, honest feature list,
each one still tied to a benefit, not a spec sheet.

### Feature blocks

Same rule as the home showcase: one claim (concrete, benefit-first) + one visual, no exceptions.
This page can carry more blocks than the home teaser, but each still needs its own visual.

| # | Claim | Visual | Platform (iOS / macOS / both) |
|---|-------|--------|-------------------------------|
| 1 | | | |

### Small delighters (optional)

Polish details too small to earn their own claim-plus-visual block, but real enough to mention:
a bold five-to-eight-word title plus one plain sentence, no visual required (dockset.app's "The
little things, taken care of" section is the reference — six short entries, no icons, the title
alone does the work). Use only for genuine small wins; padding this table to look thorough is
worse than leaving it empty.

| Title (bold, short) | One sentence |
|-----------------------|-----------------|
| | |

### Screenshot requirements

- Real device frames, not bare crops. Device: [iPhone model | Mac frame].
- Consistent device/OS chrome across the whole set (same device, same OS version, same status
  bar/time if visible).
- Each screenshot has a one-line caption stating the benefit shown, not the feature's name (for
  example "Never lose a draft again", not "Autosave").

| Screenshot | Device frame | Caption (benefit, not feature name) |
|------------|---------------|----------------------------------------|
| | | |

### Content inputs needed from Yuno

- [ ] Full feature list with a one-line benefit per feature
- [ ] Screenshots or a build to capture them from, per platform
- [ ] Which features are iOS-only, macOS-only, or both
- [ ] Any small polish details worth a "delighters" line, or confirmation there are none

### What NOT to do

- Do not caption a screenshot with the feature's internal name.
- Do not mix device frames or OS chrome within one screenshot set.
- Do not list a feature with no visual "for now" — hold the row until the visual exists.
- Do not pad the delighters table with restated main features; leave it empty if there's nothing
  genuinely small to add.

---

## Pricing

Fill `page-brief.md`'s fields plus:

### Plans

| Plan | One-line value pitch | Price | Recommended tier? |
|------|------------------------|-------|---------------------|
| | | | [tag: yes/no — only one plan carries this tag] |

### What differs between plans

List only what changes from plan to plan, not the full feature set repeated per column. If a
feature is in every plan, it does not belong in this table.

| Feature (only where it differs) | [Plan A] | [Plan B] | [Plan C] |
|-----------------------------------|----------|----------|----------|
| | | | |

### FAQ — must address the two most common pricing objections

| Question | Answer (plain language) |
|----------|--------------------------|
| [price objection, e.g. "Why is this a subscription?"] | |
| [second objection, e.g. "What happens to my data if I cancel?"] | |
| [additional pricing questions] | |

### Content inputs needed from Yuno

- [ ] Final plan names and prices, including any regional pricing
- [ ] Which plan is the recommended tier and why
- [ ] The two objections he hears most from real users or support email
- [ ] Refund/trial/cancellation policy in plain language

### What NOT to do

- Do not repeat the full feature list per plan column; scope the table to differences only.
- Do not tag more than one plan as recommended.
- Do not leave the two pricing-objection FAQ rows generic ("Questions? Contact us") — answer
  the actual objection.

---

## Changelog

Fill `page-brief.md`'s intent/audience fields plus:

### Entry format

Every entry: date, one type tag, a plain-language title, one sentence written for the user, not
the engineer.

| Date | Type | Title (plain language) | Description (one sentence, for users) |
|------|------|--------------------------|------------------------------------------|
| [yyyy-mm-dd] | New / Improved / Fixed | | ("no more accidental deletes", not "fixed race condition in delete handler") |

### Content inputs needed from Yuno

- [ ] Raw release notes or commit summaries to translate into user-facing language
- [ ] Confirmation of the type tag per entry (New / Improved / Fixed)

### What NOT to do

- Do not paste engineering commit messages or ticket IDs as the description.
- Do not use a type tag outside New / Improved / Fixed.
- Do not combine multiple unrelated changes into one entry; one row per user-visible change.

---

## Feedback (forum)

Fill `page-brief.md`'s fields plus:

### How it works (one sentence, shown up top)

[ ] (e.g. "Propose a feature, vote on what others proposed, and Yuno reviews the most-voted
ideas and ships what he picks.")

### Status vocabulary (shown to users, exactly these terms)

| Status | Plain-language meaning |
|--------|--------------------------|
| Open | Submitted, not yet reviewed |
| Planned | Reviewed and accepted; not started |
| In progress | Being built right now |
| Shipped | Live in the app — say which version |
| Declined | Reviewed and not going forward — say why in one line when possible |

### Before you post (nudge line, shown near the submit form)

[ ] (e.g. "Search first — someone may have already proposed this. One request per idea keeps
votes from splitting.")

### Content inputs needed from Yuno

- [ ] Confirmation of the exact status labels and their order in the UI
- [ ] Whether declined items show a reason and how much detail
- [ ] Moderation rules (what gets removed, spam policy) if any

### What NOT to do

- Do not invent extra status labels beyond the five above; if a sixth is needed, that's a
  product decision for Yuno, not a copy decision here.
- Do not skip the "before you post" nudge — duplicates are the main cost of an open forum.
- Do not promise a timeline ("coming next month") the status vocabulary does not support.

---

## Security & privacy

Fill `page-brief.md`'s fields plus the `legal.md` template's controller-data and privacy-notice
sections (this page links to, and must agree with, the real privacy notice — it does not
replace it). Coordinate with `skills/security/references/legal-mx.md` and Mexico's 2025 LFPDPPP;
loop in Schneier before publishing.

### Why this page exists

The forum is a public write surface: anyone can read what a person posted and, depending on
the forum's settings, their name or handle. This page tells users in plain language what that
means before they post.

### What's public vs. private (forum-specific — plain language, not legal language)

| Data | Public or private | Where it's shown |
|------|---------------------|-------------------|
| Display name or handle | [public/private] | next to every post and vote |
| Request text | public | the forum post |
| Vote count | public | the forum post |
| Email address | private | never shown, used only for [account / notifications] |
| [any other field the forum collects] | | |

### Content inputs needed from Yuno

- [ ] Confirmation of what the forum actually shows publicly (check the real UI, don't assume)
- [ ] Link to the approved privacy notice (from `docs/03-content/legal.md`)
- [ ] Whether users can post anonymously or must use a real identity

### What NOT to do

- Do not describe the forum's data handling in terms that don't match what the UI actually
  shows — verify against the built forum, not the spec.
- Do not duplicate the full privacy notice here; link to it.
- Do not publish this page without Schneier's review — it governs a public write surface with
  user-generated content.
