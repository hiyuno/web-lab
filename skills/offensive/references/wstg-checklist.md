# WSTG-driven checklist · identity first

Mallory's working list for an offensive pass against the user's own staging. It follows the OWASP
Web Security Testing Guide (WSTG) top-level categories, reordered so **identity comes first**,
because that is where account/data/access takeovers live. It is the map, not a payload cookbook:
each row says what to probe and what a pass looks like; the methodology and the defenses are
summarized, not step-by-step exploits.

- **Severity** is not set here. Every confirmed finding is rated with
  `skills/security/scripts/risk_rating.py` so it matches Schneier's grades.
- **Owners of the rules** are cited, not restated: the "Better Auth configuration" checklist
  (`skills/security/references/code-review.md`, §6), the public-write-surfaces review
  (`skills/security/references/public-write-surfaces.md`), the headers reference
  (`skills/build/references/headers.md`), and the shared severity/verdict method in `CLAUDE.md`.
- **Scope and limits** are the rules of engagement in `agents/mallory.md` and SKILL step 0:
  Yuno's staging only, report-only, no destruction or DoS, confirmation at minimum impact.

WSTG ids below use the v4.2 scheme (stable at the time of writing). The 2025 edition renumbers
some categories; record the id and the version with each finding so it stays traceable.

## A · Identity management — WSTG-IDENT

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| Role definitions: can a client set its own role at sign-up? | role assigned server-side only | §6 item 7 (global vs org role) |
| Account enumeration on sign-up/sign-in/recovery | same message, status and timing for existing vs. nonexistent email | §6 item 5 |
| Guessable/weak account provisioning, default accounts | no default or guessable credentials | — |
| Scripted sign-up in a loop (account creation abuse) | rate limited and email-verification gated | §6 items 1, 5; public-write-surfaces §1 |

## B · Authentication — WSTG-ATHN

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| Credentials over an unencrypted channel | HTTPS only; no login over HTTP | headers.md (HSTS) |
| Default/weak lockout: 20 failed sign-ins and 20 reset requests across cold starts | 429 before the 20th, held across serverless instances | §6 item 1 |
| Weak password policy / breached passwords | min length enforced; breached-password check when ASVS asks | §6 item 6 |
| Password reset: token entropy, single use, expiry | random, one-time, short-lived token | code-review.md §3 |
| **Password-reset poisoning** via `Host` / `X-Forwarded-Host` | reset link built from configured `baseURL`, not the request header | §6 item 3 |
| Email-change flow | re-authenticates, notifies the old address, does not take over on its own | — |
| Second factor weak or bypassable; enrollment not enforced for admins | 2FA on; admins enrolled before launch | §6 item 4 |
| AiTM/session-phishing resilience (documented risk, not run live) | short sessions, revocation, re-auth on sensitive actions | §6 items 1, 2 |

## C · Session management — WSTG-SESS

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| Cookie attributes | HttpOnly, Secure, SameSite | code-review.md §3 |
| **Session fixation**: does the session id rotate on login? | new session id after authentication | code-review.md §3 (rotation) |
| Predictable or non-rotating tokens | tokens are random and rotate after privilege change | — |
| Logout invalidates server-side; back button after logout | no private content served post-logout | qa security.md |
| Session survives a password reset / change | revoked on reset and change, within `cookieCache.maxAge` | §6 item 2 |
| CSRF on state-changing actions; untrusted `Origin` on the auth handler | rejected; origin check on | §6 item 3 |

## D · Authorization between users — WSTG-ATHZ (IDOR/BOLA)

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| IDOR read: session A opens B's resource id | same response as nonexistent (404/403) | code-review.md §3; public-write-surfaces §3 |
| IDOR write: A sends edit/delete/vote with B's id | rejected, nothing changes | public-write-surfaces §3 |
| Vertical escalation: user calls an admin-only endpoint directly | rejected on the server, not just hidden in UI | public-write-surfaces §2 |
| Org-scoped query trusts `activeOrganizationId` | query joins `member` on (orgId, userId) and checks role | §6 item 7 |
| OAuth: `redirect_uri` exact match, `state` bound to session, PKCE present | no subdomain wildcard; state verified; PKCE on; account-linking re-authenticates, never auto-links by email alone | code-review.md §3 |
| Directory traversal / path manipulation | path validated before use | code-review.md §2 |

## E · Input validation & injection — WSTG-INPV

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| SQL injection (confirm with a low `--level`/`--risk` sqlmap on one agreed param) | parameterized queries; no injection | code-review.md §3 (input validation) |
| Reflected / stored / DOM XSS, especially public-write surfaces | output encoded; CSP blocks injected script | public-write-surfaces §3; headers.md |
| Server-side template injection | no template eval of user input | code-review.md §3 |
| SSRF: fields that fetch a URL server-side → internal/metadata addresses | blocked; allowlist of outbound hosts (report attempt, do not pivot) | code-review.md §3 |
| Host-header injection beyond reset (cache, links) | app does not trust the Host header | §6 item 3 |

## F · Business logic & files — WSTG-BUSL / file upload

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| File upload: fake type/extension, oversized, path in filename | validated by real type and size, renamed, served off-origin | code-review.md §3 (files); public-write-surfaces §3 |
| Stored HTML/SVG that executes when served | served as attachment / separate origin, not inline | — |
| Workflow bypass: skip a step, replay, race a double-submit | idempotent, server-enforced order | public-write-surfaces §3 (votes) |

## G · API — WSTG-APIT

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| BOLA / BFLA: object- and function-level authorization | authorized per object and per function in the query | code-review.md §3 |
| Mass assignment | DTO/Zod omits server-set fields | public-write-surfaces §3 |
| Unexpected verbs on a route | only intended methods handled | code-review.md §2 |
| Excessive data in JSON | response carries only DTO fields | code-review.md §3 (data protection) |

## H · Configuration & deployment — WSTG-CONF

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| Security headers: HSTS, CSP without `unsafe-inline`, nosniff, Referrer-Policy, Permissions-Policy, frame-ancestors | all present; CSP actually blocks injected script | headers.md; qa security.md §2 |
| Exposed `.env`, `.git`, source maps, backups, admin panels without auth | all blocked | qa security.md §6 |
| Error responses | generic to the user, no stack trace or internal path | code-review.md §3 (errors) |

## I · Supply chain — dependencies

| Probe | What a pass looks like | Defense (cite) |
|-------|------------------------|----------------|
| `pnpm audit` / `osv-scanner` highs cross-checked against reachable code | no reachable high/critical without a plan | beizer.md; code-review.md §2 |

## Not covered here, on purpose

Client-side storage minutiae, WebRTC (ASVS V17) and anything needing production data or a
third-party system out of scope. If one becomes relevant, it is a scope change Yuno approves in
the conversation, never a decision taken mid-test.
