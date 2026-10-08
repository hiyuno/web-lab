# Checks and criteria

Every check cites its source script (matches `finding.source` in `findings/*.json`) so a
disagreement traces back to logic, not vibes.

The title and meta-description numbers below are **not owned here** — they are the canonical
limits set by [`skills/seo`](../../seo/SKILL.md) ("Title and meta length"). This audit applies
them; if they change, they change there first. Same for the AI-crawler robots.txt policy
(`skills/seo` → "Robots.txt for AI crawlers") and the AEO/GEO checklist.

## Classic SEO

| Check | Script | Criterion | Why |
|---|---|---|---|
| HTTPS + redirect | `check_site.check_https` | `https://` loads; `http://` returns 301/308 | Ranking factor since 2014; avoids scheme-duplicate content |
| robots.txt exists | `check_site.check_robots` | 200 on `/robots.txt` | Without it there is no way to declare the sitemap or per-bot rules |
| sitemap.xml exists | `check_site.check_sitemap` | 200 + parseable XML at `/sitemap.xml` | The most direct way to tell Google what to index |
| Real 404 | `check_site.check_404` | A made-up URL returns 404, not 200 | Avoids indexing junk URLs ("soft 404") |
| Favicon | `check_site.check_favicon` | `<link rel=icon>` or `/favicon.ico` returns 200 | Basic brand presence in tabs/results |
| `<title>` | `check_page.title` | Present; target 50-60 chars (~600px); flagged outside 30-60 | Strongest on-page signal; shown as the result's heading. Google truncates ~600px and often rewrites long titles — the char count is a proxy for pixel width |
| Meta description | `check_page.meta_description` | Present; target 120-160 chars (~920px desktop); flagged outside 70-160 | Controls the snippet; below 70 wastes space, above 160 truncates. Front-load the key message in the first ~120 chars for mobile |
| Single H1 | `check_page.h1` | Exactly one `<h1>` | Main-topic/hierarchy signal |
| Canonical | `check_page.canonical` | `<link rel=canonical>` present | Avoids URL-variant duplicate content |
| `meta robots` | `check_page.meta_robots` | No `noindex` on pages that should be indexed | `noindex` removes the page from results, no exceptions |
| `lang` | `check_page.lang` | `<html lang="...">` present | Explicit language for engines and screen readers |
| Alt text | `check_page.alt_text` | Every `<img>` has `alt` | Image SEO + accessibility |
| Open Graph | `check_page.open_graph` | `og:title`, `og:description`, `og:image` present | Correct preview when shared on social/messaging |
| Schema.org / JSON-LD | `check_page.schema` | At least one valid JSON-LD block | 2026 technical baseline for rich results and for AI engines to identify the entity. Of the ~25 types Google renders, the ones that matter for a product/marketing site are Organization, WebSite, BreadcrumbList, Article, Product, LocalBusiness, SoftwareApplication — **FAQPage/HowTo rich results are retired** (HowTo 2023, FAQ effective May 2026): both stay valid Schema.org, harmless to keep, but do not add new ones expecting rich results |
| Core Web Vitals | `pagespeed.py` | LCP < 2.5s, INP < 200ms, CLS < 0.1 on field data (CrUX, p75) | Direct ranking factor since 2021; without field data it is marked **not_verified**, never faked with lab data |

## GEO / AEO (visibility in AI engines)

Framing from [`skills/seo`](../../seo/SKILL.md): for Google surfaces (AI Overviews, AI Mode)
Google states there is no special AEO technique — being crawlable, indexable and snippet-eligible
is the requirement, so classic SEO is most of the work. These checks cover the independent
AI-crawler access decision plus the content conditions that research associates with citation.

| Check | Script | Criterion | Why |
|---|---|---|---|
| robots.txt — retrieval bots | `check_site.check_robots` | `OAI-SearchBot`, `ChatGPT-User`, `Claude-SearchBot`, `Claude-User`, `PerplexityBot`, `Perplexity-User` not blocked | These bots fetch/cite in real time; blocking the search ones (OAI-SearchBot, Claude-SearchBot, PerplexityBot) removes you from those answers. The user-initiated ones (ChatGPT-User, Perplexity-User) often ignore robots.txt anyway |
| robots.txt — training bots | `check_site.check_robots` | Informational, non-blocking: `GPTBot`, `anthropic-ai`, `ClaudeBot`, `CCBot`, `Bytespider`, `Google-Extended` | User's decision: allowing training is independent of appearing in live answers. Note `Google-Extended` only controls Gemini training/grounding — it does **not** remove you from AI Overviews, which run off the ordinary Googlebot index |
| `llms.txt` | `check_site.check_llms_txt` | Present at `/llms.txt` | Open convention (llmstxt.org, 2024); **no major lab confirms using it in production** (Google's John Mueller: "no AI system currently uses llms.txt"); Ahrefs found ~97% of such files get zero AI-crawler requests — reported as `low`/nice-to-have, never a blocker |
| Visible date | `check_page.freshness` | A date or update word visible in the text (not only in schema) | Perplexity strongly prioritizes recent content; an LLM cannot cite a date it cannot see |
| Citable opening block | `check_page.citability` | The first ~400 chars of visible text have substance | Answer-first openings are what an LLM most readily lifts and attributes |

## Calibration notes

- Anything that could not be confirmed (failed fetch, rate limit, insufficient traffic for CrUX)
  is marked `status: not_verified` and **does not count** toward the Blocked/Approved verdict —
  never reported as a pass nor a fail.
- The final verdict is `Blocked` only if a `critical` finding remains unresolved; `Approved`
  otherwise, leaving the rest as pending work in the table (same method as the rest of web-lab,
  see `CLAUDE.md` → Shared review method).
- GEO/AEO findings are a newer, less deterministic area than classic SEO: the report never
  promises an outcome ("you will appear in ChatGPT"), only describes conditions documented by the
  industry as of 2026. The firmest guidance (Google's own) is that good classic SEO is the base;
  the strongest research-backed content levers (GEO paper, arXiv 2311.09735) are citing sources,
  including statistics and quoting experts, not keyword stuffing.
