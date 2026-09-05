# Capa de acceso a datos (DAL) · patrón para Next.js

La única frontera de seguridad. `import 'server-only'` arriba de cada archivo. Es la única que
lee `process.env` y usa el cliente de base de datos. Cada función: autentica, autoriza por
recurso, valida, devuelve un DTO mínimo. Las server actions son delgadas y delegan aquí.

## `src/data/auth.ts`

```ts
import 'server-only'
import { cache } from 'react'
import { auth } from '@clerk/nextjs/server' // o Better Auth / Auth.js

export class Viewer {
  constructor(readonly id: string, readonly orgId: string | null, readonly role: 'member' | 'admin') {}
}

// cache(): un solo cálculo por petición, sin pasar el usuario de componente en componente
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

// DTO: solo lo que la interfaz necesita. Nunca el registro completo.
export type ProjectDTO = { id: string; name: string; updatedAt: string }

const toDTO = (r: typeof projects.$inferSelect): ProjectDTO =>
  ({ id: r.id, name: r.name, updatedAt: r.updatedAt.toISOString() })

export async function listProjects(): Promise<ProjectDTO[]> {
  const v = await requireViewer()
  // autorización EN la consulta: solo lo del dueño
  const rows = await db.select().from(projects).where(eq(projects.ownerId, v.id))
  return rows.map(toDTO)
}

export async function getProject(id: string): Promise<ProjectDTO | null> {
  const v = await requireViewer()
  const [row] = await db.select().from(projects)
    .where(and(eq(projects.id, id), eq(projects.ownerId, v.id))) // no basta el id
  return row ? toDTO(row) : null
}

export async function createProject(raw: unknown): Promise<ProjectDTO> {
  const v = await requireViewer()
  const input = projectInput.parse(raw) // Zod: los tipos se borran; el esquema no
  const [row] = await db.insert(projects).values({ ...input, ownerId: v.id }).returning()
  return toDTO(row)
}

export async function deleteProject(id: string): Promise<void> {
  const v = await requireViewer()
  const res = await db.delete(projects)
    .where(and(eq(projects.id, id), eq(projects.ownerId, v.id)))
    .returning({ id: projects.id })
  if (res.length === 0) throw new Error('FORBIDDEN') // no existe o no es suyo: misma respuesta
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
    await rateLimit('create-project') // Upstash o el del hosting
    await createProject(Object.fromEntries(formData))
    revalidatePath('/projects')
    return { ok: true }
  } catch (e) {
    console.error('createProject', { code: (e as Error).message }) // sin datos del usuario
    return { ok: false, error: 'No se pudo crear el proyecto. Revisa los datos e intenta de nuevo.' }
  }
}

export async function deleteProjectAction(id: string): Promise<ActionState> {
  try {
    await deleteProject(id) // auth + authz dentro de la DAL
    revalidatePath('/projects')
    return { ok: true }
  } catch {
    return { ok: false, error: 'No se pudo eliminar.' } // genérico: no revela si existe
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

## Pruebas por función de la DAL y por acción

| Caso | Qué comprueba |
|------|---------------|
| Feliz | crea / lee / borra lo propio y devuelve el DTO |
| Inválido | entrada que no pasa Zod → error, sin tocar la BD |
| Sin permiso | id de otro usuario → FORBIDDEN, misma respuesta que inexistente |
| Sin sesión | UNAUTHENTICATED |

## Webhooks · `src/app/api/webhooks/stripe/route.ts`

```ts
import Stripe from 'stripe'
import { headers } from 'next/headers'
import { handleStripeEvent } from '@/data/billing'

export async function POST(req: Request) {
  const body = await req.text() // crudo, antes de parsear
  const sig = (await headers()).get('stripe-signature')
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!) // process.env solo aquí o en data/
  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, sig!, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch {
    return new Response('bad signature', { status: 400 })
  }
  await handleStripeEvent(event) // idempotente por event.id
  return new Response('ok')
}
```

## Auditoría rápida (Schneier)

```bash
grep -rn "process.env" src --include=*.ts --include=*.tsx | grep -v "src/data/" | grep -v NEXT_PUBLIC_
grep -rln "from '@/data/db'" src | grep -v "src/data/"
grep -rn "dangerouslySetInnerHTML" src
```

Las tres deben salir vacías (la primera puede mostrar `proxy.ts` y `route.ts` de webhooks).
