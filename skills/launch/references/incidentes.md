# Runbook de incidentes · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Allspaw · Revisar tras cada incidente y al menos cada 6 meses.

Un runbook corto que existe vale más que uno largo que no. Primero qué ves y qué haces; la
explicación después. Nunca "quién".

## Severidades

| Nivel | Qué significa | Responde | En | Comunica a usuarios |
|-------|---------------|----------|----|---------------------|
| SEV1 | sitio caído, pagos rotos, filtración de datos | [nombre] · respaldo [nombre] | 15 min | sí, en 30 min |
| SEV2 | función principal rota (login, formulario, checkout) | [nombre] | 1 h | si dura > 1 h |
| SEV3 | degradación con rodeo; lentitud; error en página secundaria | [nombre] | 1 día laboral | no |
| SEV4 | cosmético, texto | backlog | siguiente ciclo | no |

## Primeros 10 minutos, siempre

1. Confirma: ¿es el sitio o soy yo? Monitor externo + `curl -sI https://<dominio>` + otro dispositivo.
2. Declara severidad y avisa en [canal]: "SEV[n]: [qué falla] desde [hora]. Investigando."
3. Mira en orden: estado de Vercel (vercel-status.com) → último despliegue → Sentry → DNS (`dig`) → certificado → terceros.
4. Si el último despliegue coincide con el inicio: **Instant Rollback** primero, investigar después.
5. Anota la línea de tiempo desde el minuto uno; el post-mortem la necesita.

## Escenarios

### A · Sitio caído (SEV1)
- Vercel status → si es plataforma, comunicar y esperar; no tocar nada.
- Último despliegue → Instant Rollback. Verificar. Recordar deshacer el rollback después.
- DNS: `dig +short <dominio>` devuelve lo esperado? Si no, restaurar snapshot.
- Certificado: `curl -vI https://<dominio> 2>&1 | grep -i expire`. Si expiró, renovar en el hosting.
- Comunicar: banner o red social: "Estamos teniendo problemas; trabajando en ello."

### B · Filtración o sospecha de acceso no autorizado (SEV1)
- No borrar nada: preservar logs y evidencias.
- Contener: rotar TODOS los secretos (hosting, BD, proveedores), cerrar sesiones, revocar tokens, cambiar contraseñas de cuentas críticas.
- Llamar a Schneier: alcance, datos afectados, causa.
- Obligaciones: LFPDPPP exige informar a los titulares sin dilación cuando afecta sus derechos; GDPR 72 h a la autoridad si aplica. Redactar el aviso con hechos, qué se hizo y qué hacer.
- Post-mortem obligatorio.

### C · Dominio o certificado expirado (SEV1)
- Registrador: renovar hoy; puede tardar horas en volver. Activar renovación automática.
- Certificado: Vercel renueva solo; si falló, revisar CAA y DNS y forzar renovación.
- Después: alertas de expiración a 60 y 14 días (monitoreo.md).

### D · Tercero caído: pagos, auth, CMS, correo (SEV1 o SEV2)
- Confirmar en el status del proveedor.
- Degradar con gracia: mensaje claro al usuario ("los pagos no están disponibles, intenta en una hora"), sin errores 500.
- No intentar arreglar lo del proveedor. Comunicar y esperar. Anotar duración para el post-mortem.

### E · Pico de tráfico o ataque (SEV2)
- Vercel: revisar Firewall y activar Attack Challenge Mode si es ataque (skill `vercel:vercel-firewall`).
- Rate limiting en formularios y login ya debería existir; verificar que actúa.
- Costos: revisar límites del plan.

### F · Contenido incorrecto publicado (SEV2 o SEV3)
- Instant Rollback si vino en el último despliegue; si es CMS, revertir la entrada.
- Verificar caché: purgar si aplica.

## Comunicación

| Momento | Dónde | Qué |
|---------|-------|-----|
| Al declarar | [canal interno] | SEV, qué, desde cuándo, quién lleva |
| 30 min (SEV1) | usuarios: banner / red social / correo | qué pasa, qué no está afectado, cuándo hay próxima actualización |
| Cada hora | ambos | avance |
| Resolución | ambos | qué pasó en una frase, qué se hizo, post-mortem en 72 h |

## Contactos

| Quién | Rol | Cómo | Horario |
|-------|-----|------|---------|
| | dueño | | |
| | responde SEV1 | | |
| | Schneier / seguridad | | |
| | registrador soporte | | |
| | hosting soporte | | |
