# Componente · [Nombre] · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Frost · Base: [shadcn/ui Button | Astro component | propio] · Estado: borrador | listo

## Para qué sirve y cuándo no

- Uso: [ ]
- No usar para: [ ] (y qué usar en su lugar)
- Aparece en: [plantillas y bloques de wireframe]

## Anatomía

```
┌───────────────────────────────┐
│ [icono?] Etiqueta   [icono?]  │
└───────────────────────────────┘
```

| Parte | Obligatoria | Token |
|-------|-------------|-------|
| Contenedor | sí | radius: semantic.radius.control; altura: component.button.height |
| Etiqueta | sí | text.sm, font.sans, tracking.normal |
| Icono | no | 16 px, hereda color |

## Variantes y tamaños

| Variante | Fondo | Texto | Borde | Cuándo |
|----------|-------|-------|-------|--------|
| primary | primary | primary-foreground | ninguno | una por pantalla |
| secondary | muted | foreground | border | |
| ghost | transparente | foreground | ninguno | |
| danger | danger | white | ninguno | acciones destructivas, con confirmación |

| Tamaño | Altura | Padding | Texto |
|--------|--------|---------|-------|
| sm | spacing.8 | spacing.3 | text.sm |
| md | spacing.10 | spacing.4 | text.sm |
| lg | spacing.12 | spacing.6 | text.base |

## Estados (todos obligatorios)

| Estado | Cambio visual | Token | Nota |
|--------|---------------|-------|------|
| default | | | |
| hover | | | solo con puntero; nunca revela contenido nuevo |
| focus-visible | anillo 2 px `ring`, offset 2 px | ring | nunca se elimina; 3:1 contra el fondo |
| active | | | |
| disabled | opacidad y cursor | muted-foreground | sigue siendo legible; explica por qué si es posible |
| loading | spinner reemplaza icono, etiqueta se mantiene | | ancho no cambia |
| error | | danger | mensaje junto al componente, no solo color |
| empty | | | qué se muestra cuando no hay datos |
| selected / checked | | | |

## Contenido

- Texto mínimo y máximo probados: [ ] ("Aceptar" y "Descargar el reporte completo de 2026")
- Truncado o salto de línea: [ ]
- Iconos permitidos: [set]

## Responsive

| Ancho | Cambio |
|-------|--------|
| 375 | [ancho completo si está solo en formulario] |
| 768 | |
| 1280 | |

## Accesibilidad

- Rol y elemento nativo: [`<button>`; nunca `<div>` con onClick]
- Nombre accesible: [texto visible; `aria-label` solo en icono solo]
- Teclado: [Enter y Espacio activan; Tab llega; Escape cierra si aplica]
- Objetivo táctil: ≥ 24 × 24 px (WCAG 2.2) · recomendado 44 en móvil
- Lector de pantalla anuncia: [ ]
- Movimiento: [transición duration.ui / ease.ui; sin animación bajo reduced-motion]

## Seguridad y confianza (si aplica)

- Acción destructiva: confirmación explícita, nunca junto a acciones frecuentes
- En login: `autocomplete` correcto, sin bloquear pegar, sin ocultar campo de contraseña sin opción de ver

## Implementación (para Osmani)

- Props: [variant, size, loading, disabled, asChild]
- Clases Tailwind de referencia: [ ]
