# Client handoff · editor guide

A short guide for a **non-coder owner or editor** who will keep the content fresh after launch.
Deliver it only when such a person exists and will self-edit; if the owner is technical or every
change will keep coming through the team, skip it with a one-line reason (efficiency —
`CLAUDE.md`, item 7). It is a close-of-project deliverable, written once at launch, not a
per-change artefact.

Cooper assembles it with the team: **Osmani** fills the CMS specifics (where to log in, how
publish works for the chosen CMS — `skills/build/references/cms.md`), **Rosenfeld** the content
model (which fields and collections exist, who owns each — `skills/content`), and **Bellard** the
image step (`skills/optimize-assets`). It is delivered to `docs/08-maintenance/handoff.md`, next
to the maintenance plan the editor will live alongside.

Fill every `[bracket]`; leave none abstract. Write it in the user's language.

---

## Editing [site name]

### How to log in

- Where: `[CMS admin URL — e.g. /keystatic, the Sanity studio URL, or /admin]`
- How: `[GitHub account with write access / your Sanity account / your Payload login]`
- 2FA: `[on — use an app or a key, not SMS]`
- Who to contact if you cannot get in: `[name · channel]`

### How to edit content

- The pages and fields you can change: `[list the collections and fields from Rosenfeld's model]`
- What each field is for and its limits: `[e.g. title 50–60 chars, summary 120–160, one H1]`
- How to save a draft vs. make it live: `[CMS-specific — commit/PR, publish button, etc.]`
- How changes reach the live site: `[auto-deploy on publish / PR merge / the team deploys]`

### How to publish

1. `[step]`
2. `[step]`
3. Check the live page after `[N minutes]` at `[URL]`.

### Uploading images

Images must stay optimized or the site slows down and the performance budget breaks. Do not
upload straight from a phone or camera.

1. Run the image through `[Bellard's optimize-assets flow / the agreed tool]` first.
2. Target: `[format — WebP · max dimensions · max weight]`.
3. Always fill the **alt text** (what the image shows, for screen readers and SEO); leave it empty
   only for purely decorative images.
4. Upload where: `[CMS media field / repo asset folder / object storage]`.

### What NOT to touch

- Code, configuration files, build settings.
- Secrets, API keys, tokens, environment variables, `.env` files.
- DNS, the domain, email settings.
- User accounts, roles or access settings (unless that is explicitly your job).
- Anything you did not create and do not recognise — ask first.

If something looks broken after you edit, do not try to fix the code: contact the team and, if
there is one, use the rollback.

### Who to contact

- Content questions: `[name · channel]`
- Something is broken / the site is down: `[name · channel]` (see the incident runbook,
  `docs/08-maintenance/incidents.md`)
- Billing / domain / accounts: `[name · channel]`
