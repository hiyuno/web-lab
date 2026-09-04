# Umbrales y criterios del análisis

Los valores viven en el diccionario `T` al inicio de `scripts/analyze_assets.py`. Son
heurísticas razonables para sitios de marketing/portafolio; ajústalos si el usuario tiene
otro criterio (por ejemplo, un sitio de fotografía tolera imágenes más pesadas).

## Imágenes

| Criterio | Warn | Crit | Por qué |
|---|---|---|---|
| Peso | > 300 KB | > 1 MB | Por encima de 300 KB una imagen ya domina el LCP en móvil. |
| Sobredimensión | ancho ≥ 2× (renderizado × DPR) | ≥ 3× | El navegador descarga píxeles que nunca muestra. Se usa el ancho renderizado más grande visto en cualquier página. |
| Ancho absoluto | > 4000 px | — | Casi nunca se necesita más de 2560 px, ni en retina. |
| PNG sin alpha | > 100 KB | — | PNG solo compensa con transparencia o gráficos planos; una foto en PNG pesa 3-10× más que en WebP. |
| GIF animado | — | siempre | Un MP4/WebM equivalente pesa 5-20× menos. |
| SVG | > 150 KB | — | Suele ser un SVG exportado con imágenes embebidas o sin simplificar. |
| BMP / TIFF | — | siempre | Formatos sin compresión para web. |

Nota Framer: Framer sirve variantes WebP/AVIF redimensionadas, así que el peso *servido*
puede ser mucho menor que el original. Aun así conviene subir originales razonables (≤ 2560 px,
< 1 MB): las variantes grandes para retina parten del original y el primer render de cada
variante es más lento.

## Videos

| Criterio | Warn | Crit | Por qué |
|---|---|---|---|
| Peso | > 8 MB | > 20 MB | Framer y la mayoría de builders no recomprimen video. |
| Resolución | alto > 1080 px | — | 4K en un hero web no se aprecia y multiplica el peso ×4. Fondos: 720p basta. |
| Bitrate | > 6 Mbps | > 12 Mbps | Objetivo 3-5 Mbps a 1080p, 1.5-2.5 Mbps a 720p. |
| Audio en muted/autoplay | siempre | — | Pista de audio inútil que pesa y a veces bloquea autoplay. |
| Códec | — | fuera de H.264/HEVC/AV1/VP9 | ProRes, MJPEG o similares no son para web. |
| Autoplay sin poster | nota | — | Sin poster hay un hueco vacío hasta que carga el primer frame. |
| Loop largo | > 30 s | — | Los loops de fondo funcionan igual con 8-15 s. |

## Comandos de optimización (para el usuario, no ejecutar sin que lo pida)

Video hero/fondo, 1080p, sin audio, listo para streaming progresivo:
```bash
ffmpeg -i in.mp4 -an -vf "scale=-2:1080" -c:v libx264 -crf 26 -preset slow -movflags +faststart -pix_fmt yuv420p out.mp4
```
Fondo 720p más agresivo: cambia `1080` por `720` y `-crf 26` por `-crf 28`.
Versión WebM (opcional, más pequeña, sin soporte en Safari viejo):
```bash
ffmpeg -i in.mp4 -an -vf "scale=-2:1080" -c:v libvpx-vp9 -b:v 0 -crf 34 out.webm
```
Poster de un video:
```bash
ffmpeg -i in.mp4 -ss 00:00:01 -frames:v 1 -q:v 3 poster.jpg
```
GIF a MP4:
```bash
ffmpeg -i in.gif -movflags +faststart -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" out.mp4
```
Imagen: redimensionar a 2560 px y recomprimir con sips (viene en macOS):
```bash
sips -Z 2560 -s format jpeg -s formatOptions 80 in.png --out out.jpg
```
Imagen a WebP con Pillow:
```bash
python3 -c "from PIL import Image; im=Image.open('in.png'); im.thumbnail((2560,2560)); im.save('out.webp', quality=80, method=6)"
```
