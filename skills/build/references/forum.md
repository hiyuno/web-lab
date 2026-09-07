# Forum · public feature-request and voting board

Backend spec for the feature-request/voting forum used by the `app-web` skill (marketing site
for one of Yuno's own apps). Built from scratch on the DAL pattern in `dal.md` — Drizzle,
Postgres, Zod, `server-only`, `requireViewer()`. Not an external tool (Canny, Frill and similar
were considered and rejected: Yuno already has auth and a Postgres database, and a bought tool
adds a second identity system and a second place data can leak). Votes are authenticated only:
no anonymous or fingerprint voting. One vote per person is enforced by a unique database
constraint, not by application logic. Yuno reviews and picks what ships; this is curated, not a
self-service roadmap.

## Data model · `src/db/schema.ts`

Reference the app's existing `users` table for every author/voter FK. Do not create a parallel
user table for the forum.

```ts
import { pgTable, uuid, text, timestamp, pgEnum, uniqueIndex, type AnyPgColumn } from 'drizzle-orm/pg-core'
import { users } from './schema' // the app's existing table — do not duplicate it

export const requestStatus = pgEnum('request_status', [
  'open',
  'planned',
  'in_progress',
  'shipped',
  'declined',
])

export const requests = pgTable('requests', {
  id: uuid('id').primaryKey().defaultRandom(),
  title: text('title').notNull(),
  body: text('body').notNull(),
  authorId: text('author_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  status: requestStatus('status').notNull().default('open'),
  mergedIntoId: uuid('merged_into_id').references((): AnyPgColumn => requests.id, { onDelete: 'set null' }),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).notNull().defaultNow(),
})

export const votes = pgTable('votes', {
  id: uuid('id').primaryKey().defaultRandom(),
  requestId: uuid('request_id').notNull().references(() => requests.id, { onDelete: 'cascade' }),
  voterId: text('voter_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
}, (t) => ({
  // THIS constraint is the anti-abuse mechanism, not a nice-to-have.
  // One row per (request, voter) is what makes "one vote per person" true
  // even if a bug, a race condition or a replayed request calls voteRequest twice.
  oneVotePerVoter: uniqueIndex('votes_request_voter_uidx').on(t.requestId, t.voterId),
}))

export const comments = pgTable('comments', {
  id: uuid('id').primaryKey().defaultRandom(),
  requestId: uuid('request_id').notNull().references(() => requests.id, { onDelete: 'cascade' }),
  authorId: text('author_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  body: text('body').notNull(),
  createdAt: timestamp('created_at', { withTimezone: true }).notNull().defaultNow(),
})
```

Both `requests` and `comments` also carry a moderation state — see Step 3 below; add
`moderationStatus: pgEnum('moderation_status', ['pending', 'published', 'redacted'])` with a
`.notNull().default('pending')` column to each table rather than a separate table, so the DAL's
`where` clauses stay single-table.

### Merge re-parenting

When Yuno sets `requests.mergedIntoId` on a duplicate (source → target), its votes must move to
the target request without creating a second vote for a voter who already backed both. Do this
in one transaction in `mergeRequests`:

1. Set `requests.mergedIntoId = targetId` and `requests.status = 'declined'` on the source (a
   merged request is not separately actionable).
2. For each vote row on the source request, attempt `insert into votes (request_id, voter_id)
   values (targetId, sourceVote.voterId)`.
3. Catch the unique-constraint violation on `votes_request_voter_uidx` and ignore it — that
   voter already has a vote on the target, so the insert correctly does nothing.
4. Delete all vote rows on the source request (`delete from votes where request_id = sourceId`).
5. Re-point comments the same way is not needed — leave `comments.requestId` on the source and
   let `getRequest` follow `mergedIntoId` to show them under the target, since comments carry no
   uniqueness constraint to reconcile.

```ts
export async function mergeRequests(sourceId: string, targetId: string): Promise<void> {
  const v = await requireViewer()
  if (v.role !== 'admin') throw new Error('FORBIDDEN')
  await db.transaction(async (tx) => {
    const sourceVotes = await tx.select().from(votes).where(eq(votes.requestId, sourceId))
    for (const vote of sourceVotes) {
      await tx.insert(votes).values({ requestId: targetId, voterId: vote.voterId })
        .onConflictDoNothing({ target: [votes.requestId, votes.voterId] })
    }
    await tx.delete(votes).where(eq(votes.requestId, sourceId))
    await tx.update(requests).set({ mergedIntoId: targetId, status: 'declined', updatedAt: new Date() })
      .where(eq(requests.id, sourceId))
  })
}
```

`onConflictDoNothing` targeting the exact unique index is Drizzle's way of expressing "attempt
insert, ignore the conflict" — prefer it over a manual `try/catch` around a plain `insert`.

## DAL functions · `src/data/forum.ts`

All `import 'server-only'`, all start with `requireViewer()` except the read paths that also
serve anonymous visitors (listing and reading published requests is public; voting, commenting
and posting are not).

| Function | Purpose |
|----------|---------|
| `listRequests({ status?, sort })` | Published requests only (`moderationStatus = 'published'`), optionally filtered by `status`, sorted by vote count or `createdAt`. No auth required. |
| `getRequest(id)` | One published request with its vote count, the viewer's own vote state if signed in, and its published comments. No auth required for reading. |
| `createRequest({ title, body })` | Zod-validated insert, `authorId = viewer.id`, `moderationStatus = 'pending'`. Rate-limited — see Step 3. |
| `voteRequest(id)` | Insert `{ requestId: id, voterId: viewer.id }` with `onConflictDoNothing`. Idempotent: a repeat call is a no-op, never an error. |
| `unvoteRequest(id)` | Delete the viewer's own vote row (`where requestId = id and voterId = viewer.id`); a missing vote is also a no-op. |
| `commentOnRequest(id, body)` | Zod-validated insert on a published, non-declined request; `authorId = viewer.id`, `moderationStatus = 'pending'`. Rate-limited. |
| `updateRequestStatus(id, status)` | **Admin only.** Validates the transition (see Step 4), sets `status` and `updatedAt`. |
| `mergeRequests(sourceId, targetId)` | **Admin only.** The transaction above. |
| `deleteRequest(id)` | **Admin only**, moderation removal — hard delete or set `moderationStatus = 'redacted'` depending on whether Yuno needs the LFPDPPP audit trail (see Step 5); prefer redact over delete so votes/comments counts stay consistent. |

Authorization pattern per `dal.md`: admin-only functions check `viewer.role === 'admin'` inside
the function, right after `requireViewer()` — never only in the UI or in middleware. Every
public read filters `moderationStatus = 'published'` in the query itself, the same way ownership
is filtered in the query for private resources.

```ts
export async function voteRequest(id: string): Promise<void> {
  const v = await requireViewer()
  await rateLimit(`vote:${v.id}`)
  await db.insert(votes).values({ requestId: id, voterId: v.id })
    .onConflictDoNothing({ target: [votes.requestId, votes.voterId] })
}
```

## Rate limiting and abuse controls

Reuse the `@upstash/ratelimit` convention already established in `dal.md`'s
`src/actions/projects.ts` (`rateLimit('create-project')`) and listed in `backend.md`'s stack
table. Apply a sliding-window limiter per viewer id (not per IP — voting is authenticated, so the
user id is always available and harder to spoof than an IP):

| Function | Window | Why |
|----------|--------|-----|
| `createRequest` | e.g. 5 / hour per user | Public write surface; a burst of requests is either spam or a bug. |
| `commentOnRequest` | e.g. 20 / hour per user | Same surface, higher normal-use ceiling. |
| `voteRequest` / `unvoteRequest` | e.g. 30 / minute per user, combined | The unique constraint stops duplicate votes, not vote-toggle spam — a script can still hammer vote/unvote in a loop to generate load or skew activity signals. Rate-limit the pair together. |

New `requests` and `comments` are inserted with `moderationStatus = 'pending'` and excluded from
every public `listRequests`/`getRequest` query until Yuno (or another admin) flips them to
`published` — this is user-generated content on a public site, it is never auto-published.
Give Yuno a `listPending()` DAL function (admin-only) and an `approve`/`reject` pair (`reject`
sets `moderationStatus = 'redacted'` rather than deleting, so the LFPDPPP trail in Step 5 holds).

## Status vocabulary and transitions

```
open ─▶ planned ─▶ in_progress ─▶ shipped
  │         │            │
  └─────────┴────────────┴──▶ declined
```

- Forward path: `open → planned → in_progress → shipped`, in order — do not let
  `updateRequestStatus` skip a rung silently; either allow it explicitly (Yuno may ship
  something without a `planned` stage) or validate the transition table and reject an invalid
  jump with a clear error.
- `declined` is reachable from `open`, `planned` or `in_progress` at any point — a request can be
  declined at any stage before shipping.
- `shipped` and `declined` are terminal; only `mergeRequests` (which forces `declined` on the
  source) touches status after that.
- Only `viewer.role === 'admin'` may call `updateRequestStatus`. There is no self-service status
  change for the requester.
- Shipped requests feed the `/changelog` page: the changelog is a curated view over `shipped`
  requests plus any release notes not tied to a request — the changelog's own schema and
  authoring flow belong to the `content` skill, not to this reference.

## Security note

This forum is the site's only public-write surface and gets full Schneier review against
`skills/security/references/public-write-surfaces.md` before launch — do not treat the
moderation queue or the rate limits above as a substitute for that gate. Free-text `body` fields
on `requests` and `comments` can contain personal data volunteered by requesters (names, emails,
account details pasted into a bug report), which puts them under Mexico's 2025 LFPDPPP per
`skills/security/references/legal-mx.md`; moderation must be able to redact or delete a single
request or comment on request (the `deleteRequest`/reject path above), and that capability must
exist before launch, not be added after the first takedown request arrives.
