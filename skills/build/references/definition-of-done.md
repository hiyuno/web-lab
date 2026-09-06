# Definition of done

## Per task

- [ ] Comes from a spec story and is in `tasks.md`
- [ ] Test written first, seen red, now green
- [ ] Verified in the browser at 375 and 1280 (and dark mode if it exists)
- [ ] `pnpm lint`, `pnpm typecheck`, `pnpm test` green with no new exceptions
- [ ] Tokens only; Frost's components with all their states
- [ ] No secrets, no `console.log` of data, no `TODO` without an issue
- [ ] Conventional commits that are explained in one sentence
- [ ] PR with template, Vercel preview, screenshot; reviewed and merged
- [ ] Lighthouse CI within budget on the preview

## Per phase

- [ ] Every `must` story done; `should` done or postponed with a written reason
- [ ] Staging with real content, optimized assets, redirects, forms, analytics, legal pages, 404
- [ ] Performance budget met in CI; LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 mobile
- [ ] Headers verified: `curl -sI <staging>` shows HSTS, CSP, nosniff, Referrer-Policy, Permissions-Policy, frame-ancestors
- [ ] `pnpm audit --audit-level=high` clean; `gitleaks detect` clean over the whole history
- [ ] `.env.example` complete; variables loaded in Vercel with least privilege
- [ ] `docs/05-development/frontend.md` (and `backend.md`) written
- [ ] Schneier's verdict without criticals
- [ ] User checkpoint approved
