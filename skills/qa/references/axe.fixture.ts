// tests/e2e/fixtures/axe.ts · web-lab phase 6
// Reusable fixture: axe configured for WCAG 2.2 AA in every test.
// Usage: import { test, expect } from './fixtures/axe'
import { test as base, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

type AxeFixture = { makeAxeBuilder: () => AxeBuilder }

export const test = base.extend<AxeFixture>({
  makeAxeBuilder: async ({ page }, use) => {
    const make = () =>
      new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
        // Exclude ONLY third-party widgets you do not control, and document why in accessibility.md
        .exclude('#third-party-chat-widget')
    await use(make)
  },
})

export { expect }

// Stable violation fingerprint: rule + selectors, no HTML, for snapshots that do not break on copy changes.
export function fingerprint(results: Awaited<ReturnType<AxeBuilder['analyze']>>) {
  return results.violations.map((v) => ({
    id: v.id,
    impact: v.impact,
    targets: v.nodes.map((n) => n.target.join(' ')),
  }))
}
