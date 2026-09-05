# Tarea · [H-xx.Tn] · [título en una frase]

Pista: fe | be | infra | media · Rol: Osmani | Hopper | Bellard · Rama: `feat/h-xx-tn-slug` · Estado: pendiente

## Contexto

- Historia: [H-xx · título] en `docs/01-descubrimiento/spec.md`
- Diseño: `docs/04-diseno/componentes/<x>.md`, `plantillas/<y>.md`
- Contenido: `docs/03-contenido/briefs/<slug>.md`
- Depende de: [T-000, H-xx.T1]

## Objetivo

[Qué existe cuando la tarea termina, en una frase observable.]

## Criterios de aceptación (de la spec)

- Dado [contexto], cuando [acción], entonces [resultado].
- Dado [contexto inválido], cuando [acción], entonces [mensaje o comportamiento].

## Restricciones

- Solo tokens de `tokens.css`; componentes de Frost con sus estados.
- [Astro: sin `client:*` salvo ...] · [Next.js: Server Component salvo ...]
- Presupuesto: no sube JS inicial más de [n] KB.
- Seguridad: [validar con Zod ...; autorizar por propiedad ...; sin datos privados a cliente].
- Accesibilidad: [teclado, foco, nombre accesible, contraste].

## Pruebas (escribir primero, ver en rojo)

| Caso | Tipo | Archivo | Comando |
|------|------|---------|---------|
| H-xx.C1 | unit / e2e | `tests/...` | `pnpm test -- <archivo>` |

## Verificación manual

- [ ] 375 y 1280, claro y oscuro
- [ ] Teclado: Tab, Enter, Escape
- [ ] Estados: vacío, cargando, error, éxito

## Definición de terminado

Ver `definicion-de-terminado.md`. PR con plantilla, preview, captura, revisado.
