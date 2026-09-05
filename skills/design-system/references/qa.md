# QA de diseño · [proyecto]

Fecha: [aaaa-mm-dd] · Revisa: Frost · Sobre: prototipo en [URL o rama] · Estado: [ ] aprobado

Se verifica sobre el prototipo en código, en 375, 768 y 1280, en modo claro y oscuro si existe.

## Tokens

- [ ] Ningún color, espacio, radio, sombra o duración fuera de `tokens.css` (buscar valores literales en el CSS)
- [ ] `tokens_to_tailwind.py --check` sin fallos de contraste
- [ ] Modo oscuro: solo sobreescritura semántica; nada hardcodeado

## Tipografía

- [ ] Familia, tamaño, line-height y tracking de la escala en cada elemento
- [ ] Jerarquía visible: se distingue H1, H2, cuerpo y nota sin leer
- [ ] Longitud de línea 45 a 75 caracteres en cuerpo
- [ ] Texto real de los briefs, sin truncados ni desbordes

## Componentes

- [ ] Cada componente del inventario tiene los 9 estados en el prototipo
- [ ] Foco visible en todos; objetivos ≥ 24 px; nada solo-hover
- [ ] Mismo componente se ve igual en todas las plantillas
- [ ] Textos largos y cortos probados

## Plantillas y responsive

- [ ] 375: sin scroll horizontal, menú accesible, imágenes con proporción
- [ ] 768 y 1280: retícula respetada, ancho máximo de contenido
- [ ] Estados de página: cargando sin saltos, vacío, error, éxito
- [ ] Imágenes con el asset y proporción de assets.md; la del hero marcada como prioridad

## Accesibilidad

- [ ] Checklist de `accesibilidad.md` completa
- [ ] Recorrido con teclado de los flujos principales
- [ ] Zoom 200 % y reflow 320 px
- [ ] Reduced motion activado: nada esencial se pierde

## Movimiento

- [ ] Solo lo listado en `motion.md`, con tokens de duración y curva
- [ ] Nada empuja el layout

## Contenido y seguridad

- [ ] Copy exacto de los briefs, incluidos microcopy y errores
- [ ] Login en página propia, `autocomplete`, ver contraseña, error genérico
- [ ] Acciones destructivas con confirmación y separadas
- [ ] Consentimiento: rechazar tan visible como aceptar
- [ ] Sesión visible en pantallas autenticadas

## Hallazgos

| # | Dónde | Qué | Severidad | Arreglo en | Estado |
|---|-------|-----|-----------|------------|--------|
| | | | bloqueante / mayor / menor | token / componente / plantilla | |
