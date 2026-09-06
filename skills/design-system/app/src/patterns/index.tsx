import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import type { Ramps, Semantic } from '../engine/color'
import { STEPS, hex } from '../engine/color'
import type { PairResult } from '../engine/contrast'
import type { Knobs } from '../engine/tokens'
import { typeScale, TEXT_STEPS, SPACE_KEYS, spacing } from '../engine/tokens'
import { PRESETS } from '../engine/presets'

export interface Copy { brand: string; title: string; lede: string; cta: string; cta2: string }

export interface SavedPresetSummary { slug: string; name: string; accent?: string; font?: string; updated: string }

const Pattern = ({ n, title, note, children }: { n: number; title: string; note: string; children: React.ReactNode }) => (
  <section className="pattern" aria-labelledby={`p${n}`}>
    <header><h2 id={`p${n}`}>{title}</h2><span className="n">{String(n).padStart(2, '0')} · {note}</span></header>
    {children}
  </section>
)

export function Presets({ builtIn, saved, current, onApply, onDelete }: {
  builtIn: string[]
  saved: SavedPresetSummary[]
  current: string
  onApply: (name: string) => void
  onDelete: (name: string) => void
}) {
  return (
    <Pattern n={0} title="Presets" note="starting points · saved presets live in skills/design-system/presets">
      <div className="stack">
        <div className="grid">
          {builtIn.map((name) => {
            const p = PRESETS[name]
            return (
              <article className="card" key={name}>
                <div className="row" style={{ justifyContent: 'space-between' }}>
                  <h3>{name}</h3>
                  {current === name && <span className="tag accent">Current</span>}
                </div>
                <div style={{ height: 12, borderRadius: 'var(--radius-sm)', background: p.accent }} />
                <span className="small muted">{p.font}</span>
                <div className="row"><button className="btn primary sm" onClick={() => onApply(name)}>Use preset</button></div>
              </article>
            )
          })}
        </div>
        {saved.length > 0 && (
          <div className="stack">
            <h3>Saved in web-lab</h3>
            <div className="grid">
              {saved.map((sp) => (
                <article className="card" key={sp.slug}>
                  <div className="row" style={{ justifyContent: 'space-between' }}>
                    <h3>{sp.name}</h3>
                    {current === sp.name && <span className="tag accent">Current</span>}
                  </div>
                  <div style={{ height: 12, borderRadius: 'var(--radius-sm)', background: sp.accent ?? 'var(--muted)' }} />
                  <span className="small muted">{sp.font}</span>
                  <div className="row">
                    <button className="btn primary sm" onClick={() => onApply(sp.name)}>Use preset</button>
                    <button className="btn ghost sm" onClick={() => onDelete(sp.name)}>Delete</button>
                  </div>
                </article>
              ))}
            </div>
          </div>
        )}
        <p className="small muted">Save the current settings as a preset from the DialKit panel: Export → name → Save preset to web-lab. Then say 'use &lt;name&gt;' when starting a project.</p>
      </div>
    </Pattern>
  )
}

export function Typography({ k, copy }: { k: Knobs; copy: Copy }) {
  const scale = typeScale(k.base, k.ratio)
  return (
    <Pattern n={2} title="Typography" note={`${k.font} · ratio ${k.ratio} · base ${k.base}px`}>
      <div className="stack">
        <h1>{copy.title}</h1>
        <p className="muted" style={{ fontSize: 'var(--text-lg)' }}>{copy.lede}</p>
        <p>Body copy stays at the base size with a line-height of {k.leading}. Long lines are capped near 65 characters so the eye finds the next line without effort. <a href="#">Links are underlined</a>, not just colored, and <strong>emphasis</strong> uses weight.</p>
        <p className="small muted">Small text for captions, meta and hints. Never lighter than 400 below 18px.</p>
        <div className="stack" style={{ gap: 0 }}>
          {TEXT_STEPS.slice().reverse().map((s) => (
            <div className="type-row" key={s}><span className="k">text-{s} · {scale[s]}</span><span style={{ fontSize: `var(--text-${s})`, fontFamily: ['4xl', '5xl', '6xl', '3xl', '2xl'].includes(s) ? 'var(--font-display)' : undefined, lineHeight: 1.15 }}>The quick brown fox</span></div>
          ))}
        </div>
      </div>
    </Pattern>
  )
}

const MODE_SWATCHES = ['background', 'card', 'muted', 'border', 'accent', 'danger', 'success', 'warning'] as const

export function Color({ ramps, sem, pairs, pinned }: { ramps: Ramps; sem: Semantic; pairs: PairResult[]; pinned: number | null }) {
  const fails = pairs.filter((p) => !p.ok).length
  const semList = Object.entries(sem)
  const hasDarkAccent = !!ramps['brand-dark']
  return (
    <Pattern n={1} title="Color" note={`accent ${pinned ? `pinned on ${pinned}` : 'snapped to the ramp'} · ${fails ? `${fails} pair(s) fail` : 'all pairs pass'}${hasDarkAccent ? ' · custom dark accent' : ''}`}>
      <div className="stack">
        <div className="stack">
          <h3>Both modes</h3>
          <p className="small muted">Both palettes at once, from the concrete token values (not the live theme toggle above).</p>
          <div className="grid">
            {(['light', 'dark'] as const).map((mode) => (
              <div
                key={mode}
                style={{ background: sem.background[mode], border: `1px solid ${sem.border[mode]}`, borderRadius: 'var(--radius-lg)', padding: 'var(--spacing-4)' }}
              >
                <div className="row" style={{ justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: sem.foreground[mode], fontWeight: 600, textTransform: 'capitalize' }}>{mode}</span>
                </div>
                <p style={{ color: sem.foreground[mode], margin: 'var(--spacing-2) 0' }}>The quick brown fox jumps over the lazy dog.</p>
                <div className="row" style={{ gap: 'var(--spacing-2)', flexWrap: 'wrap' }}>
                  {MODE_SWATCHES.map((n) => (
                    <span key={n} className="tag" style={{ background: sem[n][mode], color: sem.foreground[mode], border: `1px solid ${sem.border[mode]}` }}>{n}</span>
                  ))}
                  <span className="tag" style={{ background: sem.accent[mode], color: sem['accent-foreground'][mode] }}>Primary button</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        {(Object.keys(ramps) as (keyof Ramps)[]).map((g) => {
          const r = ramps[g]!
          return (
            <div key={g}>
              <div className="ramp-name">{g}</div>
              <div className="ramp">{STEPS.map((s) => <div key={s} style={{ background: r[s] }} title={`${g}-${s} · ${r[s]} · ${hex(r[s])}`}><span style={{ color: s >= 500 ? '#fff' : '#000', opacity: 0.7 }}>{s}</span></div>)}</div>
            </div>
          )
        })}
        <div className="row" style={{ gap: 'var(--spacing-2)' }}>
          {(Object.keys(sem) as (keyof Semantic)[]).map((n) => (
            <span key={n} className="tag" style={{ background: `var(--${n})`, color: n.endsWith('foreground') || n === 'background' || n === 'card' || n === 'muted' || n === 'border' ? 'var(--foreground)' : n === 'accent' ? 'var(--accent-foreground)' : '#fff', border: '1px solid var(--border)' }}>{n}</span>
          ))}
        </div>
        <table>
          <thead><tr><th>Pair</th><th>Sample</th><th>Min</th><th>Light</th><th>Dark</th><th>APCA Lc (light / dark)</th></tr></thead>
          <tbody>
            {pairs.map((p) => (
              <tr key={p.label}>
                <td>{p.label}<br /><span className="mono" style={{ fontSize: 11 }}>{p.fg} / {p.bg}</span></td>
                <td><span className="sample" style={{ background: `var(--${p.bg})`, color: `var(--${p.fg})`, border: '1px solid var(--border)' }}>Aa 12px</span></td>
                <td>{p.min}:1</td>
                <td className={p.light >= p.min ? 'ok' : 'fail'}>{p.light.toFixed(2)}</td>
                <td className={p.dark >= p.min ? 'ok' : 'fail'}>{p.dark.toFixed(2)}</td>
                <td className="muted">{p.lightLc} / {p.darkLc}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="small muted">WCAG is the legal gate; APCA (Lc 75 body, 60 labels, 45 large, 30 controls) is the tiebreaker. Fix contrast by moving lightness, not hue.</p>
        <h3>Semantic tokens</h3>
        <table><thead><tr><th>Token</th><th>Light</th><th>Dark</th></tr></thead><tbody>
          {semList.map(([n, val]) => <tr key={n}><td className="mono">--{n}</td><td className="mono">{val.lightRef} <span className="sample" style={{ background: val.light, border: '1px solid var(--border)' }}>&nbsp;&nbsp;&nbsp;</span></td><td className="mono">{val.darkRef} <span className="sample" style={{ background: val.dark, border: '1px solid var(--border)' }}>&nbsp;&nbsp;&nbsp;</span></td></tr>)}
        </tbody></table>
      </div>
    </Pattern>
  )
}

export function Shape({ k }: { k: Knobs }) {
  const sizes = ['none', 'sm', 'md', 'lg', 'xl'] as const
  return (
    <Pattern n={3} title="Shape" note={`${k.corner} corners · radius ${k.radius}px · border ${k.border}px`}>
      <div className="stack">
        <div className="row" style={{ alignItems: 'flex-end' }}>
          {sizes.map((s) => (
            <div key={s}>
              <span className="state-label">{s}</span>
              <div style={{ width: 64, height: 64, background: 'var(--muted)', border: 'var(--border-width) solid var(--border)', borderRadius: `var(--radius-${s})` }} />
            </div>
          ))}
        </div>
        <div className="card" style={{ maxWidth: 240 }}>
          <div className="thumb" role="img" aria-label="Placeholder image" />
          <button className="btn primary sm">Concentric radius</button>
        </div>
        <p className="small muted">Outer radius = inner radius + padding. Squircle uses CSS corner-shape where supported and falls back to the radius.</p>
      </div>
    </Pattern>
  )
}

export function Elevation({ k }: { k: Knobs }) {
  const items = [
    { label: 'sm', style: { boxShadow: 'var(--shadow-sm)' } },
    { label: 'md', style: { boxShadow: 'var(--shadow-md)' } },
    { label: 'lg', style: { boxShadow: 'var(--shadow-lg)' } },
  ]
  return (
    <Pattern n={4} title="Elevation" note={`${k.shadow} shadows`}>
      <div className="stack">
        <div className="grid">
          {items.map((it) => (
            <div key={it.label}>
              <span className="state-label">{it.label}</span>
              <div className="card" style={it.style}><h3>Surface</h3><span className="small muted">Hover to lift</span></div>
            </div>
          ))}
          <div>
            <span className="state-label">border only</span>
            <div className="card" style={{ boxShadow: 'none', border: '1px solid var(--border)' }}><h3>Surface</h3><span className="small muted">Hover to lift</span></div>
          </div>
        </div>
        <p className="small muted">Shadows for depth, borders for structure. In dark mode layered shadows become a single light ring.</p>
      </div>
    </Pattern>
  )
}

export function Spacing({ k }: { k: Knobs }) {
  const sp = spacing(k.space)
  const gaps = ['2', '4', '8'] as const
  return (
    <Pattern n={5} title="Spacing" note={`base unit ${k.space}px`}>
      <div className="stack">
        <div className="stack" style={{ gap: 0 }}>
          {SPACE_KEYS.map((key) => (
            <div className="type-row" key={key}>
              <span className="k">spacing-{key} · {sp[String(key)]}</span>
              <div style={{ height: 12, width: `var(--spacing-${key})`, background: 'var(--accent)', borderRadius: 'var(--radius-sm)' }} />
            </div>
          ))}
        </div>
        <div className="stack">
          {gaps.map((g) => (
            <div key={g}>
              <span className="state-label">gap spacing-{g}</span>
              <div className="row" style={{ gap: `var(--spacing-${g})` }}>
                <button className="btn secondary sm">One</button>
                <button className="btn secondary sm">Two</button>
                <button className="btn secondary sm">Three</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Pattern>
  )
}

export function Motion({ k, reduced }: { k: Knobs; reduced: boolean }) {
  const rows = ['fast', 'normal', 'slow'] as const
  const [moved, setMoved] = useState<Record<string, boolean>>({ fast: false, normal: false, slow: false })
  function replay(r: string) {
    setMoved((m) => ({ ...m, [r]: false }))
    requestAnimationFrame(() => requestAnimationFrame(() => setMoved((m) => ({ ...m, [r]: true }))))
  }
  return (
    <Pattern n={6} title="Motion" note={`${k.duration} ms · ease ${k.ease}`}>
      <div className="stack">
        {rows.map((r) => (
          <div className="row" key={r} style={{ alignItems: 'center' }}>
            <span className="state-label" style={{ minWidth: 56 }}>{r}</span>
            <button className="btn secondary sm" onClick={() => replay(r)}>Replay</button>
            <div className="dot" style={{
              translate: moved[r] ? '160px 0' : '0 0',
              transitionProperty: 'translate',
              transitionDuration: reduced ? '0.01ms' : `var(--duration-${r})`,
              transitionTimingFunction: 'var(--ease-ui)',
            }} />
          </div>
        ))}
        <p className="small muted">150 to 300 ms for interface transitions, interruptible, with a static cue left behind. Under reduced motion everything snaps.</p>
      </div>
    </Pattern>
  )
}

export function Buttons({ copy }: { copy: Copy }) {
  const states: { label: string; props: Record<string, unknown>; body?: React.ReactNode }[] = [
    { label: 'default', props: {} }, { label: 'hover', props: { style: { filter: 'brightness(0.92)' } } },
    { label: 'focus-visible', props: { style: { outline: '2px solid var(--ring)', outlineOffset: 2 } } },
    { label: 'active', props: { style: { scale: '0.96' } } }, { label: 'disabled', props: { disabled: true } },
    { label: 'loading', props: { 'aria-busy': true }, body: <><span className="spin" aria-hidden="true" /> {copy.cta}</> },
  ]
  return (
    <Pattern n={7} title="Buttons" note="4 variants · 3 sizes · 9 states · scale 0.96 on press">
      <div className="stack">
        <div className="row"><button className="btn primary">{copy.cta}</button><button className="btn secondary">{copy.cta2}</button><button className="btn ghost">Learn more about plans</button><button className="btn danger">Delete project</button></div>
        <div className="row"><button className="btn primary sm">Small</button><button className="btn primary">Medium</button><button className="btn primary lg">Large</button><button className="btn secondary" aria-label="Add item" style={{ paddingInline: 'var(--spacing-3)' }}>＋</button></div>
        <div className="row" style={{ alignItems: 'flex-end' }}>
          {states.map((s) => <div key={s.label}><span className="state-label">{s.label}</span><button className="btn primary" {...s.props}>{s.body ?? copy.cta}</button></div>)}
          <div><span className="state-label">error</span><button className="btn secondary" style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}>Retry payment</button></div>
          <div><span className="state-label">selected</span><button className="btn secondary" aria-pressed="true" style={{ background: 'color-mix(in oklab, var(--accent) 14%, var(--card))', color: 'var(--accent)', borderColor: 'var(--accent)' }}>Monthly</button></div>
          <div><span className="state-label">empty</span><button className="btn ghost" disabled>No actions available</button></div>
        </div>
      </div>
    </Pattern>
  )
}

export function Cards({ k, copy }: { k: Knobs; copy: Copy }) {
  return (
    <Pattern n={9} title="Cards" note={`${k.corner} corners · radius ${k.radius}px · ${k.shadow} shadow · border ${k.border}px`}>
      <div className="grid">
        {[copy.title, 'A second card with a shorter title', 'Donaudampfschifffahrtsgesellschaftskapitän and a very long unbreakable word'].map((t, i) => (
          <article className="card" key={i}>
            <div className={`thumb ${i === 1 ? 'neutral' : ''}`} role="img" aria-label="Placeholder image" />
            <div className="row" style={{ justifyContent: 'space-between' }}><span className="tag accent">Featured</span><span className="small muted">5 min</span></div>
            <h3 style={{ overflowWrap: 'anywhere' }}>{t}</h3>
            <p className="small muted">The outer radius equals the inner radius plus the padding, so the thumbnail sits concentric with the card.</p>
            <div className="row"><button className="btn primary sm">{copy.cta}</button><a href="#" className="small">Read the details</a></div>
          </article>
        ))}
      </div>
    </Pattern>
  )
}

export function FormControls() {
  const [on, setOn] = useState(true)
  return (
    <Pattern n={8} title="Form controls" note="labels visible · errors next to the field · 24px targets">
      <form className="stack" style={{ maxWidth: 480 }} onSubmit={(e) => e.preventDefault()}>
        <div className="field"><label htmlFor="f-name">Full name</label><input id="f-name" className="input" placeholder="Ada Lovelace" autoComplete="name" /></div>
        <div className="field error"><label htmlFor="f-email">Email</label><input id="f-email" className="input" defaultValue="ada@example" aria-invalid="true" aria-describedby="f-email-msg" autoComplete="email" /><span id="f-email-msg" className="msg">Enter an email with an @, like ada@example.com</span></div>
        <div className="field"><label htmlFor="f-plan">Plan</label><select id="f-plan" className="input"><option>Starter</option><option>Studio</option><option>Agency</option></select><span className="hint">You can change it any time.</span></div>
        <div className="field"><label htmlFor="f-msg">Message</label><textarea id="f-msg" className="input" placeholder="Tell us what you need" /></div>
        <fieldset className="field" style={{ border: 0, padding: 0, margin: 0 }}>
          <legend>Plan type</legend>
          <div className="row">
            <label className="check"><input type="radio" name="plan" value="monthly" defaultChecked /> Monthly</label>
            <label className="check"><input type="radio" name="plan" value="yearly" /> Yearly</label>
            <label className="check"><input type="radio" name="plan" value="lifetime" /> Lifetime</label>
          </div>
        </fieldset>
        <div className="row">
          <label className="check"><input type="checkbox" /> Email updates</label>
          <label className="check"><input type="checkbox" /> SMS reminders</label>
          <label className="check"><input type="checkbox" /> Partner offers</label>
        </div>
        <label className="check"><input type="checkbox" defaultChecked /> Send me the monthly newsletter</label>
        <div className="row"><button type="button" role="switch" aria-checked={on} className="switch" onClick={() => setOn(!on)} aria-label="Email notifications" /><span className="small">Email notifications</span></div>
        <div className="row"><button className="btn primary">Create account</button><button className="btn ghost" type="button">Cancel</button></div>
      </form>
    </Pattern>
  )
}

export function Navigation({ copy }: { copy: Copy }) {
  return (
    <Pattern n={10} title="Navigation" note="header · menu · footer · current page in accent">
      <div style={{ border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'clip' }}>
        <nav className="nav" aria-label="Main">
          <span className="logo">{copy.brand}</span>
          <ul><li><a href="#" aria-current="page">Classes</a></li><li><a href="#">Schedule</a></li><li><a href="#">Pricing</a></li><li><a href="#">About</a></li><li><a href="#" className="btn primary sm" style={{ textDecoration: 'none' }}>{copy.cta}</a></li></ul>
          <button className="btn ghost sm menu" aria-label="Open menu">☰ Menu</button>
        </nav>
        <div style={{ padding: 'var(--spacing-6)' }}><p className="muted small">Page content</p></div>
        <footer className="footer"><span>© 2026 {copy.brand}</span><span><a href="#">Privacy notice</a> · <a href="#">Terms</a> · <a href="#">hello@example.mx</a></span></footer>
      </div>
    </Pattern>
  )
}

export function Hero({ copy }: { copy: Copy }) {
  return (
    <Pattern n={11} title="Hero" note="density · content width · image treatment">
      <div className="hero wrap">
        <div className="stack"><span className="tag accent">New this season</span><h1>{copy.title}</h1><p className="lede">{copy.lede}</p><div className="row"><button className="btn primary lg">{copy.cta}</button><button className="btn secondary lg">{copy.cta2}</button></div><p className="small muted">No card required · Cancel any time</p></div>
        <div className="art" role="img" aria-label="Hero illustration" />
      </div>
    </Pattern>
  )
}

export function List() {
  const rows = [['Morning flow', 'Mon · 7:00 · Beginners', 'success', 'Open'], ['Power vinyasa', 'Tue · 19:00 · Intermediate', 'warning', '2 left'], ['Restorative', 'Thu · 20:00 · All levels', 'danger', 'Full'], ['Weekend long form with an intentionally long class name to test wrapping', 'Sat · 9:00 · All levels', 'accent', 'Waitlist']]
  const tableRows = [
    ['Morning flow', 'Mon', 'Beginners', '8'],
    ['Power vinyasa', 'Tue', 'Intermediate', '2'],
    ['Restorative', 'Thu', 'All levels', '0'],
    ['Weekend long form', 'Sat', 'All levels', 'Waitlist'],
  ]
  return (
    <Pattern n={12} title="List and table" note="rows · hover · status tags · long content">
      <div className="stack">
        <div className="list">
          {rows.map(([t, m, tag, label]) => (
            <div className="item" key={t}><div className="avatar" /><div><b>{t}</b><span className="small muted">{m}</span></div><span className={`tag ${tag}`}>{label}</span></div>
          ))}
        </div>
        <table>
          <thead><tr><th>Class</th><th>Day</th><th>Level</th><th>Spots</th></tr></thead>
          <tbody>
            {tableRows.map((r) => <tr key={r[0]}>{r.map((c, i) => <td key={i}>{c}</td>)}</tr>)}
          </tbody>
        </table>
      </div>
    </Pattern>
  )
}

export function Feedback() {
  return (
    <Pattern n={13} title="Feedback" note="alert · toast · tags · empty · loading">
      <div className="grid">
        <div className="stack">
          <div className="alert info" role="status"><span aria-hidden="true">ⓘ</span><div><b>Your booking is pending</b>We will confirm by email within an hour.</div></div>
          <div className="alert success" role="status"><span aria-hidden="true">✓</span><div><b>Payment received</b>Receipt sent to ada@example.com.</div></div>
          <div className="alert danger" role="alert"><span aria-hidden="true">!</span><div><b>Unable to save</b>Check your connection and try again.</div></div>
          <div className="toast" role="status"><span aria-hidden="true">✓</span> Class booked <button className="btn ghost sm" style={{ color: 'inherit' }}>Undo</button></div>
        </div>
        <div className="stack">
          <div className="empty"><div className="ico" aria-hidden="true" /><b>No bookings yet</b><span className="small muted">Bookings keep your classes and receipts together.</span><button className="btn primary sm">Book a class</button></div>
          <div className="stack" style={{ gap: 'var(--spacing-2)' }} aria-busy="true" aria-label="Loading"><div className="skeleton" style={{ width: '60%' }} /><div className="skeleton" /><div className="skeleton" style={{ width: '80%' }} /></div>
        </div>
      </div>
    </Pattern>
  )
}

export function Dialog({ k, reduced }: { k: Knobs; reduced: boolean }) {
  const [open, setOpen] = useState(true)
  const [sheetOpen, setSheetOpen] = useState(false)
  const [tick, setTick] = useState(0)
  const d = reduced ? 0 : Math.max(k.duration, 0) / 1000
  return (
    <Pattern n={14} title="Dialog and sheet" note={`${k.duration} ms · ease ${k.ease} · ${reduced ? 'reduced motion on' : 'interruptible transitions'}`}>
      <div className="stack">
        <div className="dialog-stage">
          {!open && <button className="btn primary" onClick={() => setOpen(true)}>Open dialog</button>}
          <AnimatePresence initial={false}>
            {open && (
              <>
                <motion.div key="scrim" className="scrim" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: d }} onClick={() => setOpen(false)} />
                <motion.div key="dlg" role="dialog" aria-modal="true" aria-labelledby="dlg-t" className="dialog"
                  initial={{ opacity: 0, y: 8, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 8, scale: 0.98 }}
                  transition={k.ease === 'spring' && !reduced ? { type: 'spring', visualDuration: Math.max(d, 0.15), bounce: 0 } : { duration: d, ease: [0.2, 0, 0, 1] }}>
                  <h3 id="dlg-t">Delete this project?</h3>
                  <p className="small muted">This removes the project and its 14 files. You can restore it from the trash for 30 days.</p>
                  <div className="actions"><button className="btn ghost" onClick={() => setOpen(false)}>Cancel</button><button className="btn danger" onClick={() => setOpen(false)}>Delete project</button></div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
        <div className="motion-row">
          <button className="btn secondary sm" onClick={() => setTick((t) => t + 1)}>Replay icon swap</button>
          <AnimatePresence mode="popLayout" initial={false}>
            <motion.span key={tick} className="dot" initial={{ opacity: 0, scale: 0.25, filter: 'blur(4px)' }} animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }} exit={{ opacity: 0, scale: 0.25, filter: 'blur(4px)' }} transition={reduced ? { duration: 0 } : { type: 'spring', visualDuration: 0.3, bounce: 0 }} />
          </AnimatePresence>
          <span className="small muted">Icons swap with scale 0.25 → 1, opacity 0 → 1, blur 4 → 0 px (better-ui). Every state change also leaves a static cue.</span>
        </div>
        <div className="dialog-stage">
          {!sheetOpen && <button className="btn primary" onClick={() => setSheetOpen(true)}>Open sheet</button>}
          <AnimatePresence initial={false}>
            {sheetOpen && (
              <>
                <motion.div key="sheet-scrim" className="scrim" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: d }} onClick={() => setSheetOpen(false)} />
                <motion.div key="sheet" role="dialog" aria-modal="true" aria-labelledby="sheet-t" className="dialog"
                  style={{ alignSelf: 'end', width: '100%', borderBottomLeftRadius: 0, borderBottomRightRadius: 0 }}
                  initial={{ y: '100%' }} animate={{ y: 0 }} exit={{ y: '100%' }}
                  transition={k.ease === 'spring' && !reduced ? { type: 'spring', visualDuration: Math.max(d, 0.15), bounce: 0 } : { duration: d, ease: [0.2, 0, 0, 1] }}>
                  <h3 id="sheet-t">Filter classes</h3>
                  <label className="check"><input type="checkbox" defaultChecked /> Morning only</label>
                  <label className="check"><input type="checkbox" /> Beginner friendly</label>
                  <div className="actions"><button className="btn primary" onClick={() => setSheetOpen(false)}>Apply</button><button className="btn ghost" onClick={() => setSheetOpen(false)}>Close</button></div>
                </motion.div>
              </>
            )}
          </AnimatePresence>
        </div>
      </div>
    </Pattern>
  )
}
