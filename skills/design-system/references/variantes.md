# Variantes · paso 4.1

Adaptado de `variant` de la colección `interfaces` de Jakub Krehel (MIT). Aquí es un paso de
Frost con checkpoint del usuario; allí es un skill que solo el usuario dispara.

## Respuestas distintas, no tintes distintos

Tres direcciones que difieren solo en el color de acento no enseñan nada. Cada variante es una
respuesta distinta al mismo brief sobre **un solo eje**:

| Eje | Dueño de las reglas | Qué varía |
|-----|---------------------|-----------|
| Estructura | `better-layout` | agrupación, orden, columnas, qué colapsa |
| Densidad | `better-layout` | escala de espaciado, áreas de toque, cuánto cabe |
| Énfasis | `better-colors` | dónde va el color sólido, qué retrocede |
| Tipografía | `better-typography` | pasos de escala, contraste de peso, medida |
| Voz | `better-writing` | etiquetas, tono, cuánto texto |

Elige un eje primario y da a cada variante una posición distinta. Lo secundario sigue al eje:
una variante densa puede pedir un paso tipográfico menor, y eso es coherencia, no un segundo
eje. Variar todo a la vez produce tres resultados que no se pueden atribuir.

## El piso que toda variante cumple

Una variante que gana en aspecto y falla un disparador de escalada (CLAUDE.md, método de
revisión) no es candidata. Nombre accesible en cada control, teclado llega a todo, foco
visible, nada se corta a 320 px, ningún significado solo por color. El piso no es un eje y
nunca se negocia contra uno.

## Procedimiento

1. **Una pieza.** La home entera no es una pieza; el hero o la tarjeta de producto sí. Empieza
   por la que define a las demás y ofrece el resto como rondas posteriores.
2. **Lee el terreno.** Guía editorial, wireframes, tokens si ya existen, gustos del usuario en
   `docs/PREFERENCIAS.md`. Sin marca previa: grises neutros, un acento y fuente del sistema, y
   dilo.
3. **Nombra el eje y las tres posiciones antes de escribir código.** Nombres que digan la
   dirección: `Silenciosa`, `Editorial`, `Densa`; nunca `Opción A`. Tres por defecto; cinco
   solo si el espacio lo pide.
4. **Constrúyelas en la página real** del prototipo, con el texto real de los briefs y la
   cantidad real de elementos. Un parámetro de URL las selecciona (`?variante=densa`) y un
   control flotante, visiblemente fuera del sistema de diseño, permite cambiar. Una a la vez,
   a tamaño completo; las miniaturas mienten sobre el espacio.
5. **Recórrelas tú primero**, en 375 y 1280, sin errores en consola.
6. **Presenta la tabla y para.** Sin marcar favorita.

| Variante | Posición en el eje | Va bien cuando | Cuesta |
|----------|--------------------|----------------|--------|
| | | | |

Di dónde corre el selector y a qué ancho juzgaste. Si te preguntan cuál, responde por la
frecuencia de uso y la personalidad del producto, no por la que disfrutaste construir.

7. **Checkpoint A.** El usuario elige. Promueve esa variante al sistema siguiendo las
   convenciones del proyecto y borra las demás y el selector, salvo que pida otra ronda:
   entonces conserva el selector y toma nuevas posiciones alrededor de la elegida.

## Antes de terminar

| Síntoma | Arreglo |
|---------|---------|
| Las variantes solo difieren en color o en texto | mueve una a otra posición del eje o córtala |
| Todos los ejes varían a la vez | varía uno; deja que el resto siga |
| Juzgadas en una ruta en blanco | móntalas en la página que las contendrá |
| Lorem ipsum, tres filas, "Juan Pérez" | texto real y la cantidad real de elementos |
| La más audaz salta teclado o foco | cumple el piso o descarta la dirección |
| Una favorita marcada en la tabla | costo de cada una y que el usuario elija |
| Selector con los tokens del proyecto | manténlo visiblemente fuera del sistema |
| Selector olvidado tras la promoción | bórralo salvo que pidan conservarlo |
