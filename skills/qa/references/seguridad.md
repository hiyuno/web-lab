# Pruebas de seguridad en staging · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Beizer · Lo interpreta: Schneier · Staging: [URL]

**Solo contra staging del propio usuario. Nunca producción. Nunca sitios ajenos.** Avisa al
usuario antes del escaneo activo; puede generar correos y registros de prueba.

## 1. Dependencias y secretos

```bash
pnpm audit --audit-level=high
gitleaks detect --source . --log-opts="--all" --redact
```

| Prueba | Resultado | Severidad si falla |
|--------|-----------|--------------------|
| audit altos/críticos | | crítico si llega a producción; mayor si es solo dev |
| gitleaks | | bloqueante; rotar el secreto hoy aunque esté borrado |

## 2. Transporte y cabeceras (del rastreo)

```bash
curl -sI https://<staging> | grep -iE "strict-transport|content-security|x-content-type|referrer|permissions|x-frame"
curl -sI http://<staging> | head -3   # espera 301/308 a https
```

- [ ] HSTS · CSP sin `unsafe-inline` en script-src · nosniff · Referrer-Policy · Permissions-Policy · frame-ancestors
- [ ] Certificado válido; sin contenido mixto (consola del navegador)

## 3. OWASP ZAP

Baseline (pasivo, seguro, ~5 minutos):

```bash
docker run --rm -v "$PWD/docs/06-qa:/zap/wrk:rw" -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t https://<staging> -r zap-baseline.html -J zap-baseline.json -I
```

Activo autenticado (solo aplicaciones, con usuario de prueba, avisando al usuario):

```bash
docker run --rm -v "$PWD/docs/06-qa:/zap/wrk:rw" -t ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py -t https://<staging> -r zap-full.html -J zap-full.json -I -j
```

Falsos positivos conocidos se listan en `zap-rules.tsv` con razón. Alertas altas = crítico;
medias = mayor salvo justificación.

| Alerta | Nivel ZAP | URL | Real / falso positivo | Severidad | Arreglo |
|--------|-----------|-----|-----------------------|-----------|---------|
| | | | | | |

## 4. Autenticación y autorización (si hay cuenta)

Con dos usuarios de prueba A y B:

| Prueba | Cómo | Esperado | Resultado |
|--------|------|----------|-----------|
| IDOR lectura | con sesión A, abrir URL de un recurso de B | 404 o 403, mismo mensaje que inexistente | |
| IDOR escritura | con sesión A, enviar la acción de editar/borrar con id de B | rechazado, nada cambia | |
| Sesión expirada | borrar cookie de sesión y repetir acción | redirige a login, sin error 500 | |
| Rate limit login | 20 intentos fallidos seguidos | bloqueo o retraso antes del 20 | |
| Enumeración | login y recuperación con correo inexistente | mismo mensaje que con existente | |
| Redirección abierta | `?returnTo=https://evil.example` tras login | ignora o solo rutas relativas | |
| Cookies | inspeccionar en DevTools | HttpOnly, Secure, SameSite | |
| Cierre de sesión | volver atrás tras salir | no se ve contenido privado | |

## 5. Entradas

| Prueba | Campos | Esperado | Resultado |
|--------|--------|----------|-----------|
| HTML y comillas `<b>x</b>"'` | todos los de texto | se escapa; no se ejecuta ni rompe | |
| Muy largo (10 000 caracteres) | texto y textarea | rechazo con mensaje; sin 500 | |
| Archivo con extensión falsa (`.png` que es `.html`) | subidas | rechazado por tipo real | |
| Archivo muy grande | subidas | rechazado por tamaño | |
| Parámetros de URL manipulados (`?page=-1`, `?id=abc`) | listados y detalles | 400/404, sin 500 ni stack trace | |

## 6. Exposición

- [ ] `/.env`, `/.git/HEAD`, mapas de fuentes, backups, `/api/*` sin auth: del rastreo, todos bloqueados
- [ ] Mensajes de error al usuario sin stack traces ni rutas internas
- [ ] Respuestas de API sin campos de más (revisar un JSON en DevTools)

## Veredicto de Schneier

[aprobado | con condiciones | bloqueado] · [razón] · [fecha]
