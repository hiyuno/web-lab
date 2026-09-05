# Cabeceras de seguridad y CSP

Objetivo: HSTS, CSP sin `unsafe-inline` ni `unsafe-eval`, `X-Content-Type-Options: nosniff`,
`Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy` mínima,
`frame-ancestors 'none'` (o `X-Frame-Options: DENY`). Verifica con `curl -sI <url>` y en
securityheaders.com. Beizer lo comprueba en la fase 6.

Inventaría primero qué carga cada página (analítica, fuentes, videos, mapas, pagos) y añade
solo esos orígenes. Cada tercero nuevo pasa por Schneier.

## Astro (sitio estático) · `vercel.json`

Sin scripts inline propios, la CSP puede ser estática. Astro inyecta estilos inline para los
componentes; usa `style-src 'self' 'unsafe-inline'` solo si no puedes evitarlo, o configura
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

Si hay scripts inline inevitables (JSON-LD es `type="application/ld+json"` y **no** lo bloquea
la CSP; no cuenta), usa hashes: `script-src 'self' 'sha256-...'`. Astro puede generar los
hashes con `experimental.csp` en versiones recientes; revisa la documentación de la versión.

## Next.js (aplicación) · CSP con nonce en `proxy.ts` (antes `middleware.ts`)

Next.js necesita scripts inline para hidratar, así que la CSP estricta usa un nonce por
petición. Esto obliga a renderizado dinámico en las rutas que la reciben; para páginas
estáticas de marketing usa una CSP con hashes o sepáralas en Astro.

```ts
// proxy.ts (Next.js 16) — solo cabeceras y redirecciones. NUNCA la barrera de auth.
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

Lee el nonce en el layout con `(await headers()).get('x-nonce')` y pásalo a `<Script nonce>`.

Resto de cabeceras en `next.config.ts`:

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

## Verificación

```bash
curl -sI https://<staging> | grep -iE "strict-transport|content-security|x-content-type|referrer|permissions|x-frame"
```

Modo reporte primero si el sitio ya está en producción: `Content-Security-Policy-Report-Only`
durante una semana con `report-to`, luego se hace obligatoria.
