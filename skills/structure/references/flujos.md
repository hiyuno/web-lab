# Flujos de usuario · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Rosenfeld · Fuente: historias de `docs/01-descubrimiento/spec.md`

Una sección por tarea principal. Marca con 🔒 los pasos donde la persona entrega un dato o
entra con cuenta: son las superficies que revisa Schneier.

## Tareas principales

| # | Audiencia | Tarea | Historias | Entrada típica | Éxito |
|---|-----------|-------|-----------|----------------|-------|
| T1 | | | H-01, H-03 | buscador, red social, enlace directo, correo | |

## T1 · [nombre de la tarea]

```mermaid
flowchart LR
  E[Entrada: buscador] --> P1[/página-de-entrada]
  P1 --> D{¿Decisión?}
  D -->|sí| P2[/siguiente]
  D -->|no| P3[/alternativa]
  P2 --> F[🔒 /formulario: nombre, correo]
  F --> OK[Éxito: confirmación]
```

Páginas que toca: [ ]. Datos que entrega: [ ]. Qué pasa si abandona en el paso X: [ ].

## Páginas que salen de los flujos

Lista consolidada de todas las páginas que aparecen en los flujos. Es el insumo del sitemap.

- [ ]
