// Color engine: one accent → ramps (accent, neutral, status) → semantic tokens in light and dark.
// Rules from `better-colors` (interfaces collection): ramps not colors, every step has a role,
// even perceived lightness, constant hue, vividness peaking mid-ramp, ends short of pure
// white/black, denser at the light end, status hues distinct from the accent, dark mode is not
// the mirror. Math in OKLCH via culori.
import { converter, formatHex, clampChroma, wcagContrast, parse } from 'culori'
import type { Oklch } from 'culori'

export const STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950] as const
export type Step = (typeof STEPS)[number]
export type Ramp = Record<Step, string>

// Perceived lightness per step (OKLCH L). Denser at the light end, ends short of 1 and 0.
const L: Record<Step, number> = {
  50: 0.985, 100: 0.965, 200: 0.92, 300: 0.86, 400: 0.76, 500: 0.66,
  600: 0.56, 700: 0.46, 800: 0.36, 900: 0.26, 950: 0.17,
}
// Vividness multiplier: peaks mid-ramp, falls off at both ends.
const CMUL: Record<Step, number> = {
  50: 0.12, 100: 0.28, 200: 0.5, 300: 0.7, 400: 0.88, 500: 1,
  600: 0.96, 700: 0.84, 800: 0.66, 900: 0.48, 950: 0.32,
}

const toOklch = converter('oklch')

export function oklchOf(color: string): Oklch {
  const c = toOklch(parse(color) ?? '#000') as Oklch
  return { mode: 'oklch', l: c.l ?? 0, c: c.c ?? 0, h: c.h ?? 0 }
}

export function oklchString(c: { l: number; c: number; h?: number }, digits = 3) {
  const pct = (c.l * 100).toFixed(1).replace(/\.0$/, '')
  return `oklch(${pct}% ${c.c.toFixed(digits)} ${(c.h ?? 0).toFixed(1)})`
}

function stepColor(l: number, chroma: number, hue: number): Oklch {
  return clampChroma({ mode: 'oklch', l, c: chroma, h: hue }, 'oklch') as Oklch
}

/** Builds an 11-step ramp holding the hue, with the given peak chroma. */
export function buildRamp(hue: number, peakChroma: number): Ramp {
  const out = {} as Ramp
  for (const s of STEPS) out[s] = oklchString(stepColor(L[s], peakChroma * CMUL[s], hue))
  return out
}

/** Pins or snaps the brand color: returns the ramp and which step the exact brand lands on. */
export function accentRamp(accent: string, pin: boolean): { ramp: Ramp; pinned: Step | null } {
  const a = oklchOf(accent)
  const ramp = buildRamp(a.h ?? 0, Math.max(a.c, 0.02))
  if (!pin) return { ramp, pinned: null }
  // Closest step by lightness; pin the exact value there.
  let best: Step = 500, d = 1
  for (const s of STEPS) { const dd = Math.abs(L[s] - a.l); if (dd < d) { d = dd; best = s } }
  ramp[best] = oklchString(a)
  return { ramp, pinned: best }
}

/** Neutral ramp: pure gray or tinted toward the accent hue (a few percent of its vividness). */
export function neutralRamp(accentHue: number, tint: number): Ramp {
  return buildRamp(accentHue, tint)
}

/** Status ramps with hues kept at least 15° from the accent. */
export function statusHue(base: number, accentHue: number): number {
  let h = base
  const d = Math.abs(((h - accentHue + 540) % 360) - 180)
  if (d < 15) h = (accentHue + (h >= accentHue ? 20 : -20) + 360) % 360
  return h
}

export const hex = (c: string) => formatHex(parse(c) ?? '#000') ?? '#000000'
export const wcag = (fg: string, bg: string) => wcagContrast(parse(fg) ?? '#000', parse(bg) ?? '#fff')

/** Picks white or the darkest neutral as text over a solid, whichever contrasts more. */
export function onColor(bg: string, dark: string): string {
  return wcag('#ffffff', bg) >= wcag(dark, bg) ? '#ffffff' : dark
}

export type SemanticName =
  | 'background' | 'foreground' | 'muted' | 'muted-foreground' | 'card' | 'border'
  | 'accent' | 'accent-foreground' | 'danger' | 'success' | 'warning' | 'ring'

export type Semantic = Record<SemanticName, { light: string; dark: string; lightRef: string; darkRef: string }>

export interface Ramps { brand: Ramp; gray: Ramp; red: Ramp; green: Ramp; amber: Ramp }

export function buildRamps(accent: string, pin: boolean, tint: number, hues: { danger: number; success: number; warning: number }): { ramps: Ramps; pinned: Step | null } {
  const a = oklchOf(accent)
  const { ramp: brand, pinned } = accentRamp(accent, pin)
  const ramps: Ramps = {
    brand,
    gray: neutralRamp(a.h ?? 0, tint),
    red: buildRamp(statusHue(hues.danger, a.h ?? 0), 0.2),
    green: buildRamp(statusHue(hues.success, a.h ?? 0), 0.16),
    amber: buildRamp(statusHue(hues.warning, a.h ?? 0), 0.15),
  }
  return { ramps, pinned }
}

/** Semantic tokens per better-colors: swap roles for dark, then reduce vividness at the dark end. */
export function buildSemantic(r: Ramps): Semantic {
  const ref = (g: keyof Ramps, s: Step) => `{color.${g}.${s}}`
  const S = (lg: keyof Ramps, ls: Step, dg: keyof Ramps, ds: Step) =>
    ({ light: r[lg][ls], dark: r[dg][ds], lightRef: ref(lg, ls), darkRef: ref(dg, ds) })
  const accentFgDark = onColor(r.brand[400], r.gray[950])
  // Status text on the light background: the first step from 600 that clears 4.5:1 against
  // white. Fix contrast by moving lightness, never hue (better-colors). Hues like green and
  // amber are perceptually lighter, so they land a step deeper than red.
  const textStep = (g: keyof Ramps, from: Step[] = [600, 700, 800]): Step => from.find((st) => wcag(r[g][st], '#ffffff') >= 4.5) ?? 800
  const dangerL = textStep('red'), successL = textStep('green'), warningL = textStep('amber', [700, 800])
  // The accent doubles as link text and as the primary fill, so its light step must clear 4.5:1
  // against white too (a teal or yellow brand lands on 700 instead of 600).
  const accentL = textStep('brand')
  const accentFgLight = onColor(r.brand[accentL], r.gray[950])
  return {
    background: { light: '#ffffff', dark: r.gray[950], lightRef: '{color.white}', darkRef: ref('gray', 950) },
    foreground: S('gray', 900, 'gray', 50),
    muted: S('gray', 100, 'gray', 900),
    'muted-foreground': S('gray', 600, 'gray', 400),
    card: { light: '#ffffff', dark: r.gray[900], lightRef: '{color.white}', darkRef: ref('gray', 900) },
    border: S('gray', 200, 'gray', 800),
    accent: S('brand', accentL, 'brand', 400),
    'accent-foreground': {
      light: accentFgLight, dark: accentFgDark,
      lightRef: accentFgLight === '#ffffff' ? '{color.white}' : ref('gray', 950),
      darkRef: accentFgDark === '#ffffff' ? '{color.white}' : ref('gray', 950),
    },
    danger: S('red', dangerL, 'red', 300),
    success: S('green', successL, 'green', 300),
    warning: S('amber', warningL, 'amber', 300),
    ring: S('brand', accentL, 'brand', 300),
  }
}
