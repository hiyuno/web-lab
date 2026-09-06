# Test plan · [project]

Date: [yyyy-mm-dd] · Author: Beizer · Staging: [URL] · Commit: [sha] · Status: proposal | approved

## Scope

- Must and should stories in the spec: [S-01, S-02, ...]
- Flows from `docs/02-structure/flows.md`: [T1, T2, ...]
- Templates: [home, interior, listing, detail, form, legal, account]
- Out of scope this round: [ ] (and why)

## Severities and exit criteria

Set here, before anything is found. See `exit.md`. Blocker and critical block the launch; major is
fixed or accepted by the user in writing; minor and trivial go to the backlog.

## Browser and device matrix

| Environment | Version | Who | How |
|-------------|---------|-----|-----|
| Desktop Chromium, Firefox, WebKit | latest | Playwright | CI |
| Chromium 375 × 812 | latest | Playwright | CI |
| iPhone [model] · iOS Safari | | [user] | manual, script |
| Android [model] · Chrome | | [user] | manual, script |
| Safari Mac, Edge | latest | Beizer | manual |
| Screen reader | VoiceOver Mac / iPhone | [who] | script in accessibility.md |

## Areas and owners

| Area | What | Tool | Who | Output |
|------|------|------|-----|--------|
| Crawl | links, codes, 404, redirects, metadata, headers, sensitive paths | crawl_check.py | Beizer | crawl.md |
| Functional | acceptance criteria, edge cases, forms, analytics | Playwright + manual | Beizer | tests/e2e, report |
| Accessibility | axe per template and state; manual keyboard and reader | axe.fixture.ts + script | Beizer + [who] | accessibility.md |
| Performance | mobile Lighthouse ×3 vs budget; field if any | Lighthouse, CrUX | Beizer | report |
| Security | audit, gitleaks, ZAP baseline, IDOR, rate limit, forms | security.md script | Beizer → Schneier | security.md |
| Visual and devices | baseline screenshots 375/768/1280; walkthrough on real phones | Playwright, manual | Beizer + [user] | tests/visual |

## Test data

- Test users (two, for IDOR): [ ] · never real accounts
- Test email for forms: [ ]
- Payment provider test cards: [ ]

## Calendar

| Day | What |
|-----|------|
| 1 | crawl, axe, Lighthouse, scans |
| 2-3 | functional and Playwright |
| 3 | manual: screen reader and phones |
| 4 | report, triage, retest |
| 5 | exit and Schneier's gate |
