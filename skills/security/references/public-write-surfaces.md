# Public-write surfaces · review checklist

A **public-write surface** is any page where a visitor writes content that other visitors read:
a feature-request and voting forum, comments, reviews, a guestbook, a public profile bio. The
visitor is anonymous *to the page* and authenticated *to the action*: anyone can read, only an
account can write. That asymmetry is where the findings live.

Written for the forum in `skills/app-web/SKILL.md`, built in-house on the app's own auth, with
votes deduplicated by a database unique constraint on `(request, voter)`, new requests and
comments landing in a pending state before they are public, and rate limiting on create, comment
and vote (`skills/build/references/forum.md`). Those decisions are settled: you review **against**
them, you do not reopen them. The same checklist applies to any later public-write feature.

Use it in S.2 (the surface appears in the sitemap and the wireframes), in S.3 (the code exists)
and in S.4 (QA reports on it). Not a replacement for `code-review.md`: an addition for this
surface.

## 1 · Threat categories

STRIDE letter and LINDDUN family in the third column, so the rows land in `threat-model.md`
without rewriting them.

| Category | What it looks like | S/L |
|----------|--------------------|-----|
| Bulk posting | A script opens accounts and posts requests or comments in a loop; the queue fills with spam and the owner stops reading it, which is the real damage | D |
| Vote manipulation · per account | The same account votes twice on a request, by double-submit, by replaying the request, or by racing two concurrent calls | T |
| Vote manipulation · sybil | One person, several accounts, one vote each. The `(request, voter)` unique constraint stops the first case at the database and does nothing here: every vote is valid on its own | T |
| Personal data in free text | Someone pastes their phone number, their email, a client's name or a colleague's into a request or a comment, and it becomes public and indexable. Their obligations as controller follow the data, not the intent: see `legal-mx.md` | I · Identifiability, Disclosure |
| Harassment and abusive content | The surface carries someone else's name; the target has no way to report it and the owner no way to remove it fast | I |
| IDOR on content ids | `PATCH /requests/42`, `DELETE /comments/17`, `POST /requests/42/vote` with someone else's id: can an account edit, delete or vote as another? Sequential ids make this a two-minute attack | E |
| Stored XSS | Body, title, display name or a link's `href` rendered back to every other visitor. One stored payload runs in the owner's admin session, which is the account that can delete anything | T · E |
| Metadata leaks | The public list exposes the voter's email, the author's internal id, an unpublished pending item, or the vote count of a moderated-away request | I · Linkability |

**Sybil, proportionately.** This is a solo owner's forum, not a marketplace. The proportionate
control set is: an account required and its email verified before the first vote, a rate limit
per account and per IP on create, comment and vote, and one query the owner can run when a
request's count looks wrong — votes on that request grouped by account creation date. Ten
accounts created within an hour, all voting on the same request, is visible in one screen. A
device-fingerprinting or fraud-scoring pipeline is not proportionate here and you do not ask for
one; the ranking is advisory input to the owner's roadmap, not a payout.

## 2 · What counts as a critical here

Same bar and same "serious on sight" reading as the escalation triggers in `CLAUDE.md`: found,
it blocks, whatever the deadline says. These extend that list for this surface.

- a write path reachable without the auth check — an API route, a server action or a form
  endpoint that creates, edits or votes for an unauthenticated caller;
- votes deduplicated in application code only, with no unique constraint on `(request, voter)`
  in a migration;
- user-generated content rendered without output encoding — `dangerouslySetInnerHTML`,
  `set:html`, or an unvalidated `href` or `src` built from a field;
- content publicly visible without passing the moderation gate — a create path that writes
  `published` directly, or a public query that does not filter by state;
- a write action with no rate limit: create, comment, vote, edit;
- an owner-only action reachable without an authorization check — status change, merge, pin,
  delete, moderate — including one hidden only by not rendering the button.

Everything else on this surface is rated with `risk_rating.py` like any other finding. Typical
calibration, so two forums get the same grade: an anonymous write path is `--size 9`, an
authenticated-user abuse is `--size 6`; guessable sequential ids are `--discovery 7 --exploit 5`;
personal data in a public free-text field is `--privacy 3` for one person and `--confidentiality
6` when the field is indexed by search engines; a spam flood is impact on `--availability`, not
on confidentiality, and rarely reaches high on its own.

## 3 · Verification checklist

Each row is something you check against code, a migration or a config file, and each carries its
evidence into the verdict. What you could not check is **Not verified**, never a pass.

Auth and authorization

- [ ] Every create, comment, vote, edit and delete path re-verifies the session **server-side**
      in the action or route, not only in the page that renders the form
- [ ] The public list and detail queries live in `src/data/**` with `import 'server-only'`
- [ ] Edit and delete authorize by ownership **in the query** (`where id = ? and author = ?`),
      not by fetching then comparing
- [ ] Owner-only actions check the role on the server; hiding the control is not the check
- [ ] Requesting another account's request or comment id returns the same response as one that
      does not exist

Votes

- [ ] A migration contains a unique constraint or unique index on `(request, voter)`; grep the
      `drizzle/` SQL, not the schema file's intent
- [ ] The vote handler is idempotent: the duplicate-key error is caught and answered as
      "already voted", not as a 500 with a database message
- [ ] Un-voting deletes only the caller's own row
- [ ] The vote count shown is derived from the rows, not from a counter column the app
      increments and could desynchronize
- [ ] Two concurrent vote calls from one account leave one row (transaction or the constraint,
      demonstrated by a test)

Moderation gate

- [ ] The default state at insert is the pending one, set in the schema default, not passed in
      by the caller
- [ ] The state field is not settable from the create or edit payload — check the Zod schema
      omits it
- [ ] Every public read path filters by the published state, including RSS, sitemap, search,
      the API and any JSON-LD
- [ ] Moderation and status transitions are logged with actor id and timestamp
- [ ] A report or contact route exists for abusive content and reaches a person

Output and input

- [ ] Free-text fields render through JSX/Astro escaping; any HTML path goes through DOMPurify
      with an allowlist, and the allowlist is in the repo
- [ ] Links written by users get `rel="nofollow ugc noopener noreferrer"`; `href` schemes are
      allowlisted (`http`, `https`, `mailto`), so `javascript:` and `data:` cannot be stored
- [ ] Markdown, if any, is rendered with raw HTML disabled
- [ ] Length limits on title, body and display name, enforced by Zod and by the column type
- [ ] The display name shown publicly is a chosen name, never the account email

Rate limiting and abuse

- [ ] A limit exists per account and per IP on create, comment and vote, with the values written
      down in `backend.md`'s routes table
- [ ] Exceeding it returns 429 with a message that says when to retry, and is logged
- [ ] The limiter is enforced server-side and survives a page reload (store, not memory, on
      serverless)

Privacy

- [ ] The form's short notice says the text will be public and asks not to include third
      parties' personal data
- [ ] Voter identities are not exposed in the public payload; check the DTO, not the UI
- [ ] Author deletion or account deletion has a defined outcome for their content, written in
      the privacy notice
- [ ] IPs kept for rate limiting have a retention period and are not returned to any client
- [ ] The privacy notice lists this surface's data among what is processed

## 4 · Accepted risk, proportionate to a solo owner

Fixed regardless of scale, never a register row: anything in section 2. Unencoded output, a
missing authorization check and an unauthenticated write path are not trade-offs; a critical is
fixed or the feature does not ship (`risk-register.md`).

Acceptable, with the compensating control named in the row:

| Risk | Acceptable when | Compensating control |
|------|-----------------|----------------------|
| No CAPTCHA or bot challenge | Rate limiting **and** the moderation queue are both live | The queue absorbs what the limit lets through |
| No sybil detection beyond rate limits | Votes only inform the roadmap; no money or ranking depends on them | The grouped-by-signup-date query, run when a count looks off |
| Manual moderation by one person, no SLA | Volume is low and a report route exists | A published expectation of how fast items are reviewed |
| No profanity or content classifier | Nothing is public before review | The gate itself |
| Edit history not kept | Content is not evidentiary | Moderation actions logged with actor and timestamp |

Each accepted row goes to `docs/SECURITY-risks.md` with who accepts, the date and a review date,
and is reopened when the context changes — volume grows, votes start deciding something with
money attached, or the queue stops being read.

Before adding a control, walk the cheapest-fix ladder from `CLAUDE.md`: delete the field, use
the platform (the database constraint, the framework's escaping, the provider's limiter), reuse
what the app already has, correct the value, add. A new moderation service where removing a
free-text field was enough is itself a finding.

## Verdict

One table ordered by severity then reach, triggers first, and one word on the last line —
**Blocked** if any section 2 item stands, **Approved** otherwise — per the shared review method
in `CLAUDE.md` and the format in `verdict.md`.
