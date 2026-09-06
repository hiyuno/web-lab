import { useEffect, useMemo, useState } from 'react'
import { DialRoot, useDialKitController } from 'dialkit'
import { buildRamps, buildSemantic } from './engine/color'
import { checkPairs } from './engine/contrast'
import { FONTS, PRESETS } from './engine/presets'
import { buildTokens, cssVars, tokensCss } from './engine/tokens'
import type { Knobs } from './engine/tokens'
import { Presets, Typography, Color, Shape, Elevation, Spacing, Motion, Buttons, FormControls, Cards, Navigation, Hero, List, Feedback, Dialog } from './patterns'
import type { Copy } from './patterns'

const P = PRESETS.Minimal

interface SavedPreset { slug: string; name: string; accent?: string; font?: string; updated: string; lab: Record<string, any> }

type SectionId = 'presets' | 'color' | 'typography' | 'shape' | 'elevation' | 'spacing' | 'motion' | 'buttons' | 'forms' | 'cards' | 'navigation' | 'hero' | 'list' | 'feedback' | 'dialog'

const SECTIONS: { id: SectionId; label: string; group: 'General' | 'Patterns' }[] = [
  { id: 'presets', label: 'Presets', group: 'General' },
  { id: 'color', label: 'Color', group: 'General' },
  { id: 'typography', label: 'Typography', group: 'General' },
  { id: 'shape', label: 'Shape', group: 'General' },
  { id: 'elevation', label: 'Elevation', group: 'General' },
  { id: 'spacing', label: 'Spacing', group: 'General' },
  { id: 'motion', label: 'Motion', group: 'General' },
  { id: 'buttons', label: 'Buttons', group: 'Patterns' },
  { id: 'forms', label: 'Form controls', group: 'Patterns' },
  { id: 'cards', label: 'Cards', group: 'Patterns' },
  { id: 'navigation', label: 'Navigation', group: 'Patterns' },
  { id: 'hero', label: 'Hero', group: 'Patterns' },
  { id: 'list', label: 'List and table', group: 'Patterns' },
  { id: 'feedback', label: 'Feedback', group: 'Patterns' },
  { id: 'dialog', label: 'Dialog and sheet', group: 'Patterns' },
]
const SECTION_IDS = new Set<string>(SECTIONS.map((s) => s.id))
function sectionFromHash(): SectionId {
  const h = location.hash.slice(1)
  return (SECTION_IDS.has(h) ? h : 'presets') as SectionId
}

const CONFIG = {
  color: {
    accent: P.accent,
    pin: false,
    tint: [P.tint, 0, 0.03, 0.001] as [number, number, number, number],
    danger: [27, 0, 360, 1] as [number, number, number, number],
    success: [150, 0, 360, 1] as [number, number, number, number],
    warning: [75, 0, 360, 1] as [number, number, number, number],
  },
  shape: {
    radius: [P.radius, 0, 24, 1] as [number, number, number, number],
    corner: { type: 'select' as const, options: ['round', 'squircle', 'sharp'], default: P.corner },
    shadow: { type: 'select' as const, options: ['none', 'soft', 'hard', 'border'], default: P.shadow },
    border: [P.border, 0, 3, 0.5] as [number, number, number, number],
  },
  type: {
    font: { type: 'select' as const, options: Object.keys(FONTS), default: P.font },
    ratio: [P.ratio, 1.067, 1.5, 0.001] as [number, number, number, number],
    base: [P.base, 14, 20, 1] as [number, number, number, number],
    leading: [P.leading, 1.2, 1.8, 0.05] as [number, number, number, number],
  },
  space: {
    unit: [P.space, 2, 8, 1] as [number, number, number, number],
    width: [P.width, 48, 96, 4] as [number, number, number, number],
  },
  motion: {
    duration: [P.duration, 0, 500, 10] as [number, number, number, number],
    ease: { type: 'select' as const, options: ['out', 'in-out', 'spring'], default: 'out' },
    reduced: false,
  },
  copy: {
    brand: 'Casa Yoga',
    title: 'Yoga classes that fit around your week',
    lede: 'Small groups, real teachers and a schedule that changes with you. First class free, no card required.',
    cta: 'Book a class',
    cta2: 'See the schedule',
  },
  export: {
    presetName: 'Template A',
    savePreset: { type: 'action' as const, label: 'Save preset to web-lab' },
    tokensJson: { type: 'action' as const, label: 'Download tokens.tokens.json' },
    tokensCss: { type: 'action' as const, label: 'Download tokens.css' },
    copyJson: { type: 'action' as const, label: 'Copy tokens JSON' },
  },
}

function download(name: string, text: string, type = 'application/json') {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([text], { type }))
  a.download = name
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}

export default function App() {
  const [dark, setDark] = useState(false)
  const [width, setWidth] = useState<'auto' | '375' | '768' | '1280'>('auto')
  const [presetName, setPresetName] = useState(() => { try { return localStorage.getItem('style-lab:preset') || 'Minimal' } catch { return 'Minimal' } })
  const [toast, setToast] = useState('')
  const [saved, setSaved] = useState<SavedPreset[]>([])
  const [section, setSection] = useState<SectionId>(() => sectionFromHash())
  const refreshSaved = () => fetch('/api/presets').then((r) => r.json()).then(setSaved).catch(() => setSaved([]))
  useEffect(() => { void refreshSaved() }, [])
  useEffect(() => {
    const onHash = () => setSection(sectionFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])
  useEffect(() => {
    if (location.hash.slice(1) !== section) location.hash = section
  }, [section])

  const kit = useDialKitController('Style lab', CONFIG, {
    id: 'style-lab',
    persist: true,
    onAction: (action) => {
      const k = knobs(), r = ramps(), s = sem()
      if (action.endsWith('tokensJson')) download('tokens.tokens.json', JSON.stringify(buildTokens(k, r, s), null, 2))
      if (action.endsWith('tokensCss')) download('tokens.css', tokensCss(k, r, s), 'text/css')
      if (action.endsWith('copyJson')) navigator.clipboard.writeText(JSON.stringify(buildTokens(k, r, s), null, 2)).then(() => flash('Tokens JSON copied'))
      if (action.endsWith('savePreset')) {
        const name = String(kit.getValues().export.presetName || '').trim()
        const tokens = buildTokens(k, r, s) as Record<string, unknown> & { $extensions: { 'web-lab': { lab: Record<string, unknown> } } }
        tokens.$extensions['web-lab'].lab.copy = kit.getValues().copy
        fetch('/api/presets', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, tokens }) })
          .then((res) => res.json()).then((j) => { if (j.error) flash(j.error); else { flash(`Saved: ${j.file}`); setPresetName(name); void refreshSaved() } })
          .catch(() => flash('Could not save (is the dev server running?)'))
      }
    },
  })
  const v = kit.values

  const knobs = (): Knobs => ({
    accent: v.color.accent, pin: v.color.pin, tint: v.color.tint,
    radius: v.shape.radius, corner: v.shape.corner as Knobs['corner'], shadow: v.shape.shadow as Knobs['shadow'], border: v.shape.border,
    font: v.type.font, ratio: v.type.ratio, base: v.type.base, leading: v.type.leading,
    space: v.space.unit, width: v.space.width, duration: v.motion.duration, ease: v.motion.ease,
  })
  const k = useMemo(knobs, [v])
  const built = useMemo(() => buildRamps(k.accent, k.pin, k.tint, { danger: v.color.danger, success: v.color.success, warning: v.color.warning }), [k.accent, k.pin, k.tint, v.color.danger, v.color.success, v.color.warning])
  const rampsAll = built.ramps
  const ramps = () => rampsAll
  const semantic = useMemo(() => buildSemantic(rampsAll), [rampsAll])
  const sem = () => semantic
  const pairs = useMemo(() => checkPairs(semantic), [semantic])
  const vars = useMemo(() => cssVars(k, rampsAll, semantic, dark), [k, rampsAll, semantic, dark])
  const fails = pairs.filter((p) => !p.ok).length
  const copy: Copy = v.copy

  function flash(msg: string) { setToast(msg); setTimeout(() => setToast(''), 1800) }

  function applyPreset(name: string) {
    setPresetName(name)
    try { localStorage.setItem('style-lab:preset', name) } catch { /* private mode */ }
    const p = PRESETS[name]
    if (p) {
      kit.setValues({
        color: { accent: p.accent, tint: p.tint, pin: false },
        shape: { radius: p.radius, corner: p.corner, shadow: p.shadow, border: p.border },
        type: { font: p.font, ratio: p.ratio, base: p.base, leading: p.leading },
        space: { unit: p.space, width: p.width },
        motion: { duration: p.duration, ease: 'out' },
        export: { presetName: name },
      } as Parameters<typeof kit.setValues>[0])
      return
    }
    const sp = saved.find((x) => x.name === name || x.slug === name)
    if (!sp) return
    const l = sp.lab
    kit.setValues({
      color: { accent: l.accent, tint: l.tint, pin: !!l.pin },
      shape: { radius: l.radius, corner: l.corner, shadow: l.shadow, border: l.border },
      type: { font: l.font, ratio: l.ratio, base: l.base, leading: l.leading },
      space: { unit: l.space, width: l.width },
      motion: { duration: l.duration, ease: l.ease ?? 'out' },
      ...(l.copy ? { copy: l.copy } : {}),
      export: { presetName: sp.name },
    } as Parameters<typeof kit.setValues>[0])
  }

  function deleteSaved(name: string = presetName) {
    const sp = saved.find((x) => x.name === name || x.slug === name)
    if (!sp || !confirm(`Delete saved preset "${sp.name}"? The file in web-lab is removed.`)) return
    fetch(`/api/presets?slug=${encodeURIComponent(sp.slug)}`, { method: 'DELETE' }).then(() => { flash('Deleted'); setPresetName('Minimal'); void refreshSaved() })
  }

  function onDeleteSaved(name: string) {
    setPresetName(name)
    deleteSaved(name)
  }

  // Suppress transitions while the theme flips (better-ui: theme switch should snap, not smear).
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = '*,*::before,*::after{transition:none !important}'
    document.head.append(style)
    void document.body.offsetHeight
    requestAnimationFrame(() => requestAnimationFrame(() => style.remove()))
  }, [dark])

  // Current export, readable from the DOM (Frost's skill and tests read it without clicking).
  const tokensJson = useMemo(() => JSON.stringify(buildTokens(k, rampsAll, semantic), null, 2), [k, rampsAll, semantic])

  function renderSection() {
    switch (section) {
      case 'presets': return <Presets builtIn={Object.keys(PRESETS)} saved={saved} current={presetName} onApply={applyPreset} onDelete={onDeleteSaved} />
      case 'color': return <Color ramps={rampsAll} sem={semantic} pairs={pairs} pinned={built.pinned} />
      case 'typography': return <Typography k={k} copy={copy} />
      case 'shape': return <Shape k={k} />
      case 'elevation': return <Elevation k={k} />
      case 'spacing': return <Spacing k={k} />
      case 'motion': return <Motion k={k} reduced={v.motion.reduced} />
      case 'buttons': return <Buttons copy={copy} />
      case 'forms': return <FormControls />
      case 'cards': return <Cards k={k} copy={copy} />
      case 'navigation': return <Navigation copy={copy} />
      case 'hero': return <Hero copy={copy} />
      case 'list': return <List />
      case 'feedback': return <Feedback />
      case 'dialog': return <Dialog k={k} reduced={v.motion.reduced} />
      default: return null
    }
  }

  return (
    <div className="lab">
      <DialRoot position="top-right" theme="system" mode="popover" defaultOpen />
      <div className="lab-bar">
        <strong>web-lab · Style lab</strong>
        <div className="grp"><span>Preset</span>
          <select value={presetName} onChange={(e) => applyPreset(e.target.value)}>
            <optgroup label="Built-in">{Object.keys(PRESETS).map((n) => <option key={n}>{n}</option>)}</optgroup>
            {saved.length > 0 && <optgroup label="Saved in web-lab">{saved.map((sp) => <option key={sp.slug} value={sp.name}>{sp.name}</option>)}</optgroup>}
            {!Object.keys(PRESETS).includes(presetName) && !saved.some((sp) => sp.name === presetName) && <option value={presetName}>{presetName}</option>}
          </select>
          {saved.some((sp) => sp.name === presetName) && <button onClick={() => deleteSaved()} aria-label={`Delete saved preset ${presetName}`}>Delete</button>}
        </div>
        <div className="grp" role="group" aria-label="Preview width">
          {(['auto', '375', '768', '1280'] as const).map((w) => <button key={w} aria-pressed={width === w} onClick={() => setWidth(w)}>{w === 'auto' ? 'Fluid' : `${w} px`}</button>)}
        </div>
        <div className="grp"><button aria-pressed={dark} onClick={() => setDark(!dark)}>{dark ? 'Dark' : 'Light'} mode</button></div>
        <div className="status">contrast: <b className={fails ? 'fail' : 'ok'}>{fails ? `${fails} pair(s) fail` : `${pairs.length} pairs pass`}</b>{toast ? ` · ${toast}` : ''}</div>
      </div>
      <script type="application/json" id="tokens-json" dangerouslySetInnerHTML={{ __html: tokensJson.replace(/</g, '\\u003c') }} />
      <div className="lab-main">
        <nav className="lab-nav" aria-label="Sections">
          {(['General', 'Patterns'] as const).map((group) => (
            <div className="lab-nav-group" key={group}>
              <div className="lab-nav-heading">{group}</div>
              {SECTIONS.filter((s) => s.group === group).map((s) => (
                <button key={s.id} aria-current={section === s.id ? 'page' : undefined} onClick={() => setSection(s.id)}>{s.label}</button>
              ))}
            </div>
          ))}
        </nav>
        <div className="stage">
          <div className="frame" data-width={width === 'auto' ? undefined : width}>
            <div className="preview" data-theme={dark ? 'dark' : 'light'} data-reduced={v.motion.reduced ? 'true' : 'false'} style={vars as React.CSSProperties}>
              {renderSection()}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
