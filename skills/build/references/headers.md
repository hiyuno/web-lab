# Security headers and CSP

Goal: HSTS, CSP without `unsafe-inline` or `unsafe-eval`, `X-Content-Type-Options: nosniff`,
`Referrer-Policy: strict-origin-when-cross-origin`, minimal `Permissions-Policy`,
`frame-ancestors 'none'` (or `X-Frame-Options: DENY`). Verify with `curl -sI <url>` and on
securityheaders.com. Beizer checks it in phase 6.

Inventory first what each page loads (analytics, fonts, video, maps, payments) and add only
those origins. Every new third party goes through Schneier.

## Astro (static site) · `vercel.json`

With no inline scripts of your own, the CSP can be static. Astro injects inline styles for
components; use `style-src 'self' 'unsafe-inline'` only if you cannot avoid it, or set
`build.inlineStylesheets: 'never'`.

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://plausible.io; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=(), usb=()" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    }
  ]
}
```

If inline scripts are unavoidable (JSON-LD is `type="application/ld+json"` and is **not** blocked
by CSP; it does not count), use hashes: `script-src 'self' 'sha256-...'`. Astro can generate the
hashes with `experimental.csp` in recent versions; check the docs for your version.

## Next.js (application) · CSP with nonce in `proxy.ts` (formerly `middleware.ts`)

Next.js needs inline scripts to hydrate, so a strict CSP uses a per-request nonce. That forces
dynamic rendering on the routes that receive it; for static marketing pages use a hash-based CSP
or split them into Astro.

```ts
// proxy.ts (Next.js 16) — headers and redirects only. NEVER the auth barrier.
import { NextResponse, type NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  const nonce = Buffer.from(crypto.randomUUID()).toString('base64')
  const isDev = process.env.NODE_ENV === 'development'
  const csp = [
    "default-src 'self'",
    `script-src 'self' 'nonce-${nonce}' 'strict-dynamic'${isDev ? " 'unsafe-eval'" : ''}`,
    `style-src 'self' 'nonce-${nonce}'`,
    "img-src 'self' blob: data: https:",
    "font-src 'self'",
    "connect-src 'self' https://*.clerk.accounts.dev https://api.stripe.com",
    "frame-src https://js.stripe.com https://checkout.stripe.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "object-src 'none'",
    'upgrade-insecure-requests',
  ].join('; ')

  const headers = new Headers(request.headers)
  headers.set('x-nonce', nonce)
  headers.set('Content-Security-Policy', csp)

  const response = NextResponse.next({ request: { headers } })
  response.headers.set('Content-Security-Policy', csp)
  return response
}

export const config = {
  matcher: [{ source: '/((?!api|_next/static|_next/image|favicon.ico).*)', missing: [{ type: 'header', key: 'next-router-prefetch' }, { type: 'header', key: 'purpose', value: 'prefetch' }] }],
}
```

Read the nonce in the layout with `(await headers()).get('x-nonce')` and pass it to `<Script nonce>`.

Remaining headers in `next.config.ts`:

```ts
const securityHeaders = [
  { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains' },
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), payment=(self "https://js.stripe.com"), usb=()' },
  { key: 'X-Frame-Options', value: 'DENY' },
]
export default { async headers() { return [{ source: '/(.*)', headers: securityHeaders }] } }
```

## Verification

```bash
curl -sI https://<staging> | grep -iE "strict-transport|content-security|x-content-type|referrer|permissions|x-frame"
```

Report-only mode first if the site is already in production: `Content-Security-Policy-Report-Only`
for a week with `report-to`, then make it enforced.
