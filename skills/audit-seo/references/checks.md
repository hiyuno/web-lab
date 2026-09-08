# Checks and criteria

Every check cites its source script (matches `finding.source` in `findings/*.json`) so a
disagreement can be traced back to logic, not vibes.

## SEO clásico

| Check | Script | Criterio | Por qué |
|---|---|---|---|
| HTTPS + redirect | `check_site.check_https` | `https://` carga; `http://` responde 301/308 | Factor de ranking desde 2014; evita contenido duplicado por esquema |
| robots.txt existe | `check_site.check_robots` | 200 en `/robots.txt` | Sin él, no hay forma de declarar sitemap ni reglas por bot |
| sitemap.xml existe | `check_site.check_sitemap` | 200 + XML parseable en `/sitemap.xml` | Forma directa de decirle a Google qué indexar |
| 404 real | `check_site.check_404` | Una URL inventada responde 404, no 200 | Evita indexar URLs basura ("soft 404") |
| Favicon | `check_site.check_favicon` | `<link rel=icon>` o `/favicon.ico` responde 200 | Presencia básica de marca en pestañas/resultados |
| `<title>` | `check_page.title` | Existe, 15-65 caracteres | Señal on-page más fuerte; se muestra como encabezado del resultado |
| Meta description | `check_page.meta_description` | Existe, 70-175 caracteres | Snippet controlado en el resultado de búsqueda |
| Un solo H1 | `check_page.h1` | Exactamente un `<h1>` | Señal de jerarquía/tema principal |
| Canonical | `check_page.canonical` | `<link rel=canonical>` presente | Evita contenido duplicado por variantes de URL |
| `meta robots` | `check_page.meta_robots` | Sin `noindex` en páginas que deben indexarse | `noindex` saca la página de los resultados, sin excepción |
| `lang` | `check_page.lang` | `<html lang="...">` presente | Idioma explícito para buscadores y lectores de pantalla |
| Alt text | `check_page.alt_text` | Todo `<img>` tiene `alt` | SEO de imágenes + accesibilidad |
| Open Graph | `check_page.open_graph` | `og:title`, `og:description`, `og:image` presentes | Preview correcto al compartir en redes/mensajería |
| Schema.org / JSON-LD | `check_page.schema` | Al menos un bloque JSON-LD válido | Base técnica 2026 para rich results y para que motores de IA identifiquen la entidad |
| Core Web Vitals | `pagespeed.py` | LCP < 2.5s, INP < 200ms, CLS < 0.1 en datos de campo (CrUX, p75) | Factor de ranking directo desde 2021; sin datos de campo se marca **not_verified**, nunca se inventa con datos de laboratorio |

## GEO / AEO (visibilidad en motores de IA)

| Check | Script | Criterio | Por qué |
|---|---|---|---|
| robots.txt — bots de recuperación | `check_site.check_robots` | `OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User` no bloqueados | Estos bots citan en tiempo real; bloquearlos te saca de esas respuestas |
| robots.txt — bots de entrenamiento | `check_site.check_robots` | Informativo, no bloqueante: `GPTBot`, `anthropic-ai`, `ClaudeBot`, `CCBot`, `Bytespider`, `Google-Extended` | Decisión del usuario: permitir/entrenar es independiente de aparecer en respuestas en vivo |
| `llms.txt` | `check_site.check_llms_txt` | Presente en `/llms.txt` | Convención abierta (llmstxt.org, 2024); **ningún laboratorio grande confirma usarla en producción todavía** — se reporta como `low`/nice-to-have, nunca como bloqueante |
| Fecha visible | `check_page.freshness` | Fecha o palabra de actualización visible en el texto (no solo en schema) | Perplexity prioriza fuertemente contenido reciente; un LLM no puede citar una fecha que no ve |
| Bloque inicial citable | `check_page.citability` | Los primeros ~400 caracteres de texto visible tienen sustancia | Es lo que un LLM cita más fácil y textualmente al responder |

## Notas de calibración

- Todo lo que no se pudo confirmar (fetch fallido, rate limit, tráfico insuficiente para CrUX) se
  marca `status: not_verified` y **no cuenta para el veredicto** Blocked/Approved — nunca se
  reporta como si hubiera pasado ni como si hubiera fallado.
- El veredicto final es `Blocked` solo si queda algún hallazgo `critical` sin resolver;
  `Approved` en cualquier otro caso, dejando el resto como trabajo pendiente en la tabla (mismo
  método que el resto de web-lab, ver `CLAUDE.md` → Shared review method).
- Los hallazgos GEO/AEO son un área más nueva y menos determinista que el SEO clásico: el
  reporte nunca promete resultados ("vas a aparecer en ChatGPT"), solo describe condiciones
  necesarias documentadas por la industria a 2026.
