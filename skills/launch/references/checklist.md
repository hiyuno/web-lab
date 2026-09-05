# Checklist de lanzamiento · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Allspaw · Cada punto con fecha y quién verificó. Firmas al final.

## Entrada
- [ ] `docs/06-qa/salida.md` firmado por Beizer y Schneier, sin bloqueantes ni críticos · [fecha, quién]

## Cuentas y dominio (7.1)
- [ ] Registrador con 2FA, bloqueo, renovación automática, a nombre del dueño
- [ ] Accesos individuales y mínimos en registrador, DNS, hosting, repo, analítica, pagos
- [ ] CAA publicado · DNSSEC activado o anotado
- [ ] Snapshot DNS guardado

## Correo (7.2)
- [ ] SPF único, -all, ≤ 10 consultas
- [ ] DKIM por cada fuente
- [ ] DMARC publicado con política [ ] y rua

## Producción (7.3)
- [ ] Producción solo desde main; protección de rama
- [ ] Variables de producción cargadas; sensibles separadas de preview; tokens con expiración
- [ ] Dominio en el proyecto; certificado emitido
- [ ] HTTPS forzado; HSTS
- [ ] Redirects cargados y probados uno a uno contra la URL de producción

## Observabilidad (7.4)
- [ ] Disponibilidad multi-región, alerta tras 3 fallos
- [ ] Errores (Sentry) sin datos personales; alertas configuradas
- [ ] Core Web Vitals de campo
- [ ] Vigilancia de dominio: NS, MX, TXT, CAA, expiraciones
- [ ] Alertas llegan a [nombre] por [canal]; probadas con una alerta de prueba
- [ ] Analítica con consentimiento correcto; anotación de lanzamiento preparada
- [ ] Línea base exportada (posiciones, páginas de aterrizaje) si hay sitio previo

## Backups y rollback (7.5)
- [ ] Backups automáticos; retención [ ] días
- [ ] Restauración probada el [fecha] en [entorno]
- [ ] Instant Rollback probado; advertencias (env, BD, auto-assign) en el runbook
- [ ] Rollback de DNS: snapshot + tiempo con TTL actual

## Corte (7.6)
- [ ] TTL bajado a 300 s el [fecha] (24-72 h antes) y confirmado con dig
- [ ] Ventana: [día y hora], entre semana, temprano
- [ ] Plazos de rollback: web/DNS 2 h · correo 24 h
- [ ] `runbook-corte.md` completo con quién hace cada paso
- [ ] Veredicto de Schneier: [aprobado | con condiciones] · [fecha]

## Firmas
Allspaw: [fecha] · Schneier: [fecha] · Usuario (go-live autorizado): [fecha]
