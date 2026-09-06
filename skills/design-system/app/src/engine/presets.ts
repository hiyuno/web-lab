// Starting personalities. Each is a full position on the knobs; the user tunes from there.
export interface Preset {
  name: string; accent: string; tint: number; radius: number; corner: 'round' | 'squircle' | 'sharp'
  shadow: 'none' | 'soft' | 'hard' | 'border'; border: number; font: string; ratio: number
  base: number; leading: number; space: number; width: number; duration: number
}

export const FONTS: Record<string, { sans: string; display: string; mono: string }> = {
  'Inter / Inter': { sans: '"Inter", system-ui, sans-serif', display: '"Inter", system-ui, sans-serif', mono: '"JetBrains Mono", ui-monospace, monospace' },
  'Source Serif / Inter': { sans: '"Inter", system-ui, sans-serif', display: '"Source Serif 4", Georgia, serif', mono: '"JetBrains Mono", ui-monospace, monospace' },
  'Playfair / Manrope': { sans: '"Manrope", system-ui, sans-serif', display: '"Playfair Display", Georgia, serif', mono: '"JetBrains Mono", ui-monospace, monospace' },
  'Space Grotesk / IBM Plex Sans': { sans: '"IBM Plex Sans", system-ui, sans-serif', display: '"Space Grotesk", system-ui, sans-serif', mono: '"JetBrains Mono", ui-monospace, monospace' },
  'Fraunces / Manrope': { sans: '"Manrope", system-ui, sans-serif', display: '"Fraunces", Georgia, serif', mono: '"JetBrains Mono", ui-monospace, monospace' },
  'IBM Plex Serif / IBM Plex Sans': { sans: '"IBM Plex Sans", system-ui, sans-serif', display: '"IBM Plex Serif", Georgia, serif', mono: '"JetBrains Mono", ui-monospace, monospace' },
  'System': { sans: 'system-ui, -apple-system, "Segoe UI", sans-serif', display: 'system-ui, -apple-system, "Segoe UI", sans-serif', mono: 'ui-monospace, SFMono-Regular, monospace' },
}

export const PRESETS: Record<string, Preset> = {
  Minimal: { name: 'Minimal', accent: '#1d4ed8', tint: 0.006, radius: 6, corner: 'round', shadow: 'border', border: 1, font: 'Inter / Inter', ratio: 1.2, base: 16, leading: 1.5, space: 4, width: 72, duration: 150 },
  Editorial: { name: 'Editorial', accent: '#9a3412', tint: 0.01, radius: 2, corner: 'round', shadow: 'none', border: 1, font: 'Source Serif / Inter', ratio: 1.333, base: 17, leading: 1.6, space: 4, width: 64, duration: 200 },
  Playful: { name: 'Playful', accent: '#db2777', tint: 0.012, radius: 16, corner: 'squircle', shadow: 'soft', border: 0, font: 'Space Grotesk / IBM Plex Sans', ratio: 1.25, base: 16, leading: 1.5, space: 5, width: 72, duration: 250 },
  Corporate: { name: 'Corporate', accent: '#0f766e', tint: 0.004, radius: 4, corner: 'round', shadow: 'soft', border: 1, font: 'IBM Plex Serif / IBM Plex Sans', ratio: 1.2, base: 16, leading: 1.5, space: 4, width: 80, duration: 150 },
  Brutalist: { name: 'Brutalist', accent: '#111111', tint: 0, radius: 0, corner: 'sharp', shadow: 'hard', border: 2, font: 'Space Grotesk / IBM Plex Sans', ratio: 1.414, base: 16, leading: 1.4, space: 4, width: 72, duration: 0 },
  Soft: { name: 'Soft', accent: '#7c3aed', tint: 0.015, radius: 12, corner: 'squircle', shadow: 'soft', border: 0, font: 'Playfair / Manrope', ratio: 1.25, base: 16, leading: 1.6, space: 5, width: 68, duration: 250 },
}
