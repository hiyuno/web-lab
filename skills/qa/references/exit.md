# Exit criteria · [project]

Date: [yyyy-mm-dd] · Author: Beizer · Set in the plan, before testing.

## To close phase 6

- [ ] Zero open blocker and critical findings
- [ ] Majors: fixed and retested, or accepted by the user in writing in `report.md`
- [ ] Every acceptance criterion of must stories covered by a passing test
- [ ] Playwright green on Chromium, Firefox and WebKit, desktop and 375
- [ ] Crawl: no broken links, 404 with a 404 code, 301 redirects without chains, robots and sitemap correct
- [ ] Forms: submission confirmed at the destination and email received
- [ ] Analytics: loads once, conversions fire once, respects consent
- [ ] Accessibility: axe without violations on every template and mode; manual keyboard and reader walkthrough done with no criticals
- [ ] Performance: mobile Lighthouse ≥ 90; LCP ≤ 2.5 s, CLS ≤ 0.1, TBT ≤ 200 ms on home and conversion; initial JS ≤ 150 KB
- [ ] Security: audit without highs, gitleaks clean, complete headers, ZAP without highs, auth tests without failures
- [ ] Baseline screenshots saved for visual regression
- [ ] Every bug found by hand has its automated test
- [ ] Schneier's verdict: approved or with written conditions
- [ ] User checkpoint approved

## Risk acceptances

| Finding | Severity | Reason to launch like this | Who accepts | Date | When it gets fixed |
|---------|----------|----------------------------|-------------|------|--------------------|
| | | | | | |

## Signatures

Beizer: [date] · Schneier: [verdict, date] · User: [approved, date]
