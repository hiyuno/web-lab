# Architecture decision · [project name]

Date: [yyyy-mm-dd] · Author: Cooper · Reviewed by: Schneier · Status: proposal | approved

## Decision

[Content site with Astro | Application with Next.js | Hybrid: which part on each]

## Why

| Criterion | What the user said | Where it points |
|-----------|--------------------|-----------------|
| Pages are the same for every visitor | | |
| There are signed-in users who see different things | | |
| Data that changes in real time | | |
| Payments, subscriptions, roles | | |
| Visitor-generated content | | |
| Who edits the content and how often | | |

## Components

- Framework: [Astro x | Next.js x]
- Styling: Tailwind v4 with Frost's tokens
- CMS: [none | which and why]
- Database: [none | Postgres on ...]
- Identity: [none | Clerk | Auth.js | Supabase Auth]
- Payments: [none | Stripe | Mercado Pago]
- Hosting: [Vercel | another the user already has]
- Analytics: [cookieless: Plausible, Fathom, Vercel Analytics | with consent]
- Transactional email: [none | Resend | other]

## External integrations

| Service | For what | Data that crosses | Account owner |
|---------|----------|-------------------|---------------|
| | | | |

## Alternatives discarded

- [Alternative]: [why not]

## Consequences

- [What becomes easy, what becomes hard, what to watch]
