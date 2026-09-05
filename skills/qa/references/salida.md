# Criterios de salida · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Beizer · Se fijan en el plan, antes de probar.

## Para cerrar la fase 6

- [ ] Cero hallazgos bloqueantes y críticos abiertos
- [ ] Mayores: arreglados y re-probados, o aceptados por el usuario por escrito en `reporte.md`
- [ ] Todos los criterios de aceptación de historias imprescindibles cubiertos por una prueba que pasa
- [ ] Playwright verde en Chromium, Firefox y WebKit, escritorio y 375
- [ ] Rastreo: sin enlaces rotos, 404 con código 404, redirects 301 sin cadenas, robots y sitemap correctos
- [ ] Formularios: envío confirmado en destino y correo recibido
- [ ] Analítica: carga una vez, conversiones disparan una vez, respeta consentimiento
- [ ] Accesibilidad: axe sin violaciones en todas las plantillas y modos; recorrido manual con teclado y lector hecho y sin críticos
- [ ] Rendimiento: Lighthouse móvil ≥ 90; LCP ≤ 2.5 s, CLS ≤ 0.1, TBT ≤ 200 ms en home y conversión; JS inicial ≤ 150 KB
- [ ] Seguridad: audit sin altos, gitleaks limpio, cabeceras completas, ZAP sin altas, pruebas de auth sin fallos
- [ ] Capturas de línea base guardadas para regresión visual
- [ ] Cada bug encontrado a mano tiene su prueba automatizada
- [ ] Veredicto de Schneier: aprobado o con condiciones escritas
- [ ] Checkpoint del usuario aprobado

## Aceptaciones de riesgo

| Hallazgo | Severidad | Razón para lanzar así | Quién acepta | Fecha | Cuándo se arregla |
|----------|-----------|----------------------|--------------|-------|-------------------|
| | | | | | |

## Firma

Beizer: [fecha] · Schneier: [veredicto, fecha] · Usuario: [aprobado, fecha]
