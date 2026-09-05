// tests/e2e/fixtures/axe.ts · web-lab fase 6
// Fixture reutilizable: axe configurado para WCAG 2.2 AA en todas las pruebas.
// Uso: import { test, expect } from './fixtures/axe'
import { test as base, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

type AxeFixture = { makeAxeBuilder: () => AxeBuilder }

export const test = base.extend<AxeFixture>({
  makeAxeBuilder: async ({ page }, use) => {
    const make = () =>
      new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
        // Excluye SOLO widgets de terceros que no controlas y documenta por qué en accesibilidad.md
        .exclude('#third-party-chat-widget')
    await use(make)
  },
})

export { expect }

// Huella estable de violaciones: regla + selectores, sin HTML, para snapshots que no se rompan por texto.
export function fingerprint(results: Awaited<ReturnType<AxeBuilder['analyze']>>) {
  return results.violations.map((v) => ({
    id: v.id,
    impact: v.impact,
    targets: v.nodes.map((n) => n.target.join(' ')),
  }))
}
