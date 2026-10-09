# Legal deliverables and data inventory · index

Schneier's single list of **which legal pages and documents a project must produce**, and the
**data inventory** that drives them. This file is the index and the per-project deliverable list;
the regime detail is not here. Each regime lives in its own reference and is cited, never restated:

- Mexico's 2025 LFPDPPP → `legal-mx.md`
- GDPR (EU/UK users) → `privacy-eu.md`
- CCPA/CPRA and GPC (California users) → `privacy-us.md`
- EAA accessibility (EU users + covered service or selling into the EU) → `accessibility-law.md`
- COPPA and minors (children under 13, or minors' data) → `privacy-minors.md`

Schneier **owns the list** (what each deliverable must say, which regimes apply); Rosenfeld
**drafts the pages** (`skills/content/references/legal.md`, the "how it is written"). Summary for
the threat model and the gates, not legal advice; a human legal review precedes any public launch
that touches sensitive data or minors.

## Spend the minimum

Per `CLAUDE.md`'s efficiency rule (item 7), the legal review is **milestone work, not
per-change**: the deliverable list and data inventory are produced **once in phase 1** (with the
regime detection in `skills/discovery/references/threat-model.md`), the pages are **drafted in
phase 3** (Rosenfeld, `/content`), their **presence is checked in phase 6** (Beizer runs it,
Schneier reads it), and the whole set is confirmed **before launch** (phase 7). A single new form,
cookie or third party does not re-run the review — it updates the data inventory row and, if it
changes a legal basis or adds a deliverable, flags it to Schneier.

## 1 · Default legal deliverables

Produced in phase 1 as the project's list, from the regime detection. A row is **required**,
**conditional** (only if its trigger holds) or **n/a**. "Owner" is always Schneier for the content
and Rosenfeld for the drafting; the column notes anything specific. All pages live in the content
phase's legal set (`docs/03-content/legal.md`, published as the site's legal pages).

| Deliverable | When required | Owner | Where it lives | Regime refs |
|-------------|---------------|-------|----------------|-------------|
| **Privacy notice / aviso de privacidad** (full + short next to each form) | Always, as soon as any personal data is collected (almost every site with a form) | Schneier defines content; Rosenfeld drafts | `docs/03-content/legal.md` → published `/privacy` | `legal-mx.md` (base) + `privacy-eu.md`, `privacy-us.md`, `privacy-minors.md` as they apply |
| **Terms & conditions** | When there is a sale, a user account, or user-generated content | Schneier / Rosenfeld | `docs/03-content/legal.md` → `/terms` | `legal-mx.md`; `privacy-eu.md` (contract as a lawful basis) |
| **Cookie policy + consent banner copy** | Only when non-essential / tracking cookies exist. A **cookieless-analytics-only** site needs **none** — state that in the privacy notice instead | Schneier / Rosenfeld | `docs/03-content/legal.md` → `/cookies` | Klaro decision in `skills/build/references/headers.md` ("Consent and GPC"); `privacy-us.md` (GPC); `privacy-eu.md` (consent standard) |
| **Accessibility statement** | When the EAA applies (EU users + covered service or selling into the EU, and not an exempt microenterprise-service) | Schneier flags; Rosenfeld drafts; Beizer confirms claims | `docs/03-content/legal.md` → `/accessibility` | `accessibility-law.md` (criteria owned by `better-accessibility`) |
| **Data Processing Agreement (DPA)** | B2B / whenever the site acts as a **processor** for another business, or engages its own processors | Schneier identifies; signed with each processor | `docs/03-content/legal.md` (reference) + signed copies off-repo | `privacy-eu.md` (Art 28); `privacy-us.md` (service-provider terms) |
| **Subprocessor list** | Alongside a DPA, or whenever processors handle personal data (hosting, analytics, email, payments, CRM) | Schneier maintains; derived from the data inventory below | `docs/03-content/legal.md` → published or on request | `privacy-eu.md` (Art 28 subprocessors) |

Record the list in the threat model (§4) as `[required | conditional | n/a]` per row, so phase 3
knows exactly which pages to write and phase 6 knows exactly which to check.

### Subprocessor list · template

One row per third party that processes personal data on the project's behalf. Fill from the data
inventory's "Provider" column.

| Subprocessor | Service | Data categories | Location / transfer | DPA on file | SCCs needed |
|--------------|---------|-----------------|---------------------|-------------|-------------|
| e.g. Vercel | Hosting | all request data | US | [ ] | [ ] |
| e.g. Plausible | Analytics | aggregate, cookieless | EU | [ ] | [ ] |
| e.g. Stripe | Payments | name, card token, email | US | [ ] | [ ] |

## 2 · Data inventory and legal basis

The bridge between **what the site collects**, **what Ellis measures**, **the cookie banner** and
**the legal basis**. Filled in phase 1 from the briefs, wireframes and the architecture decision;
updated whenever a form, event or third party is added. One row per piece of personal data, keyed
to the form, feature or **event** that collects it.

| Data collected | Source (form / feature / event) | Purpose | Stored where | Provider / processor | Legal basis | Retention | Transfer out → SCCs? |
|----------------|--------------------------------|---------|--------------|----------------------|-------------|-----------|---------------------|
| e.g. email | Newsletter form | send the newsletter | Postgres | Vercel (host), ESP | consent | until unsubscribe | US → yes |
| e.g. name, message | Contact form | answer the enquiry | Postgres | Vercel | legitimate interest | 12 months | US → yes |
| e.g. `signup_completed` + props | Analytics event | measure activation | PostHog | PostHog EU | consent (or cookieless hash) | per tool config | — |
| e.g. card token | Checkout | take payment | — (tokenized) | Stripe | contract | per Stripe | US → yes |

One datum used for two purposes gets one row per purpose, each with its own basis — the lawful
basis is per purpose, and a ROPA (`privacy-eu.md`, Art 30) lists the purpose of processing.

**Legal basis** is one of GDPR Art 6's six — consent, contract, legal obligation, vital interests,
public task, legitimate interests — chosen and recorded **before** collecting, never "consent for
everything" (`privacy-eu.md`, "Lawful basis (Art. 6)"). Sensitive/special-category data needs an
Art 9 condition on top; minors' data follows `privacy-minors.md`. **Transfer**: data leaving the
EU needs a mechanism — Standard Contractual Clauses or adequacy (`privacy-eu.md`, Arts 44–49).

**The two bridges Schneier must close:**

- **Analytics / tracking rows ↔ Ellis's measurement plan.** Every event row here must match an
  event in `docs/03-content/measurement-plan.md` (`skills/growth`, "The measurement-plan method").
  Each tracked event that sets non-essential storage or identifies a visitor has a legal basis of
  **consent** here and loads only behind the banner; an event captured cookielessly (no cookie, no
  identifier — e.g. Plausible or PostHog `cookieless_mode: 'always'`) is marked as such, and
  whether its storage use needs consent in a jurisdiction is Schneier's call, not the vendor's.
- **Cookie rows ↔ the Klaro banner and GPC.** Every non-essential cookie row maps to a Klaro
  service that does not load before consent (`skills/build/references/headers.md`), and a visitor
  with Global Privacy Control on is treated as having rejected it, with no re-prompt (`privacy-us.md`,
  "Do Not Sell or Share and Global Privacy Control"). A site with **no** non-essential cookie rows
  needs no banner and no cookie policy.

This inventory feeds the subprocessor list (§1), the privacy-notice "who it is shared with" and
retention fields, and the GDPR records of processing (ROPA) when one is required (`privacy-eu.md`,
"Accountability obligations").

## 3 · Minors (COPPA / GDPR child consent / LFPDPPP)

Detection in phase 1: does the site **target children under 13**, or does it **knowingly collect
their personal data**? If yes, this raises the ASVS level and adds obligations that differ from the
adult regimes — verifiable parental consent, data minimization, no behavioral advertising to
children. The detail, the current COPPA basics (including the 2025 amended Rule), GDPR's
child-consent age and LFPDPPP's treatment of minors as sensitive data live in **`privacy-minors.md`**.
Wired to the discovery interview's "minors" question (`skills/discovery/references/interview.md`)
and recorded in the threat model's sector line
(`skills/discovery/references/threat-model.md`, §4).
