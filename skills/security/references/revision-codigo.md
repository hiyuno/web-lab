# Revisión de código · fase 5

Manual y por fronteras. El control de acceso roto es la vulnerabilidad más frecuente y la que
ningún escáner encuentra. Semgrep después, como red de seguridad.

## 1. Mapa en un minuto

```bash
grep -rn "process.env" src --include=*.ts --include=*.tsx | grep -v "src/data/" | grep -v NEXT_PUBLIC_
grep -rln "from '@/data/db'\|from '@/db'" src | grep -v "src/data/"
grep -rn "dangerouslySetInnerHTML\|set:html" src
grep -rn "NEXT_PUBLIC_" .env.example src | grep -iE "secret|key|token|password"
grep -rn "'use server'" src -l
grep -rn "export async function \(GET\|POST\|PUT\|PATCH\|DELETE\)" src/app/api
```

Las dos primeras deben salir vacías (salvo `proxy.ts` y webhooks). La cuarta debe salir vacía
siempre. Las dos últimas son tu lista de entradas.

## 2. Archivos en orden de riesgo

1. `proxy.ts` / `middleware.ts`: solo cabeceras y redirecciones. Si decide auth, es hallazgo alto.
2. `src/app/api/**/route.ts`: firma de webhooks antes de leer el cuerpo; sin lógica de negocio.
3. `src/actions/**`: cada acción valida con Zod, llama a `src/data`, devuelve solo lo necesario, error genérico.
4. `src/data/**`: `import 'server-only'`; autentica; **autoriza en la consulta** (dueño u organización); DTO.
5. Componentes `"use client"`: props sin campos privados; tipos estrechos.
6. Carpetas `[param]`: parámetro validado antes de usarse.
7. `next.config.ts`, `vercel.json`, `astro.config.mjs`: cabeceras, CSP, redirects, `images.remotePatterns` acotado.
8. `package.json` y lockfile: dependencias nuevas justificadas; `pnpm audit`.

## 3. Categorías (OWASP Code Review Guide) y qué buscar

| Categoría | Buscar | Hallazgo típico |
|-----------|--------|-----------------|
| Validación de entrada | Zod en toda frontera; listas blancas; tamaño máximo | tipo TS confiado en runtime |
| Codificación de salida | JSX escapa por defecto; HTML externo con DOMPurify; URLs con `encodeURIComponent` | `dangerouslySetInnerHTML` con CMS |
| Autenticación | proveedor; re-verificación en cada acción; cookies HttpOnly Secure SameSite | auth solo en la página |
| Sesiones | expiración; invalidación al cambiar contraseña; rotación tras elevar privilegio | sesión eterna |
| Control de acceso | propiedad en la consulta; roles verificados en servidor; mismo error para "no existe" y "no es tuyo" | IDOR |
| Criptografía | nada casero; secretos en env; hashes vía proveedor; `crypto.randomUUID` | secreto en el repo |
| Errores y registro | genéricos al usuario; detalle al log sin datos personales; acciones sensibles registradas con id | stack trace al cliente |
| Protección de datos | DTO mínimo; datos sensibles cifrados si el modelo lo pide; borrado y exportación posibles | registro completo al cliente |
| Comunicación | HTTPS; HSTS; terceros por HTTPS; webhooks firmados | webhook sin firma |
| Configuración | CSP sin unsafe-inline; cabeceras; `.env` en gitignore; source maps privados | CSP con unsafe-inline |
| Archivos | tipo real, tamaño, renombrado, origen aparte | extensión confiada |
| Rate limiting | login, registro, recuperación, formularios, endpoints caros | ninguno |

## 4. Semgrep (complemento)

```bash
semgrep --config p/owasp-top-ten --config p/nextjs --config p/typescript src
```

Cada resultado se lee; un falso positivo se documenta, no se silencia a ciegas.

## 5. Escribir el hallazgo

Con `risk_rating.py` para la severidad y `veredicto.md` para el formato. "Qué puede pasar"
es una historia de dos frases que entiende el dueño del negocio: "Un cliente cambia el número
en la URL de su pedido y ve el pedido de otro cliente, con nombre y dirección. Lo puede hacer
cualquiera con cuenta en dos minutos."
