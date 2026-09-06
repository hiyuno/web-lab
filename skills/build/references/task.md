# Task · [S-xx.Tn] · [one-sentence title]

Track: fe | be | infra | media · Role: Osmani | Hopper | Bellard · Branch: `feat/s-xx-tn-slug` · Status: pending

## Context

- Story: [S-xx · title] in `docs/01-discovery/spec.md`
- Design: `docs/04-design/components/<x>.md`, `templates/<y>.md`
- Content: `docs/03-content/briefs/<slug>.md`
- Depends on: [T-000, S-xx.T1]

## Goal

[What exists when the task is done, in one observable sentence.]

## Acceptance criteria (from the spec)

- Given [context], when [action], then [result].
- Given [invalid context], when [action], then [message or behavior].

## Constraints

- Tokens from `tokens.css` only; Frost's components with their states.
- [Astro: no `client:*` except ...] · [Next.js: Server Component except ...]
- Budget: does not raise initial JS by more than [n] KB.
- Security: [validate with Zod ...; authorize by ownership ...; no private data to the client].
- Accessibility: [keyboard, focus, accessible name, contrast].

## Tests (write first, see red)

| Case | Type | File | Command |
|------|------|------|---------|
| S-xx.C1 | unit / e2e | `tests/...` | `pnpm test -- <file>` |

## Manual verification

- [ ] 375 and 1280, light and dark
- [ ] Keyboard: Tab, Enter, Escape
- [ ] States: empty, loading, error, success

## Definition of done

See `definition-of-done.md`. PR with template, preview, screenshot, reviewed.
