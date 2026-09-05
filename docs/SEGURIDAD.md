# Checklist de seguridad por fase

Lista mínima que **Schneier** revisa al cierre de cada fase y que todos los roles aplican en su
trabajo. Referencias de fondo: OWASP Top 10, OWASP API Security Top 10, OWASP ASVS nivel 1
(nivel 2 si hay datos sensibles). Un hallazgo crítico bloquea el paso de fase; uno alto
bloquea el lanzamiento.

## Reglas que aplican siempre

- [ ] Autenticación, hash de contraseñas y datos de tarjeta solo con proveedores establecidos.
- [ ] Ningún secreto en el repo, en el cliente, en logs ni en el chat. Si aparece uno, se rota ese día.
- [ ] Autorización en el servidor, por recurso, en cada consulta.
- [ ] Pruebas de seguridad solo contra entornos propios del usuario.
- [ ] Cuentas de hosting, DNS, registrador, repositorio y analítica con segundo factor.
- [ ] Decisiones de aceptar un riesgo quedan escritas con fecha y razón en `docs/SEGURIDAD-decisiones.md` del proyecto.

## Fase 1 · Descubrimiento

- [ ] Modelo de amenazas escrito: activos, datos y clasificación (públicos, internos, personales, sensibles), actores, impacto, obligaciones legales (LFPDPPP, GDPR).
- [ ] La spec dice qué proveedor de identidad y de pagos se usa, si aplica.
- [ ] Retención y borrado de datos personales definidos.
- [ ] Nivel ASVS objetivo decidido según la clasificación de datos.

## Fases 2 y 3 · Estructura y contenido

- [ ] Formularios con el mínimo de campos; cada campo tiene una razón escrita.
- [ ] Sin datos personales en URLs ni parámetros.
- [ ] Aviso de privacidad, términos, y gestión de consentimiento si hay cookies no esenciales.
- [ ] Superficies de contenido de usuarios identificadas.
- [ ] Mensajes de error de login y recuperación definidos como genéricos.

## Fase 4 · Diseño

- [ ] Login en página propia con `autocomplete` correcto y soporte para segundo factor.
- [ ] Acciones destructivas con confirmación y separadas de las frecuentes.
- [ ] Consentimiento sin patrones oscuros: rechazar tan visible como aceptar.
- [ ] Estado de sesión visible en pantallas autenticadas.
- [ ] Componentes que muestran contenido de usuarios marcados para escape obligatorio.

## Fase 5 · Desarrollo

Frontend:

- [ ] CSP sin `unsafe-inline` ni `unsafe-eval`; terceros en lista blanca.
- [ ] Cabeceras: HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, `frame-ancestors`.
- [ ] Ningún secreto llega al cliente; `NEXT_PUBLIC_` solo para valores públicos.
- [ ] Sin HTML sin sanitizar; DOMPurify o equivalente donde haga falta.
- [ ] Validación de formularios repetida en el servidor.
- [ ] `rel="noopener noreferrer"` en enlaces externos; recursos de CDN con `integrity` o servidos localmente.
- [ ] Lockfile versionado; `npm audit --audit-level=high` limpio.

Backend, solo aplicaciones:

- [ ] Toda entrada validada con esquema en la frontera.
- [ ] Autorización por recurso en cada consulta; probado con el id de otro usuario.
- [ ] Consultas parametrizadas; nunca concatenación de entrada en SQL, comandos ni rutas.
- [ ] Cookies `HttpOnly`, `Secure`, `SameSite`; sesiones invalidadas al cambiar contraseña.
- [ ] Rate limiting en login, registro, recuperación, formularios públicos y endpoints caros.
- [ ] CSRF cubierto en toda mutación.
- [ ] Subidas: tipo real, tamaño máximo, renombrado, almacenamiento y origen separados.
- [ ] Webhooks verificados por firma.
- [ ] Logs sin datos personales; errores al usuario genéricos.
- [ ] Cifrado en reposo; campos sensibles cifrados en aplicación si el modelo lo pide.
- [ ] Exportar y borrar datos de un usuario es posible.
- [ ] `.env` en `.gitignore` desde el primer commit; `.env.example` con nombres.

## Fase 6 · QA

- [ ] `npm audit` u `osv-scanner` sin altos ni críticos sin plan.
- [ ] `gitleaks detect` sobre todo el historial, limpio.
- [ ] Cabeceras verificadas con `curl -sI` en staging.
- [ ] Solo HTTPS, redirección desde HTTP, sin contenido mixto.
- [ ] Si hay auth: IDOR, sesión expirada, límite de intentos, mensajes genéricos probados.
- [ ] Formularios probados con HTML, comillas, tamaño máximo y extensiones falsas.
- [ ] Si hay API: OWASP ZAP baseline contra staging.
- [ ] `.env`, `.git`, mapas de fuentes, backups y paneles no son públicos.

## Fase 7 · Lanzamiento

- [ ] Registrador con 2FA, bloqueo de transferencia y renovación automática.
- [ ] DNS con registro CAA; DNSSEC si está disponible.
- [ ] SPF, DKIM y DMARC con `quarantine` o `reject`, aunque el sitio no envíe correo.
- [ ] HTTPS forzado; HSTS con `max-age` largo e `includeSubDomains`.
- [ ] Variables de producción con mínimo privilegio; tokens de despliegue con expiración.
- [ ] Backups automáticos con una restauración probada.
- [ ] Monitoreo de disponibilidad, errores y Core Web Vitals con alertas a una persona.
- [ ] Analítica sin cookies o con consentimiento previo real.
- [ ] Runbook de incidentes escrito: caída, filtración, dominio expirado.
- [ ] Firma de Schneier para el go-live.

## Fase 8 · Mantenimiento

- [ ] Dependabot o Renovate activo; parches de seguridad en la semana.
- [ ] Rotación de secretos y revisión de accesos cada trimestre.
- [ ] Post-mortem sin culpa tras cada incidente.
- [ ] Revisión anual del modelo de amenazas o al cambiar el alcance.
