# Data access layer (DAL) · pattern for Next.js

The only security boundary. `import 'server-only'` at the top of every file. It is the only layer
that reads `process.env` and uses the database client. Every function: authenticates, authorizes
per resource, validates, returns a minimal DTO. Server actions are thin and delegate here.

## `src/data/auth.ts`

```ts
import 'server-only'
import { cache } from 'react'
import { auth } from '@clerk/nextjs/server' // or Better Auth / Auth.js

export class Viewer {
  constructor(readonly id: string, readonly orgId: string | null, readonly role: 'member' | 'admin') {}
}

// cache(): computed once per request, no passing the user from component to component
export const getViewer = cache(async (): Promise<Viewer | null> => {
  const { userId, orgId, sessionClaims } = await auth()
  if (!userId) return null
  return new Viewer(userId, orgId ?? null, (sessionClaims?.role as 'admin') ?? 'member')
})

export async function requireViewer() {
  const v = await getViewer()
  if (!v) throw new Error('UNAUTHENTICATED')
  return v
}
```

## `src/data/projects.ts`

```ts
import 'server-only'
import { and, eq } from 'drizzle-orm'
import { db } from './db'
import { projects } from '@/db/schema'
import { requireViewer } from './auth'
import { projectInput } from '@/lib/validators'

// DTO: only what the UI needs. Never the full record.
export type ProjectDTO = { id: string; name: string; updatedAt: string }

const toDTO = (r: typeof projects.$inferSelect): ProjectDTO =>
  ({ id: r.id, name: r.name, updatedAt: r.updatedAt.toISOString() })

export async function listProjects(): Promise<ProjectDTO[]> {
  const v = await requireViewer()
  // authorization IN the query: only the owner's
  const rows = await db.select().from(projects).where(eq(projects.ownerId, v.id))
  return rows.map(toDTO)
}

export async function getProject(id: string): Promise<ProjectDTO | null> {
  const v = await requireViewer()
  const [row] = await db.select().from(projects)
    .where(and(eq(projects.id, id), eq(projects.ownerId, v.id))) // the id is not enough
  return row ? toDTO(row) : null
}

export async function createProject(raw: unknown): Promise<ProjectDTO> {
  const v = await requireViewer()
  const input = projectInput.parse(raw) // Zod: types are erased; the schema is not
  const [row] = await db.insert(projects).values({ ...input, ownerId: v.id }).returning()
  return toDTO(row)
}

export async function deleteProject(id: string): Promise<void> {
  const v = await requireViewer()
  const res = await db.delete(projects)
    .where(and(eq(projects.id, id), eq(projects.ownerId, v.id)))
    .returning({ id: projects.id })
  if (res.length === 0) throw new Error('FORBIDDEN') // missing or not theirs: same answer
}
```

## `src/actions/projects.ts`

```ts
'use server'
import { revalidatePath } from 'next/cache'
import { createProject, deleteProject } from '@/data/projects'
import { rateLimit } from '@/lib/ratelimit'

export type ActionState = { ok: true } | { ok: false; error: string }

export async function createProjectAction(_: ActionState, formData: FormData): Promise<ActionState> {
  try {
    await rateLimit('create-project') // Upstash or the hosting's
    await createProject(Object.fromEntries(formData))
    revalidatePath('/projects')
    return { ok: true }
  } catch (e) {
    console.error('createProject', { code: (e as Error).message }) // no user data
    return { ok: false, error: 'Could not create the project. Check the data and try again.' }
  }
}

export async function deleteProjectAction(id: string): Promise<ActionState> {
  try {
    await deleteProject(id) // auth + authz inside the DAL
    revalidatePath('/projects')
    return { ok: true }
  } catch {
    return { ok: false, error: 'Could not delete.' } // generic: does not reveal existence
  }
}
```

## `src/lib/validators.ts`

```ts
import { z } from 'zod'
export const projectInput = z.object({
  name: z.string().trim().min(1).max(80),
  description: z.string().trim().max(500).optional(),
})
export const idParam = z.string().uuid()
```

## Tests per DAL function and per action

| Case | What it checks |
|------|----------------|
| Happy | creates / reads / deletes their own and returns the DTO |
| Invalid | input that fails Zod → error, without touching the DB |
| Forbidden | another user's id → FORBIDDEN, same answer as nonexistent |
| No session | UNAUTHENTICATED |

## Webhooks · `src/app/api/webhooks/stripe/route.ts`

```ts
import Stripe from 'stripe'
import { headers } from 'next/headers'
import { handleStripeEvent } from '@/data/billing'

export async function POST(req: Request) {
  const body = await req.text() // raw, before parsing
  const sig = (await headers()).get('stripe-signature')
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!) // process.env only here or in data/
  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, sig!, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch {
    return new Response('bad signature', { status: 400 })
  }
  await handleStripeEvent(event) // idempotent by event.id
  return new Response('ok')
}
```

## Quick audit (Schneier)

```bash
grep -rn "process.env" src --include=*.ts --include=*.tsx | grep -v "src/data/" | grep -v NEXT_PUBLIC_
grep -rln "from '@/data/db'" src | grep -v "src/data/"
grep -rn "dangerouslySetInnerHTML" src
```

All three should come back empty (the first may show `proxy.ts` and webhook `route.ts`).
