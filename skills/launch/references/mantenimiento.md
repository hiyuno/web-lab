# Plan de mantenimiento · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Allspaw · Dueño del plan: [nombre] · Revisión del plan: cada 6 meses

## Calendario

| Frecuencia | Tarea | Cómo | Dueño | Última | Próxima |
|------------|-------|------|-------|--------|---------|
| Continuo | Dependencias | Dependabot (Renovate si monorepo): grupo semanal, parches de seguridad el mismo día; CI decide | | | |
| Continuo | Alertas | responder según incidentes.md | | | |
| Mensual | Salud del sitio | `domain_check.py` + `launch_check.py` contra producción | | | |
| Mensual | Core Web Vitals de campo | Speed Insights / CrUX vs presupuesto | | | |
| Mensual | Indexación | Search Console: cobertura, 404, mejoras | | | |
| Mensual | Formularios y correo | envío de prueba; llega y no a spam | | | |
| Mensual | Backups | verificar que corren; restauración de prueba cada 6 meses | | | |
| Mensual | Expiraciones | dominio > 60 días, certificado > 14 días | | | |
| Trimestral | Rotación de secretos | los rotables (API keys, tokens); con Schneier | | | |
| Trimestral | Revisión de accesos | registrador, DNS, hosting, repo, analítica, pagos; quitar lo que no hace falta | | | |
| Trimestral | Contenido | legales vigentes, precios, testimonios, fechas | | | |
| Semestral | Runbook de incidentes | releer; probar un escenario | | | |
| Anual | Modelo de amenazas | contra lo que el sitio es hoy; con Schneier | | | |
| Anual | SEGURIDAD.md completa | | | | |
| Anual | Siguiente ciclo | historias pospuestas → `/discovery` | | | |

## Reglas

- Una versión mayor de framework es una tarea planificada con rama, pruebas y preview; nunca automerge.
- Salidas de personas: accesos revocados el mismo día.
- Un incidente siempre termina en post-mortem (≤ 72 h) y en un cambio al runbook.
- Lo que se aprende y aplica a otros proyectos va a `<web-lab>/learnings/allspaw.md`.

## Costos recurrentes

| Servicio | Costo | Renovación | Tarjeta vence | Cuenta a nombre de |
|----------|-------|------------|---------------|--------------------|
| Dominio | | | | |
| Hosting | | | | |
| Base de datos | | | | |
| Correo | | | | |
| Monitoreo | | | | |

## Historial

| Fecha | Qué se hizo | Quién |
|-------|-------------|-------|
| | | |
