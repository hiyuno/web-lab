import { APCAcontrast, sRGBtoY } from 'apca-w3'
import { parse, converter } from 'culori'
import { wcag } from './color'
import type { Semantic, SemanticName } from './color'

const toRgb = converter('rgb')

export function apca(fg: string, bg: string): number {
  const f = toRgb(parse(fg) ?? '#000')!, b = toRgb(parse(bg) ?? '#fff')!
  const to255 = (x: { r: number; g: number; b: number }) => [x.r * 255, x.g * 255, x.b * 255] as [number, number, number]
  return Math.round(Number(APCAcontrast(sRGBtoY(to255(f)), sRGBtoY(to255(b)))))
}

export interface Pair { fg: SemanticName; bg: SemanticName; min: number; label: string }

// Every text-on-background pair that exists in the system. 4.5 normal text, 3 large text, icons
// and focus. Decorative borders have no WCAG requirement; 1.2 keeps them distinguishable.
export const PAIRS: Pair[] = [
  { fg: 'foreground', bg: 'background', min: 4.5, label: 'body text' },
  { fg: 'muted-foreground', bg: 'background', min: 4.5, label: 'secondary text' },
  { fg: 'foreground', bg: 'muted', min: 4.5, label: 'text on muted' },
  { fg: 'foreground', bg: 'card', min: 4.5, label: 'text on card' },
  { fg: 'accent-foreground', bg: 'accent', min: 4.5, label: 'primary button' },
  { fg: 'accent', bg: 'background', min: 4.5, label: 'link / accent text' },
  { fg: 'danger', bg: 'background', min: 4.5, label: 'error text' },
  { fg: 'success', bg: 'background', min: 4.5, label: 'success text' },
  { fg: 'warning', bg: 'background', min: 4.5, label: 'warning text' },
  { fg: 'ring', bg: 'background', min: 3, label: 'focus ring' },
  { fg: 'border', bg: 'background', min: 1.2, label: 'border (decorative)' },
]

export interface PairResult extends Pair { light: number; dark: number; lightLc: number; darkLc: number; ok: boolean }

export function checkPairs(sem: Semantic): PairResult[] {
  return PAIRS.map((p) => {
    const light = wcag(sem[p.fg].light, sem[p.bg].light)
    const dark = wcag(sem[p.fg].dark, sem[p.bg].dark)
    return {
      ...p, light, dark,
      lightLc: Math.abs(apca(sem[p.fg].light, sem[p.bg].light)),
      darkLc: Math.abs(apca(sem[p.fg].dark, sem[p.bg].dark)),
      ok: light >= p.min && dark >= p.min,
    }
  })
}
