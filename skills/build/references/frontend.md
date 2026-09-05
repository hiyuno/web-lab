# Frontend · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Osmani · Framework: Astro 5 | Next.js 16 · Hosting: Vercel

## Cómo correrlo

```bash
pnpm install
cp .env.example .env.local   # pide los valores al dueño del proyecto; nunca los pegues en el chat
pnpm dev
pnpm test && pnpm test:e2e
```

## Decisiones

| Qué | Decisión | Por qué | Alternativa descartada |
|-----|----------|---------|------------------------|
| Framework | | decision-arquitectura.md | |
| Estilos | Tailwind v4 + tokens.css | | |
| Componentes base | shadcn/ui / Astro | | |
| Fuentes | locales, subconjunto, swap | | |
| Analítica | | sin cookies / con consentimiento | |

## Presupuesto de rendimiento (móvil)

| Métrica | Objetivo | Staging | Fecha |
|---------|----------|---------|-------|
| LCP | ≤ 2.5 s | | |
| INP | ≤ 200 ms | | |
| CLS | ≤ 0.1 | | |
| JS inicial | ≤ 150 KB gz | | |
| Lighthouse rendimiento | ≥ 90 | | |

## Cabeceras

Verificado con `curl -sI` el [fecha]: [pegar resultado].

## Mapa de componentes

| Componente (Frost) | Archivo | Estados implementados | Pruebas |
|--------------------|---------|-----------------------|---------|
| | | 9/9 | |

## Mapa de plantillas

| Plantilla | Layout / ruta | Páginas | Estado |
|-----------|---------------|---------|--------|
| | | | |

## Deuda y pendientes

| Qué | Por qué se pospuso | Cuándo |
|-----|--------------------|--------|
| | | |
