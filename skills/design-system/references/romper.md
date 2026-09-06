# Romper · paso 4.8

Adaptado de `break` de la colección `interfaces` de Jakub Krehel (MIT). Renderiza un componente
en todos los escenarios que pueden alcanzarlo, en una página desechable que es el reporte.
Un componente construido contra el camino feliz parece terminado hasta que llega el contenido
real.

Observa, no juzga. Un hallazgo es algo que se rompió visiblemente, nombrado con el vocabulario
del skill que posee el arreglo. Aquí se aísla a propósito: no se juzga cómo se ve en contexto,
sino si se defiende con el peor contenido.

## Procedimiento

1. **Un componente por corrida.** El formulario de contacto no es un componente; su campo de
   texto sí. Con varios candidatos, lista y pregunta cuál.
2. **Infiere los escenarios del componente**, no del menú. Lee sus props, slots, estados y
   datos. Cada eje tiene una señal que dice si aplica; conserva solo los que coinciden y di en
   una línea cuáles descartaste.
3. **Construye la página desechable**: una ruta de prueba dentro del prototipo, el componente
   real importado sin tocar, una instancia por escenario en una columna con una etiqueta de
   texto encima. Nada de estilos propios, ni temas simulados, ni datos en vivo. Los anchos son
   contenedores fijos en la misma página, nunca redimensionar la ventana.
4. **Mira una vez.** Carga, recorre de arriba abajo y anota lo que se rompió visiblemente:
   "el texto sale por el borde derecho", nunca "el espaciado se siente apretado". Una carga es
   el presupuesto. Marca cada rotura debajo de su etiqueta en la página.
5. **Reporta y para.** Roturas primero:

| Escenario | Observado | Dueño |
|-----------|-----------|-------|
| Una cadena de 60 caracteres sin espacios | desborda la tarjeta, sin ajuste ni truncado | `better-typography` |
| Cero elementos | región en blanco sin mensaje | `better-writing` |

"Todo sobrevivió" es un reporte completo. Di qué escenarios están en la página y dónde corre.
No arregles sin que te lo pidan; al arreglar, sigue al dueño y vuelve a renderizar solo lo que
falló.

6. **Deja la página arriba** hasta que el usuario diga que terminó; es la mitad del reporte.

## Ejes y señales

| Eje | Señal para incluirlo | Escenarios |
|-----|----------------------|------------|
| Longitud de contenido | renderiza texto que no escribe el equipo | vacío · una palabra · típico · varias frases · una cadena irrompible |
| Forma del contenido | el texto puede venir de usuarios o idiomas ajenos | emoji solo y mezclado · texto de derecha a izquierda · dirección mixta · diacríticos y letras altas · números en columnas |
| Cantidad | se repite sobre elementos | cero · uno · la cantidad realista · diez veces la realista |
| Contenedor | siempre | 320 px · apretado por un hermano flex o grid · muy ancho |
| Estado | el componente tiene el estado como prop | cargando · error · deshabilitado (hover y foco los prueba el usuario con teclado) |
| Entorno | el proyecto soporta el modo; no se simula, se pide al usuario que lo active | modo oscuro · zoom 200 % · movimiento reducido |

Dueños típicos: ajuste y truncado en `better-typography`; sin sitio en `better-layout`; texto
fuente en `better-writing`; vacíos en `better-writing` y `better-layout`; estados en
`better-accessibility`; modo oscuro en `better-colors`.

## Antes de terminar

| Síntoma | Arreglo |
|---------|---------|
| Todos los ejes contra todos los componentes | solo los que la señal admite, y di cuáles descartaste |
| Un fallo previsto reportado como observado | renderízalo o déjalo fuera |
| Un escenario sin el contenido que se le dio | la página está rota, no el componente; hazla cliente y revisa |
| Un componente parecido reconstruido en la página | importa el real |
| La página restiliza o retema el componente | layout, fuentes y tokens tal cual; solo etiquetas y anchos |
| Ventana redimensionada por escenario | contenedores fijos; una carga muestra todos |
| Rotura en la tabla sin marca en la página | anótala bajo su etiqueta |
| Página borrada en el mismo turno del reporte | bórrala solo cuando el usuario lo diga |
