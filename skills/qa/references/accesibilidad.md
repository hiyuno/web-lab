# Accesibilidad · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Beizer · Nivel: WCAG 2.2 AA · Staging: [URL]

Las herramientas detectan entre 30 y 57 % de los problemas. Lo demás es esta lista, a mano.

## Automático (axe en Playwright)

| Plantilla | Claro | Oscuro | Estados probados (menú, modal, error, hover) | Violaciones |
|-----------|-------|--------|-----------------------------------------------|-------------|
| home | | | | |

## Manual · teclado (5 a 10 minutos por plantilla)

| Plantilla | Tab llega a todo | Orden lógico | Foco visible siempre | Saltar al contenido es el 1.º | Sin trampas | Escape cierra | Ok |
|-----------|------------------|--------------|----------------------|-------------------------------|-------------|---------------|----|
| | | | | | | | |

## Manual · lector de pantalla (VoiceOver: Cmd+F5 en Mac; en iPhone triple clic lateral)

Guion para quien lo hace. Veinte minutos. Un flujo completo de `flujos.md`.

1. Abre la home con VoiceOver activo. ¿El título de la página se anuncia y tiene sentido?
2. Navega por encabezados (VO+Cmd+H). ¿El esquema se entiende sin ver la pantalla?
3. Navega por landmarks (rotor). ¿Hay header, nav, main, footer con nombres distintos?
4. Recorre los enlaces con el rotor. Leídos solos, ¿se sabe a dónde van? Anota los "leer más".
5. Completa la tarea principal (por ejemplo, enviar el formulario). ¿Cada campo anuncia su etiqueta? ¿El error se anuncia y dice cómo corregir? ¿La confirmación se anuncia?
6. Abre un menú o modal. ¿Se anuncia? ¿El foco entra y vuelve al cerrar?
7. Una imagen con contenido: ¿el alt dice lo que importa? Una decorativa: ¿se ignora?
8. Cambia algo con estado (modo oscuro, favorito). ¿El nombre del control cambia con él?

| Paso | Resultado | Cita de lo que anunció | Severidad |
|------|-----------|------------------------|-----------|
| | | | |

## Manual · visual y motor

- [ ] Zoom 200 %: nada se corta, nada se superpone
- [ ] Reflow a 320 px: sin scroll horizontal
- [ ] Movimiento reducido activado (Sistema → Accesibilidad): nada esencial se pierde
- [ ] Contraste real sobre imágenes y en hover, foco, deshabilitado, modo oscuro
- [ ] Objetivos táctiles ≥ 24 px; en móvil real se aciertan con el pulgar
- [ ] Nada solo por color; nada solo al pasar el cursor; arrastres con alternativa
- [ ] Login funciona con gestor de contraseñas y pegar; no pide el mismo dato dos veces
- [ ] Ayuda en el mismo lugar en todas las páginas

## Hallazgos

Van al `reporte.md` con severidad. Barrera en tarea clave = crítico.
