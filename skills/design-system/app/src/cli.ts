// Headless export: the same tokens the lab shows, from a preset or a saved lab JSON, without a browser.
//   npx tsx src/cli.ts --preset Playful --json tokens.tokens.json --css tokens.css
//   npx tsx src/cli.ts --from docs/04-design/tokens.tokens.json --css tokens.css   (re-reads $extensions.web-lab.lab)
//   npx tsx src/cli.ts --saved "Template A" --json tokens.tokens.json --css tokens.css   (a preset saved from the lab)
import { readFileSync, writeFileSync } from 'node:fs'
import { buildRamps, buildSemantic } from './engine/color'
import { checkPairs } from './engine/contrast'
import { PRESETS } from './engine/presets'
import { buildTokens, tokensCss } from './engine/tokens'
import type { Knobs } from './engine/tokens'

const args = process.argv.slice(2)
const opt = (name: string) => { const i = args.indexOf(`--${name}`); return i >= 0 ? args[i + 1] : undefined }

let k: Knobs
const savedName = opt('saved')
if (savedName) {
  const dir = new URL('../../presets/', import.meta.url)
  const { readdirSync } = await import('node:fs')
  const slug = savedName.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
  const file = readdirSync(dir).find((f) => f === `${slug}.tokens.json`)
  if (!file) { console.error(`No saved preset "${savedName}" in skills/design-system/presets/`); process.exit(1) }
  args.push('--from', new URL(file, dir).pathname)
}
if (opt('from')) {
  const lab = JSON.parse(readFileSync(opt('from')!, 'utf8'))?.$extensions?.['web-lab']?.lab
  if (!lab) { console.error('No $extensions.web-lab.lab in that file'); process.exit(1) }
  k = lab as Knobs
} else {
  const p = PRESETS[opt('preset') ?? 'Minimal']
  if (!p) { console.error(`Unknown preset. Options: ${Object.keys(PRESETS).join(', ')}`); process.exit(1) }
  k = { accent: p.accent, pin: false, tint: p.tint, radius: p.radius, corner: p.corner, shadow: p.shadow, border: p.border, font: p.font, ratio: p.ratio, base: p.base, leading: p.leading, space: p.space, width: p.width, duration: p.duration, ease: 'out' }
}
if (opt('accent')) k.accent = opt('accent')!

const { ramps } = buildRamps(k.accent, k.pin, k.tint, { danger: 27, success: 150, warning: 75 })
const sem = buildSemantic(ramps)
const pairs = checkPairs(sem)
const fails = pairs.filter((p) => !p.ok)
for (const p of pairs) console.error(`${p.label.padEnd(24)} min ${String(p.min).padStart(4)}  light ${p.light.toFixed(2).padStart(6)}  dark ${p.dark.toFixed(2).padStart(6)}  ${p.ok ? 'ok' : 'FAIL'}`)
if (opt('json')) { writeFileSync(opt('json')!, JSON.stringify(buildTokens(k, ramps, sem), null, 2)); console.error(`[json] ${opt('json')}`) }
if (opt('css')) { writeFileSync(opt('css')!, tokensCss(k, ramps, sem)); console.error(`[css] ${opt('css')}`) }
if (!opt('json') && !opt('css')) process.stdout.write(JSON.stringify(buildTokens(k, ramps, sem), null, 2))
process.exit(fails.length ? 1 : 0)
