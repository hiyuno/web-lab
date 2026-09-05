# Registro de riesgos aceptados · [proyecto]

`docs/SEGURIDAD-riesgos.md`. Aceptar un riesgo a sabiendas es legítimo; ignorarlo no. Cada
fila la firma quien decide, con fecha y fecha de revisión. Se relee en cada puerta y en la
revisión anual.

| # | Hallazgo | Severidad | Fase | Razón para aceptar | Controles compensatorios | Quién acepta | Fecha | Revisar el | Estado |
|---|----------|-----------|------|--------------------|--------------------------|--------------|-------|------------|--------|
| R-01 | | | | | | | | | abierto / cerrado / mitigado |

## Reglas

- Un crítico no se acepta: se corrige o se elimina la función.
- Un alto se puede aceptar solo con fecha de corrección antes del día 30 post-lanzamiento.
- Todo riesgo aceptado tiene fecha de revisión; al llegar, se vuelve a decidir.
- Si el contexto cambia (más usuarios, nuevos datos, incidente), el riesgo se reabre.
