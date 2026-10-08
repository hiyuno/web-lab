# AEO / GEO and robots.txt for AI crawlers

Answer Engine Optimization (AEO) and Generative Engine Optimization (GEO) are about being
**cited** by AI answer engines — ChatGPT, Perplexity, Google AI Overviews and AI Mode, Microsoft
Copilot, Claude — not just ranked by Google. Honest framing: classic SEO has decades of controlled
testing behind it; AEO/GEO does not. The firmest facts here are the **crawler tokens**; most "how
to get cited" tactics rest on a couple of papers plus reasoning. Flag established vs. speculative
when you report, and never guarantee placement.

## What the engines actually say (established)

- **Google** is explicit that no special AEO technique is needed: a page is eligible for AI
  Overviews / AI Mode if it is simply indexed and snippet-eligible. No `llms.txt`, no AI-specific
  schema, no artificial "AI chunks." For Google surfaces, **AEO ≈ good classic SEO** — the AI
  layer reads the same index Googlebot builds. (developers.google.com/search/docs/appearance/ai-features)
- Implication: get the classic baseline right first (crawlable, server-rendered HTML, indexable,
  fast, useful). Content that only exists after client-side hydration is invisible to the many AI
  crawlers that do not run JavaScript — server-rendered HTML matters more in 2026, not less.

## Content levers with research behind them

From the original GEO paper (Princeton et al., arXiv 2311.09735, KDD 2024), which ran controlled
tests: the biggest levers are **content-side, not technical** —

- **Cite authoritative sources**, **include statistics**, **quote experts**. These raised a
  source's visibility in generated answers by up to ~40% in the study. Keyword stuffing did not
  help.
- **Answer-first / inverted pyramid**: lead with a direct, self-contained answer, then elaborate.
  Sound for extractability; a writing habit, not a proven ranking lever.
- **Extractable, self-contained passages**; **question-based headings** that match natural-language
  queries; **entity clarity** (name the entity, don't lean on pronouns/context).
- **Freshness** for time-sensitive queries — and a **visible** date, not only `dateModified` in
  schema (an engine can't cite a date it can't read; Perplexity weights recency heavily).
- **Third-party authority**: citations are concentrated (one analysis put Wikipedia at ~7.8% of
  all ChatGPT citations). Being referenced by Wikipedia, Reddit, established publications and
  structured directories often beats micro-optimizing your own page.

Schema's role in AEO is **contested**: controlled tests (Ahrefs, ~1,885 pages) found adding
JSON-LD made no reliable difference to AI citations, and Google says no AI-specific schema is
needed. Keep schema for rich results and entity clarity, not as an AI-citation lever.

## Robots.txt for AI crawlers

Three independent jobs: **training**, **search/citation indexing**, **live user-initiated
retrieval**. Blocking a training bot does not block the search/citation bot, and vice versa —
decide each deliberately. Re-verify tokens periodically; this landscape shifts.

| Vendor | Token | Job | Honors robots.txt? | Note |
|--------|-------|-----|--------------------|------|
| OpenAI | `GPTBot` | Training | Yes | Block to opt out of model training |
| OpenAI | `OAI-SearchBot` | Search / citation (ChatGPT search) | Yes | **Allow to be cited in ChatGPT.** Independent of `GPTBot` |
| OpenAI | `ChatGPT-User` | User-initiated fetch | Often not (user action) | Not used for search inclusion |
| Anthropic | `ClaudeBot` | Training | Yes | Add per subdomain; supports `Crawl-delay` |
| Anthropic | `Claude-SearchBot` | Search indexing | Yes | Blocking reduces appearance in Anthropic search results |
| Anthropic | `Claude-User` | User-initiated fetch | Yes | Blocking may reduce visibility for user-directed web search |
| Perplexity | `PerplexityBot` | Search / citation | Yes | **Allow to be cited in Perplexity.** Not used for training |
| Perplexity | `Perplexity-User` | User-initiated fetch | Generally no (user action) | — |
| Google | `Googlebot` | The index that feeds Search **and** AI Overviews / AI Mode | Yes | Blocking removes you from Search and all AI features built on it |
| Google | `Google-Extended` | Control token for Gemini **training/grounding** | Yes (as a control) | Does **not** affect Search ranking and does **not** remove you from AI Overviews |
| Microsoft | `Bingbot` | Bing index, which grounds consumer Copilot | Yes | Bing indexing health is the Copilot lever; no separate confirmed public Copilot crawler |

Legacy `anthropic-ai` / `Claude-Web`: not in Anthropic's current docs — treat as
deprecated/unconfirmed. Page-level generative controls exist too: `nosnippet`, `max-snippet`,
`data-nosnippet` (Google), `NOCACHE`/`NOARCHIVE` (Bing).

**Citation levers, one line:** allow `OAI-SearchBot`, `PerplexityBot`, `Claude-SearchBot` +
`Claude-User`, `Googlebot`, `Bingbot`. You can block the pure training bots (`GPTBot`, `ClaudeBot`,
`Google-Extended`) without losing citation eligibility.

## llms.txt — honest status

A proposed standard (llmstxt.org, Sept 2024): a Markdown file at `/llms.txt` giving an assistant
already on your site a curated map of your key pages. It is a content-curation aid, **not** an
access control.

- **No major lab confirms honoring it.** Google's John Mueller compared it to the long-ignored
  keywords meta tag ("no AI system currently uses llms.txt"); OpenAI, Anthropic and Perplexity
  have no public statement confirming use. An Ahrefs analysis (~137k domains) found ~97% of such
  files received zero AI-crawler requests.
- **Verdict:** cheap to publish, possibly marginal help for agents already navigating your docs,
  but never rely on it for discovery or citation and never report its absence above a `low`. It is
  no substitute for being crawlable and indexable by the bots above.

## Sources

Google AI features (developers.google.com/search/docs/appearance/ai-features); OpenAI crawlers
(developers.openai.com/docs/gptbot); Anthropic ClaudeBot (support.claude.com, article 8896518);
Perplexity bots (docs.perplexity.ai/guides/bots); Google crawler list
(developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers); GEO paper
(arxiv.org/abs/2311.09735); AI Overview citation study (arxiv.org/pdf/2509.14436v1); llms.txt
(llmstxt.org) and Mueller's skepticism (searchenginejournal.com/google-llms-txt-comparable-keywords-meta-tag/544804/).
Vendor positions change fast — re-verify before relying in production.
