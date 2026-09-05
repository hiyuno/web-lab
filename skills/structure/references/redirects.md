# Mapa de redirects · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Rosenfeld · Se convierte al formato del hosting en la fase 7 (Allspaw)

Reglas: una fila por URL actual que cambia. Uno a uno hacia la página más afín. Nunca en masa a
la home. Sin cadenas. Todo 301. Los enlaces internos del sitio nuevo apuntan a la URL nueva.

| URL actual | URL destino | Tipo | Motivo | Tráfico 90d | Posiciones | Backlinks | Responsable | Probado |
|------------|-------------|------|--------|-------------|------------|-----------|-------------|---------|
| /vieja | /nueva | 301 | fusionar / renombrar / eliminar | | | | | [ ] |

## Patrones (si hay muchas URLs con la misma forma)

| Patrón actual | Patrón destino | Ejemplo |
|---------------|----------------|---------|
| /blog/2023/:slug | /blog/:slug | /blog/2023/hola → /blog/hola |

## URLs que se conservan sin cambio

[ ] (no necesitan redirect; se listan para verificar que siguen respondiendo 200 tras el lanzamiento)

## Verificación tras el lanzamiento (Allspaw y Beizer)

- [ ] Cada fila devuelve 301 a su destino y el destino devuelve 200.
- [ ] Ninguna cadena de más de un salto.
- [ ] Rastreo del sitio nuevo sin enlaces internos a URLs viejas.
- [ ] Search Console sin errores de cobertura nuevos a los 7 y 30 días.
