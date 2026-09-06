# User flows · [project]

Date: [yyyy-mm-dd] · Author: Rosenfeld · Source: stories in `docs/01-discovery/spec.md`

One section per main task. Mark with 🔒 the steps where the person hands over data or signs in:
those are the surfaces Schneier reviews.

## Main tasks

| # | Audience | Task | Stories | Typical entry | Success |
|---|----------|------|---------|---------------|---------|
| T1 | | | S-01, S-03 | search, social, direct link, email | |

## T1 · [task name]

```mermaid
flowchart LR
  E[Entry: search] --> P1[/landing-page]
  P1 --> D{Decision?}
  D -->|yes| P2[/next]
  D -->|no| P3[/alternative]
  P2 --> F[🔒 /form: name, email]
  F --> OK[Success: confirmation]
```

Pages it touches: [ ]. Data handed over: [ ]. What happens if they abandon at step X: [ ].

## Pages that come out of the flows

Consolidated list of every page that appears in the flows. It is the input for the sitemap.

- [ ]
