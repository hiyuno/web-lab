# Fixes específicos de Framer

Framer da buena base (URLs limpias, sitemap automático, meta por página, Open Graph, SSL,
imágenes optimizadas) pero limita el control técnico fino por debajo del plan Enterprise. Esta
referencia da el fix exacto por tipo de hallazgo en vez de una instrucción genérica que no
aplica en la plataforma.

## Meta tags por página (title, description, OG)

Site Settings → páginas → seleccionar la página → panel **SEO** en el lado derecho. Cada página
tiene sus propios campos de title, description y Open Graph image; no hay que tocar código.

## `<html lang>`

Site Settings → **General** → Language. Si el sitio es multi-idioma real (no solo el atributo),
Framer no soporta hreflang nativo por debajo de Enterprise: documentarlo como limitación conocida,
no como algo que el usuario "olvidó" configurar.

## JSON-LD / schema.org

Framer no tiene UI para schema. Se agrega como **Custom Code** → "End of `<head>` tag" (a nivel
sitio para `Organization`, o por página para `Article`/`Product`/`FAQPage`):

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "NOMBRE_DEL_SITIO",
  "url": "https://ejemplo.com",
  "logo": "https://ejemplo.com/logo.png",
  "sameAs": ["https://instagram.com/...", "https://linkedin.com/company/..."]
}
</script>
```

Validar siempre con el Rich Results Test de Google antes de dar por resuelto el hallazgo — un
JSON-LD con sintaxis inválida se ignora silenciosamente.

## robots.txt

Framer genera `/robots.txt` automáticamente y **no es editable** por debajo de Enterprise. Si el
audit encuentra que bloquea bots de recuperación de IA (`OAI-SearchBot`, `ChatGPT-User`,
`Claude-SearchBot`, `PerplexityBot`...), es una limitación de plataforma: documentarla como tal y,
si de verdad importa para el proyecto, la opción es evaluar el plan Enterprise o mover el sitio.
No hay workaround en el plan estándar.

## llms.txt

No hay UI dedicada. Se sirve como archivo estático si Framer lo permite en el proyecto, o vía
Custom Code de una página con la ruta `/llms.txt` si el hosting lo soporta; si no es viable,
marcarlo como "no aplica en este plan" en vez de dejarlo como pendiente indefinido.

## Favicon

Site Settings → **General** → Icon.

## 404 personalizado

Se edita la página `404` del proyecto igual que cualquier otra página; Framer ya la sirve con
status 404 correcto, así que si el audit reporta un soft-404 normalmente es porque la página que
se probó existe de verdad (falso positivo) o porque hay un redirect mal configurado a home.

## Core Web Vitals

Sin control de bundle JS ni pipeline de imágenes propio: la optimización de peso de imágenes y
video vive en el skill `optimize-assets` (Bellard), no en este. Si Core Web Vitals sale mal por
peso de medios, referir ahí en vez de duplicar el trabajo.
