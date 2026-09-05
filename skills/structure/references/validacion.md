# Validación de la estructura · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Rosenfeld

## Card sorting (paso 2.3)

**Preparación.** Una tarjeta por contenido, entre 30 y 60, con nombre neutro (sin la etiqueta
que quieres validar). Abierto si no hay estructura previa: los participantes agrupan y
nombran. Cerrado si quieres validar categorías ya propuestas.

**Guion para el usuario o el participante.**
1. "Aquí hay tarjetas con cosas que tendrá el sitio. Agrúpalas como te parezca natural. No hay respuesta correcta."
2. "Ponle un nombre a cada grupo, con las palabras que tú usarías para buscarlo."
3. "¿Alguna tarjeta que no supiste dónde poner? ¿Alguna que pondrías en dos sitios?"

**Herramientas.** Con personas remotas: OptimalSort, Maze o una pizarra en Miro. Con el
usuario como proxy: una tabla en este documento.

**Resultado.** Tabla en `organizacion.md`: grupos, tarjetas, porcentaje de acuerdo y nombres.
Un acuerdo bajo el 50 % en una tarjeta significa que va en dos sitios o que necesita otro nombre.

## Tree testing (paso 2.7)

**Preparación.** La jerarquía del sitemap en texto plano, solo etiquetas, sin diseño ni
descripciones. Cinco a ocho tareas que cubran las tareas principales de `flujos.md`, escritas
sin usar las palabras de las etiquetas ("¿dónde averiguarías cuánto cuesta?" y no "¿dónde
está Precios?").

**Guion.**
1. "Te voy a mostrar el menú de un sitio como una lista. Para cada pregunta, dime dónde harías clic primero y luego dónde seguirías hasta encontrarlo."
2. Una tarea a la vez. No ayudes. Anota el primer clic, la ruta y si llegó.
3. Al final: "¿Alguna etiqueta que no entendiste?"

**Registro.**

| Tarea | Destino correcto | Participante | Primer clic | Ruta | Llegó | Directo (sin volver atrás) |
|-------|------------------|--------------|-------------|------|-------|----------------------------|
| | | P1 | | | sí/no | sí/no |

**Resumen por tarea.**

| Tarea | Éxito (%) | Primer clic correcto (%) | Directo (%) | Diagnóstico | Cambio en el sitemap |
|-------|-----------|--------------------------|-------------|-------------|----------------------|
| | | | | etiqueta / ubicación / falta página | |

**Interpretación.** Éxito bajo con primer clic correcto: el problema está en el segundo nivel.
Primer clic equivocado en más de la mitad: la etiqueta de primer nivel no huele a lo que hay
detrás. Éxito alto pero indirecto: funciona pero cuesta; revisa nombres cercanos.

**Umbral.** Menos de cinco participantes o participantes que ya conocen el proyecto: anota
"no validado" y sigue. Las decisiones se marcan como supuestos en la spec.

## Resultado

- Participantes: [n] · Proxy: sí/no
- Cambios aplicados al sitemap: [ ]
- Pendiente de validar: [ ]
