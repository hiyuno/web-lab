# Monitoreo y alertas · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Allspaw · Alertas llegan a: [nombre] por [canal] · Respaldo: [nombre]

Principio: pocas alertas, todas accionables. Alerta cuando la experiencia del usuario está
comprometida, no en cada parpadeo.

## Qué se vigila

| Señal | Herramienta | Regla de alerta | A quién | Revisión |
|-------|-------------|-----------------|---------|----------|
| Disponibilidad | [Sentry Uptime / OnlineOrNot / UptimeRobot] | 3 fallos seguidos desde ≥ 2 regiones | | inmediata |
| Errores de aplicación | Sentry | nuevo tipo de error; > [n] eventos en 10 min | | inmediata |
| Core Web Vitals de campo | Vercel Speed Insights | LCP p75 > 2.5 s o INP p75 > 200 ms 7 días | | semanal |
| Certificado | monitor de dominio | expira en < 14 días | | inmediata |
| Dominio | registrador + monitor | expira en < 60 días; cambio en NS/MX/TXT/CAA | | inmediata |
| Indexación | Search Console | caída de cobertura; errores de rastreo nuevos | | diaria 14 días, luego semanal |
| 404 | logs del hosting / Search Console | patrón nuevo con > [n] hits | | diaria 14 días |
| Formularios | prueba mensual | correo no llega | | mensual |
| Backups | proveedor | fallo de backup | | inmediata |
| Presupuesto de hosting | Vercel | > [ ]% del plan | | semanal |

## Sentry

- DSN en variables de entorno; `sendDefaultPii: false`; `beforeSend` que quita correo, IP y nombre.
- Release por commit; source maps subidos en CI, no públicos.
- Alertas: nuevo issue → [canal]; regresión → [canal]; pico → [canal].

## Analítica

- Herramienta: [Plausible / Fathom / Vercel Analytics / GA4 con consentimiento]
- Anotación "Lanzamiento [fecha]" · Objetivos: [conversiones de la spec]

## Línea base (antes del corte, si había sitio)

| Métrica | Valor | Fuente | Fecha |
|---------|-------|--------|-------|
| Sesiones orgánicas / mes | | | |
| Páginas de aterrizaje top 10 | | | |
| Posiciones de keywords principales | | | |
| Core Web Vitals de campo | | | |

## Seguimiento de 30 días

| Día | Disponibilidad | Errores nuevos | Cobertura GSC | 404 nuevos | CWV campo | Notas |
|-----|----------------|----------------|---------------|------------|-----------|-------|
| 1 | | | | | | |
| 2 | | | | | | |
| ... | | | | | | |
| 28 | | | | | comparar con laboratorio | |
| 30 | | | | | | checkpoint de cierre |
