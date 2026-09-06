# Launch checklist · [project]

Date: [yyyy-mm-dd] · Author: Allspaw · Every item with the date and who verified it. Signatures at the end.

## Entry
- [ ] `docs/06-qa/exit.md` signed by Beizer and Schneier, no blockers or criticals · [date, who]

## Accounts and domain (7.1)
- [ ] Registrar with 2FA, lock, auto-renewal, in the owner's name
- [ ] Individual, minimal access on registrar, DNS, hosting, repo, analytics, payments
- [ ] CAA published · DNSSEC on or noted
- [ ] DNS snapshot saved

## Email (7.2)
- [ ] Single SPF, -all, ≤ 10 lookups
- [ ] DKIM per source
- [ ] DMARC published with policy [ ] and rua

## Production (7.3)
- [ ] Production only from main; branch protection
- [ ] Production variables loaded; sensitive ones separate from preview; tokens with expiration
- [ ] Domain on the project; certificate issued
- [ ] HTTPS forced; HSTS
- [ ] Redirects loaded and tested one by one against the production URL

## Observability (7.4)
- [ ] Multi-region availability, alert after 3 failures
- [ ] Errors (Sentry) without personal data; alerts configured
- [ ] Field Core Web Vitals
- [ ] Domain watch: NS, MX, TXT, CAA, expiries
- [ ] Alerts reach [name] via [channel]; tested with a test alert
- [ ] Analytics with correct consent; launch annotation ready
- [ ] Baseline exported (rankings, landing pages) if there is a previous site

## Backups and rollback (7.5)
- [ ] Automatic backups; retention [ ] days
- [ ] Restore tested on [date] in [environment]
- [ ] Instant Rollback tested; warnings (env, DB, auto-assign) in the runbook
- [ ] DNS rollback: snapshot + time with current TTL

## Cutover (7.6)
- [ ] TTL lowered to 300 s on [date] (24-72 h before) and confirmed with dig
- [ ] Window: [day and time], midweek, early
- [ ] Rollback deadlines: web/DNS 2 h · email 24 h
- [ ] `cutover-runbook.md` complete with who does each step
- [ ] Schneier's verdict: [approved | with conditions] · [date]

## Signatures
Allspaw: [date] · Schneier: [date] · User (go-live authorized): [date]
