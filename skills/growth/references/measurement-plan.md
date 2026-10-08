# Measurement plan · [project]

Date: [yyyy-mm-dd] · Author: Ellis · Reviewed by: Schneier (privacy) · Implemented by: Osmani ·
Status: draft | approved

The single place that says what this site measures and why. Drafted in phases 1-2 from
`brief.md`'s business goals and `spec.md`'s stories, **before** build, so Osmani instruments it in
phase 5 and Beizer checks it in phase 6. Every row traces to a question the business asked; an
event that answers no question is not here. Reply/write in the project's language; event names in
English (`object_action`, `snake_case`, past tense).

## 1. Questions the site must answer

The three-to-five questions, straight from the business goals. Everything below works backward
from these.

1. [e.g. How many visitors start signup and how many finish?]
2. [e.g. Which acquisition source converts best? — the source dimension is Sullivan's SEO/acquisition angle; the conversion is yours]
3. [ ]

## 2. North-star metric

| Field | Value |
|-------|-------|
| North-star | [one metric = value delivered to the user] |
| Why it is not gameable | [it cannot rise without the business actually improving] |
| Inputs the team can move | [2-4 sub-metrics] |
| Guardrails | [metrics that must not degrade: retention, page weight, refund rate…] |
| Revisit when | [the product changes materially] |

## 3. Conversion funnel

Ordered steps from landing to the north-star action. One canonical event = value received.

| # | Step | Event that marks it | Expected drop | Notes |
|---|------|---------------------|---------------|-------|
| 1 | [landing] | `page_viewed` | — | entry |
| 2 | [intent] | `[object_action]` | | |
| 3 | [action] | `[object_action]` | | |
| 4 | [value received] | `[object_action]` | | north-star action |

Retention cohort (only if the product has return visits): [define the returning-value event and
the cohort window].

## 4. Events

One row per event. The naming convention is fixed once: `object_action`, `snake_case`, past-tense
action; properties `snake_case`; booleans `is_*`/`has_*`. One name means one thing everywhere.

| Event | When it fires | Properties | Funnel step | Question (§1) | Tool | Client/Server |
|-------|---------------|------------|-------------|---------------|------|---------------|
| `page_viewed` | on each page load | `path`, `referrer_source` | 1 | 1,2 | [tool] | client |
| `[form_submitted]` | on successful submit | `form_id`, `is_valid` | 3 | 1 | [tool] | [server if it carries outcome] |
| `[signup_completed]` | server confirms account | `plan`, `source` | 4 | 1,2 | [tool] | server |

Each event carries a one-line **description of correct behaviour** so QA has an agreed standard:

- `page_viewed`: [fires once per navigation, not per render].
- `[form_submitted]`: [fires once, only on server-confirmed success, never on validation error].

## 5. Identity and consent

| Rule | Decision |
|------|----------|
| Default identity | anonymous (no profile) |
| When identified | [only on account creation, with consent] |
| Tool & mode | [Plausible cookieless / PostHog `cookieless_mode: 'always'` / PostHog consent-aware behind Klaro] |
| Needs a banner? | [no — cookieless exception / yes — behind Klaro, non-essential loads only on Accept] |
| GPC | honoured before any banner, no re-prompt (`build` headers.md) |
| Replay (if any) | consent-gated, form inputs masked; Schneier reviews |
| Legal basis / notice | [Schneier — LFPDPPP / GDPR / US privacy per `security`] |

## 6. Dashboards and ownership

| Dashboard | Shows | Owner | Reviewed |
|-----------|-------|-------|----------|
| North-star + funnel | §2, §3 | [name] | monthly (30/60/90, then quarterly) |
