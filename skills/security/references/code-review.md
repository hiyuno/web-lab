# Code review · phase 5

Manual and by boundaries. Broken access control is the most frequent vulnerability and the one no
scanner finds. Semgrep afterwards, as a safety net.

## 1. One-minute map

```bash
grep -rn "process.env" src --include=*.ts --include=*.tsx | grep -v "src/data/" | grep -v NEXT_PUBLIC_
grep -rln "from '@/data/db'\|from '@/db'" src | grep -v "src/data/"
grep -rn "dangerouslySetInnerHTML\|set:html" src
grep -rn "NEXT_PUBLIC_" .env.example src | grep -iE "secret|key|token|password"
grep -rn "'use server'" src -l
grep -rn "export async function \(GET\|POST\|PUT\|PATCH\|DELETE\)" src/app/api
```

The first two must come back empty (except `proxy.ts` and webhooks). The fourth must always be
empty. The last two are your list of entry points.

## 2. Files in risk order

1. `proxy.ts` / `middleware.ts`: headers and redirects only. If it decides auth, it is a high finding.
2. `src/app/api/**/route.ts`: webhook signature before reading the body; no business logic.
3. `src/actions/**`: every action validates with Zod, calls `src/data`, returns only what is needed, generic error.
4. `src/data/**`: `import 'server-only'`; authenticates; **authorizes in the query** (owner or organization); DTO.
5. `"use client"` components: props without private fields; narrow types.
6. `[param]` folders: parameter validated before use.
7. `next.config.ts`, `vercel.json`, `astro.config.mjs`: headers, CSP, redirects, bounded `images.remotePatterns`.
8. `package.json` and lockfile: new dependencies justified; `pnpm audit`.

## 3. Categories (OWASP Code Review Guide) and what to look for

| Category | Look for | Typical finding |
|----------|----------|-----------------|
| Input validation | Zod at every boundary; allowlists; max size | TS type trusted at runtime |
| Output encoding | JSX escapes by default; external HTML through DOMPurify; URLs with `encodeURIComponent` | `dangerouslySetInnerHTML` with CMS |
| Authentication | Better Auth configured per §6; re-verification in every action; HttpOnly Secure SameSite cookies | auth only in the page |
| Sessions | expiration; revocation on password reset and change (§6); rotation after privilege elevation | eternal session |
| Access control | ownership in the query; roles verified on the server; same error for "does not exist" and "not yours" | IDOR |
| Cryptography | nothing home-grown; secrets in env; password hashing via Better Auth (§6); `crypto.randomUUID` | secret in the repo |
| Errors and logging | generic to the user; detail in the log without personal data; sensitive actions logged with id | stack trace to the client |
| Data protection | minimal DTO; sensitive data encrypted if the model requires; deletion and export possible | full record to the client |
| Communication | HTTPS; HSTS; third parties over HTTPS; signed webhooks | unsigned webhook |
| Configuration | CSP without unsafe-inline; headers; `.env` in gitignore; private source maps | CSP with unsafe-inline |
| Files | real type, size, renamed, separate origin | trusted extension |
| Rate limiting | login, signup, recovery, forms, expensive endpoints; auth endpoints per §6 | none |

## 4. Semgrep (complement)

```bash
semgrep --config p/owasp-top-ten --config p/nextjs --config p/typescript src
```

Every result is read; a false positive is documented, not blindly silenced.

## 5. Writing the finding

With `risk_rating.py` for the severity and `verdict.md` for the format. "What can happen" is a
two-sentence story the business owner understands: "A customer changes the number in their order
URL and sees another customer's order, with name and address. Anyone with an account can do it
in two minutes."

## 6. Better Auth configuration

The one checklist for every project that uses Better Auth. Other roles and skills cite it by
name; they do not restate it. Defaults below were checked against the Better Auth docs on
2026-10-08; anything marked "check on the pinned version" was not confirmed there and is read
in `node_modules/better-auth` or tested before the item is ticked.

| # | Item | Severity if missing |
|---|------|---------------------|
| 1 | **Rate limiting inside Better Auth.** Sign-in, sign-up, forget/reset password and two-factor go through the `api/auth/[...all]` handler, not our server actions, so the app's `rateLimit()` never sees them. Set `rateLimit.storage` to `"database"` or `"secondary-storage"` (e.g. Upstash Redis); the default `"memory"` store does not survive across serverless instances on Vercel. Keep or tighten the built-in rules (`/sign-in/email` and `/two-factor/*`: 3 requests per 10 s) and add `customRules` for sign-up and the password-reset request path (`/request-password-reset` or `/forget-password`; check the name on the pinned version). Limiting is on by default only in production; set `rateLimit.enabled: true` to test it on a preview | high |
| 2 | **Session revocation.** `emailAndPassword.revokeSessionsOnPasswordReset: true` (default `false`). The change-password call passes `revokeOtherSessions: true`. If `session.cookieCache` is enabled, keep its `maxAge` short (minutes): a revoked session stays valid on other devices until the cache expires | high |
| 3 | **Origins and CSRF.** `baseURL` (or `BETTER_AUTH_URL`) set explicitly, never inferred from the request. `trustedOrigins` lists only exact origins; no wildcards such as `https://*.vercel.app`. Each Vercel environment sets its own exact URL. The same list validates `callbackURL` and redirect targets. `advanced.disableOriginCheck` stays off. Better Auth's handler is a route handler, so the CSRF protection of Next.js server actions does not apply to it; its own origin check is the barrier | high |
| 4 | **Second factor.** The `twoFactor` plugin is on for any app with accounts. Users with an admin-plugin admin role (`adminRoles`, default `["admin"]`) or listed in `adminUserIds` have it enrolled before launch. The plugin does not force enrollment; enforce it in our code (refuse admin actions without it) | high for admins, medium otherwise |
| 5 | **Enumeration and email verification.** With the default config, sign-up with an existing email returns `422`; with `requireEmailVerification: true` or `autoSignIn: false` it returns the same `200` either way. `requireEmailVerification: true` wherever an account can write publicly (see `public-write-surfaces.md`). Check sign-up, sign-in and recovery responses on the pinned version | medium |
| 6 | **Password storage.** Default scrypt; never override `emailAndPassword.password.hash`/`verify`. `minPasswordLength` at least 8 (default 8), `maxPasswordLength` 128 (default). Add the `haveIBeenPwned` plugin when the ASVS level asks for breached-password checks; it sends only the first five characters of the SHA-1 hash | low |
| 7 | **Organizations and roles.** The admin plugin's `user.role` is a global role. The organization role lives in the `member` table (`organizationId`, `userId`, `role`). `session.activeOrganizationId` is set by the client (`organization.setActive`) and is a hint, never proof of membership: org-scoped queries join `member` on (orgId, userId) and check the role there. Whether `setActive` verifies membership: check on the pinned version | high if a query trusts `activeOrganizationId` |
| 8 | **`BETTER_AUTH_SECRET`.** At least 32 random bytes (`openssl rand -base64 32`), a different value per Vercel environment, name only in `.env.example`, on the phase 8 rotation list. Production throws if it is unset. Rotating it invalidates sessions and anything it encrypts unless the pinned version's non-destructive rotation is used; check on the pinned version | low |
| 9 | **Credential store.** The `account` table holds password hashes (`password`) and OAuth tokens (`accessToken`, `refreshToken`, `idToken`); `session` holds session tokens; the `twoFactor` table holds 2FA secrets and backup codes. Database access, read replicas and backups are scoped as credential stores in the threat model | per threat model |

Sources: better-auth.com/docs/concepts/rate-limit, /docs/authentication/email-password,
/docs/concepts/session-management, /docs/reference/options, /docs/reference/security,
/docs/plugins/2fa, /docs/plugins/organization, /docs/plugins/admin,
/docs/plugins/have-i-been-pwned, /docs/concepts/database.
