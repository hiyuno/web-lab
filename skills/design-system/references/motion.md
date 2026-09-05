# Movimiento · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Frost · Tokens: duration.*, ease.* · Referencia: skills apple-design, emil-design-eng

## Principios

- El movimiento explica un cambio de estado o de lugar. Si no explica nada, no se anima.
- Interrumpible: el usuario puede cambiar de idea a mitad de camino.
- Rápido: 150 a 300 ms para interfaz; resortes solo para gestos y elementos que se arrastran.
- Nada esencial depende del movimiento. Bajo `prefers-reduced-motion: reduce`, transiciones a 0 ms o fundidos de opacidad.

## Qué se anima

| Elemento | Propiedad | Duración | Curva | Reduced motion |
|----------|-----------|----------|-------|----------------|
| Hover de botón | color de fondo | duration.fast | ease.out | igual (no es movimiento) |
| Aparición de menú / popover | opacity + translateY 4 px | duration.normal | ease.out | solo opacity |
| Hoja o modal | translateY / scale 0.98 → 1 | duration.slow | ease.spring | solo opacity |
| Cambio de página | opacity | duration.page | ease.in-out | ninguno |
| Acordeón | height (grid-template-rows) | duration.normal | ease.out | instantáneo |
| Toast | translateY + opacity | duration.normal | ease.out | solo opacity |
| Esqueletos de carga | pulso de opacidad | 1.5 s loop | linear | estático |

## Qué no se anima

- Texto mientras se lee. Layout que empuja contenido (causa CLS).
- Nada en bucle infinito salvo indicadores de carga.
- Parallax y efectos al hacer scroll salvo decisión explícita del usuario.

## Gestos (solo aplicaciones)

| Gesto | Dónde | Física | Cancelación |
|-------|-------|--------|-------------|
| Arrastrar hoja para cerrar | hoja móvil | resorte ease.spring | vuelve si < 40 % |
| Alternativa de un clic (WCAG 2.5.7) | botón cerrar visible | | |

## Implementación (para Osmani)

- CSS `transition` con tokens; View Transitions para cambio de página (skill `react-view-transitions` en Next.js).
- `@media (prefers-reduced-motion: reduce)` global que reduce duraciones a 0.01 ms salvo opacidad.
