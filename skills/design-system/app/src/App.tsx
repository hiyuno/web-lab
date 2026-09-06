import { useEffect, useMemo, useState } from 'react'
import { DialRoot, useDialKitController } from 'dialkit'
import { buildRamps, buildSemantic } from './engine/color'
import { checkPairs } from './engine/contrast'
import { FONTS, PRESETS } from './engine/presets'
import { buildTokens, cssVars, tokensCss } from './engine/tokens'
import type { Knobs } from './engine/tokens'
import { Typography, Color, Buttons, Cards, Form, Navigation, Hero, List, Feedback, Dialog } from './patterns'
import type { Copy } from './patterns'

const P = PRESETS.Minimal

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

  const kit = useDialKitController('Style lab', CONFIG, {
    id: 'style-lab',
    persist: true,
    onAction: (action) => {
      const k = knobs(), r = ramps(), s = sem()
      if (action.endsWith('tokensJson')) download('tokens.tokens.json', JSON.stringify(buildTokens(k, r, s), null, 2))
      if (action.endsWith('tokensCss')) download('tokens.css', tokensCss(k, r, s), 'text/css')
      if (action.endsWith('copyJson')) navigator.clipboard.writeText(JSON.stringify(buildTokens(k, r, s), null, 2)).then(() => flash('Tokens JSON copied'))
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
    const p = PRESETS[name]; if (!p) return
    setPresetName(name)
    try { localStorage.setItem('style-lab:preset', name) } catch { /* private mode */ }
    kit.setValues({
      color: { accent: p.accent, tint: p.tint },
      shape: { radius: p.radius, corner: p.corner, shadow: p.shadow, border: p.border },
      type: { font: p.font, ratio: p.ratio, base: p.base, leading: p.leading },
      space: { unit: p.space, width: p.width },
      motion: { duration: p.duration },
    } as Parameters<typeof kit.setValues>[0])
  }

  // Suppress transitions while the theme flips (better-ui: theme switch should snap, not smear).
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = '*,*::before,*::after{transition:none !important}'
    document.head.append(style)
    void document.body.offsetHeight
    requestAnimationFrame(() => requestAnimationFrame(() => style.remove()))
  }, [dark])

  const semList = Object.entries(semantic)

  // Current export, readable from the DOM (Frost's skill and tests read it without clicking).
  const tokensJson = useMemo(() => JSON.stringify(buildTokens(k, rampsAll, semantic), null, 2), [k, rampsAll, semantic])

  return (
    <div className="lab">
      <DialRoot position="top-right" theme="system" mode="popover" defaultOpen />
      <div className="lab-bar">
        <strong>web-lab · Style lab</strong>
        <div className="grp"><span>Preset</span>
          <select value={presetName} onChange={(e) => applyPreset(e.target.value)}>{Object.keys(PRESETS).map((n) => <option key={n}>{n}</option>)}</select>
        </div>
        <div className="grp" role="group" aria-label="Preview width">
          {(['auto', '375', '768', '1280'] as const).map((w) => <button key={w} aria-pressed={width === w} onClick={() => setWidth(w)}>{w === 'auto' ? 'Fluid' : `${w} px`}</button>)}
        </div>
        <div className="grp"><button aria-pressed={dark} onClick={() => setDark(!dark)}>{dark ? 'Dark' : 'Light'} mode</button></div>
        <div className="grp"><button onClick={() => download('tokens.tokens.json', JSON.stringify(buildTokens(k, rampsAll, semantic), null, 2))}>Export tokens.tokens.json</button><button onClick={() => download('tokens.css', tokensCss(k, rampsAll, semantic), 'text/css')}>Export tokens.css</button></div>
        <div className="status">contrast: <b className={fails ? 'fail' : 'ok'}>{fails ? `${fails} pair(s) fail` : `${pairs.length} pairs pass`}</b>{toast ? ` · ${toast}` : ''}</div>
      </div>
      <script type="application/json" id="tokens-json" dangerouslySetInnerHTML={{ __html: tokensJson.replace(/</g, '\\u003c') }} />
      <div className="stage">
        <div className="frame" data-width={width === 'auto' ? undefined : width}>
          <div className="preview" data-theme={dark ? 'dark' : 'light'} data-reduced={v.motion.reduced ? 'true' : 'false'} style={vars as React.CSSProperties}>
            <Typography k={k} copy={copy} />
            <Color ramps={rampsAll} sem={semantic} pairs={pairs} pinned={built.pinned} />
            <Buttons copy={copy} />
            <Cards k={k} copy={copy} />
            <Form />
            <Navigation copy={copy} />
            <Hero copy={copy} />
            <List />
            <Feedback />
            <Dialog k={k} reduced={v.motion.reduced} />
            <section className="pattern"><header><h2>Semantic tokens</h2><span className="n">what the export writes</span></header>
              <table><thead><tr><th>Token</th><th>Light</th><th>Dark</th></tr></thead><tbody>
                {semList.map(([n, val]) => <tr key={n}><td className="mono">--{n}</td><td className="mono">{val.lightRef} <span className="sample" style={{ background: val.light, border: '1px solid var(--border)' }}>&nbsp;&nbsp;&nbsp;</span></td><td className="mono">{val.darkRef} <span className="sample" style={{ background: val.dark, border: '1px solid var(--border)' }}>&nbsp;&nbsp;&nbsp;</span></td></tr>)}
              </tbody></table>
            </section>
          </div>
        </div>
      </div>
    </div>
  )
}
