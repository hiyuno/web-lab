# Maintenance plan · [project]

Date: [yyyy-mm-dd] · Author: Allspaw · Plan owner: Allspaw · Alerts a decision to: Yuno ·
Plan review: every 6 months

## How it fires: owner, trigger, routing

Without this section the calendar below is a wish list nobody runs. Two things make it real:

- **Owner and routing.** **Allspaw owns this schedule and is the point of contact.** He runs and
  triages every scheduled task, handles what is routine himself, and **alerts Yuno on anything
  that needs a decision** (a major version to plan, a secret or access to revoke, a cost or expiry
  to approve). The per-task **Owner** column names who does that task when it is not Allspaw; the
  routing to Yuno for decisions is the same for all of them.
- **Trigger: a dated checklist, committed in git (default).** The task fires because a date came
  due, not because someone remembered. The **Last** and **Next** columns below are that mechanism:
  fill **Next** for every row at project close (step 8.1), commit this file to
  `docs/08-maintenance/plan.md`, and Allspaw works from the rows whose **Next** has arrived,
  stamping **Last** and setting the following **Next** each time. This needs no infrastructure,
  lives in git, and survives any handoff — the next owner inherits the dates. *Optional upgrade:*
  a cron job or a calendar reminder that pushes the due rows to Allspaw's channel, for teams that
  want a notification instead of reading the file. The checklist stays the source of truth; the
  reminder only points at it.

**This is not monitoring.** `monitoring.md` is the **real-time machine** channel: uptime, error
and Core Web Vitals alerts fire automatically the moment the user's experience breaks, to a named
person, day or night. This file is the **scheduled periodic human** channel: tasks that come due
on a date and need a person to run and judge them. The two never overlap — an outage is
`monitoring.md`; a quarterly access review is here.

## Calendar

| Frequency | Task | How | Owner | Last | Next |
|-----------|------|-----|-------|------|------|
| Continuous | Dependencies | Dependabot (Renovate if monorepo): weekly group, same-day security patches; CI decides | | | |
| Continuous | Alerts | respond per incidents.md | | | |
| Monthly | Site health | `domain_check.py` + `launch_check.py` against production | | | |
| Monthly | Field Core Web Vitals | Speed Insights / CrUX vs budget | | | |
| Monthly | Indexing + SEO cycle | Search Console coverage/404/positions, AI citations, decaying content — per Sullivan's post-launch SEO cycle (`skills/seo`) | | | |
| Monthly→quarterly | Metrics + CRO review | North-star and funnel vs the spec's goals, CRO evidence, experiments — per Ellis's 30/60/90 review (`skills/growth`); monthly for the first 90 days, then quarterly | | | |
| Monthly | Forms and email | test submission; arrives and not in spam | | | |
| Monthly | Backups | verify they run; test restore every 6 months | | | |
| Monthly | Expiries | domain > 60 days, certificate > 14 days | | | |
| Quarterly | Secret rotation | the rotatable ones (API keys, tokens, `BETTER_AUTH_SECRET` per "Better Auth configuration", item 8: rotating it signs everyone out); with Schneier | | | |
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
- What is learned and applies to other projects goes to the project's `docs/learnings.md`, under
  the allspaw section; the Web Master harvests it (see `<web-lab>/docs/LADDER.md`).

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
