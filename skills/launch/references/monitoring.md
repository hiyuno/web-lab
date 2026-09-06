# Monitoring and alerts · [project]

Date: [yyyy-mm-dd] · Author: Allspaw · Alerts go to: [name] via [channel] · Backup: [name]

Principle: few alerts, all actionable. Alert when the user's experience is compromised, not on
every blip.

## What is watched

| Signal | Tool | Alert rule | To whom | Review |
|--------|------|------------|---------|--------|
| Availability | [Sentry Uptime / OnlineOrNot / UptimeRobot] | 3 consecutive failures from ≥ 2 regions | | immediate |
| Application errors | Sentry | new error type; > [n] events in 10 min | | immediate |
| Field Core Web Vitals | Vercel Speed Insights | LCP p75 > 2.5 s or INP p75 > 200 ms for 7 days | | weekly |
| Certificate | domain monitor | expires in < 14 days | | immediate |
| Domain | registrar + monitor | expires in < 60 days; change in NS/MX/TXT/CAA | | immediate |
| Indexing | Search Console | coverage drop; new crawl errors | | daily 14 days, then weekly |
| 404 | hosting logs / Search Console | new pattern with > [n] hits | | daily 14 days |
| Forms | monthly test | email does not arrive | | monthly |
| Backups | provider | backup failure | | immediate |
| Hosting budget | Vercel | > [ ]% of the plan | | weekly |

## Sentry

- DSN in environment variables; `sendDefaultPii: false`; `beforeSend` that strips email, IP and name.
- Release per commit; source maps uploaded in CI, not public.
- Alerts: new issue → [channel]; regression → [channel]; spike → [channel].

## Analytics

- Tool: [Plausible / Fathom / Vercel Analytics / GA4 with consent]
- Annotation "Launch [date]" · Goals: [spec conversions]

## Baseline (before cutover, if there was a site)

| Metric | Value | Source | Date |
|--------|-------|--------|------|
| Organic sessions / month | | | |
| Top 10 landing pages | | | |
| Main keyword rankings | | | |
| Field Core Web Vitals | | | |

## 30-day follow-up

| Day | Availability | New errors | GSC coverage | New 404s | Field CWV | Notes |
|-----|--------------|------------|--------------|----------|-----------|-------|
| 1 | | | | | | |
| 2 | | | | | | |
| ... | | | | | | |
| 28 | | | | | compare with lab | |
| 30 | | | | | | closing checkpoint |
