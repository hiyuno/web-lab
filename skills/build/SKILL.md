---
name: build
description: Osmani y Hopper, ingeniería. Fase 5 del proceso de web-lab. Con el diseño aprobado, construye el sitio o la app en Astro 5 o Next.js 16 siguiendo la spec: fundación del repo con TypeScript, Tailwind v4 con los tokens de Frost, CI con pruebas, auditoría y Lighthouse CI con presupuesto de rendimiento, tareas derivadas de las historias, ciclo por tarea con prueba primero y pull request con preview, pista frontend (componentes, SEO, cabeceras y CSP, Core Web Vitals) y pista backend solo para apps (capa de acceso a datos server-only, Drizzle y Postgres, Zod, auth con proveedor, autorización por recurso, rate limiting, webhooks). Usa este skill cuando el usuario pida construir, implementar, programar, maquetar, "pasar el diseño a código", montar el repo, configurar CI, Next.js, Astro, base de datos, login, API, server actions, o cuando un proyecto tenga docs/04-diseno aprobado y aún no tenga código. Trabaja por tareas con checkpoint del usuario.
---

# /build · Osmani y Hopper

Este skill corre la fase 5: del diseño aprobado a un staging con contenido real que Beizer
puede probar. Lo cargan dos roles: **Osmani** (frontend y rendimiento, `agents/osmani.md`) y
**Hopper** (backend, datos y auth, `agents/hopper.md`). Los pasos 5.0 a 5.3 y 5.6 a 5.9 son
comunes; el 5.4 es la pista de Osmani y el 5.5 la de Hopper, que solo se activa si
`decision-arquitectura.md` dice aplicación.

El resultado es el repositorio del proyecto en staging más `docs/05-desarrollo/` con
`tareas.md`, `frontend.md` y, si aplica, `backend.md`.

## Regla de oro: spec → tarea → prueba → código → verificar → commit

Nada se construye sin una tarea que venga de una historia de la spec. Ninguna tarea se
implementa sin su prueba en rojo primero. Ningún commit sin verificar en el navegador y sin
poder explicarlo. Nunca se desactiva un lint, una prueba o una advertencia para que pase el
build. Responde en el idioma del usuario; código, nombres y commits en inglés.

Trabajas como orquestador: delegas tareas al subagente `osmani` o `hopper` según la pista,
una o pocas a la vez, con el issue completo en el prompt, y revisas cada pull request antes
de mezclar. Los cambios de alcance vuelven a la spec primero.

## Paso 5.0 · Entrada

0. Lee `<web-lab>/learnings/osmani.md`, `<web-lab>/learnings/hopper.md` y
   `<web-lab>/docs/PREFERENCIAS.md`.
1. Lee `docs/01-descubrimiento/spec.md`, `decision-arquitectura.md` y
   `modelo-de-amenazas.md`; `docs/03-contenido/seo.md`, `assets.md`, `legales.md` y los
   briefs; `docs/04-diseno/tokens.css`, `componentes/`, `plantillas/`, `accesibilidad.md`,
   `motion.md` y el prototipo. Si el diseño no está aprobado, detente y propón `/design-system`.
2. Confirma con el usuario: framework según la decisión, gestor de paquetes (pnpm por
   defecto), hosting (Vercel por defecto), repositorio remoto y quién revisa los pull requests.
   No crees el repo remoto ni despliegues sin que lo pida.

## Paso 5.1 · Fundación del repositorio

Un día que ahorra semanas. Con `references/estructura.md` para las carpetas de cada framework:

1. Scaffold: `pnpm create astro@latest` o `pnpm create next-app@latest` con TypeScript
   estricto. Tailwind v4 y `docs/04-diseno/tokens.css` como hoja principal.
2. `.gitignore` con `.env*` (menos `.env.example`) desde el primer commit. `.env.example` con
   nombres y descripción, nunca valores.
3. Lint y formato (ESLint, Prettier). Hooks de pre-commit con lint-staged: lint, tipos y
   `gitleaks protect --staged`.
4. CI con `references/ci.yml`: tipos, lint, pruebas, build, `pnpm audit --audit-level=high` y
   Lighthouse CI con `references/lighthouserc.json` como umbral que falla el build.
5. Vercel enlazado al repo: preview por rama, producción solo desde `main`. La preview de
   `main` es staging. Skills `deploy-to-vercel` o `vercel:deploy` si hace falta.
6. Protección de rama `main`: CI verde y una revisión antes de mezclar.
7. Dependabot o Renovate con agrupación semanal y parches de seguridad inmediatos.
8. `CLAUDE.md` del proyecto: stack, comandos, dónde están los docs, reglas de este skill.
   Parte del de web-lab.
9. Primer commit: "chore: scaffold" con todo lo anterior. Verifica que la preview levanta.

## Paso 5.2 · Plan de tareas

```bash
python3 <skill>/scripts/tasks_from_spec.py docs/01-descubrimiento/spec.md > docs/05-desarrollo/tareas.md
```

Genera una sección por historia con sus criterios de aceptación convertidos en casos de
prueba y una tabla de tareas vacía. Completa cada tarea con `references/tarea.md`: contexto,
objetivo, criterios, restricciones, pista (frontend o backend), dependencias y comando de
prueba. Tareas del tamaño de un pull request revisable: un componente, una plantilla, una
acción, una integración. Ordena por dependencias; primero fundación, luego componentes base
(botón, campo, enlace), luego plantillas, luego flujos.

**Checkpoint A**: el usuario aprueba el plan de tareas y el orden. Aquí se ve si algo de la
spec no cabe en el plazo; se decide antes de escribir código.

## Paso 5.3 · Ciclo por tarea

El mismo para ambas pistas. Delega al subagente con el issue completo y estas reglas:

1. Rama `feat/<id>-<slug>` desde `main` actualizado.
2. Prueba primero, en rojo: unitaria para lógica y componentes, Playwright para flujos.
   Correrla y verla fallar antes de implementar.
3. Implementar solo lo que la prueba pide. Componentes de Frost con sus nueve estados;
   valores solo desde tokens.
4. Verificar en el navegador integrado en 375 y 1280, modo claro y oscuro si existe.
5. `pnpm lint && pnpm typecheck && pnpm test` verdes. Si algo falla, se arregla o se reporta;
   nunca se silencia.
6. Commit convencional pequeño: `feat(scope): ...`, `fix:`, `chore:`, `test:`. Un commit que
   no se puede explicar en una frase se divide.
7. Pull request con la plantilla de `references/revision-pr.md` rellenada, preview de Vercel
   y captura. Tú revisas con la checklist; solo entonces se mezcla.

## Paso 5.4 · Pista frontend · Osmani

Delegas a `osmani`. Además del ciclo:

- **Astro**: content collections tipadas para todo el contenido de los briefs; un layout por
  plantilla de Frost; islas solo donde hay interacción real, con `client:visible` o
  `client:idle`, nunca `client:load` sin razón; `<Image>` y `<Picture>` de Astro con los
  assets de Bellard; fuentes locales en subconjunto con `font-display: swap` y preload de la
  principal; View Transitions si el diseño lo pide.
- **Next.js**: App Router; Server Components por defecto y `"use client"` solo en hojas
  interactivas; grupos de ruta `(marketing)` y `(app)`; Cache Components con `"use cache"`
  explícito y `cacheLife` en lo cacheable, Suspense en lo dinámico; `loading.tsx` y
  `error.tsx` por segmento; `next/image` y `next/font`. Skills `vercel:nextjs`,
  `react-best-practices`, `composition-patterns`, `vercel:next-cache-components`.
- **Común**: HTML semántico con landmarks, foco visible, `label` en todo campo; la tabla de
  `seo.md` implementada con metadatos, JSON-LD, `sitemap.xml`, `robots.txt`, OG por página,
  canonical y `hreflang`; cabeceras y CSP con `references/headers.md` (nonce en Next.js,
  estática en Astro); redirects de `docs/02-estructura/redirects.md` en `vercel.json` o
  `astro.config`; enlaces externos con `rel="noopener noreferrer"`; nada de HTML sin
  sanitizar; ningún secreto en el cliente.
- **Presupuesto** que CI vigila con `lighthouserc.json`: HTML 50 KB, CSS 60 KB, JS inicial
  150 KB comprimidos, fuentes 80 KB, imágenes sobre el pliegue 200 KB; LCP 2.5 s, INP 200 ms,
  CLS 0.1 en móvil simulado. Si un pull request lo rompe, no se mezcla.
- Imágenes y video: pide a `bellard` las variantes con `/optimize-assets` sobre `assets.md`;
  tú los colocas con `width`, `height`, `sizes`, `loading` y `fetchpriority` correctos.

## Paso 5.5 · Pista backend · Hopper (solo aplicaciones)

Delegas a `hopper`. Con `references/dal.md` como patrón:

- **Capa de acceso a datos** en `src/data/` marcada `import 'server-only'`: la única que lee
  `process.env` y toca la base de datos. Cada función autentica, autoriza por recurso
  (propiedad u organización en la consulta, nunca solo el id) y devuelve un DTO mínimo.
- **Base de datos**: Postgres en Neon (o el del hosting) con Drizzle y migraciones
  versionadas en `drizzle/`. Esquema con dueño por tabla y `on delete` explícito. Nunca
  cambios a mano en producción.
- **Validación**: Zod en toda frontera: `FormData`, `params`, `searchParams`, cabeceras,
  cuerpo de webhooks. Los tipos se borran en tiempo de ejecución; el esquema no.
- **Auth** con proveedor: Clerk, Better Auth o Auth.js según `decision-arquitectura.md`.
  Skill `vercel:auth`. Cookies `HttpOnly`, `Secure`, `SameSite=Lax`. El middleware o `proxy.ts`
  solo redirige; nunca es la barrera. Cada server action y route handler re-verifica.
- **Server actions** delgadas en `src/actions/`: validan con Zod, llaman a la capa de datos,
  devuelven solo lo que la interfaz necesita, `revalidatePath` o `updateTag`. Errores al
  cliente genéricos; el detalle al log.
- **Rate limiting** con `@upstash/ratelimit` o el del hosting en login, registro,
  recuperación, formularios públicos y operaciones caras.
- **Pagos** con Stripe o Mercado Pago vía Checkout; webhooks verificados por firma antes de
  leer el cuerpo; idempotencia por id de evento.
- **Subidas** a Vercel Blob o S3: tipo real, tamaño máximo, renombrado, servidas desde otro
  origen.
- **Logs** sin datos personales. **Backups** automáticos activados en el proveedor.
- **Pruebas** por acción: caso feliz, entrada inválida, usuario sin permiso (IDOR).

## Paso 5.6 · Integración en staging

Contenido real de los briefs cargado en colecciones o CMS; assets de Bellard en su sitio;
redirects respondiendo 301; formularios que llegan a su destino; analítica y banner de
consentimiento funcionando; legales publicados en sus URLs; 404 personalizada. La preview de
`main` es lo que Beizer prueba. Ábrela y recorre los flujos principales de `flujos.md`.

## Paso 5.7 · Definición de terminado

Con `references/definicion-de-terminado.md`. Por tarea: prueba verde, verificado en
navegador, lint y tipos limpios, sin secretos, commit explicable, revisado y mezclado. Por
fase: todas las historias imprescindibles implementadas, presupuesto cumplido en CI,
cabeceras verificadas con `curl -sI`, `pnpm audit` sin altos, `gitleaks detect` limpio,
`docs/05-desarrollo/frontend.md` y `backend.md` escritos con `references/frontend.md` y
`references/backend.md`.

## Paso 5.8 · Puerta de seguridad

Lanza a `schneier` con acceso al repo y la fase 5 de `docs/SEGURIDAD.md` más los puntos de
auditoría de Next.js: base de datos y `process.env` solo en la capa de datos; props de
componentes cliente sin datos privados; cada `"use server"` valida, autoriza, comprueba
propiedad y filtra el retorno; parámetros de ruta validados; `proxy.ts` y `route.ts` revisados
con lupa. Un hallazgo crítico se arregla antes del checkpoint.

## Paso 5.9 · Checkpoint y retro

1. **Checkpoint B**: presenta la URL de staging, el estado de CI, el reporte de Lighthouse
   móvil, cuántas historias imprescindibles e importantes están hechas, el veredicto de
   Schneier y lo que quedó fuera. Pide aprobación explícita.
2. Retro a `<web-lab>/learnings/osmani.md` y `hopper.md`; preferencias de stack o
   herramientas confirmadas a `docs/PREFERENCIAS.md`.
3. Con la aprobación, di qué sigue: fase 6 con Beizer sobre staging.

## Errores que evitas

- Construir desde el wireframe saltándose los tokens y componentes de Frost.
- `"use client"` en todo. `client:load` en todo.
- Auth solo en el middleware. Confiar en tipos en tiempo de ejecución. Devolver el registro completo.
- Secretos con `NEXT_PUBLIC_`. `.env` en el primer commit.
- Desactivar lint o pruebas para que pase el build. Pull requests de dos mil líneas.
- Prueba escrita después del código "para que pase".
- Sin presupuesto hasta que Lighthouse da 40 la semana del lanzamiento.
- Staging con lorem ipsum y fotos sin optimizar.
