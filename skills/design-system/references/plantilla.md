# Plantilla · [nombre] · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Frost · Wireframe: docs/02-estructura/wireframes/[nombre].md · Páginas: [ ]

Texto real de los briefs de `docs/03-contenido/briefs/`. Tres anchos: 375, 768, 1280.

## Retícula

| Ancho | Columnas | Margen | Gutter | Ancho máximo del contenido |
|-------|----------|--------|--------|----------------------------|
| 375 | 4 | spacing.4 | spacing.4 | — |
| 768 | 8 | spacing.6 | spacing.6 | — |
| 1280 | 12 | auto | spacing.8 | 72rem |

## Bloques

| # | Bloque del wireframe | Componentes | Texto (brief) | 375 | 768 | 1280 |
|---|----------------------|-------------|---------------|-----|-----|------|
| 1 | Cabecera | Header, Nav, Button | | menú en hoja | menú visible | menú visible |
| 2 | Hero | Heading, Text, Button, Image | | apilado, imagen debajo | | imagen a la derecha 5/12 |

## Estados de página

| Estado | Qué se ve | Componentes |
|--------|-----------|-------------|
| Cargando | esqueleto de los bloques 1 a 3, sin saltos de layout (CLS) | Skeleton |
| Vacío | mensaje que orienta + acción | EmptyState |
| Error | qué pasó y qué hacer; genérico si es login | Alert |
| Éxito | confirmación y siguiente paso | Alert, Button |

## Imágenes

| Bloque | Asset (assets.md) | Proporción | Tamaño en pantalla 1280 | Prioridad de carga |
|--------|-------------------|------------|-------------------------|--------------------|
| Hero | #1 | 16:9 | 560 × 315 | alta (LCP) |

## Jerarquía tipográfica

| Elemento | Token | Ancho 375 | Ancho 1280 |
|----------|-------|-----------|------------|
| H1 | text.4xl → text.6xl, leading.tight | 2.25rem | 3.75rem |
| H2 | text.2xl → text.4xl | | |
| Cuerpo | text.base, leading.relaxed | | |

## Notas

- Orden de foco: [ ]
- Punto de anclaje para "saltar al contenido": [ ]
- Qué anima al entrar (motion.md): [ ]
