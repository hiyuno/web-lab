# Redirect map · [project]

Date: [yyyy-mm-dd] · Author: Rosenfeld · Converted to the hosting's format in phase 7 (Allspaw)

Rules: one row per current URL that changes. One to one toward the closest page. Never en masse
to the home. No chains. All 301. Internal links on the new site point to the new URL.

| Current URL | Target URL | Type | Reason | Traffic 90d | Rankings | Backlinks | Owner | Tested |
|-------------|------------|------|--------|-------------|----------|-----------|-------|--------|
| /old | /new | 301 | merge / rename / remove | | | | | [ ] |

## Patterns (if many URLs share a shape)

| Current pattern | Target pattern | Example |
|-----------------|----------------|---------|
| /blog/2023/:slug | /blog/:slug | /blog/2023/hello → /blog/hello |

## URLs kept unchanged

[ ] (no redirect needed; listed to verify they still return 200 after launch)

## Post-launch verification (Allspaw and Beizer)

- [ ] Every row returns 301 to its target and the target returns 200.
- [ ] No chain longer than one hop.
- [ ] New-site crawl with no internal links to old URLs.
- [ ] Search Console with no new coverage errors at 7 and 30 days.
