# Accesibilidad del sistema · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Frost · Nivel: WCAG 2.2 AA · Verificado en tokens y componentes, no página por página.

## Contraste (verificado por `tokens_to_tailwind.py`)

| Par | Mínimo | Claro | Oscuro | Ok |
|-----|--------|-------|--------|----|
| foreground / background | 4.5 | | | |
| muted-foreground / background | 4.5 | | | |
| primary-foreground / primary | 4.5 | | | |
| ring / background | 3 | | | |

Texto grande (≥ 24 px, o ≥ 18.66 px en negrita) y componentes gráficos: 3:1. Texto sobre imagen: capa de color o caja detrás; nunca a ojo.

## Checklist WCAG 2.2 AA para el diseño

Percepción
- [ ] Nada se comunica solo por color: icono, texto o patrón además del color
- [ ] Texto redimensionable al 200 % sin perder contenido ni función
- [ ] Reflow a 320 px de ancho sin scroll horizontal
- [ ] Espaciado de texto ajustable (line-height 1.5, párrafos 2×) sin romper
- [ ] Imágenes con contenido llevan alt de assets.md; decorativas `alt=""`

Operación
- [ ] Foco visible en todo elemento interactivo: ≥ 2 px, 3:1 contra el fondo, nunca eliminado (2.4.11)
- [ ] Objetivos ≥ 24 × 24 px o con espacio suficiente entre ellos (2.5.8)
- [ ] Ningún control aparece solo al pasar el cursor o al enfocar (3.2.7)
- [ ] Toda acción de arrastrar tiene alternativa de un clic (2.5.7)
- [ ] Orden de foco lógico y sin trampas; enlace "saltar al contenido"
- [ ] Sin contenido que parpadee más de 3 veces por segundo
- [ ] Animaciones con alternativa bajo `prefers-reduced-motion`; nada esencial depende del movimiento
- [ ] Hover y foco muestran lo mismo; el contenido que aparece se puede descartar con Escape

Comprensión
- [ ] Ayuda (contacto, chat, FAQ) en el mismo lugar en todas las páginas (3.2.6)
- [ ] No se pide el mismo dato dos veces en un flujo; se rellena o se ofrece elegir (3.3.8)
- [ ] Login funciona con gestores de contraseñas y pegar; sin pruebas cognitivas ni CAPTCHA de recordar (3.3.7)
- [ ] Etiquetas visibles en todos los campos; placeholder no sustituye etiqueta
- [ ] Errores identificados junto al campo, con texto que dice cómo corregir
- [ ] Navegación consistente entre páginas

Robustez (para Osmani)
- [ ] Elementos nativos antes que ARIA: `<button>`, `<a>`, `<input>`, `<dialog>`
- [ ] Nombre accesible en todo control; landmarks: header, nav, main, footer

## Por componente

| Componente | Rol | Nombre | Teclado | Anuncia | Pendiente |
|------------|-----|--------|---------|---------|-----------|
| | | | | | |

## Decisiones y excepciones

| Qué | Por qué | Alternativa ofrecida | Aprobó |
|-----|---------|----------------------|--------|
| | | | |
