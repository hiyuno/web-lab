# Security checklist by phase

Minimum list that **Schneier** reviews at the close of every phase and that all roles apply in
their work. Background references: OWASP Top 10, OWASP API Security Top 10, OWASP ASVS level 1
(level 2 with sensitive data). A critical finding blocks the phase transition; a high one blocks
the launch.

## Rules that always apply

- [ ] Authentication, password hashing and card data only through established providers.
- [ ] No secret in the repo, in the client, in logs or in the chat. If one appears, it is rotated that day.
- [ ] Authorization on the server, per resource, in every query.
- [ ] Security tests only against the user's own environments.
- [ ] Hosting, DNS, registrar, repository and analytics accounts with a second factor.
- [ ] Decisions to accept a risk are written with date and reason in the project's `docs/SECURITY-risks.md`.

## Phase 1 · Discovery

- [ ] Threat model written: assets, data and classification (public, internal, personal, sensitive), actors, impact, legal obligations (Mexico's 2025 LFPDPPP, GDPR if there are users in Europe; see `skills/security/references/legal-mx.md`).
- [ ] The spec names the identity and payment providers, if applicable.
- [ ] Retention and deletion of personal data defined.
- [ ] Target ASVS level decided by data classification.

## Phases 2 and 3 · Structure and content

- [ ] Forms with the minimum fields; each field has a written reason.
- [ ] No personal data in URLs or parameters.
- [ ] Privacy notice, terms, and consent management if there are non-essential cookies.
- [ ] User-generated content surfaces identified.
- [ ] Login and recovery error messages defined as generic.

## Phase 4 · Design

- [ ] Login on its own page with correct `autocomplete` and second-factor support.
- [ ] Destructive actions with confirmation and separated from frequent ones.
- [ ] Consent without dark patterns: reject as visible as accept.
- [ ] Session state visible on authenticated screens.
- [ ] Components that show user content marked for mandatory escaping.

## Phase 5 · Development

Frontend:

- [ ] CSP without `unsafe-inline` or `unsafe-eval`; third parties allowlisted.
- [ ] Headers: HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, `frame-ancestors`.
- [ ] No secret reaches the client; `NEXT_PUBLIC_` only for public values.
- [ ] No unsanitized HTML; DOMPurify or equivalent where needed.
- [ ] Form validation repeated on the server.
- [ ] `rel="noopener noreferrer"` on external links; CDN resources with `integrity` or served locally.
- [ ] Versioned lockfile; `npm audit --audit-level=high` clean.

Backend, applications only:

- [ ] Every input validated with a schema at the boundary.
- [ ] Per-resource authorization in every query; tested with another user's id.
- [ ] Parameterized queries; never concatenate input into SQL, commands or paths.
- [ ] Cookies `HttpOnly`, `Secure`, `SameSite`; sessions invalidated on password change.
- [ ] Rate limiting on login, signup, recovery, public forms and expensive endpoints.
- [ ] CSRF covered on every mutation.
- [ ] Uploads: real type, max size, renamed, separate storage and origin.
- [ ] Webhooks verified by signature.
- [ ] Logs without personal data; generic errors to the user.
- [ ] Encryption at rest; sensitive fields encrypted in the application if the model requires it.
- [ ] Exporting and deleting a user's data is possible.
- [ ] `.env` in `.gitignore` from the first commit; `.env.example` with names.

## Phase 6 · QA

- [ ] `npm audit` or `osv-scanner` with no highs or criticals without a plan.
- [ ] `gitleaks detect` over the whole history, clean.
- [ ] Headers verified with `curl -sI` on staging.
- [ ] HTTPS only, redirect from HTTP, no mixed content.
- [ ] If there is auth: IDOR, expired session, attempt limit, generic messages tested.
- [ ] Forms tested with HTML, quotes, max size and fake extensions.
- [ ] If there is an API: OWASP ZAP baseline against staging.
- [ ] `.env`, `.git`, source maps, backups and admin panels are not public.

## Phase 7 · Launch

- [ ] Registrar with 2FA, transfer lock and auto-renewal.
- [ ] DNS with a CAA record; DNSSEC if available.
- [ ] SPF, DKIM and DMARC with `quarantine` or `reject`, even if the site sends no email.
- [ ] HTTPS forced; HSTS with a long `max-age` and `includeSubDomains`.
- [ ] Production variables with least privilege; deploy tokens with expiration.
- [ ] Automatic backups with one tested restore.
- [ ] Availability, error and Core Web Vitals monitoring with alerts to a person.
- [ ] Cookieless analytics or real prior consent.
- [ ] Incident runbook written: outage, breach, expired domain.
- [ ] Schneier's sign-off for go-live.

## Phase 8 · Maintenance

- [ ] Dependabot or Renovate active; security patches within the week.
- [ ] Secret rotation and access review every quarter.
- [ ] Blameless post-mortem after every incident.
- [ ] Annual threat model review, or when the scope changes.
