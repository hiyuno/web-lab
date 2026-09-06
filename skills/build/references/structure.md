# Repository structure

Standard `package.json` scripts so CI and the roles do not guess: `dev`, `build`, `preview`,
`lint`, `typecheck`, `test`, `test:e2e`, `format`.

## Astro 5 · content site

```
.
├── astro.config.mjs
├── src/
│   ├── assets/            # images and fonts Astro processes (from Bellard)
│   ├── components/        # one file per Frost component; subfolders per family
│   │   ├── ui/            # Button, Input, Link, Card...
│   │   └── blocks/        # Hero, Testimonials, Pricing... (wireframe blocks)
│   ├── content/           # collections: pages, posts, faqs... (copy from the briefs)
│   ├── content.config.ts  # Zod schemas of the collections
│   ├── layouts/           # one per sitemap template: Base, Home, Interior, Listing, Detail, Form, Legal
│   ├── pages/             # routes = sitemap.md; [slug].astro reads from collections
│   ├── styles/tokens.css  # exact copy of docs/04-design/tokens.css
│   └── lib/               # seo.ts (metadata and JSON-LD from seo.md), utils
├── public/                # favicon, robots.txt, default og
├── tests/                 # vitest (unit) + playwright (e2e)
├── vercel.json            # headers.md + redirects.md
├── lighthouserc.json
└── .github/workflows/ci.yml
```

Rules: `client:*` only on interactive `components/ui` and with a reason in the PR; images with
`<Image>`; local fonts in `src/assets/fonts` subsetted; JSON-LD in the layout from `lib/seo.ts`.

## Next.js 16 · application

```
.
├── next.config.ts         # headers, images, experimental.taint
├── proxy.ts               # CSP with nonce, redirects; NO auth
├── src/
│   ├── app/
│   │   ├── (marketing)/   # light layout, public pages, can be static or a separate Astro
│   │   ├── (app)/         # authenticated layout: dashboard, account...
│   │   │   ├── layout.tsx
│   │   │   ├── loading.tsx
│   │   │   ├── error.tsx
│   │   │   └── <route>/page.tsx
│   │   ├── (auth)/        # login, recover (their own pages, never a modal)
│   │   ├── api/           # route handlers only for webhooks and external APIs
│   │   ├── layout.tsx     # tokens.css, fonts with next/font, nonce to <Script>
│   │   ├── robots.ts · sitemap.ts · opengraph-image.tsx
│   │   └── not-found.tsx
│   ├── actions/           # "use server": thin; validate with Zod and call data/
│   ├── data/              # data access layer: import 'server-only'; the only one touching db and process.env
│   │   ├── auth.ts        # getViewer() with cache()
│   │   ├── db.ts          # Drizzle client (Neon)
│   │   └── <entity>.ts    # get<X>DTO, create<X>, ... with authorization inside
│   ├── db/schema.ts       # Drizzle schema
│   ├── components/ui/     # shadcn/ui adjusted to tokens; blocks/ for blocks
│   ├── lib/               # validators (Zod), seo, utils; no secrets
│   └── styles/tokens.css
├── drizzle/               # versioned migrations
├── drizzle.config.ts
├── tests/                 # vitest + playwright; per action: happy, invalid, forbidden
├── .env.example
├── lighthouserc.json
└── .github/workflows/ci.yml
```

Rules: `process.env` and `db` only in `src/data/`; `"use client"` only on leaves; every
`actions/*` re-verifies the session and delegates; `[param]` validated with Zod; `route.ts` only
for webhooks with a verified signature.

## Shared

- The project's `CLAUDE.md` with stack, commands, doc paths and this skill's rules.
- `docs/` with phases 1 to 5 versioned next to the code.
- `.gitignore`: `.env*` (except `.env.example`), `node_modules`, `.vercel`, `dist`/`.next`, `playwright-report`.
