# Framer-specific fixes

Framer gives a good baseline (clean URLs, automatic sitemap, per-page meta, Open Graph, SSL,
optimized images) but limits fine technical control below the Enterprise plan. This reference
gives the exact fix per finding type instead of a generic instruction that does not apply on the
platform.

## Per-page meta tags (title, description, OG)

Site Settings → pages → select the page → **SEO** panel on the right side. Each page has its own
title, description and Open Graph image fields; no code needed.

## `<html lang>`

Site Settings → **General** → Language. If the site is genuinely multilingual (not just the
attribute), Framer does not support native hreflang below Enterprise: document it as a known
limitation, not as something the user "forgot" to configure.

## JSON-LD / schema.org

Framer has no UI for schema. Add it as **Custom Code** → "End of `<head>` tag" (site-wide for
`Organization`, or per page for `Article`/`Product`/`SoftwareApplication`):

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "SITE_NAME",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": ["https://instagram.com/...", "https://linkedin.com/company/..."]
}
</script>
```

Always validate with Google's Rich Results Test before marking the finding resolved — a JSON-LD
block with invalid syntax is silently ignored. Do not reach for `FAQPage`/`HowTo` expecting rich
results: Google retired those (HowTo 2023, FAQ effective May 2026).

## robots.txt

Framer generates `/robots.txt` automatically and it is **not editable** below Enterprise. If the
audit finds it blocks AI retrieval bots (`OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`,
`PerplexityBot`...), that is a platform limitation: document it as such and, if it genuinely
matters for the project, the option is to evaluate the Enterprise plan or move the site. There is
no workaround on the standard plan.

## llms.txt

No dedicated UI. Serve it as a static file if Framer allows it on the project, or via a page's
Custom Code at the path `/llms.txt` if the hosting supports it; if neither is viable, mark it
"not applicable on this plan" rather than leaving it pending indefinitely.

## Favicon

Site Settings → **General** → Icon.

## Custom 404

Edit the project's `404` page like any other; Framer already serves it with a correct 404 status,
so if the audit reports a soft-404 it is usually because the page tested actually exists (false
positive) or because there is a redirect misconfigured to the home.

## Core Web Vitals

With no JS bundle control or own image pipeline: image and video weight optimization lives in the
`optimize-assets` skill (Bellard), not here. If Core Web Vitals fail because of media weight,
refer there instead of duplicating the work.
