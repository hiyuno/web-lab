# Pull request · [H-xx.Tn] · [título]

## Qué cambia

[Dos frases. Qué historia cubre y qué se puede probar en la preview.]

Preview: [URL] · Captura: [ ]

## Cómo probarlo

1. [ ]
2. [ ]

## Checklist del autor

- [ ] Prueba en rojo antes, verde ahora; archivos: [ ]
- [ ] Verificado 375 y 1280
- [ ] Solo tokens; estados completos
- [ ] Sin secretos ni datos privados al cliente
- [ ] Lint, tipos, pruebas verdes

## Checklist del revisor

Correctitud
- [ ] Hace lo que dice el criterio de aceptación y nada más
- [ ] Casos límite: vacío, muy largo, caracteres raros, doble clic, sesión expirada
- [ ] Manejo de errores: genérico al usuario, detalle al log

Seguridad (leer con atención si toca auth, datos, pagos, borrado, uploads, `route.ts`, `proxy.ts`)
- [ ] Entrada validada con esquema en la frontera
- [ ] Autorización por recurso dentro de la acción o la capa de datos, no solo en la página
- [ ] Retorno filtrado a lo que la interfaz necesita
- [ ] Sin `process.env` ni cliente de BD fuera de `src/data/`
- [ ] Sin `dangerouslySetInnerHTML` / `set:html` con contenido no controlado
- [ ] Dependencias nuevas justificadas y con lockfile

Rendimiento
- [ ] `"use client"` / `client:*` solo donde hace falta
- [ ] Imágenes con dimensiones, `sizes`, prioridad; fuentes sin bloqueo
- [ ] Lighthouse CI dentro de presupuesto

Accesibilidad
- [ ] Elementos nativos, `label`, foco visible, nombre accesible, teclado

Calidad
- [ ] Nombres claros, sin duplicar utilidades existentes, sin código muerto
- [ ] Commits pequeños y explicables
- [ ] Lo que no entiendo, lo pregunto; no se mezcla lo que nadie puede explicar

Resultado: [ ] aprobar · [ ] cambios pedidos: [ ]
