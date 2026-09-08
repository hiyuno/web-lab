---
name: build
description: Osmani and Hopper, engineering. Phase 5 of the web-lab process. With the approved design, builds the site or app in Astro 5 or Next.js 16 following the spec: repo foundation with TypeScript, Tailwind v4 with Frost's tokens, CI with tests, audit and Lighthouse CI with a performance budget, tasks derived from the stories, a per-task cycle with tests first and pull requests with preview, a frontend track (components, SEO, headers and CSP, Core Web Vitals) and a backend track for apps only (server-only data access layer, Drizzle and Postgres, Zod, auth with a provider, per-resource authorization, rate limiting, webhooks). Use this skill when the user asks to build, implement, code, lay out, "turn the design into code", set up the repo, configure CI, Next.js, Astro, database, login, API, server actions, or when a project has an approved docs/04-design and no code yet. Works in tasks with user checkpoints.
---

# /build · Osmani and Hopper

This skill runs phase 5: from the approved design to a staging with real content that Beizer can
test. Two roles load it: **Osmani** (frontend and performance, `agents/osmani.md`) and **Hopper**
(backend, data and auth, `agents/hopper.md`). Steps 5.0 to 5.3 and 5.6 to 5.9 are shared; 5.4
is Osmani's track and 5.5 is Hopper's, which only activates if `architecture-decision.md` says
application.

The result is the project repository on staging plus `docs/05-development/` with `tasks.md`,
`frontend.md` and, if applicable, `backend.md`.

## Golden rule: spec → task → test → code → verify → commit

Nothing is built without a task that comes from a spec story. No task is implemented without its
test in red first. No commit without checking in the browser and without being able to explain
it. Never disable a lint, a test or a warning to make the build pass. Reply in the user's
language; code, names and commits in English.

You work as orchestrator: you delegate tasks to the `osmani` or `hopper` subagent by track, one
or a few at a time, with the full issue in the prompt, and you review every pull request before
merging. Scope changes go back to the spec first.

## Calibration and hand-off

Exact: the budget in `lighthouserc.json`, the headers in `headers.md`, the nine states of every
component and the three test cases per action. A disabled lint, a skipped test or an `any` to
make it compile are findings, not shortcuts. Before opening a pull request, the subagent runs
`better-interface` over what it touched and attaches its verdict; accessibility, layout,
typography, color, surface and writing rules belong to the `better-*` skills, and here they are
only required to be met. What was not tested in the browser is reported as **Not verified**.

## Step 5.0 · Entry

0. Read this project's own `docs/learnings.md` (osmani's and hopper's sections, if they have
   entries) and `<web-lab>/docs/PREFERENCES.md`.
1. Read `docs/01-discovery/spec.md`, `architecture-decision.md` and `threat-model.md`;
   `docs/03-content/seo.md`, `assets.md`, `legal.md` and the briefs; `docs/04-design/tokens.css`,
   `components/`, `templates/`, `accessibility.md`, `motion.md` and the prototype. If the design
   is not approved, stop and propose `/design-system`.
2. Confirm with the user: framework per the decision, package manager (pnpm by default),
   hosting (Vercel by default), remote repository and who reviews pull requests. Do not create the
   remote repo or deploy without being asked.

## Step 5.1 · Repository foundation

One day that saves weeks. With `references/structure.md` for each framework's folders:

1. Scaffold: `pnpm create astro@latest` or `pnpm create next-app@latest` with strict TypeScript.
   Tailwind v4 and `docs/04-design/tokens.css` as the main stylesheet.
2. `.gitignore` with `.env*` (except `.env.example`) from the first commit. `.env.example` with
   names and descriptions, never values.
3. Lint and format (ESLint, Prettier). Pre-commit hooks with lint-staged: lint, types and
   `gitleaks protect --staged`.
4. CI with `references/ci.yml`: types, lint, tests, build, `pnpm audit --audit-level=high` and
   Lighthouse CI with `references/lighthouserc.json` as a threshold that fails the build.
5. Vercel linked to the repo: preview per branch, production only from `main`. The `main`
   preview is staging. `deploy-to-vercel` or `vercel:deploy` skills if needed.
6. `main` branch protection: green CI and one review before merging.
7. Dependabot or Renovate with weekly grouping and immediate security patches.
8. The project's `CLAUDE.md`: stack, commands, where the docs are, this skill's rules. Start from
   web-lab's.
9. First commit: "chore: scaffold" with all of the above. Verify the preview comes up.

## Step 5.2 · Task plan

```bash
python3 <skill>/scripts/tasks_from_spec.py docs/01-discovery/spec.md > docs/05-development/tasks.md
```

Generates one section per story with its acceptance criteria turned into test cases and an
empty task table. Complete each task with `references/task.md`: context, goal, criteria,
constraints, track (frontend or backend), dependencies and test command. Tasks the size of a
reviewable pull request: one component, one template, one action, one integration. Order by
dependencies; foundation first, then base components (button, field, link), then templates, then
flows.

**Checkpoint A**: the user approves the task plan and order. Here you see whether something in
the spec does not fit the deadline; it is decided before writing code.

## Step 5.3 · Per-task cycle

The same for both tracks. Delegate to the subagent with the full issue and these rules:

1. Branch `feat/<id>-<slug>` from an up-to-date `main`.
2. Test first, in red: unit for logic and components, Playwright for flows. Run it and watch it
   fail before implementing.
3. Implement only what the test asks for. Frost's components with their nine states; values only
   from tokens.
4. Verify in the built-in browser at 375 and 1280, light and dark mode if it exists.
5. `pnpm lint && pnpm typecheck && pnpm test` green. If something fails, it is fixed or reported;
   never silenced.
6. Small conventional commit: `feat(scope): ...`, `fix:`, `chore:`, `test:`. A commit that
   cannot be explained in one sentence is split.
7. Pull request with the `references/pr-review.md` template filled in, Vercel preview and
   screenshot. You review with the checklist; only then is it merged.

## Step 5.4 · Frontend track · Osmani

You delegate to `osmani`. Beyond the cycle:

- **Astro**: typed content collections for all the briefs' content; one layout per Frost
  template; islands only where there is real interaction, with `client:visible` or
  `client:idle`, never `client:load` without reason; Astro's `<Image>` and `<Picture>` with
  Bellard's assets; local subset fonts with `font-display: swap` and preload of the main one;
  View Transitions if the design asks for them.
- **Next.js**: App Router; Server Components by default and `"use client"` only on interactive
  leaves; `(marketing)` and `(app)` route groups; Cache Components with explicit `"use cache"`
  and `cacheLife` on what is cacheable, Suspense on what is dynamic; `loading.tsx` and
  `error.tsx` per segment; `next/image` and `next/font`. Skills `vercel:nextjs`,
  `react-best-practices`, `composition-patterns`, `vercel:next-cache-components`.
- **Shared**: semantic HTML with landmarks, visible focus, `label` on every field; the `seo.md`
  table implemented with metadata, JSON-LD, `sitemap.xml`, `robots.txt`, OG per page, canonical
  and `hreflang`; headers and CSP with `references/headers.md` (nonce on Next.js, static on
  Astro); redirects from `docs/02-structure/redirects.md` in `vercel.json` or `astro.config`;
  external links with `rel="noopener noreferrer"`; no unsanitized HTML; no secret in the client.
- **Budget** that CI enforces with `lighthouserc.json`: HTML 50 KB, CSS 60 KB, initial JS
  150 KB compressed, fonts 80 KB, above-the-fold images 200 KB; LCP 2.5 s, INP 200 ms, CLS 0.1
  on simulated mobile. If a pull request breaks it, it is not merged.
- Images and video: ask `bellard` for the variants with `/optimize-assets` over `assets.md`; you
  place them with correct `width`, `height`, `sizes`, `loading` and `fetchpriority`.

## Step 5.5 · Backend track · Hopper (applications only)

You delegate to `hopper`. With `references/dal.md` as the pattern. For `app-web` projects, `references/forum.md` has the feature-request forum's schema, DAL functions and rate limiting.

- **Data access layer** in `src/data/` marked `import 'server-only'`: the only one that reads
  `process.env` and touches the database. Every function authenticates, authorizes per resource
  (ownership or organization in the query, never just the id) and returns a minimal DTO.
- **Database**: Postgres on Neon (or the hosting's) with Drizzle and versioned migrations in
  `drizzle/`. Schema with an owner per table and explicit `on delete`. Never manual changes in
  production.
- **Validation**: Zod at every boundary: `FormData`, `params`, `searchParams`, headers, webhook
  bodies. Types are erased at runtime; the schema is not.
- **Auth** with a provider: Clerk, Better Auth or Auth.js per `architecture-decision.md`. Skill
  `vercel:auth`. Cookies `HttpOnly`, `Secure`, `SameSite=Lax`. Middleware or `proxy.ts` only
  redirects; it is never the barrier. Every server action and route handler re-verifies.
- **Thin server actions** in `src/actions/`: validate with Zod, call the data layer, return only
  what the UI needs, `revalidatePath` or `updateTag`. Generic errors to the client; detail to the
  log.
- **Rate limiting** with `@upstash/ratelimit` or the hosting's on login, signup, recovery, public
  forms and expensive operations.
- **Payments** with Stripe or Mercado Pago via Checkout; webhooks verified by signature before
  reading the body; idempotency by event id.
- **Uploads** to Vercel Blob or S3: real type, max size, renamed, served from another origin.
- **Logs** without personal data. **Backups** automatic, enabled at the provider.
- **Tests** per action: happy path, invalid input, user without permission (IDOR).

## Step 5.6 · Staging integration

Real content from the briefs loaded into collections or CMS; Bellard's assets in place;
redirects responding 301; forms reaching their destination; analytics and consent banner
working; legal pages published at their URLs; custom 404. The `main` preview is what Beizer
tests. Open it and walk the main flows in `flows.md`.

## Step 5.7 · Definition of done

With `references/definition-of-done.md`. Per task: green test, verified in the browser, clean
lint and types, no secrets, explainable commit, reviewed and merged. Per phase: every must-have
story implemented, budget met in CI, headers verified with `curl -sI`, `pnpm audit` without
highs, `gitleaks detect` clean, `docs/05-development/frontend.md` and `backend.md` written with
`references/frontend.md` and `references/backend.md`.

## Step 5.8 · Security gate

Launch `schneier` with repo access and phase 5 of `docs/SECURITY.md` plus the Next.js audit
points: database and `process.env` only in the data layer; client component props without
private data; every `"use server"` validates, authorizes, checks ownership and filters its
return; route params validated; `proxy.ts` and `route.ts` reviewed closely. A critical finding
is fixed before the checkpoint.

## Step 5.9 · Checkpoint and retro

1. **Checkpoint B**: present the staging URL, the CI status, the mobile Lighthouse report, how
   many must and should stories are done, Schneier's verdict and what was left out. Ask for
   explicit approval.
2. Retro into this project's own `docs/learnings.md` (create it from
   `<web-lab>/docs/learnings-template.md` if it does not exist yet), under the osmani and hopper
   sections. Bring the file to a web-lab session at project close so it merges into the
   persistent learnings there. Confirmed stack or tool preferences to `docs/PREFERENCES.md`.
3. With approval, say what comes next: phase 6 with Beizer on staging.

## Before you finish

| Symptom | Fix |
|---------|-----|
| A literal color, spacing or radius in a component | token from `tokens.css`; Frost has it or it is added |
| `"use client"` or `client:load` on a file with no event or state | remove it; Server Component or HTML |
| `auth()` only in `page.tsx` and not in the action or in `src/data` | re-verify inside; middleware is not a barrier |
| `process.env` or the DB client outside `src/data/` | move it; the three greps in `dal.md` |
| An action that returns the full record | DTO with what the UI needs |
| `NEXT_PUBLIC_` with "secret", "key" or "token" in the name | it is private; drop the prefix and move it to the server |
| New `eslint-disable`, `@ts-ignore`, `test.skip` or `any` in the diff | fix the cause or justify in the PR with an issue |
| A PR with more than 400 changed lines | split it by task |
| The test commit is later than the implementation commit | test first; if not, say so in the PR |
| Lighthouse CI yellow "for now" | not merged; the budget is the threshold |
| Lorem ipsum or an image over 300 KB on staging | briefs and Bellard before the checkpoint |
