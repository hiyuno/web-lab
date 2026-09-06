# Incident runbook · [project]

Date: [yyyy-mm-dd] · Author: Allspaw · Review after every incident and at least every 6 months.

A short runbook that exists beats a long one that does not. First what you see and what you do;
the explanation later. Never "who".

## Severities

| Level | What it means | Responds | Within | Tells users |
|-------|---------------|----------|--------|-------------|
| SEV1 | site down, payments broken, data breach | [name] · backup [name] | 15 min | yes, within 30 min |
| SEV2 | main function broken (login, form, checkout) | [name] | 1 h | if it lasts > 1 h |
| SEV3 | degradation with a workaround; slowness; error on a secondary page | [name] | 1 business day | no |
| SEV4 | cosmetic, copy | backlog | next cycle | no |

## First 10 minutes, always

1. Confirm: is it the site or is it me? External monitor + `curl -sI https://<domain>` + another device.
2. Declare severity and notify in [channel]: "SEV[n]: [what fails] since [time]. Investigating."
3. Look in order: Vercel status (vercel-status.com) → last deployment → Sentry → DNS (`dig`) → certificate → third parties.
4. If the last deployment matches the start: **Instant Rollback** first, investigate later.
5. Write the timeline from minute one; the post-mortem needs it.

## Scenarios

### A · Site down (SEV1)
- Vercel status → if it is the platform, communicate and wait; touch nothing.
- Last deployment → Instant Rollback. Verify. Remember to undo the rollback later.
- DNS: does `dig +short <domain>` return what is expected? If not, restore the snapshot.
- Certificate: `curl -vI https://<domain> 2>&1 | grep -i expire`. If expired, renew at the hosting.
- Communicate: banner or social: "We are having issues; working on it."

### B · Breach or suspected unauthorized access (SEV1)
- Delete nothing: preserve logs and evidence.
- Contain: rotate ALL secrets (hosting, DB, providers), close sessions, revoke tokens, change passwords of critical accounts.
- Call Schneier: scope, affected data, cause.
- Obligations: Mexico's 2025 LFPDPPP requires informing data subjects without delay when the breach significantly affects their rights; GDPR 72 h to the authority if applicable. Detail in `skills/security/references/legal-mx.md`. Draft the notice with facts, what was done and what to do.
- Mandatory post-mortem.

### C · Expired domain or certificate (SEV1)
- Registrar: renew today; it can take hours to come back. Turn on auto-renewal.
- Certificate: Vercel renews on its own; if it failed, check CAA and DNS and force renewal.
- Afterwards: expiry alerts at 60 and 14 days (monitoring.md).

### D · Third party down: payments, auth, CMS, email (SEV1 or SEV2)
- Confirm on the provider's status page.
- Degrade gracefully: clear message to the user ("payments are unavailable, try again in an hour"), no 500 errors.
- Do not try to fix the provider's problem. Communicate and wait. Note the duration for the post-mortem.

### E · Traffic spike or attack (SEV2)
- Vercel: check the Firewall and turn on Attack Challenge Mode if it is an attack (`vercel:vercel-firewall` skill).
- Rate limiting on forms and login should already exist; verify it acts.
- Costs: check plan limits.

### F · Wrong content published (SEV2 or SEV3)
- Instant Rollback if it came in the last deployment; if it is CMS, revert the entry.
- Check cache: purge if applicable.

## Communication

| Moment | Where | What |
|--------|-------|------|
| On declaring | [internal channel] | SEV, what, since when, who leads |
| 30 min (SEV1) | users: banner / social / email | what is happening, what is not affected, when the next update is |
| Every hour | both | progress |
| Resolution | both | what happened in one sentence, what was done, post-mortem in 72 h |

## Contacts

| Who | Role | How | Hours |
|-----|------|-----|-------|
| | owner | | |
| | responds to SEV1 | | |
| | Schneier / security | | |
| | registrar support | | |
| | hosting support | | |
