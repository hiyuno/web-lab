import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import { readdirSync, readFileSync, writeFileSync, unlinkSync, mkdirSync, existsSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'

// Saved presets live in the repo so roles can read them from any project:
//   skills/design-system/presets/<slug>.tokens.json  (full DTCG export + knob positions)
const PRESETS_DIR = resolve(__dirname, '..', 'presets')
const slugify = (s: string) => s.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60)

function presetsApi(): Plugin {
  return {
    name: 'web-lab-presets-api',
    configureServer(server) {
      mkdirSync(PRESETS_DIR, { recursive: true })
      server.middlewares.use('/api/presets', (req, res) => {
        const send = (code: number, body: unknown) => { res.statusCode = code; res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(body)) }
        const url = new URL(req.url ?? '/', 'http://x')
        if (req.method === 'GET') {
          const list = readdirSync(PRESETS_DIR).filter((f) => f.endsWith('.tokens.json')).map((f) => {
            try {
              const j = JSON.parse(readFileSync(join(PRESETS_DIR, f), 'utf8'))
              const lab = j?.$extensions?.['web-lab']?.lab ?? {}
              return { slug: f.replace(/\.tokens\.json$/, ''), name: lab.name ?? f, accent: lab.accent, font: lab.font, updated: statSync(join(PRESETS_DIR, f)).mtime.toISOString(), lab }
            } catch { return null }
          }).filter(Boolean)
          return send(200, list)
        }
        if (req.method === 'POST') {
          let body = ''
          req.on('data', (c) => (body += c))
          req.on('end', () => {
            try {
              const { name, tokens } = JSON.parse(body)
              const slug = slugify(String(name ?? ''))
              if (!slug) return send(400, { error: 'Give the preset a name.' })
              if (!tokens?.$extensions?.['web-lab']?.lab) return send(400, { error: 'Tokens without lab knobs.' })
              tokens.$extensions['web-lab'].lab.name = String(name).trim()
              tokens.$description = `web-lab saved preset "${String(name).trim()}". ${tokens.$description ?? ''}`
              writeFileSync(join(PRESETS_DIR, `${slug}.tokens.json`), JSON.stringify(tokens, null, 2))
              send(200, { ok: true, slug, file: `skills/design-system/presets/${slug}.tokens.json` })
            } catch (e) { send(400, { error: String(e) }) }
          })
          return
        }
        if (req.method === 'DELETE') {
          const slug = slugify(url.searchParams.get('slug') ?? '')
          const f = join(PRESETS_DIR, `${slug}.tokens.json`)
          if (!slug || !existsSync(f)) return send(404, { error: 'No such preset.' })
          unlinkSync(f); return send(200, { ok: true })
        }
        send(405, { error: 'Method not allowed' })
      })
    },
  }
}

export default defineConfig({ plugins: [react(), presetsApi()], server: { host: 'localhost' } })
