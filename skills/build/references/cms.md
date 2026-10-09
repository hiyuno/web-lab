# CMS integration · phase 5 · Osmani

When the architecture decision names a CMS, Osmani integrates it here. A CMS exists for one
reason only: **someone who does not code will edit content often**. If every change is a
developer editing a content collection or a brief, there is no CMS — the content lives in the
repo (Astro collections, MDX) and the "none" option stands. Add a CMS only when the owner, an
editor or a client will log in and change words, posts or pages on their own, repeatedly.

The **content model is Rosenfeld's** — fields, collections, who edits each one — defined in phase
3 (`skills/content`, the matrix and per-page briefs). You implement that model in the chosen CMS;
you do not invent fields. If the model is missing or thin, go back to `/content` before wiring
anything.

## Default by site type

Yuno's fixed decision. The team still picks per project and justifies it in
`architecture-decision.md`; the default is the starting point, not the only answer.

| Site type | Framework | CMS default | Alternatives |
|-----------|-----------|-------------|--------------|
| Content site | Astro 7 | **Keystatic** (git-based) | Sanity, when editors need a hosted studio and no repo |
| Web app | Next.js 16 | **Payload** (in our Postgres via Drizzle) | — |
| Either, no frequent non-coder editing | — | **none** — content in the repo | — |

Keystatic is the default for content sites because it keeps content in the repo as files, needs
no database and no third party, and every edit is a reviewable commit — the cheapest option that
respects the stack. Reach for Sanity only when a non-technical editor must work in a hosted studio
without touching GitHub, and accept that content then lives on Sanity's infrastructure (see
"Hosted vs. self-hosted"). Payload is the only CMS for apps, because it embeds in the Next.js app
and stores content in the same Postgres we already run through Drizzle — no new data home, no new
vendor.

## Decision table

| | Keystatic | Sanity | Payload |
|---|---|---|---|
| **Site type** | Content site (Astro) | Content site (Astro), hosted-studio need | Web app (Next.js) |
| **Where content lives** | Git repo, as Markdown / Markdoc / YAML / JSON — no DB | Sanity's hosted Content Lake (their infra) | Our own Postgres, via Drizzle (`@payloadcms/db-postgres`) |
| **Hosted / git / our-DB** | Git-based, self-contained in the repo | Hosted SaaS (free tier: hosting + bandwidth) | Self-hosted, inside our Next.js deployment |
| **Editor UI** | `/keystatic` route; local mode writes files on disk, GitHub mode commits via the GitHub API | Studio (open-source React SPA), hosted | `/admin` panel embedded in the app |
| **Editor roles / auth** | GitHub write access on the repo (GitHub mode); local mode has no auth | Sanity accounts and project roles | Collection / global / field / operation-level access control in code; its own auth |
| **Preview / draft** | Branch-based; drafts are commits/PRs; no built-in scheduling or approval workflow | Real-time drafts, live preview, GROQ | Drafts, versions and live preview built in |
| **Our stack fit** | Reads straight into Astro content collections; no new vendor, no DB | New vendor; content leaves our infra | Same Postgres + Drizzle we already use; no new data home |

## Hosted vs. self-hosted — be honest about where data goes

- **Keystatic**: content never leaves the repo. Git-based, no database, no third party in the
  critical path (Keystatic Cloud is optional and only adds hosted GitHub auth + asset handling).
  Lowest privacy surface.
- **Payload**: self-hosted in our own Next.js app and our own Postgres. Data stays on our infra.
  No new vendor boundary.
- **Sanity**: **hosted SaaS.** Content lives in Sanity's Content Lake, on their infrastructure —
  data leaves our infra. The public sources do not name a data-residency region, so if residency
  or the LFPDPPP/GDPR transfer basis matters, Schneier confirms it against Sanity's own docs
  before it is chosen, and it goes in the threat model's data inventory and the external-integration
  table (`architecture-decision.md`).

## Security and sanitization

CMS integration is a **new dependency and, for Sanity/Payload, a new data and auth surface**, so
it is a structural change: full phase-5 flow and **Schneier's gate** (`skills/security`). What he
looks at:

- **Who can edit, and how they authenticate.** Keystatic in GitHub mode = GitHub write access on
  the repo; local mode has no auth and is dev-only (never exposed in production). Sanity = Sanity
  project roles. Payload = its own auth and access control; configure it per the Better Auth /
  session rules where it shares the app's identity, and lock down collection, field and operation
  access so an editor cannot read or write beyond their role.
- **Rich-text / HTML rendering is the main injection risk.** A CMS rich-text or HTML field
  rendered with `dangerouslySetInnerHTML` (React) or `set:html` (Astro) is exactly the
  `dangerouslySetInnerHTML with CMS` finding in `skills/security/references/code-review.md`
  (§1 one-minute map grep, §3 Output encoding). External/CMS HTML goes through **DOMPurify** (or
  the framework's sanitizer) before rendering — never rendered raw. Prefer structured rendering
  over raw HTML: Markdoc/Markdown (Keystatic) and Portable Text (Sanity) render through typed
  components, not a raw HTML string; keep it that way instead of converting to an HTML blob.
- Editors are trusted-but-limited: even a trusted editor's input is sanitized on output, because
  an editor account can be compromised and a rich-text field is a stored-XSS vector.

## Performance and images

- **Build-time vs. runtime.** Keystatic content is files in the repo, read at build time — zero
  runtime CMS cost, fits Astro's zero-JS default. Sanity is fetched over its API (build-time for
  static pages, runtime for live content). Payload is queried server-side inside the Next.js app.
  Keep CMS reads on the server / at build; never ship a CMS client or its token to the browser.
- **Images stay optimized.** CMS-uploaded media still goes through **Bellard**
  (`skills/optimize-assets`) and is placed with correct `width`, `height`, `sizes`, `loading` and
  `fetchpriority` per the frontend track — an editor uploading a 4 MB photo must not blow the
  Lighthouse budget in `lighthouserc.json`. For Keystatic, uploads land in the repo's asset folder
  and Astro's `<Image>`/`<Picture>` processes them. For Payload, store uploads in external object
  storage (Vercel Blob / S3), not the ephemeral container disk, and serve them through an
  optimizer. The client handoff guide (`skills/launch/references/handoff.md`) tells non-coder
  editors to run images through Bellard's flow so they stay within budget.

## Sources

- [Keystatic & Astro — Astro docs](https://docs.astro.build/en/guides/cms/keystatic/)
- [Keystatic, git-based CMS — LinuxLinks](https://www.linuxlinks.com/keystatic-git-based-content-management-system/)
- [Payload Postgres adapter (Drizzle) — Payload docs](https://payloadcms.com/docs/v3/database/postgres)
- [Self-host Payload CMS with Postgres — Railway](https://docs.railway.com/guides/payload-cms)
- [Sanity — Content Lake and Studio — sanity-io on GitHub](https://github.com/sanity-io/sanity)
