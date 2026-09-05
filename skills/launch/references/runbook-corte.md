# Runbook del día de corte · [proyecto]

Fecha del corte: [aaaa-mm-dd hh:mm] · Ventana: [ ] · Quién ejecuta: [ ] · Quién vigila: [ ] · Canal: [ ]

Plazos de decisión (no se debaten durante el corte): rollback web/DNS hasta [hh:mm, +2 h] · rollback correo hasta [+24 h].

## Antes de empezar (T-30 min)
- [ ] Checklist firmado; Schneier ha aprobado
- [ ] Todos en el canal; nadie más desplegando
- [ ] Preview de producción abierta y verificada
- [ ] Snapshot DNS a mano; comandos de rollback copiados abajo

## Pasos

| # | Paso | Quién | Comando / acción | Verificación | Rollback de este paso |
|---|------|-------|------------------|--------------|-----------------------|
| 1 | Promover despliegue a producción | | `vercel promote <url>` o botón Promote | `curl -sI https://<preview-prod>` 200 | Instant Rollback |
| 2 | Añadir/apuntar dominio | | A @ → 76.76.21.21 · CNAME www → cname.vercel-dns.com | `dig +short ejemplo.mx` · `dig +short www.ejemplo.mx` | restaurar A/CNAME del snapshot |
| 3 | Certificado emitido | | esperar en Vercel → Domains | `curl -sI https://ejemplo.mx` sin error TLS | — |
| 4 | Verificación 60 min automática | | `python3 launch_check.py https://ejemplo.mx --redirects ... --seo ... --old-urls ...` | sin críticos de acceso ni continuidad | ver decisión |
| 5 | Manual: formulario, login, analítica | | | correo recibido; evento en tiempo real | — |
| 6 | Sitemap a Search Console y Bing; indexar home | | | "Sitemap enviado correctamente" | — |
| 7 | Correo (si cambia MX) | | MX → nuevo proveedor | `dig MX ejemplo.mx @8.8.8.8` y @1.1.1.1 coinciden | restaurar MX del snapshot |
| 8 | Anotación de lanzamiento en analítica; aviso a interesados | | | | — |

## Vigilancia (T+0 a T+60)
- [ ] Sentry: cero errores nuevos · [ ] Disponibilidad: sin alertas · [ ] Tráfico llegando · [ ] 404 en logs: revisar patrones

## Decisión a T+60
[ ] Seguir · [ ] Rollback (razón: ) · Firmado por: [ ]

## Rollback

Web (Vercel): Dashboard → Instant Rollback → despliegue anterior → Confirmar. Recuerda: no revierte variables ni base de datos; después, `vercel promote <deployment>` para volver a la normalidad.

DNS: restaurar del snapshot `dns-snapshot-[fecha].json`. Propaga en ≤ TTL actual ([ ] s).

Correo: restaurar MX del snapshot; reactivar reenvíos antiguos si los había.

## Después
- [ ] Subir TTL de vuelta a [3600] cuando todo está estable (T+24 h como mínimo)
- [ ] Inicio del seguimiento de 30 días (`monitoreo.md`)
