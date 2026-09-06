# Maintenance plan · [project]

Date: [yyyy-mm-dd] · Author: Allspaw · Plan owner: [name] · Plan review: every 6 months

## Calendar

| Frequency | Task | How | Owner | Last | Next |
|-----------|------|-----|-------|------|------|
| Continuous | Dependencies | Dependabot (Renovate if monorepo): weekly group, same-day security patches; CI decides | | | |
| Continuous | Alerts | respond per incidents.md | | | |
| Monthly | Site health | `domain_check.py` + `launch_check.py` against production | | | |
| Monthly | Field Core Web Vitals | Speed Insights / CrUX vs budget | | | |
| Monthly | Indexing | Search Console: coverage, 404, enhancements | | | |
| Monthly | Forms and email | test submission; arrives and not in spam | | | |
| Monthly | Backups | verify they run; test restore every 6 months | | | |
| Monthly | Expiries | domain > 60 days, certificate > 14 days | | | |
| Quarterly | Secret rotation | the rotatable ones (API keys, tokens); with Schneier | | | |
| Quarterly | Access review | registrar, DNS, hosting, repo, analytics, payments; remove what is not needed | | | |
| Quarterly | Content | legal pages current, prices, testimonials, dates | | | |
| Semiannual | Incident runbook | reread; rehearse one scenario | | | |
| Yearly | Threat model | against what the site is today; with Schneier | | | |
| Yearly | Full SECURITY.md | | | | |
| Yearly | Next cycle | postponed stories → `/discovery` | | | |

## Rules

- A major framework version is a planned task with branch, tests and preview; never automerge.
- Departures: access revoked the same day.
- An incident always ends in a post-mortem (≤ 72 h) and a change to the runbook.
- What is learned and applies to other projects goes to `<web-lab>/learnings/allspaw.md`.

## Recurring costs

| Service | Cost | Renewal | Card expires | Account in the name of |
|---------|------|---------|--------------|------------------------|
| Domain | | | | |
| Hosting | | | | |
| Database | | | | |
| Email | | | | |
| Monitoring | | | | |

## History

| Date | What was done | Who |
|------|---------------|-----|
| | | |
