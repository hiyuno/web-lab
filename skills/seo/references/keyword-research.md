# Keyword / query research — the repeatable method

A concrete loop, free-first. Paid SaaS (Ahrefs, Semrush) only adds absolute volume and keyword
difficulty; everything below works without it. Run it in phase 3 to assign a primary and a
secondary keyword per page into `content`'s `seo.md`, and again after launch from real Search
Console data (that is where the best queries actually come from).

Output is always a small spreadsheet: `keyword · source · intent · trend · current rank · target
page`. Intent is one of informational, commercial, transactional, navigational — it decides which
template the query belongs on.

## Step 1 · Autocomplete mining

Type each seed topic into Google (and Bing) and read the 4–8 suggestions **without hitting enter**.
Branch by appending letters (a–z) and modifiers ("best", "how", "vs", "for", "near me"). Use a
private window, and check both mobile and desktop — suggestions differ. These are real, current
queries.

## Step 2 · People Also Ask + related searches

Search the main term; expand two or three PAA boxes (new questions keep spawning) and collect
15–20 questions in a few minutes. Grab the 8 "related searches" at the bottom of the page. Each
question is a candidate H2 or a candidate page.

## Step 3 · Google Trends

Enter the candidates and compare them. Trends gives **relative direction and seasonality, not
absolute volume** — prefer rising or stable lines over declining ones, read "related queries"
(breakout vs. top) for fresh terms, and filter by region.

## Step 4 · Search Console — the biggest free win (live sites only)

Performance report → Queries, sorted by **impressions**. Two gold mines:

- Queries where the site ranks around **position 8–15** with impressions but few clicks — usually
  a quick win from a better title or more depth, not a new page.
- Filter by page to see which queries each URL already earns, and whether it matches the intent
  you assigned.

On a redesign or refresh this is the first place to look, before inventing keywords.

## Step 5 · Bing Webmaster Tools

The free Keyword Research tool gives **actual volume estimates** (unlike Trends) and sources data
differently from Google — a good free cross-check. Bing's index also grounds Microsoft Copilot, so
it doubles as an AI-surface signal.

## Step 6 · Optional paid / free-tier

Google **Keyword Planner** gives volume ranges but needs billing info on the account (no charge
without ads). Free tiers exist for Ahrefs' Free Keyword Generator, Semrush (limited searches) and
AnswerThePublic. Paid Ahrefs/Semrush add true volume, keyword difficulty and competitor gap
analysis — optional, not required.

## Step 7 · Organize and prioritize

Fill the spreadsheet. Prioritize: rising terms the site already gets impressions for (the GSC
quick wins), then build or strengthen pages around the strongest question clusters. One primary
keyword per page, assigned to a specific URL and template; secondaries become H2s. Hand the result
to `content`'s `seo.md`.

Sources: Google Search Console Performance report; Google autocomplete and People Also Ask; Google
Trends; Bing Webmaster Tools. Vendor consensus on the workflow; the GSC step requires a verified
live site.
