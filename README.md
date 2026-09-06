# web-lab

Tools, roles and skills for building websites and apps with Claude Code, from a static site to
an application. Each utility lives in its own folder with everything it needs; skills are
installed by linking them into `~/.claude/skills`, roles into `~/.claude/agents`.

## Process

The eight phases for building a website, with checkpoints, architecture decision and minimum
standards, are in [`docs/PROCESS.md`](docs/PROCESS.md). Each skill in the repo covers one
phase.

## Roles

A team of subagents, one per phase of the process, plus a security role that reviews at the
close of every phase and can block a checkpoint. Claude Code acts as orchestrator following
[`CLAUDE.md`](CLAUDE.md); the security checklist is in [`docs/SECURITY.md`](docs/SECURITY.md).

| Phase | Role | Specialty |
|-------|------|-----------|
| 1 | [`cooper`](agents/cooper.md) | Discovery, spec, architecture decision, threat model |
| 2 and 3 | [`rosenfeld`](agents/rosenfeld.md) | Information architecture, content, SEO, redirects |
| 4 | [`frost`](agents/frost.md) | Design system, components, accessibility, prototype |
| 5 | [`osmani`](agents/osmani.md) | Frontend in Astro or Next.js, performance, CSP and headers |
| 5 | [`hopper`](agents/hopper.md) | Backend, data, auth and payments with providers. Applications only |
| 5 and 6 | [`bellard`](agents/bellard.md) | Images and video |
| 6 | [`beizer`](agents/beizer.md) | QA, accessibility, performance, security scanners |
| All | [`schneier`](agents/schneier.md) | Security and privacy. Gate at every phase, signs the launch. Skill `/security` |
| 7 and 8 | [`allspaw`](agents/allspaw.md) | Deployment, DNS, monitoring, backups, maintenance |

## Dependency: the `interfaces` collection

The roles load by name the domain skills from [jakubkrehel/skills](https://github.com/jakubkrehel/skills)
(Jakub Krehel, MIT), included as a submodule in `vendor/interfaces`: `better-accessibility`,
`better-layout`, `better-writing`, `better-typography`, `better-colors`, `better-ui`,
`better-interface`, `interface-review`, `explain-interface`, `break` and `variant`. Our skills
carry each phase's process; theirs carry interface knowledge, and each rule lives in one place
(ownership table in [`CLAUDE.md`](CLAUDE.md)). Frost's steps 4.1 and 4.8 are adaptations of
`variant` and `break`.

```bash
git submodule update --init            # first time
git submodule update --remote --merge  # pull the latest version
```

## Learning

Roles improve with every project. [`learnings/`](learnings/README.md) holds one file per role
that is read on start and fed by a retro at the close of each phase;
[`docs/PREFERENCES.md`](docs/PREFERENCES.md) holds the user's stable preferences that apply to
all. Whatever repeats three times is promoted to the role or the skill.

## Skills

### `/discovery` · Cooper

Phase 1. Starts a project from the idea, with no brief: interviews the user in seven short
rounds with checkpoints, researches the current site and competitors, and produces in the
project's `docs/01-discovery/` the brief, the architecture decision (Astro or Next.js), the
threat model with Schneier, the spec as source of truth and the phased plan.

- Skill: [`skills/discovery/SKILL.md`](skills/discovery/SKILL.md)
- Interview script: [`skills/discovery/references/interview.md`](skills/discovery/references/interview.md)
- Templates: `skills/discovery/references/` (brief, spec, decision, threat model, plan)

### `/structure` · Rosenfeld

Phase 2. With the approved spec, defines the structure: inventory and audit of the current site
if it is a redesign (`scripts/inventory.py`), flows per task, organization and labeling with card
sorting, sitemap with final URLs and navigation, 301 redirect map, low-fidelity wireframes per
template and validation with tree testing. All in `docs/02-structure/`.

- Skill: [`skills/structure/SKILL.md`](skills/structure/SKILL.md)
- Inventory: `skills/structure/scripts/inventory.py` (Python stdlib, no dependencies)
- Templates: `skills/structure/references/` (inventory, flows, organization, sitemap, redirects, wireframe, validation)

### `/content` · Rosenfeld

Phase 3. With the signed sitemap, produces the real content before design: voice and tone
guide, key messages with proof, a brief per page over the wireframes, concise and scannable
writing with microcopy, per-page SEO with JSON-LD per template, legal pages compliant with the
2025 Mexican data protection law reviewed by Schneier, asset list for Bellard and review with one
approver and two rounds. `scripts/content_matrix.py` generates the matrix and the empty briefs
from the sitemap. All in `docs/03-content/`.

- Skill: [`skills/content/SKILL.md`](skills/content/SKILL.md)
- Templates: `skills/content/references/` (editorial guide, messages, page brief, matrix, seo, legal, assets, review)

### `/design-system` · Frost

Phase 4. With the approved content, produces the visual direction, the three-tier tokens in W3C
DTCG format, the components with their nine states, the templates at three widths, WCAG 2.2 AA
accessibility as a system property, motion, the prototype in code and the design QA with
usability testing. `scripts/tokens_to_tailwind.py` converts the tokens to Tailwind v4's `@theme`
block with dark mode and verifies the contrast of every semantic pair in both modes. All in
`docs/04-design/`.

- Skill: [`skills/design-system/SKILL.md`](skills/design-system/SKILL.md)
- Style lab: `skills/design-system/app/` (Vite + React + DialKit + culori + apca-w3). `npm install && npm run dev`, then `http://localhost:8771`; or `preview_start name=style-lab` from the repo root. Pick an accent, tune shape, type, space and motion on ten real patterns, verify contrast live (WCAG and APCA) and export `tokens.tokens.json` and `tokens.css`. Headless: `npx tsx src/cli.ts --preset Playful --json tokens.tokens.json`.
- Base tokens: [`skills/design-system/references/tokens.tokens.json`](skills/design-system/references/tokens.tokens.json)
- Templates: `skills/design-system/references/` (visual direction, component, template, accessibility, motion, usability test, QA, variants, break)

### `/build` · Osmani and Hopper

Phase 5. With the approved design, builds the site or app in Astro 5 or Next.js 16: repo
foundation with TypeScript, Tailwind v4 and Frost's tokens, CI with tests, audit, secret
scanning and Lighthouse CI with a performance budget, tasks derived from the spec's stories
(`scripts/tasks_from_spec.py`), a per-task cycle with tests first and pull requests with preview.
Frontend track for Osmani and backend track for Hopper with the data access layer pattern:
`server-only`, Drizzle, Zod, per-resource authorization, signed webhooks.

- Skill: [`skills/build/SKILL.md`](skills/build/SKILL.md)
- Templates: `skills/build/references/` (task, definition of done, PR review, `lighthouserc.json`, `ci.yml`, headers and CSP for Astro and Next.js, structure, DAL, frontend, backend)

### `/qa` · Beizer

Phase 6. With staging on green CI, runs the test plan: one-pass staging crawl
(`scripts/crawl_check.py`: links, status codes, 404, 301 redirects without chains, metadata
against seo.md, robots, sitemap, HTTP to HTTPS, headers, sensitive paths), functional testing
with Playwright against the spec's criteria, accessibility with axe per template and state plus a
manual keyboard and screen reader script, Lighthouse against the budget, security scanning
(audit, gitleaks, OWASP ZAP, IDOR, rate limit), visual regression and device matrix, a report
with severities set before testing and exit criteria.

- Skill: [`skills/qa/SKILL.md`](skills/qa/SKILL.md)
- Playwright: `skills/qa/references/axe.fixture.ts` and `a11y.spec.ts` to copy into the project
- Templates: `skills/qa/references/` (plan, report, accessibility, security, exit criteria)

### `/launch` · Allspaw

Phases 7 and 8. With QA signed, prepares and runs the production launch as a 30-day window:
accounts and domain (2FA, lock, CAA, DNSSEC, DNS snapshot), domain email (SPF, DKIM, DMARC),
production on Vercel, monitoring with alerts to a person, tested backups and rollback, TTL and
cutover runbook with rollback deadlines, first-60-minutes verification ordered by cost of
failure, 30-day follow-up, and the maintenance plan with incident runbook and blameless
post-mortems.

- Skill: [`skills/launch/SKILL.md`](skills/launch/SKILL.md)
- Scripts: `domain_check.py` (NS, CAA, DNSSEC, MX, SPF, DKIM, DMARC, expirations, HSTS) and `launch_check.py` (production crawl reusing QA's plus old-URL continuity)
- Templates: `skills/launch/references/` (domain, checklist, cutover runbook, monitoring, incidents, post-mortem, maintenance)

### `/security` · Schneier

Cross-cutting across the eight phases. Sets the OWASP ASVS 5.0 level by data and impact, builds
the threat model (four questions, STRIDE per interaction, LINDDUN GO for privacy), reviews
design, reviews code by trust boundaries, interprets the security QA, signs the launch and
reviews access and secrets. Rates every finding with the OWASP risk rating methodology
(`scripts/risk_rating.py`), issues a verdict and keeps the accepted-risk register. Includes the
note on the Mexican data protection law in force since March 2025.

- Skill: [`skills/security/SKILL.md`](skills/security/SKILL.md)
- Templates: `skills/security/references/` (ASVS, threat model script, legal MX, design review, code review, risk, verdict, risk register)

### `/optimize-assets` · Bellard

Audit and optimization of images and video for a published site or a local folder. Pulls the
sitemap, inventories assets page by page with the browser, downloads them into a folder per
page, analyzes them (weight, dimensions vs. on-screen size, format, codec, bitrate) and starts a
local app on `localhost:8770` to convert them with one click: WebP, H.264 MP4, first-frame
covers, comparator, version history and configurable output folder.

- Skill: [`skills/optimize-assets/SKILL.md`](skills/optimize-assets/SKILL.md)
- Agent: [`agents/bellard.md`](agents/bellard.md), web media specialist
- App: `skills/optimize-assets/app/` (Python stdlib + Pillow + ffmpeg, no npm dependencies)
- Analysis thresholds: `skills/optimize-assets/references/thresholds.md`

Mac requirements: `python3` with Pillow, `ffmpeg`/`ffprobe` (`brew install ffmpeg`), and Node
with Playwright only for the optional responsive audit. The style lab needs Node 22 and npm.

## Install

```bash
git clone https://github.com/hiyuno/web-lab.git ~/Documents/GitSync/web-lab
for d in ~/Documents/GitSync/web-lab/skills/*/; do ln -sfn "${d%/}" ~/.claude/skills/; done
mkdir -p ~/.claude/agents && for f in ~/Documents/GitSync/web-lab/agents/*.md; do ln -sf "$f" ~/.claude/agents/; done
cd ~/Documents/GitSync/web-lab && git submodule update --init
for d in ~/Documents/GitSync/web-lab/vendor/interfaces/skills/*/; do ln -sfn "${d%/}" ~/.claude/skills/; done
```

With that, `/discovery`, `/structure`, `/content`, `/design-system`, `/build`, `/qa`, `/launch`,
`/security` and `/optimize-assets` appear in Claude Code along with the eleven `interfaces`
skills, and the nine roles are available as subagents.

## App tests

```bash
cd skills/optimize-assets/app && python3 -m unittest discover -s . -p 'test_*.py' -v
```
