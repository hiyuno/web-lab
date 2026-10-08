# Security headers and CSP

Goal: HSTS, CSP without `unsafe-inline` or `unsafe-eval`, `X-Content-Type-Options: nosniff`,
`Referrer-Policy: strict-origin-when-cross-origin`, minimal `Permissions-Policy`,
`frame-ancestors 'none'` (or `X-Frame-Options: DENY`). Verify with `curl -sI <url>` and on
securityheaders.com. Beizer checks it in phase 6.

Inventory first what each page loads (analytics, fonts, video, maps, payments) and add only
those origins. Every new third party goes through Schneier.

## Astro (content site) · `security.csp` plus `vercel.json`

Astro 7 writes the CSP itself with `security.csp` (stable since 6.0, off by default, unchanged in
7.0): on each page
it hashes the scripts and styles it processes and bundles and emits `script-src` and `style-src`
with those hashes, so no `unsafe-inline`. What it does not process needs care (see the list
below). Everything else goes in `directives`:

```js
// astro.config.mjs
import { defineConfig } from 'astro/config'

export default defineConfig({
  security: {
    csp: {
      directives: [
        "default-src 'self'",
        "img-src 'self' data: https:",
        "font-src 'self'",
        "connect-src 'self' https://plausible.io",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
        'upgrade-insecure-requests',
      ],
    },
  },
})
```

How it arrives and its limits, per the Astro docs:

- By default the policy is a `<meta http-equiv="content-security-policy">` in each page's
  `<head>`. With the `@astrojs/vercel` adapter (10+; 11 for Astro 7) and `staticHeaders: true`,
  prerendered pages get it as a real header in Vercel's config instead; prefer that when the site
  uses the adapter.
- A meta policy cannot carry `frame-ancestors`, `report-uri` or `sandbox` (CSP Level 3, §3.3),
  and `Content-Security-Policy-Report-Only` only exists as a header. So `frame-ancestors` and any
  reporting stay in `vercel.json`, below.
- Not supported: Shiki's inline styles, and `<ClientRouter />`, which we do not use: it is
  incompatible with `security.csp`, so page transitions are CSS `@view-transition`
  (`motion-gsap.md`). External scripts and styles need their origin in
  `scriptDirective.resources` / `styleDirective.resources` (which replace Astro's defaults, so
  add `'self'`) or their hash in `.hashes`. If a directive contains `'unsafe-inline'`, Astro
  drops its hashes from it.
- It does not run in `astro dev`: check it with `astro build` and `astro preview`.
- `<script is:inline>` is not processed and not hashed. The docs are silent, but Astro 7.3's CSP
  build code (`dist/core/csp/common.js`, checked 2026-10-08) hashes only the scripts Astro
  bundles or inlines itself. Move the code into a processed `<script>`, or add its `sha256-…` to
  `scriptDirective.hashes`; confirm in the built policy either way.
- `style="…"` attributes and `define:vars` produce inline style attributes; the docs only offer
  `'unsafe-inline'` with `kind: "attribute"` (since 7.1) for them, which we do not use. Move them
  to classes or CSS custom properties set from a stylesheet.
- The meta policy covers only HTML documents and has no reporting. A site that serves
  user-facing SVG or PDF files, which a meta tag cannot protect, uses `staticHeaders: true` so the
  policy arrives as a header.

JSON-LD is `type="application/ld+json"` and is **not** blocked by CSP; it does not count.

## Consent and Global Privacy Control

Third parties on the CSP allowlist that set non-essential cookies (ads, non-cookieless analytics,
embeds) must not load before consent. The default is a **consent banner** with Accept and Reject
equally easy; the reference tool is **Klaro** (open source, BSD-3-Clause, self-hosted — no SaaS
dependency; configure each service with its purpose and load its script only on consent via
`data-name`/`type="text/plain" data-type`). **Exception:** a site with **cookieless analytics
only** (e.g. Plausible) sets no non-essential cookies and needs no banner.

**Honor Global Privacy Control** on every site. GPC arrives as the `Sec-GPC: 1` request header and
the `navigator.globalPrivacyControl` property. Treat it as an opt-out of sale/share and of
non-essential cookies, before any banner renders and with no dark-pattern re-prompt:

```js
// Run before loading non-essential scripts / showing the banner.
const gpc = navigator.globalPrivacyControl === true
if (gpc) {
  // Default everything non-essential to rejected; do not re-prompt.
  // Klaro: pass { default: false } and skip auto-show for GPC visitors.
}
```

Klaro does not read GPC itself, so this gate is wired by hand. Server-side, code that decides
whether to sell/share may also read the `Sec-GPC` header. See
`skills/security/references/privacy-us.md` (GPC is a legal opt-out in California and 12+ US states)
and `skills/content/references/legal.md` (banner and cookie-policy copy).

The other headers, and the CSP header that carries only what a meta tag cannot, in `vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains" },
        { "key": "Content-Security-Policy", "value": "frame-ancestors 'none'" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
        { "key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=(), payment=(), usb=()" },
        { "key": "X-Frame-Options", "value": "DENY" }
      ]
    }
  ]
}
```

The browser enforces every policy it receives, so this header and Astro's policy add up; neither
loosens the other.

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
    "connect-src 'self' https://api.stripe.com",
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
for a week with `report-to`, then make it enforced. That mode is a header, never a meta tag, and
the Astro docs describe no report-only option for `security.csp`: on Astro, check the policy on a
preview deployment and the browser console before it reaches production.

On Astro with `staticHeaders: true`, `curl -sI` must show two `Content-Security-Policy` headers,
Astro's and the `frame-ancestors` one from `vercel.json`. The adapter docs do not say how the two
merge. Its code (`@astrojs/vercel` 11.0, checked 2026-10-08) writes both into the same routes
list in `.vercel/output/config.json`, `vercel.json`'s first and one CSP route per page after
them, and Vercel's docs do not say whether a later header of the same name replaces or adds. So
check it on every deployment: if only one is present, one replaced the other, and the missing
policy is restored before the checkpoint.

On Astro with the meta policy, `curl -sI` shows only the `frame-ancestors` header; read the rest
in the page itself:

```bash
curl -s https://<staging> | grep -io '<meta http-equiv="content-security-policy"[^>]*>'
```
