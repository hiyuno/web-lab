# SEO por página · [proyecto]

Fecha: [aaaa-mm-dd] · Autor: Rosenfeld · Lo implementa Osmani en la fase 5; lo valida Beizer en la 6.

## Tabla por página

| URL | Título (50-60) | Meta description (120-160) | H1 | Keyword | Canonical | Schema | OG image |
|-----|----------------|----------------------------|----|---------|-----------|--------|----------|
| / | | | | | / | Organization, WebSite | og/home.jpg |

## Reglas

- Título único por página, keyword al inicio, marca al final si cabe: "Keyword · Marca".
- Meta description con llamada a la acción. No influye en ranking; influye en el clic.
- Un H1 por página. H2 como las preguntas que haría el lector. Sin saltos de nivel.
- Enlaces internos pilar ↔ satélites con anclas descriptivas. Ninguna página huérfana.
- Canonical en todas. `hreflang` si hay idiomas. `robots` solo para excluir legales o gracias si se decide.
- Open Graph: `og:title`, `og:description`, `og:image` (1200 × 630), `og:type`, `og:url`. Twitter card `summary_large_image`.
- JSON-LD solo con datos visibles en la página. Validar en la fase 6 con la prueba de resultados enriquecidos de Google.

## JSON-LD por plantilla

Home: Organization + WebSite.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://ejemplo.mx/#org",
      "name": "[Razón social o marca]",
      "url": "https://ejemplo.mx/",
      "logo": "https://ejemplo.mx/logo.png",
      "contactPoint": { "@type": "ContactPoint", "email": "hola@ejemplo.mx", "contactType": "customer service" },
      "sameAs": ["https://www.instagram.com/ejemplo"]
    },
    {
      "@type": "WebSite",
      "@id": "https://ejemplo.mx/#site",
      "url": "https://ejemplo.mx/",
      "name": "[Nombre del sitio]",
      "publisher": { "@id": "https://ejemplo.mx/#org" },
      "inLanguage": "es-MX"
    }
  ]
}
```

Interior con más de un nivel: BreadcrumbList.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Inicio", "item": "https://ejemplo.mx/" },
    { "@type": "ListItem", "position": 2, "name": "[Sección]", "item": "https://ejemplo.mx/seccion" },
    { "@type": "ListItem", "position": 3, "name": "[Página]" }
  ]
}
```

Artículo o entrada de blog: Article.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[H1]",
  "description": "[meta description]",
  "image": "https://ejemplo.mx/og/articulo.jpg",
  "author": { "@type": "Person", "name": "[Nombre]", "url": "https://ejemplo.mx/sobre" },
  "publisher": { "@id": "https://ejemplo.mx/#org" },
  "datePublished": "2026-09-05",
  "dateModified": "2026-09-05",
  "mainEntityOfPage": "https://ejemplo.mx/blog/slug"
}
```

Producto o servicio con precio visible: Product.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Nombre]",
  "description": "[Descripción visible]",
  "image": "https://ejemplo.mx/img/producto.jpg",
  "brand": { "@type": "Brand", "name": "[Marca]" },
  "offers": { "@type": "Offer", "price": "900", "priceCurrency": "MXN", "availability": "https://schema.org/InStock", "url": "https://ejemplo.mx/producto" }
}
```

Preguntas frecuentes visibles en la página: FAQPage.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "[Pregunta tal como aparece]", "acceptedAnswer": { "@type": "Answer", "text": "[Respuesta tal como aparece]" } }
  ]
}
```

Negocio con dirección física: LocalBusiness (o subtipo: Restaurant, Dentist, Store).

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Nombre]",
  "image": "https://ejemplo.mx/img/local.jpg",
  "url": "https://ejemplo.mx/",
  "telephone": "+52 55 0000 0000",
  "address": { "@type": "PostalAddress", "streetAddress": "[Calle y número]", "addressLocality": "[Ciudad]", "addressRegion": "[Estado]", "postalCode": "[CP]", "addressCountry": "MX" },
  "openingHoursSpecification": [ { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "18:00" } ]
}
```

## Idiomas (si aplica)

| URL es | URL en | hreflang |
|--------|--------|----------|
| / | /en/ | es-MX, en, x-default → / |
