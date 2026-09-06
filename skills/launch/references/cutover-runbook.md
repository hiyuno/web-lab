# Cutover-day runbook · [project]

Cutover date: [yyyy-mm-dd hh:mm] · Window: [ ] · Executes: [ ] · Watches: [ ] · Channel: [ ]

Decision deadlines (not debated during the cutover): web/DNS rollback until [hh:mm, +2 h] · email rollback until [+24 h].

## Before starting (T-30 min)
- [ ] Checklist signed; Schneier has approved
- [ ] Everyone in the channel; nobody else deploying
- [ ] Production preview open and verified
- [ ] DNS snapshot at hand; rollback commands copied below

## Steps

| # | Step | Who | Command / action | Verification | Rollback of this step |
|---|------|-----|------------------|--------------|-----------------------|
| 1 | Promote deployment to production | | `vercel promote <url>` or Promote button | `curl -sI https://<prod-preview>` 200 | Instant Rollback |
| 2 | Add / point domain | | A @ → 76.76.21.21 · CNAME www → cname.vercel-dns.com | `dig +short example.mx` · `dig +short www.example.mx` | restore A/CNAME from snapshot |
| 3 | Certificate issued | | wait in Vercel → Domains | `curl -sI https://example.mx` no TLS error | — |
| 4 | Automated 60-minute verification | | `python3 launch_check.py https://example.mx --redirects ... --seo ... --old-urls ...` | no access or continuity criticals | see decision |
| 5 | Manual: form, login, analytics | | | email received; live event | — |
| 6 | Sitemap to Search Console and Bing; index home | | | "Sitemap submitted successfully" | — |
| 7 | Email (if MX changes) | | MX → new provider | `dig MX example.mx @8.8.8.8` and @1.1.1.1 agree | restore MX from snapshot |
| 8 | Launch annotation in analytics; notify stakeholders | | | | — |

## Watch (T+0 to T+60)
- [ ] Sentry: zero new errors · [ ] Availability: no alerts · [ ] Traffic arriving · [ ] 404s in logs: review patterns

## Decision at T+60
[ ] Continue · [ ] Rollback (reason: ) · Signed by: [ ]

## Rollback

Web (Vercel): Dashboard → Instant Rollback → previous deployment → Confirm. Remember: it does not revert variables or the database; afterwards, `vercel promote <deployment>` to return to normal.

DNS: restore from the `dns-snapshot-[date].json` snapshot. Propagates in ≤ current TTL ([ ] s).

Email: restore MX from the snapshot; re-enable old forwarding if any.

## After
- [ ] Raise TTL back to [3600] when everything is stable (T+24 h at the earliest)
- [ ] Start of the 30-day follow-up (`monitoring.md`)
