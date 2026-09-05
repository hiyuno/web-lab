# Estructura del repositorio

Comandos estándar en `package.json` para que CI y los roles no adivinen:
`dev`, `build`, `preview`, `lint`, `typecheck`, `test`, `test:e2e`, `format`.

## Astro 5 · sitio de contenido

```
.
├── astro.config.mjs
├── src/
│   ├── assets/            # imágenes y fuentes que procesa Astro (de Bellard)
│   ├── components/        # un archivo por componente de Frost; subcarpetas por familia
│   │   ├── ui/            # Button, Input, Link, Card...
│   │   └── blocks/        # Hero, Testimonials, Pricing... (bloques de wireframe)
│   ├── content/           # colecciones: pages, posts, faqs... (texto de los briefs)
│   ├── content.config.ts  # esquemas Zod de las colecciones
│   ├── layouts/           # uno por plantilla del sitemap: Base, Home, Interior, Listado, Detalle, Formulario, Legal
│   ├── pages/             # rutas = sitemap.md; [slug].astro lee de colecciones
│   ├── styles/tokens.css  # copia exacta de docs/04-diseno/tokens.css
│   └── lib/               # seo.ts (metadatos y JSON-LD desde seo.md), utils
├── public/                # favicon, robots.txt, og por defecto
├── tests/                 # vitest (unit) + playwright (e2e)
├── vercel.json            # headers.md + redirects.md
├── lighthouserc.json
└── .github/workflows/ci.yml
```

Reglas: `client:*` solo en `components/ui` interactivos y con razón en el PR; imágenes con
`<Image>`; fuentes locales en `src/assets/fonts` con subconjunto; JSON-LD en el layout desde
`lib/seo.ts`.

## Next.js 16 · aplicación

```
.
├── next.config.ts         # headers, images, experimental.taint
├── proxy.ts               # CSP con nonce, redirecciones; NO auth
├── src/
│   ├── app/
│   │   ├── (marketing)/   # layout ligero, páginas públicas, puede ser estático o Astro aparte
│   │   ├── (app)/         # layout autenticado: dashboard, cuenta...
│   │   │   ├── layout.tsx
│   │   │   ├── loading.tsx
│   │   │   ├── error.tsx
│   │   │   └── <ruta>/page.tsx
│   │   ├── (auth)/        # login, recuperar (páginas propias, nunca modal)
│   │   ├── api/           # route handlers solo para webhooks y APIs externas
│   │   ├── layout.tsx     # tokens.css, fuentes con next/font, nonce a <Script>
│   │   ├── robots.ts · sitemap.ts · opengraph-image.tsx
│   │   └── not-found.tsx
│   ├── actions/           # "use server": delgadas; validan con Zod y llaman a data/
│   ├── data/              # capa de acceso a datos: import 'server-only'; única que toca db y process.env
│   │   ├── auth.ts        # getCurrentUser() con cache()
│   │   ├── db.ts          # cliente Drizzle (Neon)
│   │   └── <entidad>.ts   # get<X>DTO, create<X>, ... con autorización dentro
│   ├── db/schema.ts       # esquema Drizzle
│   ├── components/ui/     # shadcn/ui ajustado a tokens; blocks/ para bloques
│   ├── lib/               # validators (Zod), seo, utils; nada de secretos
│   └── styles/tokens.css
├── drizzle/               # migraciones versionadas
├── drizzle.config.ts
├── tests/                 # vitest + playwright; por acción: feliz, inválido, sin permiso
├── .env.example
├── lighthouserc.json
└── .github/workflows/ci.yml
```

Reglas: `process.env` y `db` solo en `src/data/`; `"use client"` solo en hojas; cada
`actions/*` re-verifica sesión y delega; `[param]` validado con Zod; `route.ts` solo para
webhooks con firma verificada.

## Común

- `CLAUDE.md` del proyecto con stack, comandos, rutas de docs y las reglas de este skill.
- `docs/` con las fases 1 a 5 versionadas junto al código.
- `.gitignore`: `.env*` (excepto `.env.example`), `node_modules`, `.vercel`, `dist`/`.next`, `playwright-report`.
