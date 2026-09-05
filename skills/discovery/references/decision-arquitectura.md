# Decisión de arquitectura · [nombre del proyecto]

Fecha: [aaaa-mm-dd] · Autor: Cooper · Revisó: Schneier · Estado: propuesta | aprobada

## Decisión

[Sitio de contenido con Astro | Aplicación con Next.js | Híbrido: qué parte en cada uno]

## Por qué

| Criterio | Lo que dijo el usuario | Hacia dónde apunta |
|----------|------------------------|--------------------|
| Las páginas son iguales para todos los visitantes | | |
| Hay usuarios con cuenta que ven cosas distintas | | |
| Datos que cambian en tiempo real | | |
| Pagos, suscripciones, roles | | |
| Contenido generado por visitantes | | |
| Quién edita el contenido y con qué frecuencia | | |

## Componentes

- Framework: [Astro x | Next.js x]
- Estilos: Tailwind v4 con tokens de Frost
- CMS: [ninguno | cuál y por qué]
- Base de datos: [ninguna | Postgres en ...]
- Identidad: [ninguna | Clerk | Auth.js | Supabase Auth]
- Pagos: [ninguno | Stripe | Mercado Pago]
- Hosting: [Vercel | otro que el usuario ya tiene]
- Analítica: [sin cookies: Plausible, Fathom, Vercel Analytics | con consentimiento]
- Correo transaccional: [ninguno | Resend | otro]

## Integraciones externas

| Servicio | Para qué | Datos que cruzan | Dueño de la cuenta |
|----------|----------|------------------|--------------------|
| | | | |

## Alternativas descartadas

- [Alternativa]: [por qué no]

## Consecuencias

- [Qué se vuelve fácil, qué se vuelve difícil, qué hay que vigilar]
