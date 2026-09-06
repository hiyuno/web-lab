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
| Authentication | provider; re-verification in every action; HttpOnly Secure SameSite cookies | auth only in the page |
| Sessions | expiration; invalidation on password change; rotation after privilege elevation | eternal session |
| Access control | ownership in the query; roles verified on the server; same error for "does not exist" and "not yours" | IDOR |
| Cryptography | nothing home-grown; secrets in env; hashes via provider; `crypto.randomUUID` | secret in the repo |
| Errors and logging | generic to the user; detail in the log without personal data; sensitive actions logged with id | stack trace to the client |
| Data protection | minimal DTO; sensitive data encrypted if the model requires; deletion and export possible | full record to the client |
| Communication | HTTPS; HSTS; third parties over HTTPS; signed webhooks | unsigned webhook |
| Configuration | CSP without unsafe-inline; headers; `.env` in gitignore; private source maps | CSP with unsafe-inline |
| Files | real type, size, renamed, separate origin | trusted extension |
| Rate limiting | login, signup, recovery, forms, expensive endpoints | none |

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
