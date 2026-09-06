# Pull request · [S-xx.Tn] · [title]

## What changes

[Two sentences. Which story it covers and what can be tried on the preview.]

Preview: [URL] · Screenshot: [ ]

## How to test it

1. [ ]
2. [ ]

## Author checklist

- [ ] Test red before, green now; files: [ ]
- [ ] Verified 375 and 1280
- [ ] Tokens only; full states
- [ ] No secrets or private data to the client
- [ ] Lint, types, tests green
- [ ] `better-interface` run over what changed; verdict attached

## Reviewer checklist

Correctness
- [ ] Does what the acceptance criterion says and nothing more
- [ ] Edge cases: empty, very long, odd characters, double click, expired session
- [ ] Error handling: generic to the user, detail to the log

Security (read closely if it touches auth, data, payments, deletion, uploads, `route.ts`, `proxy.ts`)
- [ ] Input validated with a schema at the boundary
- [ ] Per-resource authorization inside the action or the data layer, not only in the page
- [ ] Return filtered to what the UI needs
- [ ] No `process.env` or DB client outside `src/data/`
- [ ] No `dangerouslySetInnerHTML` / `set:html` with uncontrolled content
- [ ] New dependencies justified and in the lockfile

Performance
- [ ] `"use client"` / `client:*` only where needed
- [ ] Images with dimensions, `sizes`, priority; fonts non-blocking
- [ ] Lighthouse CI within budget

Accessibility
- [ ] Native elements, `label`, visible focus, accessible name, keyboard

Quality
- [ ] Clear names, no duplicated utilities, no dead code
- [ ] Small, explainable commits
- [ ] What I do not understand, I ask; nothing nobody can explain gets merged

Result: [ ] approve · [ ] changes requested: [ ]
