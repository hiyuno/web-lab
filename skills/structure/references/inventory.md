# Inventory and audit of the current site · [project]

Date: [yyyy-mm-dd] · Author: Rosenfeld · Source: `inventory.py` over `pages.json` + user data

Baseline of the redesign. Every URL not kept as is needs a row in `redirects.md`.

## Summary

| Metric | Value |
|--------|-------|
| URLs found | |
| Status other than 200 | |
| Without title or meta description | |
| Without H1 or with more than one | |
| With traffic in the last 90 days | |
| With backlinks | |
| With forms | |

## Decisions per URL

Decision: **keep** (same URL, same content), **improve** (same URL, content rewritten in phase
3), **merge into <url>**, **remove**. The last three generate a redirect.

| url | status | title | h1 | words | forms | fields | traffic 90d | rankings | backlinks | decision | target | note |
|-----|--------|-------|----|-------|-------|--------|-------------|----------|-----------|----------|--------|------|
| | | | | | | | | | | | | |

## Findings

- Orphan pages (no internal links to them): [ ]
- Duplicates or near-duplicates: [ ]
- Forms that ask for more than needed: [ ] → Schneier
- Outdated or legally required content that is missing: [ ]
- Current stack signals (CMS, builder, framework): [ ]
