import { useEffect, useMemo, useRef, useState } from 'react'
import { DialRoot, useDialKitController } from 'dialkit'
import { buildRamps, buildSemantic } from './engine/color'
import { checkPairs } from './engine/contrast'
import { FONTS, PRESETS } from './engine/presets'
import { buildTokens, cssVars, tokensCss } from './engine/tokens'
import type { Knobs } from './engine/tokens'
import { Presets, Typography, Color, Shape, Elevation, Spacing, Motion, Buttons, FormControls, Cards, Navigation, Hero, List, Feedback, Dialog, Showcase, Pricing, Changelog, Voting } from './patterns'
import type { Copy } from './patterns'

const P = PRESETS.Minimal

interface SavedPreset { slug: string; name: string; accent?: string; font?: string; updated: string; lab: Record<string, any> }

type SectionId = 'presets' | 'color' | 'typography' | 'shape' | 'elevation' | 'spacing' | 'motion' | 'buttons' | 'forms' | 'cards' | 'navigation' | 'hero' | 'list' | 'feedback' | 'dialog' | 'showcase' | 'pricing' | 'changelog' | 'voting'

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
  { id: 'showcase', label: 'Feature showcase', group: 'Patterns' },
  { id: 'pricing', label: 'Pricing', group: 'Patterns' },
  { id: 'changelog', label: 'Changelog', group: 'Patterns' },
  { id: 'voting', label: 'Voting board', group: 'Patterns' },
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
    customDark: false,
    darkAccent: '#a5b4fc',
    darkSurface: { type: 'select' as const, options: ['deep', 'soft'], default: 'deep' },
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
    fast: [150, 0, 400, 10] as [number, number, number, number],
    normal: [200, 0, 600, 10] as [number, number, number, number],
    slow: [300, 0, 900, 10] as [number, number, number, number],
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

// Which DialKit panels are relevant to each section (matched by panel name against
// the "name" passed to useDialKitController below). Panels not in the list are hidden.
type PanelName = 'Color' | 'Shape' | 'Type' | 'Space' | 'Motion' | 'Copy' | 'Export'
const VISIBILITY: Record<SectionId, PanelName[]> = {
  presets: ['Export'],
  color: ['Color'],
  typography: ['Type', 'Copy'],
  shape: ['Shape'],
  elevation: ['Shape'],
  spacing: ['Space'],
  motion: ['Motion'],
  buttons: ['Shape', 'Motion'],
  forms: ['Shape', 'Type'],
  cards: ['Shape', 'Space'],
  navigation: ['Type', 'Space', 'Copy'],
  hero: ['Copy', 'Type', 'Space'],
  list: ['Space', 'Shape'],
  feedback: ['Color', 'Shape'],
  dialog: ['Motion', 'Shape'],
  showcase: ['Copy', 'Type', 'Space'],
  pricing: ['Shape', 'Space'],
  changelog: ['Space', 'Shape'],
  voting: ['Shape', 'Color'],
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

  // One controller per group, so each shows as its own DialKit panel and can be
  // hidden/shown independently depending on the active section (see VISIBILITY above).
  const colorKit = useDialKitController('Color', CONFIG.color, { id: 'lab-color', persist: true })
  const shapeKit = useDialKitController('Shape', CONFIG.shape, { id: 'lab-shape', persist: true })
  const typeKit = useDialKitController('Type', CONFIG.type, { id: 'lab-type', persist: true })
  const spaceKit = useDialKitController('Space', CONFIG.space, { id: 'lab-space', persist: true })
  const motionKit = useDialKitController('Motion', CONFIG.motion, { id: 'lab-motion', persist: true })
  const copyKit = useDialKitController('Copy', CONFIG.copy, { id: 'lab-copy', persist: true })
  const exportKit = useDialKitController('Export', CONFIG.export, {
    id: 'lab-export',
    persist: true,
    onAction: (action) => {
      const k = knobs(), r = ramps(), s = sem()
      if (action.endsWith('tokensJson')) download('tokens.tokens.json', JSON.stringify(buildTokens(k, r, s), null, 2))
      if (action.endsWith('tokensCss')) download('tokens.css', tokensCss(k, r, s), 'text/css')
      if (action.endsWith('copyJson')) navigator.clipboard.writeText(JSON.stringify(buildTokens(k, r, s), null, 2)).then(() => flash('Tokens JSON copied'))
      if (action.endsWith('savePreset')) {
        const name = String(exportKit.getValues().presetName || '').trim()
        const tokens = buildTokens(k, r, s) as Record<string, unknown> & { $extensions: { 'web-lab': { lab: Record<string, unknown> } } }
        tokens.$extensions['web-lab'].lab.copy = copyKit.getValues()
        fetch('/api/presets', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, tokens }) })
          .then((res) => res.json()).then((j) => { if (j.error) flash(j.error); else { flash(`Saved: ${j.file}`); setPresetName(name); void refreshSaved() } })
          .catch(() => flash('Could not save (is the dev server running?)'))
      }
    },
  })
  const controllers = { Color: colorKit, Shape: shapeKit, Type: typeKit, Space: spaceKit, Motion: motionKit, Copy: copyKit, Export: exportKit }

  const knobs = (): Knobs => ({
    accent: colorKit.values.accent, pin: colorKit.values.pin, tint: colorKit.values.tint,
    customDark: colorKit.values.customDark, darkAccent: colorKit.values.darkAccent, darkSurface: colorKit.values.darkSurface as Knobs['darkSurface'],
    radius: shapeKit.values.radius, corner: shapeKit.values.corner as Knobs['corner'], shadow: shapeKit.values.shadow as Knobs['shadow'], border: shapeKit.values.border,
    font: typeKit.values.font, ratio: typeKit.values.ratio, base: typeKit.values.base, leading: typeKit.values.leading,
    space: spaceKit.values.unit, width: spaceKit.values.width,
    fast: motionKit.values.fast, normal: motionKit.values.normal, slow: motionKit.values.slow, ease: motionKit.values.ease,
  })
  const k = useMemo(knobs, [colorKit.values, shapeKit.values, typeKit.values, spaceKit.values, motionKit.values])
  const built = useMemo(
    () => buildRamps(k.accent, k.pin, k.tint, { danger: colorKit.values.danger, success: colorKit.values.success, warning: colorKit.values.warning }, { accent: k.customDark ? k.darkAccent : undefined }),
    [k.accent, k.pin, k.tint, k.customDark, k.darkAccent, colorKit.values.danger, colorKit.values.success, colorKit.values.warning],
  )
  const rampsAll = built.ramps
  const ramps = () => rampsAll
  const semantic = useMemo(() => buildSemantic(rampsAll, { darkSurface: k.darkSurface }), [rampsAll, k.darkSurface])
  const sem = () => semantic
  const pairs = useMemo(() => checkPairs(semantic), [semantic])
  const vars = useMemo(() => cssVars(k, rampsAll, semantic, dark), [k, rampsAll, semantic, dark])
  const fails = pairs.filter((p) => !p.ok).length
  const copy: Copy = copyKit.values

  function flash(msg: string) { setToast(msg); setTimeout(() => setToast(''), 1800) }

  function applyPreset(name: string) {
    setPresetName(name)
    try { localStorage.setItem('style-lab:preset', name) } catch { /* private mode */ }
    const p = PRESETS[name]
    if (p) {
      colorKit.setValues({ accent: p.accent, tint: p.tint, pin: false, customDark: false, darkSurface: 'deep' })
      shapeKit.setValues({ radius: p.radius, corner: p.corner, shadow: p.shadow, border: p.border })
      typeKit.setValues({ font: p.font, ratio: p.ratio, base: p.base, leading: p.leading })
      spaceKit.setValues({ unit: p.space, width: p.width })
      motionKit.setValues({ fast: p.fast, normal: p.normal, slow: p.slow, ease: 'out' })
      exportKit.setValues({ presetName: name })
      return
    }
    const sp = saved.find((x) => x.name === name || x.slug === name)
    if (!sp) return
    const l = sp.lab
    colorKit.setValues({ accent: l.accent, tint: l.tint, pin: !!l.pin, customDark: !!l.customDark, darkAccent: l.darkAccent ?? l.accent, darkSurface: l.darkSurface ?? 'deep' })
    shapeKit.setValues({ radius: l.radius, corner: l.corner, shadow: l.shadow, border: l.border })
    typeKit.setValues({ font: l.font, ratio: l.ratio, base: l.base, leading: l.leading })
    spaceKit.setValues({ unit: l.space, width: l.width })
    // Saved presets from before fast/normal/slow existed only have "duration" (the old
    // normal speed). Derive the three the same way the CLI's backward-compat path does.
    const fast = l.fast ?? Math.round(l.duration * 0.75)
    const normal = l.normal ?? l.duration
    const slow = l.slow ?? Math.round(l.duration * 1.5)
    motionKit.setValues({ fast, normal, slow, ease: l.ease ?? 'out' })
    if (l.copy) copyKit.setValues(l.copy)
    exportKit.setValues({ presetName: sp.name })
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

  // Settings that apply to the active section only: expand the relevant DialKit panels...
  const visiblePanels = VISIBILITY[section]
  useEffect(() => {
    visiblePanels.forEach((name) => controllers[name]?.setOpen(true))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [section])

  // ...and hide every other panel. DialKit renders each controller as a
  // ".dialkit-folder" (the shared shell folder carries ".dialkit-folder-root" too,
  // so excluding it leaves just the seven group panels); its accessible name lives
  // on the ".dialkit-folder-header-top" element's aria-label, set unconditionally
  // regardless of open/collapsed state, which is why we read that instead of the
  // title span (only rendered while a root folder is open).
  const panelRef = useRef<HTMLElement>(null)
  useEffect(() => {
    const aside = panelRef.current
    if (!aside) return
    const applyVisibility = () => {
      const folders = aside.querySelectorAll<HTMLElement>('.dialkit-folder:not(.dialkit-folder-root)')
      folders.forEach((el) => {
        const header = el.querySelector<HTMLElement>('.dialkit-folder-header-top')
        const title = header?.getAttribute('aria-label')?.trim() || header?.textContent?.trim() || ''
        el.hidden = !visiblePanels.includes(title as PanelName)
      })
    }
    applyVisibility()
    const mo = new MutationObserver(applyVisibility)
    mo.observe(aside, { childList: true, subtree: true })
    return () => mo.disconnect()
  }, [section, visiblePanels])

  function renderSection() {
    switch (section) {
      case 'presets': return <Presets builtIn={Object.keys(PRESETS)} saved={saved} current={presetName} onApply={applyPreset} onDelete={onDeleteSaved} />
      case 'color': return <Color ramps={rampsAll} sem={semantic} pairs={pairs} pinned={built.pinned} />
      case 'typography': return <Typography k={k} copy={copy} />
      case 'shape': return <Shape k={k} />
      case 'elevation': return <Elevation k={k} />
      case 'spacing': return <Spacing k={k} />
      case 'motion': return <Motion k={k} reduced={motionKit.values.reduced} onReset={() => motionKit.resetValues()} />
      case 'buttons': return <Buttons copy={copy} />
      case 'forms': return <FormControls />
      case 'cards': return <Cards k={k} copy={copy} />
      case 'navigation': return <Navigation copy={copy} />
      case 'hero': return <Hero copy={copy} />
      case 'list': return <List />
      case 'feedback': return <Feedback />
      case 'dialog': return <Dialog k={k} reduced={motionKit.values.reduced} />
      case 'showcase': return <Showcase copy={copy} />
      case 'pricing': return <Pricing k={k} copy={copy} />
      case 'changelog': return <Changelog />
      case 'voting': return <Voting />
      default: return null
    }
  }

  const activeLabel = SECTIONS.find((s) => s.id === section)?.label ?? ''
  const onlyExportVisible = visiblePanels.length === 1 && visiblePanels[0] === 'Export'

  return (
    <div className="lab">
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
            <div className="preview" data-theme={dark ? 'dark' : 'light'} data-reduced={motionKit.values.reduced ? 'true' : 'false'} style={vars as React.CSSProperties}>
              {renderSection()}
            </div>
          </div>
        </div>
        <aside className="lab-panel" aria-label="Settings" ref={panelRef}>
          <div className="lab-panel-title">
            Settings · <span>{activeLabel}</span>
            <button
              className="lab-panel-reset"
              title="Reset the visible settings to their defaults"
              onClick={() => visiblePanels.forEach((name) => controllers[name]?.resetValues())}
            >
              Reset
            </button>
          </div>
          {onlyExportVisible && (
            <p className="small muted">Save the current settings as a preset. Copy and colors are edited in their sections.</p>
          )}
          <DialRoot mode="inline" theme="system" defaultOpen />
        </aside>
      </div>
    </div>
  )
}
