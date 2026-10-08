---
name: global-audit
description: Cooper's umbrella routine. Runs web-lab's heavy analyses together — SEO/GEO (/audit-seo, Sullivan), accessibility (/qa, Beizer), the authorized offensive pass (/offensive, Mallory) and performance/Lighthouse (/qa against /build's budget), plus Schneier's security consolidation — over ONE shared repo-and-staging exploration, so no agent re-reads everything. Runs only on demand or as the mandatory pre-launch pass; triages away what does not apply with a one-line reason, but never skips the pre-launch security and offensive run. Consolidates every finding into one severity-ranked board in docs/06-qa/global-audit.md, citing each analysis's own output file — it consolidates and orders, it never invents severities. Modes: /global-audit (all that apply), /global-audit <names> (seo, a11y, security, offensive, perf), /global-audit status (re-read outputs, refresh the board, no re-run). Use when the user says "audit everything", "how is the site", "review it all before launch", or wants the heavy analyses run together.
---

# /global-audit · Cooper

The cheap way to review a project that already partly exists. Instead of running the SEO audit,
the accessibility pass, the offensive pentest and the performance check one by one — each
re-crawling the site, re-listing the repo, re-auditing the dependencies — `/global-audit` does
**one shared exploration** and feeds it to every analysis, then consolidates the results into a
single severity-ranked board.

This is a **cross-phase routine, not a phase role** — like `/security` and `/offensive`. Cooper
runs it (the orchestrator; a subagent cannot). It changes nothing by itself: each analysis keeps
its own owner, its own skill and its own output file; `/global-audit` **consolidates and orders,
it never invents findings or severities of its own**.

## When it runs

- **On demand**, when Yuno asks: "audit everything", "how is the site", "what's missing",
  "review it before launch", "I inherited this site".
- **As the mandatory pre-launch pass.** `CLAUDE.md`'s efficiency rule (item 7) defers the heavy
  sweeps between launches; the one place they are not optional is before a launch. At that point
  Cooper runs this routine, and the security and offensive parts are never skipped to save cost.

It is not run on every edit. A small change goes straight to its owning agent (`CLAUDE.md`,
"How you orchestrate", items 1 and 7).

## The analyses it covers

| Name | Owner | Skill / source | What it measures |
|------|-------|----------------|------------------|
| `seo` | Sullivan | [`/audit-seo`](../audit-seo/SKILL.md) | Technical/on-page SEO, structured data, Core Web Vitals, AI-search/GEO findability |
| `a11y` | Beizer | [`/qa`](../qa/SKILL.md) step 6.4 | Automated (axe) and manual (keyboard, screen reader) accessibility, WCAG 2.2 AA |
| `perf` | Beizer | [`/qa`](../qa/SKILL.md) step 6.5, against [`/build`](../build/SKILL.md)'s budget | Lighthouse and CrUX against LCP/INP/CLS/JS budget |
| `offensive` | Mallory | [`/offensive`](../offensive/SKILL.md) | Authorized adversarial pentest of the user's own staging, identity first |
| `security` | Schneier | [`/security`](../security/SKILL.md) | Consolidates the security QA (`/qa` 6.6) and Mallory's report into one verdict |

Accessibility rules are owned by `better-accessibility`, performance budget by `/build`, media
by `/optimize-assets`, security/privacy and the verdict by `/security` (`CLAUDE.md`, rule
ownership). This routine only schedules and consolidates them.

## Modes

| Command | What it does |
|---------|--------------|
| `/global-audit` | Every heavy analysis that the triage says applies, over one shared exploration |
| `/global-audit <names>` | Only the named ones · valid names: `seo`, `a11y`, `perf`, `offensive`, `security` |
| `/global-audit status` | Does not re-run anything: re-reads the existing output files, refreshes the board and says what is stale against the current staging/commit |

Models are set per analysis by `CLAUDE.md`'s model table and the ladder below, not by the mode.

## Who does what

| Phase | Agent | Role |
|-------|-------|------|
| 0 · Scope & triage | **Cooper** | Which analyses apply, which outputs are fresh, in what order to explore |
| 1 · Shared exploration | **Cooper** (delegates the scripted parts) | Runs each inventory command **once** and hands its output to every analysis |
| 2 · Analyses | each owner (Sullivan, Beizer ×2, Mallory, Schneier) | Each consumes the shared output instead of re-collecting it; produces its own file |
| 3 · Board | **Cooper** | Writes `docs/06-qa/global-audit.md` and makes one consolidated summary |

Respect the ladder (`docs/LADDER.md`): the roles do the work, Cooper consolidates, nobody edits
the team.

## Before you begin

Read if they exist: `docs/01-discovery/spec.md` and `threat-model.md`,
`docs/02-structure/flows.md` and `redirects.md`, `docs/03-content/seo.md`,
`docs/04-design/accessibility.md`, `docs/05-development/frontend.md` (budget, headers) and
`backend.md`, and any existing `docs/06-qa/` outputs plus a previous `global-audit.md`. These
are read **once, here**, and passed to the analyses, not re-read by each one.

## Phase 0 · Scope and triage (Cooper)

### Triage — what is needed, not only what applies

An analysis that is not needed is noise and cost. Decide one by one, with a one-line reason for
each skip, and **never skip the pre-launch security and offensive run**.

| Project state | Signals | seo | a11y | perf | offensive | security |
|---------------|---------|-----|------|------|-----------|----------|
| **No staging yet** | no `main` preview on Vercel, no live content | — nothing to crawl | — | — | — | — → say the routine ends here; come back when there is staging |
| **In construction** — staging exists, pre-launch | `main` preview with real content, not launched | on request | on request | on request | lighter scope if no accounts; **not skipped** before launch | on request / consolidates whatever ran |
| **Pre-launch** — mandatory pass | "I want to launch", QA underway | ✅ | ✅ | ✅ | ✅ (apps with accounts; lighter but present for static sites) | ✅ full verdict |
| **Static marketing site** — no accounts, no backend | spec classifies data as public/contact only | ✅ | ✅ | ✅ | **lighter scope** — no auth/IDOR/session surface to test; still run config/headers/CSP; **not skipped** before launch | ✅ |
| **Published / maintenance** | real users, live domain | on request | on request | ✅ with CrUX field data | ✅ periodically on staging that mirrors production | on request |

**Triage rules.**

- **A skip is stated, never silent.** Every skipped or lighter-scope analysis appears on the
  board with its one-line reason.
- **The user decides.** If Yuno asks for an analysis the triage skipped, Cooper says why in one
  sentence and runs it anyway if he insists.
- **Fresh beats needed.** If an analysis is needed but its output file is unchanged against the
  current staging/commit, it is reused, not re-run (that is what `status` checks).
- **Never skip the pre-launch security and offensive run** — no triage reason and no cost
  argument removes it. A static site gets a lighter offensive scope, not none.

### Exploration order

The order in which information is **collected** so the analyses have everything, not the order
findings are applied:

1. Page inventory / sitemap — the crawl every analysis needs.
2. Site-wide and header checks — SEO, perf and the offensive config pass all read these.
3. Rendered HTML per page — SEO and accessibility both read the same saved HTML.
4. Dependency and secret audit — security and offensive both read this.

Cooper announces the scope before starting, in the shape of:

> "Global audit on `<staging>` @ `a1b2c3d`. State: **pre-launch**. Running: seo, a11y, perf,
> offensive (full — the app has accounts), security consolidation. Skipping: none. Shared
> exploration runs once. Starting."

## Phase 1 · Shared exploration (done ONCE)

Several analyses ask the repo and the staging for the same things. Here each command runs
**once** and its output is passed to every consumer, so two analyses never produce two different
inventories of the same site. **Reuse the existing audit skills' scripts** — do not invent new
ones:

| Output | Produced once by | Consumed by |
|--------|------------------|-------------|
| Page inventory / sitemap (`inventory.json`) | [`skills/audit-seo/scripts/sitemap.py`](../audit-seo/scripts/sitemap.py) (identical to [`skills/audit-animations/scripts/sitemap.py`](../audit-animations/scripts/sitemap.py)) | `seo` step 1 · `a11y` template list · `perf` page list · `offensive` recon |
| Site-wide checks — `robots.txt`, AI crawlers, `sitemap.xml`, `llms.txt`, HTTPS/redirect, custom 404, favicon (`findings/site.json`) | [`skills/audit-seo/scripts/check_site.py`](../audit-seo/scripts/check_site.py) | `seo` step 2 · `offensive` config/headers/CSP (WSTG-CONF) |
| Staging crawl — internal links and codes, broken links, 404, 301 redirects without chains, metadata, robots, sitemap, HTTP→HTTPS, home security headers, sensitive paths (`.env`, `.git`, source maps) | [`skills/qa/scripts/crawl_check.py`](../qa/scripts/crawl_check.py) | `seo` and `perf` reuse the codes/metadata · `offensive` reuses headers and sensitive-path results instead of re-scanning |
| Rendered HTML per page saved to `pages/<slug>.html` | one browser pass (`/audit-seo` step 3 pattern: `navigate` + `javascript_tool`, batched) | `seo` per-page checks ([`check_page.py`](../audit-seo/scripts/check_page.py)) · `a11y` axe per template |
| Core Web Vitals / field data per key page | [`skills/audit-seo/scripts/pagespeed.py`](../audit-seo/scripts/pagespeed.py) (CrUX when available) | `seo` step 4 · `perf` field-data input alongside Lighthouse |
| Dependency and secret audit — `pnpm audit --audit-level=high`, `gitleaks detect` over all history (commands in [`skills/qa/references/security.md`](../qa/references/security.md)) | one run | `security` (6.6) · `offensive` dependency cross-check |

Each analysis **consumes this shared output and does not repeat it.** If a shared command cannot
run (password-protected staging, no PageSpeed quota, no CI), mark it pending once, here, the way
the owning skill would, and the board records it as "not verified — requires X" rather than
letting two analyses each hit the wall.

## Phase 2 · The analyses (each owner, consuming the shared output)

Each runs its own skill, but starts from the shared output instead of re-collecting it:

- **`seo`** → Sullivan, `/audit-seo` from step 2 onward (step 1 is already done). The scripted
  per-page checks run under `sonnet`; synthesizing the report and its verdict is `opus`
  (judgment). Writes `docs/06-qa/seo/report.md` (or the audit's own folder).
- **`a11y`** → Beizer, `/qa` step 6.4: axe over the saved rendered HTML, plus the manual
  keyboard/screen-reader script the user runs. `sonnet` for the automated pass, `opus` where
  findings need interface judgment. Writes `docs/06-qa/accessibility.md`.
- **`perf`** → Beizer, `/qa` step 6.5 against `/build`'s budget, reusing the CrUX field data
  already pulled; Lighthouse adds lab data. `sonnet`. Folds into `docs/06-qa/report.md`.
- **`offensive`** → Mallory, `/offensive`. **`opus`, always** (security judgment). Its Step 0
  rules-of-engagement gate is non-negotiable and runs in full even inside this routine — the
  shared exploration does not replace Yuno's authorization. Writes `docs/06-qa/offensive.md`.
- **`security`** → Schneier, `/security` step 6.9: reads Beizer's `docs/06-qa/security.md` and
  Mallory's `docs/06-qa/offensive.md`, rates with `skills/security/scripts/risk_rating.py`, and
  issues the verdict in `docs/06-qa/security-verdict.md`. **`opus`, always.** Schneier owns the
  verdict; this routine does not.

## Phase 3 · The board (Cooper)

Write `docs/06-qa/global-audit.md` — a **board, not a copy**. Findings live in each analysis's
own file; here go references, counts and the one consolidated summary. It consolidates and
orders; it does not invent severities (it reuses `/qa`'s severity scale: Blocker, Critical,
Major, Minor, Trivial, and Schneier's verdict). Cite each analysis's output file.

```markdown
# Global audit — [project] @ [commit]

> Staging: [URL]. Date: [yyyy-mm-dd]. Mode: full / [names].
> Ran: seo, a11y, perf, offensive, security. Skipped: [none / perf — no change since last pass].
> Shared exploration ran once.

## Board

| Analysis | Output file | Blocker | Critical | Major | Minor | Verdict |
|----------|-------------|---------|----------|-------|-------|---------|
| SEO/GEO | `docs/06-qa/seo/report.md` | 0 | 1 | 3 | 5 | — |
| Accessibility | `docs/06-qa/accessibility.md` | 0 | 1 | 2 | 4 | — |
| Performance | `docs/06-qa/report.md` | 0 | 0 | 2 | 1 | within budget / over |
| Offensive | `docs/06-qa/offensive.md` | 0 | 1 | 1 | 0 | input to Schneier |
| Security | `docs/06-qa/security-verdict.md` | — | — | — | — | **Schneier: Approved / with conditions / Blocked** |
| **Total** | | **0** | **3** | **8** | **10** | |

## Not verified
- [what could not be run, and the exact steps for the user — pending from the shared exploration]

## Next
- Blockers and criticals → back to the owning role via `/build` as tasks.
- Launch gate: Schneier's verdict above. A critical blocks the phase; a high blocks the launch.
```

Then **one** consolidated summary to the user, ten lines: counts by severity per analysis,
Schneier's verdict, what was skipped and why, and what is pending verification. No analysis shows
its own separate closing inside this routine.

## `/global-audit status`

Re-reads the existing output files, recomputes the board totals, and marks each analysis fresh or
stale against the current staging/commit (same freshness idea as `/update` and the audit skills).
It **re-runs nothing** and issues no new verdict. Use it to see where things stand after some
fixes without paying for a full re-audit.

## Before you finish

| Symptom | Fix |
|---------|-----|
| A scan or offensive test pointed at a host that is not Yuno's own staging | **stop** — own environments only, never production, never a third party (reuse `/offensive` Step 0 and `/qa`'s "own environments only" rule) |
| No signed rules of engagement for the offensive part | run `/offensive` Step 0 and get Checkpoint 0 before any active test — the shared exploration never substitutes for Yuno's authorization |
| Tempted to skip the offensive or security run to save cost before launch | **never** — the pre-launch security and offensive run is not optional; a static site gets a lighter offensive scope, not none |
| Invented a severity to rank findings across analyses | stop — consolidate the severities each analysis set; this routine does not create them |
| The same inventory ran twice for two analyses | collapse it into Phase 1; each command runs once and its output is shared |
| A verdict written here instead of by Schneier | Schneier owns the security verdict (`security-verdict.md`); this board only references it |
| Re-ran a fresh output | reuse it; only re-run what `status` marks stale against the current commit |
| An analysis the triage skipped, with no reason on the board | state the skip and its one-line reason, or run it |
