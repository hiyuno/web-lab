# Frontend · [project]

Date: [yyyy-mm-dd] · Author: Osmani · Framework: Astro 5 | Next.js 16 · Hosting: Vercel

## How to run it

```bash
pnpm install
cp .env.example .env.local   # ask the project owner for the values; never paste them in the chat
pnpm dev
pnpm test && pnpm test:e2e
```

## Decisions

| What | Decision | Why | Alternative discarded |
|------|----------|-----|-----------------------|
| Framework | | architecture-decision.md | |
| Styling | Tailwind v4 + tokens.css | | |
| Base components | shadcn/ui / Astro | | |
| Fonts | local, subset, swap | | |
| Analytics | | cookieless / with consent | |

## Performance budget (mobile)

| Metric | Target | Staging | Date |
|--------|--------|---------|------|
| LCP | ≤ 2.5 s | | |
| INP | ≤ 200 ms | | |
| CLS | ≤ 0.1 | | |
| Initial JS | ≤ 150 KB gz | | |
| Lighthouse performance | ≥ 90 | | |

## Headers

Verified with `curl -sI` on [date]: [paste result].

## Component map

| Component (Frost) | File | States implemented | Tests |
|-------------------|------|--------------------|-------|
| | | 9/9 | |

## Template map

| Template | Layout / route | Pages | Status |
|----------|----------------|-------|--------|
| | | | |

## Debt and pending

| What | Why postponed | When |
|------|---------------|------|
| | | |
