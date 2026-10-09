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
- CMS: [none | Keystatic | Sanity | Payload]
  - When: only if someone who does not code will edit content often; otherwise **none** (content
    lives in the repo).
  - Default by site type: content site (Astro) → Keystatic (git-based); web app (Next.js) →
    Payload (in our Postgres via Drizzle). Sanity (hosted) only when editors need a studio and no
    repo. The team picks per project and justifies the choice here.
  - Why this one: [justification, incl. where content lives and who edits]
  - Detail and the security/sanitization + performance notes:
    `skills/build/references/cms.md`. Osmani integrates it; Rosenfeld's content model
    (`skills/content`) drives the schema. A hosted CMS (Sanity) means data leaves our infra —
    record it in the external-integrations table below.
- Database: [none | Postgres on ...]
- Identity: [none | Better Auth: sign-in methods, plugins]
- Payments: [none | Stripe | Mercado Pago]
- Hosting: Vercel
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
