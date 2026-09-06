# Per-page SEO · [project]

Date: [yyyy-mm-dd] · Author: Rosenfeld · Implemented by Osmani in phase 5; validated by Beizer in phase 6.

## Per-page table

| URL | Title (50-60) | Meta description (120-160) | H1 | Keyword | Canonical | Schema | OG image |
|-----|---------------|----------------------------|----|---------|-----------|--------|----------|
| / | | | | | / | Organization, WebSite | og/home.jpg |

## Rules

- Unique title per page, keyword first, brand last if it fits: "Keyword · Brand".
- Meta description with a call to action. It does not affect ranking; it affects the click.
- One H1 per page. H2s as the questions the reader would ask. No level skipping.
- Internal links pillar ↔ satellites with descriptive anchors. No orphan page.
- Canonical on all. `hreflang` if there are languages. `robots` only to exclude legal or thank-you pages if decided.
- Open Graph: `og:title`, `og:description`, `og:image` (1200 × 630), `og:type`, `og:url`. Twitter card `summary_large_image`.
- JSON-LD only with data visible on the page. Validate in phase 6 with Google's rich results test.

## JSON-LD per template

Home: Organization + WebSite.

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://example.mx/#org",
      "name": "[Legal name or brand]",
      "url": "https://example.mx/",
      "logo": "https://example.mx/logo.png",
      "contactPoint": { "@type": "ContactPoint", "email": "hello@example.mx", "contactType": "customer service" },
      "sameAs": ["https://www.instagram.com/example"]
    },
    {
      "@type": "WebSite",
      "@id": "https://example.mx/#site",
      "url": "https://example.mx/",
      "name": "[Site name]",
      "publisher": { "@id": "https://example.mx/#org" },
      "inLanguage": "es-MX"
    }
  ]
}
```

Interior with more than one level: BreadcrumbList.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://example.mx/" },
    { "@type": "ListItem", "position": 2, "name": "[Section]", "item": "https://example.mx/section" },
    { "@type": "ListItem", "position": 3, "name": "[Page]" }
  ]
}
```

Article or blog post: Article.

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[H1]",
  "description": "[meta description]",
  "image": "https://example.mx/og/article.jpg",
  "author": { "@type": "Person", "name": "[Name]", "url": "https://example.mx/about" },
  "publisher": { "@id": "https://example.mx/#org" },
  "datePublished": "2026-09-05",
  "dateModified": "2026-09-05",
  "mainEntityOfPage": "https://example.mx/blog/slug"
}
```

Product or service with a visible price: Product.

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Name]",
  "description": "[Visible description]",
  "image": "https://example.mx/img/product.jpg",
  "brand": { "@type": "Brand", "name": "[Brand]" },
  "offers": { "@type": "Offer", "price": "900", "priceCurrency": "MXN", "availability": "https://schema.org/InStock", "url": "https://example.mx/product" }
}
```

Frequently asked questions visible on the page: FAQPage.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "[Question as it appears]", "acceptedAnswer": { "@type": "Answer", "text": "[Answer as it appears]" } }
  ]
}
```

Business with a physical address: LocalBusiness (or a subtype: Restaurant, Dentist, Store).

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Name]",
  "image": "https://example.mx/img/venue.jpg",
  "url": "https://example.mx/",
  "telephone": "+52 55 0000 0000",
  "address": { "@type": "PostalAddress", "streetAddress": "[Street and number]", "addressLocality": "[City]", "addressRegion": "[State]", "postalCode": "[ZIP]", "addressCountry": "MX" },
  "openingHoursSpecification": [ { "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday"], "opens": "09:00", "closes": "18:00" } ]
}
```

## Languages (if applicable)

| URL es | URL en | hreflang |
|--------|--------|----------|
| / | /en/ | es-MX, en, x-default → / |
