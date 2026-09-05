# Plan de pruebas · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Beizer · Staging: [URL] · Commit: [sha] · Estado: propuesta | aprobado

## Alcance

- Historias imprescindibles e importantes de la spec: [H-01, H-02, ...]
- Flujos de `docs/02-estructura/flujos.md`: [T1, T2, ...]
- Plantillas: [home, interior, listado, detalle, formulario, legal, cuenta]
- Fuera de alcance esta ronda: [ ] (y por qué)

## Severidades y criterios de salida

Se fijan aquí, antes de encontrar nada. Ver `salida.md`. Bloqueante y crítico bloquean el
lanzamiento; mayor se arregla o lo acepta el usuario por escrito; menor y trivial van al backlog.

## Matriz de navegadores y dispositivos

| Entorno | Versión | Quién | Cómo |
|---------|---------|-------|------|
| Chromium, Firefox, WebKit escritorio | últimas | Playwright | CI |
| Chromium 375 × 812 | última | Playwright | CI |
| iPhone [modelo] · iOS Safari | | [usuario] | manual, guion |
| Android [modelo] · Chrome | | [usuario] | manual, guion |
| Safari Mac, Edge | últimas | Beizer | manual |
| Lector de pantalla | VoiceOver Mac / iPhone | [quién] | guion en accesibilidad.md |

## Áreas y responsables

| Área | Qué | Herramienta | Quién | Salida |
|------|-----|-------------|-------|--------|
| Rastreo | enlaces, códigos, 404, redirects, metadatos, cabeceras, rutas sensibles | crawl_check.py | Beizer | rastreo.md |
| Funcional | criterios de aceptación, casos límite, formularios, analítica | Playwright + manual | Beizer | tests/e2e, reporte |
| Accesibilidad | axe por plantilla y estado; manual teclado y lector | axe.fixture.ts + guion | Beizer + [quién] | accesibilidad.md |
| Rendimiento | Lighthouse móvil ×3 vs presupuesto; campo si hay | Lighthouse, CrUX | Beizer | reporte |
| Seguridad | audit, gitleaks, ZAP baseline, IDOR, rate limit, formularios | guion seguridad.md | Beizer → Schneier | seguridad.md |
| Visual y dispositivos | capturas base 375/768/1280; recorrido en móviles reales | Playwright, manual | Beizer + [usuario] | tests/visual |

## Datos de prueba

- Usuarios de prueba (dos, para IDOR): [ ] · nunca cuentas reales
- Correo de prueba para formularios: [ ]
- Tarjetas de prueba del proveedor de pagos: [ ]

## Calendario

| Día | Qué |
|-----|-----|
| 1 | rastreo, axe, Lighthouse, escaneos |
| 2-3 | funcional y Playwright |
| 3 | manual: lector de pantalla y móviles |
| 4 | reporte, triaje, re-prueba |
| 5 | salida y puerta de Schneier |
