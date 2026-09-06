# Security tests on staging · [project]

Date: [yyyy-mm-dd] · Author: Beizer · Interpreted by: Schneier · Staging: [URL]

**Only against the user's own staging. Never production. Never third-party sites.** Warn the
user before the active scan; it can generate test emails and records.

## 1. Dependencies and secrets

```bash
pnpm audit --audit-level=high
gitleaks detect --source . --log-opts="--all" --redact
```

| Test | Result | Severity if it fails |
|------|--------|----------------------|
| audit highs/criticals | | critical if it reaches production; major if dev only |
| gitleaks | | blocker; rotate the secret today even if deleted |

## 2. Transport and headers (from the crawl)

```bash
curl -sI https://<staging> | grep -iE "strict-transport|content-security|x-content-type|referrer|permissions|x-frame"
curl -sI http://<staging> | head -3   # expect 301/308 to https
```

- [ ] HSTS · CSP without `unsafe-inline` in script-src · nosniff · Referrer-Policy · Permissions-Policy · frame-ancestors
- [ ] Valid certificate; no mixed content (browser console)

## 3. OWASP ZAP

Baseline (passive, safe, ~5 minutes):

```bash
docker run --rm -v "$PWD/docs/06-qa:/zap/wrk:rw" -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t https://<staging> -r zap-baseline.html -J zap-baseline.json -I
```

Authenticated active scan (applications only, with a test user, warning the user):

```bash
docker run --rm -v "$PWD/docs/06-qa:/zap/wrk:rw" -t ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py -t https://<staging> -r zap-full.html -J zap-full.json -I -j
```

Known false positives are listed in `zap-rules.tsv` with a reason. High alerts = critical; medium
= major unless justified.

| Alert | ZAP level | URL | Real / false positive | Severity | Fix |
|-------|-----------|-----|-----------------------|----------|-----|
| | | | | | |

## 4. Authentication and authorization (if there are accounts)

With two test users A and B:

| Test | How | Expected | Result |
|------|-----|----------|--------|
| IDOR read | with session A, open the URL of a resource of B | 404 or 403, same message as nonexistent | |
| IDOR write | with session A, send the edit/delete action with B's id | rejected, nothing changes | |
| Expired session | delete the session cookie and repeat an action | redirects to login, no 500 | |
| Login rate limit | 20 failed attempts in a row | block or delay before the 20th | |
| Enumeration | login and recovery with a nonexistent email | same message as with an existing one | |
| Open redirect | `?returnTo=https://evil.example` after login | ignored or relative paths only | |
| Cookies | inspect in DevTools | HttpOnly, Secure, SameSite | |
| Sign out | go back after signing out | no private content shown | |

## 5. Inputs

| Test | Fields | Expected | Result |
|------|--------|----------|--------|
| HTML and quotes `<b>x</b>"'` | all text ones | escaped; does not run or break | |
| Very long (10,000 characters) | text and textarea | rejected with a message; no 500 | |
| File with fake extension (`.png` that is `.html`) | uploads | rejected by real type | |
| Very large file | uploads | rejected by size | |
| Manipulated URL params (`?page=-1`, `?id=abc`) | listings and details | 400/404, no 500 or stack trace | |

## 6. Exposure

- [ ] `/.env`, `/.git/HEAD`, source maps, backups, `/api/*` without auth: from the crawl, all blocked
- [ ] Error messages to the user without stack traces or internal paths
- [ ] API responses without extra fields (check a JSON in DevTools)

## Schneier's verdict

[approved | with conditions | blocked] · [reason] · [date]
